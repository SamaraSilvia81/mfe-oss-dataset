#!/usr/bin/env node
/*
 * Sincroniza as versões do DTS1 do CuraData (Supabase) com este repositório.
 *
 *   SUPABASE_URL=https://xxxx.supabase.co SUPABASE_SECRET_KEY=... node scripts/sync-versions.mjs
 *
 * Para cada versão do banco:
 *   versions/<tag>/  arquivos da versão (CSV, CSV só com validados, JSON, metadados, notas da release)
 * E, a cada rodada:
 *   latest/          cópia da versão mais nova
 *   versions/index.json, CHANGELOG.md, CITATION.cff e as tabelas de versões do README.md e do README.pt-BR.md
 *
 * Os registros de uma versão são imutáveis no banco: se a pasta da versão já existe, os
 * arquivos de dados não são regravados. Título e changelog podem mudar e são atualizados.
 *
 * Sem dependências: só Node 20 ou mais novo.
 */
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..')
const URL_BASE = (process.env.SUPABASE_URL || '').replace(/\/+$/, '')
const KEY = process.env.SUPABASE_SECRET_KEY || ''
const DRY = process.argv.includes('--dry-run')

if (!URL_BASE || !KEY) {
  console.error('Defina SUPABASE_URL e SUPABASE_SECRET_KEY.')
  process.exit(1)
}

const META = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'fields.json'), 'utf8'))
const FIELDS = META.fields.map(f => f.key)
const PREFIX = META.dataset.filePrefix

// ── Supabase (REST) ──

function headers() {
  const h = { apikey: KEY, Accept: 'application/json' }
  // Chaves antigas (service_role) são JWT e vão também no Authorization. As novas (sb_secret_) não.
  if (KEY.startsWith('eyJ')) h.Authorization = `Bearer ${KEY}`
  return h
}

async function get(pathAndQuery) {
  const res = await fetch(`${URL_BASE}/rest/v1/${pathAndQuery}`, { headers: headers() })
  if (!res.ok) throw new Error(`Supabase ${res.status} em ${pathAndQuery.split('?')[0]}: ${await res.text()}`)
  return res.json()
}

async function fetchVersions() {
  return get('dataset_versions?select=*&order=seq.asc')
}

async function fetchRecords(versionId) {
  const all = []
  for (let offset = 0; ; offset += 1000) {
    const rows = await get(`dataset_version_entries?select=entry_id,record&version_id=eq.${versionId}&order=entry_id.asc&limit=1000&offset=${offset}`)
    all.push(...rows)
    if (rows.length < 1000) break
  }
  return all
    .sort((a, b) => a.entry_id.localeCompare(b.entry_id, 'en', { numeric: true }))
    .map(r => Object.fromEntries(FIELDS.map(k => [k, r.record[k] ?? null])))
}

// ── Formatos ──

const refDate = (v) => v.reference_date || String(v.created_at).slice(0, 10)
const br = (iso) => iso.slice(0, 10).split('-').reverse().join('/')

function csvCell(v) {
  if (v === null || v === undefined) return ''
  const s = typeof v === 'boolean' ? (v ? 'true' : 'false') : String(v)
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

// Mesmo formato do download no CuraData (UTF-8 com BOM, para o Excel abrir com acento)
function toCSV(records) {
  const lines = [FIELDS.join(',')]
  records.forEach(r => lines.push(FIELDS.map(k => csvCell(r[k])).join(',')))
  return '﻿' + lines.join('\r\n') + '\r\n'
}

function citation(v) {
  const year = String(v.created_at).slice(0, 4)
  return `${META.dataset.authors.join('; ')}. ${META.dataset.title} (${META.dataset.name}), versão ${v.tag}. ${META.dataset.institution}, ${year}. ${META.dataset.url}`
}

function versionMeta(v) {
  return {
    tag: v.tag,
    title: v.title,
    changelog: v.changelog || '',
    reference_date: refDate(v),
    reconstructed: Boolean(v.reconstructed),
    created_at: v.created_at,
    record_count: v.entry_count,
    validated_count: v.stats?.validated ?? null,
    by_status: v.stats?.by_status || {},
    diff: v.stats?.diff || null,
  }
}

function toJSON(v, records) {
  return {
    dataset: META.dataset.name,
    title: META.dataset.title,
    version: v.tag,
    version_title: v.title,
    reference_date: refDate(v),
    reconstructed: Boolean(v.reconstructed),
    released_at: v.created_at,
    changelog: v.changelog || '',
    license: META.dataset.license,
    citation: citation(v),
    url: META.dataset.url,
    record_count: records.length,
    validated_count: records.filter(r => r.validado).length,
    fields: META.fields.map(({ key, label, type, description }) => ({ key, label, type, description })),
    records,
  }
}

function statusLine(byStatus = {}) {
  const order = ['adjudicated', 'divergence', 'reviewed', 'pending_review', 'in_progress', 'pending']
  return order.filter(k => byStatus[k]).map(k => `${META.curation_status[k] || k}: ${byStatus[k]}`).join(' · ')
}

function releaseNotes(v) {
  const m = versionMeta(v)
  return [
    `**${v.title}**`,
    '',
    `Retrato do DTS1 em ${br(m.reference_date)}${m.reconstructed ? ' (versão reconstruída a partir das datas de proposta, revisão e adjudicação)' : ''}.`,
    '',
    `- Repositórios: ${m.record_count}`,
    `- Validados: ${m.validated_count ?? '—'}`,
    `- Curadoria: ${statusLine(m.by_status)}`,
    '',
    '### O que mudou',
    '',
    m.changelog || '—',
    '',
    '### Arquivos',
    '',
    `- \`${PREFIX}-${v.tag}.csv\`: os ${m.record_count} repositórios`,
    `- \`${PREFIX}-${v.tag}-validados.csv\`: só os validados`,
    `- \`${PREFIX}-${v.tag}.json\`: os registros com metadados e dicionário de dados`,
    '',
    '### Como citar',
    '',
    citation(v),
    '',
  ].join('\n')
}

// ── Escrita ──

const changed = []
function write(rel, content) {
  const file = path.join(ROOT, rel)
  const old = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : null
  if (old === content) return false
  changed.push(rel)
  if (!DRY) {
    fs.mkdirSync(path.dirname(file), { recursive: true })
    fs.writeFileSync(file, content)
  }
  return true
}

const sha256 = (text) => crypto.createHash('sha256').update(text).digest('hex')

function replaceBlock(text, name, body) {
  const re = new RegExp(`(<!-- ${name}:start -->)[\\s\\S]*?(<!-- ${name}:end -->)`)
  return re.test(text) ? text.replace(re, `$1\n${body}\n$2`) : text
}

// ── Principal ──

const versions = await fetchVersions()
if (!versions.length) {
  console.log('Nenhuma versão no banco. Nada a fazer.')
  process.exit(0)
}

const newTags = []
const index = []

for (const v of versions) {
  const dir = `versions/${v.tag}`
  const csvRel = `${dir}/${PREFIX}-${v.tag}.csv`
  const exists = fs.existsSync(path.join(ROOT, csvRel))
  let files = null

  if (!exists) {
    const records = await fetchRecords(v.id)
    if (records.length !== v.entry_count) throw new Error(`${v.tag}: ${records.length} registros, esperado ${v.entry_count}`)
    const csv = toCSV(records)
    const csvVal = toCSV(records.filter(r => r.validado))
    write(csvRel, csv)
    write(`${dir}/${PREFIX}-${v.tag}-validados.csv`, csvVal)
    write(`${dir}/${PREFIX}-${v.tag}.json`, JSON.stringify(toJSON(v, records), null, 2) + '\n')
    files = { csv: sha256(csv), csv_validados: sha256(csvVal) }
    newTags.push(v.tag)
    console.log(`+ ${v.tag}: ${records.length} repositórios`)
  } else {
    const metaFile = path.join(ROOT, dir, 'version.json')
    files = fs.existsSync(metaFile) ? JSON.parse(fs.readFileSync(metaFile, 'utf8')).sha256 || null : null
  }

  // Metadados e notas: regravados sempre (título e changelog podem ter sido editados)
  const meta = { ...versionMeta(v), sha256: files }
  write(`${dir}/version.json`, JSON.stringify(meta, null, 2) + '\n')
  write(`${dir}/RELEASE_NOTES.md`, releaseNotes(v))
  index.push(meta)
}

// latest/
const latest = versions[versions.length - 1]
for (const suffix of ['.csv', '-validados.csv', '.json']) {
  const from = path.join(ROOT, 'versions', latest.tag, `${PREFIX}-${latest.tag}${suffix}`)
  const content = DRY && !fs.existsSync(from) ? '' : fs.readFileSync(from, 'utf8')
  write(`latest/${PREFIX}-latest${suffix}`, content)
}
write('latest/VERSION', `${latest.tag}\n`)

// Dicionário de dados (de data/fields.json, o mesmo arquivo que o CuraData usa)
const dict = ['# Dicionário de dados', '', `Colunas do ${META.dataset.name}, na ordem dos arquivos CSV. Gerado por \`scripts/sync-versions.mjs\` a partir de \`data/fields.json\`.`, '']
for (const g of META.groups) {
  const fs_ = META.fields.filter(f => f.group === g.id)
  if (!fs_.length) continue
  dict.push(`## ${g.label}`, '', '| Coluna | Nome | Tipo | Descrição |', '|---|---|---|---|')
  fs_.forEach(f => dict.push(`| \`${f.key}\` | ${f.label} | ${f.type} | ${f.description} |`))
  dict.push('')
}
dict.push('## Status da curadoria', '', '| Valor | Significado |', '|---|---|')
Object.entries(META.curation_status).forEach(([k, label]) => dict.push(`| \`${k}\` | ${label} |`))
dict.push('', '## Regra dos valores de classificação', '',
  '- **Repositório validado** (`validado = true`): valor final decidido na adjudicação, por unanimidade entre analista, revisor e adjudicador.',
  '- **Repositório em curadoria**: valor da mineração automatizada e da planilha de catalogação, ainda sem validação cruzada.',
  '', 'Para análises que dependem da classificação, use só os validados (arquivo `-validados.csv`).', '')
write('DATA_DICTIONARY.md', dict.join('\n'))

// Índice, changelog, citação e README
write('versions/index.json', JSON.stringify([...index].reverse(), null, 2) + '\n')

const changelog = ['# Changelog', '', 'Versões do DTS1, da mais nova para a mais antiga. Gerado por `scripts/sync-versions.mjs`.', '']
for (const m of [...index].reverse()) {
  changelog.push(`## ${m.tag} · ${m.title}`, '')
  changelog.push(`Retrato de ${br(m.reference_date)}${m.reconstructed ? ' (reconstruída)' : ''} · ${m.record_count} repositórios · ${m.validated_count ?? '—'} validados`, '')
  changelog.push(m.changelog || '—', '')
}
write('CHANGELOG.md', changelog.join('\n'))

const cffPath = path.join(ROOT, 'CITATION.cff')
if (fs.existsSync(cffPath)) {
  let cff = fs.readFileSync(cffPath, 'utf8')
  cff = cff.replace(/^version: .*$/m, `version: "${latest.tag}"`)
  cff = cff.replace(/^date-released: .*$/m, `date-released: "${String(latest.created_at).slice(0, 10)}"`)
  write('CITATION.cff', cff)
}

// Badges do README (shields.io estático: funciona com o repositório público ou privado)
const enc = (t) => encodeURIComponent(String(t).replace(/-/g, '--').replace(/_/g, '__'))
const badge = (label, message, color, extra = '') =>
  `![${label}](https://img.shields.io/badge/${enc(label)}-${enc(message)}-${color}?style=for-the-badge${extra})`

// O README existe em dois idiomas: README.md (inglês, principal) e README.pt-BR.md.
// Os blocos marcados com <!-- nome:start --> / <!-- nome:end --> são regravados nos dois.
const STATUS_EN = {
  pending: 'Pending', in_progress: 'In progress', pending_review: 'Awaiting review',
  reviewed: 'Reviewed', divergence: 'Divergence', adjudicated: 'Validated (adjudicated)',
}
const README_LANGS = [
  {
    file: 'README.md',
    date: (iso) => iso.slice(0, 10),
    status: (k) => STATUS_EN[k] || k,
    t: {
      version: 'version', snapshot: 'snapshot', repos: 'repositories', validated: 'validated',
      of: 'of', versions: 'versions', license: 'license',
      current: 'Current version', snapshotOf: 'Snapshot date', reposCol: 'Repositories',
      validatedCol: 'Validated', curation: 'Curation', title: 'Title', files: 'Files',
      folder: 'folder', reconstructed: 'reconstructed',
    },
  },
  {
    file: 'README.pt-BR.md',
    date: br,
    status: (k) => META.curation_status[k] || k,
    t: {
      version: 'versão', snapshot: 'retrato', repos: 'repositórios', validated: 'validados',
      of: 'de', versions: 'versões', license: 'licença',
      current: 'Versão atual', snapshotOf: 'Retrato de', reposCol: 'Repositórios',
      validatedCol: 'Validados', curation: 'Curadoria', title: 'Título', files: 'Arquivos',
      folder: 'pasta', reconstructed: 'reconstruída',
    },
  },
]

const lm = index[index.length - 1]
for (const lang of README_LANGS) {
  const readmePath = path.join(ROOT, lang.file)
  if (!fs.existsSync(readmePath)) continue
  const { t } = lang
  const statusText = ['adjudicated', 'divergence', 'reviewed', 'pending_review', 'in_progress', 'pending']
    .filter(k => lm.by_status?.[k]).map(k => `${lang.status(k)}: ${lm.by_status[k]}`).join(' · ')
  let readme = fs.readFileSync(readmePath, 'utf8')
  readme = replaceBlock(readme, 'badges', [
    badge(t.version, lm.tag, 'AF0421'),
    badge(t.snapshot, lang.date(lm.reference_date), '231F20'),
    badge(t.repos, lm.record_count, '231F20'),
    badge(t.validated, `${lm.validated_count ?? 0} ${t.of} ${lm.record_count}`, '231F20'),
    badge(t.versions, index.length, '231F20'),
    badge(t.license, META.dataset.license, 'E0E1E0', '&labelColor=231F20'),
  ].join('\n'))
  readme = replaceBlock(readme, 'latest', [
    `| ${t.current} | **${lm.tag}** · ${lm.title} |`,
    '|---|---|',
    `| ${t.snapshotOf} | ${lang.date(lm.reference_date)} |`,
    `| ${t.reposCol} | ${lm.record_count} |`,
    `| ${t.validatedCol} | ${lm.validated_count ?? '—'} |`,
    `| ${t.curation} | ${statusText} |`,
  ].join('\n'))
  readme = replaceBlock(readme, 'versions', [
    `| ${t.version[0].toUpperCase() + t.version.slice(1)} | ${t.title} | ${t.snapshotOf} | ${t.validatedCol} | ${t.files} |`,
    '|---|---|---|---|---|',
    ...[...index].reverse().map(m =>
      `| ${m.tag} | ${m.title}${m.reconstructed ? ` *(${t.reconstructed})*` : ''} | ${lang.date(m.reference_date)} | ${m.validated_count ?? '—'} | [${t.folder}](versions/${m.tag}) |`),
  ].join('\n'))
  write(lang.file, readme)
}

// Saída para a Action
if (process.env.GITHUB_OUTPUT) {
  fs.appendFileSync(process.env.GITHUB_OUTPUT, `new_tags=${newTags.join(' ')}\nlatest_tag=${latest.tag}\nall_tags=${index.map(m => m.tag).join(' ')}\n`)
}

console.log(changed.length ? `Arquivos alterados (${changed.length}):\n  ${changed.join('\n  ')}` : 'Nada mudou.')
if (DRY) console.log('(--dry-run: nada foi gravado)')

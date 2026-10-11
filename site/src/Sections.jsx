import { useState } from 'react'
import { CONTENT } from './content.js'
import { STATUS, STATUS_ORDER, tally, nf, fmtDate, fileBase, copy } from './data.js'

export function Section({ id, n, title, source, children }) {
  return (
    <section id={id} className="sec">
      <aside className="margin"><span className="secnum">{n}</span>{source && <code className="src" title="Arquivo de onde esta seção lê">{source}</code>}</aside>
      <div className="body"><h2>{title}</h2>{children}</div>
    </section>
  )
}

export function CopyBtn({ text, label = 'Copiar', className = 'link' }) {
  const [state, setState] = useState('idle')
  const go = async () => {
    setState((await copy(text)) ? 'ok' : 'fail')
    setTimeout(() => setState('idle'), 2200)
  }
  return <button className={className} onClick={go}>{state === 'ok' ? 'Copiado' : state === 'fail' ? 'Selecione e copie à mão' : label}</button>
}

function Bars({ title, records, keyName }) {
  const all = tally(records, keyName)
  const head = all.slice(0, 6)
  const rest = all.slice(6).reduce((s, [, n]) => s + n, 0)
  const items = rest ? [...head, ['Outros', rest]] : head
  return (
    <div className="bars">
      <h3>{title}</h3>
      <ol>
        {items.map(([v, n]) => (
          <li key={v}>
            <span className="bl">{v}</span>
            <span className="bn">{nf.format(n)} <small>{Math.round((n / records.length) * 100)}%</small></span>
            <i style={{ width: `${(n / records.length) * 100}%` }} />
          </li>
        ))}
      </ol>
    </div>
  )
}

export function Composition({ records }) {
  if (!records.length) return <Section id="composicao" n="1" title="Composição"><p className="note">Carregando…</p></Section>
  return (
    <Section id="composicao" n="1" title="Composição" source="registros da versão">
      <p className="lead">Como os {nf.format(records.length)} repositórios se distribuem em três colunas de classificação.</p>
      <div className="three">
        <Bars title="Framework" records={records} keyName="framework" />
        <Bars title="Técnica de integração" records={records} keyName="tec_integracao" />
        <Bars title="Estrutura do repositório" records={records} keyName="estrutura" />
      </div>
    </Section>
  )
}

export function Method({ version, fieldCount }) {
  return (
    <Section id="metodo" n="2" title="Método" source="CuraData, ADR-007">
      <p className="lead">
        {nf.format(CONTENT.candidates)} candidatos minerados resultaram em {version ? nf.format(version.record_count) : '—'} repositórios, descritos em {fieldCount} colunas.
      </p>
      <ol className="stages">
        {CONTENT.stages.map((s) => <li key={s.name}><h3>{s.name}</h3><p>{s.text}</p></li>)}
      </ol>
      <h3 className="sub">Como um registro é validado</h3>
      <dl className="roles">
        {CONTENT.roles.map(([r, t]) => <div key={r}><dt>{r}</dt><dd>{t}</dd></div>)}
      </dl>
      <p>{CONTENT.divergenceNote}</p>
    </Section>
  )
}

export function Versions({ versions, selected, onSelect, repoUrl }) {
  return (
    <Section id="versoes" n="4" title="Versões" source="versions/index.json">
      <p className="lead">Cada versão é um retrato fixo e citável. Escolha uma para ver a tabela e os downloads dela.</p>
      <ol className="vers">
        {versions.map((v) => {
          const d = v.diff || {}
          const lines = String(v.changelog || '').split('\n').map((l) => l.replace(/^-\s*/, '')).filter(Boolean)
          return (
            <li key={v.tag} className={v.tag === selected ? 'on' : ''}>
              <div className="vhead">
                <h3>{v.tag} <span>{v.title}</span></h3>
                <button className="link" aria-pressed={v.tag === selected} onClick={() => onSelect(v.tag)}>{v.tag === selected ? 'Em exibição' : 'Exibir esta versão'}</button>
              </div>
              <p className="meta">Retrato de {fmtDate(v.reference_date)}{v.reconstructed ? ', reconstruído a partir das datas de proposta, revisão e adjudicação' : ''}. Publicada em {fmtDate(v.created_at)}.</p>
              <div className="stack" role="img" aria-label={STATUS_ORDER.map((s) => `${v.by_status?.[s] || 0} ${STATUS[s].toLowerCase()}`).join(', ')}>
                {STATUS_ORDER.map((s) => v.by_status?.[s] ? <i key={s} className={`cell s-${s}`} style={{ flexGrow: v.by_status[s] }} title={`${STATUS[s]}: ${v.by_status[s]}`} /> : null)}
              </div>
              <p className="counts">{STATUS_ORDER.filter((s) => v.by_status?.[s]).map((s) => `${nf.format(v.by_status[s])} ${STATUS[s].toLowerCase()}`).join(', ')}.</p>
              <p className="diff">
                {d.previous_tag
                  ? <>Desde {d.previous_tag}: {nf.format(d.added)} adicionados, {nf.format(d.changed)} alterados, {nf.format(d.removed)} removidos{Object.keys(d.changed_fields || {}).length ? `. Campos alterados: ${Object.entries(d.changed_fields).map(([k, n]) => `${k} (${n})`).join(', ')}` : ''}.</>
                  : <>Primeira versão: {nf.format(d.added ?? v.record_count)} repositórios adicionados.</>}
              </p>
              {lines.length > 0 && (
                <details><summary>Changelog</summary><ul>{lines.map((l, i) => <li key={i}>{l}</li>)}</ul></details>
              )}
              <p className="vlinks"><a href={`./versions/${v.tag}/RELEASE_NOTES.md`}>Notas da versão</a><a href={`${repoUrl}/releases/tag/${v.tag}`}>Release no GitHub</a></p>
            </li>
          )
        })}
      </ol>
    </Section>
  )
}

export function Downloads({ version }) {
  if (!version) return null
  const b = fileBase(version.tag)
  const rows = [
    ['CSV completo', 'Todos os repositórios, uma linha cada.', `${b}.csv`, version.sha256?.csv],
    ['CSV só com validados', 'Apenas registros adjudicados por unanimidade.', `${b}-validados.csv`, version.sha256?.csv_validados],
    ['JSON', 'Registros, metadados e dicionário de campos.', `${b}.json`],
  ]
  return (
    <Section id="baixar" n="5" title={`Baixar ${version.tag}`} source={`versions/${version.tag}/`}>
      <p className="lead">Os arquivos abaixo são os mesmos publicados no repositório. Para reprodutibilidade, cite a versão.</p>
      <ul className="files">
        {rows.map(([name, desc, href, sha]) => (
          <li key={href}>
            <div><h3>{name}</h3><p>{desc}</p><code>{href.split('/').pop()}</code>
              {sha && <p className="sha">SHA-256 <code>{sha}</code> <CopyBtn text={sha} label="Copiar hash" /></p>}</div>
            <a className="btn" href={href} download>Baixar</a>
          </li>
        ))}
      </ul>
      <p className="meta">Sempre a mais recente: <a href="./latest/mfe-oss-dts1-latest.csv" download>CSV</a>, <a href="./latest/mfe-oss-dts1-latest-validados.csv" download>CSV de validados</a>, <a href="./latest/mfe-oss-dts1-latest.json" download>JSON</a>. Esses links mudam de conteúdo a cada versão nova; para citar, use os de cima.</p>
    </Section>
  )
}

export function Dictionary({ fields }) {
  const [q, setQ] = useState('')
  const t = q.trim().toLocaleLowerCase('pt-BR')
  const match = (f) => !t || [f.key, f.label, f.description].some((v) => String(v).toLocaleLowerCase('pt-BR').includes(t))
  return (
    <Section id="dicionario" n="6" title="Dicionário de dados" source="data/fields.json">
      <label className="field"><span>Filtrar colunas</span>
        <input type="search" value={q} placeholder="Nome ou descrição" onChange={(e) => setQ(e.target.value)} /></label>
      {fields.groups.map((g) => {
        const list = fields.fields.filter((f) => f.group === g.id && match(f))
        if (!list.length) return null
        return (
          <div key={g.id} className="dgroup">
            <h3>{g.label}</h3>
            <dl>{list.map((f) => (
              <div key={f.key}><dt><code>{f.key}</code><small>{f.type}</small></dt><dd><b>{f.label}.</b> {f.description}</dd></div>
            ))}</dl>
          </div>
        )
      })}
      {!fields.fields.some(match) && <p className="note">Nenhuma coluna encontrada para “{q}”.</p>}
    </Section>
  )
}

export function Cite({ meta, version }) {
  const [fmt, setFmt] = useState('bibtex')
  if (!version) return null
  const year = String(version.created_at || version.reference_date).slice(0, 4)
  const names = meta.authors.map((a) => { const p = a.split(' '); return { last: p.at(-1), first: p.slice(0, -1).join(' ') } })
  const title = `${meta.title} (${meta.name})`
  const texts = {
    bibtex: `@misc{${names[0].last.toLowerCase()}${year}mfeoss,\n  author    = {${names.map((n) => `${n.last}, ${n.first}`).join(' and ')}},\n  title     = {${title}},\n  year      = {${year}},\n  version   = {${version.tag}},\n  publisher = {${meta.institution}},\n  license   = {${meta.license}},\n  url       = {${meta.url}}\n}`,
    abnt: `${names.map((n) => `${n.last.toUpperCase()}, ${n.first}`).join('; ')}. ${title}. Versão ${version.tag}. ${meta.institution}, ${year}. Disponível em: ${meta.url}.`,
    texto: `${names.map((n) => `${n.last}, ${n.first}`).join('; ')} (${year}). ${title}. Versão ${version.tag}. ${meta.institution}. ${meta.url}`,
  }
  return (
    <Section id="citar" n="7" title="Como citar" source="CITATION.cff">
      <p className="lead">Inclua a versão que você usou: {version.tag}. A licença é {meta.license}, que permite reuso com atribuição.</p>
      <div className="seg" role="group" aria-label="Formato da citação">
        {[['bibtex', 'BibTeX'], ['abnt', 'ABNT'], ['texto', 'Texto']].map(([k, n]) => (
          <button key={k} aria-pressed={fmt === k} onClick={() => setFmt(k)}>{n}</button>
        ))}
      </div>
      <pre className="cite" tabIndex={0}>{texts[fmt]}</pre>
      <p className="acts"><CopyBtn text={texts[fmt]} label="Copiar citação" className="btn solid" /><a className="btn" href="./CITATION.cff" download>Baixar CITATION.cff</a></p>
    </Section>
  )
}

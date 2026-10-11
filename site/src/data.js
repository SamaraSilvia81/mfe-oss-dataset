import { useEffect, useState } from 'react'

export const STATUS = {
  adjudicated: 'Validado',
  divergence: 'Em divergência',
  pending_review: 'Aguardando revisão',
  pending: 'Pendente',
  reviewed: 'Revisado',
  in_progress: 'Em andamento',
}
export const STATUS_ORDER = ['adjudicated', 'divergence', 'pending_review', 'pending']

export const nf = new Intl.NumberFormat('pt-BR')
export const fmtDate = (v) => {
  if (!v) return '—'
  const [y, m, d] = String(v).slice(0, 10).split('-')
  return `${d}/${m}/${y}`
}
export const statusOf = (r) => r.curadoria_status || (r.validado ? 'adjudicated' : 'pending')
export const fileBase = (tag) => `./versions/${tag}/mfe-oss-dts1-${tag}`

async function getJSON(path) {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`${path} respondeu HTTP ${res.status}`)
  return res.json()
}

// Lê versions/index.json e data/fields.json.
export function useManifest() {
  const [state, setState] = useState({ loading: true })
  useEffect(() => {
    Promise.all([getJSON('./versions/index.json'), getJSON('./data/fields.json')])
      .then(([versions, fields]) => setState({ versions, fields }))
      .catch((error) => setState({ error: error.message }))
  }, [])
  return state
}

// Lê o JSON completo da versão escolhida (com cache por tag).
const cache = new Map()
export function useVersionData(tag) {
  const [state, setState] = useState({ loading: true })
  useEffect(() => {
    if (!tag) return
    if (cache.has(tag)) return setState({ data: cache.get(tag) })
    let alive = true
    setState({ loading: true })
    getJSON(`${fileBase(tag)}.json`)
      .then((data) => { cache.set(tag, data); if (alive) setState({ data }) })
      .catch((error) => alive && setState({ error: error.message }))
    return () => { alive = false }
  }, [tag])
  return state
}

export function tally(records, key) {
  const m = new Map()
  for (const r of records) {
    const v = r[key]
    if (v === null || v === undefined || String(v).trim() === '') continue
    m.set(v, (m.get(v) || 0) + 1)
  }
  return [...m.entries()].sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0]), 'pt-BR'))
}

export function toCSV(records, keys) {
  const cell = (v) => {
    const s = v === null || v === undefined ? '' : String(v)
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  return '\uFEFF' + [keys.join(','), ...records.map((r) => keys.map((k) => cell(r[k])).join(','))].join('\r\n')
}

export function download(name, text, type = 'text/csv;charset=utf-8') {
  const url = URL.createObjectURL(new Blob([text], { type }))
  const a = Object.assign(document.createElement('a'), { href: url, download: name })
  document.body.append(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export async function copy(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    const t = Object.assign(document.createElement('textarea'), { value: text })
    t.style.cssText = 'position:fixed;opacity:0'
    document.body.append(t)
    t.select()
    const ok = document.execCommand('copy')
    t.remove()
    return ok
  }
}

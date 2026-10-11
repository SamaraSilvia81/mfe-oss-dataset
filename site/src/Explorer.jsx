import { useEffect, useMemo, useRef, useState } from 'react'
import { Section, CopyBtn } from './Sections.jsx'
import { STATUS, STATUS_ORDER, statusOf, tally, nf, fmtDate, toCSV, download } from './data.js'

const COLS = [['id', 'ID'], ['nome', 'Repositório'], ['framework', 'Framework'], ['tec_integracao', 'Integração'], ['estrutura', 'Estrutura'], ['stars', 'Stars'], ['curadoria_status', 'Status']]
const DETAIL = ['criado_em', 'data_commit_ultimo', 'forks', 'commits', 'contribuidores', 'licenca', 'desenvolvido_por', 'finalidade', 'estilo_api', 'qtd_modulos_amplo', 'documentacao_valida', 'evidencias', 'conteudo_repos']
const EMPTY = { framework: '', tec_integracao: '', estrutura: '', curadoria_status: '' }
const PAGE = 15

export default function Explorer({ records, fields, tag, focus, loading }) {
  const [q, setQ] = useState('')
  const [f, setF] = useState(EMPTY)
  const [sort, setSort] = useState({ key: 'id', dir: 1 })
  const [page, setPage] = useState(1)
  const [open, setOpen] = useState(null)
  const top = useRef(null)
  const rows = useMemo(() => records.map((r) => ({ ...r, curadoria_status: statusOf(r) })), [records])
  const label = useMemo(() => Object.fromEntries(fields.fields.map((x) => [x.key, x])), [fields])

  useEffect(() => {
    if (!focus) return
    setQ(focus.id); setF(EMPTY); setOpen(focus.id); setPage(1)
    const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    top.current?.scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'start' })
  }, [focus])

  const filtered = useMemo(() => {
    const t = q.trim().toLocaleLowerCase('pt-BR')
    const list = rows.filter((r) =>
      (!t || [r.id, r.nome, r.framework, r.tec_integracao].some((v) => String(v ?? '').toLocaleLowerCase('pt-BR').includes(t))) &&
      Object.keys(EMPTY).every((k) => !f[k] || String(r[k]) === f[k]))
    const { key, dir } = sort
    return list.sort((a, b) => {
      const x = a[key], y = b[key]
      if (x == null || x === '') return 1
      if (y == null || y === '') return -1
      return (typeof x === 'number' && typeof y === 'number' ? x - y : String(x).localeCompare(String(y), 'pt-BR', { numeric: true })) * dir
    })
  }, [rows, q, f, sort])

  const pages = Math.max(1, Math.ceil(filtered.length / PAGE))
  const cur = Math.min(page, pages)
  const visible = filtered.slice((cur - 1) * PAGE, cur * PAGE)
  const active = q || Object.values(f).some(Boolean)
  const opts = (key) => key === 'curadoria_status'
    ? STATUS_ORDER.map((s) => [s, tally(rows, key).find(([v]) => v === s)?.[1] || 0]).filter(([, n]) => n)
    : tally(rows, key)
  const setFilter = (k, v) => { setF({ ...f, [k]: v }); setPage(1) }
  const head = (k) => sort.key === k ? (sort.dir === 1 ? 'ascending' : 'descending') : 'none'

  return (
    <Section id="explorar" n="3" title="Explorar os repositórios" source={`versions/${tag}/…${tag}.json`}>
      <div ref={top} className="scroll-anchor" />
      <div className="filters">
        <label className="field grow"><span>Buscar</span>
          <input type="search" value={q} placeholder="ID, repositório, framework…" onChange={(e) => { setQ(e.target.value); setPage(1) }} /></label>
        {[['framework', 'Framework'], ['tec_integracao', 'Integração'], ['estrutura', 'Estrutura'], ['curadoria_status', 'Status']].map(([k, name]) => (
          <label className="field" key={k}><span>{name}</span>
            <select value={f[k]} onChange={(e) => setFilter(k, e.target.value)}>
              <option value="">Todos</option>
              {opts(k).map(([v, n]) => <option key={v} value={v}>{k === 'curadoria_status' ? STATUS[v] : v} ({nf.format(n)})</option>)}
            </select></label>
        ))}
      </div>
      <div className="bar">
        <p aria-live="polite">{loading ? 'Carregando…' : `${nf.format(filtered.length)} de ${nf.format(rows.length)} repositórios`}</p>
        <div className="acts">
          {active && <button className="link" onClick={() => { setQ(''); setF(EMPTY); setPage(1) }}>Limpar filtros</button>}
          <button className="link" disabled={!filtered.length} onClick={() => download(`mfe-oss-dts1-${tag}-filtrado.csv`, toCSV(filtered, fields.fields.map((x) => x.key)))}>
            Baixar seleção em CSV
          </button>
        </div>
      </div>
      <div className="tablewrap">
        <table>
          <thead><tr>{COLS.map(([k, name]) => (
            <th key={k} scope="col" aria-sort={head(k)} className={k === 'stars' ? 'num' : ''}>
              <button onClick={() => setSort({ key: k, dir: sort.key === k ? -sort.dir : 1 })}>{name}<i aria-hidden="true">{head(k) === 'ascending' ? '▲' : head(k) === 'descending' ? '▼' : ''}</i></button>
            </th>))}</tr></thead>
          <tbody>
            {!visible.length && <tr><td colSpan={7} className="empty">Nenhum repositório corresponde. Remova um filtro ou limpe a busca.</td></tr>}
            {visible.flatMap((r) => {
              const isOpen = open === r.id
              return [
                <tr key={r.id} className={isOpen ? 'on' : ''}>
                  <td className="id">{r.id}</td>
                  <td><button className="expand" aria-expanded={isOpen} onClick={() => setOpen(isOpen ? null : r.id)}>{r.nome}</button></td>
                  <td>{r.framework || '—'}</td><td>{r.tec_integracao || '—'}</td><td>{r.estrutura || '—'}</td>
                  <td className="num">{r.stars == null ? '—' : nf.format(r.stars)}</td>
                  <td><span className={`tag s-${r.curadoria_status}`}><i className="cell" />{STATUS[r.curadoria_status]}</span></td>
                </tr>,
                isOpen && (
                  <tr key={`${r.id}-d`} className="detail"><td colSpan={7}>
                    <dl>
                      {DETAIL.filter((k) => r[k] != null && r[k] !== '').map((k) => (
                        <div key={k}><dt>{label[k]?.label || k}</dt><dd>{label[k]?.type === 'data' ? fmtDate(r[k]) : typeof r[k] === 'number' ? nf.format(r[k]) : String(r[k])}</dd></div>
                      ))}
                    </dl>
                    <p className="detail-links"><a href={r.url} target="_blank" rel="noreferrer">Abrir no GitHub</a><CopyBtn text={r.url} label="Copiar URL" /></p>
                  </td></tr>
                ),
              ]
            })}
          </tbody>
        </table>
      </div>
      <nav className="pager" aria-label="Páginas da tabela">
        <button disabled={cur <= 1} onClick={() => setPage(cur - 1)}>Anterior</button>
        <span>Página {cur} de {pages}</span>
        <button disabled={cur >= pages} onClick={() => setPage(cur + 1)}>Próxima</button>
      </nav>
    </Section>
  )
}

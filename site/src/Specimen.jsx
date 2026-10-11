import { memo, useMemo, useState } from 'react'
import { STATUS, STATUS_ORDER, statusOf, nf } from './data.js'

const Cell = memo(({ i, s }) => <span className={`cell s-${s}`} data-i={i} style={{ '--d': `${Math.floor(i / 50) * 70}ms` }} />)

// Um quadrado por repositório, uma linha por lote. Dados lidos da versão escolhida.
export default function Specimen({ records, loading, error, onPick }) {
  const [hover, setHover] = useState(null)
  const rows = useMemo(() => {
    const byLote = new Map()
    records.forEach((r, i) => {
      const k = r.lote ?? Math.floor(i / 50) + 1
      if (!byLote.has(k)) byLote.set(k, [])
      byLote.get(k).push({ r, i, s: statusOf(r) })
    })
    return [...byLote.entries()].sort((a, b) => a[0] - b[0])
  }, [records])
  const counts = useMemo(() => {
    const c = {}
    records.forEach((r) => { const s = statusOf(r); c[s] = (c[s] || 0) + 1 })
    return c
  }, [records])
  const shown = hover != null ? records[hover] : null
  const find = (e) => {
    const i = e.target?.dataset?.i
    return i === undefined ? null : Number(i)
  }

  return (
    <figure className="specimen">
      <div
        className="grid"
        role="img"
        aria-label={`${nf.format(records.length)} repositórios, um quadrado cada, agrupados por lote. ${STATUS_ORDER.map((s) => `${counts[s] || 0} ${STATUS[s].toLowerCase()}`).join(', ')}.`}
        onPointerOver={(e) => { const i = find(e); if (i !== null) setHover(i) }}
        onPointerLeave={() => setHover(null)}
        onClick={(e) => { const i = find(e); if (i !== null) onPick(records[i]) }}
      >
        {loading && !records.length && <p className="note">Carregando repositórios…</p>}
        {error && <p className="note err">{error}</p>}
        {rows.map(([lote, cells]) => (
          <div className="lane" key={lote}>
            <span className="lote">L{lote}</span>
            <div className="cells">{cells.map(({ r, i, s }) => <Cell key={r.id} i={i} s={s} />)}</div>
          </div>
        ))}
      </div>
      <figcaption>
        <p className="readout" aria-live="off">
          {shown ? <><b>{shown.id}</b> {shown.nome} <span>{STATUS[statusOf(shown)]}</span></> : 'Cada quadrado é um repositório; cada linha, um lote de 50. Clique em um para abri-lo no explorador.'}
        </p>
        <ul className="legend">
          {STATUS_ORDER.map((s) => <li key={s}><i className={`cell s-${s}`} />{STATUS[s]} <b>{nf.format(counts[s] || 0)}</b></li>)}
        </ul>
      </figcaption>
    </figure>
  )
}

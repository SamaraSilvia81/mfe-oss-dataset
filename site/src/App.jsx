import { useMemo, useState } from 'react'
import { useManifest, useVersionData, fmtDate, nf, fileBase } from './data.js'
import { CONTENT } from './content.js'
import Specimen from './Specimen.jsx'
import Explorer from './Explorer.jsx'
import { Composition, Method, Versions, Downloads, Dictionary, Cite } from './Sections.jsx'

const NAV = [['composicao', 'Composição'], ['metodo', 'Método'], ['explorar', 'Explorar'], ['versoes', 'Versões'], ['baixar', 'Baixar'], ['dicionario', 'Dicionário'], ['citar', 'Citar']]

export default function App() {
  const manifest = useManifest()
  const [picked, setPicked] = useState(null)
  const [focus, setFocus] = useState(null)
  const tag = picked ?? manifest.versions?.[0]?.tag
  const version = manifest.versions?.find((v) => v.tag === tag)
  const loaded = useVersionData(tag)
  const records = useMemo(() => loaded.data?.records ?? [], [loaded.data])

  if (manifest.error) {
    return (
      <main className="fail">
        <h1>Não foi possível ler os arquivos do dataset</h1>
        <p>{manifest.error}</p>
        <p>O site busca <code>versions/index.json</code> e <code>data/fields.json</code>. Abra pelo servidor (<code>npm run dev</code> dentro da pasta <code>site</code>), não clicando duas vezes em um arquivo HTML.</p>
      </main>
    )
  }
  if (!manifest.versions) return <main className="fail"><p>Carregando versões…</p></main>

  const meta = manifest.fields.dataset
  const authors = (meta.authors || []).join(', ')

  return (
    <>
      <header className="top">
        <a className="brand" href="#topo" aria-label="DTS1 · MFE-OSS, início">
          <b>DTS1</b> <span>MFE-OSS</span>
        </a>
        <nav aria-label="Seções">
          {NAV.map(([id, label]) => <a key={id} href={`#${id}`}>{label}</a>)}
        </nav>
        <label className="vsel">
          <span>Versão</span>
          <select value={tag} onChange={(e) => setPicked(e.target.value)}>
            {manifest.versions.map((v) => <option key={v.tag} value={v.tag}>{v.tag}</option>)}
          </select>
        </label>
      </header>

      <main id="topo">
        <section className="hero">
          <h1>{meta.title.split(':')[0]}</h1>
          <p className="subtitle">{meta.title.split(':').slice(1).join(':').trim()}</p>
          <div className="front">
            <p className="byline">{authors}<br />{meta.institution}</p>
            <div className="lede">
            <p className="abstract">{CONTENT.abstract}</p>
            <div className="cta">
              <a className="btn solid" href={`${fileBase(tag)}.csv`} download>Baixar {tag} em CSV</a>
              <a className="btn" href="#explorar">Explorar os repositórios</a>
            </div>
            <p className="stamp">
              {version && <>{tag}, retrato de {fmtDate(version.reference_date)}{version.reconstructed ? ' (reconstruído)' : ''}. {nf.format(version.record_count)} repositórios, {nf.format(version.validated_count)} validados. </>}
              Licença {meta.license}.
            </p>
            </div>
          </div>
          <Specimen records={records} loading={loaded.loading} error={loaded.error} onPick={(r) => setFocus({ id: r.id, n: Date.now() })} />
        </section>

        {loaded.error && <p className="note err">Falha ao ler a versão {tag}: {loaded.error}</p>}

        <Composition records={records} />
        <Method version={version} fieldCount={manifest.fields.fields.length} />
        <Explorer records={records} fields={manifest.fields} tag={tag} focus={focus} loading={loaded.loading} />
        <Versions versions={manifest.versions} selected={tag} onSelect={setPicked} repoUrl={CONTENT.repoUrl} />
        <Downloads version={version} />
        <Dictionary fields={manifest.fields} />
        <Cite meta={meta} version={version} />
      </main>

      <footer className="foot">
        <p>{meta.name}. {meta.institution}. Dados em {meta.license}.</p>
        <p><a href={CONTENT.repoUrl}>Repositório</a> <a href="./CITATION.cff">CITATION.cff</a> <a href="./CHANGELOG.md">Changelog</a> <a href="./DATA_DICTIONARY.md">Dicionário em Markdown</a></p>
      </footer>
    </>
  )
}

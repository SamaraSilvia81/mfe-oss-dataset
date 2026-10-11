import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// O site fica em /site; os dados ficam na raiz do repositório.
// Em desenvolvimento, esses caminhos são servidos direto da raiz.
// No build, são copiados para dist/, então cada deploy publica os arquivos atuais.
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const SHARED = ['versions', 'latest', 'data', 'CITATION.cff', 'LICENSE', 'CHANGELOG.md', 'DATA_DICTIONARY.md']
const TYPES = { '.json': 'application/json', '.csv': 'text/csv; charset=utf-8', '.md': 'text/markdown; charset=utf-8', '.cff': 'text/plain; charset=utf-8' }

function datasetFiles() {
  let outDir = 'dist'
  return {
    name: 'dataset-files',
    configResolved(config) { outDir = path.resolve(config.root, config.build.outDir) },
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const rel = decodeURIComponent((req.url || '').split('?')[0]).replace(/^\/+/, '')
        if (!SHARED.includes(rel.split('/')[0])) return next()
        const file = path.join(repoRoot, rel)
        if (!file.startsWith(repoRoot) || !fs.existsSync(file) || !fs.statSync(file).isFile()) return next()
        res.setHeader('Content-Type', TYPES[path.extname(file)] || 'text/plain; charset=utf-8')
        fs.createReadStream(file).pipe(res)
      })
    },
    closeBundle() {
      for (const name of SHARED) {
        const from = path.join(repoRoot, name)
        if (fs.existsSync(from)) fs.cpSync(from, path.join(outDir, name), { recursive: true })
      }
    },
  }
}

export default defineConfig({ base: './', plugins: [react(), datasetFiles()] })

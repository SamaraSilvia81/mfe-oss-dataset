# Site do DTS1 · MFE-OSS

React + Vite, na pasta `site/`. Não tem cópia dos dados: a interface lê `versions/index.json`, `data/fields.json` e o JSON de cada versão direto da raiz do repositório. Quando a Action de sincronização gera uma versão nova, o próximo build do site já a mostra (lista de versões, tabela, números, downloads e citação).

## Rodar no Windows

1. Instale o Node.js LTS (nodejs.org), se ainda não tiver.
2. Abra a pasta `mfe-oss-dataset` no VS Code e abra o terminal (**Terminal → Novo Terminal**).
3. Entre na pasta do site e instale as dependências (só na primeira vez):

   ```powershell
   cd site
   npm install
   ```

4. Rode o servidor de desenvolvimento:

   ```powershell
   npm run dev
   ```

5. Abra o endereço que aparecer (normalmente `http://localhost:5173`). Para encerrar, `Ctrl+C` no terminal.

Para gerar a versão final: `npm run build`. O resultado fica em `site/dist` e já inclui `versions/`, `latest/`, `data/` e `CITATION.cff`.

## Arquivos que você vai editar

| Arquivo | O que tem |
|---|---|
| `site/src/content.js` | Resumo, etapas do método, papéis da curadoria, número de candidatos minerados (2.793) |
| `site/src/styles.css` | Paleta (no topo, em `:root`) e todo o visual |
| `site/src/Sections.jsx` | Composição, método, versões, downloads, dicionário e citação |
| `site/src/Explorer.jsx` | Tabela de repositórios |
| `site/src/Specimen.jsx` | Grade de quadrados da abertura |

Autores, licença e URL da citação vêm de `data/fields.json` (campo `dataset`).

## Publicar

**GitHub Pages** (quando o repositório for público): em Settings → Pages, escolha Source = GitHub Actions. O workflow `.github/workflows/deploy-site.yml` publica a cada mudança no site ou nos dados e depois de cada sincronização. Em repositório privado de organização, o Pages exige plano pago.

**Vercel**: importe o repositório, defina Root Directory = `site`, Build Command = `npm run build`, Output Directory = `dist`. Mantenha ligada a opção "Include source files outside of the Root Directory in the Build Step" (vem ligada por padrão), porque o build copia `versions/`, `latest/` e `data/` da raiz. A Vercel refaz o deploy a cada commit, inclusive os do bot de sincronização.

## Arquivos antigos

O site anterior (`index.html`, `styles.css`, `app.js` na raiz) foi removido. Apague esses três arquivos do repositório antes de publicar, para não conflitarem com o novo.

# Dicionário de dados

Colunas do DTS1 · MFE-OSS, na ordem dos arquivos CSV. Gerado por `scripts/sync-versions.mjs` a partir de `data/fields.json`.

## Identificação

| Coluna | Nome | Tipo | Descrição |
|---|---|---|---|
| `id` | ID | texto | Identificador do repositório no DTS1 (MFE-001 a MFE-455). |
| `nome` | Nome | texto | Dono e nome do repositório (owner/repo). |
| `url` | URL | texto | Endereço do repositório. |
| `lote` | Lote | número | Lote de curadoria (50 repositórios por lote). |
| `status_repositorio` | Status do repositório | texto | Situação do repositório na coleta (ativo, arquivado etc.). |

## Atividade

| Coluna | Nome | Tipo | Descrição |
|---|---|---|---|
| `criado_em` | Criado em | data | Data de criação do repositório. |
| `data_commit_primeiro` | Primeiro commit | data | Data do primeiro commit. |
| `data_commit_ultimo` | Último commit | data | Data do último commit na coleta. |
| `hash_commit_primeiro` | Hash do primeiro commit | texto | Hash curto do primeiro commit. |
| `hash_commit_ultimo` | Hash do último commit | texto | Hash curto do último commit na coleta. |

## Métricas

| Coluna | Nome | Tipo | Descrição |
|---|---|---|---|
| `stars` | Stars | número | Estrelas no GitHub na coleta. |
| `forks` | Forks | número | Forks na coleta. |
| `commits` | Commits | número | Total de commits. |
| `contribuidores` | Contribuidores | número | Total de contribuidores. |
| `prs_totais` | PRs | número | Total de pull requests. |
| `issues_open` | Issues abertas | número | Issues abertas na coleta. |
| `issues_closed` | Issues fechadas | número | Issues fechadas na coleta. |
| `churn_semanal` | Churn semanal | número | Linhas alteradas por semana. |

## Classificação

| Coluna | Nome | Tipo | Descrição |
|---|---|---|---|
| `framework` | Framework | texto | Framework principal da interface. |
| `tec_integracao` | Técnica de integração | texto | Como os microfrontends são compostos (Module Federation, Single-SPA etc.). |
| `estrutura` | Estrutura | texto | Monorepo ou polyrepo. |
| `evidencias` | Evidências da estrutura | texto | Ferramentas que evidenciam a estrutura (Nx, Lerna, workspaces etc.). |
| `licenca` | Licença | texto | Licença declarada no repositório. |
| `categ_licenca` | Categoria da licença | texto | Permissiva, copyleft ou outra. |
| `desenvolvido_por` | Desenvolvido por | texto | Comunidade, empresa, pessoa etc. |
| `finalidade` | Finalidade | texto | Produção, estudo, demonstração etc. |
| `estilo_api` | Estilo de API | texto | Como o frontend fala com o backend (REST, GraphQL etc.). |
| `qtd_modulos_amplo` | Módulos MFE (amplo) | número | Quantidade de módulos pelo critério amplo [MET-DEC-001]. |
| `qtd_modulos_restrito` | Módulos MFE (restrito) | número | Quantidade de módulos pelo critério restrito [MET-DEC-001]. |
| `documentacao_valida` | Documentação válida | texto | Avaliação da documentação do repositório. |
| `estrutura_pastas` | Estrutura de pastas | texto | Avaliação da organização de pastas e arquitetura. |
| `escopo_definido` | Escopo definido | texto | Se o objetivo do repositório está claro. |
| `conteudo_repos` | Conteúdo do repositório | texto | Descrição do que o repositório contém. |
| `detalhes_mfe` | Detalhes do MFE | texto | Evidências e detalhes da implementação de microfrontend. |

## Curadoria

| Coluna | Nome | Tipo | Descrição |
|---|---|---|---|
| `curadoria_status` | Status da curadoria | texto | pending, in_progress, pending_review, reviewed, divergence ou adjudicated. |
| `validado` | Validado | booleano | true quando a curadoria terminou (adjudicado). Só os validados têm classificação revisada por três curadores. |
| `data_validacao` | Data da validação | data | Data da adjudicação (AAAA-MM-DD). |

## Status da curadoria

| Valor | Significado |
|---|---|
| `pending` | Pendente |
| `in_progress` | Em andamento |
| `pending_review` | Aguardando revisão |
| `reviewed` | Revisado |
| `divergence` | Divergência |
| `adjudicated` | Validado (adjudicado) |

## Regra dos valores de classificação

- **Repositório validado** (`validado = true`): valor final decidido na adjudicação, por unanimidade entre analista, revisor e adjudicador.
- **Repositório em curadoria**: valor da mineração automatizada e da planilha de catalogação, ainda sem validação cruzada.

Para análises que dependem da classificação, use só os validados (arquivo `-validados.csv`).

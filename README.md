<div align="center">

<h1>DTS1 · MFE-OSS</h1>

<p><b>Mapping the Microfrontend Ecosystem: A Dataset of Open-Source Projects</b></p>

<!-- badges:start -->
<!-- badges:end -->

![Microfrontends](https://img.shields.io/badge/Microfrontends-171717?style=for-the-badge)
![MSR](https://img.shields.io/badge/Mineração%20de%20Repositórios-171717?style=for-the-badge)
![GitHub](https://img.shields.io/badge/GitHub-171717?style=for-the-badge&logo=github&logoColor=FFFFFF)
![CIn/UFPE](https://img.shields.io/badge/CIn-UFPE-AF0421?style=for-the-badge)

</div>

<br>

Dataset de projetos open-source de **microfrontend** no GitHub, construído na pesquisa de mestrado de **Samara Silvia Sabino** no Centro de Informática da UFPE (CIn/UFPE), sob orientação do **Prof. Vinicius Cardoso Garcia**.

O DTS1 parte de **2.793 candidatos** encontrados por mineração automatizada e chega a **455 repositórios**, que passam por curadoria manual com validação cruzada entre três curadores.

<!-- latest:start -->
<!-- latest:end -->

## Baixar

| Arquivo | Conteúdo |
|---|---|
| [`latest/mfe-oss-dts1-latest.csv`](latest/mfe-oss-dts1-latest.csv) | versão mais nova, os 455 repositórios |
| [`latest/mfe-oss-dts1-latest-validados.csv`](latest/mfe-oss-dts1-latest-validados.csv) | versão mais nova, só os validados |
| [`latest/mfe-oss-dts1-latest.json`](latest/mfe-oss-dts1-latest.json) | versão mais nova em JSON, com metadados e dicionário |
| [Releases](../../releases) | cada versão congelada, com os arquivos anexos |

Para reproduzir uma análise, use sempre uma **versão numerada** (pasta `versions/` ou Releases), e não a `latest/`, que muda a cada versão nova.

## Versões

Cada versão congela os 455 repositórios como estavam numa data. Versões não mudam depois de criadas: uma correção vira uma versão nova.

<!-- versions:start -->
<!-- versions:end -->

O que mudou em cada uma está no [CHANGELOG](CHANGELOG.md).

**Número da versão:**
- **correção** (v1.0.**1**): ajustes pontuais em valores já publicados;
- **avanço** (v1.**1**.0): repositórios validados, reclassificados ou que mudaram de etapa;
- **mudança de critério** (v**2**.0.0): colunas novas ou mudança na regra de classificação.

Versões marcadas como *reconstruídas* retratam uma data passada. Foram remontadas a partir das datas de proposta, revisão e adjudicação de cada repositório.

## Como o dataset é construído

1. **Mineração e identificação.** Busca no GitHub por heurísticas de microfrontend (Module Federation, Single-SPA, Bit, entre outras) e extração de metadados.
2. **Filtragem e validação.** Filtro de maturidade, *quality gate* e *sanity check*. Cada fase guarda os aprovados e os rejeitados.
3. **Mineração profunda.** Metadados detalhados dos aprovados.
4. **Curadoria manual.** Cada repositório passa por três pessoas: **analista** (cataloga), **revisor** (confere) e **adjudicador** (decide). O valor só é validado com unanimidade entre os três. Sem unanimidade, abre-se uma reunião; se ainda assim não houver acordo, decide o orientador.

A curadoria é feita no **CuraData**, ferramenta construída para esta pesquisa. As versões publicadas aqui saem direto dele.

## Colunas

As 37 colunas estão descritas no [dicionário de dados](DATA_DICTIONARY.md). Resumo:

- **Identificação e atividade:** id, nome, URL, lote, datas e hashes de commit.
- **Métricas:** stars, forks, commits, contribuidores, PRs, issues e churn.
- **Classificação:** framework, técnica de integração, estrutura (monorepo ou polyrepo), evidências, licença, quem desenvolve, finalidade, estilo de API, quantidade de módulos e avaliação de documentação, organização e escopo.
- **Curadoria:** status, `validado` e data da validação.

**Atenção:** só os repositórios com `validado = true` têm classificação revisada pelos três curadores. Nos outros, a classificação ainda é a da mineração.

## Como citar

Use o botão **Cite this repository**, no menu ao lado, ou:

> Samara Silvia Sabino; Vinicius Cardoso Garcia. *Mapping the Microfrontend Ecosystem: A Dataset of Open-Source Projects* (DTS1 · MFE-OSS), versão vX.Y.Z. Centro de Informática, Universidade Federal de Pernambuco (CIn/UFPE). https://github.com/mfe-guidelines-ufpe/mfe-oss-dataset

Sempre informe a versão usada.

## Licença

Os dados estão sob [CC BY 4.0](LICENSE): podem ser usados e adaptados para qualquer fim, com atribuição.

## Manutenção

Os arquivos deste repositório são gerados automaticamente. Uma GitHub Action (`.github/workflows/sync-versions.yml`) roda todo dia, lê as versões do CuraData e:
- grava os arquivos de cada versão nova;
- atualiza a `latest/`, o changelog, a citação e esta página;
- cria uma Release para cada versão.

Não edite os arquivos gerados à mão: a próxima sincronização sobrescreve.

Encontrou um erro num repositório? Abra uma [issue](../../issues) com o ID (por exemplo, `MFE-042`), o campo e o valor correto.

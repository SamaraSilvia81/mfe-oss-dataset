<div align="center">

[English](README.md) · **Português**

<h1>DTS1 · MFE-OSS · Pipeline de mineração</h1>

<p><b>Scripts e arquivos intermediários que produziram os 455 repositórios do dataset</b></p>

![Python](https://img.shields.io/badge/Python-3.10%2B-231F20?style=for-the-badge&logo=python&logoColor=FFFFFF)
![GitHub API](https://img.shields.io/badge/GitHub%20API-231F20?style=for-the-badge&logo=github&logoColor=FFFFFF)
![Google Colab](https://img.shields.io/badge/Google%20Colab-231F20?style=for-the-badge&logo=googlecolab&logoColor=FFFFFF)
![licença](https://img.shields.io/badge/licen%C3%A7a-MIT-E0E1E0?style=for-the-badge&labelColor=231F20)

</div>

<br>

Esta pasta reúne a pipeline de mineração do **DTS1 · MFE-OSS**, da primeira busca no GitHub até a planilha que foi para a curadoria manual. Cada etapa guarda os repositórios aprovados e os rejeitados, então qualquer número do funil pode ser conferido num arquivo.

O dataset em si, com as versões, está na [raiz deste repositório](../README.pt-BR.md). Esta pasta era o repositório `msr-mfe-oss-dataset` e foi trazida para cá com todo o histórico de commits.

## Funil

| Etapa | Script | Repositórios | Removidos |
|---|---|---|---|
| Busca por heurísticas | `01_mining_heuristics.py` | 2.793 | |
| Filtro de maturidade ($I_1$–$I_3$) | `04_filter_maturity.py` | 1.205 | 1.578 |
| *Quality gate* ($I_4$–$I_5$) | `06_quality_gate.py` | 842 | 363 |
| *Sanity check* ($I_6$) | `07_sanity_check.py` | 455 | 387 |

**Por que os repositórios saíram**

- **Maturidade:** último commit antes de 2021, sem contribuidores ou com menos de 10 commits.
- **Quality gate:** 187 sem README, 114 com documentação em outro idioma, 60 insubstanciais (menos de 100 KB) e 2 arquivados.
- **Sanity check:** 238 sem `package.json` inspecionável e 149 sem evidência estrutural de orquestração (`remotes`/`exposes`, dependências reais, estrutura de pastas).

## Estrutura

```
pipeline/
├── src/
│   ├── 01_miner&id/      etapa 1: mineração e identificação
│   ├── 02_filter&valid/  etapa 2: filtragem e validação
│   └── 03_curation/      etapa 3: mineração profunda e planilha de curadoria
├── data/
│   ├── raw/              saída de cada script, aprovados e rejeitados
│   └── curated/          primeiro lote (MFE-001 a MFE-050)
├── requirements.txt
└── LICENSE
```

## Scripts

| # | Script | Entrada | Saída |
|---|---|---|---|
| 1 | `01_miner&id/01_mining_heuristics.py` | busca de código do GitHub | `candidatos_fase1_heuristicas-1611.json` |
| 2 | `01_miner&id/02_metadatas.py` | saída da etapa 1 | `candidatos_fase2_metadados_brutos.json` |
| 3 | `01_miner&id/03_distributor_analysis.py` | saída da etapa 2 | tabelas de distribuição (só na tela) |
| 4 | `02_filter&valid/04_filter_maturity.py` | saída da etapa 2 | `dts1_candidatos_fase4_filtro_maturidade_APROVADOS.json` / `_REJEITADOS.json` |
| 5 | `02_filter&valid/05_maturity_distributor_analysis.py` | saída da etapa 4 | tabelas de distribuição (só na tela) |
| 6 | `02_filter&valid/06_quality_gate.py` | aprovados da etapa 4 | `dts1_candidatos_fase5_quality_gate_APROVADOS.json` / `_REJEITADOS.json` |
| 7 | `02_filter&valid/07_sanity_check.py` | aprovados da etapa 6 | `dts1_candidatos_fase6_sanity_check_APROVADOS.json` / `_REJEITADOS.json` |
| 7.5 | `02_filter&valid/07.5_sampling.py` | aprovados da etapa 7 | `dts1_candidatos_fase7_AMOSTRAGEM.json` (amostra de 5% para conferência manual) |
| 8 | `03_curation/08_deep_mining.py` | aprovados da etapa 7 | `dts1_candidatos_fase8_deep_mining.json` |
| 9 | `03_curation/09_curation.py` | saída da etapa 8 | `dts1_dataset_fase9_curadoria.csv` / `.json` |

Todas as saídas estão em [`data/raw/`](data/raw). Cada pasta de `src/` também tem uma nota curta sobre a sua etapa.

## Como executar

Os scripts foram escritos para o **Google Colab** e rodam um de cada vez, na ordem.

1. Abra um notebook no Colab e instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
2. Suba para o notebook o arquivo de entrada do script (veja a tabela acima) e cole o script numa célula.
3. Quando for pedido, cole um **token de acesso pessoal do GitHub**. O token é lido com `getpass` e nunca fica salvo no código.
4. Ao terminar, o Colab baixa o arquivo de saída, que é a entrada do próximo script.

Pontos de atenção:

- Alguns scripts importam `google.colab` para baixar o resultado. Para rodar fora do Colab, tire esse import e as linhas `files.download(...)`.
- Entre as etapas, alguns arquivos foram renomeados à mão (por exemplo, `candidatos_fase2_dados_brutos.json` virou `candidatos_fase2_metadados_brutos.json`). Se um script não achar a entrada, confira o nome que ele espera em `ARQUIVO_ENTRADA`.
- A API do GitHub muda com o tempo, e repositórios são editados ou apagados, então uma nova execução não devolve exatamente os mesmos números. Para reproduzir o dataset publicado, use os arquivos de `data/raw/` e os hashes de commit registrados em cada versão.

## Licença

O código desta pasta está sob a licença [MIT](LICENSE). Os dados do restante do repositório estão sob [CC BY 4.0](../LICENSE).

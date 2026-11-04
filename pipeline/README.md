<div align="center">

**English** · [Português](README.pt-BR.md)

<h1>DTS1 · MFE-OSS · Mining Pipeline</h1>

<p><b>Scripts and intermediate files that produced the 455 repositories of the dataset</b></p>

![Python](https://img.shields.io/badge/Python-3.10%2B-231F20?style=for-the-badge&logo=python&logoColor=FFFFFF)
![GitHub API](https://img.shields.io/badge/GitHub%20API-231F20?style=for-the-badge&logo=github&logoColor=FFFFFF)
![Google Colab](https://img.shields.io/badge/Google%20Colab-231F20?style=for-the-badge&logo=googlecolab&logoColor=FFFFFF)
![license](https://img.shields.io/badge/license-MIT-E0E1E0?style=for-the-badge&labelColor=231F20)

</div>

<br>

This folder holds the mining pipeline of **DTS1 · MFE-OSS**, from the first GitHub search to the spreadsheet that went to manual curation. Every stage keeps both the accepted and the rejected repositories, so any number in the funnel can be traced back to a file.

The dataset itself, with its versions, is at the [root of this repository](../README.md). This folder used to be the `msr-mfe-oss-dataset` repository and was moved here with its full commit history.

## Funnel

| Stage | Script | Repositories | Removed |
|---|---|---|---|
| Heuristic search | `01_mining_heuristics.py` | 2,793 | |
| Maturity filter ($I_1$–$I_3$) | `04_filter_maturity.py` | 1,205 | 1,578 |
| Quality gate ($I_4$–$I_5$) | `06_quality_gate.py` | 842 | 363 |
| Sanity check ($I_6$) | `07_sanity_check.py` | 455 | 387 |

**Why repositories were removed**

- **Maturity:** last commit before 2021, no contributors or fewer than 10 commits.
- **Quality gate:** 187 without a README, 114 with documentation in another language, 60 insubstantial (under 100 KB) and 2 archived.
- **Sanity check:** 238 without an inspectable `package.json` and 149 without structural evidence of orchestration (`remotes`/`exposes`, real dependencies, folder structure).

## Structure

```
pipeline/
├── src/
│   ├── 01_miner&id/      stage 1: mining and identification
│   ├── 02_filter&valid/  stage 2: filtering and validation
│   └── 03_curation/      stage 3: deep mining and curation spreadsheet
├── data/
│   ├── raw/              output of every script, accepted and rejected
│   └── curated/          first batch (MFE-001 to MFE-050)
├── requirements.txt
└── LICENSE
```

## Scripts

| # | Script | Input | Output |
|---|---|---|---|
| 1 | `01_miner&id/01_mining_heuristics.py` | GitHub code search | `candidatos_fase1_heuristicas-1611.json` |
| 2 | `01_miner&id/02_metadatas.py` | stage 1 output | `candidatos_fase2_metadados_brutos.json` |
| 3 | `01_miner&id/03_distributor_analysis.py` | stage 2 output | distribution tables (screen only) |
| 4 | `02_filter&valid/04_filter_maturity.py` | stage 2 output | `dts1_candidatos_fase4_filtro_maturidade_APROVADOS.json` / `_REJEITADOS.json` |
| 5 | `02_filter&valid/05_maturity_distributor_analysis.py` | stage 4 output | distribution tables (screen only) |
| 6 | `02_filter&valid/06_quality_gate.py` | stage 4 accepted | `dts1_candidatos_fase5_quality_gate_APROVADOS.json` / `_REJEITADOS.json` |
| 7 | `02_filter&valid/07_sanity_check.py` | stage 6 accepted | `dts1_candidatos_fase6_sanity_check_APROVADOS.json` / `_REJEITADOS.json` |
| 7.5 | `02_filter&valid/07.5_sampling.py` | stage 7 accepted | `dts1_candidatos_fase7_AMOSTRAGEM.json` (5% sample for manual check) |
| 8 | `03_curation/08_deep_mining.py` | stage 7 accepted | `dts1_candidatos_fase8_deep_mining.json` |
| 9 | `03_curation/09_curation.py` | stage 8 output | `dts1_dataset_fase9_curadoria.csv` / `.json` |

All outputs are in [`data/raw/`](data/raw). Each folder in `src/` also has a short note on its stage (in Portuguese).

## How to run

The scripts were written for **Google Colab** and run one at a time, in order.

1. Open a notebook in Colab and install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Upload the input file of the script to the notebook (see the table above) and paste the script into a cell.
3. When asked, paste a **GitHub personal access token**. The token is read with `getpass` and is never stored in the code.
4. When the script finishes, Colab downloads the output file. It is the input of the next script.

Things to keep in mind:

- Some scripts import `google.colab` to download the result. To run them outside Colab, remove that import and the `files.download(...)` lines.
- Between stages, a few files were renamed by hand (for example, `candidatos_fase2_dados_brutos.json` became `candidatos_fase2_metadados_brutos.json`). If a script does not find its input, check the name it expects in `ARQUIVO_ENTRADA`.
- The GitHub API changes over time and repositories are edited or deleted, so a new run will not return exactly the same numbers. To reproduce the published dataset, use the files in `data/raw/` and the commit hashes recorded in each version.

## License

The code in this folder is under the [MIT](LICENSE) license. The data in the rest of the repository is under [CC BY 4.0](../LICENSE).

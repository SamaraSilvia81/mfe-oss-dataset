<img width="1112" height="811" alt="image" src="https://github.com/user-attachments/assets/d82386bf-a55b-4327-a54d-418922c98a64" />

<div align="center">

**English** · [Português](README.pt-BR.md)

<h1>DTS1 · MFE-OSS</h1>

<p><b>Mapping the Microfrontend Ecosystem: A Dataset of Open-Source Projects</b></p>

<!-- badges:start -->
![version](https://img.shields.io/badge/version-v1.1.0-AF0421?style=for-the-badge)
![snapshot](https://img.shields.io/badge/snapshot-2026--10--10-231F20?style=for-the-badge)
![repositories](https://img.shields.io/badge/repositories-455-231F20?style=for-the-badge)
![validated](https://img.shields.io/badge/validated-28%20of%20455-231F20?style=for-the-badge)
![versions](https://img.shields.io/badge/versions-2-231F20?style=for-the-badge)
![license](https://img.shields.io/badge/license-CC%20BY%204.0-E0E1E0?style=for-the-badge&labelColor=231F20)
<!-- badges:end -->

![Microfrontends](https://img.shields.io/badge/Microfrontends-171717?style=for-the-badge)
![MSR](https://img.shields.io/badge/Mining%20Software%20Repositories-171717?style=for-the-badge)
![GitHub](https://img.shields.io/badge/GitHub-171717?style=for-the-badge&logo=github&logoColor=FFFFFF)
![CIn/UFPE](https://img.shields.io/badge/CIn-UFPE-AF0421?style=for-the-badge)

</div>

<br>

A dataset of open-source **microfrontend** projects on GitHub, built as part of the master's research of **Samara Silvia Sabino** at the Centro de Informática of the Universidade Federal de Pernambuco (CIn/UFPE), advised by **Prof. Vinicius Cardoso Garcia**.

DTS1 starts from **2,793 candidates** found by automated mining and arrives at **455 repositories**, which then go through manual curation with cross-validation among three curators.

Explore the dataset in the browser at **[mfe-oss-dataset.vercel.app](https://mfe-oss-dataset.vercel.app)**.

<!-- latest:start -->
| Current version | **v1.1.0** · Lote 1 validado e lote 2 catalogado |
|---|---|
| Snapshot date | 2026-10-10 |
| Repositories | 455 |
| Validated | 28 |
| Curation | Validated (adjudicated): 28 · Divergence: 21 · Awaiting review: 31 · Pending: 375 |
<!-- latest:end -->

## Download

| File | Contents |
|---|---|
| [`latest/mfe-oss-dts1-latest.csv`](latest/mfe-oss-dts1-latest.csv) | latest version, all 455 repositories |
| [`latest/mfe-oss-dts1-latest-validados.csv`](latest/mfe-oss-dts1-latest-validados.csv) | latest version, validated repositories only |
| [`latest/mfe-oss-dts1-latest.json`](latest/mfe-oss-dts1-latest.json) | latest version in JSON, with metadata and data dictionary |
| [Releases](../../releases) | every frozen version, with the files attached |

To reproduce an analysis, always use a **numbered version** (the `versions/` folder or the Releases), not `latest/`, which changes with every new version.

## Versions

Each version freezes the 455 repositories as they were on a given date. Versions never change after they are created: a correction becomes a new version.

<!-- versions:start -->
| Version | Title | Snapshot date | Validated | Files |
|---|---|---|---|---|
| v1.1.0 | Lote 1 validado e lote 2 catalogado | 2026-10-10 | 28 | [folder](versions/v1.1.0) |
| v1.0.0 | Lote 1 Catalogado *(reconstructed)* | 2025-12-09 | 0 | [folder](versions/v1.0.0) |
<!-- versions:end -->

Version titles and changelogs come from the curation tool and are written in Portuguese. What changed in each version is in the [CHANGELOG](CHANGELOG.md).

**Version numbers:**
- **patch** (v1.0.**1**): one-off fixes to values already published;
- **minor** (v1.**1**.0): repositories validated, reclassified or moved to another stage;
- **major** (v**2**.0.0): new columns or a change in a classification rule.

Versions marked as *reconstructed* depict a past date. They were rebuilt from the proposal, review and adjudication dates of each repository.

## How the dataset is built

1. **Mining and identification.** GitHub search using microfrontend heuristics (Module Federation, Single-SPA, qiankun, among others) and metadata extraction.
2. **Filtering and validation.** Maturity filter, quality gate and sanity check. Each stage keeps both the accepted and the rejected repositories.
3. **Deep mining.** Detailed metadata for the accepted repositories.
4. **Manual curation.** Each repository goes through three people: an **analyst** (catalogs), a **reviewer** (checks) and an **adjudicator** (decides). A value is validated only when all three agree. Without unanimity, a meeting is held; if there is still no agreement, the advisor decides.

The code and the intermediate files of steps 1 to 3 are in the [`pipeline/`](pipeline) folder. Curation (step 4) is done in **CuraData**, a tool built for this research, and the versions published here come straight from it.

| Stage | Repositories | Removed |
|---|---|---|
| Candidates (heuristics) | 2,793 | |
| Maturity filter | 1,205 | 1,578 |
| Quality gate | 842 | 363 |
| Sanity check | 455 | 387 |

## Columns

All 37 columns are described in the [data dictionary](DATA_DICTIONARY.md) (in Portuguese). Summary:

- **Identification and activity:** id, name, URL, curation batch, commit dates and hashes.
- **Metrics:** stars, forks, commits, contributors, PRs, issues and churn.
- **Classification:** framework, integration technique, structure (monorepo or polyrepo), evidence, license, who develops it, purpose, API style, number of modules, and assessment of documentation, organization and scope.
- **Curation:** status, `validado` and validation date.

Column names are in Portuguese, as in the published files.

**Note:** only repositories with `validado = true` have a classification reviewed by the three curators. In the others, the classification still comes from mining.

## Curation team

- **Samara Silvia Sabino** (CIn/UFPE)
- **Fagner Fernandes** (CIn/UFPE)
- **Saulo Henrique do Nascimento Aguiar** (CIn/UFPE)
- **Vinicius Cardoso Garcia** (CIn/UFPE), advisor

## How to cite

Use the **Cite this repository** button in the side menu, or:

> Samara Silvia Sabino; Vinicius Cardoso Garcia. *Mapping the Microfrontend Ecosystem: A Dataset of Open-Source Projects* (DTS1 · MFE-OSS), version vX.Y.Z. Centro de Informática, Universidade Federal de Pernambuco (CIn/UFPE). https://github.com/SamaraSilvia81/mfe-oss-dataset

Always state the version you used.

## License

- **Data** (`versions/`, `latest/` and the files at the root): [CC BY 4.0](LICENSE). They can be used and adapted for any purpose, with attribution.
- **Code** of the mining pipeline (`pipeline/`): [MIT](pipeline/LICENSE).

## Maintenance

The data files in this repository are generated automatically. A GitHub Action (`.github/workflows/sync-versions.yml`) runs every day, reads the versions from CuraData and:
- writes the files of every new version;
- updates `latest/`, the changelog, the citation and the tables in this page and in the Portuguese one;
- creates a Release for every version.

Do not edit generated files by hand: the next sync overwrites them.

Found an error in a repository? Open an [issue](../../issues) with the ID (for example, `MFE-042`), the field and the correct value.

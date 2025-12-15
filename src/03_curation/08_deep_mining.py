# --- Célula 1: Autenticação ---
!pip install PyGithub
import getpass
from github import Github, RateLimitExceededException, UnknownObjectException

# Autenticação
token = getpass.getpass('Cole seu token do GitHub:')
g = Github(token)

# ==============================================================================
# SCRIPT UNIFICADO: MINERAÇÃO PROFUNDA E TÉCNICA (OUTPUT: JSON)
# ==============================================================================

!pip install PyGithub
import json
import time
import getpass
from datetime import timedelta
from google.colab import files

# --- 1. CONFIGURAÇÕES ---
ARQUIVO_ENTRADA = 'dts1_candidatos_fase6_sanity_check_APROVADOS.json'
ARQUIVO_SAIDA_JSON = 'dts1_candidatos_fase8_deep_mining.json'

# Mapas de Detecção Técnica
MAPA_FRAMEWORKS = {
    "react": "React", "vue": "Vue", "@angular/core": "Angular",
    "svelte": "Svelte", "next": "Next.js", "lit": "LitElement",
    "preact": "Preact", "ember-source": "Ember", "qwik": "Qwik",
    "solid-js": "SolidJS"
}

MAPA_INTEGRACAO = {
    "single-spa": "Single-SPA", "module-federation": "Module Federation",
    "@angular-architects/module-federation": "Module Federation (Angular)",
    "vite-plugin-federation": "Module Federation (Vite)",
    "@module-federation/nextjs-mf": "Module Federation (Next)",
    "qiankun": "Qiankun", "piral": "Piral", "luigi-client": "Luigi",
    "frint": "Frint", "systemjs": "SystemJS", "bit.dev": "Bit",
    "mosaic": "Zalando Mosaic", "puzzle-js": "PuzzleJS"
}

ARQUIVOS_MONOREPO = {
    "lerna.json": "Lerna", "turbo.json": "Turborepo",
    "nx.json": "Nx", "rush.json": "Rush",
    "pnpm-workspace.yaml": "PNPM Workspaces",
    "yarn.lock": "Yarn Workspaces"
}

# --- 3. CARGA ---
print(f"\n📂 Lendo {ARQUIVO_ENTRADA}...")
try:
    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f:
        lista_projetos = json.load(f)
    print(f"✅ Sucesso! {len(lista_projetos)} projetos carregados.")
except FileNotFoundError:
    print(f"❌ Erro: Arquivo {ARQUIVO_ENTRADA} não encontrado.")
    lista_projetos = []

# --- 4. EXECUÇÃO UNIFICADA ---
resultados = []
start_time = time.time()

print(f"\n🚀 Iniciando Mineração Completa (Deep + Tech + First Commit)...")

for i, proj in enumerate(lista_projetos):
    repo_name = proj.get('repo_name')
    if not repo_name: continue

    print(f"[{i+1}/{len(lista_projetos)}] {repo_name:<40}", end=" ")

    try:
        repo = g.get_repo(repo_name)

        # --- A. MÉTRICAS DE SAÚDE E HISTÓRICO ---

        # 1. Last Commit
        last_hash = "N/A"
        try:
            last_commit = repo.get_commit(sha=repo.default_branch)
            last_hash = last_commit.sha
        except: pass

        # 2. FIRST COMMIT (Hash e Data) - Novo!
        first_hash = "N/A"
        first_date = "N/A"
        try:
            commits = repo.get_commits()
            if commits.totalCount > 0:
                # Pega o último da lista reversa (o primeiro cronológico)
                first_c = commits.reversed[0]
                first_hash = first_c.sha
                first_date = first_c.commit.author.date.isoformat()
        except: pass

        # 3. Pull Requests
        total_prs = 0
        last_pr_date = "N/A"
        try:
            prs = repo.get_pulls(state='all', sort='created', direction='desc')
            total_prs = prs.totalCount
            if total_prs > 0:
                last_pr_date = prs[0].created_at.isoformat()
        except: pass

        # 4. Closed Issues
        issues_closed = 0
        try:
            issues_closed = g.search_issues(f"repo:{repo_name} is:issue state:closed").totalCount
        except: pass

        # 5. Churn Rate
        churn_avg = 0
        try:
            stats = repo.get_stats_code_frequency()
            if stats:
                adds, dels, weeks = 0, 0, 0
                for week in stats:
                    adds += week.additions
                    dels += abs(week.deletions)
                    weeks += 1
                churn_avg = int((adds + dels) / weeks) if weeks > 0 else 0
        except: pass

        # --- B. METADADOS TÉCNICOS (Package.json & Estrutura) ---

        auto_frame = []
        auto_integ = []
        auto_struct = "Polyrepo (Provável)"
        auto_evidencia = "Nenhuma config"

        try:
            # B1. Arquivos na Raiz (Monorepo)
            contents = repo.get_contents("")
            root_files = [x.name for x in contents]
            found_mono = [tool for file, tool in ARQUIVOS_MONOREPO.items() if file in root_files]
            if found_mono:
                auto_struct = "Monorepo"
                auto_evidencia = ", ".join(found_mono)

            # B2. Package.json (Framework e Integração)
            try:
                pkg_file = repo.get_contents("package.json")
                pkg_content = json.loads(pkg_file.decoded_content.decode())

                deps = str(pkg_content.get('dependencies', {})) + str(pkg_content.get('devDependencies', {}))

                for k, v in MAPA_FRAMEWORKS.items():
                    if k in deps: auto_frame.append(v)

                for k, v in MAPA_INTEGRACAO.items():
                    if k in deps: auto_integ.append(v)

                if 'workspaces' in pkg_content and auto_struct != "Monorepo":
                    auto_struct = "Monorepo"
                    auto_evidencia = "Package.json Workspaces"
            except UnknownObjectException:
                pass # Sem package.json

        except Exception:
            auto_evidencia = "Erro Leitura Arqs"

        # Consolidação Strings
        frame_final = f"Multi ({', '.join(set(auto_frame))})" if len(auto_frame) > 1 else (auto_frame[0] if auto_frame else "Agnostic/Outro")
        integ_final = ", ".join(set(auto_integ)) if auto_integ else "Custom/Outra"

        # --- C. SALVAMENTO ---

        # Salva tudo dentro de metrics_deep para manter organizado
        proj['metrics_deep'] = {
            'first_commit_hash': first_hash,
            'first_commit_date': first_date,
            'last_commit_hash': last_hash,
            'last_pr_date': last_pr_date,
            'total_pull_requests': total_prs,
            'closed_issues': issues_closed,
            'churn_rate_avg_weekly': churn_avg
        }

        # Salva metadados na raiz do objeto
        proj['[Auto] Estrutura'] = auto_struct
        proj['[Auto] Evidencia'] = auto_evidencia
        proj['[Auto] Framework'] = frame_final
        proj['[Auto] Integracao'] = integ_final

        resultados.append(proj)
        print(f"✅ | {auto_struct} | {frame_final}")

    except RateLimitExceededException:
        print("\n⏳ Rate Limit! Pausando 60s...")
        time.sleep(60)
    except Exception as e:
        print(f"❌ Erro: {str(e).split()[0]}")
        proj['metrics_deep'] = {'error': str(e)}
        resultados.append(proj)

    time.sleep(0.5)

# --- 5. EXPORTAÇÃO (SÓ JSON) ---
elapsed = time.time() - start_time
tempo_total = str(timedelta(seconds=int(elapsed)))

print("\n" + "="*50)
print(f"🎉 MINERAÇÃO CONCLUÍDA EM: {tempo_total}")
print("="*50)

with open(ARQUIVO_SAIDA_JSON, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=4, ensure_ascii=False)

print(f"💾 Arquivo JSON salvo: {ARQUIVO_SAIDA_JSON}")
files.download(ARQUIVO_SAIDA_JSON)


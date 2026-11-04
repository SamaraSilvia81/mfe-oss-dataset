# Célula 1: Instalar e Importar
!pip install PyGithub # Garante que está instalado
import getpass
import time
import json
from github import Github, RateLimitExceededException
from datetime import datetime, timedelta, timezone
from google.colab import files

token = getpass.getpass('Cole seu token do GitHub:')
g = Github(token)
print(f"Login como: {g.get_user().login}")

# ==============================================================================
# SCRIPT 4.0: FILTRO DE MATURIDADE (CLEAN RUN - FASE 4)
# Objetivo: Filtrar candidatos brutos por Atividade, Commits e Contribuidores.
# Critério Novo: Contribuidores >= 1 (Aceita Solos).
# ==============================================================================

# Critérios do Funil
MIN_COMMITS = 10
MIN_CONTRIBUIDORES = 1
ANO_CORTE = 2021
data_limite_atividade = datetime(ANO_CORTE, 1, 1, tzinfo=timezone.utc)

# Arquivos (Padrão Clean Run)
ARQUIVO_ENTRADA = 'dts1_candidatos_fase2_metadados.json'
ARQUIVO_SAIDA = 'dts1_candidatos_fase4_filtro_maturidade_APROVADOS.json'
ARQUIVO_REJEITADOS = 'dts1_candidatos_fase4_filtro_maturidade_REJEITADOS.json'
ARQUIVO_LOG = 'dts1_candidatos_fase4_log_processamento.txt'

# --- 2. CARREGAMENTO ROBUSTO ---
print(f"\n📂 Carregando {ARQUIVO_ENTRADA}...")
try:
    with open(ARQUIVO_ENTRADA, 'r') as f:
        repos_brutos = json.load(f)
    print(f"📊 Total de candidatos brutos: {len(repos_brutos)}")
except FileNotFoundError:
    print(f"❌ Erro: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
    print("Faça upload do arquivo bruto da Fase 1 ou 2.")
    repos_brutos = []

# --- 3. CHECKPOINT (RETOMADA) ---
repos_ja_processados = set()
try:
    with open(ARQUIVO_LOG, 'r') as f:
        for line in f:
            if "PROCESSADO:" in line:
                repos_ja_processados.add(line.split(":")[-1].strip())
    print(f"🔄 Retomando: {len(repos_ja_processados)} já processados anteriormente.")
except FileNotFoundError:
    print("✨ Iniciando nova execução (Zero).")

# --- 4. EXECUÇÃO DO FILTRO ---
aprovados = []
rejeitados = []
contagem = {"Inativo": 0, "Contribuidores": 0, "Commits": 0, "Erro API": 0}

log_file = open(ARQUIVO_LOG, 'a', encoding='utf-8')
start_time = time.time()

# Filtra o que já foi feito
fila = []
for item in repos_brutos:
    # Lógica de Extração de Nome (Blindagem)
    nome = item if isinstance(item, str) else item.get('repo') or item.get('repo_name')
    if nome and nome not in repos_ja_processados:
        fila.append(nome)

print(f"🚀 Iniciando processamento de {len(fila)} repositórios...")

for i, repo_name in enumerate(fila):
    print(f"\r[{i+1}/{len(fila)}] Analisando: {repo_name}...", end="")

    dados_repo = {
        "repo_name": repo_name,
        "motivo_filtro": None,
        "is_active": False,
        "contributors": 0,
        "commits": 0,
        "last_push_date": None
    }

    try:
        # --- A. CONSULTA API ---
        repo = g.get_repo(repo_name)
        time.sleep(0.5) # Pausa leve

        # 1. Atividade
        pushed_at = repo.pushed_at
        is_active = pushed_at >= data_limite_atividade

        if not is_active:
            # Falha rápida (Fail Fast) - Se inativo, nem conta o resto (economiza API)
            motivo = f"Inativo (último push: {pushed_at.date()})"
            contagem["Inativo"] += 1
            dados_repo.update({"motivo_filtro": motivo, "last_push_date": pushed_at.isoformat()})
            rejeitados.append(dados_repo)
            print(f" -> ❌ {motivo}")

        else:
            # 2. Contribuidores
            contribs = repo.get_contributors(anon=True).totalCount

            if contribs < MIN_CONTRIBUIDORES:
                motivo = f"Contribuidores ({contribs} < {MIN_CONTRIBUIDORES})"
                contagem["Contribuidores"] += 1
                dados_repo.update({"motivo_filtro": motivo, "contributors": contribs, "last_push_date": pushed_at.isoformat()})
                rejeitados.append(dados_repo)
                print(f" -> ❌ {motivo}")

            else:
                # 3. Commits (O mais pesado, fica pro final)
                commits = repo.get_commits().totalCount

                if commits < MIN_COMMITS:
                    motivo = f"Commits ({commits} < {MIN_COMMITS})"
                    contagem["Commits"] += 1
                    dados_repo.update({"motivo_filtro": motivo, "contributors": contribs, "commits": commits, "last_push_date": pushed_at.isoformat()})
                    rejeitados.append(dados_repo)
                    print(f" -> ❌ {motivo}")

                else:
                    # --- APROVADO! ---
                    print(f" -> ✅ APROVADO! (C:{commits} | Devs:{contribs})")
                    dados_aprovado = {
                        "repo_name": repo.full_name,
                        "url": repo.html_url,
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "commits": commits,
                        "contributors": contribs,
                        "open_issues": repo.open_issues_count,
                        "creation_date": repo.created_at.isoformat(),
                        "last_push_date": pushed_at.isoformat(),
                        "license": repo.license.name if repo.license else None,
                        "language": repo.language
                    }
                    aprovados.append(dados_aprovado)

    except RateLimitExceededException:
        print("\n⏳ Rate Limit! Pausando 15 min...")
        log_file.flush()
        time.sleep(900)
        # Nota: O loop continua no próximo, este item pode ser perdido na iteração atual
        # mas como não gravamos no log, ele será pego no próximo Run.

    except Exception as e:
        print(f" -> ⚠️ Erro: {str(e).split()[0]}")
        contagem["Erro API"] += 1

    # Checkpoint
    log_file.write(f"PROCESSADO:{repo_name}\n")
    if i % 10 == 0: log_file.flush()

log_file.close()
end_time = time.time()
elapsed_seconds = int(end_time - start_time)
duration = str(timedelta(seconds=elapsed_seconds))

# --- 4. FINALIZAÇÃO ---
print("🏁 PROCESSAMENTO CONCLUÍDO")
print(f"⏱️ Tempo Total de Execução: {duration}")
print("-" * 30)
print(f"✅ APROVADOS (Salvos):   {len(aprovados)}")
print(f"❌ REJEITADOS (Salvos):  {len(rejeitados)}")
print("-" * 30)
print("📉 Detalhe das Rejeições:")
for motivo, qtd in contagem.items():
    print(f"   • {motivo:<15}: {qtd}")
print("="*50)

# 2. Salvar Arquivos
print(f"\n💾 Salvando arquivos...")

with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
    json.dump(aprovados, f, indent=4)
print(f" -> Aprovados salvos em: {ARQUIVO_SAIDA}")

with open(ARQUIVO_REJEITADOS, 'w', encoding='utf-8') as f:
    json.dump(rejeitados, f, indent=4)
print(f" -> Rejeitados salvos em: {ARQUIVO_REJEITADOS}")

# 3. Download Automático
print("\n⬇️ Iniciando downloads...")
try:
    files.download(ARQUIVO_SAIDA)
    files.download(ARQUIVO_REJEITADOS)
except Exception as e:
    print("⚠️ O download automático falhou (comum em alguns navegadores).")
    print("   Por favor, baixe manualmente na aba 'Arquivos' à esquerda.")
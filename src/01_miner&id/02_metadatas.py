# Célula 2: Script 2 (Extrator de Metadados)
!pip install PyGithub
import getpass
import time
import json
from github import Github, RateLimitExceededException
from datetime import datetime, timedelta, timezone

token = getpass.getpass('Cole seu token do GitHub:')
g = Github(token)
print(f"Login como: {g.get_user().login}")

# Nome do arquivo de entrada (resultado do Script 1)
arquivo_entrada = 'candidatos_fase1_heuristicas-1611.json'
# Nome do arquivo de saída (resultado deste script)
arquivo_saida = 'candidatos_fase2_dados_brutos.json'

# Carregar os candidatos brutos
try:
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        lista_bruta = json.load(f)
    print(f"Carregados {len(lista_bruta)} candidatos brutos de '{arquivo_entrada}'.")
except FileNotFoundError:
    print(f"ERRO: Arquivo de entrada '{arquivo_entrada}' não encontrado.")
    lista_bruta = []

dados_completos = []
# Tentar carregar dados existentes para continuar
try:
    with open(arquivo_saida, 'r', encoding='utf-8') as f:
        dados_completos = json.load(f)
    print(f"Progresso anterior carregado. {len(dados_completos)} repositórios já processados.")
except (FileNotFoundError, json.JSONDecodeError):
    print("Nenhum progresso anterior encontrado. Começando do zero.")
    dados_completos = []

# Criar um set de repos já processados para não re-processar
repos_processados = {repo['repo'] for repo in dados_completos}
lista_para_processar = [repo for repo in lista_bruta if repo not in repos_processados]

print(f"Total a processar: {len(lista_para_processar)} repositórios.")

start_time = time.time()

if g: # Só execute se o login funcionou
    for i, repo_name in enumerate(lista_para_processar):
        print(f"Processando {i+1}/{len(lista_para_processar)}: {repo_name}", end='')

        try:
            # 1. Obter o repositório
            repo = g.get_repo(repo_name)

            # 2. Obter data do último commit
            last_commit_date = repo.pushed_at

            # 3. Obter contagem de contribuidores
            contributors_count = repo.get_contributors().totalCount

            # 4. Obter contagem de commits (A PARTE LENTA)
            commits_count = -1 # Valor padrão em caso de erro
            try:
                commits_count = repo.get_commits().totalCount
            except GithubException as e:
                print(f" !Aviso (Commits): Falha ao contar commits para {repo_name}. Marcando como -1.")
            except Exception as e:
                print(f" !Aviso (Commits): Erro inesperado ao contar commits para {repo_name}. Marcando como -1.")

            # Adicionar dados
            dados_completos.append({
                'repo': repo_name,
                'last_commit': last_commit_date.isoformat(), # Salva como string ISO
                'contributors': contributors_count,
                'commits': commits_count
            })
            print(f" -> OK (Commits: {commits_count}, Contribs: {contributors_count})")

            time.sleep(1.5) # Pausa

            # Checkpoint a cada 50 repositórios
            if (i + 1) % 50 == 0:
                with open(arquivo_saida, 'w', encoding='utf-8') as f:
                    json.dump(dados_completos, f, indent=2)
                print(f"--- CHECKPOINT SALVO ({len(dados_completos)} repositórios) ---")

        except RateLimitExceededException:
            print(f"\n!! RATE LIMIT EXCEDIDO. Aguardando 10 minutos.")
            time.sleep(600) # Aguarda 10 minutos
            print("Retomando...")
            # (Adicionar lógica para tentar novamente o mesmo repo, se necessário)

        except GithubException as e:
            # Erros comuns: 'Not Found' (repo foi deletado), 'Repository access blocked'
            print(f" !! ERRO no Repositório: {e.data['message']}. Pulando {repo_name}.")
            dados_completos.append({
                'repo': repo_name,
                'last_commit': None,
                'contributors': -1, # Marca como erro
                'commits': -1
            })

        except Exception as e:
            print(f" !! ERRO DESCONHECIDO. Pulando {repo_name}. Erro: {e}")
            dados_completos.append({
                'repo': repo_name,
                'last_commit': None,
                'contributors': -1,
                'commits': -1
            })

    # Salvar o arquivo final
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dados_completos, f, indent=2)

    end_time = time.time()
    duration_minutes = (end_time - start_time) / 60
    print(f"\n--- Script 2 (Extrator) Concluído ---")
    print(f"Salvo {len(dados_completos)} registros em '{arquivo_saida}'.")
    print(f"Tempo total de execução: {duration_minutes:.2f} minutos.")
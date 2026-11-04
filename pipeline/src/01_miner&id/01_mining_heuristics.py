# Célula 1: Instalar e Importar
!pip install PyGithub
import getpass
import time
import json
from github import Github, RateLimitExceededException
from datetime import datetime, timedelta, timezone

token = getpass.getpass('Cole seu token do GitHub:')
g = Github(token)
print(f"Login como: {g.get_user().login}")

# Célula 2: Script 1 - Busca de Heurísticas
queries_de_busca = [
    '"ModuleFederationPlugin" in:file filename:webpack.config.js',
    '"single-spa" in:file filename:package.json',
    '"vite-plugin-federation" in:file filename:vite.config.js',
    '"vite-plugin-federation" in:file filename:vite.config.ts'
]
repositorios_brutos = set() # Usamos um "set" para evitar duplicatas
print("Iniciando a busca... (Fase 1)")

start_time = time.time()

for query in queries_de_busca:
    print(f"Buscando pela heurística: {query}")
    try:
        resultados_busca = g.search_code(query)
        for arquivo in resultados_busca:
            # Pausa para não irritar a API (30 buscas/min)
            time.sleep(3)
            repo_name = arquivo.repository.full_name
            if repo_name not in repositorios_brutos:
                print(f"  > Candidato encontrado: {repo_name}")
                repositorios_brutos.add(repo_name)
    except Exception as e:
        print(f"!! ERRO na busca: {e}. Aguardando 1 minuto.")
        time.sleep(60)

end_time = time.time() # <--- 2. ADICIONE ESTA LINHA (marca o fim)
duration_seconds = end_time - start_time
duration_minutes = duration_seconds / 60

print(f"\nBusca concluída. Total de {len(repositorios_brutos)} candidatos brutos.")

# 3. ADICIONE ESTAS LINHAS PARA VER O TEMPO
print("-" * 30)
print(f"Tempo total de execução: {duration_seconds:.2f} segundos.")
print(f"Tempo total de execução: {duration_minutes:.2f} minutos.")

# Salvar o checkpoint
nome_arquivo = 'candidatos_fase1_heuristicas-1611.json'
with open(nome_arquivo, 'w', encoding='utf-8') as f:
    json.dump(list(repositorios_brutos), f)
print(f"Checkpoint salvo em '{nome_arquivo}'")

# Baixar o arquivo
from google.colab import files
files.download(nome_arquivo)
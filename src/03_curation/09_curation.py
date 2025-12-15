# ==============================================================================
# SCRIPT FASE 9: FORMATAÇÃO FINAL (EXPORTAÇÃO DUPLA: CSV + JSON)
# Objetivo: Gerar os arquivos finais para Curadoria (Excel) e Backup (JSON).
# ==============================================================================

import json
import pandas as pd
from google.colab import files

# --- 1. CONFIGURAÇÕES ---
# O arquivo JSON que saiu do script de mineração anterior
ARQUIVO_ENTRADA = 'dts1_candidatos_fase8_deep_mining.json'
ARQUIVO_SAIDA_CSV = 'dts1_dataset_fase9_curadoria.csv'
ARQUIVO_SAIDA_JSON = 'dts1_dataset_fase9_curadoria.json'

def categorizar_licenca(nome):
    if not nome or nome in ["Ausente", "N/A", "null", None]: return "Sem Licença"
    n = nome.lower()
    if any(x in n for x in ['mit', 'apache', 'bsd', 'isc']): return "Permissiva"
    if any(x in n for x in ['gpl', 'mozilla', 'mpl', 'eclipse']): return "Copyleft"
    return "Outra"

print(f"--- Iniciando Geração dos Arquivos Finais ---")

# --- 2. CARGA DOS DADOS ---
try:
    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f:
        projetos = json.load(f)
    print(f"📂 Processando {len(projetos)} projetos do JSON base.")
except FileNotFoundError:
    print(f"❌ Erro: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
    projetos = []

# --- 3. MONTAGEM DA TABELA (CSV) ---
lista_csv = []

for proj in projetos:
    # Garante acesso aos objetos internos
    deep = proj.get('metrics_deep', {})

    # Tratamento de Datas
    cria_github = proj.get('creation_date', '').split('T')[0]
    push_date = proj.get('last_push_date', '').split('T')[0]

    first_commit_date = deep.get('first_commit_date', 'N/A')
    if 'T' in first_commit_date: first_commit_date = first_commit_date.split('T')[0]

    # Hashes
    hash_first = deep.get('first_commit_hash', 'N/A')
    hash_last = deep.get('last_commit_hash', 'N/A')
    if len(hash_first) > 7: hash_first = hash_first[:7]
    if len(hash_last) > 7: hash_last = hash_last[:7]

    status = "Arquivado" if deep.get('is_archived') else "Ativo"

    item = {
        # --- BLOCO 1: IDENTIFICAÇÃO ---
        "Nome": proj.get('repo_name'),
        "URL": proj.get('url'),
        "Status": status,

        # --- BLOCO 2: LINHA DO TEMPO ---
        "Data Criação (GitHub)": cria_github,
        "Data 1º Commit (Real)": first_commit_date,
        "Data Último Push": push_date,

        # --- BLOCO 3: RASTREABILIDADE ---
        "Hash 1º Commit": hash_first,
        "Hash Último Commit": hash_last,

        # --- BLOCO 4: MÉTRICAS ---
        "Stars": proj.get('stars', 0),
        "Forks": proj.get('forks', 0),
        "Commits": proj.get('commits', 0),
        "Contribuintes": proj.get('contributors', 0), # <--- ADICIONADO AQUI!
        "PRs Totais": deep.get('total_pull_requests', 0),
        "Issues Open": proj.get('open_issues', 0),
        "Issues Closed": deep.get('closed_issues', 0),
        "Churn Semanal": deep.get('churn_rate_avg_weekly', 'N/A'),

        # --- BLOCO 5: DETECÇÃO AUTOMÁTICA ---
        "[Auto] Framework": proj.get('[Auto] Framework', ''),
        "[Auto] Integração": proj.get('[Auto] Integracao', ''),
        "[Auto] Estrutura": proj.get('[Auto] Estrutura', ''),
        "[Auto] Evidência": proj.get('[Auto] Evidencia', ''),

        # --- BLOCO 6: LICENÇA ---
        "Licença": proj.get('license', 'Ausente'),
        "Categ. Licença": categorizar_licenca(proj.get('license')),

        # --- BLOCO 7: CURADORIA MANUAL ---
        "[M] Desenvolvido Por": "",
        "[M] Finalidade": "",
        "[M] Estilo API": "",
        "[M] Qtd Microfrontends": "",
        "[M] Obs": ""
    }
    lista_csv.append(item)

# --- 4. EXPORTAÇÃO E DOWNLOAD ---
if lista_csv:
    # A. Salvar CSV
    df = pd.DataFrame(lista_csv)
    df = df.sort_values(by='Stars', ascending=False)
    df.to_csv(ARQUIVO_SAIDA_CSV, index=False, sep=';', encoding='utf-8-sig')

    # B. Salvar JSON (Cópia fiel do processado)
    with open(ARQUIVO_SAIDA_JSON, 'w', encoding='utf-8') as f:
        json.dump(projetos, f, indent=4, ensure_ascii=False)

    print(f"\n✅ ARQUIVOS GERADOS COM SUCESSO!")
    print(f"📊 Total de projetos: {len(df)}")
    print(f"💾 CSV: {ARQUIVO_SAIDA_CSV}")
    print(f"💾 JSON: {ARQUIVO_SAIDA_JSON}")

    print("⬇️ Iniciando download...")
    files.download(ARQUIVO_SAIDA_CSV)
    files.download(ARQUIVO_SAIDA_JSON)
else:
    print("❌ Nenhum dado encontrado no JSON de entrada.")
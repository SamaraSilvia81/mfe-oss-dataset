import pandas as pd
import json
import time
from datetime import datetime

print("--- Iniciando Script 5 (Analisador Final) ---")

# --- Arquivos de Entrada (Gerados pelo Script de 3h) ---
ARQUIVO_APROVADOS = 'dts1_candidatos_fase4_filtro_maturidade_APROVADOS.json'
ARQUIVO_REJEITADOS = 'dts1_candidatos_fase4_filtro_maturidade_REJEITADOS.json'

start_time_analise = time.time()

# --- Função de Análise (Reutilizável) ---
def analisar_dataframe(df, nome_dataset):
    """Função que roda as análises do Script 3 em qualquer dataframe"""

    if df.empty:
        print(f"Dataset '{nome_dataset}' está vazio. Nenhuma análise para fazer.")
        return

    # Ajusta o nome da coluna de data (no APROVADOS é 'last_push_date', no REJEITADOS pode ser tb)
    if 'last_push_date' in df.columns:
        df['data_datetime'] = pd.to_datetime(df['last_push_date'], errors='coerce')
    else:
        print(f"Dataset '{nome_dataset}' não tem 'last_push_date'. Pulando análise de Ano.")
        df['data_datetime'] = None # Cria coluna vazia

    print(f"\n--- Análise do Dataset: {nome_dataset} ({len(df)} projetos) ---")

    # 1. Análise por ANO (do último push)
    print("\n--- 1. Distribuição por Ano (Último Commit) ---")
    if df['data_datetime'] is not None:
        ano_counts = df[df['data_datetime'].notna()]['data_datetime'].dt.year.value_counts().sort_index(ascending=False)
        print(ano_counts)
    else:
        print("N/A (Coluna de data não encontrada)")

    # 2. Análise por FAIXA DE COMMITS
    print("\n--- 2. Distribuição por Faixa de Commits ---")
    bins_commits = [-2, 0, 10, 50, 100, 500, 1000, float('inf')]
    labels_commits = ['Erro/Vazio', '1-10', '11-50', '51-100', '101-500', '501-1000', '1000+']
    commit_counts = pd.cut(df['commits'], bins=bins_commits, labels=labels_commits, right=False).value_counts().sort_index()
    print(commit_counts)

    # 3. Análise por FAIXA DE CONTRIBUIDORES
    print("\n--- 3. Distribuição por Faixa de Contribuidores ---")
    bins_contrib = [-2, 0, 1, 5, 10, 50, float('inf')]
    labels_contrib = ['Erro', '1', '2-5', '6-10', '11-50', '51+']
    df['Faixa_Contribuidores'] = pd.cut(df['contributors'], bins=bins_contrib, labels=labels_contrib, right=False)
    contrib_counts = df['Faixa_Contribuidores'].value_counts().sort_index()
    print(contrib_counts)

    # 4. Cruzamento de Ano vs. Contribuidores
    print("\n--- 4. Cruzamento: Ano vs. Faixa de Contribuidores ---")
    if df['data_datetime'] is not None:
        df['Ano'] = df['data_datetime'].dt.year
        df_filtered = df.dropna(subset=['Ano', 'Faixa_Contribuidores'])
        df_filtered['Ano'] = df_filtered['Ano'].astype(int)
        tabela_cruzada = pd.crosstab(df_filtered['Ano'], df_filtered['Faixa_Contribuidores'], dropna=False)
        tabela_cruzada = tabela_cruzada.reindex(columns=labels_contrib, fill_value=0)
        print(tabela_cruzada)
    else:
        print("N/A (Coluna de data não encontrada)")

# --- FIM DA FUNÇÃO ---

# --- Bloco de Execução ---
try:
    # 1. Carregar e Analisar APROVADOS (O MAIS IMPORTANTE)
    print(f"Carregando '{ARQUIVO_APROVADOS}'...")
    df_aprovados = pd.read_json(ARQUIVO_APROVADOS)
    analisar_dataframe(df_aprovados, "APROVADOS (Sua Lista de Ouro)")
except FileNotFoundError:
    print(f"ERRO: Arquivo '{ARQUIVO_APROVADOS}' não encontrado.")
except Exception as e:
    print(f"ERRO ao analisar APROVADOS: {e}")

try:
    # 2. Carregar e Analisar REJEITADOS (Para sua curiosidade)
    print(f"\nCarregando '{ARQUIVO_REJEITADOS}'...")
    df_rejeitados = pd.read_json(ARQUIVO_REJEITADOS)
    analisar_dataframe(df_rejeitados, "REJEITADOS")
except FileNotFoundError:
    print(f"ERRO: Arquivo '{ARQUIVO_REJEITADOS}' não encontrado.")
except Exception as e:
    print(f"ERRO ao analisar REJEITADOS: {e}")

end_time_analise = time.time()
duration_analise = end_time_analise - start_time_analise

print(f"\nTempo de execução da análise: {duration_analise:.4f} segundos.")
print("--- Análise Final Concluída ---")
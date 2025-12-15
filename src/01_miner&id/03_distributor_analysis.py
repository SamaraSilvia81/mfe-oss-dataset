# Célula 3: Script 3 (Analisador/Sintetizador)
import pandas as pd
import json
import time

# Nome do arquivo de entrada (o resultado do Script 2)
arquivo_entrada = 'candidatos_fase2_dados_brutos.json'

print(f"--- Célula 3: Script 3 (Analisador/Sintetizador) ---")

start_time_analise = time.time()

try:
    # Carregar os dados brutos de maturidade
    df = pd.read_json(arquivo_entrada)

    if df.empty:
        print("Arquivo de dados está vazio. Nenhuma análise para fazer.")
    else:
        # Converter a string de data para objeto datetime
        df['last_commit'] = pd.to_datetime(df['last_commit'], errors='coerce')

        print(f"Total de {len(df)} projetos carregados para análise.")

        # --- 1. Análise por ANO ---
        print("\n--- 1. Distribuição por Ano (Último Commit) ---")
        ano_counts = df[df['last_commit'].notna()]['last_commit'].dt.year.value_counts().sort_index(ascending=False)
        print(ano_counts)

        # --- 2. Análise por FAIXA DE COMMITS ---
        print("\n--- 2. Distribuição por Faixa de Commits ---")
        bins_commits = [-2, 0, 10, 50, 100, 500, 1000, float('inf')]
        labels_commits = ['Erro/Vazio', '1-10', '11-50', '51-100', '101-500', '501-1000', '1000+']
        commit_counts = pd.cut(df['commits'], bins=bins_commits, labels=labels_commits, right=False).value_counts().sort_index()
        print(commit_counts)

        # --- 3. Análise por FAIXA DE CONTRIBUIDORES ---
        print("\n--- 3. Distribuição por Faixa de Contribuidores ---")
        # Ajustei as faixas para ficarem mais claras na tabela
        bins_contrib = [-2, 0, 1, 5, 10, 50, float('inf')]
        labels_contrib = ['Erro', '1', '2-5', '6-10', '11-50', '51+']

        # Criar a coluna 'Faixa_Contribuidores' no DataFrame
        df['Faixa_Contribuidores'] = pd.cut(df['contributors'], bins=bins_contrib, labels=labels_contrib, right=False)
        contrib_counts = df['Faixa_Contribuidores'].value_counts().sort_index()
        print(contrib_counts)

        # --- 4. Cruzamento de Ano vs. Contribuidores ---
        print("\n--- 4. Cruzamento: Ano vs. Faixa de Contribuidores ---")

        # Criar a coluna 'Ano' no DataFrame
        df['Ano'] = df['last_commit'].dt.year

        # Filtrar dados nulos (projetos que falharam a busca de ano ou contribs)
        df_filtered = df.dropna(subset=['Ano', 'Faixa_Contribuidores'])

        # Converter 'Ano' para Inteiro para melhor visualização
        df_filtered['Ano'] = df_filtered['Ano'].astype(int)

        # Criar a tabela de cruzamento (cross-tabulation)
        tabela_cruzada = pd.crosstab(df_filtered['Ano'], df_filtered['Faixa_Contribuidores'], dropna=False)

        # Reordenar as colunas para seguir a lógica
        tabela_cruzada = tabela_cruzada.reindex(columns=labels_contrib, fill_value=0)

        print(tabela_cruzada)

except FileNotFoundError:
    print(f"ERRO: Arquivo de dados '{arquivo_entrada}' não foi encontrado.")
    print("Você precisa rodar o Script 2 (Extrator) primeiro.")
except Exception as e:
    print(f"Um erro ocorreu durante a análise do Pandas: {e}")

end_time_analise = time.time() # <--- 3. Marcar o fim
duration_analise = end_time_analise - start_time_analise

print(f"\nTempo de execução da análise: {duration_analise:.4f} segundos.")
print("--- Análise Concluída ---")
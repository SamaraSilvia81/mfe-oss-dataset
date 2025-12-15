import pandas as pd
import math
import time
from google.colab import files

print("--- Iniciando Seleção de Amostra (5%) ---")
start_time = time.time()

# --- Configurações ---
ARQUIVO_ENTRADA = 'dts1_candidatos_fase6_sanity_check_APROVADOS.json'
ARQUIVO_SAIDA = 'dts1_candidatos_fase7_AMOSTRAGEM.json'
TAMANHO_AMOSTRA = 23

try:
    print(f"📂 Lendo arquivo JSON: {ARQUIVO_ENTRADA}...")

    # --- CORREÇÃO: Usar read_json para ler JSON ---
    df_aprovados = pd.read_json(ARQUIVO_ENTRADA)

    total = len(df_aprovados)
    print(f"✅ Sucesso! Total carregado: {total} projetos.")

    # --- Selecionar a amostra ---
    if total < TAMANHO_AMOSTRA:
        print(f"⚠️ Aviso: Total menor que a amostra. Pegando tudo.")
        amostra = df_aprovados
    else:
        # random_state=42 garante que sempre pegue os mesmos projetos (reprodutível)
        amostra = df_aprovados.sample(n=TAMANHO_AMOSTRA, random_state=42)

    print(f"\n🎲 Amostra selecionada: {len(amostra)} projetos.")

    # --- Salvar ---
    amostra.to_json(ARQUIVO_SAIDA, orient='records', indent=2, force_ascii=False)
    print(f"💾 Arquivo salvo: {ARQUIVO_SAIDA}")

    files.download(ARQUIVO_SAIDA)

except ValueError as e:
    print(f"❌ Erro de formato JSON: {e}")
except FileNotFoundError:
    print(f"❌ Erro: Não encontrei o arquivo '{ARQUIVO_ENTRADA}'.")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")

print(f"\n⏱️ Tempo: {time.time() - start_time:.4f}s")


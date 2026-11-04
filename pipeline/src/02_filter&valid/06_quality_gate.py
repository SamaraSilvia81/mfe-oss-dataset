# Célula 1: Instalar e Importar
!pip install PyGithub langdetect
import getpass
import time
import json
from github import Github, RateLimitExceededException
from datetime import datetime, timedelta, timezone
from langdetect import detect, LangDetectException

token = getpass.getpass('Cole seu token do GitHub:')
g = Github(token)
print(f"Login como: {g.get_user().login}")

# --- Célula 2: Executar Filtros (IGNORANDO LICENÇA) ---
import time
import json
from langdetect import detect, LangDetectException
from github import RateLimitExceededException

# Configurações
ARQUIVO_ENTRADA = 'dts1_candidatos_fase4_filtro_maturidade_APROVADOS.json'
ARQUIVO_SAIDA = 'dts1_candidatos_fase5_quality_gate_APROVADOS.json'
ARQUIVO_REJEITADOS = 'dts1_candidatos_fase5_quality_gate_REJEITADOS.json'

# --- CONFIGURAÇÃO DOS FILTROS ---
MIN_SIZE_KB = 100         # Mantemos: Tamanho mínimo para garantir código
ALLOW_ARCHIVED = False    # Mantemos: Rejeita arquivados (foco em ativos)
ALLOW_NO_LICENSE = True   # <--- MUDANÇA: Agora é TRUE. Aceitamos sem licença.

start_time = time.time()

stats = {
    "Total Processado": 0,
    "Aprovados": 0,
    "Rejeitados Total": 0,
    "Detalhe Rejeição": {
        "Arquivado": 0,
        "Insubstancial (Tamanho)": 0,
        "Idioma (Não Inglês)": 0,
        "Sem Documentação (Readme)": 0,
        "Sem Licença (Bloqueado)": 0
    },
    "Aprovados com Alerta": {
        "Sem Licença": 0
    },
    "Erros API": 0
}

print(f"--- Iniciando Fase 5: Filtros de Qualidade (FLEXÍVEL) ---")
print(f"Config: Size>={MIN_SIZE_KB}KB | Archived={ALLOW_ARCHIVED} | AllowNoLicense={ALLOW_NO_LICENSE}")

try:
    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f:
        projetos = json.load(f)
    print(f"Carregados {len(projetos)} candidatos da Fase 3.\n")
except FileNotFoundError:
    print("ERRO: Arquivo da Fase 3 não encontrado.")
    projetos = []

aprovados = []
rejeitados = []

for i, proj in enumerate(projetos):
    repo_name = proj['repo_name']
    stats["Total Processado"] += 1

    print(f"[{i+1}/{len(projetos)}] {repo_name}...", end=" ")

    motivo_rejeicao = None

    # 1. Checagem de Licença (Lógica ajustada)
    licenca = proj.get('license')
    has_license = not (not licenca or licenca == "null")

    # Se NÃO tem licença e NÃO permitimos sem licença -> Rejeita
    if not has_license and not ALLOW_NO_LICENSE:
        motivo_rejeicao = "Sem Licença"
        stats["Detalhe Rejeição"]["Sem Licença (Bloqueado)"] += 1

    # Se tem licença ou se permitimos sem licença -> Segue para API
    if not motivo_rejeicao:
        try:
            repo = g.get_repo(repo_name)

            # Arquivado
            if not ALLOW_ARCHIVED and repo.archived:
                motivo_rejeicao = "Arquivado"
                stats["Detalhe Rejeição"]["Arquivado"] += 1

            # Tamanho
            elif repo.size < MIN_SIZE_KB:
                 motivo_rejeicao = f"Insubstancial ({repo.size}KB)"
                 stats["Detalhe Rejeição"]["Insubstancial (Tamanho)"] += 1

            # Idioma (Readme)
            else:
                try:
                    readme = repo.get_readme()
                    content = readme.decoded_content.decode('utf-8')
                    if len(content) > 100:
                        lang = detect(content)
                        if lang != 'en':
                            motivo_rejeicao = f"Idioma ({lang})"
                            stats["Detalhe Rejeição"]["Idioma (Não Inglês)"] += 1
                    else:
                        print("(Readme curto)", end=" ")
                except:
                    motivo_rejeicao = "Sem Readme"
                    stats["Detalhe Rejeição"]["Sem Documentação (Readme)"] += 1

        except RateLimitExceededException:
            print("\n!!! Rate Limit. Pausando 60s...")
            time.sleep(60)
        except Exception as e:
            print(f"(Erro API: {str(e).split()[0]})", end=" ")
            stats["Erros API"] += 1

    # Decisão Final
    if motivo_rejeicao:
        print(f"-> REJEITADO ({motivo_rejeicao})")
        proj['motivo_rejeicao_fase5'] = motivo_rejeicao
        rejeitados.append(proj)
        stats["Rejeitados Total"] += 1
    else:
        print(f"-> APROVADO", end="")
        if not has_license:
            print(" (Alerta: Sem Licença)", end="")
            stats["Aprovados com Alerta"]["Sem Licença"] += 1
        print("")

        # Salva o status da licença para análise futura
        proj['has_license_file'] = has_license
        aprovados.append(proj)
        stats["Aprovados"] += 1

    time.sleep(0.4)

print("\n\n--- Processamento Concluído! Rode a Célula 3 para ver o relatório. ---")

# --- Célula 3: Relatório e Download ---
from google.colab import files
import json
import time
import datetime
from datetime import timedelta  # <--- Adicionei essa linha para garantir

# --- Finalização e Relatório ---
end_time = time.time()

# CORREÇÃO AQUI: Usamos 'timedelta' direto, sem o 'datetime.' antes
tempo_total = str(timedelta(seconds=int(end_time - start_time)))

print("\n" + "="*40)
print(f"       RELATÓRIO FINAL FASE 5")
print("="*40)
print(f"Tempo de Execução: {tempo_total}")
print("-" * 40)
print(f"Total Analisado:   {stats['Total Processado']}")
print(f"✅ APROVADOS:       {stats['Aprovados']}")
print(f"❌ REJEITADOS:      {stats['Rejeitados Total']}")
print("-" * 40)
print("MOTIVOS DE REJEIÇÃO:")
for motivo, qtd in stats["Detalhe Rejeição"].items():
    print(f" - {motivo:<25}: {qtd}")
print("="*40)

# Salvar arquivos
with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
    json.dump(aprovados, f, indent=4)
with open(ARQUIVO_REJEITADOS, 'w', encoding='utf-8') as f:
    json.dump(rejeitados, f, indent=4)

print(f"Arquivos salvos: '{ARQUIVO_SAIDA}' e '{ARQUIVO_REJEITADOS}'")

# Download Automático
print("Iniciando download...")
try:
    files.download(ARQUIVO_SAIDA)
    files.download(ARQUIVO_REJEITADOS)
except Exception as e:
    print("⚠️ Download automático falhou. Por favor, baixe manualmente na aba de arquivos à esquerda.")


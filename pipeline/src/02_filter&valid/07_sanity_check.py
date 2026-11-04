# --- Célula 1: Autenticação ---
!pip install PyGithub pandas
import getpass
from github import Github

# Autenticação
token = getpass.getpass('Cole seu token do GitHub:')
g = Github(token)

# ==============================================================================
# SCRIPT 7: VALIDAÇÃO TÉCNICA ESTRITA (FINAL)
# Objetivo: Filtrar os 859 projetos por EVIDÊNCIA DE CÓDIGO (package.json).
# Elimina projetos que citam "microfrontend" no texto mas não usam a tecnologia.
# ==============================================================================

import json
import time
import getpass
import pandas as pd
from datetime import timedelta
from github import Github, RateLimitExceededException, UnknownObjectException
from google.colab import files

# --- 1. CONFIGURAÇÕES ---
ARQUIVO_ENTRADA = 'dts1_candidatos_fase5_quality_gate_APROVADOS.csv'
ARQUIVO_SAIDA_APROVADOS = 'dts1_candidatos_fase6_sanity_check_APROVADOS.csv'
ARQUIVO_SAIDA_REJEITADOS = 'dts1_candidatos_fase6_sanity_check_REJEITADOS.csv'

# Lista A: Assinaturas Digitais de Micro-frontend (Se tiver, É MFE)
EVIDENCIAS_MFE = [
    "single-spa",
    "module-federation",
    "@angular-architects/module-federation",
    "vite-plugin-federation",
    "@module-federation/nextjs-mf",
    "qiankun",       # Framework Alibaba (Baseado em single-spa)
    "piral",         # Framework modular
    "luigi-client",  # Framework SAP Enterprise
    "frint",         # Framework leve
    "systemjs",      # Loader comum em MFEs
    "bit.dev",       # Componentes isolados
    "zone.js"        # Indício forte para Angular MFEs
]

# Lista B: Assinaturas de Monorepo (Geralmente usados para orquestrar MFEs)
EVIDENCIAS_MONO_DEPS = [
    "lerna",
    "nx",
    "turbo",
    "turborepo",
    "rush",
    "workspaces"     # Campo nativo do package.json (yarn/npm)
]

# Evidências de Arquivos na Raiz (Para o Resgate)
ARQUIVOS_CONFIG_MONOREPO = ["lerna.json", "turbo.json", "nx.json", "pnpm-workspace.yaml", "rush.json"]
PASTAS_SUSPEITAS = ["packages", "apps", "frontend", "client", "web"]

# --- 3. CARGA DE DADOS ---
print(f"\n📂 Carregando dataset: {ARQUIVO_ENTRADA}...")
try:
    df = pd.read_csv(ARQUIVO_ENTRADA, sep=';')
    lista_projetos = df.to_dict('records')
    print(f"✅ Sucesso! {len(lista_projetos)} projetos carregados via CSV.")
except:
    try:
        with open(ARQUIVO_ENTRADA.replace('.csv', '.json'), 'r') as f:
            lista_projetos = json.load(f)
        print(f"✅ Sucesso! {len(lista_projetos)} projetos carregados via JSON.")
    except:
        print("❌ ERRO: Arquivo não encontrado!")
        lista_projetos = []

# --- 4. EXECUÇÃO ---
aprovados = []
rejeitados = []
total = len(lista_projetos)
print(f"\n🚀 Iniciando Validação Técnica em {total} projetos...")
start_time = time.time()

for i, proj in enumerate(lista_projetos):
    nome = proj.get('Nome') or proj.get('repo_name')
    print(f"[{i+1}/{total}] {nome:<40}", end=" ")

    status = "REJEITAR (Sem Evidência)"
    evidencias = []
    tipo = "Nenhuma"

    try:
        repo = g.get_repo(nome)

        # TENTATIVA 1: package.json na Raiz
        try:
            contents = repo.get_contents("package.json")
            pkg = json.loads(contents.decoded_content.decode())
            deps = str(pkg.get('dependencies', {})) + str(pkg.get('devDependencies', {}))

            # Verifica MFE
            found_mfe = [lib for lib in EVIDENCIAS_MFE if lib in deps]
            found_mono = [tool for tool in EVIDENCIAS_MONO_DEPS if tool in deps]
            if 'workspaces' in pkg: found_mono.append('workspaces')

            if found_mfe:
                status = "CONFIRMADO"
                evidencias = found_mfe
                tipo = "Framework MFE"
            elif found_mono:
                status = "MONOREPO (Indício)"
                evidencias = found_mono
                tipo = "Estrutura Monorepo"

        except UnknownObjectException:
            # TENTATIVA 2: RESGATE (Arquivos de Config ou Pastas)
            try:
                root_files = [f.name for f in repo.get_contents("")]

                # Procura configs de monorepo (lerna.json, etc)
                resgate_config = [f for f in ARQUIVOS_CONFIG_MONOREPO if f in root_files]

                # Procura pastas comuns (frontend, packages)
                resgate_pasta = [f for f in PASTAS_SUSPEITAS if f in root_files]

                if resgate_config:
                    status = "CONFIRMADO (Resgate)"
                    evidencias = resgate_config
                    tipo = "Config na Raiz"
                elif resgate_pasta:
                    status = "INVESTIGAR (Resgate)" # Aprovamos para você olhar manual
                    evidencias = resgate_pasta
                    tipo = "Estrutura de Pastas"
                else:
                    status = "ERRO (Sem package.json)"
                    tipo = "Raiz vazia/Outra ling."
            except:
                status = "ERRO (Leitura Raiz)"

    except RateLimitExceededException:
        print("\n⏳ Rate Limit! Pausando 60s...")
        time.sleep(60)
        status = "SKIPPED"
    except Exception as e:
        status = "ERRO API"

    print(f"-> {status}")

    # Atualiza
    proj['Validacao_Tecnica'] = status
    proj['Evidencias'] = ", ".join(evidencias)
    proj['Tipo_Evidencia'] = tipo

    # Separação Inteligente
    # Agora aceitamos "INVESTIGAR" e "CONFIRMADO (Resgate)" na lista de aprovados
    if "CONFIRMADO" in status or "MONOREPO" in status or "INVESTIGAR" in status:
        aprovados.append(proj)
    else:
        rejeitados.append(proj)

    time.sleep(0.4)

# --- 5. RELATÓRIO E DOWNLOAD ---
elapsed = time.time() - start_time
tempo_str = str(timedelta(seconds=int(elapsed)))

# Cria um DataFrame temporário com TUDO só para gerar o relatório
todos_processados = aprovados + rejeitados
df_total = pd.DataFrame(todos_processados)

print("\n" + "="*60)
print(f"PROCESSO CONCLUÍDO EM: {tempo_str}")
print("="*60)

# Relatório Executivo
print(f"\n📈 BALANÇO GERAL:")
print(f"🟢 APROVADOS (Total): {len(aprovados)}")
print(f"🔴 REJEITADOS (Total): {len(rejeitados)}")

# Relatório Técnico (O que você pediu)
print(f"\n 📊 DETALHE TÉCNICO (Por Status):")
if not df_total.empty:
    print(df_total['Validacao_Tecnica'].value_counts())
else:
    print("Nenhum dado processado.")

print("-" * 60)

# Salva e Baixa Aprovados
if len(aprovados) > 0:
    df_aprov = pd.DataFrame(aprovados)
    df_aprov.to_csv(ARQUIVO_SAIDA_APROVADOS, index=False, sep=';', encoding='utf-8-sig')
    print(f"💾 Baixando Aprovados: {ARQUIVO_SAIDA_APROVADOS}")
    files.download(ARQUIVO_SAIDA_APROVADOS)

# Salva e Baixa Rejeitados
if len(rejeitados) > 0:
    df_rej = pd.DataFrame(rejeitados)
    df_rej.to_csv(ARQUIVO_SAIDA_REJEITADOS, index=False, sep=';', encoding='utf-8-sig')
    print(f"💾 Baixando Rejeitados: {ARQUIVO_SAIDA_REJEITADOS}")
    files.download(ARQUIVO_SAIDA_REJEITADOS)


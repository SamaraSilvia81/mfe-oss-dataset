## Estágio 01 - Mineração e Identificação

Esta fase consiste em executar 5 scripts para extrair metadados do GitHub e gerar a primeira base de dados filtrada e validada. O objetivo é passar de um pool bruto de candidatos para uma "lista de ouro" de projetos maduros e colaborativos.

**1. Fase 1: Script 1 - Busca por Heurísticas Técnicas**
  - **O que faz:** Funciona como o "garimpo" inicial. Ele usa a API de Busca de Código do GitHub para encontrar repositórios que provavelmente são microfrontends, procurando por palavras-chave (ex: "ModuleFederationPlugin") dentro de arquivos de configuração (ex: webpack.config.js).
  - **Saída:** A lista bruta de 2.793 candidatos `dts1_candidatos_fase1_heuristicas.json`

**2. Fase 2: Script 2 - Extrator de Metadados de Maturidade**
  - **O que faz:** Pega a lista bruta de 2.793 candidatos e "enriquece" cada um com dados de maturidade. Este é o script de coleta de longa duração (executado por 3h12m).
  - **Como:** Para cada repositório, ele chama a API e coleta: contagem total de commits, contagem total de contribuidores e a data do último push.
  - **Saída:** O arquivo de dados brutos `dts1_candidatos_fase2_metadados.json`
    
**3. Fase 3: Script 3 - Analisador de Distribuição**
  - **O que faz:**  É o "dashboard de decisão". Ele lê os dados brutos do Script 2 e os sumariza em tabelas (usando Pandas) para nos ajudar a visualizar o perfil do dataset e definir os filtros ideais.
  - **Saída:** As tabelas de distribuição (ex: Commits 51-100: 1042 projetos).
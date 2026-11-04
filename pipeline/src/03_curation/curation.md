### Estágio 3 - Curadoria e Catalogação

Esta fase finaliza a coleta automatizada realizando o "enriquecimento" dos dados. Enquanto as fases anteriores focaram em metadados leves (commits, stars) para filtragem rápida, esta etapa executa consultas intensivas na API do GitHub apenas sobre os **472 projetos selecionados**.

**Objetivo:** Coletar métricas complexas de saúde do projeto e gerar os artefatos finais para a etapa de Curadoria Manual.

**1. Etapa 1: Script de Mineração Profunda (Heavy Metrics)**
* **O que faz:** Itera sobre a lista de aprovados para calcular métricas que exigem varredura de histórico ou múltiplas chamadas de API.
* **Métricas Coletadas (Conforme Esquema MET-C):**
    * `Total Pull Requests`: Soma de PRs abertos e fechados (Proxy de colaboração externa).
    * `Closed Issues`: Contagem histórica de problemas resolvidos (Proxy de manutenção).
    * `Churn Rate`: Cálculo da frequência média de alteração de código (Adições + Deleções / Semanas de vida), indicando a estabilidade do projeto.
* **Estratégia:** Execução lenta com pausas (`sleep`) para evitar o bloqueio secundário da API (Abuse Detection Mechanism).

**2. Etapa 2: Geração da Planilha Mestra de Curadoria**
* **O que faz:** Consolida todos os dados coletados (Fase 1 + Fase 2 + Fase 3) em um arquivo CSV otimizado para análise humana.
* **Funcionalidades:**
    * **Classificação de Licenças:** Categoriza automaticamente as licenças em "Permissiva" (MIT, Apache) ou "Copyleft" (GPL), ou sinaliza "Sem Licença".
    * **Preparação Manual:** Cria colunas vazias padronizadas (`[M] Estrutura`, `[M] Qtd Módulos`) para o preenchimento durante a Fase 6 (Curadoria Manual).
* **Saída Final:** Arquivo `dataset_curadoria_FINAL_MASTER.csv`.

## Estágio 2 - Filtragem & Validação

Após a extração dos dados da API do GitHub, aplicam-se validações manuais e filtros finos automatizados. Assim, esta etapa aplica os filtros finos para selecionar apenas os repositórios que demonstram a complexidade arquitetural (ex: número mínimo de microfrontends) e a qualidade documental necessárias para a análise final.

**1. Fase 4: Filtro de Maturidade** Aplica os filtros de maturidade (decididos com base no Script 3) para "limpar" o dataset.
  - **Filtros:** MIN_COMMITS >= 100, MIN_CONTRIBUIDORES >= 1 e ANO >= 2021.
  - **Saída:** Os dois datasets finais:
    - `dts1_candidatos_fase4_filtro_maturidade_APROVADOS.json`
    - `dts1_candidatos_fase4_filtro_maturidade_REJEITADOS.json`

**2. Fase 5: Análise de Distribuição de Maturidade**
   - **O que faz:** É o "script de validação final". Ele roda o mesmo "Analisador" (Script 3) separadamente nos arquivos de Aprovados e Rejeitados.
   - **Objetivo:** Confirmar que os 2.561 projetos rejeitados eram de fato "demos" ou "solo" e que os 232 projetos aprovados são maduros e colaborativos, validando todo o pipeline.

**3. Fase 6: Seleção de Projetos (Quality Gate):**  Execução de um script automatizado (conceito MFE-HS) sobre os resultados da Fase 4 para aplicar filtros que exigem análise mais complexa (ex: README em inglês, Licença existente).
  - **Saída:** Os dois datasets finais:
    - `dts1_candidatos_fase5_quality_gate_APROVADOS.json`
    - `dts1_candidatos_fase5_quality_gate_REJEITADOS.json`

**4. Fase 7: Validação Técnica Estrita (Sanity Check):** Este script tem como objetivo identificar falsos positivos com uma validação estrita de projetos MFE e apurar nossa base atual de 859 projetos.
- **Saída:** Os dois datasets finais:
    - `dts1_candidatos_fase6_sanity_check_APROVADOS.json`
    - `dts1_candidatos_fase6_sanity_check_REJEITADOS.json`

**5. Fase 7: Validação Pós-Execução (Amostragem):** Inspeção manual de uma amostra (N=200 ou 5%) dos resultados da Fase 4 para validar a precisão geral do processo Github e identificar possíveis falsos positivos.
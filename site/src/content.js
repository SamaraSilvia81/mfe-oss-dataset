// Textos que não vêm dos arquivos do dataset. Edite aqui.
export const CONTENT = {
  candidates: 2793, // candidatos minerados antes da filtragem
  repoUrl: 'https://github.com/mfe-guidelines-ufpe/mfe-oss-dataset',
  abstract:
    'Conjunto de repositórios open source que adotam microfrontends, minerados no GitHub e catalogados à mão. Cada versão é um retrato datado da curadoria: a tabela, os números e os arquivos desta página mudam junto com ela.',
  stages: [
    { name: 'Mineração e identificação', text: 'Busca de repositórios candidatos e identificação dos que parecem usar microfrontends.' },
    { name: 'Filtragem e validação', text: 'Descarte dos candidatos que não se confirmam como projetos de microfrontends.' },
    { name: 'Mineração profunda', text: 'Coleta das métricas de atividade de cada repositório que ficou no dataset.' },
    { name: 'Curadoria manual', text: 'Classificação de cada repositório em três papéis: analista, revisor e adjudicador.' },
  ],
  roles: [
    ['Analista', 'Propõe a classificação do repositório.'],
    ['Revisor', 'Confere a proposta do analista.'],
    ['Adjudicador', 'Decide o registro. A validação exige unanimidade (ADR-007 do CuraData).'],
  ],
  divergenceNote: 'Sem unanimidade, o registro fica em divergência e um chamado é aberto.',
}

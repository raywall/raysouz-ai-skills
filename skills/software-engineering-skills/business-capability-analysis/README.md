# Business Capability Analysis

Skill para analisar um ou vários repositórios como partes de uma mesma solução
ou produto, explicando o funcionamento atual do negócio e identificando
oportunidades de melhoria, decomposição, modernização e rearquitetura.

## Quando Usar

Use esta skill para:

- compreender um sistema ou produto existente;
- analisar soluções distribuídas em vários repositórios;
- descobrir estruturas, responsabilidades e dependências;
- extrair domínios, modelos e capacidades de negócio;
- rastrear processos e jornadas ponta a ponta;
- identificar lógica e regras de negócio;
- mapear integrações e autoridade dos dados;
- preparar iniciativas de melhoria, decomposição ou rearquitetura.

## Modos

| Modo | Uso |
|---|---|
| `landscape` | Análise ampla do negócio e da solução. É o modo padrão. |
| `focused` | Análise profunda de uma capacidade, processo, regra ou jornada específica. |
| `assessment` | Ênfase em riscos, oportunidades e preparação para modernização. |
| `refresh` | Atualização de uma análise existente após mudanças nos repositórios. |

## Prompt Para Análise Completa

```text
Use a skill business-capability-analysis para realizar uma análise completa do
produto implementado pelos seguintes repositórios:

- /workspace/repos/frontend
- /workspace/repos/api
- /workspace/repos/payment-worker
- /workspace/repos/infrastructure

Considere os repositórios como partes de um único produto distribuído.

Execute no modo landscape e gere os artefatos em:
/workspace/analysis

Objetivos:

- descobrir a estrutura e as responsabilidades de cada sistema;
- identificar atores, objetivos e resultados de negócio;
- extrair modelos de domínio e bounded contexts candidatos;
- documentar capacidades de negócio;
- rastrear as principais jornadas ponta a ponta;
- identificar validações, cálculos, decisões, regras e transições de estado;
- mapear APIs, eventos, filas, jobs, bancos e integrações externas;
- identificar autoridade e consumidores dos dados;
- levantar riscos, acoplamentos, regras duplicadas e gaps;
- identificar oportunidades de melhoria, decomposição e rearquitetura.

Baseie conclusões em evidências rastreáveis.
Diferencie fatos confirmados, inferências, gaps e propostas.
Não altere os repositórios analisados.
Execute os validadores e o scanner de conteúdo sensível ao finalizar.
```

## Prompt Para Análise Focada

```text
Use a skill business-capability-analysis no modo focused para analisar a
capacidade "Processar pagamento".

Repositórios:

- /workspace/repos/portal
- /workspace/repos/payment-api
- /workspace/repos/payment-worker

Rastreie o fluxo desde o acionamento inicial até os resultados finais.
Inclua regras, cálculos, estados, integrações, falhas, retries, idempotência,
autoridade dos dados e efeitos visíveis para o usuário.

Gere os artefatos em /workspace/analysis/payment-processing.
Não altere os repositórios.
```

## Prompt Para Entendimento Funcional e Construção de Uma Nova Aplicação

Use este prompt quando o objetivo principal for compreender profundamente o
comportamento existente e produzir insumos funcionais para construir uma nova
aplicação, sem copiar acidentalmente as limitações da solução atual.

Substitua `<capacidade principal>` pelo nome da capacidade ou processo que deseja
analisar. O README mantém o exemplo genérico para poder ser reutilizado em
diferentes produtos.

```text
Use a skill business-capability-analysis para analisar profundamente o
funcionamento de negócio implementado pelos seguintes repositórios:

- /workspace/repos/frontend
- /workspace/repos/api
- /workspace/repos/workers
- /workspace/repos/integrations
- /workspace/repos/infrastructure

Considere todos os repositórios como partes de uma única solução distribuída.
O foco principal da análise é a capacidade "<capacidade principal>" e todos os
processos, regras e integrações necessários para seu funcionamento.

Execute uma análise landscape para compreender o contexto geral e uma análise
focused para aprofundar a capacidade principal.

Gere os artefatos em:
/workspace/analysis

Objetivo final:

Produzir uma especificação funcional portátil e baseada em evidências, capaz de
servir como insumo para projetar e construir uma nova aplicação que preserve os
comportamentos de negócio necessários, sem assumir que a arquitetura, tecnologia
ou limitações atuais devem ser reproduzidas.

Durante a análise:

- descubra o propósito do produto, atores, responsabilidades e resultados;
- identifique capacidades de negócio e seus limites;
- extraia o vocabulário utilizado pelo negócio;
- identifique entidades, value objects, agregados candidatos e ciclos de vida;
- rastreie jornadas ponta a ponta, incluindo caminhos de sucesso, rejeição,
  exceção, cancelamento, reversão e reprocessamento;
- extraia todas as validações, elegibilidades, cálculos, decisões, políticas,
  invariantes, transições de estado e regras temporais;
- identifique diferenças de comportamento por segmento, canal, perfil,
  configuração, origem ou tipo de operação;
- documente entradas, saídas, contratos, eventos e efeitos observáveis;
- mapeie autoridade dos dados, consumidores, integrações e dependências;
- identifique idempotência, retries, concorrência, compensações e tratamento de
  falhas;
- identifique regras duplicadas, contraditórias, implícitas ou implementadas em
  camadas inadequadas;
- diferencie comportamento essencial do negócio de detalhes e limitações da
  implementação atual;
- identifique gaps que precisam ser validados com especialistas do negócio.

Além dos artefatos padrão da skill, gere:

1. portable-functional-specification.md
   - comportamento funcional independente de tecnologia;
   - atores, gatilhos, precondições e resultados;
   - requisitos funcionais identificados com IDs estáveis;
   - regras e invariantes referenciadas por ID.

2. acceptance-scenarios.md
   - cenários de sucesso, falha, exceção e borda;
   - exemplos no formato Given/When/Then;
   - rastreabilidade para jornadas, regras e evidências.

3. data-contracts.md
   - entradas, saídas, eventos e estados intermediários;
   - campos obrigatórios, opcionais, defaults e restrições;
   - contratos descritos de forma abstrata e independente da tecnologia atual.

4. reconstruction-readiness.md
   - conhecimentos confirmados que já permitem implementação;
   - gaps e contradições que bloqueiam uma implementação segura;
   - decisões de negócio necessárias;
   - testes de caracterização e regressão recomendados;
   - riscos de reproduzir comportamentos incorretos ou acoplamentos atuais.

Requisitos de qualidade:

- baseie todas as conclusões em evidências rastreáveis;
- diferencie CONFIRMED, INFERRED, GAP e PROPOSED;
- não invente regras ausentes;
- não considere código existente automaticamente como comportamento desejado;
- preserve contradições até que sejam validadas;
- não proponha a arquitetura da nova aplicação antes de consolidar e validar o
  comportamento atual;
- não altere os repositórios analisados;
- não inclua segredos, credenciais ou dados pessoais nos artefatos;
- execute os validadores e o scanner de conteúdo sensível ao finalizar.

Ao concluir, apresente:

1. resumo do funcionamento da capacidade principal;
2. regras e invariantes mais importantes;
3. jornadas e estados identificados;
4. integrações e autoridade dos dados;
5. gaps que bloqueiam uma reconstrução segura;
6. nível de prontidão dos artefatos para iniciar o desenho da nova aplicação.
```

## Prompt Para Avaliação de Decomposição

```text
Use a skill business-capability-analysis no modo assessment sobre os
repositórios localizados em /workspace/repos.

Explique o funcionamento atual do negócio e identifique oportunidades de
decomposição do monólito.

Não defina domínios ou serviços apenas com base em módulos, deployables ou
tabelas. Considere coesão das capacidades, linguagem de domínio, invariantes,
autoridade dos dados, frequência de mudança, integrações e necessidades
operacionais.

Priorize oportunidades incrementais e reversíveis por impacto, esforço,
confiança, dependências e riscos.
```

## Prompt Para Atualizar Uma Análise

```text
Use a skill business-capability-analysis no modo refresh.

Análise existente:
/workspace/analysis/_business-capability-analysis

Repositórios:

- /workspace/repos/frontend
- /workspace/repos/api
- /workspace/repos/workers

Compare os commits atuais com o manifesto da análise.
Reanalise somente estruturas, jornadas, regras, integrações, dados, riscos e
oportunidades afetados pelas mudanças.

Preserve conhecimento confirmado que continua válido e registre contradições ou
gaps encontrados.
```

## Artefatos Gerados

A análise é criada em `_business-capability-analysis/`:

| Arquivo | Conteúdo |
|---|---|
| `analysis-manifest.json` | Escopo, modo, repositórios, commits e cobertura. |
| `evidence-register.md` | Evidências rastreáveis e contradições. |
| `executive-summary.md` | Funcionamento do negócio e principais conclusões. |
| `system-structure.md` | Estrutura técnica, arquitetura atual e acoplamentos. |
| `domain-model.md` | Vocabulário, entidades, ciclos de vida e domínios candidatos. |
| `capability-map.md` | Capacidades, resultados, sistemas e maturidade. |
| `business-processes.md` | Jornadas e processos ponta a ponta. |
| `business-rules.md` | Validações, cálculos, decisões, estados e exceções. |
| `integrations-and-data.md` | Integrações, contratos e autoridade dos dados. |
| `risks-and-opportunities.md` | Riscos e oportunidades priorizadas. |
| `gaps-and-decisions.md` | Lacunas e decisões necessárias. |
| `traceability-matrix.md` | Relação entre capacidades, regras, sistemas e evidências. |

## Execução Manual Dos Scripts

Os scripts normalmente são executados automaticamente pela skill, mas também
podem ser usados diretamente.

### Inventariar repositórios

```bash
python3 scripts/inventory_codebases.py \
  --analysis-name "Nome da análise" \
  --output /tmp/business-analysis-inventory.json \
  /workspace/repos/frontend \
  /workspace/repos/api
```

### Criar estrutura inicial

```bash
python3 scripts/init_analysis.py \
  --name "Nome da análise" \
  --output /workspace/analysis \
  --inventory /tmp/business-analysis-inventory.json
```

### Validar análise

```bash
python3 scripts/validate_analysis.py \
  /workspace/analysis/_business-capability-analysis
```

### Verificar conteúdo sensível

```bash
python3 scripts/scan_artifacts.py \
  /workspace/analysis/_business-capability-analysis
```

## Boas Práticas

- Informe todos os repositórios conhecidos que participam do produto.
- Descreva capacidades ou jornadas críticas quando conhecidas.
- Informe incidentes, dores ou objetivos de modernização relevantes.
- Permita que sistemas ausentes sejam registrados como gaps.
- Valide regras financeiras, regulatórias ou de alto impacto com especialistas.
- Use os artefatos como entrada para decisões, não como substituição da validação
  dos responsáveis pelo negócio.

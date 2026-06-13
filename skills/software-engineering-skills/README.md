# Software Engineering Skills

Conjunto de skills para transformar conhecimento extraido de sistemas
existentes em especificacoes funcionais, modelos de dominio, propostas de
servicos e artefatos executaveis.

A suite pode ser usada de forma incremental: primeiro para compreender o
produto e consolidar suas regras, depois para desenhar a nova solucao e,
finalmente, para gerar codigo, conectores, simuladores e workflows.

## Visao Geral

```text
repositorios
  -> business-capability-analysis
  -> functional-specification-author
  -> domain-context-designer
  -> service blueprints
     |-> aws-service-code-generator
     |-> graphql-connector-generator
     |-> business-rule-simulator
     `-> routing-slip-application-generator
```

O `software-factory-orchestrator` coordena a pipeline completa ou um conjunto de
estagios. As demais skills tambem podem ser usadas individualmente.

Todos os estagios devem preservar IDs rastreaveis, como:

- `CAP-*`: capacidade de negocio;
- `JRN-*`: jornada ou processo;
- `BR-*`: regra de negocio;
- `INT-*`: integracao;
- `FR-*`: requisito funcional;
- `SCN-*`: cenario de aceite;
- `CTX-*`: bounded context;
- `AGG-*`: agregado;
- `SVC-*`: servico candidato.

## Quando Usar Cada Skill

| Skill | Use quando precisar |
|---|---|
| `business-capability-analysis` | Compreender o funcionamento atual a partir de um ou mais repositorios. |
| `functional-specification-author` | Converter a analise atual em uma especificacao funcional independente de tecnologia. |
| `domain-context-designer` | Separar dominios e bounded contexts, modelar agregados e propor servicos. |
| `aws-service-code-generator` | Implementar em Go um servico aprovado para um destino AWS especifico. |
| `graphql-connector-generator` | Criar uma fachada GraphQL de leitura e enriquecimento sobre APIs e fontes de dados. |
| `business-rule-simulator` | Criar scripts executaveis para simular regras, decisoes e calculos. |
| `routing-slip-application-generator` | Criar workflows executaveis, observaveis, idempotentes e reprocessaveis. |
| `software-factory-orchestrator` | Executar e validar varios estagios como uma unica pipeline. |

## Premissas Importantes

- Repositorios, modulos, tabelas e deployables nao definem automaticamente
  dominios ou servicos.
- Comportamentos `CONFIRMED`, `INFERRED`, `GAP` e `PROPOSED` devem permanecer
  diferenciados.
- Uma inferencia ou proposta nao deve virar regra implementada sem decisao
  explicita.
- A especificacao funcional deve ser consolidada antes da escolha da
  arquitetura alvo.
- Codigo deve ser gerado para um servico aprovado por vez.
- Dados sensiveis, credenciais e payloads reais nao devem aparecer nos
  artefatos.

## Estrutura Do Workspace

Inicialize um workspace depois de gerar a analise do produto:

```bash
python3 scripts/init_factory.py \
  --name meu-produto \
  --analysis /workspace/analysis/_business-capability-analysis \
  --output /workspace/delivery
```

Estrutura criada:

```text
_software-factory/
  factory-manifest.json
  10-functional/
  20-domain/
  30-services/
  40-generated/
  50-simulations/
  60-workflows/
  90-decisions/
```

O contrato entre os estagios esta em
`contracts/artifact-contracts.md`.

## Usando O Orquestrador

Use o `software-factory-orchestrator` quando quiser executar mais de uma skill
em sequencia, preservar os handoffs e validar a pipeline.

### Prompt Para Especificacao E Desenho De Dominio

```text
Use a skill software-factory-orchestrator para transformar a analise localizada
em:

/workspace/analysis/_business-capability-analysis

em uma proposta funcional e de dominio para uma nova solucao.

Objetivo:

- consolidar o comportamento funcional das capacidades <IDs ou nomes>;
- gerar requisitos e cenarios de aceite;
- separar subdominios e bounded contexts;
- modelar agregados, entidades, value objects, invariantes e eventos;
- propor service blueprints rastreaveis.

Execute ate o estagio domain.
Gere os artefatos em /workspace/delivery.

Preserve a rastreabilidade para capacidades, jornadas, regras, integracoes e
evidencias. Mantenha inferencias, gaps e propostas visiveis. Nao gere codigo
enquanto existirem decisoes de negocio que bloqueiem uma implementacao segura.
```

### Prompt Para Pipeline Completa

```text
Use a skill software-factory-orchestrator para executar a pipeline completa
utilizando:

Analise:
/workspace/analysis/_business-capability-analysis

Workspace:
/workspace/delivery/_software-factory

Escopo:
- capacidades: CAP-001, CAP-002;
- jornadas: JRN-001;
- regras: todas as regras confirmadas associadas ao escopo.

Objetivo:

1. gerar a especificacao funcional;
2. definir dominios, bounded contexts, modelos e service blueprints;
3. gerar simuladores para as regras de negocio;
4. gerar a fachada GraphQL necessaria para leituras e enriquecimento;
5. gerar os workflows routing-slip para as jornadas;
6. implementar o servico SVC-001 em Go para AWS Lambda.

Antes de cada geracao de codigo, valide o handoff anterior.
Nao implemente comportamento INFERRED ou GAP como regra confirmada.
Execute testes, validadores e scanners aplicaveis ao finalizar.
```

## Business Capability Analysis

Use `business-capability-analysis` como ponto de partida quando o conhecimento
do produto ainda esta distribuido nos repositorios.

### Entradas

- um ou mais repositorios;
- capacidade, processo ou jornada em foco, quando conhecida;
- objetivo da analise;
- diretorio de saida.

### Principais Saidas

- estrutura da solucao;
- dominios e capacidades;
- jornadas e regras de negocio;
- integracoes e autoridade dos dados;
- riscos, gaps e oportunidades;
- matriz de rastreabilidade.

### Prompt De Exemplo

```text
Use a skill business-capability-analysis para analisar os repositorios:

- /workspace/repos/frontend
- /workspace/repos/api
- /workspace/repos/workers
- /workspace/repos/infrastructure

Considere todos como partes de um unico produto distribuido.

Execute uma analise landscape e aprofunde as capacidades relacionadas a
<capacidade ou processo principal>.

Gere os artefatos em /workspace/analysis.

Descubra o funcionamento do negocio, atores, jornadas, regras, calculos,
estados, integracoes, autoridade dos dados, falhas, retries, idempotencia,
contradicoes e gaps.

Baseie conclusoes em evidencias rastreaveis, diferencie fatos, inferencias,
gaps e propostas, e nao altere os repositorios analisados.
```

Consulte `business-capability-analysis/README.md` para modos e prompts
adicionais.

## Functional Specification Author

Use `functional-specification-author` para converter a analise do estado atual
em uma especificacao funcional portavel, adequada para projetar uma nova
aplicacao sem copiar acidentalmente a arquitetura existente.

### Entradas

- `_business-capability-analysis/`;
- capacidades e jornadas em escopo;
- decisoes de negocio ja confirmadas.

### Saidas

Criadas em `10-functional/`:

- `functional-specification.md`;
- `acceptance-scenarios.md`;
- `data-contracts.md`;
- `traceability-matrix.md`.

### Prompt De Exemplo

```text
Use a skill functional-specification-author.

Analise de entrada:
/workspace/analysis/_business-capability-analysis

Workspace de saida:
/workspace/delivery/_software-factory

Escopo:
- capacidades: CAP-001 e CAP-003;
- jornadas: JRN-002;
- incluir todas as regras associadas ao escopo.

Crie uma especificacao funcional independente de tecnologia contendo atores,
gatilhos, precondicoes, fluxos principais, fluxos alternativos, resultados,
requisitos funcionais, requisitos nao funcionais, estados e contratos de dados.

Crie cenarios Given/When/Then para sucesso, rejeicao, falha, borda,
duplicidade e retry.

Preserve os IDs das evidencias e regras. Registre contradicoes e gaps como
decisoes pendentes. Nao escolha arquitetura, banco, protocolo ou AWS runtime.
Valide o estagio functional ao finalizar.
```

## Domain Context Designer

Use `domain-context-designer` para transformar a especificacao funcional em um
desenho DDD e criar os blueprints que alimentarao a implementacao.

### Entradas

- artefatos de `10-functional/`;
- regras, contratos de dados e cenarios de aceite;
- decisoes de negocio confirmadas.

### Saidas

Criadas em `20-domain/`:

- `domain-landscape.md`;
- `context-map.md`;
- `model-catalog.md`;
- `service-catalog.md`;
- `traceability-matrix.md`.

Para cada servico aprovado, cria em `30-services/<service>/`:

- `service-blueprint.yaml`;
- `acceptance-criteria.md`;
- contratos;
- rastreabilidade.

### Prompt De Exemplo

```text
Use a skill domain-context-designer.

Workspace:
/workspace/delivery/_software-factory

Utilize a especificacao localizada em 10-functional.

Separe o problema em subdominios core, supporting e generic. Defina bounded
contexts a partir da linguagem, invariantes, ciclos de vida, autoridade dos
dados e frequencia de mudanca.

Para cada contexto, modele:

- linguagem ubiqua;
- agregados, entidades e value objects;
- invariantes e servicos de dominio;
- commands, queries e eventos;
- relacionamentos com outros contextos;
- requisitos e regras atendidos.

Depois proponha candidatos SVC-* apenas quando os limites dos contextos
estiverem claros. Gere service blueprints para os candidatos aprovados.

Nao use repositorios, modulos ou tabelas atuais como limites automaticos.
Apresente alternativas e validacoes necessarias para limites incertos.
Valide os estagios domain e services ao finalizar.
```

## AWS Service Code Generator

Use `aws-service-code-generator` para implementar um unico service blueprint em
Go para um destino AWS explicitamente informado.

### Entradas

- `service-blueprint.yaml`;
- criterios de aceite e contratos;
- AWS runtime;
- repositorio ou diretorio onde o servico sera criado.

### Saidas

Criadas em `40-generated/<service>/`:

- implementacao Go em Clean Architecture;
- adapters de entrada e saida;
- testes unitarios, integracao, contrato e aceite;
- infraestrutura como codigo;
- configuracao, observabilidade e seguranca;
- `generation-report.md`.

### Prompt Para Lambda

```text
Use a skill aws-service-code-generator para implementar o servico:

/workspace/delivery/_software-factory/30-services/example-service/service-blueprint.yaml

Destino:
- AWS Lambda com arquitetura arm64;
- API Gateway para entrada sincronica;
- DynamoDB para os dados de propriedade do contexto;
- EventBridge e SQS para eventos assincronos;
- Terraform para infraestrutura;
- Go como linguagem.

Gere a implementacao em:
/workspace/delivery/_software-factory/40-generated/example-service

Implemente somente requisitos e regras confirmadas. Utilize Clean Architecture,
testes orientados pelos cenarios de aceite, IAM de menor privilegio,
idempotencia, timeouts, retries, DLQ, observabilidade e rastreabilidade.

Compile, formate, execute os testes, valide o Terraform e gere o
generation-report.md.
```

### Prompt Para ECS Fargate

```text
Use a skill aws-service-code-generator para implementar o blueprint SVC-002.

Destino AWS: ECS Fargate atras de ALB.
Persistencia: Aurora PostgreSQL.
Integracoes assincronas: SNS e SQS.
Linguagem: Go.
Infraestrutura: Terraform.

Justifique configuracoes de runtime, escalabilidade e resiliencia.
Inclua graceful shutdown, health checks, migracoes, testes e observabilidade.
Nao implemente gaps como comportamento definitivo.
```

## GraphQL Connector Generator

Use `graphql-connector-generator` para construir uma fachada de leitura,
enriquecimento e anticorrupcao usando `go-graphql-connector`.

Esta skill nao deve ser usada para comandos ou mutacoes de negocio.

### Entradas

- contratos de dados;
- fontes e integracoes;
- formato desejado da query GraphQL;
- origem das configuracoes;
- runtime alvo.

### Saidas

- `config/service.json`;
- `config/schema.json`;
- `config/connectors.json`;
- `config/mock.json`, quando necessario;
- `connector.go`;
- queries, requests de exemplo e testes.

### Prompt De Exemplo

```text
Use a skill graphql-connector-generator para gerar uma fachada de leitura para
o servico SVC-001.

Entradas:
- blueprint: /workspace/delivery/_software-factory/30-services/example-service/service-blueprint.yaml
- contratos: /workspace/delivery/_software-factory/30-services/example-service/contracts
- integracoes: INT-001, INT-003 e INT-005.

Requisitos:
- agregar dados das fontes REST e DynamoDB descritas nos contratos;
- expor uma query dataSources;
- carregar schema e connectors de arquivos locais no ambiente local;
- suportar configuracao via S3 no ambiente AWS;
- executar localmente e em Lambda integrada a ALB;
- usar Secrets Manager para credenciais;
- configurar timeouts, retries, circuit breaker e transformacao de respostas.

Gere service.json, schema.json, connectors.json, mock.json quando necessario,
connector.go, queries de exemplo e testes.

Inspecione os exemplos e APIs instaladas do go-graphql-connector antes de gerar
o codigo. Nao invente construtores ou adapters.
```

## Business Rule Simulator

Use `business-rule-simulator` para tornar regras, decisoes e calculos
executaveis e inspecionaveis no Business Rules Studio antes ou durante a
implementacao.

### Entradas

- requisitos e use cases;
- regras de negocio;
- contratos de dados;
- modelos de dominio, quando disponiveis.

### Saidas

Criadas em `50-simulations/<context>/`:

- um script YAML por use case ou processo decisorio;
- mocks editaveis;
- `scenario-matrix.md`;
- links entre use cases, quando necessario.

### Prompt De Exemplo

```text
Use a skill business-rule-simulator.

Workspace:
/workspace/delivery/_software-factory

Gere simuladores para os use cases UC-001, UC-002 e UC-004, cobrindo as regras
BR-VAL-001, BR-DEC-002, BR-CALC-001 e BR-STATE-003.

Para cada use case:

- crie um script YAML separado;
- represente entradas em input;
- represente consultas externas com mocks editaveis;
- use CEL para validacoes, decisoes e calculos;
- gere resultados terminais claros;
- inclua os IDs das regras nas descricoes;
- crie cenarios de sucesso, rejeicao, borda, duplicidade e falha externa.

Use somente dados sinteticos. Valide a sintaxe YAML e as referencias CEL.
Gere os artefatos em 50-simulations.
```

## Routing Slip Application Generator

Use `routing-slip-application-generator` para transformar uma jornada ou
processo em workflows executaveis pelo `routing-slip-pattern`.

### Entradas

- jornada, use cases e regras;
- integracoes;
- service blueprint;
- trigger e runtime desejados.

### Saidas

Criadas em `60-workflows/<service>/`:

- `config.yaml`;
- `workflows/*.yaml`;
- bootstrap Go ou handler Lambda;
- payloads e eventos de teste;
- artefatos locais ou de deploy solicitados.

### Prompt De Exemplo

```text
Use a skill routing-slip-application-generator para implementar a jornada
JRN-001 do servico SVC-001.

Workspace:
/workspace/delivery/_software-factory

Trigger:
- SQS em modo assincrono;
- uma mensagem por evento;
- suporte a partial batch failure.

Requisitos:

- mapear validacoes e regras para handlers suportados;
- usar graphql_enrich para carregar contexto de leitura;
- usar aws_action ou rest_call para efeitos;
- dividir o fluxo com workflow_ref quando melhorar a coesao;
- preservar message_id e correlation_id;
- configurar state store DynamoDB, idempotencia, processing lock e
  reprocessamento;
- adicionar auditoria, logs, metricas, tracing e redacao de campos sensiveis;
- gerar payloads de sucesso, rejeicao, retry e retomada.

Gere config.yaml, workflows, bootstrap Go, testes e eventos de exemplo.
Inspecione as APIs instaladas do routing-slip-pattern antes de gerar codigo.
```

## Combinando GraphQL, Simuladores E Routing Slip

Um fluxo comum e:

1. simular regras com `business-rule-simulator`;
2. criar a fachada de leitura com `graphql-connector-generator`;
3. orquestrar o processo com `routing-slip-application-generator`;
4. implementar comandos e dominio com `aws-service-code-generator`.

### Prompt Para Ecossistema Low-Code

```text
Use as skills business-rule-simulator, graphql-connector-generator e
routing-slip-application-generator para criar um ambiente executavel para a
jornada JRN-003.

Utilize os artefatos funcionais, de dominio e de servico existentes em:
/workspace/delivery/_software-factory

Objetivos:

- criar simuladores para todas as decisoes e calculos da jornada;
- criar uma fachada GraphQL para todas as leituras e enriquecimentos;
- criar workflows routing-slip para validacao, enriquecimento, decisoes,
  efeitos, auditoria e reprocessamento;
- preservar os mesmos IDs de regras, use cases, integracoes e contratos nos
  tres conjuntos de artefatos;
- gerar dados sinteticos e cenarios regressivos compartilhados.

Nao use GraphQL para comandos. Nao transforme mocks de simulacao em
integracoes de producao. Valide cada conjunto de artefatos ao finalizar.
```

## Validando Os Handoffs

Valide o manifesto:

```bash
python3 scripts/validate_factory.py \
  /workspace/delivery/_software-factory \
  --stage manifest
```

Valide um estagio:

```bash
python3 scripts/validate_factory.py \
  /workspace/delivery/_software-factory \
  --stage domain
```

Estagios aceitos:

- `manifest`;
- `functional`;
- `domain`;
- `services`;
- `generated`;
- `simulation`;
- `workflow`;
- `all`.

## Quality Gates

Antes de avancar para o proximo estagio, confirme:

### Analise

- jornadas representativas alcancam resultados de sucesso e falha;
- regras importantes possuem IDs e evidencias;
- integracoes e autoridade dos dados estao explicitas;
- gaps e contradicoes permanecem visiveis.

### Especificacao Funcional

- requisitos representam comportamento observavel;
- cenarios cobrem sucesso, rejeicao, falha e borda;
- contratos de dados sao independentes da tecnologia atual;
- requisitos e cenarios possuem rastreabilidade.

### Dominio E Servicos

- cada regra possui contexto responsavel;
- agregados possuem invariantes e comportamento;
- contextos possuem autoridade de dados clara;
- cada service blueprint pertence a um unico bounded context.

### Geracao

- comportamento implementado esta confirmado;
- codigo compila e testes passam;
- infraestrutura valida;
- segredos permanecem externos;
- resiliencia, seguranca e observabilidade foram tratadas;
- o relatorio de geracao registra o que foi implementado e o que permanece
  pendente.

## Boas Praticas

- Comece com um escopo pequeno e uma jornada representativa.
- Valide regras de alto impacto com especialistas antes da implementacao.
- Use o simulador para discutir regras antes de codifica-las.
- Gere e aprove um service blueprint antes de gerar codigo.
- Prefira mudancas incrementais e reversiveis.
- Preserve a rastreabilidade ate testes, codigo, workflows e contratos.
- Reexecute a analise quando mudancas relevantes ocorrerem nos repositorios.

# Crédito do Trabalhador - Gestão de Consignações

## Escopo

Descreve os eventos que administram a consignação vinculada ao contrato e ao
vínculo empregatício.

## Eventos de negócio

- **Averbação:** registra a consignação e habilita o desconto em folha.
- **Alteração:** atualiza condições permitidas de uma consignação existente.
- **Exclusão:** encerra a consignação por uma causa admitida.
- **Suspensão:** interrompe temporariamente seus efeitos ordinários.
- **Reativação:** restabelece uma consignação suspensa.

## Regras

- A consignação deve estar associada a vínculo elegível e contrato identificável.
- Cada evento deve respeitar a situação atual e produzir histórico rastreável.
- A exclusão pode exigir liberação de garantias vinculadas.
- Suspensão não equivale a liquidação ou exclusão.
- Alterações não devem apagar o histórico contratual.
- O vínculo possui limite de contratos ativos ou suspensos conforme as regras
  vigentes do produto.

## Limites

As causas internas, alçadas e controles adicionais da instituição precisam de
definição corporativa.

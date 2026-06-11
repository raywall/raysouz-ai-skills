---
name: credito-trabalhador
description: Use when analyzing, explaining, modeling, reviewing, or documenting Crédito do Trabalhador business rules, including proposals, worker authorization, consignations, payroll bookkeeping, installments, contracts, guarantees, refinancing, portability, renegotiation, legacy loans, and FGTS-related product behavior.
---

# Crédito do Trabalhador

Use this skill for business analysis of the Crédito do Trabalhador product.

## Workflow

1. Identify the business subject and actors involved.
2. Read [`references/clt-rules-index.md`](references/clt-rules-index.md) and load
   only the references related to the subject.
3. Distinguish the worker, employment relationship, employer, financial
   institution, and other participants in every rule.
4. Treat eligibility, margin, contract, and payroll deduction as associated with
   a specific employment relationship.
5. Separate similar operations:
   - proposal from contracting;
   - contracting from averbação;
   - bookkeeping from payment and repasse;
   - renegotiation from refinancing;
   - portability proposal from effective portability;
   - portability from ownership transfer;
   - suspension from exclusion or liquidation.
6. Describe rules from a business perspective. Avoid API endpoints, payload
   fields, response codes, file layouts, and implementation architecture unless
   the user explicitly requests technical integration details.
7. Do not apply Crédito do Trabalhador rules to OP or INSS.
8. Do not invent corporate policies, systems, teams, states, deadlines, or
   procedures that are absent from the references.

## Analysis Checklist

- Identify the employment relationship affected by the event.
- State required authorization or worker participation.
- Describe eligibility and preconditions.
- Explain effects on contract, installments, payroll deductions, guarantees, and
  outstanding balance.
- Preserve the distinction between current state, event, and resulting state.
- Identify the responsibility of each participant.
- Call out missing corporate definitions instead of filling them generically.

## Reference Selection

- Start with [`references/clt-rules-index.md`](references/clt-rules-index.md).
- For contract lifecycle, combine only the relevant consignation, contract,
  installment, and post-sale references.
- For FGTS or guarantee behavior, read both `clt-rules-garantias.md` and
  `clt-rules-anexos-regras-comuns.md`.
- For portability, distinguish the proposal journey from the effective migration
  by reading both portability references when necessary.

## Reference Map

- Proposals and authorization:
  [`clt-rules-leilao-propostas.md`](references/clt-rules-leilao-propostas.md),
  [`clt-rules-autorizacao-dados-fgts.md`](references/clt-rules-autorizacao-dados-fgts.md),
  and
  [`clt-rules-propostas-portabilidade.md`](references/clt-rules-propostas-portabilidade.md).
- Contract lifecycle:
  [`clt-rules-gestao-consignacoes.md`](references/clt-rules-gestao-consignacoes.md),
  [`clt-rules-informacoes-contrato.md`](references/clt-rules-informacoes-contrato.md),
  [`clt-rules-renegociacao-termino-vinculo.md`](references/clt-rules-renegociacao-termino-vinculo.md),
  and
  [`clt-rules-antecipacao-parcelas.md`](references/clt-rules-antecipacao-parcelas.md).
- Payroll cycle and records:
  [`clt-rules-calendario-escrituracao-repasses.md`](references/clt-rules-calendario-escrituracao-repasses.md)
  and [`clt-rules-arquivos.md`](references/clt-rules-arquivos.md).
- Post-sale and migration:
  [`clt-rules-refinanciamento-portabilidade.md`](references/clt-rules-refinanciamento-portabilidade.md),
  [`clt-rules-troca-titularidade.md`](references/clt-rules-troca-titularidade.md),
  [`clt-rules-emprestimos-legados.md`](references/clt-rules-emprestimos-legados.md),
  and
  [`clt-rules-tombamento-compulsorio.md`](references/clt-rules-tombamento-compulsorio.md).
- Guarantees and balances:
  [`clt-rules-garantias.md`](references/clt-rules-garantias.md),
  [`clt-rules-anexos-regras-comuns.md`](references/clt-rules-anexos-regras-comuns.md),
  and
  [`clt-rules-saldo-devedor.md`](references/clt-rules-saldo-devedor.md).
- Access governance:
  [`clt-rules-perfis-acesso.md`](references/clt-rules-perfis-acesso.md).

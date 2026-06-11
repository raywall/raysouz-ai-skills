# Operation 04 - Generate and Validate

## Generate

Create or refresh the product skill using the templates.

The generated `SKILL.md` must:

- trigger on work involving the product, its domains, journeys, and vocabulary;
- explain how future agents should load relevant references;
- require checking applicable rules and affected systems before editing code;
- require stating impacts, assumptions, and unresolved gaps;
- remain concise and defer detailed knowledge to `references/`.

The generated references must contain only evidence-backed knowledge and visible
gaps. Use stable IDs for domains, journeys, requirements, rules, evidence, and
gaps so refreshes can update rather than rewrite arbitrarily.

## Manifest

Create `product-manifest.json` with:

- product and generated skill names;
- generation and verification timestamps;
- analyzed repositories with path, remote, branch, commit, and role;
- analysis scope and excluded systems;
- artifact schema version;
- counts of domains, journeys, requirements, rules, evidence, and gaps.

Do not include secrets, credentials, personal data, or raw production records.

## Validate

Run:

```bash
python3 scripts/validate_product_skill.py <generated-product-skill>
python3 scripts/scan_artifacts.py <generated-product-skill>
```

Review the generated skill against the original repositories:

- sample at least three confirmed rules;
- sample at least two journeys across repository boundaries when available;
- ensure all sampled evidence paths exist;
- ensure no `CONFIRMED` claim relies only on a guess or generic knowledge;
- ensure every unresolved contradiction is visible.

Report generated path, repositories analyzed, coverage summary, gaps requiring
human validation, and validation results.


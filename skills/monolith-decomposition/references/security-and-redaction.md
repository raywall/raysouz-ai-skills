# Security and Redaction

## Never include

- personal or customer data;
- credentials, secrets, tokens, certificates, or private keys;
- account, tenant, subscription, or resource identifiers classified as restricted;
- sensitive internal hostnames, URLs, IP addresses, or network topology;
- raw production records;
- information outside the user's approved access scope.

## Safe handling

- Work from sanitized copies when possible.
- Replace restricted values with descriptive placeholders.
- Store only approved source locators in the evidence register.
- Keep generated examples synthetic and free of business claims.
- Review diffs and generated documentation before publishing.
- Run `scripts/scan_artifacts.py` against generated artifacts.

## Detection limitations

Automated scanning is only a guardrail. It cannot prove that an artifact contains
no sensitive information. A human or approved review process must inspect outputs
before distribution.

## Stop conditions

Stop and request a sanitized alternative when:

- access requires exposing a credential;
- the only available source contains unnecessary personal data;
- a requested output would disclose restricted architecture or identifiers;
- source authorization is unclear.

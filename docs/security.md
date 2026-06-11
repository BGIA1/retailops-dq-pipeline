# Security

## Principles

- No real PII.
- No real secrets.
- No external datasets.
- No cloud resources created during local generation.
- Manual approval before any Azure deployment.
- OIDC instead of long-lived Azure credentials.

## Data Safety

Synthetic IDs use values like `CUST-000001`, `SKU-000001`, and `STORE-001`. The generator does not create names, emails, phones, addresses, or payment cards.

## Secrets

`.env.example` contains placeholders only. Real `.env` files are ignored. GitHub workflows are written to use repository/environment variables and OIDC for Azure.

## GitHub Security

- CodeQL is configured for Python.
- Dependabot covers pip, GitHub Actions, and Docker.
- GitHub secret scanning should be enabled after repository creation.
- Critical deployment changes should require review.

## Azure Security Model

The manual deployment path uses federated identity and `id-token: write`. No client secrets are required. Future production use should assign least-privilege roles such as Storage Blob Data Contributor only to the job identity and only on required containers.

## Threat Model

| Threat | Mitigation |
| --- | --- |
| Secret leakage | No secrets committed; `.env` ignored; OIDC preferred |
| PII exposure | Synthetic non-PII data only |
| Unreviewed deployment | Manual workflow and protected environment |
| Cost surprise | Guardrail confirmation and cost docs |
| Bad data entering analytics | Quarantine and quality threshold |

## Credential Revocation

If Azure federation is misconfigured, remove the federated credential from the app registration or managed identity, rotate any accidentally created credentials, and disable the `azure-demo` environment until reviewed.

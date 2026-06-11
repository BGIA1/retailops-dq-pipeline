# Cost Control

## Local

Local execution costs $0 MXN beyond the user's own machine resources.

## GitHub

GitHub Actions and GitHub Pages are expected to cost $0 within normal included GitHub usage for a small portfolio repository. Check current GitHub billing before heavy usage.

## Azure

Azure is not used until a future manual deployment. If deployed, these resources may generate cost:

- Storage Account with ADLS Gen2 hierarchical namespace.
- Azure Container Registry.
- Log Analytics ingestion and retention.
- Azure Container Apps Environment and Job execution.

## Shutdown Plan

- Stop running Container Apps Jobs.
- Delete the resource group when the demo is no longer needed.
- Reduce or delete Log Analytics retention.
- Delete container images from ACR.
- Remove OIDC federation if no longer required.

## Budget Controls

Before deployment:

- Create an Azure budget.
- Set cost alerts.
- Review SKU choices.
- Run `what-if`.
- Confirm the manual workflow input `I_UNDERSTAND_COSTS`.

Do not deploy without a budget and shutdown plan.

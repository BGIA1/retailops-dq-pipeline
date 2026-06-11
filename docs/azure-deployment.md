# Azure Deployment Readiness

Target architecture:

- Azure Container Apps Job for batch execution.
- Azure Container Registry for the RetailDQ image.
- Azure Storage Account with hierarchical namespace enabled for ADLS Gen2 style lakehouse storage.
- Containers/filesystems for raw, silver, gold, quarantine, and reports.
- Log Analytics Workspace for job logs.
- OIDC federation from GitHub Actions to Azure.

## Prerequisites

- Existing Azure subscription.
- Existing resource group.
- GitHub repository with environments enabled.
- GitHub environment `azure-demo`.
- Federated Azure credential configured for the GitHub workflow.
- Repository or environment variables:
  - `AZURE_CLIENT_ID`
  - `AZURE_TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID`

## What-if

Run only after Azure CLI login and budget review:

```bash
./infra/azure/scripts/what-if.sh <resource-group> eastus placeholder.azurecr.io/retaildq:manual-demo
```

## Manual Deployment

Deployment is not automatic. Use the GitHub Actions manual workflow or guarded scripts only after typing `I_UNDERSTAND_COSTS`.

```bash
./infra/azure/scripts/deploy.sh <resource-group> eastus placeholder.azurecr.io/retaildq:manual-demo
```

## Rollback

- Re-run the previous known-good image tag.
- Disable the Container Apps Job trigger.
- Delete newly created resource group resources if this is a demo environment.

## Shutdown

Delete the resource group or remove the Container Apps Job, ACR, Storage Account, and Log Analytics Workspace. Remove OIDC federation when the demo is retired.

## Important

This repository does not claim Azure deployment has happened. The files are deployment readiness artifacts only.

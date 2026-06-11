# Azure Deployment Readiness

This folder contains Bicep templates and guarded helper scripts for a future manual deployment of RetailDQ as an Azure Container Apps Job.

No resources are created by this repository generation. Run `what-if` first, review cost impact, configure OIDC, and use a short-lived manual deployment path only after approval.

Target resources:

- Azure Storage Account with hierarchical namespace enabled for ADLS Gen2 style lakehouse folders.
- Blob containers/filesystems for raw, silver, gold, quarantine, and reports.
- Azure Container Registry.
- Log Analytics Workspace.
- Azure Container Apps Environment.
- Azure Container Apps Job for batch execution.
- Managed identity placeholder for least-privilege storage access.

The sample parameters intentionally contain placeholders, not real tenant IDs, subscription IDs, or secrets.

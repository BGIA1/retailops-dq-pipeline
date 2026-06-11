#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${1:-}"
LOCATION="${2:-eastus}"
CONTAINER_IMAGE="${3:-placeholder.azurecr.io/retaildq:manual-demo}"

if [[ -z "${RESOURCE_GROUP}" ]]; then
  echo "Usage: ./infra/azure/scripts/deploy.sh <resource-group> [location] [container-image]"
  exit 1
fi

echo "WARNING: this command can create billable Azure resources."
echo "Confirm budgets, OIDC, least privilege, and shutdown plans before proceeding."
read -r -p "Type I_UNDERSTAND_COSTS to continue: " CONFIRMATION
if [[ "${CONFIRMATION}" != "I_UNDERSTAND_COSTS" ]]; then
  echo "Deployment cancelled."
  exit 1
fi

az deployment group create \
  --resource-group "${RESOURCE_GROUP}" \
  --template-file infra/azure/main.bicep \
  --parameters location="${LOCATION}" containerImage="${CONTAINER_IMAGE}"

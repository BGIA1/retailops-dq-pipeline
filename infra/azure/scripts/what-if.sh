#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${1:-}"
LOCATION="${2:-eastus}"
CONTAINER_IMAGE="${3:-placeholder.azurecr.io/retaildq:manual-demo}"

if [[ -z "${RESOURCE_GROUP}" ]]; then
  echo "Usage: ./infra/azure/scripts/what-if.sh <resource-group> [location] [container-image]"
  exit 1
fi

echo "Previewing Azure changes only. Review costs and security before any deployment."
az deployment group what-if \
  --resource-group "${RESOURCE_GROUP}" \
  --template-file infra/azure/main.bicep \
  --parameters location="${LOCATION}" containerImage="${CONTAINER_IMAGE}"

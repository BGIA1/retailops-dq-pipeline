param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [string]$Location = "eastus",
    [string]$ContainerImage = "placeholder.azurecr.io/retaildq:manual-demo"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Warning "This previews Azure changes only. It must not be treated as approval to deploy."
az deployment group what-if `
    --resource-group $ResourceGroup `
    --template-file infra/azure/main.bicep `
    --parameters location=$Location containerImage=$ContainerImage

param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [string]$Location = "eastus",
    [string]$ContainerImage = "placeholder.azurecr.io/retaildq:manual-demo"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Warning "This command can create billable Azure resources."
Write-Warning "Confirm that budgets, OIDC, least privilege, and shutdown plans are in place."
$confirmation = Read-Host "Type I_UNDERSTAND_COSTS to continue"
if ($confirmation -ne "I_UNDERSTAND_COSTS") {
    throw "Deployment cancelled."
}

az deployment group create `
    --resource-group $ResourceGroup `
    --template-file infra/azure/main.bicep `
    --parameters location=$Location containerImage=$ContainerImage

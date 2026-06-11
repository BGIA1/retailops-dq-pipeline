targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Short application name used as a resource prefix.')
param appName string = 'retaildq'

@description('Container image used by the Container Apps Job. Replace after ACR push.')
param containerImage string = 'placeholder.azurecr.io/retaildq:manual-demo'

@description('Tags applied to resources.')
param tags object = {
  workload: 'retaildq'
  environment: 'demo'
  managedBy: 'bicep'
}

var suffix = uniqueString(resourceGroup().id, appName)
var storageName = toLower('${appName}${suffix}st')
var acrName = toLower('${appName}${suffix}acr')
var logAnalyticsName = '${appName}-${suffix}-law'
var environmentName = '${appName}-${suffix}-cae'
var jobName = '${appName}-${suffix}-job'

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: storageName
    location: location
    tags: tags
  }
}

module acr 'modules/container-registry.bicep' = {
  name: 'acr'
  params: {
    name: acrName
    location: location
    tags: tags
  }
}

module logs 'modules/log-analytics.bicep' = {
  name: 'logs'
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

module environment 'modules/container-apps-environment.bicep' = {
  name: 'containerAppsEnvironment'
  params: {
    name: environmentName
    location: location
    logAnalyticsWorkspaceId: logs.outputs.workspaceId
    logAnalyticsCustomerId: logs.outputs.customerId
    logAnalyticsSharedKey: logs.outputs.sharedKey
    tags: tags
  }
}

module job 'modules/container-app-job.bicep' = {
  name: 'containerAppsJob'
  params: {
    name: jobName
    location: location
    environmentId: environment.outputs.environmentId
    containerImage: containerImage
    acrLoginServer: acr.outputs.loginServer
    storageAccountUrl: storage.outputs.dfsEndpoint
    tags: tags
  }
}

output storageAccountName string = storage.outputs.name
output storageAccountDfsEndpoint string = storage.outputs.dfsEndpoint
output acrName string = acr.outputs.name
output acrLoginServer string = acr.outputs.loginServer
output containerAppsEnvironmentName string = environment.outputs.name
output containerAppsJobName string = job.outputs.name
output containerAppsJobPrincipalId string = job.outputs.principalId

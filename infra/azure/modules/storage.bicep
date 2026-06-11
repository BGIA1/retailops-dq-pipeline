@description('Storage account name. Must be globally unique when deployed.')
param name string

param location string
param tags object

resource account 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    accessTier: 'Hot'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: account
  name: 'default'
}

var containers = [
  'raw'
  'silver'
  'gold'
  'quarantine'
  'reports'
]

resource lakehouseContainers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [for containerName in containers: {
  parent: blobService
  name: containerName
  properties: {
    publicAccess: 'None'
  }
}]

output name string = account.name
output id string = account.id
output dfsEndpoint string = account.properties.primaryEndpoints.dfs

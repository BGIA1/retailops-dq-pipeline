param name string
param location string
param environmentId string
param containerImage string
param acrLoginServer string
param storageAccountUrl string
param tags object

@description('CPU allocated to the batch container.')
param cpu string = '0.5'

@description('Memory allocated to the batch container.')
param memory string = '1Gi'

resource job 'Microsoft.App/jobs@2024-03-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    environmentId: environmentId
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 1800
      replicaRetryLimit: 1
      manualTriggerConfig: {
        parallelism: 1
        replicaCompletionCount: 1
      }
      registries: [
        {
          server: acrLoginServer
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'retaildq'
          image: containerImage
          command: [
            'retaildq'
          ]
          args: [
            'run'
            '--config'
            'configs/azure.sample.yaml'
            '--no-fail-on-quality-threshold'
          ]
          env: [
            {
              name: 'RETAILDQ_STORAGE_ACCOUNT_URL'
              value: storageAccountUrl
            }
            {
              name: 'RETAILDQ_CLOUD_MODE'
              value: 'azure-container-apps-job'
            }
          ]
          resources: {
            cpu: cpu
            memory: memory
          }
        }
      ]
    }
  }
}

output name string = job.name
output id string = job.id
output principalId string = job.identity.principalId

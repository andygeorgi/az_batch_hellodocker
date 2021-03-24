# Helloworld for Docker with Azure Batch

## Software requirements

This project was tested with the following software packages/modules:

| Software | Version |
| -------- |---------|
| azure-cli | 2.20.0<br>2.21.0 |
| Python | 3.6<br>3.7<br>3.8 |
| azure-batch | 9.0.0<br>10.0.0 |
| azure-common | 1.1.25<br>1.1.26 |
| azure-core | 1.9.0<br>1.12.0 |
| azure-storage-blob | 12.5.0<br>12.8.0 |

## Create and prepare a Batch Account

If you want to use the portal please refer to the official documentation on how to [Create a Batch Account with the Azure portal](https://docs.microsoft.com/en-us/azure/batch/batch-account-create-portal) and how to [Authenticate Batch service solutions with Active Directory](https://docs.microsoft.com/en-us/azure/batch/batch-aad-auth).

If you prefer a programmatic approach, you can follow the steps below:

```bash
#Set values for Azure resources
subscription="Microsoft Internal Subscription"
rg="rgbatchdemo"
region="westeurope"
storageAcc="sabatchdemo"
batchAcc="babatchdemo"
servicePrincipal="spbatchdemo"
```

```bash
#Azure login with MFA, opens in a new broswer window
az login
```

```bash
az account set --subscription "${subscription}"
az configure --defaults location="${region}"
```

```bash
# Create a resource group which will contain all resources of this helloworld example (output skipped ...)
az group create --name "${rg}"
```

```bash
# Create a storage account to be used by Azure Batch in the resource group created (output skipped ...)
az storage account create --resource-group "${rg}" --name "${storageAcc}" --sku Standard_LRS
```

```bash
# Create an Azure batch account in the specified resource group with the created storage account and note the accountEndpoint (output reduced)
az batch account create --resource-group "${rg}" --name "${batchAcc}" --storage-account "${storageAcc}"
    { 
      ...
      "accountEndpoint": "babatchdemo.westeurope.batch.azure.com",
      ...
    }
```

```bash
# Create an Azure service principal and note appID, password and tenant
az ad sp create-for-rbac --name "http://${servicePrincipal}" --role Contributor --years 1
    {
      "appId": "#####################################",
      "displayName": "spbatchdemo",
      "name": "http://spbatchdemo",
      "password": "#####################################",
      "tenant": "#####################################"
    }
```
## Checkout and run the helloworld script

```bash
# Checkout and prepare Python venv
git clone https://github.com/andygeorgi/az_batch_hellodocker.git
cd az_batch_hellodocker
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install azure-batch azure-common azure-core azure-storage-blob
```

```bash
# Fill Batch account and service principal information which have been created previously and check if the other parameters fit the needs
# common/config.py
    TENANT_ID = ''
    BATCH_ACCOUNT_URL = ''
    APP_ID = ''
    PASSWORD = ''
```

```bash
# Run the script that launches a job on a newly created pool, and a task that launches a Docker container that runs the task
# When it finishes, it waits for any key to be pressed, then deletes the pool, job, and task
python3 CreatePool-DockerHub-Image.py
    Attempting to create pool: container-test-pool-20210324-150514
    Created pool: container-test-pool-20210324-150514
    waiting for all nodes in pool container-test-pool-20210324-150514 to reach one of: frozenset({<ComputeNodeState.start_task_failed: 'starttaskfailed'>, <ComputeNodeState.idle: 'idle'>, <ComputeNodeState.unusable: 'unusable'>})
    waiting for 1 nodes to reach desired state...
    waiting for 1 nodes to reach desired state...
    waiting for 1 nodes to reach desired state...
    pool created successfully and 1 nodes are up and ready for job execution
    Creating job [container-test-job-20210324-150755]...
    Creating task [container-test-task-20210324-150755]...
    ######################################################################################################
    Pool [container-test-pool-20210324-150514], job [container-test-job-20210324-150755] and task [container-test-task-20210324-150755] will be deleted...
    ######################################################################################################
    Press any key to continue...
```

## Cleanup

```bash
# Delete the resource group and all contained resources
az group delete --resource-group "${rg}" --yes
```

```bash
# Delete the service principal and its role assignments
az ad sp delete --id http://${servicePrincipal}
```

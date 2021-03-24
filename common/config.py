# Batch account credentials
TENANT_ID = ''
RESOURCE = 'https://batch.core.windows.net/'
BATCH_ACCOUNT_URL = ''
APP_ID = ''
PASSWORD = ''
# Custom prefixes for jobs, pools and tasks
JOB_PREFIX = 'container-test-job'
POOL_PREFIX = 'container-test-pool'
TASK_PREFIX = 'container-test-task'
# Pool VM specifications
VM_SKU = 'STANDARD_D1_V2'
VM_NODE_AGENT='batch.node.ubuntu 20.04'
# Select image with container support and RDMA support if required: 
#   Offer: [centos|ubuntu-server]-container[-rdma]
# Some images require to accept T&Cs once before being used for the first time. You can use the portal or Azure CLI as in the following example:
#   az vm image terms accept --publisher microsoft-azure-batch --offer ubuntu-server-container --plan 20-04-lts
IMAGE_PUBLISHER='microsoft-azure-batch'
IMAGE_OFFER='ubuntu-server-container'
IMAGE_SKU='20-04-lts'
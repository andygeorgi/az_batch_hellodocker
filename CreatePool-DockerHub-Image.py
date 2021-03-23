import azure.batch

from azure.batch import BatchServiceClient
from azure.common.credentials import ServicePrincipalCredentials

import common.helpers
import common.config

# Create a Batch service client. We'll now be interacting with the Batch service
credentials = ServicePrincipalCredentials(
  client_id=common.config.CLIENT_ID,
  secret=common.config.SECRET,
  tenant=common.config.TENANT_ID,
  resource=common.config.RESOURCE
)

batch_client = BatchServiceClient(
  credentials,
  batch_url=common.config.BATCH_ACCOUNT_URL
)

image_ref_to_use = azure.batch.models.ImageReference(
    publisher=common.config.IMAGE_PUBLISHER,
    offer=common.config.IMAGE_OFFER,
    sku=common.config.IMAGE_SKU,
    version='latest')

# Specify container configuration, fetching the official Ubuntu container image from Docker Hub.
container_conf = azure.batch.models.ContainerConfiguration(
    container_image_names=['ubuntu'])

# To prefetch images from a private container registry complete and use the following
## Specify a container registry
#container_registry = batch.models.ContainerRegistry(
#        registry_server="myRegistry.azurecr.io",
#        user_name="myUsername",
#        password="myPassword")

## Create container configuration, prefetching Docker images from the container registry
#container_conf = batch.models.ContainerConfiguration(
#        container_image_names = ["myRegistry.azurecr.io/samples/myImage"],
#        container_registries =[container_registry])

pool_id = common.helpers.generate_unique_resource_name(common.config.POOL_PREFIX)

# Create a pool if it does not exist
# Add azure.batch.models.StartTask or azure.batch.models.NFSMountConfiguration as needed
new_pool = azure.batch.models.PoolAddParameter(
    id=pool_id,
    enable_inter_node_communication=True,
    virtual_machine_configuration=azure.batch.models.VirtualMachineConfiguration(
        image_reference=image_ref_to_use,
        container_configuration=container_conf,
        node_agent_sku_id=common.config.VM_NODE_AGENT),
    vm_size=common.config.VM_SKU,
    target_dedicated_nodes=1)

common.helpers.create_pool_if_not_exist(batch_client, new_pool)

# because we want all nodes to be available before any tasks are assigned
# to the pool, here we will wait for all compute nodes to reach idle
nodes = common.helpers.wait_for_all_nodes_state(batch_client, new_pool, frozenset(
          (azure.batch.models.ComputeNodeState.start_task_failed,
           azure.batch.models.ComputeNodeState.unusable,
           azure.batch.models.ComputeNodeState.idle)
    )
)

# ensure all nodes are idle
if any(node.state != azure.batch.models.ComputeNodeState.idle for node in nodes):
   raise RuntimeError('node(s) of pool {} not in idle state'.format(new_pool.id))
else:
   print('pool created successfully and {} nodes are up and ready for job execution'.format(new_pool.target_dedicated_nodes))

# Creates a job with a unique ID, associated with the pool created
job_id = common.helpers.generate_unique_resource_name(common.config.JOB_PREFIX)

print('Creating job [{}]...'.format(job_id))

job = azure.batch.models.JobAddParameter(
    id=job_id,
    pool_info=azure.batch.models.PoolInformation(pool_id=pool_id)
    )

batch_client.job.add(job)

# Creates a task with a unique ID, associated with the job created

task_id = common.helpers.generate_unique_resource_name(common.config.TASK_PREFIX)

print('Creating task [{}]...'.format(task_id))

# Removing container after the task finishes (--rm) and set the working directory to root (--workdir /)
task_container_settings = azure.batch.models.TaskContainerSettings(
    image_name='ubuntu',
    container_run_options='--rm --workdir /')

# The command line overrides the container ENTRYPOINT with a simple shell command that writes a small file to the task working directory on the host
task = azure.batch.models.TaskAddParameter(
    id=task_id,
    command_line='/bin/sh -c \"echo \'hello world\' > $AZ_BATCH_TASK_WORKING_DIR/output.txt\"',
    container_settings=task_container_settings
)

batch_client.task.add(job_id,task)

# Cleanup
print('######################################################################################################')
print('Pool [{}], job [{}] and task [{}] will be deleted...'.format(pool_id,job_id,task_id))
print('######################################################################################################')
print('Press any key to continue...')
input()

batch_client.task.delete(job_id,task_id)
batch_client.job.delete(job_id)
batch_client.pool.delete(pool_id)
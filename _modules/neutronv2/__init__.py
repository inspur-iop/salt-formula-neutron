try:
    import os_client_config
    from keystoneauth1 import exceptions as ka_exceptions
    REQUIREMENTS_MET = True
except ImportError:
    REQUIREMENTS_MET = False

from neutronv2 import networks
from neutronv2 import subnetpools
from neutronv2 import auto_alloc
from neutronv2 import subnets

network_get_details = networks.network_get_details
network_update = networks.network_update
network_delete = networks.network_delete
network_list = networks.network_list
network_create = networks.network_create
network_bulk_create = networks.network_bulk_create

subnetpool_get_details = subnetpools.subnetpool_get_details
subnetpool_update = subnetpools.subnetpool_update
subnetpool_delete = subnetpools.subnetpool_delete
subnetpool_list = subnetpools.subnetpool_list
subnetpool_create = subnetpools.subnetpool_create

auto_alloc_get_details = auto_alloc.auto_alloc_get_details
auto_alloc_delete = auto_alloc.auto_alloc_delete

subnet_list = subnets.subnet_list
subnet_create = subnets.subnet_create
subnet_bulk_create = subnets.subnet_bulk_create
subnet_get_details = subnets.subnet_get_details
subnet_update = subnets.subnet_update
subnet_delete = subnets.subnet_delete


__all__ = (
    'network_get_details', 'network_update', 'network_delete', 'network_list',
    'network_create', 'network_bulk_create', 'subnetpool_get_details',
    'subnetpool_update', 'subnetpool_delete', 'subnetpool_list',
    'subnetpool_create', 'auto_alloc_get_details', 'auto_alloc_delete',
    'subnet_list', 'subnet_create', 'subnet_bulk_create', 'subnet_get_details',
    'subnet_update', 'subnet_delete',
)


def __virtual__():
    """Only load neutronv2 if requirements are available."""
    if REQUIREMENTS_MET:
        return 'neutronv2'
    else:
        return False, ("The neutronv2 execution module cannot be loaded: "
                       "os_client_config or keystoneauth are unavailable.")

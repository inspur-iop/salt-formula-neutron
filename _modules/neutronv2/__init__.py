try:
    import os_client_config
    from keystoneauth1 import exceptions as ka_exceptions
    REQUIREMENTS_MET = True
except ImportError:
    REQUIREMENTS_MET = False

from neutronv2 import lists
from neutronv2 import networks
from neutronv2 import subnetpools
from neutronv2 import auto_alloc
from neutronv2 import subnets
from neutronv2 import agents
from neutronv2 import routers


network_get_details = networks.network_get_details
network_update = networks.network_update
network_delete = networks.network_delete
network_list = lists.network_list
network_create = networks.network_create
network_bulk_create = networks.network_bulk_create

subnetpool_get_details = subnetpools.subnetpool_get_details
subnetpool_update = subnetpools.subnetpool_update
subnetpool_delete = subnetpools.subnetpool_delete
subnetpool_list = lists.subnetpool_list
subnetpool_create = subnetpools.subnetpool_create

auto_alloc_get_details = auto_alloc.auto_alloc_get_details
auto_alloc_delete = auto_alloc.auto_alloc_delete

subnet_list = lists.subnet_list
subnet_create = subnets.subnet_create
subnet_bulk_create = subnets.subnet_bulk_create
subnet_get_details = subnets.subnet_get_details
subnet_update = subnets.subnet_update
subnet_delete = subnets.subnet_delete


agent_list = lists.agent_list
agent_get_details = agents.agent_get_details
agent_update = agents.agent_update
agent_delete = agents.agent_delete
l3_agent_router_list = agents.l3_agent_router_list
l3_agent_router_schedule = agents.l3_agent_router_schedule
l3_agent_router_remove = agents.l3_agent_router_remove
l3_agent_by_router_list = agents.l3_agent_by_router_list
dhcp_agent_list_networks = agents.dhcp_agent_list_networks
dhcp_agent_network_schedule = agents.dhcp_agent_network_schedule
dhcp_agent_network_remove = agents.dhcp_agent_network_remove
dhcp_agent_by_network_list = agents.dhcp_agent_by_network_list


router_list = lists.router_list
router_create = routers.router_create
router_get_details = routers.router_get_details
router_update = routers.router_update
router_delete = routers.router_delete
router_interface_add = routers.router_interface_add
router_interface_remove = routers.router_interface_remove


__all__ = (
    'network_get_details', 'network_update', 'network_delete', 'network_list',
    'network_create', 'network_bulk_create', 'subnetpool_get_details',
    'subnetpool_update', 'subnetpool_delete', 'subnetpool_list',
    'subnetpool_create', 'auto_alloc_get_details', 'auto_alloc_delete',
    'subnet_list', 'subnet_create', 'subnet_bulk_create', 'subnet_get_details',
    'subnet_update', 'subnet_delete',
    'agent_list', 'agent_delete', 'agent_get_details', 'agent_update',
    'l3_agent_by_router_list', 'l3_agent_router_list',
    'l3_agent_router_remove', 'l3_agent_router_schedule',
    'dhcp_agent_by_network_list', 'dhcp_agent_list_networks',
    'dhcp_agent_network_remove', 'dhcp_agent_network_schedule',
    'router_list', 'router_create', 'router_delete', 'router_get_details',
    'router_interface_add', 'router_interface_remove', 'router_update',
)


def __virtual__():
    """Only load neutronv2 if requirements are available."""
    if REQUIREMENTS_MET:
        return 'neutronv2'
    else:
        return False, ("The neutronv2 execution module cannot be loaded: "
                       "os_client_config or keystoneauth are unavailable.")

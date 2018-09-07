import logging
import time
from salt.exceptions import CommandExecutionError

from neutronv2.common import send
from neutronv2.arg_converter import get_by_name_or_uuid_multiple
from neutronv2.lists import agent_list


log = logging.getLogger(__name__)

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@send('get')
def agent_get_details(agent_id, **kwargs):
    url = '/agents/{}?{}'.format(agent_id, urlencode(kwargs))
    return url, {}


@send('put')
def agent_update(agent_id, **kwargs):
    url = '/agents/{}'.format(agent_id)
    json = {
        'agent': kwargs,
    }
    return url, {'json': json}


@send('delete')
def agent_delete(agent_id, **kwargs):
    url = '/agents/{}'.format(agent_id)
    return url, {}


@send('get')
def l3_agent_router_list(agent_id, **kwargs):
    url = '/agents/{}/l3-routers'.format(agent_id)
    return url, {}


@get_by_name_or_uuid_multiple([('router', 'router_id')])
@send('post')
def l3_agent_router_schedule(router_id, agent_id, **kwargs):
    url = '/agents/{}/l3-routers'.format(agent_id)
    json = {
        'router_id': router_id,
    }
    return url, {'json': json}


@get_by_name_or_uuid_multiple([('router', 'router_id')])
@send('delete')
def l3_agent_router_remove(router_id, agent_id, **kwargs):
    url = '/agents/{}/l3-routers/{}'.format(agent_id, router_id)
    return url, {}


@get_by_name_or_uuid_multiple([('router', 'router_id')])
@send('get')
def l3_agent_by_router_list(router_id, **kwargs):
    url = '/routers/{}/l3-agents'.format(router_id)
    return url, {}


@send('get')
def dhcp_agent_list_networks(agent_id, **kwargs):
    url = '/agents/{}/dhcp-networks'.format(agent_id)
    return url, {}


@get_by_name_or_uuid_multiple([('network', 'network_id')])
@send('post')
def dhcp_agent_network_schedule(network_id, agent_id, **kwargs):
    url = '/agents/{}/dhcp-networks'.format(agent_id)
    json = {
        'network_id': network_id,
    }
    return url, {'json': json}


@get_by_name_or_uuid_multiple([('network', 'network_id')])
@send('delete')
def dhcp_agent_network_remove(network_id, agent_id, **kwargs):
    url = '/agents/{}/dhcp-networks/{}'.format(agent_id, network_id)
    return url, {}


@get_by_name_or_uuid_multiple([('network', 'network_id')])
@send('get')
def dhcp_agent_by_network_list(network_id, **kwargs):
    url = '/networks/{}/dhcp-agents'.format(network_id)
    return url, {}


def wait_for_network_services(cloud_name, host_id=None,
                              admin_up_only=True,
                              retries=18, timeout=10):
    """
    Ensure services on specified host are alive, othervise fail with exception.

    :param host_id:              host name to wait or None (to check for all hosts)
    :param cloud_name:           name of cloud from os client config
    :param admin_up_only:        do not check for admin disabled agents
    :param timeout:              number of seconds to wait before retries
    :param retries:              number of retries
    """

    kwargs = {'alive': False}

    if admin_up_only:
      kwargs['admin_state_up'] = True

    if host_id is not None:
      kwargs['host'] = host_id

    res = None
    for i in range(retries):
        try:
          agents = agent_list(cloud_name=cloud_name, **kwargs)['agents']
          res = len(agents)
        except Exception as e:
          msg = "Failed to get agent list {0}".format(e)
          log.trace(msg)
          raise CommandExecutionError(e)

        if res == 0:
            return "All services are up"
        time.sleep(timeout)
    raise CommandExecutionError("Some agents are still down {}".format(agents))

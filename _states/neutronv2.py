import logging
import random

log = logging.getLogger(__name__)


def __virtual__():
    return 'neutronv2' if 'neutronv2.subnet_list' in __salt__ else False


def _neutronv2_call(fname, *args, **kwargs):
    return __salt__['neutronv2.{}'.format(fname)](*args, **kwargs)


def _resource_present(resource, name, changeable_params, cloud_name, **kwargs):
    try:
        method_name = '{}_get_details'.format(resource)
        exact_resource = _neutronv2_call(
            method_name, name, cloud_name=cloud_name
        )[resource]
    except Exception as e:
        if 'ResourceNotFound' in repr(e):
            try:
                method_name = '{}_create'.format(resource)
                resp = _neutronv2_call(
                    method_name, name=name, cloud_name=cloud_name, **kwargs
                )
            except Exception as e:
                log.exception('Neutron {0} create failed with {1}'.
                    format(resource, e))
                return _failed('create', name, resource)
            return _succeeded('create', name, resource, resp)
        elif 'MultipleResourcesFound' in repr(e):
            return _failed('find', name, resource)
        else:
            raise

    to_update = {}
    for key in kwargs:
        if key in changeable_params and (key not in exact_resource
                or kwargs[key] != exact_resource[key]):
            to_update[key] = kwargs[key]
    try:
        method_name = '{}_update'.format(resource)
        resp = _neutronv2_call(
            method_name, name=name, cloud_name=cloud_name, **to_update
        )
    except Exception as e:
        log.exception('Neutron {0} update failed with {1}'.format(resource, e))
        return _failed('update', name, resource)
    return _succeeded('update', name, resource, resp)


def _resource_absent(resource, name, cloud_name):
    try:
        method_name = '{}_get_details'.format(resource)
        _neutronv2_call(
            method_name, name, cloud_name=cloud_name
        )[resource]
    except Exception as e:
        if 'ResourceNotFound' in repr(e):
            return _succeeded('absent', name, resource)
        if 'MultipleResourcesFound' in repr(e):
            return _failed('find', name, resource)
    try:
        method_name = '{}_delete'.format(resource)
        _neutronv2_call(
            method_name, name, cloud_name=cloud_name
        )
    except Exception as e:
        log.error('Neutron delete {0} failed with {1}'.format(resource, e))
        return _failed('delete', name, resource)
    return _succeeded('delete', name, resource)


def network_present(name, cloud_name, **kwargs):
    changeable = (
        'admin_state_up', 'dns_domain', 'mtu', 'port_security_enabled',
        'provider:network_type', 'provider:physical_network',
        'provider:segmentation_id', 'qos_policy_id', 'router:external',
        'segments', 'shared', 'description', 'is_default'
    )

    return _resource_present('network', name, changeable, cloud_name, **kwargs)


def network_absent(name, cloud_name):
    return _resource_absent('network', name, cloud_name)


def subnet_present(name, cloud_name, network_id, ip_version, cidr, **kwargs):
    kwargs.update({'network_id': network_id,
                   'ip_version': ip_version,
                   'cidr': cidr})
    changeable = (
        'name', 'enable_dhcp', 'dns_nameservers', 'allocation_pools',
        'host_routes', 'gateway_ip', 'description', 'service_types',
    )

    return _resource_present('subnet', name, changeable, cloud_name, **kwargs)


def subnet_absent(name, cloud_name):
    return _resource_absent('subnet', name, cloud_name)


def subnetpool_present(name, cloud_name, prefixes, **kwargs):
    kwargs.update({'prefixes': prefixes})
    changeable = (
        'default_quota', 'min_prefixlen', 'address_scope_id',
        'default_prefixlen', 'description'
    )

    return _resource_present('subnetpool', name, changeable, cloud_name, **kwargs)


def subnetpool_absent(name, cloud_name):
    return _resource_absent('subnetpool', name, cloud_name)


def agent_present(name, agent_type, cloud_name, **kwargs):
    """
    :param name: agent host name
    :param agent_type: type of the agent. i.e. 'L3 agent' or 'DHCP agent'
    :param kwargs:
        :param description: agent description
        :param admin_state_up: administrative state of the agent
    """
    agents = _neutronv2_call(
        'agent_list', host=name, agent_type=agent_type,
        cloud_name=cloud_name)['agents']
    # Make sure we have one and only one such agent
    if len(agents) == 1:
        agent = agents[0]
        to_update = {}
        for key in kwargs:
            if kwargs[key] != agent[key]:
                to_update[key] = kwargs[key]
        if to_update:
            try:
                _neutronv2_call('agent_update', agent_id=agent['id'],
                                cloud_name=cloud_name, **kwargs)
            except Exception:
                return _failed('update', name, 'agent')
            return _succeeded('update', name, 'agent')
        return _succeeded('no_changes', name, 'agent')
    else:
        return _failed('find', name, 'agent')


def agents_disabled(name, cloud_name, **kwargs):
    """
    :param name: agent host name
    :param kwargs:
        :param description: agent description
        :param admin_state_up: administrative state of the agent
    """
    agents = _neutronv2_call(
        'agent_list', host=name, cloud_name=cloud_name)['agents']

    changes = {}
    for agent in agents:
      if agent['admin_state_up'] == True:
        try:
          changes[agent['id']] = _neutronv2_call('agent_update', agent_id=agent['id'],
                                                 cloud_name=cloud_name, admin_state_up=False)
        except Exception:
          return _failed('update', name, 'agent')
    return _succeeded('update', name, 'agent',changes)


def agents_enabled(name, cloud_name, **kwargs):
    """
    :param name: agent host name
    :param kwargs:
        :param description: agent description
        :param admin_state_up: administrative state of the agent
    """
    agents = _neutronv2_call(
        'agent_list', host=name, cloud_name=cloud_name)['agents']

    changes = {}
    for agent in agents:
      if agent['admin_state_up'] == False:
        try:
          changes[agent['id']] = _neutronv2_call('agent_update', agent_id=agent['id'],
                                                 cloud_name=cloud_name, admin_state_up=True)
        except Exception:
          return _failed('update', name, 'agent')

    return _succeeded('update', name, 'agent', changes)


def l3_resources_moved(name, cloud_name, target=None):
    """
    Ensure l3 resources are moved to target/other nodes
    Move non-HA (legacy and DVR) routers.

    :param name: agent host to remove routers from
    :param target: target host to move routers to
    :param cloud_name: name of cloud from os client config
    """

    all_agents = _neutronv2_call(
        'agent_list', agent_type='L3 agent', cloud_name=cloud_name)['agents']

    current_agent_id = [x['id'] for x in all_agents if x['host'] == name][0]

    if target is not None:
      target_agents = [x['id'] for x in all_agents if x['host'] == target]
    else:
      target_agents = [x['id'] for x in all_agents
                       if x['host'] != name and x['alive'] and x['admin_state_up']]

    if len(target_agents) == 0:
        log.error("No candidate agents to move routers.")
        return _failed('resources_moved', name, 'L3 agent')

    routers_on_agent = _neutronv2_call(
        'l3_agent_router_list', current_agent_id, cloud_name=cloud_name)['routers']

    routers_on_agent = [x for x in routers_on_agent if x['ha'] == False]

    try:
        for router in routers_on_agent:
            _neutronv2_call(
                'l3_agent_router_remove', router_id=router['id'],
                agent_id=current_agent_id, cloud_name=cloud_name)
            _neutronv2_call(
                'l3_agent_router_schedule', router_id=router['id'],
                agent_id=random.choice(target_agents),
                cloud_name=cloud_name)
    except Exception as e:
        log.exception("Failed to move router from {0}: {1}".format(name, e))
        return _failed('resources_moved', name, 'L3 agent')

    return _succeeded('resources_moved', name, 'L3 agent')


def _succeeded(op, name, resource, changes=None):
    msg_map = {
        'create': '{0} {1} created',
        'delete': '{0} {1} removed',
        'update': '{0} {1} updated',
        'no_changes': '{0} {1} is in desired state',
        'absent': '{0} {1} not present',
        'resources_moved': '{1} resources were moved from {0}',
    }
    changes_dict = {
        'name': name,
        'result': True,
        'comment': msg_map[op].format(resource, name),
        'changes': changes or {},
    }
    return changes_dict


def _failed(op, name, resource):
    msg_map = {
        'create': '{0} {1} failed to create',
        'delete': '{0} {1} failed to delete',
        'update': '{0} {1} failed to update',
        'find': '{0} {1} found multiple {0}',
        'resources_moved': 'failed to move {1} from {0}',
    }
    changes_dict = {
        'name': name,
        'result': False,
        'comment': msg_map[op].format(resource, name),
        'changes': {},
    }
    return changes_dict

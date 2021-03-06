# -*- coding: utf-8 -*-
'''
Management of Neutron resources
===============================
:depends:   - neutronclient Python module
:configuration: See :py:mod:`salt.modules.neutron` for setup instructions.
.. code-block:: yaml
    neutronng network present:
      neutronng.network_present:
        - name: Netone
        - provider_physical_network: PHysnet1
        - provider_network_type: vlan
'''
import logging
from functools import wraps
LOG = logging.getLogger(__name__)


def __virtual__():
    '''
    Only load if neutron module is present in __salt__
    '''
    return 'neutronng' if 'neutron.list_networks' in __salt__ else False


def _test_call(method):
    (resource, functionality) = method.func_name.split('_')
    if functionality == 'present':
        functionality = 'updated'
    else:
        functionality = 'removed'

    @wraps(method)
    def check_for_testing(name, *args, **kwargs):
        if __opts__.get('test', None):
            return _no_change(name, resource, test=functionality)
        return method(name, *args, **kwargs)
    return check_for_testing


def _neutron_module_call(method, *args, **kwargs):
    return __salt__['neutronng.{0}'.format(method)](*args, **kwargs)

def _get_tenant_id(tenant_name, *args, **kwargs):
    try:
        tenant_id = __salt__['keystoneng.tenant_get'](
            name=tenant_name, **kwargs)[tenant_name]['id']
    except:
        tenant_id = None
        LOG.debug('Cannot get the tenant id. User {0} is not an admin.'.format(
            kwargs.get('connection_user')))
    return tenant_id

def _auth(profile=None, endpoint_type=None):
    '''
    Set up neutron credentials
    '''
    if profile:
        credentials = __salt__['config.option'](profile)
        user = credentials['keystone.user']
        password = credentials['keystone.password']
        tenant = credentials['keystone.tenant']
        auth_url = credentials['keystone.auth_url']
    kwargs = {
        'connection_user': user,
        'connection_password': password,
        'connection_tenant': tenant,
        'connection_auth_url': auth_url,
        'connection_endpoint_type': endpoint_type,
        'profile': profile
    }

    return kwargs

@_test_call
def network_present(name=None,
                    network_id=None,
                    tenant=None,
                    provider_network_type=None,
                    provider_physical_network=None,
                    router_external=None,
                    admin_state_up=None,
                    shared=None,
                    provider_segmentation_id=None,
                    profile=None,
                    endpoint_type=None,
                    dns_domain=None,
                    is_default=None):
    '''
    Ensure that the neutron network is present with the specified properties.
    name
        The name of the network to manage
    '''
    connection_args = _auth(profile, endpoint_type)
    tenant_id = _get_tenant_id(tenant_name=tenant, **connection_args)

    existing_networks = _neutron_module_call(
        'list_networks', name=name, tenant_id=tenant_id,
        **connection_args)['networks']
    network_arguments = _get_non_null_args(
        name=name,
        provider_network_type=provider_network_type,
        provider_physical_network=provider_physical_network,
        router_external=router_external,
        admin_state_up=admin_state_up,
        shared=shared,
        tenant_id=tenant_id,
        provider_segmentation_id=provider_segmentation_id,
        dns_domain=dns_domain,
        is_default=is_default)

    if len(existing_networks) == 0:
        network_arguments.update(connection_args)
        res = _neutron_module_call(
            'create_network', **network_arguments)['network']

        if res.get('name') == name:
            return _created(name, 'network', res['name'])

    elif len(existing_networks) > 1:
        LOG.error("More than one network found with the name: {0}".format(
                  name))

    elif len(existing_networks) == 1:
        existing_network = existing_networks[0]
        LOG.info('CONNECTION STRINGS' + str(connection_args))
        LOG.info('existing ' + str(existing_network))
        LOG.info('new ' + str(network_arguments))
        existing_network = dict((key.replace(':', '_', 1), value)
                                for key, value in
                                existing_network.iteritems())
        # generate differential
        diff = dict((key, value) for key, value in network_arguments.iteritems()
                    if existing_network.get(key, None) != value)
        if diff:
            # update the changes
            network_arguments = diff.copy()
            network_arguments.update(connection_args)
            try:
                LOG.debug('updating network {0} with changes {1}'.format(
                    name, str(diff)))
                _neutron_module_call('update_network',
                                     existing_network['id'],
                                     **network_arguments)
                changes_dict = _created(name, 'network', diff)
                changes_dict['comment'] = '{1} {0} updated'.format(name, 'network')
                return changes_dict
            except:
                LOG.error('Could not update network {0}'.format(name))
                return _update_failed(name, 'network')
        return _no_change(name, 'network')
    return _create_failed(name, 'network')


@_test_call
def network_absent(name, network_id=None, profile=None, endpoint_type=None):
    connection_args = _auth(profile, endpoint_type)
    identifier = network_id or name
    _neutron_module_call(
        'delete_network', identifier, **connection_args)
    return _absent(identifier, 'network')


@_test_call
def subnet_present(name,
                   network_name=None,
                   network_id=None,
                   tenant=None,
                   cidr=None,
                   ip_version=4,
                   enable_dhcp=True,
                   allocation_pools=None,
                   gateway_ip=None,
                   dns_nameservers=None,
                   host_routes=None,
                   profile=None,
                   endpoint_type=None):
    '''
    Ensure that the neutron subnet is present with the specified properties.
    name
        The name of the subnet to manage
    '''
    if network_name is None and network_id is None:
        LOG.error("Network identificator name or uuid should be provided.")
        return _create_failed(name, 'subnet')

    connection_args = _auth(profile, endpoint_type)
    tenant_id = _get_tenant_id(tenant_name=tenant, **connection_args)

    existing_subnets = _neutron_module_call(
        'list_subnets', tenant_id=tenant_id, name=name,
         **connection_args)['subnets']

    subnet_arguments = _get_non_null_args(
        name=name,
        cidr=cidr,
        ip_version=ip_version,
        enable_dhcp=enable_dhcp,
        allocation_pools=allocation_pools,
        gateway_ip=gateway_ip,
        dns_nameservers=dns_nameservers,
        host_routes=host_routes)

    if network_id is None and network_name:
        existing_networks = _neutron_module_call(
            'list_networks', tenant_id=tenant_id, name=network_name,
            **connection_args)['networks']
        if len(existing_networks) == 0:
            LOG.error("Can't find network with name: {0}".format(network_name))
        elif len(existing_networks) == 1:
            network_id = existing_networks[0]['id']
        elif len(existing_networks) > 1:
            LOG.error("Multiple networks with name: {0} found.".format(
                      network_name))

    if network_id is None:
        return _create_failed(name, 'subnet')

    subnet_arguments['network_id'] = network_id

    if len(existing_subnets) == 0:
        subnet_arguments.update(connection_args)
        res = _neutron_module_call('create_subnet', tenant_id=tenant_id,
                                   **subnet_arguments)['subnet']
        if res.get('name') == name:
            return _created(name, 'subnet', res)
        return _create_failed(name, 'subnet')

    elif len(existing_subnets) == 1:
        existing_subnet = existing_subnets[0]

        # create differential
        LOG.error('existing ' + str(existing_subnet))
        LOG.error('new ' + str(subnet_arguments))
        diff = dict((key, value) for key, value in subnet_arguments.iteritems()
                    if existing_subnet.get(key, None) != value)
        if not diff:
            return _no_change(name, 'subnet')

        # update the changes
        subnet_arguments = diff.copy()
        subnet_arguments.update(connection_args)
        try:
            LOG.debug('updating subnet {0} with changes {1}'.format(
                name, str(diff)))
            _neutron_module_call('update_subnet',
                                 existing_subnet['id'],
                                 **subnet_arguments)
            changes_dict = _created(name, 'subnet', diff)
            changes_dict['comment'] = '{1} {0} updated'.format(name, 'subnet')
            return changes_dict
        except:
            LOG.error('Could not update subnet {0}'.format(name))
            return _update_failed(name, 'subnet')

    elif len(existing_subnets) > 1:
        LOG.error("Multiple subnets with name: {0} found".format(
                  name))
        return _create_failed(name, 'network')


@_test_call
def subnet_absent(name, subnet_id=None, profile=None, endpoint_type=None):
    connection_args = _auth(profile, endpoint_type)
    identifier = subnet_id or name
    _neutron_module_call(
        'delete_subnet', identifier, **connection_args)
    return _absent(name, 'subnet')


@_test_call
def router_present(name=None,
                   tenant=None,
                   gateway_network=None,
                   interfaces=None,
                   admin_state_up=True,
                   profile=None,
                   endpoint_type=None):
    '''
    Ensure that the neutron router is present with the specified properties.
    name
        The name of the subnet to manage
    gateway_network
        The network that would be the router's default gateway
    interfaces
        list of subnets the router attaches to
    '''
    connection_args = _auth(profile, endpoint_type)
    tenant_name = tenant
    try:
        tenant_id = __salt__['keystoneng.tenant_get'](
            name=tenant_name, **connection_args)[tenant_name]['id']
    except:
        tenant_id = None
        LOG.debug('Cannot get the tenant id. User {0} is not an admin.'.format(
            connection_args['connection_user']))
    existing_router = _neutron_module_call(
        'list_routers', name=name, **connection_args)
    if not existing_router:
        _neutron_module_call('create_router', name=name, tenant_id=tenant_id, admin_state_up=admin_state_up, **connection_args)
        created_router = _neutron_module_call(
            'list_routers', name=name, **connection_args)
        if created_router:
            router_id = created_router[name]['id']
            network = _neutron_module_call(
                'list_networks', name=gateway_network, **connection_args)["networks"]
            #TODO test for more networks
            gateway_network_id = network[0]['id']
            _neutron_module_call('router_gateway_set',
                                 router_id=router_id,
                                 external_gateway=gateway_network_id,
                                 **connection_args)
            for interface in interfaces:
                subnet = _neutron_module_call(
                    'list_subnets', name=interface, **connection_args)["subnets"]
                subnet_id = subnet[0]['id']
                _neutron_module_call('router_add_interface',
                                     router_id=router_id,
                                     subnet_id=subnet_id,
                                     **connection_args)
            return _created(name,
                            'router',
                            _neutron_module_call('list_routers',
                                                 name=name,
                                                 **connection_args))
        return _create_failed(name, 'router')

    router_id = existing_router[name]['id']
    existing_router = existing_router[name]
    diff = {}
    if ( admin_state_up == True or admin_state_up == False ) and existing_router['admin_state_up'] != admin_state_up:
        diff.update({'admin_state_up': admin_state_up})
    if gateway_network:
        network = _neutron_module_call(
            'list_networks', name=gateway_network, **connection_args)["networks"]
        gateway_network_id = network[0]['id']
        if not existing_router['external_gateway_info'] and not existing_router['external_gateway_info'] == None:
            if existing_router['external_gateway_info']['network_id'] != gateway_network_id:
                diff.update({'external_gateway_info': {'network_id': gateway_network_id}})
        elif not existing_router['external_gateway_info'] == None:
            if not 'network_id' in existing_router['external_gateway_info'] or existing_router['external_gateway_info']['network_id'] != gateway_network_id:
                diff.update({'external_gateway_info': {'network_id': gateway_network_id}})
    if diff:
        # update the changes
        router_args = diff.copy()
        router_args.update(connection_args)
        try:
            _neutron_module_call('update_router', existing_router['id'], **router_args)
            changes_dict = _created(name, 'router', diff)
            changes_dict['comment'] = 'Router {0} updated'.format(name)
            return changes_dict
        except:
            LOG.exception('Router {0} could not be updated'.format(name))
            return _update_failed(name, 'router')
    return _no_change(name, 'router')


def floatingip_present(name=None,
                       tenant_name=None,
                       subnet=None,
                       tenant=None,
                       network=None,
                       port_id=None,
                       fip_exists=False,
                       profile=None,
                       endpoint_type=None):
    '''
    Ensure that the floating ip address is present for an instance
    '''
    instance_id = __salt__['novang.server_get'](name=name, tenant_name=tenant_name, profile=profile)
    subnet_name = subnet
    connection_args = _auth(profile, endpoint_type)
    existing_subnet = _neutron_module_call(
        'list_subnets', name=subnet_name, **connection_args)["subnets"]
    subnet_id = existing_subnet[0]['id']

    ret = {}
    existing_ports = _neutron_module_call(
        'list_ports', **connection_args)
    existing_floatingips = _neutron_module_call(
        'list_floatingips', **connection_args)

    tenant = __salt__['keystoneng.tenant_get'](name=tenant_name, **connection_args)
    tenant_id = tenant[tenant_name]['id']
    existing_network = _neutron_module_call(
            'list_networks', name=network, **connection_args)["networks"]
    floating_network_id = existing_network[0]['id']

    for key, value in existing_ports.iteritems():
        try:
            if value['fixed_ips'][0]['subnet_id'] == subnet_id and value['device_id'] == instance_id:
                port_id=value['id']
        except:
            pass
    for key, value in existing_floatingips.iteritems():
        try:
            if value['floating_network_id'] == floating_network_id and value['port_id'] == port_id and value['tenant_id'] == tenant_id:
                fip_exists = True
                break
        except:
            pass

    if fip_exists == False:
        for key, value in existing_ports.iteritems():
            try:
                if value['fixed_ips'][0]['subnet_id'] == subnet_id and value['device_id'] == instance_id:
                    ret = _neutron_module_call('create_floatingip', floating_network_id=floating_network_id, port_id=value['id'], tenant_id=tenant_id, **connection_args)
            except:
                pass
        return _created('port', 'floatingip', ret)
    else:
        return _no_change('for instance {0}'.format(name), 'floatingip')


def security_group_present(name=None,
                           tenant=None,
                           description='',
                           rules=[],
                           profile=None,
                           endpoint_type=None):
    '''
    Ensure that the security group is present with the specified properties.
    name
        The name of the security group
    description
        The description of the security group
    rules
        list of rules to be added to the given security group
    '''
    # If the user is an admin, he's able to see the security groups from
    # other tenants. In this case, we'll use the tenant id to get an existing
    # security group.
    connection_args = _auth(profile, endpoint_type)
    tenant_name = tenant
    try:
        tenant_id = __salt__['keystoneng.tenant_get'](
            name=tenant_name, **connection_args)[tenant_name]['id']
    except:
        tenant_id = None
        LOG.debug('Cannot get the tenant id. User {0} is not an admin.'.format(
            connection_args['connection_user']))
    if tenant_id:
        security_group = _neutron_module_call(
            'list_security_groups', name=name, tenant_id=tenant_id,
            **connection_args)
    else:
        security_group = _neutron_module_call(
            'list_security_groups', name=name, **connection_args)

    if not security_group:
        # Create the security group as it doesn't exist already.
        security_group_id = _neutron_module_call('create_security_group',
                                                 name=name,
                                                 description=description,
                                                 tenant_id=tenant_id,
                                                 **connection_args)
    else:
        security_group_id = security_group[name]['id']

    # Set the missing rules attributes (in case the user didn't specify them
    # in pillar) to some default values.
    rules_attributes_defaults = {
        'direction': 'ingress',
        'ethertype': 'IPv4',
        'protocol': 'TCP',
        'port_range_min': None,
        'port_range_max': None,
        'remote_ip_prefix': None
    }
    for rule in rules:
        for attribute in rules_attributes_defaults.keys():
            if not rule.has_key(attribute):
                rule[attribute] = rules_attributes_defaults[attribute]

    # Remove all the duplicates rules given by the user in pillar.
    unique_rules = []
    for rule in rules:
        if rule not in unique_rules:
            unique_rules.append(rule)

    # Get the existing security group rules.
    existing_rules = _neutron_module_call(
        'list_security_groups',
        id=security_group_id,
        **connection_args)[name]['security_group_rules']

    new_rules = {}
    for rule in unique_rules:
        rule_found = False
        for existing_rule in existing_rules:
            attributes_match = True
            # Compare the attributes of the existing security group rule with
            # the attributes of the rule that we want to add.
            for attribute in rules_attributes_defaults.keys():
                existing_attribute = '' if not existing_rule[attribute] \
                                        else str(existing_rule[attribute]).lower()
                attribute = '' if not rule[attribute] \
                               else str(rule[attribute]).lower()
                if existing_attribute != attribute:
                    attributes_match = False
                    break
            if attributes_match:
                rule_found = True
                break
        if rule_found:
            # Skip adding the rule as it already exists.
            continue
        rule_index = len(new_rules) + 1
        new_rules.update({'Rule {0}'.format(rule_index): rule})
        _neutron_module_call('create_security_group_rule',
                             security_group_id=security_group_id,
                             direction=rule['direction'],
                             ethertype=rule['ethertype'],
                             protocol=rule['protocol'],
                             port_range_min=rule['port_range_min'],
                             port_range_max=rule['port_range_max'],
                             remote_ip_prefix=rule['remote_ip_prefix'],
                             tenant_id=tenant_id,
                             **connection_args)

    if not security_group:
        # The security group didn't exist. It was created and specified
        # rules were added to it.
        security_group = _neutron_module_call('list_security_groups',
                                              id=security_group_id,
                                              **connection_args)[name]
        return _created(name, 'security_group', security_group)
    if len(new_rules) == 0:
        # Security group already exists and specified rules are already
        # present.
        return _no_change(name, 'security_group')
    # Security group already exists, but the specified rules were added to it.
    return _updated(name, 'security_group', {'New Rules': new_rules})


def port_present(network_name, profile=None, endpoint_type=None, name=None,
                 tenant=None, description='', fixed_ips=None, device_id=None,
                 device_owner=None, binding_host_id=None, admin_state_up=True,
                 mac_address=None, vnic_type=None, binding_profile=None,
                 security_groups=None, extra_dhcp_opt=None, qos_policy=None,
                 allowed_address_pair=None, dns_name=None):
    """
    Ensure the port is present with specified parameters.

    :param network_name: Name of the network to create port in
    :param profile: Authentication profile
    :param endpoint_type: Endpoint type
    :param name: Name of this port
    :param tenant: Tenant in which the port should be created, avaiable for
                   admin only.
    :param description: Port description
    :param fixed_ips: Desired IP and/or subnet for this port:
                      subnet_id=<name_or_id>,ip_address=<ip>.
    :param device_id: Device ID of this port
    :param device_owner: Device owner of this port
    :param binding_host_id: he ID of the host where the port resides.
    :param admin_state_up: Admin state of this port
    :param mac_address: MAC address of this port
    :param vnic_type: VNIC type for this port
    :param binding_profile: Custom data to be passed as binding:profile
    :param security_groups: Security group associated with the port
    :param extra_dhcp_opt: Extra dhcp options to be assigned to this port:
                           opt_na me=<dhcp_option_name>,opt_value=<value>,
                                     ip_version={4, 6}
    :param qos_policy: ID or name of the QoS policy that shouldbe attached to
                       the resource
    :param allowed_address_pair: ip_address=IP_ADDR|CIDR[,mac_address=MAC_ADDR]
                                 Allowed address pair associated with the port.
                                 "ip_address" parameter is required. IP address
                                 or CIDR can be specified for "ip_address".
                                 "mac_address" parameter is optional.
    :param dns_name: Assign DNS name to the port (requires DNS integration
                     extension)
    """

    connection_args = _auth(profile, endpoint_type)
    tenant_id = _get_tenant_id(tenant_name=tenant, **connection_args)
    network_id = None
    port_exists = False

    port_arguments = _get_non_null_args(
        name=name, tenant_id=tenant_id, description=description,
        fixed_ips=fixed_ips, device_id=device_id, device_owner=device_owner,
        admin_state_up=admin_state_up,
        mac_address=mac_address, vnic_type=vnic_type,
        binding_profile=binding_profile,
        extra_dhcp_opt=extra_dhcp_opt, qos_policy=qos_policy,
        allowed_address_pair=allowed_address_pair, dns_name=dns_name)
    if binding_host_id:
        port_arguments['binding:host_id'] = binding_host_id
    if security_groups:
        sec_group_list = []
        for sec_group_name in security_groups:
            security_group = _neutron_module_call(
                'list_security_groups', name=sec_group_name, **connection_args)
            if security_group:
                sec_group_list.append(security_group[sec_group_name]['id'])
        port_arguments['security_groups'] = sec_group_list

    existing_networks = _neutron_module_call(
        'list_networks', tenant_id=tenant_id, name=network_name,
        **connection_args)['networks']
    if len(existing_networks) == 0:
        LOG.error("Can't find network with name: {0}".format(network_name))
    elif len(existing_networks) == 1:
        network_id = existing_networks[0]['id']
    elif len(existing_networks) > 1:
        LOG.error("Multiple networks with name: {0} found.".format(network_name))

    if network_id is None:
        return _create_failed(name, 'port')

    port_arguments['network_id'] = network_id

    existing_ports = _neutron_module_call(
        'list_ports', network_id=network_id, tenant_id=tenant_id,
        **connection_args)

    if name:
        for key, value in existing_ports.iteritems():
            try:
                if value['name'] == name and value['tenant_id'] == tenant_id:
                    port_exists = True
                    break
            except KeyError:
                pass

    if not port_exists:
        port_arguments.update(connection_args)
        res = _neutron_module_call('create_port', **port_arguments)['port']
        if res['name'] == name:
            return _created(name, 'port', res)
        return _create_failed(name, 'port')
    else:
        return _no_change('for instance {0}'.format(name), 'port')


def _created(name, resource, resource_definition):
    changes_dict = {'name': name,
                    'changes': resource_definition,
                    'result': True,
                    'comment': '{0} {1} created'.format(resource, name)}
    return changes_dict

def _updated(name, resource, resource_definition):
    changes_dict = {'name': name,
                    'changes': resource_definition,
                    'result': True,
                    'comment': '{0} {1} updated'.format(resource, name)}
    return changes_dict

def _no_change(name, resource, test=False):
    changes_dict = {'name': name,
                    'changes': {},
                    'result': True}
    if test:
        changes_dict['comment'] = \
            '{0} {1} will be {2}'.format(resource, name, test)
    else:
        changes_dict['comment'] = \
            '{0} {1} is in correct state'.format(resource, name)
    return changes_dict


def _deleted(name, resource, resource_definition):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} removed'.format(resource, name),
                    'result': True}
    return changes_dict


def _absent(name, resource):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} not present'.format(resource, name),
                    'result': True}
    return changes_dict


def _delete_failed(name, resource):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} failed to delete'.format(resource,
                                                                 name),
                    'result': False}
    return changes_dict

def _create_failed(name, resource):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} failed to create'.format(resource,
                                                                 name),
                    'result': False}
    return changes_dict

def _update_failed(name, resource):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} failed to update'.format(resource,
                                                                 name),
                    'result': False}
    return changes_dict


def _get_non_null_args(**kwargs):
    '''
    Return those kwargs which are not null
    '''
    return dict((key, value,) for key, value in kwargs.iteritems()
                if value is not None)

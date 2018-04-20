from neutronv2.common import send, get_by_name_or_uuid
from neutronv2 import networks
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

RESOURCE_LIST_KEY = 'subnets'


@send('get')
def subnet_list(**kwargs):
    url = '/subnets?{}'.format(urlencode(kwargs))
    return url, {}


@get_by_name_or_uuid(networks.network_list, networks.RESOURCE_LIST_KEY,
                     res_id_key='network_id')
@send('post')
def subnet_create(network_id, ip_version, cidr, **kwargs):
    url = '/subnets'
    json = {
        'subnet': {
            'network_id': network_id,
            'ip_version': ip_version,
            'cidr': cidr,
        }
    }
    json['subnet'].update(kwargs)
    return url, {'json': json}


@send('post')
def subnet_bulk_create(subnets, **kwargs):
    url = '/subnets'
    json = {
        'subnets': subnets,
    }
    return url, {'json': json}


@get_by_name_or_uuid(subnet_list, RESOURCE_LIST_KEY)
@send('get')
def subnet_get_details(subnet_id, **kwargs):
    url = '/subnets/{}'.format(subnet_id)
    return url, {}


@get_by_name_or_uuid(subnet_list, RESOURCE_LIST_KEY)
@send('put')
def subnet_update(subnet_id, **kwargs):
    url = '/subnets/{}'.format(subnet_id)
    json = {
        'subnet': kwargs,
    }
    return url, {'json': json}


@get_by_name_or_uuid(subnet_list, RESOURCE_LIST_KEY)
@send('delete')
def subnet_delete(subnet_id, **kwargs):
    url = '/subnets/{}'.format(subnet_id)
    return url, {}

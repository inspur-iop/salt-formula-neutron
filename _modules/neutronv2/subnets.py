from neutronv2.common import send
from neutronv2.arg_converter import get_by_name_or_uuid_multiple

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@get_by_name_or_uuid_multiple([('network', 'network_id')])
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


@get_by_name_or_uuid_multiple([('subnet', 'subnet_id')])
@send('get')
def subnet_get_details(subnet_id, **kwargs):
    url = '/subnets/{}'.format(subnet_id)
    return url, {}


@get_by_name_or_uuid_multiple([('subnet', 'subnet_id')])
@send('put')
def subnet_update(subnet_id, **kwargs):
    url = '/subnets/{}'.format(subnet_id)
    json = {
        'subnet': kwargs,
    }
    return url, {'json': json}


@get_by_name_or_uuid_multiple([('subnet', 'subnet_id')])
@send('delete')
def subnet_delete(subnet_id, **kwargs):
    url = '/subnets/{}'.format(subnet_id)
    return url, {}

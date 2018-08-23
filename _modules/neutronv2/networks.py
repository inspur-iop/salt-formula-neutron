from neutronv2.common import send
from neutronv2.arg_converter import get_by_name_or_uuid_multiple

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@get_by_name_or_uuid_multiple([('network', 'network_id')])
@send('get')
def network_get_details(network_id, **kwargs):
    url = '/networks/{}?{}'.format(network_id, urlencode(kwargs))
    return url, {}


@get_by_name_or_uuid_multiple([('network', 'network_id')])
@send('put')
def network_update(network_id, **kwargs):
    url = '/networks/{}'.format(network_id)
    json = {
        'network': kwargs,
    }
    return url, {'json': json}


@get_by_name_or_uuid_multiple([('network', 'network_id')])
@send('delete')
def network_delete(network_id, **kwargs):
    url = '/networks/{}'.format(network_id)
    return url, {}


@send('post')
def network_create(**kwargs):
    url = '/networks'
    json = {
        'network': kwargs,
    }
    return url, {'json': json}


@send('post')
def network_bulk_create(networks, **kwargs):
    url = '/networks'
    json = {
        'networks': networks,
    }
    return url, {'json': json}

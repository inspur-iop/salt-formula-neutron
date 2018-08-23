from neutronv2.common import send
from neutronv2.arg_converter import get_by_name_or_uuid_multiple

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@get_by_name_or_uuid_multiple([('subnetpool', 'subnetpool_id')])
@send('get')
def subnetpool_get_details(subnetpool_id, **kwargs):
    url = '/subnetpools/{}?{}'.format(
        subnetpool_id, urlencode(kwargs)
    )
    return url, {}


@get_by_name_or_uuid_multiple([('subnetpool', 'subnetpool_id')])
@send('put')
def subnetpool_update(subnetpool_id, **kwargs):
    url = '/subnetpools/{}'.format(subnetpool_id)
    json = {
        'subnetpool': kwargs,
    }
    return url, {'json': json}


@get_by_name_or_uuid_multiple([('subnetpool', 'subnetpool_id')])
@send('delete')
def subnetpool_delete(subnetpool_id, **kwargs):
    url = '/subnetpools/{}'.format(subnetpool_id)
    return url, {}


@send('post')
def subnetpool_create(name, prefixes, **kwargs):
    url = '/subnetpools'
    json = {
        'subnetpool': {
            'name': name,
            'prefixes': prefixes,
        }
    }
    json['subnetpool'].update(kwargs)
    return url, {'json': json}

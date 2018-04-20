from neutronv2.common import send, get_by_name_or_uuid
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

RESOURCE_LIST_KEY = 'subnetpools'


@send('get')
def subnetpool_list(**kwargs):
    url = '/subnetpools?{}'.format(urlencode(kwargs))
    return url, {}


@get_by_name_or_uuid(subnetpool_list, RESOURCE_LIST_KEY)
@send('get')
def subnetpool_get_details(subnetpool_id, **kwargs):
    url = '/subnetpools/{}?{}'.format(
        subnetpool_id, urlencode(kwargs)
    )
    return url, {}


@get_by_name_or_uuid(subnetpool_list, RESOURCE_LIST_KEY)
@send('put')
def subnetpool_update(subnetpool_id, **kwargs):
    url = '/subnetpools/{}'.format(subnetpool_id)
    json = {
        'subnetpool': kwargs,
    }
    return url, {'json': json}


@get_by_name_or_uuid(subnetpool_list, RESOURCE_LIST_KEY)
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

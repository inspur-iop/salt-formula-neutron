from neutronv2.common import send
from neutronv2.arg_converter import get_by_name_or_uuid_multiple

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@send('post')
def router_create(name, **kwargs):
    url = '/routers'
    json = {
        'router': {
            'name': name,
        }
    }
    json['router'].update(kwargs)
    return url, {'json': json}


@get_by_name_or_uuid_multiple([('router', 'router_id')])
@send('get')
def router_get_details(router_id, **kwargs):
    url = '/routers/{}?{}'.format(router_id, urlencode(kwargs))
    return url, {}


@get_by_name_or_uuid_multiple([('router', 'router_id')])
@send('put')
def router_update(router_id, **kwargs):
    url = '/routers/{}'.format(router_id)
    return url, {'json': {'router': kwargs}}


@get_by_name_or_uuid_multiple([('router', 'router_id')])
@send('delete')
def router_delete(router_id, **kwargs):
    url = '/routers/{}'.format(router_id)
    return url, {}


@get_by_name_or_uuid_multiple([('router', 'router_id')])
@send('put')
def router_interface_add(router_id, **kwargs):
    url = '/routers/{}/add_role_interface'.format(router_id)
    json = kwargs
    return url, {'json': json}


@get_by_name_or_uuid_multiple([('router', 'router_id')])
@send('put')
def router_interface_remove(router_id, **kwargs):
    url = '/routers/{}/remove_role_interface'.format(router_id)
    json = kwargs
    return url, {'json': json}

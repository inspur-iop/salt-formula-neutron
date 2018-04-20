from neutronv2.common import send

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@send('get')
def auto_alloc_get_details(project_id, **kwargs):
    url = '/auto-allocated-topology/{}?{}'.format(
        project_id, urlencode(kwargs)
    )
    return url, {}


@send('delete')
def auto_alloc_delete(project_id, **kwargs):
    url = '/auto-allocated-topology/{}'.format(project_id)
    return url, {}

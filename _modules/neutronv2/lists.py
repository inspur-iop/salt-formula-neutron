from neutronv2.common import send

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@send('get')
def subnet_list(**kwargs):
    url = '/subnets?{}'.format(urlencode(kwargs))
    return url, {}


@send('get')
def subnetpool_list(**kwargs):
    url = '/subnetpools?{}'.format(urlencode(kwargs))
    return url, {}


@send('get')
def agent_list(**kwargs):
    url = '/agents?{}'.format(urlencode(kwargs))
    return url, {}


@send('get')
def network_list(**kwargs):
    url = '/networks?{}'.format(urlencode(kwargs))
    return url, {}


@send('get')
def router_list(**kwargs):
    url = '/routers?{}'.format(urlencode(kwargs))
    return url, {}

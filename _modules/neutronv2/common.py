import logging
import os_client_config
from uuid import UUID

log = logging.getLogger(__name__)

NEUTRON_VERSION_HEADER = 'x-openstack-networking-version'
ADAPTER_VERSION = '2.0'


class NeutronException(Exception):

    _msg = "Neutron module exception occured."

    def __init__(self, message=None, **kwargs):
        super(NeutronException, self).__init__(message or self._msg)


class NoNeutronEndpoint(NeutronException):
    _msg = "Neutron endpoint not found in keystone catalog."


class NoAuthPluginConfigured(NeutronException):
    _msg = ("You are using keystoneauth auth plugin that does not support "
            "fetching endpoint list from token (noauth or admin_token).")


class NoCredentials(NeutronException):
    _msg = "Please provide cloud name present in clouds.yaml."


class ResourceNotFound(NeutronException):
    _msg = "Uniq resource: {resource} with name: {name} not found."

    def __init__(self, resource, name, **kwargs):
        super(NeutronException, self).__init__(
            self._msg.format(resource=resource, name=name))


class MultipleResourcesFound(NeutronException):
    _msg = "Multiple resource: {resource} with name: {name} found."

    def __init__(self, resource, name, **kwargs):
        super(NeutronException, self).__init__(
            self._msg.format(resource=resource, name=name))


def _get_raw_client(cloud_name):
    service_type = 'network'
    config = os_client_config.OpenStackConfig()
    cloud = config.get_one_cloud(cloud_name)
    adapter = cloud.get_session_client(service_type)
    adapter.version = ADAPTER_VERSION
    try:
        access_info = adapter.session.auth.get_access(adapter.session)
        access_info.service_catalog.get_endpoints()
    except (AttributeError, ValueError):
        e = NoAuthPluginConfigured()
        log.exception('%s' % e)
        raise e
    return adapter


def send(method):
    def wrap(func):
        def wrapped_f(*args, **kwargs):
            cloud_name = kwargs.pop('cloud_name')
            if not cloud_name:
                e = NoCredentials()
                log.error('%s' % e)
                raise e
            adapter = _get_raw_client(cloud_name)
            # Remove salt internal kwargs
            kwarg_keys = list(kwargs.keys())
            for k in kwarg_keys:
                if k.startswith('__'):
                    kwargs.pop(k)
            url, request_kwargs = func(*args, **kwargs)
            if 'microversion' in kwargs:
                request_kwargs['headers'][
                    NEUTRON_VERSION_HEADER] = kwargs['microversion']
            response = getattr(adapter, method)(url, **request_kwargs)
            if not response.content:
                return {}
            try:
                resp = response.json()
            except ValueError:
                resp = response.content
            return resp
        return wrapped_f
    return wrap


def _check_uuid(val):
    try:
        return str(UUID(val)) == val
    except (TypeError, ValueError, AttributeError):
        return False


def get_by_name_or_uuid(resource_list, resp_key,
                        res_id_key='name'):
    def wrap(func):
        def wrapped_f(*args, **kwargs):
            if res_id_key in kwargs:
                ref = kwargs.pop(res_id_key)
                start_arg = 0
            else:
                start_arg = 1
                ref = args[0]
            cloud_name = kwargs['cloud_name']
            if _check_uuid(ref):
                uuid = ref
            else:
                # Then we have name not uuid
                resp = resource_list(
                    name=ref, cloud_name=cloud_name)[resp_key]
                if len(resp) == 0:
                    raise ResourceNotFound(resp_key, ref)
                elif len(resp) > 1:
                    raise MultipleResourcesFound(resp_key, ref)
                uuid = resp[0]['id']
            return func(uuid, *args[start_arg:], **kwargs)
        return wrapped_f
    return wrap

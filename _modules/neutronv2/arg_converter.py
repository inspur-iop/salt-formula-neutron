from neutronv2 import lists
from neutronv2 import common
import functools
import inspect
from uuid import UUID


def _check_uuid(val):
    try:
        return str(UUID(val)) == val
    except (TypeError, ValueError, AttributeError):
        return False


resource_lists = {
    'network': lists.network_list,
    'subnet': lists.subnet_list,
    'subnetpool': lists.subnetpool_list,
    'agent': lists.agent_list,
    'router': lists.router_list,
}


response_keys = {
    'network': 'networks',
    'subnet': 'subnets',
    'subnetpool': 'subnetpools',
    'agent': 'agents',
    'router': 'routers',
}


def get_by_name_or_uuid_multiple(resource_arg_name_pairs):
    def wrap(func):
        @functools.wraps(func)
        def wrapped_f(*args, **kwargs):
            largs = list(args)
            inspect_args = inspect.getargspec(
                func.func_closure[0].cell_contents)
            for (resource, arg_name) in resource_arg_name_pairs:
                arg_index = inspect_args.args.index(arg_name)
                if arg_name in kwargs:
                    ref = kwargs.pop(arg_name, None)
                else:
                    ref = largs.pop(arg_index)
                cloud_name = kwargs['cloud_name']
                if _check_uuid(ref):
                    kwargs[arg_name] = ref
                else:
                    # Then we have name not uuid
                    resp_key = response_keys[resource]
                    resp = resource_lists[resource](
                        name=ref, cloud_name=cloud_name)[resp_key]
                    if len(resp) == 0:
                        raise common.ResourceNotFound(resp_key, ref)
                    elif len(resp) > 1:
                        raise common.MultipleResourcesFound(resp_key, ref)
                    kwargs[arg_name] = resp[0]['id']
            return func(*largs, **kwargs)
        return wrapped_f
    return wrap

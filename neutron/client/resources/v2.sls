{%- from "neutron/map.jinja" import client with context %}
{%- if client.enabled %}

{%- for identity_name, identity in client.get('resources', {}).get('v2', {}).iteritems() %}

  {%- if identity.network is defined %}
  {%- for network_name, network in identity.network.iteritems() %}

neutron_openstack_network_{{ network_name }}:
  neutronv2.network_present:
    - cloud_name: {{ identity_name }}
    - name: {{ network_name }}
    {%- if network.provider_network_type is defined %}
    - provider:network_type: {{ network.provider_network_type }}
    {%- endif %}
    {%- if network.provider_physical_network is defined %}
    - provider:physical_network: {{ network.provider_physical_network }}
    {%- endif %}
    {%- if network.provider_segmentation_id is defined %}
    - provider:segmentation_id: {{ network.provider_segmentation_id }}
    {%- endif %}
    {%- if network.router_external is defined %}
    - router:external: {{ network.router_external }}
    {%- endif %}
    {%- if network.admin_state_up is defined %}
    - admin_state_up: {{ network.admin_state_up }}
    {%- endif %}
    {%- if network.shared is defined %}
    - shared: {{ network.shared }}
    {%- endif %}
    {%- if network.dns_domain is defined %}
    - dns_domain: {{ network.dns_domain }}
    {%- endif %}
    {%- if network.is_default is defined %}
    - is_default: {{ network.is_default }}
    {%- endif %}

    {%- if network.subnet is defined %}
    {%- for subnet_name, subnet in network.subnet.iteritems() %}

neutron_openstack_subnet_{{ subnet_name }}:
  neutronv2.subnet_present:
    - cloud_name: {{ identity_name }}
    - name: {{ subnet_name }}
    - network_id: {{ network_name }}

    {%- if subnet.cidr is defined %}
    - cidr: {{ subnet.cidr  }}
    {%- endif %}
    {%- if subnet.ip_version is defined %}
    - ip_version: {{ subnet.ip_version }}
    {%- endif %}
    {%- if subnet.enable_dhcp is defined %}
    - enable_dhcp: {{ subnet.enable_dhcp }}
    {%- endif %}
    {%- if subnet.allocation_pools is defined %}
    - allocation_pools: {{ subnet.allocation_pools }}
    {%- endif %}
    {%- if subnet.gateway_ip is defined %}
    - gateway_ip: {{ subnet.gateway_ip }}
    {%- endif %}
    {%- if subnet.dns_nameservers is defined %}
    - dns_nameservers: {{ subnet.dns_nameservers }}
    {%- endif %}
    {%- if subnet.host_routes is defined %}
    - host_routes: {{ subnet.host_routes }}
    {%- endif %}
    - require:
      - neutronv2: neutron_openstack_network_{{ network_name }}

    {%- endfor %}
    {%- endif %}

  {%- endfor %}
  {%- endif %}

  {%- if identity.subnetpool is defined %}
  {%- for pool_name, pool in identity.subnetpool.iteritems() %}

neutron_openstack_subnetpool_{{ pool_name }}:
  neutronv2.subnetpool_present:
    - cloud_name: {{ identity_name }}
    - name: {{ pool_name }}
    {%- if pool.default_quota is defined %}
    - default_quota: {{ pool.default_quota }}
    {%- endif %}
    {%- if pool.min_prefixlen is defined %}
    - min_prefixlen: {{ pool.min_prefixlen }}
    {%- endif %}
    {%- if pool.address_scope_id is defined %}
    - address_scope_id: {{ pool.address_scope_id }}
    {%- endif %}
    {%- if pool.default_prefixlen is defined %}
    - default_prefixlen: {{ pool.default_prefixlen }}
    {%- endif %}
    {%- if pool.is_default is defined %}
    - is_default: {{ pool.is_default }}
    {%- endif %}
    {%- if pool.prefixes is defined %}
    - prefixes:
      {%- for prefix in pool.prefixes %}
      - {{ prefix }}
      {%- endfor %}
    {%- endif %}

  {%- endfor %}
  {%- endif %}

{%- endfor %}
{%- endif %}
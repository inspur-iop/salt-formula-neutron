{%- if pillar.neutron.gateway is defined %}
{%- from "neutron/map.jinja" import gateway as neutron with context %}
{%- else %}
{%- from "neutron/map.jinja" import compute as neutron with context %}
{%- endif %}

python-networking-odl:
  pkg.installed

{%- if not grains.get('noservices', False) %}

{%- set ovs_manager = [neutron.opendaylight.ovsdb_odl_iface] %}
{%- do ovs_manager.append(neutron.opendaylight.ovsdb_server_iface) if neutron.opendaylight.ovsdb_server_iface is defined %}

ovs_set_manager:
  cmd.run:
  - name: 'ovs-vsctl set-manager {{ ovs_manager|join(' ') }}'
  - unless: 'ovs-vsctl get-manager | fgrep -qx {{ neutron.opendaylight.ovsdb_odl_iface }}'

{%- if neutron.dpdk|default(False) %}
{%- set ovs_hostconfig = ['--ovs_dpdk --vhostuser_mode=' ~ neutron.vhost_mode|default('server')] %}
{%- do ovs_hostconfig.append('--vhostuser_socket_dir=' ~ neutron.vhost_socket_dir) if neutron.vhost_socket_dir is defined %}
{%- else %}
{%- set ovs_hostconfig = ['--noovs_dpdk'] %}
{%- endif %}

{%- do ovs_hostconfig.append('--local_ip=' ~ neutron.opendaylight.tunnel_ip) if neutron.opendaylight.tunnel_ip is defined %}
{%- do ovs_hostconfig.append('--bridge_mapping=' ~ neutron.opendaylight.provider_mappings) if neutron.opendaylight.provider_mappings is defined %}

neutron_odl_ovs_hostconfig:
  cmd.run:
  - name: 'neutron-odl-ovs-hostconfig {{ ovs_hostconfig|join(' ') }}'
  - require:
    - pkg: python-networking-odl

{%- endif %}

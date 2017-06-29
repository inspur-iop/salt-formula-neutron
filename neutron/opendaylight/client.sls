{%- if pillar.neutron.gateway is defined %}
{%- from "neutron/map.jinja" import gateway as neutron with context %}
{%- else %}
{%- from "neutron/map.jinja" import compute as neutron with context %}
{%- endif %}

python-networking-odl:
  pkg.installed

{%- if not grains.get('noservices', False) %}

ovs_set_manager:
  cmd.run:
  - name: 'ovs-vsctl set-manager {{ neutron.opendaylight.ovsdb_server_iface }} {{ neutron.opendaylight.ovsdb_odl_iface }}'
  - unless: 'ovs-vsctl get-manager | fgrep -x {{ neutron.opendaylight.ovsdb_odl_iface }}'

ovs_set_tunnel_endpoint:
  cmd.run:
  - name: 'ovs-vsctl set Open_vSwitch . other_config:local_ip={{ neutron.opendaylight.tunnel_ip }}'
  - unless: 'ovs-vsctl get Open_vSwitch . other_config | fgrep local_ip="{{ neutron.opendaylight.tunnel_ip }}"'

{%- if neutron.opendaylight.provider_mappings is defined %}
ovs_set_provider_mappings:
  cmd.run:
  - name: 'ovs-vsctl set Open_vSwitch . other_config:provider_mappings={{ neutron.opendaylight.provider_mappings }}'
  - unless: 'ovs-vsctl get Open_vSwitch . other_config | fgrep provider_mappings="{{ neutron.opendaylight.provider_mappings }}"'
{%- endif %}

neutron_odl_ovs_hostconfig:
  cmd.run:
  - name: 'neutron-odl-ovs-hostconfig --noovs_dpdk'
  - require:
    - pkg: python-networking-odl

{%- endif %}

{%- from "neutron/map.jinja" import server with context %}

{%- set should_run = '/bin/false' %}
{%- if not grains.get('noservices') and server.get('role', 'primary') == 'primary' and server.get('bgp_vpn', {}).get('enabled', False) %}
{%- set should_run = '/bin/true' %}
{%- endif %}

bgpvpn_db_manage:
  cmd.run:
  - name: neutron-db-manage --config-file /etc/neutron/neutron.conf --subproject networking-bgpvpn upgrade head
  - onlyif: {{ should_run }}

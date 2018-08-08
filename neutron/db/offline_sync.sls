{%- from "neutron/map.jinja" import server, fwaas with context %}

include:
 - neutron.db.plugins.midonet
 - neutron.db.plugins.service.bgpvpn

{#- TODO(vsaienko): move this to map.jinja or pillars that should be included for specific plugins #}
{%- set config_files = ['/etc/neutron/neutron.conf'] %}
{%- if server.backend.engine in ["ml2", "ovn"] %}
{%- do config_files.append('/etc/neutron/plugins/ml2/ml2_conf.ini') %}
{%- elif server.backend.engine == "midonet" %}
{%- do config_files.append('/etc/neutron/plugins/midonet/midonet.ini') %}
{%- elif server.backend.engine == "vmware" %}
{%- do config_files.append('/etc/neutron/plugins/vmware/nsx.ini') %}
{%- endif %}


neutron_db_manage:
  cmd.run:
  - name: neutron-db-manage --config-file {{ ' --config-file '.join(config_files) }} upgrade head
  {%- if grains.get('noservices') or server.get('role', 'primary') == 'secondary' %}
  - onlyif: /bin/false
  {%- endif %}
  - require_in:
    - sls: neutron.db.plugins.service.bgpvpn
    - sls: neutron.db.plugins.midonet

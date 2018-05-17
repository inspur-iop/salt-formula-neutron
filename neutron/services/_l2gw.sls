{%- from "neutron/map.jinja" import server with context %}
{%- if server.l2gw.get('enabled', False) %}

networking_l2gw_packages:
  pkg.installed:
  - names: {{ server.pkgs_l2gw }}

/etc/neutron/l2gw_plugin.ini:
  file.managed:
  - source: salt://neutron/files/{{ server.version }}/l2gw/l2gw_plugin.ini
  - template: jinja
  - require_in:
    - cmd: neutron_db_manage
  - require:
    - pkg: networking_l2gw_packages
  - watch_in:
    - service: neutron_server_services

{%- endif %}

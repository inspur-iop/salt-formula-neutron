{%- from "neutron/map.jinja" import gateway with context %}
{%- if gateway.l2gw.get('enabled', False) %}

l2gw_agent_packages:
  pkg.installed:
  - names: {{ gateway.pkgs_l2gw_agent }}

/etc/neutron/l2gateway_agent.ini:
  file.managed:
  - source: salt://neutron/files/{{ gateway.version }}/l2gw/l2gateway_agent.ini
  - template: jinja
  - require:
    - pkg: l2gw_agent_packages

neutron-l2gateway-agent:
  service.running:
  - enable: true
  {%- if grains.get('noservices') %}
  - onlyif: /bin/false
  {%- endif %}
  - watch:
    - file: /etc/neutron/l2gateway_agent.ini

{%- endif %}

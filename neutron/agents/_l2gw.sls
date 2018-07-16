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

{%- if not grains.get('noservices', False) %}

{%- if grains.init == 'systemd' %}
{%- if grains['saltversioninfo'] < [2017, 7] %}
service.mask:
  module.run:
  - m_name: neutron-l2gateway-agent
{%- else %}
l2gw_agent__service_mask:
  service.masked:
  - name: neutron-l2gateway-agent
{%- endif %}
  - require_in:
    - pkg: l2gw_agent_packages
{%- endif %}

neutron-l2gateway-agent:
  service.running:
  - enable: true
{%- if grains['saltversioninfo'] >= [2017, 7] %}
  - unmask: true
{%- endif %}
  - watch:
    - file: /etc/neutron/l2gateway_agent.ini
    - file: /etc/neutron/neutron.conf

{%- endif %}
{%- endif %}

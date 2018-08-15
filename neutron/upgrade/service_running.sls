{%- from "neutron/map.jinja" import server,gateway,compute with context %}

neutron_service_running:
  test.show_notification:
    - text: "Running neutron.upgrade.service_running"

{%- set nservices = [] %}

{%- if server.enabled %}
  {%- do nservices.extend(server.services) %}
  {% if server.backend.engine == "contrail" %}
    {%- do nservices.append('neutron-server') %}
  {%- endif %}
{%- endif %}
{%- if gateway.enabled is defined and gateway.enabled%}
  {%- do nservices.extend(gateway.services) %}
{%- endif %}
{%- if compute.enabled is defined and compute.enabled%}
  {%- do nservices.extend(compute.services) %}
  {%- if compute.dvr %}
    {%- do nservices.extend(['neutron-l3-agent', 'neutron-metadata-agent']) %}
  {%- endif %}
  {% if compute.get('dhcp_agent_enabled', False) %}
    {%- do nservices.append('neutron-dhcp-agent') %}
  {%- endif %}
  {% if compute.backend.sriov is defined %}
    {%- do nservices.append('neutron-sriov-agent') %}
  {%- endif %}
{%- endif %}

{%- for nservice in nservices|unique %}
neutron_service_{{ nservice }}_running:
  service.running:
  - enable: True
  - name: {{ nservice }}
{%- endfor %}

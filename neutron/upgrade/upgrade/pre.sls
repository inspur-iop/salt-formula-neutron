{%- from "neutron/map.jinja" import server,gateway with context %}

{%- if gateway.get('enabled') %}
{% set host_id = salt['network.get_hostname']() %}

neutron_agent_disable:
  neutronv2.agents_disabled:
    - name: {{ host_id }}
    - cloud_name: admin_identity

{%- endif %}

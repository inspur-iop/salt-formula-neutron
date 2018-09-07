{%- from "neutron/map.jinja" import upgrade,server,gateway with context %}

{%- if gateway.get('enabled') %}
{% set host_id = salt['network.get_hostname']() %}

neutron_agent_disable:
  neutronv2.agents_disabled:
    - name: {{ host_id }}
    - cloud_name: admin_identity

{%- if upgrade.get('resource_migration').get('l3', {}).get('enabled') %}
migrate_non_ha_l3:
  neutronv2.l3_resources_moved:
    - name: {{ host_id }}
    - cloud_name: admin_identity
{%- endif %}

{%- endif %}

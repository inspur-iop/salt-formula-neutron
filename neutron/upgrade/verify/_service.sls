{%- from "neutron/map.jinja" import server,gateway,compute with context %}

neutron_task_uprade_verify_service:
  test.show_notification:
    - text: "Running neutron.upgrade.verify.service"

{%- if gateway.get('enabled') or compute.get('enabled') %}
  {% set host_id = salt['network.get_hostname']() %}
{%- endif %}

wait_for_neutron_agents:
  module.run:
    - name: neutronv2.wait_for_network_services
    {%- if host_id is defined %}
    - host_id: {{ host_id }}
    {%- endif %}
    - cloud_name: admin_identity

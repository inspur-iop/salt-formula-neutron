{%- from "neutron/map.jinja" import server,gateway with context %}

neutron_post:
  test.show_notification:
    - text: "Running neutron.upgrade.post"

{%- if gateway.get('enabled') %}
keystone_os_client_config_absent:
  file.absent:
    - name: /etc/openstack/clouds.yml
{%- endif %}

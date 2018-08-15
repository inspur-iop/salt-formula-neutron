{%- from "neutron/map.jinja" import server,gateway with context %}

include:
 - neutron.upgrade.verify.api

neutron_pre:
  test.show_notification:
    - text: "Running neutron.upgrade.pre"

{%- if gateway.get('enabled') %}
{# Get os client config from mine #}

{%- set os_content = salt['mine.get']('I@keystone:client:os_client_config:enabled:true', 'keystone_os_client_config', 'compound').values()[0] %}

keystone_os_client_config:
  file.managed:
    - name: /etc/openstack/clouds.yml
    - contents: |
        {{ os_content |yaml(False)|indent(8) }}
    - user: 'root'
    - group: 'root'
    - makedirs: True

{%- endif %}

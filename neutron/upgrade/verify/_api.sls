{%- from "neutron/map.jinja" import server with context %}
{%- from "keystone/map.jinja" import client as kclient with context %}

neutron_upgrade_verify_api:
  test.show_notification:
    - text: "Running neutron.upgrade.verify.api"

{%- if kclient.enabled and kclient.get('os_client_config', {}).get('enabled', False)  %}
  {%- if server.enabled %}
    {%- set neutron_test_network = 'Upgrade_TestNetwork' %}
    {%- set neutron_test_subnet = 'Upgrade_TestSubnet' %}

neutronv2_subnet_list:
  module.run:
    - name: neutronv2.subnet_list
    - kwargs:
        cloud_name: admin_identity

neutronv2_network_list:
  module.run:
    - name: neutronv2.network_list
    - kwargs:
        cloud_name: admin_identity

neutronv2_network_present:
  neutronv2.network_present:
  - cloud_name: admin_identity
  - name: {{ neutron_test_network }}

neutronv2_subnet_present:
  neutronv2.subnet_present:
  - name: {{ neutron_test_subnet }}
  - cloud_name: admin_identity
  - network_id: {{ neutron_test_network }}
  - ip_version: 4
  - cidr: 192.168.89.0/24
  - require:
    - neutronv2_network_present

neutronv2_subnet_absent:
  neutronv2.subnet_absent:
  - cloud_name: admin_identity
  - name: {{ neutron_test_subnet }}
  - require:
    - neutronv2_subnet_present

neutronv2_network_absent:
  neutronv2.network_absent:
  - cloud_name: admin_identity
  - name: {{ neutron_test_network }}
  - require:
    - neutronv2_subnet_absent

  {%- endif %}
{%- endif %}

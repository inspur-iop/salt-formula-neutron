{%- from "neutron/map.jinja" import server,gateway,compute,fwaas with context %}

neutron_render_config:
  test.show_notification:
    - text: "Running neutron.upgrade.render_config"

{%- if server.enabled %}
  {%- set conf_mapping = [['/etc/neutron/neutron.conf', 'salt://neutron/files/' + server.version + '/neutron-server.conf'],
                          ['/etc/neutron/api-paste.ini','salt://neutron/files/' + server.version + '/api-paste.ini']] %}
{%- elif gateway.enabled %}
  {%- set conf_mapping = [['/etc/neutron/neutron.conf', 'salt://neutron/files/' + gateway.version + '/neutron-generic.conf']] %}
{%- elif compute.enabled %}
  {%- set conf_mapping = [['/etc/neutron/neutron.conf', 'salt://neutron/files/' + compute.version + '/neutron-generic.conf']] %}
{%- endif %}

{%- if server.enabled %}
  {% if server.backend.engine == "contrail" %}
    {%- do conf_mapping.append(['/etc/neutron/plugins/opencontrail/ContrailPlugin.ini', "salt://neutron/files/" + server.version + "/ContrailPlugin.ini"]) %}
  {% elif server.backend.engine == "ml2" %}
    {%- do conf_mapping.append(['/etc/neutron/plugins/ml2/ml2_conf.ini', "salt://neutron/files/" + server.version + "/ml2_conf.ini"]) %}
  {%- elif server.backend.engine == "midonet" %}
    {%- do conf_mapping.append(['/etc/neutron/plugins/midonet/midonet.ini', "salt://neutron/files/" + server.version + "/midonet.ini"]) %}
  {% elif server.backend.engine == "vmware" %}
    {%- do conf_mapping.append(['/etc/neutron/plugins/vmware/nsx.ini', "salt://neutron/files/" + server.version + "/plugins/nsx.ini"]) %}
  {%- endif %}
  {%- if fwaas.get('enabled', False) %}
    {%- do conf_mapping.append(['/etc/neutron/fwaas_driver.ini', "salt://neutron/files/" + fwaas.version + "/fwaas_driver.ini"]) %}
  {%- endif %}
  {%- if server.get('l2gw', {}).get('enabled', False) %}
    {%- do conf_mapping.append(['/etc/neutron/l2gw_plugin.ini', "salt://neutron/files/" + server.version + "/l2gw/l2gw_plugin.ini"]) %}
  {%- endif %}
{%- elif gateway.enabled %}
  {%- do conf_mapping.extend([['/etc/neutron/l3_agent.ini', "salt://neutron/files/" + gateway.version + "/l3_agent.ini"],
                             ['/etc/neutron/plugins/ml2/openvswitch_agent.ini', "salt://neutron/files/" + gateway.version + "/openvswitch_agent.ini"],
                             ['/etc/neutron/dhcp_agent.ini', "salt://neutron/files/" + gateway.version + "/dhcp_agent.ini"],
                             ['/etc/neutron/metadata_agent.ini',"salt://neutron/files/" + gateway.version + "/metadata_agent.ini"]]) %}
{%- elif compute.enabled %}
  {% if compute.get('bgp_vpn', {}).get('enabled', False) and server.bgp_vpn.driver == "bagpipe" %}
    {%- do conf_mapping.append(['/etc/bagpipe-bgp/bgp.conf', "salt://neutron/files/" + compute.version + "/bagpipe-bgp.conf"]) %}
  {%- endif %}
  {% if compute.backend.engine == "ml2" %}
    {%- if compute.dvr %}
      {%- do conf_mapping.extend([['/etc/neutron/l3_agent.ini', "salt://neutron/files/" + compute.version + "/l3_agent.ini"],
                                 ['/etc/neutron/metadata_agent.ini',"salt://neutron/files/" + compute.version + "/metadata_agent.ini"]]) %}
    {%- endif %}
    {% if compute.get('dhcp_agent_enabled', False) %}
      {%- do conf_mapping.extend([['/etc/neutron/dhcp_agent.ini', "salt://neutron/files/" + compute.version + "/dhcp_agent.ini"]]) %}
    {%- endif %}
    {% if compute.backend.sriov is defined %}
      {%- do conf_mapping.extend([['/etc/neutron/plugins/ml2/sriov_agent.ini', "salt://neutron/files/" + compute.version + "/sriov_agent.ini"]]) %}
    {%- endif %}
  {%- endif %}
{%- endif %}


{%- for file, source in conf_mapping %}
{{ file }}:
  file.managed:
  - source: {{ source }}
  - template: jinja
{%- endfor %}

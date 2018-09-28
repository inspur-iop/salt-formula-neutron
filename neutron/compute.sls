{% from "neutron/map.jinja" import compute, fwaas with context %}

{%- if compute.enabled %}
include:
  {% if compute.backend.engine == "ml2" and compute.dvr and fwaas.get('enabled', False) %}
- neutron.fwaas
  {%- endif %}
- neutron._ssl.rabbitmq

  {%- if not salt['user.info']('neutron') %}
user_neutron:
  user.present:
  - name: neutron
  - home: /var/lib/neutron
  - shell: /bin/false
  - system: True
  - groups:
    - neutron
  - require_in:
    - sls: neutron._ssl.rabbitmq
    {% if compute.backend.engine == "ml2" and compute.dvr and fwaas.get('enabled', False) %}
    - sls: neutron.fwaas
    {%- endif %}
group_neutron:
  group.present:
    - name: neutron
    - system: True
    - require_in:
      - user: user_neutron
  {%- endif %}

  {% if compute.backend.engine == "ml2" %}

    {% if compute.get('dhcp_agent_enabled', False) %}
neutron_dhcp_agent_packages:
  pkg.installed:
  - names:
    - neutron-dhcp-agent
  - require_in:
    - sls: neutron._ssl.rabbitmq

neutron_dhcp_agent:
  service.running:
    - enable: true
    - names:
      - neutron-dhcp-agent
    - watch:
      - file: /etc/neutron/neutron.conf
      - file: /etc/neutron/dhcp_agent.ini
    - require:
      - pkg: neutron_dhcp_agent_packages

/etc/neutron/dhcp_agent.ini:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/dhcp_agent.ini
  - mode: 0640
  - group: neutron
  - template: jinja
  - require:
    - pkg: neutron_dhcp_agent_packages

    {% endif %}

    {%- if compute.opendaylight is defined %}
      {%- include "neutron/opendaylight/client.sls" %}
    {%- else %}
      {%- include "neutron/ml2_ovs/init.sls" %}
    {%- endif %}

  {%- elif compute.backend.engine == "ovn" %}

ovn_packages:
  pkg.installed:
  - names: {{ compute.pkgs_ovn }}

    {%- if not grains.get('noservices', False) %}

remote_ovsdb_access:
  cmd.run:
  - name: "ovs-vsctl set open .
  external-ids:ovn-remote=tcp:{{ compute.controller_vip }}:6642"

enable_overlays:
  cmd.run:
  - name: "ovs-vsctl set open . external-ids:ovn-encap-type=geneve,vxlan"

configure_local_endpoint:
  cmd.run:
  - name: "ovs-vsctl set open .
  external-ids:ovn-encap-ip={{ compute.local_ip }}"

      {%- if compute.get('external_access', True) %}

set_bridge_external_id:
  cmd.run:
  - name: "ovs-vsctl --no-wait br-set-external-id
   {{ compute.external_bridge }} bridge-id {{ compute.external_bridge }}"

set_bridge_mapping:
  cmd.run:
  - name: "ovs-vsctl set open .
   external-ids:ovn-bridge-mappings=physnet1:{{ compute.external_bridge }}"

      {%- endif %}

ovn_services:
  service.running:
  - names: {{ compute.services_ovn }}
  - enable: true
      {%- if grains.get('noservices') %}
  - onlyif: /bin/false
      {%- endif %}
  - require:
    - pkg: ovn_packages
    - sls: neutron._ssl.rabbitmq

      {%- if compute.metadata is defined %}
        {%- include "neutron/agents/ovn_metadata.sls" %}
      {%- endif %}
    {%- endif %}

  {%- endif %}

{%- endif %}

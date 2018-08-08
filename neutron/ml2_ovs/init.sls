{% from "neutron/map.jinja" import compute, fwaas with context %}
{%- if compute.enabled %}

  {% if compute.backend.engine == "ml2" %}

neutron_compute_packages:
  pkg.installed:
  - names: {{ compute.pkgs }}

    {% if compute.get('bgp_vpn', {}).get('enabled', False) and compute.bgp_vpn.driver == "bagpipe" %}
      {%- include "neutron/services/_bagpipe.sls" %}
    {% endif %}

/etc/neutron/neutron.conf:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/neutron-generic.conf.{{ grains.os_family }}
  - template: jinja
  - require:
    - pkg: neutron_compute_packages

    {% if compute.backend.sriov is defined %}

neutron_sriov_package:
  pkg.installed:
  - name: neutron-sriov-agent

/etc/neutron/plugins/ml2/sriov_agent.ini:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/sriov_agent.ini
  - template: jinja
  - watch_in:
    - service: neutron_compute_services
  - require:
    - pkg: neutron_compute_packages
    - pkg: neutron_sriov_package

neutron_sriov_service:
  service.running:
  - name: neutron-sriov-agent
  - enable: true
      {%- if grains.get('noservices') %}
  - onlyif: /bin/false
      {%- endif %}
  - watch_in:
    - service: neutron_compute_services
  - watch:
    - file: /etc/neutron/neutron.conf
    - file: /etc/neutron/plugins/ml2/openvswitch_agent.ini
    - file: /etc/neutron/plugins/ml2/sriov_agent.ini
      {%- if compute.message_queue.get('ssl',{}).get('enabled', False) %}
    - file: rabbitmq_ca_neutron_compute
      {%- endif %}

    {% endif %}

    {% if compute.dvr %}

      {%- if fwaas.get('enabled', False) %}
include:
- neutron.fwaas
      {%- endif %}

      {%- if not grains.get('noservices', False) and pillar.haproxy is not defined %}
# NOTE(mpolenchuk): haproxy is used as a replacement for
# neutron-ns-metadata-proxy Python implementation starting from Pike
haproxy:
  service.dead:
  - enable: False
  - require:
    - pkg: neutron_dvr_packages
        {%- if compute.get('dhcp_agent_enabled', False) %}
    - pkg: neutron_dhcp_agent_packages
        {%- endif %}
      {%- endif %}

neutron_dvr_packages:
  pkg.installed:
  - names:
    - neutron-l3-agent
    - neutron-metadata-agent

neutron_dvr_agents:
  service.running:
    - enable: true
    - names:
      - neutron-l3-agent
      - neutron-metadata-agent
    - watch:
      - file: /etc/neutron/neutron.conf
      - file: /etc/neutron/l3_agent.ini
      - file: /etc/neutron/metadata_agent.ini
      {%- if fwaas.get('enabled', False) %}
      - file: /etc/neutron/fwaas_driver.ini
      {% endif %}
      {%- if compute.message_queue.get('ssl',{}).get('enabled', False) %}
      - file: rabbitmq_ca_neutron_compute
      {%- endif %}
    - require:
      - pkg: neutron_dvr_packages

/etc/neutron/l3_agent.ini:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/l3_agent.ini
  - template: jinja
  - watch_in:
    - service: neutron_compute_services
  - require:
    - pkg: neutron_dvr_packages

/etc/neutron/metadata_agent.ini:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/metadata_agent.ini
  - template: jinja
  - watch_in:
    - service: neutron_compute_services
  - require:
    - pkg: neutron_dvr_packages

    {% endif %}

/etc/neutron/plugins/ml2/openvswitch_agent.ini:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/openvswitch_agent.ini
  - template: jinja
  - require:
    - pkg: neutron_compute_packages

neutron_compute_services:
  service.running:
  - names: {{ compute.services }}
  - enable: true
  - watch:
    - file: /etc/neutron/neutron.conf
    - file: /etc/neutron/plugins/ml2/openvswitch_agent.ini
    {%- if compute.message_queue.get('ssl',{}).get('enabled', False) %}
    - file: rabbitmq_ca_neutron_compute
    {%- endif %}

    {%- set neutron_compute_services_list = compute.services %}
    {%- if compute.backend.sriov is defined %}
      {%- do neutron_compute_services_list.append('neutron-sriov-agent') %}
    {%- endif %}
    {%- if compute.dvr %}
      {%- do neutron_compute_services_list.extend(['neutron-l3-agent', 'neutron-metadata-agent']) %}
    {%- endif %}
    {%- if compute.get('dhcp_agent_enabled', False) %}
      {%- do neutron_compute_services_list.append('neutron-dhcp-agent') %}
    {%- endif %}

    {%- for service_name in neutron_compute_services_list %}
{{ service_name }}_default:
  file.managed:
    - name: /etc/default/{{ service_name }}
    - source: salt://neutron/files/default
    - template: jinja
    - defaults:
        service_name: {{ service_name }}
        values: {{ compute }}
    - require:
      - pkg: neutron_compute_packages
      {% if compute.backend.sriov is defined %}
      - pkg: neutron_sriov_package
      {% endif %}
      {% if compute.dvr %}
      - pkg: neutron_dvr_packages
      {% endif %}
    - watch_in:
      - service: neutron_compute_services
      {% if compute.backend.sriov is defined %}
      - service: neutron_sriov_service
      {% endif %}
      {% if compute.dvr %}
      - service: neutron_dvr_agents
      {% endif %}
    {% endfor %}

    {%- if compute.logging.log_appender %}

      {%- if compute.logging.log_handlers.get('fluentd', {}).get('enabled', False) %}
neutron_compute_fluentd_logger_package:
  pkg.installed:
    - name: python-fluent-logger
      {%- endif %}

      {% for service_name in neutron_compute_services_list %}
{{ service_name }}_logging_conf:
  file.managed:
    - name: /etc/neutron/logging/logging-{{ service_name }}.conf
    - source: salt://oslo_templates/files/logging/_logging.conf
    - template: jinja
    - makedirs: True
    - user: neutron
    - group: neutron
    - defaults:
        service_name: {{ service_name }}
        _data: {{ compute.logging }}
    - require:
      - pkg: neutron_compute_packages
        {% if compute.backend.sriov is defined %}
      - pkg: neutron_sriov_package
        {% endif %}
        {% if compute.dvr %}
      - pkg: neutron_dvr_packages
        {% endif %}
        {%- if compute.logging.log_handlers.get('fluentd', {}).get('enabled', False) %}
      - pkg: neutron_compute_fluentd_logger_package
        {%- endif %}
    - watch_in:
      - service: neutron_compute_services
        {% if compute.backend.sriov is defined %}
      - service: neutron_sriov_service
        {% endif %}
        {% if compute.dvr %}
      - service: neutron_dvr_agents
        {% endif %}
      {% endfor %}

    {% endif %}

    {%- if compute.message_queue.get('ssl',{}).get('enabled', False) %}
rabbitmq_ca_neutron_compute:
      {%- if compute.message_queue.ssl.cacert is defined %}
  file.managed:
    - name: {{ compute.message_queue.ssl.cacert_file }}
    - contents_pillar: neutron:compute:message_queue:ssl:cacert
    - mode: 0444
    - makedirs: true
      {%- else %}
  file.exists:
   - name: {{ compute.message_queue.ssl.get('cacert_file', compute.cacert_file) }}
      {%- endif %}
    {%- endif %}

  {%- endif %}

{%- endif %}

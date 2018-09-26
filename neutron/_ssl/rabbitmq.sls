{% from "neutron/map.jinja" import server, compute, gateway with context %}

{%- if server.enabled == True %}
  {%- set neutron_msg = server.get('message_queue', {}) %}
  {%- set neutron_cacert = server.cacert_file %}
  {%- set role = 'server' %}
{%- elif compute.enabled == True %}
  {%- set neutron_msg = compute.get('message_queue', {}) %}
  {%- set neutron_cacert = compute.cacert_file %}
  {%- set role = 'compute' %}
{%- elif gateway.enabled == True %}
  {%- set neutron_msg = gateway.get('message_queue', {}) %}
  {%- set neutron_cacert = gateway.cacert_file %}
  {%- set role = 'gateway' %}
{%- endif %}

neutron_{{ role }}_ssl_rabbitmq:
  test.show_notification:
    - text: "Running neutron._ssl.rabbitmq"

{%- if neutron_msg is mapping and neutron_msg.get('x509',{}).get('enabled',False) %}

  {%- set ca_file=neutron_msg.x509.ca_file %}
  {%- set key_file=neutron_msg.x509.key_file %}
  {%- set cert_file=neutron_msg.x509.cert_file %}

rabbitmq_neutron_{{ role }}_ssl_x509_ca:
  {%- if neutron_msg.x509.cacert is defined %}
  file.managed:
    - name: {{ ca_file }}
    - contents_pillar: neutron:{{ role }}:message_queue:x509:cacert
    - mode: 444
    - user: neutron
    - group: neutron
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ ca_file }}
  {%- endif %}

rabbitmq_neutron_{{ role }}_client_ssl_cert:
  {%- if neutron_msg.x509.cert is defined %}
  file.managed:
    - name: {{ cert_file }}
    - contents_pillar: neutron:{{ role }}:message_queue:x509:cert
    - mode: 440
    - user: neutron
    - group: neutron
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ cert_file }}
  {%- endif %}

rabbitmq_neutron_{{ role }}_client_ssl_private_key:
  {%- if neutron_msg.x509.key is defined %}
  file.managed:
    - name: {{ key_file }}
    - contents_pillar: neutron:{{ role }}:message_queue:x509:key
    - mode: 400
    - user: neutron
    - group: neutron
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ key_file }}
  {%- endif %}

rabbitmq_neutron__ssl_x509_set_user_and_group:
  file.managed:
    - names:
      - {{ ca_file }}
      - {{ cert_file }}
      - {{ key_file }}
    - user: neutron
    - group: neutron

  {% elif neutron_msg.get('ssl',{}).get('enabled',False) %}
rabbitmq_ca_neutron_client:
  {%- if neutron_msg.ssl.cacert is defined %}
  file.managed:
    - name: {{ neutron_msg.ssl.cacert_file }}
    - contents_pillar: neutron:{{ role }}:message_queue:ssl:cacert
    - mode: 0444
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ neutron_msg.ssl.get('cacert_file', neutron_cacert) }}
  {%- endif %}

{%- endif %}

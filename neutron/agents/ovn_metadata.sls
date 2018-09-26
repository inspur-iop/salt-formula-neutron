{%- from "neutron/map.jinja" import compute with context %}
{%- if compute.metadata.enabled|default(False) %}

/lib/systemd/system/ovn-metadata-agent.service:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/ovn/metadata-agent.systemd

/etc/neutron/plugins/ovn/metadata-agent.ini:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/ovn/metadata-agent.ini
  - template: jinja
  - mode: 0640
  - group: neutron
  - makedirs: true
  - require:
    - pkg: ovn_packages

/etc/neutron/neutron.conf:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/neutron-generic.conf
  - mode: 0640
  - group: neutron
  - template: jinja
  - require:
    - pkg: ovn_packages

{%- if not grains.get('noservices', False) %}

ovs_set_manager:
  cmd.run:
  - name: 'ovs-vsctl set-manager {{ compute.metadata.ovsdb_server_iface }}'
  - unless: 'ovs-vsctl get-manager | fgrep -qx {{ compute.metadata.ovsdb_server_iface }}'

ovn-metadata-agent:
  service.running:
  - enable: true
  - watch:
    - file: /etc/neutron/plugins/ovn/metadata-agent.ini
    - file: /etc/neutron/neutron.conf

{%- endif %}
{%- endif %}

{%- from "neutron/map.jinja" import compute with context %}

bagpipe_packages:
  pkg.installed:
  - names: {{ compute.pkgs_bagpipe }}

/etc/bagpipe-bgp/bgp.conf:
  file.managed:
  - source: salt://neutron/files/{{ compute.version }}/bagpipe-bgp.conf
  - template: jinja
  - require:
    - pkg: bagpipe_packages

mpls_interface:
  cmd.run:
    - name: "ovs-vsctl --may-exist add-br br-mpls -- set-fail-mode br-mpls secure"
    - unless: "ovs-vsctl show | grep -w br-mpls"

bagpipe-bgp:
  service.running:
  - enable: true
  {%- if grains.get('noservices') %}
  - onlyif: /bin/false
  {%- endif %}
  - require:
    - cmd: mpls_interface
  - watch:
    - file: /etc/bagpipe-bgp/bgp.conf
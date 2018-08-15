{%- from "neutron/map.jinja" import server,client,gateway,compute,fwaas with context %}

neutron_task_pkg_latest:
  test.show_notification:
    - text: "Running neutron.upgrade.pkg_latest"

policy-rc.d_present:
  file.managed:
    - name: /usr/sbin/policy-rc.d
    - mode: 755
    - contents: |
        #!/bin/sh
        exit 101

{%- set npkgs = [] %}
{%- if server.enabled %}
  {%- do npkgs.extend(server.pkgs) %}
  {% if server.backend.engine == "contrail" %}
    {%- do npkgs.append('neutron-plugin-contrail') %}
  {% elif server.backend.engine == "ml2" %}
    {%- do npkgs.extend(server.pkgs_ml2) %}
  {%- elif server.backend.get('opendaylight', False) %}
    {%- do npkgs.append('python-networking-odl') %}
  {%- elif server.backend.engine == "ovn" %}
    {%- do npkgs.extend(server.pkgs_ovn) %}
  {%- elif server.backend.engine == "midonet" %}
    {%- if server.version == "kilo" %}
      {%- do npkgs.extend(['python-neutron-plugin-midonet', 'python-neutron-lbaas']) %}
    {%- else %}
      {%- do npkgs.extend(['python-networking-midonet', 'python-neutron-lbaas', 'python-neutron-fwaas']) %}
    {%- endif %}
  {% elif server.backend.engine == "vmware" %}
    {%- do npkgs.append('python-vmware-nsx') %}
  {%- endif %}
  {% if server.get('bgp_vpn', {}).get('enabled', False) %}
    {%- do npkgs.extend(server.pkgs_bagpipe) %}
  {%- endif %}
  {%- if fwaas.get('enabled', False) %}
    {%- do npkgs.extend(fwaas.pkgs) %}
  {%- endif %}
{%- endif %}
{%- if gateway.enabled is defined and gateway.enabled %}
  {%- do npkgs.extend(gateway.pkgs) %}
{%- endif %}
{%- if compute.enabled is defined and compute.enabled %}
  {%- do npkgs.extend(compute.pkgs) %}
{%- endif %}
{%- if client.enabled is defined and client.enabled %}
  {%- do npkgs.extend(client.pkgs) %}
{%- endif %}

neutron_pkg_latest:
  pkg.latest:
    - names: {{ npkgs|unique }}
    - require:
      - file: policy-rc.d_present
    - require_in:
      - file: policy-rc.d_absent

policy-rc.d_absent:
  file.absent:
    - name: /usr/sbin/policy-rc.d

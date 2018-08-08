{%- from "neutron/map.jinja" import server with context %}

{%- set should_run = '/bin/false' %}
{%- if not grains.get('noservices') and server.get('role', 'primary') == 'primary' and server.backend.engine == "midonet" %}
  {%- set should_run = '/bin/true' %}
{%- endif %}

  {%- if server.version == "kilo" %}

midonet-db-manage:
  cmd.run:
  - name: midonet-db-manage upgrade head
  - onlyif: {{ should_run }}

  {%- else %}

midonet-db-manage:
  cmd.run:
  - name: neutron-db-manage --subproject networking-midonet upgrade head
  - onlyif: {{ should_run }}

  {%- endif %}

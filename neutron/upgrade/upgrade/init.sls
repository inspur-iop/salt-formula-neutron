{%- from "neutron/map.jinja" import server with context %}

neutron_upgrade:
  test.show_notification:
    - text: "Running neutron.upgrade.upgrade"

include:
 - neutron.upgrade.upgrade.pre
 - neutron.upgrade.service_stopped
 - neutron.upgrade.pkgs_latest
 - neutron.upgrade.render_config
{%- if server.get('enabled') %}
 - neutron.db.offline_sync
{%- endif %}
 - neutron.upgrade.service_running
 - neutron.upgrade.upgrade.post

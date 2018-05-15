neutron:
  server:
    enabled: true
    version: queens
    api_workers: 2
    rpc_workers: 2
    rpc_state_report_workers: 2
    backend:
      engine: ovn
      external_mtu: 1500
      mechanism:
        ovn:
          driver: ovn
      tenant_network_types: "geneve,flat"
      ovn:
        ovn_l3_scheduler: chance
        neutron_sync_mode: off
        metadata_enabled: true
    controller_vip: 172.16.10.101
    dvr: false
    l3_ha: false
    dns_domain: novalocal
    global_physnet_mtu: 1500
    bind:
      address: 172.16.10.101
      port: 9696
    compute:
      host: 127.0.0.1
      password: workshop
      region: RegionOne
      tenant: service
      user: nova
    database:
      engine: mysql
      host: 127.0.0.1
      name: neutron
      password: workshop
      port: 3306
      user: neutron
    identity:
      engine: keystone
      host: 127.0.0.1
      password: workshop
      port: 35357
      region: RegionOne
      tenant: service
      user: neutron
      endpoint_type: internal
    message_queue:
      engine: rabbitmq
      host: 127.0.0.1
      password: workshop
      port: 5672
      user: openstack
      virtual_host: /openstack
    ovn_ctl_opts:
      db-nb-create-insecure-remote: 'yes'
      db-sb-create-insecure-remote: 'yes'

linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_queens:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/queens/xenial queens main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/queens/xenial/archive-mcpqueens.key"

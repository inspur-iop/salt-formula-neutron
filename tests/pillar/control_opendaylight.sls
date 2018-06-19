neutron:
  server:
    api_workers: 2
    rpc_workers: 2
    rpc_state_report_workers: 2
    bind:
      address: 172.16.10.101
      port: 9696
    compute:
      host: 127.0.0.1
      password: unsegreto
      region: RegionOne
      tenant: service
      user: nova
    database:
      engine: mysql
      host: 127.0.0.1
      name: neutron
      password: unsegreto
      port: 3306
      user: neutron
    dns_domain: novalocal
    dvr: false
    enabled: true
    global_physnet_mtu: 1500
    identity:
      engine: keystone
      host: 127.0.0.1
      password: unsegreto
      port: 35357
      region: RegionOne
      tenant: service
      user: neutron
      endpoint_type: internal
    l3_ha: False
    message_queue:
      engine: rabbitmq
      host: 127.0.0.1
      password: unsegreto
      port: 5672
      user: openstack
      virtual_host: /openstack
    policy:
      create_subnet: 'rule:admin_or_network_owner'
      'get_network:queue_id': 'rule:admin_only'
      'create_network:shared':
    version: pike
    backend:
      engine: ml2
      external_mtu: 1500
      tenant_network_types: flat,vxlan
      opendaylight: true
      router: odl-router
      host: 127.0.0.1
      rest_api_port: 8282
      user: admin
      password: admin
      ovsdb_connection: tcp:127.0.0.1:6639
      mechanism:
        ovs:
          driver: opendaylight
          order: 77
linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_pike:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/pike/xenial pike main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/pike/xenial/archive-mcppike.key"

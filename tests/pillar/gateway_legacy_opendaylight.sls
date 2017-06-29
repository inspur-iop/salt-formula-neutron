neutron:
  gateway:
    agent_mode: legacy
    backend:
      engine: ml2
      tenant_network_types: "flat,vxlan"
      router: odl-router
      ovsdb_connection: tcp:127.0.0.1:6639
      mechanism:
        ovs:
          driver: opendaylight
    dvr: false
    enabled: true
    external_access: True
    local_ip: 10.1.0.110
    message_queue:
      engine: rabbitmq
      host: 127.0.0.1
      password: unsegreto
      port: 5672
      user: openstack
      virtual_host: /openstack
    metadata:
      host: 127.0.0.1
      password: unsegreto
      workers: 2
    version: pike
    opendaylight:
      ovsdb_server_iface: ptcp:6639:127.0.0.1
      ovsdb_odl_iface: tcp:127.0.0.1:6640
      tunnel_ip: 10.1.0.110
      provider_mappings: physnet1:br-floating
linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_pike:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/pike/xenial pike main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/pike/xenial/archive-mcppike.key"

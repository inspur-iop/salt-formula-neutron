neutron:
  gateway:
    agent_mode: legacy
    backend:
      engine: ml2
      tenant_network_types: "flat,vxlan"
      mechanism:
        ovs:
          driver: openvswitch
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
      password: password
      workers: 2
    version: pike
    l2gw:
      enabled: true
      ovsdb_hosts:
        ovsdbx: 10.164.5.33:6632
linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_pike:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/pike/xenial pike main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/pike/xenial/archive-mcppike.key"

neutron:
  compute:
    enabled: true
    version: queens
    local_ip: 10.2.0.105
    controller_vip: 10.1.0.101
    external_access: false
    backend:
      engine: ovn
      ovn_encap_type: geneve
      ovsdb_connection: tcp:127.0.0.1:6640
    metadata:
      enabled: true
      ovsdb_server_iface: ptcp:6640:127.0.0.1
      host: 10.1.0.101
      password: unsegreto
linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_queens:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/queens/xenial queens main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/queens/xenial/archive-mcpqueens.key"

include:
  - .control_nodvr

neutron:
  server:
    version: pike
    bgp_vpn:
      enabled: true
      driver: bagpipe
linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_pike:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/pike/xenial pike main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/pike/xenial/archive-mcppike.key"
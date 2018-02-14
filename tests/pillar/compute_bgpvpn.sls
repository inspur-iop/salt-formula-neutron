include:
  - .compute_legacy

neutron:
  compute:
    version: pike
    bgp_vpn:
      enabled: true
      driver: bagpipe
    backend:
      extension:
        bagpipe_bgpvpn:
          enabled: True
linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_pike:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/pike/xenial pike main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/pike/xenial/archive-mcppike.key"
include:
  - .compute_legacy

neutron:
  compute:
    version: pike
    bgp_vpn:
      enabled: true
      driver: bagpipe
      bagpipe:
        local_address: 192.168.20.20
        peers: 192.168.20.30
        autonomous_system: 64512
        enable_rtc: True
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
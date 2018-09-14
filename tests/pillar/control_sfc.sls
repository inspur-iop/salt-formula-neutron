include:
  - .control_nodvr

neutron:
  server:
    version: queens
    sfc:
      enabled: true
      sfc_drivers:
        - ovs
      flow_classifier_drivers:
        - ovs

linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_queens:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/queens/xenial queens main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/queens/xenial/archive-mcpqueens.key"

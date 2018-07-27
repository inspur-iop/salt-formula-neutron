neutron:
  gateway:
    agent_mode: legacy
    dhcp_lease_duration: 86400
    firewall_driver: noop
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
      password: workshop
      port: 5672
      user: openstack
      virtual_host: /openstack
    metadata:
      host: 127.0.0.1
      password: password
      workers: 2
    version: mitaka
    agents:
      dhcp:
        ovs_use_veth: True

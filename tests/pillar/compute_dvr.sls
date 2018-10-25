neutron:
  compute:
    base_mac: fa:16:3f:00:00:00
    dvr_base_mac: fa:16:3f:a0:00:00
    agent_mode: dvr
    backend:
      engine: ml2
      tenant_network_types: "flat,vxlan"
      mechanism:
        ovs:
          driver: openvswitch
    dvr: true
    enabled: true
    external_access: true
    local_ip: 10.1.0.105
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
      insecure: true
      proto: https
      workers: 2
    version: pike

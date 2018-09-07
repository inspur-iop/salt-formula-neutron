=====
Usage
=====

Neutron is an OpenStack project to provide *networking as a service* between
interface devices (e.g., vNICs) managed by other Openstack services (e.g.,
nova).

Starting with the Folsom release, Neutron is a core and supported part of the
OpenStack platform (for Essex, we were an *incubated* project, which means use
is suggested only for those who really know what they're doing with Neutron).

Sample Pillars
==============

Neutron Server on the controller node

.. code-block:: yaml

    neutron:
      server:
        enabled: true
        version: mitaka
        allow_pagination: true
        pagination_max_limit: 100
        api_workers: 2
        rpc_workers: 2
        rpc_state_report_workers: 2
        root_helper_daemon: false
        dhcp_lease_duration: 600
        firewall_driver: iptables_hybrid
        bind:
          address: 172.20.0.1
          port: 9696
        database:
          engine: mysql
          host: 127.0.0.1
          port: 3306
          name: neutron
          user: neutron
          password: pwd
        identity:
          engine: keystone
          host: 127.0.0.1
          port: 35357
          user: neutron
          password: pwd
          tenant: service
          endpoint_type: internal
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        metadata:
          host: 127.0.0.1
          port: 8775
          password: pass
          workers: 2
        audit:
          enabled: false

.. note:: The pagination is useful to retrieve a large bunch of resources,
   because a single request may fail (timeout). This is enabled with both
   parameters *allow_pagination* and *pagination_max_limit* as shown above.

Configuration of policy.json file:

.. code-block:: yaml

    neutron:
      server:
        ....
        policy:
          create_subnet: 'rule:admin_or_network_owner'
          'get_network:queue_id': 'rule:admin_only'
          # Add key without value to remove line from policy.json
          'create_network:shared':

Neutron LBaaSv2 enablement
--------------------------

.. code-block:: yaml

  neutron:
    server:
      lbaas:
        enabled: true
        providers:
          octavia:
            engine: octavia
            driver_path: 'neutron_lbaas.drivers.octavia.driver.OctaviaDriver'
            base_url: 'http://127.0.0.1:9876'
          avi_adc:
            engine: avinetworks
            driver_path: 'avi_lbaasv2.avi_driver.AviDriver'
            controller_address: 10.182.129.239
            controller_user: admin
            controller_password: Cloudlab2016
            controller_cloud_name: Default-Cloud
          avi_adc2:
            engine: avinetworks
            ...

.. note:: If the Contrail backend is set, Opencontrail loadbalancer
   would be enabled automatically. In this case lbaas should disabled
   in pillar:

   .. code-block:: yaml

    neutron:
      server:
        lbaas:
          enabled: false

Neutron FWaaSv1 enablement
--------------------------

.. code-block:: yaml

  neutron:
    fwaas:
      enabled: true
      version: ocata
      api_version: v1


Enable CORS parameters
----------------------

.. code-block:: yaml

    neutron:
      server:
        cors:
          allowed_origin: https:localhost.local,http:localhost.local
          expose_headers: X-Auth-Token,X-Openstack-Request-Id,X-Subject-Token
          allow_methods: GET,PUT,POST,DELETE,PATCH
          allow_headers: X-Auth-Token,X-Openstack-Request-Id,X-Subject-Token
          allow_credentials: True
          max_age: 86400

Neutron VXLAN tenant networks with Network nodes
------------------------------------------------

With DVR for East-West and Network node for North-South.

This use case describes a model utilising VxLAN overlay with DVR. The DVR
routers will only be utilized for traffic that is router within the cloud
infrastructure and that remains encapsulated. External traffic will be
routed to via the network nodes.

The intention is that each tenant will require at least two (2) vrouters
one to be utilised

Neutron Server:

.. code-block:: yaml

    neutron:
      server:
        version: mitaka
        path_mtu: 1500
        bind:
          address: 172.20.0.1
          port: 9696
        database:
          engine: mysql
          host: 127.0.0.1
          port: 3306
          name: neutron
          user: neutron
          password: pwd
        identity:
          engine: keystone
          host: 127.0.0.1
          port: 35357
          user: neutron
          password: pwd
          tenant: service
          endpoint_type: internal
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        global_physnet_mtu: 9000
        l3_ha: False # Which type of router will be created by default
        dvr: True # disabled for non DVR use case
        backend:
          engine: ml2
          tenant_network_types: "flat,vxlan"
          external_mtu: 9000
          mechanism:
            ovs:
              driver: openvswitch

Network Node:

.. code-block:: yaml

    neutron:
      gateway:
        enabled: True
        version: mitaka
        dhcp_lease_duration: 600
        firewall_driver: iptables_hybrid
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        local_ip: 192.168.20.20 # br-mesh ip address
        dvr: True # disabled for non DVR use case
        agent_mode: dvr_snat
        metadata:
          host: 127.0.0.1
          password: pass
        backend:
          engine: ml2
          tenant_network_types: "flat,vxlan"
          mechanism:
            ovs:
              driver: openvswitch
        agents:
          dhcp:
            ovs_use_veth: False

Compute Node:

.. code-block:: yaml

    neutron:
      compute:
        enabled: True
        version: mitaka
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        local_ip: 192.168.20.20 # br-mesh ip address
        dvr: True # disabled for non DVR use case
        agent_mode: dvr
        external_access: false # Compute node with DVR for east-west only, Network Node has True as default
        metadata:
          host: 127.0.0.1
          password: pass
        backend:
          engine: ml2
          tenant_network_types: "flat,vxlan"
          mechanism:
            ovs:
              driver: openvswitch
        audit:
          enabled: false


Disable physnet1 bridge
-----------------------

By default we have external access turned on, so among any physnets in
your reclass there would be additional one: physnet1, which is mapped to
br-floating

If you need internal nets only without this bridge, remove br-floating
and configurations mappings. Disable mappings for this bridge on
neutron-servers:

.. code-block:: yaml

    neutron:
      server:
        external_access: false

gateways:

.. code-block:: yaml

    neutron:
      gateway:
        external_access: false

compute nodes:

.. code-block:: yaml

    neutron:
      compute:
        external_access: false


Add additional bridge mappings for OVS bridges
----------------------------------------------

By default we have external access turned on, so among any physnets in
your reclass there would be additional one: physnet1, which is mapped to
br-floating

If you need to add extra non-default bridge mappings they can be defined
separately for both gateways and compute nodes:

gateways:

.. code-block:: yaml

    neutron:
      gateway:
        bridge_mappings:
          physnet4: br-floating-internet

compute nodes:

.. code-block:: yaml

    neutron:
      compute:
        bridge_mappings:
          physnet4: br-floating-internet


Specify different mtu values for different physnets
---------------------------------------------------

Neutron Server:

.. code-block:: yaml

    neutron:
      server:
        version: mitaka
        backend:
          external_mtu: 1500
          tenant_net_mtu: 9000
          ironic_net_mtu: 9000

Neutron VXLAN tenant networks with Network Nodes (non DVR)
----------------------------------------------------------

This section describes a network solution that utilises VxLAN overlay
 networks without DVR with all routers being managed on the network nodes.

Neutron Server:

.. code-block:: yaml

    neutron:
      server:
        version: mitaka
        bind:
          address: 172.20.0.1
          port: 9696
        database:
          engine: mysql
          host: 127.0.0.1
          port: 3306
          name: neutron
          user: neutron
          password: pwd
        identity:
          engine: keystone
          host: 127.0.0.1
          port: 35357
          user: neutron
          password: pwd
          tenant: service
          endpoint_type: internal
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        global_physnet_mtu: 9000
        l3_ha: True
        dvr: False
        backend:
          engine: ml2
          tenant_network_types= "flat,vxlan"
          external_mtu: 9000
          mechanism:
            ovs:
              driver: openvswitch

Network Node:

.. code-block:: yaml

    neutron:
      gateway:
        enabled: True
        version: mitaka
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        local_ip: 192.168.20.20 # br-mesh ip address
        dvr: False
        agent_mode: legacy
        availability_zone: az1
        metadata:
          host: 127.0.0.1
          password: pass
        backend:
          engine: ml2
          tenant_network_types: "flat,vxlan"
          mechanism:
            ovs:
              driver: openvswitch

Compute Node:

.. code-block:: yaml

    neutron:
      compute:
        enabled: True
        version: mitaka
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        local_ip: 192.168.20.20 # br-mesh ip address
        external_access: False
        dvr: False
        backend:
          engine: ml2
          tenant_network_types: "flat,vxlan"
          mechanism:
            ovs:
              driver: openvswitch

Neutron VXLAN tenant networks with Network Nodes with DVR
---------------------------------------------------------

With DVR for East-West and North-South, DVR everywhere, Network
node for SNAT.

This section describes a network solution that utilises VxLAN
overlay networks with DVR with North-South and East-West. Network
Node is used only for SNAT.

Neutron Server:

.. code-block:: yaml

    neutron:
      server:
        version: mitaka
        bind:
          address: 172.20.0.1
          port: 9696
        database:
          engine: mysql
          host: 127.0.0.1
          port: 3306
          name: neutron
          user: neutron
          password: pwd
        identity:
          engine: keystone
          host: 127.0.0.1
          port: 35357
          user: neutron
          password: pwd
          tenant: service
          endpoint_type: internal
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        global_physnet_mtu: 9000
        l3_ha: False
        dvr: True
        backend:
          engine: ml2
          tenant_network_types= "flat,vxlan"
          external_mtu: 9000
          mechanism:
            ovs:
              driver: openvswitch

Network Node:

.. code-block:: yaml

    neutron:
      gateway:
        enabled: True
        version: mitaka
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        local_ip: 192.168.20.20 # br-mesh ip address
        dvr: True
        agent_mode: dvr_snat
        availability_zone: az1
        metadata:
          host: 127.0.0.1
          password: pass
        backend:
          engine: ml2
          tenant_network_types: "flat,vxlan"
          mechanism:
            ovs:
              driver: openvswitch

Compute Node:

.. code-block:: yaml

    neutron:
      compute:
        enabled: True
        version: mitaka
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        local_ip: 192.168.20.20 # br-mesh ip address
        dvr: True
        external_access: True
        agent_mode: dvr
        availability_zone: az1
        metadata:
          host: 127.0.0.1
          password: pass
        backend:
          engine: ml2
          tenant_network_types: "flat,vxlan"
          mechanism:
            ovs:
              driver: openvswitch

Sample Linux network configuration for DVR:

.. code-block:: yaml

    linux:
      network:
        bridge: openvswitch
        interface:
          eth1:
            enabled: true
            type: eth
            mtu: 9000
            proto: manual
          eth2:
            enabled: true
            type: eth
            mtu: 9000
            proto: manual
          eth3:
            enabled: true
            type: eth
            mtu: 9000
            proto: manual
          br-int:
            enabled: true
            mtu: 9000
            type: ovs_bridge
          br-floating:
            enabled: true
            mtu: 9000
            type: ovs_bridge
          float-to-ex:
            enabled: true
            type: ovs_port
            mtu: 65000
            bridge: br-floating
          br-mgmt:
            enabled: true
            type: bridge
            mtu: 9000
            address: ${_param:single_address}
            netmask: 255.255.255.0
            use_interfaces:
            - eth1
          br-mesh:
            enabled: true
            type: bridge
            mtu: 9000
            address: ${_param:tenant_address}
            netmask: 255.255.255.0
            use_interfaces:
            - eth2
          br-ex:
            enabled: true
            type: bridge
            mtu: 9000
            address: ${_param:external_address}
            netmask: 255.255.255.0
            use_interfaces:
            - eth3
            use_ovs_ports:
            - float-to-ex

Additonal VXLAN tenant network settings
---------------------------------------

The default multicast group of ``224.0.0.1`` only multicasts
to a single subnet. Allow overriding it to allow larger underlay
network topologies.

Neutron Server:

.. code-block:: yaml

    neutron:
      server:
        vxlan:
          group: 239.0.0.0/8
          vni_ranges: "2:65535"

Neutron VLAN tenant networks with Network Nodes
-----------------------------------------------

VLAN tenant provider

Neutron Server only:

.. code-block:: yaml

    neutron:
      server:
        version: mitaka
        ...
        global_physnet_mtu: 9000
        l3_ha: False
        dvr: True
        backend:
          engine: ml2
          tenant_network_types: "flat,vlan" # Can be mixed flat,vlan,vxlan
          tenant_vlan_range: "1000:2000"
          external_vlan_range: "100:200" # Does not have to be defined.
          external_mtu: 9000
          mechanism:
            ovs:
              driver: openvswitch

Compute node:

.. code-block:: yaml

    neutron:
      compute:
        version: mitaka
        ...
        dvr: True
        agent_mode: dvr
        external_access: False
        backend:
          engine: ml2
          tenant_network_types: "flat,vlan" # Can be mixed flat,vlan,vxlan
          mechanism:
            ovs:
              driver: openvswitch

Neutron with explicit physical networks
---------------------------------------

Neutron Server only:

.. code-block:: yaml

    neutron:
      server:
        version: ocata
        ...
        backend:
          engine: ml2
          tenant_network_types: "flat,vlan" # Can be mixed flat,vlan,vxlan
          ...
          # also need to configure corresponding bridge_mappings on
          # compute and gateway nodes
          flat_networks_default: '*' # '*' to allow arbitrary names or '' to disable
          physnets: # only listed physnets will be configured (overrides physnet1/2/3)
            external:
              mtu: 1500
              types:
                - flat # possible values - 'flat' or 'vlan'
            sriov_net:
              mtu: 9000 # Optional, defaults to 1500
              vlan_range: '100:200' # Optional
              types:
                - vlan
            ext_net2:
              mtu: 1500
              types:
                - flat
                - vlan
          mechanism:
            ovs:
              driver: openvswitch

Advanced Neutron Features (DPDK, SR-IOV)
----------------------------------------

Neutron OVS DPDK

Enable datapath netdev for neutron openvswitch agent:

.. code-block:: yaml

    neutron:
      server:
        version: mitaka
        ...
        dpdk: True
        ...

    neutron:
      compute:
        version: mitaka
        dpdk: True
        vhost_mode: client # options: client|server (default)
        vhost_socket_dir: /var/run/openvswitch
        backend:
          engine: ml2
          ...
          mechanism:
            ovs:
              driver: openvswitch

Neutron OVS SR-IOV:

.. code-block:: yaml

    neutron:
      server:
        version: mitaka
        backend:
          engine: ml2
          ...
          mechanism:
            ovs:
              driver: openvswitch
            sriov:
              driver: sriovnicswitch
              # Driver w/ highest number will be placed ahead in the list (default is 0).
              # It's recommended for SR-IOV driver to set an order >0 to get it
              # before (for example) the opendaylight one.
              order: 9

    neutron:
      compute:
        version: mitaka
        ...
        backend:
          engine: ml2
          tenant_network_types: "flat,vlan" # Can be mixed flat,vlan,vxlan
          sriov:
            nic_one:
              devname: eth1
              physical_network: physnet3
          mechanism:
            ovs:
              driver: openvswitch

Neutron with VLAN-aware-VMs
---------------------------

.. code-block:: yaml

    neutron:
      server:
        vlan_aware_vms: true
      ....
      compute:
        vlan_aware_vms: true
      ....
      gateway:
        vlan_aware_vms: true

Neutron with BGP VPN (BaGPipe driver)
-------------------------------------

.. code-block:: yaml

    neutron:
      server:
        version: pike
        bgp_vpn:
          enabled: true
          driver: bagpipe # Options: bagpipe/opencontrail/opendaylight[_v2]
      ....
      compute:
        version: pike
        bgp_vpn:
          enabled: true
          driver: bagpipe # Options: bagpipe/opencontrail/opendaylight[_v2]
          bagpipe:
            local_address: 192.168.20.20 # IP address for mpls/gre tunnels
            peers: 192.168.20.30 # IP addresses of BGP peers
            autonomous_system: 64512 # Autonomous System number
            enable_rtc: True # Enable RT Constraint (RFC4684)
        backend:
          ovs_extension: # for OVS agent only, not supported in SRIOV agent
            bagpipe_bgpvpn:
              enabled: True

Neutron with DHCP agent on compute node
---------------------------------------

.. code-block:: yaml

    neutron:
      ....
      compute:
        dhcp_agent_enabled: true
      ....

Neutron with OVN
----------------

Control node:

.. code-block:: yaml

    neutron:
      server:
        backend:
          engine: ovn
          mechanism:
            ovn:
              driver: ovn
          tenant_network_types: "geneve,flat"
          ovn:
            ovn_l3_scheduler: leastloaded # valid options: chance, leastloaded
            neutron_sync_mode: repair # valid options: log, off, repair
        ovn_ctl_opts:
          db-nb-create-insecure-remote: 'yes'
          db-sb-create-insecure-remote: 'yes'

Compute node:

.. code-block:: yaml

    neutron:
      compute:
        local_ip: 10.2.0.105
        controller_vip: 10.1.0.101
        external_access: false
        backend:
          engine: ovn

Neutron L2 Gateway
----------------

Control node:

.. code-block:: yaml

    neutron:
      server:
        version: pike
        l2gw:
          enabled: true
          periodic_monitoring_interval: 5
          quota_l2_gateway: 20
          # service_provider=<service_type>:<name>:<driver>[:default]
          service_provider: L2GW:OpenDaylight:networking_odl.l2gateway.driver.OpenDaylightL2gwDriver:default
        backend:
          engine: ml2

Network/Gateway node:

.. code-block:: yaml

    neutron:
      gateway:
        version: pike
        l2gw:
          enabled: true
          debug: true
          socket_timeout: 20
          ovsdb_hosts:
            # <ovsdb_name>: <ip address>:<port>
            # - ovsdb_name: a user defined symbolic identifier of physical switch
            # - ip address: the address or dns name for the OVSDB server (i.e. pointer to the switch)
            ovsdb1: 10.164.5.33:6632
            ovsdb2: 10.164.4.33:6632


OpenDaylight integration
------------------------

Control node:

.. code-block:: yaml

  neutron:
    server:
      backend:
        opendaylight: true
        router: odl-router_v2
        host: 10.20.0.77
        rest_api_port: 8282
        user: admin
        password: admin
        ovsdb_connection: tcp:127.0.0.1:6639
        ovsdb_interface: native
        enable_websocket: true
        enable_dhcp_service: false
        mechanism:
          ovs:
            driver: opendaylight_v2
            order: 1

Network/Gateway node:

.. code-block:: yaml

  neutron:
    gateway:
      backend:
        router: odl-router_v2
        ovsdb_connection: tcp:127.0.0.1:6639
        ovsdb_interface: native
      opendaylight:
        ovsdb_server_iface: ptcp:6639:127.0.0.1
        ovsdb_odl_iface: tcp:10.20.0.77:6640
        tunnel_ip: 10.1.0.110
        provider_mappings: physnet1:br-floating

Compute node:

.. code-block:: yaml

  neutron:
    compute:
      opendaylight:
        ovsdb_server_iface: ptcp:6639:127.0.0.1
        ovsdb_odl_iface: tcp:10.20.0.77:6640
        tunnel_ip: 10.1.0.105
        provider_mappings: physnet1:br-floating


Neutron Server
--------------

Neutron Server with OpenContrail:

.. code-block:: yaml

    neutron:
      server:
        backend:
          engine: contrail
          host: contrail_discovery_host
          port: 8082
          user: admin
          password: password
          tenant: admin
          token: token

Neutron Server with Midonet:

.. code-block:: yaml

    neutron:
      server:
        backend:
          engine: midonet
          host: midonet_api_host
          port: 8181
          user: admin
          password: password

Neutron Server with NSX:

.. code-block:: yaml

    neutron:
      server:
        backend:
          engine: vmware
        core_plugin: vmware_nsxv3
        vmware:
          nsx:
            extension_drivers:
              - vmware_nsxv3_dns
            v3:
              api_password: nsx_password
              api_user: nsx_username
              api_managers:
                01:
                  scheme: https
                  host: 192.168.10.120
                  port: '443'
              insecure: true

Neutron Keystone region:

.. code-block:: yaml

    neutron:
      server:
        enabled: true
        version: kilo
        ...
        identity:
          region: RegionTwo
        ...
        compute:
          region: RegionTwo
        ...

Client-side RabbitMQ HA setup:

.. code-block:: yaml

    neutron:
      server:
        ....
        message_queue:
          engine: rabbitmq
          members:
            - host: 10.0.16.1
            - host: 10.0.16.2
            - host: 10.0.16.3
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        ....

Configuring TLS communications
------------------------------

.. note:: By default, system-wide installed CA certs are used,
   so ``cacert_file`` param is optional, as well as ``cacert``.

- **RabbitMQ TLS**

  .. code-block:: yaml

   neutron:
     server, gateway, compute:
        message_queue:
          port: 5671
          ssl:
            enabled: True
            (optional) cacert: cert body if the cacert_file does not exists
            (optional) cacert_file: /etc/openstack/rabbitmq-ca.pem
            (optional) version: TLSv1_2

- **MySQL TLS**

  .. code-block:: yaml

     neutron:
       server:
          database:
            ssl:
              enabled: True
              (optional) cacert: cert body if the cacert_file does not exists
              (optional) cacert_file: /etc/openstack/mysql-ca.pem

- **Openstack HTTPS API**

  .. code-block:: yaml

     neutron:
       server:
          identity:
             protocol: https
             (optional) cacert_file: /etc/openstack/proxy.pem

Enable auditing filter, ie: CADF:

.. code-block:: yaml

    neutron:
      server:
        audit:
          enabled: true
      ....
          filter_factory: 'keystonemiddleware.audit:filter_factory'
          map_file: '/etc/pycadf/neutron_api_audit_map.conf'
      ....
      compute:
        audit:
          enabled: true
      ....
          filter_factory: 'keystonemiddleware.audit:filter_factory'
          map_file: '/etc/pycadf/neutron_api_audit_map.conf'
      ....

Neutron with security groups disabled:

.. code-block:: yaml

    neutron:
      server:
        security_groups_enabled: False
      ....
      compute:
        security_groups_enabled: False
      ....
      gateway:
        security_groups_enabled: False


Neutron Client
--------------

Neutron networks:

.. code-block:: yaml

    neutron:
      client:
        enabled: true
        server:
          identity:
            endpoint_type: internalURL
            network:
              inet1:
                tenant: demo
                shared: False
                admin_state_up: True
                router_external: True
                provider_physical_network: inet
                provider_network_type: flat
                provider_segmentation_id: 2
                subnet:
                  inet1-subnet1:
                    cidr: 192.168.90.0/24
                    enable_dhcp: False
              inet2:
                tenant: admin
                shared: False
                router_external: True
                provider_network_type: "vlan"
                subnet:
                  inet2-subnet1:
                    cidr: 192.168.92.0/24
                    enable_dhcp: False
                  inet2-subnet2:
                    cidr: 192.168.94.0/24
                    enable_dhcp: True
          identity1:
            network:
              ...

Neutron routers:

.. code-block:: yaml

    neutron:
      client:
        enabled: true
        server:
          identity:
            endpoint_type: internalURL
            router:
              inet1-router:
                tenant: demo
                admin_state_up: True
                gateway_network: inet
                interfaces:
                  - inet1-subnet1
                  - inet1-subnet2
          identity1:
            router:
              ...

.. TODO implement adding new interfaces to a router while updating it

Neutron security groups:

.. code-block:: yaml

    neutron:
      client:
        enabled: true
        server:
          identity:
            endpoint_type: internalURL
            security_group:
              security_group1:
                tenant: demo
                description: security group 1
                rules:
                  - direction: ingress
                    ethertype: IPv4
                    protocol: TCP
                    port_range_min: 1
                    port_range_max: 65535
                    remote_ip_prefix: 0.0.0.0/0
                  - direction: ingress
                    ethertype: IPv4
                    protocol: UDP
                    port_range_min: 1
                    port_range_max: 65535
                    remote_ip_prefix: 0.0.0.0/0
                  - direction: ingress
                    protocol: ICMP
                    remote_ip_prefix: 0.0.0.0/0
          identity1:
            security_group:
              ...

.. TODO: implement updating existing security rules (now it adds new rule if
   trying to update existing one)

Floating IP addresses:

.. code-block:: yaml

    neutron:
      client:
        enabled: true
        server:
          identity:
            endpoint_type: internalURL
            floating_ip:
              prx01-instance:
                server: prx01.mk22-lab-basic.local
                subnet: private-subnet1
                network: public-net1
                tenant: demo
              gtw01-instance:
                ...

.. note:: The network must have flag router:external set to True.
          Instance port in the stated subnet will be associated
          with the dynamically generated floating IP.

Enable Neutron extensions (QoS, DNS, etc.)
------------------------------------------

.. code-block:: yaml

    neutron:
      server:
        backend:
          extension:
            dns:
              enabled: True
              host: 127.0.0.1
              port: 9001
              protocol: http
              ....
            qos
              enabled: True

Different Neutron extensions for different agents
-------------------------------------------------

.. code-block:: yaml

    neutron:
      server:
        backend:
          extension: # common extensions for OVS and SRIOV agents
            dns:
              enabled: True
              ...
            qos
              enabled: True
          ovs_extension: # OVS specific extensions
            bagpipe_bgpvpn:
              enabled: True
          sriov_extension: # SRIOV specific extensions
            dummy:
              enabled: True

Neutron with Designate
-----------------------------------------

.. code-block:: yaml

    neutron:
      server:
        backend:
          extension:
            dns:
              enabled: True
              host: 127.0.0.1
              port: 9001
              protocol: http

Enable RBAC for OpenContrail engine
-----------------------------------

.. code-block:: yaml

    neutron:
      server:
        backend:
          engine: contrail
          rbac:
            enabled: True

Enhanced logging with logging.conf
----------------------------------

By default ``logging.conf`` is disabled.

That is possible to enable per-binary logging.conf with new variables:

* ``openstack_log_appender``
   Set to true to enable ``log_config_append`` for all OpenStack services

* ``openstack_fluentd_handler_enabled``
   Set to true to enable FluentHandler for all Openstack services

* ``openstack_ossyslog_handler_enabled``
   Set to true to enable OSSysLogHandler for all Openstack services.

Only ``WatchedFileHandler``, ``OSSysLogHandler``, and ``FluentHandler``
are available.

Also it is possible to configure this with pillar:

.. code-block:: yaml

  neutron:
    server:
      logging:
        log_appender: true
        log_handlers:
          watchedfile:
            enabled: true
          fluentd:
            enabled: true
          ossyslog:
            enabled: true
    ....
    compute:
      logging:
        log_appender: true
        log_handlers:
          watchedfile:
            enabled: true
          fluentd:
            enabled: true
          ossyslog:
            enabled: true
    ....
    gateway:
      logging:
        log_appender: true
        log_handlers:
          watchedfile:
            enabled: true
          fluentd:
            enabled: true
          ossyslog:
            enabled: true

Logging levels pillar example:

.. code-block:: yaml

  neutron:
    server:
      logging:
        log_appender: true
        loggers:
          root:
            level: 'DEBUG'
          neutron:
            level: 'DEBUG'
          amqplib:
            level: 'DEBUG'
          sqlalchemy:
            level: 'DEBUG'
          boto:
            level: 'DEBUG'
          suds:
            level: 'DEBUG'
          eventletwsgi:
            level: 'DEBUG'
    ......

Upgrades
========

Each openstack formula provide set of phases (logical bloks) that will help to
build flexible upgrade orchestration logic for particular components. The list
of phases might and theirs descriptions are listed in table below:

+-------------------------------+------------------------------------------------------+
| State                         | Description                                          |
+===============================+======================================================+
| <app>.upgrade.service_running | Ensure that all services for particular application  |
|                               | are enabled for autostart and running                |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.service_stopped | Ensure that all services for particular application  |
|                               | disabled for autostart and dead                      |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.pkg_latest      | Ensure that packages used by particular application  |
|                               | are installed to latest available version.           |
|                               | This will not upgrade data plane packages like qemu  |
|                               | and openvswitch as usually minimal required version  |
|                               | in openstack services is really old. The data plane  |
|                               | packages should be upgraded separately by `apt-get   |
|                               | upgrade` or `apt-get dist-upgrade`                   |
|                               | Applying this state will not autostart service.      |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.render_config   | Ensure configuration is rendered actual version.     +
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.pre             | We assume this state is applied on all nodes in the  |
|                               | cloud before running upgrade.                        |
|                               | Only non destructive actions will be applied during  |
|                               | this phase. Perform service built in service check   |
|                               | like (keystone-manage doctor and nova-status upgrade)|
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.upgrade.pre     | Mostly applicable for data plane nodes. During this  |
|                               | phase resources will be gracefully removed from      |
|                               | current node if it is allowed. Services for upgraded |
|                               | application will be set to admin disabled state to   |
|                               | make sure node will not participate in resources     |
|                               | scheduling. For example on gtw nodes this will set   |
|                               | all agents to admin disable state and will move all  |
|                               | routers to other agents.                             |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.upgrade         | This state will basically upgrade application on     |
|                               | particular target. Stop services, render             |
|                               | configuration, install new packages, run offline     |
|                               | dbsync (for ctl), start services. Data plane should  |
|                               | not be affected, only OpenStack python services.     |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.upgrade.post    | Add services back to scheduling.                     |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.post            | This phase should be launched only when upgrade of   |
|                               | the cloud is completed.                              |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.verify          | Here we will do basic health checks (API CRUD        |
|                               | operations, verify do not have dead network          |
|                               | agents/compute services)                             |
+-------------------------------+------------------------------------------------------+


Documentation and Bugs
======================

* http://salt-formulas.readthedocs.io/
   Learn how to install and update salt-formulas

* https://github.com/salt-formulas/salt-formula-neutron/issues
   In the unfortunate event that bugs are discovered, report the issue to the
   appropriate issue tracker. Use the Github issue tracker for a specific salt
   formula

* https://launchpad.net/salt-formulas
   For feature requests, bug reports, or blueprints affecting the entire
   ecosystem, use the Launchpad salt-formulas project

* https://launchpad.net/~salt-formulas-users
   Join the salt-formulas-users team and subscribe to mailing list if required

* https://github.com/salt-formulas/salt-formula-neutron
   Develop the salt-formulas projects in the master branch and then submit pull
   requests against a specific formula

* #salt-formulas @ irc.freenode.net
   Use this IRC channel in case of any questions or feedback which is always
   welcome


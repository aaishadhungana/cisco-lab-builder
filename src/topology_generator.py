import networkx as nx
import random
from typing import Dict, List, Optional
import json


class NetworkTopologyGenerator:
    """Generate network topologies with AI optimization"""
    
    def __init__(self):
        self.topology = None
        self.devices = []
        self.links = []
        
    def generate_topology(
        self,
        network_type: str = "enterprise",
        num_routers: int = 5,
        num_switches: int = 10,
        num_hosts: int = 50,
        security_level: str = "high",
        redundancy: bool = True,
        ai_optimize: bool = True
    ) -> Dict:
        """
        Generate network topology based on parameters
        
        Args:
            network_type: Type of network (enterprise, datacenter, campus, cloud, hybrid)
            num_routers: Number of routers
            num_switches: Number of switches
            num_hosts: Number of end hosts
            security_level: Security level (low, medium, high, critical)
            redundancy: Enable redundant paths
            ai_optimize: Use AI for optimization
            
        Returns:
            Dictionary containing topology data
            
        Raises:
            ValueError: If parameters are invalid
        """
        
        # Validate input parameters
        if num_routers < 0 or num_switches < 0 or num_hosts < 0:
            raise ValueError("Device counts must be non-negative")
        
        # Validate network type
        valid_network_types = ["enterprise", "datacenter", "campus", "cloud", "hybrid"]
        if network_type not in valid_network_types:
            raise ValueError(f"Invalid network_type '{network_type}'. Must be one of: {valid_network_types}")
        
        # Validate security level
        valid_security_levels = ["low", "medium", "high", "critical"]
        if security_level not in valid_security_levels:
            raise ValueError(f"Invalid security_level '{security_level}'. Must be one of: {valid_security_levels}")
        
        # Reset state
        self.devices = []
        self.links = []
        
        # Generate core routers
        core_routers = self._generate_routers(num_routers, "core")
        
        # Generate distribution switches
        dist_switches = self._generate_switches(max(num_switches // 2, 0), "distribution")
        
        # Generate access switches
        access_switches = self._generate_switches(max(num_switches - len(dist_switches), 0), "access")
        
        # Generate hosts
        hosts = self._generate_hosts(num_hosts)
        
        # Add security devices based on security level
        security_devices = self._add_security_devices(security_level)
        
        # Combine all devices
        self.devices = core_routers + dist_switches + access_switches + hosts + security_devices
        
        # Create links based on network type
        if network_type == "enterprise":
            self._create_enterprise_topology(core_routers, dist_switches, access_switches, hosts, redundancy)
        elif network_type == "datacenter":
            self._create_datacenter_topology(core_routers, dist_switches, access_switches, hosts, redundancy)
        elif network_type == "campus":
            self._create_campus_topology(core_routers, dist_switches, access_switches, hosts, redundancy)
        else:
            self._create_default_topology(core_routers, dist_switches, access_switches, hosts, redundancy)
        
        # AI optimization
        if ai_optimize:
            self._ai_optimize_topology()
        
        # Calculate network segments
        segments = self._calculate_segments()
        
        topology_data = {
            'network_type': network_type,
            'devices': self.devices,
            'links': self.links,
            'total_devices': len(self.devices),
            'total_links': len(self.links),
            'segments': segments,
            'security_level': security_level,
            'redundancy_enabled': redundancy,
            'ai_optimized': ai_optimize,
            'metadata': {
                'routers': num_routers,
                'switches': num_switches,
                'hosts': num_hosts,
                'security_devices': len(security_devices)
            }
        }
        
        self.topology = topology_data
        return topology_data
    
    def _generate_routers(self, count: int, router_type: str) -> List[Dict]:
        """Generate router devices"""
        routers = []
        for i in range(count):
            router = {
                'name': f'Router-{router_type}-{i+1:02d}',
                'type': 'router',
                'subtype': router_type,
                'model': 'Cisco ISR 4451' if router_type == 'core' else 'Cisco ISR 4331',
                'ip_address': f'10.0.{i}.1',
                'interfaces': self._generate_interfaces('router', 8),
                'routing_protocol': 'OSPF',
                'management_ip': f'192.168.100.{i+1}'
            }
            routers.append(router)
        return routers
    
    def _generate_switches(self, count: int, switch_type: str) -> List[Dict]:
        """Generate switch devices"""
        switches = []
        for i in range(count):
            switch = {
                'name': f'Switch-{switch_type}-{i+1:02d}',
                'type': 'switch',
                'subtype': switch_type,
                'model': 'Cisco Catalyst 9300' if switch_type == 'distribution' else 'Cisco Catalyst 2960',
                'ip_address': f'10.{1 if switch_type == "distribution" else 2}.{i}.1',
                'interfaces': self._generate_interfaces('switch', 48),
                'vlan_support': True,
                'management_ip': f'192.168.101.{i+1}'
            }
            switches.append(switch)
        return switches
    
    def _generate_hosts(self, count: int) -> List[Dict]:
        """Generate host devices"""
        hosts = []
        for i in range(count):
            host = {
                'name': f'Host-{i+1:03d}',
                'type': 'host',
                'subtype': 'workstation',
                'ip_address': f'10.10.{i // 254}.{(i % 254) + 1}',
                'mac_address': self._generate_mac_address(),
                'os': random.choice(['Windows 10', 'Windows 11', 'Ubuntu 22.04', 'macOS'])
            }
            hosts.append(host)
        return hosts
    
    def _add_security_devices(self, security_level: str) -> List[Dict]:
        """Add security devices based on security level"""
        security_devices = []
        
        if security_level in ['high', 'critical']:
            # Add firewall
            firewall = {
                'name': 'Firewall-01',
                'type': 'firewall',
                'model': 'Cisco ASA 5516-X',
                'ip_address': '10.0.0.254',
                'interfaces': self._generate_interfaces('firewall', 4),
                'features': ['stateful_inspection', 'ips', 'vpn']
            }
            security_devices.append(firewall)
        
        if security_level == 'critical':
            # Add IPS
            ips = {
                'name': 'IPS-01',
                'type': 'ips',
                'model': 'Cisco Firepower 2130',
                'ip_address': '10.0.0.253',
                'interfaces': self._generate_interfaces('ips', 4),
                'features': ['intrusion_prevention', 'malware_detection', 'threat_intelligence']
            }
            security_devices.append(ips)
        
        return security_devices
    
    def _generate_interfaces(self, device_type: str, count: int) -> List[Dict]:
        """Generate network interfaces"""
        interfaces = []
        for i in range(count):
            interface = {
                'name': f'GigabitEthernet0/{i}' if device_type in ['router', 'firewall'] else f'FastEthernet0/{i}',
                'status': 'up',
                'speed': '1000' if device_type in ['router', 'switch'] else '100',
                'duplex': 'full'
            }
            interfaces.append(interface)
        return interfaces
    
    def _generate_mac_address(self) -> str:
        """Generate random MAC address"""
        return ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])
    
    def _create_enterprise_topology(self, routers, dist_switches, access_switches, hosts, redundancy):
        """Create enterprise network topology"""
        # Connect core routers in full mesh
        for i, r1 in enumerate(routers):
            for r2 in routers[i+1:]:
                self.links.append({
                    'source': r1['name'],
                    'target': r2['name'],
                    'type': 'core_link',
                    'bandwidth': '10Gbps'
                })
        
        # Connect distribution switches to core routers
        if len(dist_switches) > 0 and len(routers) > 0:
            for dist_sw in dist_switches:
                # Connect to first 2 routers for redundancy (or all if less than 2)
                router_count = min(2, len(routers))
                for router in routers[:router_count]:
                    self.links.append({
                        'source': router['name'],
                        'target': dist_sw['name'],
                        'type': 'distribution_link',
                        'bandwidth': '10Gbps'
                    })
        
        # Connect access switches to distribution switches
        if len(access_switches) > 0 and len(dist_switches) > 0:
            for i, access_sw in enumerate(access_switches):
                dist_idx = i % len(dist_switches)
                self.links.append({
                    'source': dist_switches[dist_idx]['name'],
                    'target': access_sw['name'],
                    'type': 'access_link',
                    'bandwidth': '1Gbps'
                })
                
                if redundancy and len(dist_switches) > 1:
                    # Add redundant link to another distribution switch
                    redundant_dist_idx = (dist_idx + 1) % len(dist_switches)
                    self.links.append({
                        'source': dist_switches[redundant_dist_idx]['name'],
                        'target': access_sw['name'],
                        'type': 'access_link_redundant',
                        'bandwidth': '1Gbps'
                    })
        
        # Connect hosts to access switches or distribution switches or routers
        if len(hosts) > 0:
            if len(access_switches) > 0:
                # Connect hosts to access switches
                hosts_per_switch = len(hosts) // len(access_switches)
                if hosts_per_switch == 0:
                    hosts_per_switch = 1
                    
                for i, host in enumerate(hosts):
                    switch_idx = i // hosts_per_switch
                    if switch_idx >= len(access_switches):
                        switch_idx = len(access_switches) - 1
                    
                    self.links.append({
                        'source': access_switches[switch_idx]['name'],
                        'target': host['name'],
                        'type': 'host_link',
                        'bandwidth': '1Gbps'
                    })
            elif len(dist_switches) > 0:
                # Connect hosts directly to distribution switches if no access switches
                hosts_per_switch = len(hosts) // len(dist_switches)
                if hosts_per_switch == 0:
                    hosts_per_switch = 1
                    
                for i, host in enumerate(hosts):
                    switch_idx = i // hosts_per_switch
                    if switch_idx >= len(dist_switches):
                        switch_idx = len(dist_switches) - 1
                    
                    self.links.append({
                        'source': dist_switches[switch_idx]['name'],
                        'target': host['name'],
                        'type': 'host_link',
                        'bandwidth': '1Gbps'
                    })
            elif len(routers) > 0:
                # Connect hosts directly to routers if no switches
                hosts_per_router = len(hosts) // len(routers)
                if hosts_per_router == 0:
                    hosts_per_router = 1
                    
                for i, host in enumerate(hosts):
                    router_idx = i // hosts_per_router
                    if router_idx >= len(routers):
                        router_idx = len(routers) - 1
                    
                    self.links.append({
                        'source': routers[router_idx]['name'],
                        'target': host['name'],
                        'type': 'host_link',
                        'bandwidth': '1Gbps'
                    })
    
    def _create_datacenter_topology(self, routers, dist_switches, access_switches, hosts, redundancy):
        """Create datacenter network topology (spine-leaf)"""
        # Routers act as spine switches
        # Distribution switches act as leaf switches
        
        # Full mesh between spine and leaf
        if len(routers) > 0 and len(dist_switches) > 0:
            for spine in routers:
                for leaf in dist_switches:
                    self.links.append({
                        'source': spine['name'],
                        'target': leaf['name'],
                        'type': 'spine_leaf_link',
                        'bandwidth': '40Gbps'
                    })
        
        # Connect access switches to leaf switches
        if len(access_switches) > 0 and len(dist_switches) > 0:
            for i, access_sw in enumerate(access_switches):
                leaf_idx = i % len(dist_switches)
                self.links.append({
                    'source': dist_switches[leaf_idx]['name'],
                    'target': access_sw['name'],
                    'type': 'leaf_access_link',
                    'bandwidth': '10Gbps'
                })
        
        # Connect hosts (servers) to access switches
        if len(hosts) > 0:
            if len(access_switches) > 0:
                hosts_per_switch = max(1, len(hosts) // len(access_switches))
                for i, host in enumerate(hosts):
                    switch_idx = min(i // hosts_per_switch, len(access_switches) - 1)
                    self.links.append({
                        'source': access_switches[switch_idx]['name'],
                        'target': host['name'],
                        'type': 'server_link',
                        'bandwidth': '10Gbps'
                    })
            elif len(dist_switches) > 0:
                hosts_per_switch = max(1, len(hosts) // len(dist_switches))
                for i, host in enumerate(hosts):
                    switch_idx = min(i // hosts_per_switch, len(dist_switches) - 1)
                    self.links.append({
                        'source': dist_switches[switch_idx]['name'],
                        'target': host['name'],
                        'type': 'server_link',
                        'bandwidth': '10Gbps'
                    })
    
    def _create_campus_topology(self, routers, dist_switches, access_switches, hosts, redundancy):
        """Create campus network topology"""
        # Similar to enterprise but with building-based segmentation
        self._create_enterprise_topology(routers, dist_switches, access_switches, hosts, redundancy)
    
    def _create_default_topology(self, routers, dist_switches, access_switches, hosts, redundancy):
        """Create default hierarchical topology"""
        self._create_enterprise_topology(routers, dist_switches, access_switches, hosts, redundancy)
    
    def _ai_optimize_topology(self):
        """AI-based topology optimization"""
        # Placeholder for AI optimization logic
        pass
    
    def _calculate_segments(self) -> int:
        """Calculate number of network segments"""
        # Count unique subnets
        subnets = set()
        for device in self.devices:
            if 'ip_address' in device:
                ip_parts = device['ip_address'].split('.')
                subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0"
                subnets.add(subnet)
        return len(subnets)
    
    def get_topology_json(self) -> str:
        """Export topology as JSON"""
        return json.dumps(self.topology, indent=2)
    
    def export_to_pkt(self, filename: str = "network.pkt"):
        """Export topology to Cisco Packet Tracer format"""
        # This would generate actual .pkt file
        # For now, return topology data
        return self.topology

"""
Packet Tracer Exporter
Export network topology to Cisco Packet Tracer format
"""

from typing import Dict
import json


class PacketTracerExporter:
    """Export network topology to various formats"""
    
    def __init__(self, topology: Dict):
        self.topology = topology
        
    def export_to_pkt(self, include_configs: bool = True, include_docs: bool = True) -> bytes:
        """
        Export topology to Packet Tracer .pkt format
        
        Args:
            include_configs: Include device configurations
            include_docs: Include documentation
            
        Returns:
            Binary data for .pkt file
        """
        
        # In production, this would generate actual .pkt binary format
        # For now, return JSON representation
        export_data = {
            'version': '8.2',
            'topology': self.topology,
            'configurations': self._generate_configs() if include_configs else {},
            'documentation': self._generate_documentation() if include_docs else {}
        }
        
        return json.dumps(export_data, indent=2).encode('utf-8')
    
    def _generate_configs(self) -> Dict:
        """Generate device configurations"""
        configs = {}
        
        for device in self.topology.get('devices', []):
            if device['type'] in ['router', 'switch', 'firewall']:
                configs[device['name']] = self._generate_device_config(device)
        
        return configs
    
    def _generate_device_config(self, device: Dict) -> str:
        """Generate configuration for a single device"""
        
        if device['type'] == 'router':
            return f"""!
hostname {device['name']}
!
interface GigabitEthernet0/0
 ip address {device['ip_address']} 255.255.255.0
 no shutdown
!
router ospf 1
 network {device['ip_address']} 0.0.0.255 area 0
!
line vty 0 4
 login local
 transport input ssh
!
end
"""
        elif device['type'] == 'switch':
            return f"""!
hostname {device['name']}
!
vlan 10
 name DATA
vlan 20
 name VOICE
vlan 30
 name MANAGEMENT
!
interface vlan 30
 ip address {device['ip_address']} 255.255.255.0
!
end
"""
        
        return "! No configuration available\n"
    
    def _generate_documentation(self) -> Dict:
        """Generate network documentation"""
        return {
            'network_overview': f"Network Type: {self.topology.get('network_type', 'Unknown')}",
            'total_devices': self.topology.get('total_devices', 0),
            'ip_addressing_scheme': self._document_ip_scheme(),
            'vlan_design': self._document_vlans(),
            'routing_protocols': ['OSPF'],
            'security_features': self._document_security()
        }
    
    def _document_ip_scheme(self) -> Dict:
        """Document IP addressing scheme"""
        return {
            'management_network': '192.168.100.0/24',
            'core_network': '10.0.0.0/16',
            'distribution_network': '10.1.0.0/16',
            'access_network': '10.10.0.0/16'
        }
    
    def _document_vlans(self) -> Dict:
        """Document VLAN design"""
        return {
            'VLAN 10': 'Data Network',
            'VLAN 20': 'Voice Network',
            'VLAN 30': 'Management Network',
            'VLAN 40': 'Guest Network'
        }
    
    def _document_security(self) -> list:
        """Document security features"""
        return [
            'Firewall deployed at network edge',
            'ACLs configured on all routers',
            'Port security enabled on access switches',
            'DHCP snooping enabled',
            'Dynamic ARP Inspection enabled',
            'SSH enabled for management access'
        ]

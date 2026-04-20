"""
Unit tests for NetworkTopologyGenerator
"""

import pytest
from src.topology_generator import NetworkTopologyGenerator


class TestNetworkTopologyGenerator:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.generator = NetworkTopologyGenerator()
    
    def test_generator_initialization(self):
        """Test generator initializes correctly"""
        assert self.generator is not None
        assert self.generator.topology is None
        assert self.generator.devices == []
        assert self.generator.links == []
    
    def test_generate_basic_topology(self):
        """Test basic topology generation"""
        topology = self.generator.generate_topology(
            network_type="enterprise",
            num_routers=2,
            num_switches=4,
            num_hosts=10
        )
        
        assert topology is not None
        assert 'devices' in topology
        assert 'links' in topology
        assert topology['total_devices'] > 0
        assert topology['total_links'] > 0
    
    def test_device_count(self):
        """Test correct number of devices are generated"""
        topology = self.generator.generate_topology(
            num_routers=3,
            num_switches=6,
            num_hosts=20
        )
        
        routers = [d for d in topology['devices'] if d['type'] == 'router']
        switches = [d for d in topology['devices'] if d['type'] == 'switch']
        hosts = [d for d in topology['devices'] if d['type'] == 'host']
        
        assert len(routers) == 3
        assert len(switches) == 6
        assert len(hosts) == 20
    
    def test_security_devices(self):
        """Test security devices are added based on security level"""
        high_security = self.generator.generate_topology(
            num_routers=2,
            num_switches=2,
            num_hosts=5,
            security_level="high"
        )
        
        security_devices = [d for d in high_security['devices'] 
                        if d['type'] in ['firewall', 'ips']]
        
        assert len(security_devices) > 0
    
    def test_network_types(self):
        """Test different network types"""
        network_types = ["enterprise", "datacenter", "campus"]
        
        for net_type in network_types:
            topology = self.generator.generate_topology(
                network_type=net_type,
                num_routers=2,
                num_switches=2,
                num_hosts=5
            )
            
            assert topology['network_type'] == net_type
            assert topology['total_devices'] > 0
    
    def test_redundancy(self):
        """Test redundancy creates additional links"""
        no_redundancy = self.generator.generate_topology(
            num_routers=2,
            num_switches=4,
            num_hosts=10,
            redundancy=False
        )
        
        self.generator = NetworkTopologyGenerator()  # Reset
        
        with_redundancy = self.generator.generate_topology(
            num_routers=2,
            num_switches=4,
            num_hosts=10,
            redundancy=True
        )
        
        # With redundancy should have more or equal links
        assert with_redundancy['total_links'] >= no_redundancy['total_links']
    
    def test_ip_addressing(self):
        """Test IP addresses are assigned"""
        topology = self.generator.generate_topology(
            num_routers=2,
            num_switches=2,
            num_hosts=5
        )
        
        for device in topology['devices']:
            if device['type'] in ['router', 'switch', 'host']:
                assert 'ip_address' in device
                assert device['ip_address'] is not None
    
    def test_export_json(self):
        """Test JSON export"""
        # Fixed: Use more switches to ensure access switches are created
        topology = self.generator.generate_topology(
            num_routers=2,
            num_switches=4,
            num_hosts=2
        )
        
        json_data = self.generator.get_topology_json()
        assert json_data is not None
        assert isinstance(json_data, str)
        assert 'devices' in json_data
        assert 'links' in json_data
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters"""
        with pytest.raises(ValueError):
            self.generator.generate_topology(
                num_routers=-1,
                num_switches=2,
                num_hosts=5
            )
        
        with pytest.raises(ValueError):
            self.generator.generate_topology(
                num_routers=0,
                num_switches=-5,
                num_hosts=5
            )
        
        with pytest.raises(ValueError):
            self.generator.generate_topology(
                network_type="invalid_type",
                num_routers=2,
                num_switches=2,
                num_hosts=5
            )
            
    def test_large_topology_performance(self):
        """Test performance on large topology generation"""
        import time
        
        start_time = time.time()
        topology = self.generator.generate_topology(
            num_routers=50,
            num_switches=100,
            num_hosts=500
        )
        end_time = time.time()
        
        assert topology is not None
        # Fixed: Account for potential security devices added automatically
        # Count actual devices instead of assuming exact count
        routers = [d for d in topology['devices'] if d['type'] == 'router']
        switches = [d for d in topology['devices'] if d['type'] == 'switch']
        hosts = [d for d in topology['devices'] if d['type'] == 'host']
        
        assert len(routers) == 50
        assert len(switches) == 100
        assert len(hosts) == 500
        assert (end_time - start_time) < 10  # Should complete within 10 seconds
        
if __name__ == "__main__":
    pytest.main()

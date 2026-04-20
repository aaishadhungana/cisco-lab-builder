#!/usr/bin/env python3
"""
Deployment Verification Script
Tests all core functionality before production deployment
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    try:
        import streamlit
        import plotly
        import networkx
        import pandas
        import numpy
        print("✅ All core packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_modules():
    """Test custom modules"""
    print("\nTesting custom modules...")
    try:
        from topology_generator import NetworkTopologyGenerator
        from security_auditor import SecurityAuditor
        from cloud_integrator import CloudNetworkBuilder
        from analytics_engine import NetworkAnalytics
        from packet_tracer_exporter import PacketTracerExporter
        print("✅ All custom modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Module import error: {e}")
        return False

def test_topology_generation():
    """Test topology generation"""
    print("\nTesting topology generation...")
    try:
        from topology_generator import NetworkTopologyGenerator
        
        generator = NetworkTopologyGenerator()
        topology = generator.generate_topology(
            network_type="enterprise",
            num_routers=2,
            num_switches=2,
            num_hosts=5,
            security_level="high"
        )
        
        assert topology is not None
        assert 'devices' in topology
        assert 'links' in topology
        assert topology['total_devices'] > 0
        
        print(f"✅ Topology generated: {topology['total_devices']} devices, {topology['total_links']} links")
        return True, topology
    except Exception as e:
        print(f"❌ Topology generation error: {e}")
        return False, None

def test_security_audit(topology):
    """Test security auditing"""
    print("\nTesting security audit...")
    try:
        from security_auditor import SecurityAuditor
        
        auditor = SecurityAuditor(topology)
        report = auditor.run_audit(
            audit_types=["Vulnerability Scan"],
            compliance_standards=["ISO 27001"]
        )
        
        assert report is not None
        assert 'security_score' in report
        assert 'vulnerabilities' in report
        
        print(f"✅ Security audit completed: Score {report['security_score']}/100")
        return True
    except Exception as e:
        print(f"❌ Security audit error: {e}")
        return False

def test_cloud_integration(topology):
    """Test cloud integration"""
    print("\nTesting cloud integration...")
    try:
        from cloud_integrator import CloudNetworkBuilder
        
        cloud_builder = CloudNetworkBuilder()
        result = cloud_builder.create_hybrid_topology(
            on_premise=topology,
            cloud_provider="aws",
            integration_type="site-to-site vpn",
            bandwidth=1000
        )
        
        assert result is not None
        assert 'cloud_provider' in result
        assert 'cloud_resources' in result
        
        print(f"✅ Cloud integration successful: {result['cloud_provider']}")
        return True
    except Exception as e:
        print(f"❌ Cloud integration error: {e}")
        return False

def test_analytics(topology):
    """Test analytics engine"""
    print("\nTesting analytics...")
    try:
        from analytics_engine import NetworkAnalytics
        
        analytics = NetworkAnalytics(topology)
        data = analytics.analyze()
        
        assert data is not None
        assert 'performance_metrics' in data
        
        print(f"✅ Analytics completed successfully")
        return True
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False

def test_export(topology):
    """Test export functionality"""
    print("\nTesting export...")
    try:
        from packet_tracer_exporter import PacketTracerExporter
        
        exporter = PacketTracerExporter(topology)
        pkt_data = exporter.export_to_pkt()
        
        assert pkt_data is not None
        assert len(pkt_data) > 0
        
        print(f"✅ Export successful: {len(pkt_data)} bytes")
        return True
    except Exception as e:
        print(f"❌ Export error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CISCO NETWORK TOPOLOGY SIMULATOR - DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test modules
    results.append(("Modules", test_modules()))
    
    # Test topology generation
    success, topology = test_topology_generation()
    results.append(("Topology Generation", success))
    
    if topology:
        # Test security audit
        results.append(("Security Audit", test_security_audit(topology)))
        
        # Test cloud integration
        results.append(("Cloud Integration", test_cloud_integration(topology)))
        
        # Test analytics
        results.append(("Analytics", test_analytics(topology)))
        
        # Test export
        results.append(("Export", test_export(topology)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready for production deployment!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

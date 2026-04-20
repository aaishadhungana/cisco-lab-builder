"""
Example: Basic Network Topology Generation
Demonstrates how to create a simple enterprise network
"""

from src.topology_generator import NetworkTopologyGenerator
from src.security_auditor import SecurityAuditor
from src.packet_tracer_exporter import PacketTracerExporter
import json


def main():
    print("=" * 60)
    print("Cisco Network Topology Generator - Basic Example")
    print("=" * 60)
    
    # Initialize generator
    print("\n1. Initializing topology generator...")
    generator = NetworkTopologyGenerator()
    
    # Generate enterprise network
    print("\n2. Generating enterprise network topology...")
    topology = generator.generate_topology(
        network_type="enterprise",
        num_routers=3,
        num_switches=6,
        num_hosts=30,
        security_level="high",
        redundancy=True,
        ai_optimize=True
    )
    
    print(f"\n✓ Topology generated successfully!")
    print(f"  - Total devices: {topology['total_devices']}")
    print(f"  - Total links: {topology['total_links']}")
    print(f"  - Network segments: {topology['segments']}")
    
    # Display device summary
    print("\n3. Device Summary:")
    device_types = {}
    for device in topology['devices']:
        dtype = device['type']
        device_types[dtype] = device_types.get(dtype, 0) + 1
    
    for dtype, count in device_types.items():
        print(f"  - {dtype.capitalize()}: {count}")
    
    # Run security audit
    print("\n4. Running security audit...")
    auditor = SecurityAuditor(topology)
    report = auditor.run_audit(
        audit_types=["Vulnerability Scan", "Configuration Audit"],
        compliance_standards=["ISO 27001"]
    )
    
    print(f"\n✓ Security audit completed!")
    print(f"  - Security score: {report['security_score']}/100")
    print(f"  - Vulnerabilities found: {len(report['vulnerabilities'])}")
    
    # Display vulnerabilities by severity
    severity_count = {}
    for vuln in report['vulnerabilities']:
        sev = vuln['severity']
        severity_count[sev] = severity_count.get(sev, 0) + 1
    
    print("\n  Vulnerabilities by severity:")
    for sev in ['Critical', 'High', 'Medium', 'Low']:
        if sev in severity_count:
            print(f"    - {sev}: {severity_count[sev]}")
    
    # Export to Packet Tracer
    print("\n5. Exporting to Packet Tracer format...")
    exporter = PacketTracerExporter(topology)
    pkt_data = exporter.export_to_pkt(include_configs=True, include_docs=True)
    
    # Save to file
    with open('enterprise_network.pkt', 'wb') as f:
        f.write(pkt_data)
    
    print(f"\n✓ Exported to enterprise_network.pkt")
    
    # Save topology as JSON
    print("\n6. Saving topology data...")
    with open('topology_data.json', 'w') as f:
        json.dump(topology, f, indent=2)
    
    print(f"✓ Saved to topology_data.json")
    
    # Save security report
    with open('security_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Saved security report to security_report.json")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    
    # Display recommendations
    print("\n📋 Top Security Recommendations:")
    for i, rec in enumerate(report['recommendations'][:5], 1):
        print(f"{i}. {rec}")


if __name__ == "__main__":
    main()

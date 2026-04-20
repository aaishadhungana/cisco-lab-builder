import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from src.topology_generator import NetworkTopologyGenerator
import json
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Cisco Network Topology Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'topology' not in st.session_state:
    st.session_state.topology = None
if 'generator' not in st.session_state:
    st.session_state.generator = None

# Header
st.title("🌐 Cisco Network Topology Simulator")
st.markdown("""
Generate Cisco-style network topology diagrams with AI-powered optimization.  
Perfect for network planning, documentation, and cybersecurity analysis.
""")

# Sidebar configuration
st.sidebar.header("⚙️ Topology Configuration")
st.sidebar.markdown("---")

network_type = st.sidebar.selectbox(
    "🏢 Network Type",
    ["enterprise", "datacenter", "campus", "cloud", "hybrid"],
    help="Select the type of network infrastructure"
)

st.sidebar.markdown("### 📊 Network Size")
num_routers = st.sidebar.slider("Routers", 1, 10, 3, help="Number of core routers")
num_switches = st.sidebar.slider("Switches", 2, 20, 6, help="Distribution and access switches")
num_hosts = st.sidebar.slider("Hosts/Endpoints", 5, 50, 20, help="End devices (PCs, servers)")

st.sidebar.markdown("### 🛡️ Security & Optimization")
security_level = st.sidebar.selectbox(
    "Security Level",
    ["low", "medium", "high", "critical"],
    index=2,
    help="Determines firewall and IPS placement"
)

redundancy = st.sidebar.checkbox("Enable Redundancy", value=True, help="Add redundant links for high availability")
ai_optimize = st.sidebar.checkbox("AI Optimization", value=True, help="Use AI to optimize topology design")
show_bandwidth = st.sidebar.checkbox("Show Bandwidth Labels", value=True, help="Display link speeds on diagram")

st.sidebar.markdown("---")

# Generate topology button
if st.sidebar.button("🚀 Generate Topology", type="primary", use_container_width=True):
    with st.spinner("🔄 Generating network topology..."):
        try:
            generator = NetworkTopologyGenerator()
            topology = generator.generate_topology(
                network_type=network_type,
                num_routers=num_routers,
                num_switches=num_switches,
                num_hosts=num_hosts,
                security_level=security_level,
                redundancy=redundancy,
                ai_optimize=ai_optimize
            )
            st.session_state.topology = topology
            st.session_state.generator = generator
            st.success("✅ Topology generated successfully!")
        except Exception as e:
            st.error(f"❌ Error generating topology: {str(e)}")
            with st.expander("🔍 View Error Details"):
                import traceback
                st.code(traceback.format_exc())


def compute_hierarchical_positions(topology):
    """Compute deterministic 3-tier hierarchical layout"""
    devices = topology['devices']
    
    routers = [d for d in devices if d['type'] == 'router']
    switches = [d for d in devices if d['type'] == 'switch']
    hosts = [d for d in devices if d['type'] == 'host']
    firewalls = [d for d in devices if d['type'] == 'firewall']
    ips_devices = [d for d in devices if d['type'] == 'ips']
    clouds = [d for d in devices if d['type'] == 'cloud']
    
    dist_switches = [s for s in switches if 'distribution' in s.get('subtype', '').lower()]
    access_switches = [s for s in switches if 'access' in s.get('subtype', '').lower()]
    
    if not dist_switches and not access_switches and switches:
        mid = len(switches) // 2
        dist_switches = switches[:mid] if mid > 0 else []
        access_switches = switches[mid:] if mid < len(switches) else switches
    
    pos = {}
    spacing_x = 4.5
    spacing_y = 4.0
    
    # Layer 0: Cloud
    y_cloud = 5 * spacing_y
    if clouds:
        start_x = -spacing_x * (len(clouds) - 1) / 2
        for i, cloud in enumerate(clouds):
            pos[cloud['name']] = (start_x + i * spacing_x, y_cloud)
    
    # Layer 1: Core Routers
    y_core = 4 * spacing_y
    if routers:
        start_x = -spacing_x * (len(routers) - 1) / 2
        for i, router in enumerate(routers):
            pos[router['name']] = (start_x + i * spacing_x, y_core)
    
    # Layer 2: Security
    y_security = 3.2 * spacing_y
    security_devices = firewalls + ips_devices
    if security_devices:
        start_x = -spacing_x * (len(security_devices) - 1) / 2
        for i, sec in enumerate(security_devices):
            pos[sec['name']] = (start_x + i * spacing_x, y_security)
    
    # Layer 3: Distribution Switches
    y_dist = 2.5 * spacing_y
    if dist_switches:
        start_x = -spacing_x * (len(dist_switches) - 1) / 2
        for i, switch in enumerate(dist_switches):
            pos[switch['name']] = (start_x + i * spacing_x, y_dist)
    
    # Layer 4: Access Switches
    y_access = 1.7 * spacing_y
    if access_switches:
        start_x = -spacing_x * (len(access_switches) - 1) / 2
        for i, switch in enumerate(access_switches):
            pos[switch['name']] = (start_x + i * spacing_x, y_access)
    
    # Layer 5: Hosts
    y_host = 0.8 * spacing_y
    max_hosts = min(30, len(hosts))
    if hosts:
        host_spacing_x = 3.0
        start_x = -host_spacing_x * (max_hosts - 1) / 2
        for i, host in enumerate(hosts[:max_hosts]):
            pos[host['name']] = (start_x + i * host_spacing_x, y_host)
    
    return pos


def create_cisco_diagram(topology, show_bandwidth=True):
    """Create professional Cisco-style diagram with emoji icons"""
    
    # Icon mapping
    icon_map = {
        'router': '🛜',
        'switch': '🔀',
        'host': '💻',
        'firewall': '🧱',
        'ips': '🔒',
        'cloud': '☁️'
    }
    
    G = nx.Graph()
    
    for device in topology['devices']:
        G.add_node(device['name'], **device)
    
    for link in topology['links']:
        G.add_edge(link['source'], link['target'], **link)
    
    pos = compute_hierarchical_positions(topology)
    
    fig = go.Figure()
    
    # Draw connection lines
    for u, v, data in G.edges(data=True):
        if u not in pos or v not in pos:
            continue
        
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(color='#4B5563', width=2.5),
            hoverinfo='none',
            showlegend=False
        ))
        
        if show_bandwidth:
            bandwidth = data.get('bandwidth', '')
            if bandwidth:
                mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
                
                fig.add_annotation(
                    x=mid_x,
                    y=mid_y,
                    text=f"<b>{bandwidth}</b>",
                    showarrow=False,
                    font=dict(size=10, family='Courier New, monospace', color='#DC2626'),
                    bgcolor='rgba(255, 255, 255, 0.95)',
                    bordercolor='#E5E7EB',
                    borderwidth=1,
                    borderpad=3,
                    opacity=0.95
                )
    
    # Draw device icons
    for node in G.nodes():
        if node not in pos:
            continue
        
        x, y = pos[node]
        node_data = G.nodes[node]
        device_type = node_data['type']
        ip_addr = node_data.get('ip_address', '')
        model = node_data.get('model', 'N/A')
        
        device_icon = icon_map.get(device_type, '📦')
        
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='text',
            text=[device_icon],
            textfont=dict(size=50),
            hovertext=(
                f"<b>{node}</b><br>"
                f"─────────────────<br>"
                f"<b>Type:</b> {device_type.upper()}<br>"
                f"<b>IP:</b> {ip_addr}<br>"
                f"<b>Model:</b> {model}"
            ),
            hoverinfo='text',
            showlegend=False
        ))
        
        fig.add_annotation(
            x=x,
            y=y - 0.55,
            text=f"<b>{node}</b>",
            showarrow=False,
            font=dict(size=11, family='Arial, sans-serif', color='#1F2937'),
            yanchor='top'
        )
        
        if device_type in ['router', 'switch', 'firewall', 'ips']:
            fig.add_annotation(
                x=x,
                y=y - 0.85,
                text=ip_addr,
                showarrow=False,
                font=dict(size=9, family='Courier New, monospace', color='#6B7280'),
                yanchor='top'
            )
    
    fig.update_layout(
        title=dict(
            text=f"<b>{topology['network_type'].upper()} Network Topology</b>",
            font=dict(size=26, color='#111827', family='Arial Black, sans-serif'),
            x=0.5,
            xanchor='center',
            y=0.98,
            yanchor='top'
        ),
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='#F9FAFB',
        paper_bgcolor='#FFFFFF',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-22, 22]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 22]),
        height=900,
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    return fig


def generate_cisco_commands(topology):
    """Generate Cisco IOS commands for Packet Tracer"""
    commands = {}
    
    G = nx.Graph()
    for device in topology['devices']:
        G.add_node(device['name'], **device)
    for link in topology['links']:
        G.add_edge(link['source'], link['target'], **link)
    
    interface_counter = {}
    
    def get_next_interface(device_name, device_type):
        if device_name not in interface_counter:
            interface_counter[device_name] = {'gig': 0, 'fast': 0}
        
        if device_type == 'router':
            num = interface_counter[device_name]['gig']
            interface_counter[device_name]['gig'] += 1
            return f"GigabitEthernet0/{num}"
        elif device_type == 'switch':
            num = interface_counter[device_name]['fast']
            interface_counter[device_name]['fast'] += 1
            return f"FastEthernet0/{num + 1}"
        else:
            num = interface_counter[device_name]['gig']
            interface_counter[device_name]['gig'] += 1
            return f"GigabitEthernet0/{num}"
    
    for device in topology['devices']:
        device_name = device['name']
        device_type = device['type']
        ip_address = device.get('ip_address', '')
        
        if device_type == 'host':
            commands[device_name] = f"""! Configuration for {device_name} (PC)
! Use GUI in Packet Tracer:
! 1. Click on {device_name}
! 2. Go to Desktop > IP Configuration
! 3. Set IP Address: {ip_address}
! 4. Set Subnet Mask: 255.255.255.0
! 5. Set Default Gateway: (router IP on same network)
"""
            continue
        
        config = f"""! Configuration for {device_name}
enable
configure terminal
hostname {device_name}
no ip domain-lookup
service password-encryption
enable secret cisco123

"""
        
        if device_type == 'router':
            config += """line console 0
 password cisco
 login
 logging synchronous
 exit

line vty 0 4
 password cisco
 login
 exit

"""
            neighbors = list(G.neighbors(device_name))
            for neighbor in neighbors:
                interface = get_next_interface(device_name, device_type)
                
                if ip_address:
                    ip_parts = ip_address.split('.')
                    interface_ip = f"{ip_parts[0]}.{ip_parts[1]}.{int(ip_parts[2])+1}.{ip_parts[3]}"
                    
                    config += f"""interface {interface}
 description Connection to {neighbor}
 ip address {interface_ip} 255.255.255.0
 no shutdown
 exit

"""
            
            config += f"""router ospf 1
 network {ip_address} 0.0.0.255 area 0
 exit

"""
        
        elif device_type == 'switch':
            config += """line console 0
 password cisco
 login
 exit

line vty 0 15
 password cisco
 login
 exit

vlan 10
 name DATA
 exit

vlan 99
 name MANAGEMENT
 exit

interface vlan 99
 ip address {ip_address} 255.255.255.0
 no shutdown
 exit

"""
            neighbors = list(G.neighbors(device_name))
            for neighbor in neighbors:
                neighbor_data = G.nodes[neighbor]
                interface = get_next_interface(device_name, device_type)
                
                if neighbor_data['type'] in ['router', 'switch']:
                    config += f"""interface {interface}
 description Trunk to {neighbor}
 switchport mode trunk
 no shutdown
 exit

"""
                else:
                    config += f"""interface {interface}
 description Access to {neighbor}
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
 exit

"""
        
        config += """end
write memory
"""
        
        commands[device_name] = config
    
    return commands


# Main Application
if st.session_state.topology is not None:
    topology = st.session_state.topology
    
    st.markdown("### 📊 Network Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Devices", topology['total_devices'])
    with col2:
        st.metric("Network Links", topology['total_links'])
    with col3:
        st.metric("Network Segments", topology['segments'])
    with col4:
        st.metric("Security Devices", topology['metadata'].get('security_devices', 0))
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Topology Diagram",
        "📋 Device Inventory",
        "🔗 Network Links",
        "💾 Export & Config",
        "🖥️ Cisco Commands"
    ])
    
    with tab1:
        st.markdown("### 🎨 Network Topology Visualization")
        
        try:
            fig = create_cisco_diagram(topology, show_bandwidth)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🎨 Device Legend")
            cols = st.columns(6)
            with cols[0]:
                st.markdown("🛜 **Router**")
            with cols[1]:
                st.markdown("🔀 **Switch**")
            with cols[2]:
                st.markdown("💻 **Host/PC**")
            with cols[3]:
                st.markdown("🧱 **Firewall**")
            with cols[4]:
                st.markdown("🔒 **IPS/IDS**")
            with cols[5]:
                st.markdown("☁️ **Cloud**")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("🔍 Details"):
                import traceback
                st.code(traceback.format_exc())
    
    with tab2:
        st.markdown("### 📋 Complete Device Inventory")
        
        device_types = {}
        for device in topology['devices']:
            dev_type = device['type']
            if dev_type not in device_types:
                device_types[dev_type] = []
            device_types[dev_type].append(device)
        
        type_icons = {'router': '🛜', 'switch': '🔀', 'host': '💻', 'firewall': '🧱', 'ips': '🔒', 'cloud': '☁️'}
        
        for dev_type, devices in sorted(device_types.items()):
            icon = type_icons.get(dev_type, '📦')
            with st.expander(f"{icon} **{dev_type.upper()}** ({len(devices)} devices)", expanded=True):
                df = pd.DataFrame(devices)
                
                # Fix for missing columns
                cols_to_show = ['name', 'type']
                if 'ip_address' in df.columns:
                    cols_to_show.append('ip_address')
                if 'model' in df.columns:
                    cols_to_show.append('model')
                if 'subtype' in df.columns:
                    cols_to_show.append('subtype')
                
                st.dataframe(df[cols_to_show], use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("### 🔗 Network Connection Matrix")
        
        links_df = pd.DataFrame(topology['links'])
        st.dataframe(links_df, use_container_width=True, height=400)
    
    with tab4:
        st.markdown("### 💾 Export Options")
        
        if st.session_state.generator:
            json_data = st.session_state.generator.get_topology_json()
            st.download_button(
                "📥 Download JSON",
                json_data,
                f"{network_type}_topology.json",
                "application/json"
            )
    
    with tab5:
        st.markdown("### 🖥️ Cisco Packet Tracer Configuration Commands")
        
        cisco_commands = generate_cisco_commands(topology)
        
        for dev_type in ['router', 'switch', 'firewall', 'ips']:
            devices = [d for d in topology['devices'] if d['type'] == dev_type]
            if not devices:
                continue
            
            type_icons = {'router': '🛜', 'switch': '🔀', 'firewall': '🧱', 'ips': '🔒'}
            icon = type_icons.get(dev_type, '📦')
            
            with st.expander(f"{icon} **{dev_type.upper()}** ({len(devices)} devices)", expanded=True):
                for device in devices:
                    if device['name'] in cisco_commands:
                        st.markdown(f"##### {device['name']}")
                        st.code(cisco_commands[device['name']], language='cisco')
        
        all_commands = "\n\n".join([
            f"{'='*60}\nDevice: {name}\n{'='*60}\n{cmd}\n"
            for name, cmd in cisco_commands.items()
        ])
        
        st.download_button(
            "📥 Download All Commands",
            all_commands,
            f"cisco_config_{network_type}.txt",
            "text/plain"
        )

else:
    st.info("👈 Configure and generate your topology using the sidebar")

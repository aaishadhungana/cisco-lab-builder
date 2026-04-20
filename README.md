# TOPOLOGYX: A Cisco Network Topology Simulator

A Python-based tool to generate, analyze, and simulate network topologies with security, cloud, and export features.

---

## 🔥 Features
- Generate enterprise, datacenter, campus & cloud networks  
- Routers, switches, hosts + security devices  
- Security audit (firewall, IPS, vulnerability check)  
- Network analytics  
- Packet Tracer export (simulated)  

---

## ⚙️ Run Project

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
---

## 🧪 Run Tests
```bash
pytest tests/
```

---
## 📁 Structure
```bash
topologyx/
│
├── app.py
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── topology_generator.py
│   ├── security_auditor.py
│   ├── analytics_engine.py
│   └── packet_tracer_exporter.py
│
├── examples/
│   └── basic_topology.py
│
├── tests/
│   └── test_topology_generator.py
│
└── test_deployment.py
```
---
## 👨‍💻 Author
- Built by Aaisha Dhungana 💻
- Cybersecurity + Networking project






# Enterprise Network Topology Diagram

```mermaid
graph TD
    %% LAN A - Client Side
    subgraph LANA["LAN A (Client Side)"]
        C0["Client A0<br/>10.1.1.1<br/>TCP NewReno Main"]
        C1["Client A1<br/>10.1.2.1<br/>TCP Competing 1"]
        C2["Client A2<br/>10.1.3.1<br/>TCP Competing 2"]
        C3["Client A3<br/>10.1.4.1<br/>TCP Reno"]
        C4["Client A4<br/>10.1.5.1<br/>UDP CBR"]
        SA["Switch LAN A<br/>(CSMA Bridge)"]
        
        C0 --- SA
        C1 --- SA
        C2 --- SA
        C3 --- SA
        C4 --- SA
    end
    
    %% WAN Connection
    subgraph WAN["WAN Connection"]
        RA["Router A<br/>LAN: 10.1.100.2<br/>WAN: 10.2.1.1"]
        RB["Router B<br/>WAN: 10.2.1.2<br/>LAN: 10.3.100.1"]
        
        RA ---|"P2P 5Mbps<br/>30ms delay<br/>30 packets queue"| RB
    end
    
    %% LAN B - Server Side
    subgraph LANB["LAN B (Server Side)"]
        SB["Switch LAN B<br/>(CSMA Bridge)"]
        S0["Server B0<br/>10.3.1.2"]
        S1["Server B1<br/>10.3.2.2"]
        S2["Server B2<br/>10.3.3.2"]
        
        SB --- S0
        SB --- S1
        SB --- S2
    end
    
    %% Inter-LAN Connections
    SA ---|"CSMA 100Mbps<br/>2ms delay"| RA
    RB ---|"CSMA 100Mbps<br/>2ms delay"| SB
    
    %% Traffic Flows with timing
    C0 -.->|"TCP NewReno Main<br/>1s → 190s<br/>Port 9000"| S0
    C1 -.->|"TCP Competing 1<br/>20s → 180s<br/>Port 9001"| S1
    C2 -.->|"TCP Competing 2<br/>40s → 160s<br/>Port 9002"| S2
    C3 -.->|"TCP Reno<br/>60s → 140s<br/>Port 9003"| S0
    C4 -.->|"UDP CBR 1<br/>30s → 90s<br/>1Mbps"| S2
    C4 -.->|"UDP CBR 2<br/>100s → 170s<br/>1.5Mbps"| S1
    
    %% Styling
    classDef client fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef server fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef router fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef switch fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef newreno fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef reno fill:#ffcdd2,stroke:#c62828,stroke-width:3px
    
    class C0 newreno
    class C3 reno
    class C1,C2,C4 client
    class S0,S1,S2 server
    class RA,RB router
    class SA,SB switch
```

## TCP NewReno vs TCP Reno Comparison Results

```mermaid
graph LR
    subgraph RESULTS["Simulation Results"]
        NR["TCP NewReno<br/>📊 1.03 Mbps<br/>📦 24.5 MB<br/>🔧 53,780 bytes CWND<br/>⏱️ 1s→190s"]
        R["TCP Reno<br/>📊 0.59 Mbps<br/>📦 5.97 MB<br/>🔧 42,408 bytes CWND<br/>⏱️ 60s→140s"]
        
        NR -.->|"74% better throughput<br/>26.8% higher CWND"| R
    end
    
    classDef newreno fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef reno fill:#ffcdd2,stroke:#c62828,stroke-width:3px
    
    class NR newreno
    class R reno
```

## Network Configuration Details

### **📍 Network Segments:**
- **LAN A Subnets**: 
  - Client A0: 10.1.1.0/24 (TCP NewReno Main)
  - Client A1: 10.1.2.0/24 (TCP Competing 1)  
  - Client A2: 10.1.3.0/24 (TCP Competing 2)
  - Client A3: 10.1.4.0/24 (TCP Reno)
  - Client A4: 10.1.5.0/24 (UDP CBR)
- **LAN A-Router**: 10.1.100.0/24
- **WAN Link**: 10.2.1.0/24 
- **LAN B-Router**: 10.3.100.0/24
- **LAN B Subnets**: 
  - Server B0: 10.3.1.0/24
  - Server B1: 10.3.2.0/24  
  - Server B2: 10.3.3.0/24

### **🔗 Link Specifications:**
- **LAN Links (CSMA)**: 100 Mbps, 2ms delay, 100 packet queue
- **WAN Link (P2P)**: 5 Mbps, 30ms delay, 30 packet queue

### **🚀 Traffic Flows:**
1. **🟢 Main TCP NewReno**: Client A0 → Server B0 (1s-190s, Port 9000)
2. **🔴 TCP Reno**: Client A3 → Server B0 (60s-140s, Port 9003) - **NEW!**
3. **🔵 Competing TCP 1**: Client A1 → Server B1 (20s-180s, Port 9001) 
4. **🔵 Competing TCP 2**: Client A2 → Server B2 (40s-160s, Port 9002)
5. **🟡 UDP CBR 1**: Client A4 → Server B2 (30s-90s, 1 Mbps)
6. **🟡 UDP CBR 2**: Client A4 → Server B1 (100s-170s, 1.5 Mbps)

### **⚙️ TCP Configuration:**
- **NewReno Protocol**: Fast Recovery with partial ACK handling
- **Reno Protocol**: Traditional Fast Recovery
- **Segment Size**: 1448 bytes
- **Initial Congestion Window**: 10 segments
- **Features**: SACK, Window Scaling, Timestamps enabled
- **Buffer Sizes**: 131072 bytes (send/receive)

### **📊 Performance Comparison:**
- **TCP NewReno**: 1.03 Mbps average throughput, 53,780 bytes average CWND
- **TCP Reno**: 0.59 Mbps average throughput, 42,408 bytes average CWND
- **Performance Gain**: NewReno shows 74% better throughput and 26.8% higher CWND
- **Network Utilization**: 104.2% of 5Mbps WAN capacity (due to competing traffic)

### **📁 Generated Files:**
All simulation data files are saved in the `scratch/` directory:
- `enterprise-main-newreno-rx.data` / `enterprise-main-newreno-cwnd.data`
- `enterprise-reno-rx.data` / `enterprise-reno-cwnd.data`  
- `enterprise-comp1-newreno-rx.data` / `enterprise-comp1-newreno-cwnd.data`
- `enterprise-comp2-newreno-rx.data` / `enterprise-comp2-newreno-cwnd.data`
- `enterprise-udp1-rx.data` / `enterprise-udp2-rx.data`
- `enterprise-flowmon-results.xml`
- `enterprise-all-rx.data` 
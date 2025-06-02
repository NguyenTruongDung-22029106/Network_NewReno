# So sánh TCP NewReno vs TCP Reno trong NS-3

## 🎯 Tổng quan
Project này thực hiện so sánh hiệu suất chi tiết giữa hai thuật toán kiểm soát tắc nghẽn TCP:
- **TCP NewReno**: Phiên bản cải tiến với Fast Recovery nâng cao và xử lý partial ACK
- **TCP Reno**: Thuật toán TCP truyền thống với Fast Retransmit và Fast Recovery cơ bản

### 📊 Kết quả chính
- **TCP NewReno**: 1.03 Mbps throughput trung bình, 53.8 KB CWND trung bình
- **TCP Reno**: 0.59 Mbps throughput trung bình, 42.4 KB CWND trung bình  
- **Hiệu suất**: NewReno vượt trội 74% về throughput và 26.8% về CWND

## 🏗️ Cấu trúc mô phỏng

### Topology mạng
```
[Clients A] -- [Switch A] -- [Router A] -- WAN -- [Router B] -- [Switch B] -- [Servers B]
    5 nodes      Bridge       Node         5Mbps     Node        Bridge       3 nodes
```

### Các luồng dữ liệu
1. **🟢 Main TCP NewReno**: Client A0 → Server B0 (1.0s - 190.0s, Port 9000)
2. **🔴 TCP Reno**: Client A3 → Server B0 (60.0s - 140.0s, Port 9003) - **Luồng so sánh chính**
3. **🔵 Competing TCP flows**: 
   - TCP1: Client A1 → Server B1 (20.0s - 180.0s, Port 9001)
   - TCP2: Client A2 → Server B2 (40.0s - 160.0s, Port 9002)
4. **🟡 UDP background traffic**:
   - UDP1: 1Mbps (30.0s - 90.0s) → Server B2
   - UDP2: 1.5Mbps (100.0s - 170.0s) → Server B1

### Thông số mạng
- **LAN Links**: 100 Mbps, 2ms delay, 100 packet queue
- **WAN Link**: 5 Mbps, 30ms delay, 30 packet queue (bottleneck)
- **Addressing**: Multiple subnets (10.1.x.0/24, 10.3.x.0/24)

## 🚀 Cách chạy mô phỏng

### 1. Biên dịch và chạy NS-3
```bash
# Từ thư mục ns-3.44
./ns3 configure --enable-examples --enable-tests
./ns3 build

# Chạy mô phỏng so sánh TCP
./ns3 run scratch/enterprise-network-newreno
```

### 2. Phân tích kết quả chi tiết
```bash
# Chuyển đến thư mục scratch
cd scratch/

# Chạy script phân tích đầy đủ (khuyến nghị)
python3 analyze_complete.py

# Hoặc phân tích đơn giản
python3 analyze_simple.py

# Tạo biểu đồ so sánh cơ bản
python3 plot_comparison.py

# Hiển thị tóm tắt kết quả
python3 summary_display.py
```

## 📁 File kết quả được tạo

### Dữ liệu thô (Raw Data)
- `enterprise-main-newreno-rx.data` / `enterprise-main-newreno-cwnd.data`: TCP NewReno chính
- `enterprise-reno-rx.data` / `enterprise-reno-cwnd.data`: TCP Reno so sánh
- `enterprise-comp1-newreno-rx.data` / `enterprise-comp1-newreno-cwnd.data`: Competing TCP 1
- `enterprise-comp2-newreno-rx.data` / `enterprise-comp2-newreno-cwnd.data`: Competing TCP 2
- `enterprise-udp1-rx.data` / `enterprise-udp2-rx.data`: UDP background traffic
- `enterprise-all-rx.data`: Tổng hợp tất cả flows
- `enterprise-flowmon-results.xml`: Thống kê chi tiết FlowMonitor

### Kết quả phân tích
- `tcp_network_analysis.png`: **Biểu đồ tổng hợp 6 panel**:
  1. Throughput tích lũy theo thời gian
  2. Throughput tức thời (moving average)
  3. Histogram phân phối throughput
  4. So sánh thống kê tổng hợp
  5. Fairness index và network utilization
  6. Timeline các events mạng

- `tcp_throughput_analysis.png`: **Phân tích throughput chi tiết**
- `tcp_cwnd_analysis.png`: **Phân tích Congestion Window**
- `tcp_analysis_report.txt`: **Báo cáo văn bản chi tiết**

## 📊 Các thông số so sánh chính

### Metrics đánh giá
1. **Throughput Performance**:
   - Throughput trung bình, tối đa, tối thiểu
   - Độ lệch chuẩn và độ ổn định
   - Hiệu suất sử dụng băng thông WAN

2. **Congestion Window Analysis**:
   - CWND trung bình, tối đa, tối thiểu
   - Số lần tăng/giảm CWND
   - Độ ổn định CWND (stability index)

3. **Network Fairness**:
   - Jain's Fairness Index
   - Chia sẻ băng thông giữa các flows
   - Tác động của UDP traffic

4. **Recovery Performance**:
   - Thời gian phục hồi sau packet loss
   - Hiệu quả xử lý multiple packet loss
   - Behavior trong môi trường tắc nghẽn

### Điều kiện thử nghiệm
- **Bandwidth**: WAN link 5Mbps (bottleneck)
- **Delay**: 30ms WAN delay, 2ms LAN delay
- **Queue size**: 30 packets (WAN), 100 packets (LAN)
- **Packet loss**: Do queue overflow tự nhiên
- **Background traffic**: UDP CBR và TCP competing flows
- **Simulation time**: 200 giây

## 📈 Kết quả chi tiết

### TCP NewReno vs TCP Reno
```
TCP NewReno:
├── Throughput: 1.035 Mbps (74% tốt hơn)
├── CWND: 53,780 bytes (26.8% cao hơn)
├── Dữ liệu: 24.48 MB trong 189.2s
├── Packets: 16,764 gói
└── WAN utilization: 20.7%

TCP Reno:
├── Throughput: 0.595 Mbps
├── CWND: 42,408 bytes
├── Dữ liệu: 5.97 MB trong 80.3s
├── Packets: 3,265 gói
└── WAN utilization: 11.9%
```

### Phân tích so sánh
- **NewReno** thường có throughput cao hơn nhờ:
  - Fast Recovery cải tiến với partial ACK handling
  - Xử lý multiple packet loss hiệu quả hơn
  - Không giảm cwnd nhiều lần trong một RTT
  - Recovery nhanh hơn sau congestion events

- **Reno** có xu hướng:
  - Conservative hơn trong việc tăng cwnd
  - Recovery chậm hơn sau packet loss
  - Throughput thấp hơn trong môi trường có loss
  - Ổn định hơn nhưng kém hiệu quả

## 🛠️ Troubleshooting

### Lỗi thường gặp
1. **"TcpReno not found"**: 
   ```bash
   # Kiểm tra NS-3 version (cần ≥ 3.40)
   ./ns3 --version
   # Đảm bảo TCP modules được compile
   ./ns3 configure --enable-modules=internet
   ```

2. **Không có dữ liệu Reno**:
   - Kiểm tra `renoTcpStartTime > 0` trong code
   - Verify nodes đủ (cần ít nhất 4 clients)
   - Check simulation time đủ dài

3. **Script Python lỗi**:
   ```bash
   # Cài đặt dependencies
   pip3 install matplotlib pandas numpy seaborn scipy
   ```

4. **File không tồn tại**:
   ```bash
   # Kiểm tra files được tạo
   ls -la enterprise-*.data
   # Verify quyền ghi trong thư mục scratch
   ```

### Debug tips
- Enable logging: `LogComponentEnable("TcpSocketBase", LOG_LEVEL_INFO)`
- Check trace files: Verify file sizes > 0
- Validate simulation time: Đảm bảo flows chạy đủ lâu để so sánh
- Monitor memory usage: Large simulations có thể cần nhiều RAM

## ⚙️ Tùy chỉnh thử nghiệm

### Thay đổi thông số mạng
```cpp
// Trong enterprise-network-newreno.cc
double simulationTime = 200.0;           // Thời gian mô phỏng
std::string wanDataRate = "5Mbps";       // Bandwidth bottleneck
std::string wanDelay = "30ms";           // Network delay
std::string wanQueueSize = "30p";        // Queue size
double renoTcpStartTime = 60.0;          // Thời gian bắt đầu TCP Reno
double renoTcpStopTime = 140.0;          // Thời gian kết thúc
```

### Thêm thuật toán TCP khác
Có thể thêm các variant khác:
```cpp
// Trong SetupTcpConnection()
"ns3::TcpCubic"     // TCP CUBIC
"ns3::TcpBbr"       // TCP BBR (nếu có)
"ns3::TcpVegas"     // TCP Vegas
"ns3::TcpWestwood"  // TCP Westwood
```

### Tùy chỉnh phân tích
```python
# Trong analyze_complete.py
window_size = 5.0           # Cửa sổ moving average
bins = 50                   # Số bins cho histogram
figsize = (16, 12)          # Kích thước biểu đồ
```

## 📚 Tài liệu tham khảo
- [NS-3 TCP Documentation](https://www.nsnam.org/docs/models/html/tcp.html)
- [RFC 2581 - TCP Congestion Control](https://tools.ietf.org/html/rfc2581)
- [RFC 3782 - TCP NewReno](https://tools.ietf.org/html/rfc3782)
- [Network Topology Diagram](network-diagram.md)

## 🔄 Phiên bản và cập nhật
- **Current Version**: NS-3.44 compatible
- **Last Updated**: 2025-06-01
- **Features**: Advanced analysis, multiple metrics, detailed reporting
- **Requirements**: Python 3.6+, matplotlib, pandas, numpy, seaborn 
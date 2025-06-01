# So sánh TCP NewReno vs TCP Reno trong NS-3

## Tổng quan
Project này so sánh hiệu suất giữa hai thuật toán kiểm soát tắc nghẽn TCP:
- **TCP NewReno**: Phiên bản cải tiến của TCP Reno với khả năng phục hồi nhanh hơn
- **TCP Reno**: Thuật toán TCP truyền thống với Fast Retransmit và Fast Recovery

## Cấu trúc mô phỏng

### Topology mạng
```
[Clients A] -- [Switch A] -- [Router A] -- WAN -- [Router B] -- [Switch B] -- [Servers B]
    5 nodes      Bridge       Node         5Mbps     Node        Bridge       3 nodes
```

### Các luồng dữ liệu
1. **Main TCP NewReno**: Client A0 → Server B0 (1.0s - 190.0s)
2. **TCP Reno**: Client A3 → Server B0 (60.0s - 140.0s) - *MỚI THÊM*
3. **Competing TCP flows**: 
   - TCP1: Client A1 → Server B1 (20.0s - 180.0s)
   - TCP2: Client A2 → Server B2 (40.0s - 160.0s)
4. **UDP background traffic**:
   - UDP1: 1Mbps (30.0s - 90.0s)
   - UDP2: 1.5Mbps (100.0s - 170.0s)

## Cách chạy mô phỏng

### 1. Biên dịch và chạy NS-3
```bash
# Từ thư mục ns-3.44
./ns3 configure --enable-examples --enable-tests
./ns3 build

# Chạy mô phỏng so sánh TCP
./ns3 run scratch/enterprise-network-newreno
```

### 2. Phân tích kết quả
```bash
# Chuyển đến thư mục scratch
cd scratch/

# Chạy script phân tích Python
python3 compare_tcp_algorithms.py
```

## File kết quả được tạo

### Dữ liệu thô
- `enterprise-main-newreno-rx.data`: Throughput TCP NewReno
- `enterprise-main-newreno-cwnd.data`: Congestion Window TCP NewReno
- `enterprise-reno-rx.data`: Throughput TCP Reno
- `enterprise-reno-cwnd.data`: Congestion Window TCP Reno
- `enterprise-flowmon-results.xml`: Thống kê chi tiết FlowMonitor

### Kết quả phân tích
- `tcp_comparison.png`: Biểu đồ so sánh 4 panel:
  1. **Throughput theo thời gian**: So sánh hiệu suất truyền tải
  2. **Congestion Window**: So sánh cách thức điều chỉnh cửa sổ tắc nghẽn
  3. **Histogram Throughput**: Phân bố giá trị throughput
  4. **Thống kê tổng hợp**: Số liệu so sánh chi tiết

## Các thông số so sánh chính

### Metrics đánh giá
1. **Throughput trung bình** (Mbps)
2. **Congestion Window**:
   - Giá trị tối đa
   - Giá trị trung bình
   - Độ ổn định
3. **Fairness**: Chia sẻ băng thông với các flow khác
4. **Recovery time**: Thời gian phục hồi sau packet loss

### Điều kiện thử nghiệm
- **Bandwidth**: WAN link 5Mbps (bottleneck)
- **Delay**: 30ms WAN delay
- **Queue size**: 30 packets
- **Packet loss**: Do queue overflow
- **Background traffic**: UDP và TCP competing flows

## Kết quả mong đợi

### TCP NewReno vs TCP Reno
- **NewReno** thường có throughput cao hơn nhờ:
  - Fast Recovery cải tiến
  - Xử lý multiple packet loss tốt hơn
  - Không giảm cwnd nhiều lần trong một RTT

- **Reno** có xu hướng:
  - Conservative hơn trong việc tăng cwnd
  - Recovery chậm hơn sau packet loss
  - Throughput thấp hơn trong môi trường có loss

## Troubleshooting

### Lỗi thường gặp
1. **"TcpReno not found"**: 
   - Kiểm tra NS-3 version (cần ≥ 3.40)
   - Đảm bảo TCP modules được compile

2. **Không có dữ liệu Reno**:
   - Kiểm tra `renoTcpStartTime > 0` trong code
   - Verify nodes đủ (cần ít nhất 4 clients)

3. **Script Python lỗi**:
   ```bash
   # Cài đặt dependencies
   pip3 install matplotlib pandas numpy
   ```

### Debug tips
- Enable logging: `LogComponentEnable("TcpSocketBase", LOG_LEVEL_INFO)`
- Check trace files: `ls -la enterprise-*.data`
- Validate simulation time: Đảm bảo flows chạy đủ lâu để so sánh

## Tùy chỉnh thử nghiệm

### Thay đổi thông số
```cpp
// Trong enterprise-network-newreno.cc
double renoTcpStartTime = 60.0;  // Thời gian bắt đầu TCP Reno
double renoTcpStopTime = 140.0;  // Thời gian kết thúc
std::string wanDataRate = "5Mbps";  // Bandwidth bottleneck
std::string wanDelay = "30ms";       // Network delay
```

### Thêm thuật toán TCP khác
Có thể thêm các variant khác như:
- TcpCubic: `"ns3::TcpCubic"`
- TcpBbr: `"ns3::TcpBbr"` (nếu có sẵn)
- TcpVegas: `"ns3::TcpVegas"`

## Tài liệu tham khảo
- [NS-3 TCP Documentation](https://www.nsnam.org/docs/models/html/tcp.html)
- [RFC 2581 - TCP Congestion Control](https://tools.ietf.org/html/rfc2581)
- [RFC 3782 - TCP NewReno](https://tools.ietf.org/html/rfc3782) 
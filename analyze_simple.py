#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script đơn giản để so sánh hiệu suất TCP NewReno vs TCP Reno
Không cần matplotlib - chỉ phân tích văn bản
"""

import os

def read_rx_data(filename):
    """Đọc dữ liệu throughput từ file rx data"""
    if not os.path.exists(filename):
        print(f"Cảnh báo: File {filename} không tồn tại")
        return []
    
    try:
        data = []
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    time = float(parts[0])
                    bytes_val = int(parts[1])
                    data.append((time, bytes_val))
        return data
    except Exception as e:
        print(f"Lỗi đọc file {filename}: {e}")
        return []

def read_cwnd_data(filename):
    """Đọc dữ liệu congestion window từ file cwnd data"""
    if not os.path.exists(filename):
        print(f"Cảnh báo: File {filename} không tồn tại")
        return []
    
    try:
        data = []
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    time = float(parts[0])
                    cwnd = int(parts[1])
                    data.append((time, cwnd))
        return data
    except Exception as e:
        print(f"Lỗi đọc file {filename}: {e}")
        return []

def calculate_stats(rx_data):
    """Tính thống kê từ dữ liệu rx"""
    if not rx_data:
        return 0, 0, 0, 0
    
    total_bytes = sum(bytes_val for _, bytes_val in rx_data)
    start_time = min(time for time, _ in rx_data)
    end_time = max(time for time, _ in rx_data)
    duration = end_time - start_time
    
    if duration > 0:
        avg_throughput = (total_bytes * 8) / (duration * 1e6)  # Mbps
    else:
        avg_throughput = 0
    
    return total_bytes, duration, avg_throughput, len(rx_data)

def calculate_cwnd_stats(cwnd_data):
    """Tính thống kê từ dữ liệu congestion window"""
    if not cwnd_data:
        return 0, 0, 0
    
    cwnd_values = [cwnd for _, cwnd in cwnd_data]
    max_cwnd = max(cwnd_values)
    min_cwnd = min(cwnd_values)
    avg_cwnd = sum(cwnd_values) / len(cwnd_values)
    
    return max_cwnd, min_cwnd, avg_cwnd

def main():
    """Hàm chính"""
    print("="*60)
    print("        SO SÁNH TCP NEWRENO VS TCP RENO")
    print("="*60)
    
    # Đọc dữ liệu
    print("\n1. Đọc dữ liệu từ các file...")
    newreno_rx = read_rx_data('enterprise-main-newreno-rx.data')
    newreno_cwnd = read_cwnd_data('enterprise-main-newreno-cwnd.data')
    reno_rx = read_rx_data('enterprise-reno-rx.data')
    reno_cwnd = read_cwnd_data('enterprise-reno-cwnd.data')
    
    print(f"   - TCP NewReno RX: {len(newreno_rx)} data points")
    print(f"   - TCP NewReno CWND: {len(newreno_cwnd)} data points")
    print(f"   - TCP Reno RX: {len(reno_rx)} data points")
    print(f"   - TCP Reno CWND: {len(reno_cwnd)} data points")
    
    # Phân tích TCP NewReno
    print("\n2. PHÂN TÍCH TCP NEWRENO:")
    print("-" * 30)
    if newreno_rx:
        total_bytes, duration, avg_throughput, num_packets = calculate_stats(newreno_rx)
        print(f"   • Tổng bytes nhận: {total_bytes:,} bytes")
        print(f"   • Thời gian truyền: {duration:.2f} giây")
        print(f"   • Throughput TB: {avg_throughput:.2f} Mbps")
        print(f"   • Số gói tin: {num_packets:,}")
    else:
        print("   • Không có dữ liệu throughput")
    
    if newreno_cwnd:
        max_cwnd, min_cwnd, avg_cwnd = calculate_cwnd_stats(newreno_cwnd)
        print(f"   • CWND tối đa: {max_cwnd:,} bytes")
        print(f"   • CWND tối thiểu: {min_cwnd:,} bytes")
        print(f"   • CWND trung bình: {avg_cwnd:.0f} bytes")
    else:
        print("   • Không có dữ liệu congestion window")
    
    # Phân tích TCP Reno
    print("\n3. PHÂN TÍCH TCP RENO:")
    print("-" * 30)
    if reno_rx:
        total_bytes_reno, duration_reno, avg_throughput_reno, num_packets_reno = calculate_stats(reno_rx)
        print(f"   • Tổng bytes nhận: {total_bytes_reno:,} bytes")
        print(f"   • Thời gian truyền: {duration_reno:.2f} giây")
        print(f"   • Throughput TB: {avg_throughput_reno:.2f} Mbps")
        print(f"   • Số gói tin: {num_packets_reno:,}")
    else:
        print("   • Không có dữ liệu throughput")
        
    if reno_cwnd:
        max_cwnd_reno, min_cwnd_reno, avg_cwnd_reno = calculate_cwnd_stats(reno_cwnd)
        print(f"   • CWND tối đa: {max_cwnd_reno:,} bytes")
        print(f"   • CWND tối thiểu: {min_cwnd_reno:,} bytes")
        print(f"   • CWND trung bình: {avg_cwnd_reno:.0f} bytes")
    else:
        print("   • Không có dữ liệu congestion window")
    
    # So sánh
    print("\n4. SO SÁNH KẾT QUẢ:")
    print("-" * 30)
    if newreno_rx and reno_rx:
        # So sánh throughput
        if avg_throughput_reno > 0:
            improvement = ((avg_throughput - avg_throughput_reno) / avg_throughput_reno) * 100
            print(f"   • Throughput NewReno: {avg_throughput:.2f} Mbps")
            print(f"   • Throughput Reno: {avg_throughput_reno:.2f} Mbps")
            print(f"   • Cải thiện: {improvement:+.1f}%")
            
            if improvement > 0:
                print(f"   ➤ TCP NewReno hiệu quả hơn TCP Reno {abs(improvement):.1f}%")
            elif improvement < 0:
                print(f"   ➤ TCP Reno hiệu quả hơn TCP NewReno {abs(improvement):.1f}%")
            else:
                print(f"   ➤ Hiệu suất tương đương")
        
        # So sánh bytes
        if total_bytes_reno > 0:
            byte_ratio = (total_bytes / total_bytes_reno) * 100
            print(f"   • NewReno truyền {byte_ratio:.1f}% so với Reno")
    
    if newreno_cwnd and reno_cwnd:
        print(f"   • CWND trung bình NewReno: {avg_cwnd:.0f} bytes")
        print(f"   • CWND trung bình Reno: {avg_cwnd_reno:.0f} bytes")
        if avg_cwnd_reno > 0:
            cwnd_improvement = ((avg_cwnd - avg_cwnd_reno) / avg_cwnd_reno) * 100
            print(f"   • Cải thiện CWND: {cwnd_improvement:+.1f}%")
    
    # Phân tích file khác
    print("\n5. THÔNG TIN THÊM:")
    print("-" * 30)
    
    # Kiểm tra file competing flows
    comp1_rx = read_rx_data('enterprise-comp1-newreno-rx.data')
    comp2_rx = read_rx_data('enterprise-comp2-newreno-rx.data')
    udp1_rx = read_rx_data('enterprise-udp1-rx.data')
    udp2_rx = read_rx_data('enterprise-udp2-rx.data')
    
    if comp1_rx:
        _, _, comp1_throughput, _ = calculate_stats(comp1_rx)
        print(f"   • Competing TCP 1: {comp1_throughput:.2f} Mbps")
    
    if comp2_rx:
        _, _, comp2_throughput, _ = calculate_stats(comp2_rx)
        print(f"   • Competing TCP 2: {comp2_throughput:.2f} Mbps")
    
    if udp1_rx:
        _, _, udp1_throughput, _ = calculate_stats(udp1_rx)
        print(f"   • UDP Flow 1: {udp1_throughput:.2f} Mbps")
    
    if udp2_rx:
        _, _, udp2_throughput, _ = calculate_stats(udp2_rx)
        print(f"   • UDP Flow 2: {udp2_throughput:.2f} Mbps")
    
    # Tổng throughput
    total_throughput = 0
    if newreno_rx:
        total_throughput += avg_throughput
    if reno_rx:
        total_throughput += avg_throughput_reno
    if comp1_rx:
        total_throughput += comp1_throughput
    if comp2_rx:
        total_throughput += comp2_throughput
    if udp1_rx:
        total_throughput += udp1_throughput
    if udp2_rx:
        total_throughput += udp2_throughput
        
    print(f"   • Tổng throughput mạng: {total_throughput:.2f} Mbps")
    print(f"   • Bandwidth utilization: {(total_throughput/5)*100:.1f}% (WAN 5Mbps)")
    
    print("\n" + "="*60)
    print("Hoàn thành phân tích!")
    print("="*60)

if __name__ == "__main__":
    main() 
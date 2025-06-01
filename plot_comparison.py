#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script vẽ biểu đồ so sánh TCP NewReno vs TCP Reno
"""

import matplotlib.pyplot as plt
import numpy as np
import os

def read_data(filename):
    """Đọc dữ liệu từ file"""
    if not os.path.exists(filename):
        return [], []
    
    times, values = [], []
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    times.append(float(parts[0]))
                    values.append(int(parts[1]))
    except:
        pass
    return times, values

def plot_comparison():
    """Vẽ biểu đồ so sánh"""
    # Đọc dữ liệu
    newreno_rx_times, newreno_rx_bytes = read_data('enterprise-main-newreno-rx.data')
    newreno_cwnd_times, newreno_cwnd_values = read_data('enterprise-main-newreno-cwnd.data')
    reno_rx_times, reno_rx_bytes = read_data('enterprise-reno-rx.data')
    reno_cwnd_times, reno_cwnd_values = read_data('enterprise-reno-cwnd.data')
    
    # Tạo figure với 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Biểu đồ 1: Throughput qua thời gian
    if newreno_rx_times:
        # Tính throughput tích lũy (cumulative)
        cumulative_bytes = np.cumsum(newreno_rx_bytes)
        throughput_mbps = (cumulative_bytes * 8) / (np.array(newreno_rx_times) * 1e6)
        ax1.plot(newreno_rx_times, throughput_mbps, 'g-', label='TCP NewReno', linewidth=2)
    
    if reno_rx_times:
        cumulative_bytes = np.cumsum(reno_rx_bytes)
        throughput_mbps = (cumulative_bytes * 8) / (np.array(reno_rx_times) * 1e6)
        ax1.plot(reno_rx_times, throughput_mbps, 'r-', label='TCP Reno', linewidth=2)
    
    ax1.set_xlabel('Thời gian (giây)')
    ax1.set_ylabel('Throughput tích lũy (Mbps)')
    ax1.set_title('So sánh Throughput: TCP NewReno vs TCP Reno')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Biểu đồ 2: Congestion Window
    if newreno_cwnd_times:
        cwnd_kb = np.array(newreno_cwnd_values) / 1024  # Convert to KB
        ax2.plot(newreno_cwnd_times, cwnd_kb, 'g-', label='TCP NewReno', linewidth=2)
    
    if reno_cwnd_times:
        cwnd_kb = np.array(reno_cwnd_values) / 1024  # Convert to KB
        ax2.plot(reno_cwnd_times, cwnd_kb, 'r-', label='TCP Reno', linewidth=2)
    
    ax2.set_xlabel('Thời gian (giây)')
    ax2.set_ylabel('Congestion Window (KB)')
    ax2.set_title('So sánh Congestion Window: TCP NewReno vs TCP Reno')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('tcp_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Đã lưu biểu đồ: tcp_comparison.png")
    
    # Biểu đồ cột so sánh tổng kết
    fig2, ax3 = plt.subplots(figsize=(10, 6))
    
    # Tính toán số liệu tổng kết
    newreno_total = sum(newreno_rx_bytes) if newreno_rx_bytes else 0
    reno_total = sum(reno_rx_bytes) if reno_rx_bytes else 0
    newreno_avg_cwnd = np.mean(newreno_cwnd_values) if newreno_cwnd_values else 0
    reno_avg_cwnd = np.mean(reno_cwnd_values) if reno_cwnd_values else 0
    
    # Dữ liệu cho biểu đồ cột
    categories = ['Tổng bytes (MB)', 'CWND TB (KB)', 'Throughput (Mbps)']
    newreno_values = [
        newreno_total / 1e6,  # MB
        newreno_avg_cwnd / 1024,  # KB
        1.03  # Mbps từ kết quả trước
    ]
    reno_values = [
        reno_total / 1e6,  # MB
        reno_avg_cwnd / 1024,  # KB
        0.59  # Mbps từ kết quả trước
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax3.bar(x - width/2, newreno_values, width, label='TCP NewReno', color='green', alpha=0.7)
    ax3.bar(x + width/2, reno_values, width, label='TCP Reno', color='red', alpha=0.7)
    
    ax3.set_xlabel('Metrics')
    ax3.set_ylabel('Values')
    ax3.set_title('Tổng kết so sánh TCP NewReno vs TCP Reno')
    ax3.set_xticks(x)
    ax3.set_xticklabels(categories)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Thêm số liệu lên cột
    for i, (nr_val, r_val) in enumerate(zip(newreno_values, reno_values)):
        ax3.text(i - width/2, nr_val + max(newreno_values) * 0.01, f'{nr_val:.1f}', 
                ha='center', va='bottom', fontweight='bold')
        ax3.text(i + width/2, r_val + max(newreno_values) * 0.01, f'{r_val:.1f}', 
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('tcp_summary.png', dpi=300, bbox_inches='tight')
    print("✅ Đã lưu biểu đồ tổng kết: tcp_summary.png")

if __name__ == "__main__":
    print("🎨 Đang tạo biểu đồ so sánh TCP NewReno vs TCP Reno...")
    plot_comparison()
    print("🎉 Hoàn thành!") 
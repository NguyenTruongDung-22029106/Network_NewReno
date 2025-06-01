#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script phân tích đầy đủ và chi tiết TCP NewReno vs TCP Reno
Bao gồm biểu đồ, thống kê, và báo cáo chi tiết
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os
import seaborn as sns
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style cho biểu đồ đẹp hơn
try:
    plt.style.use('seaborn-v0_8')
except OSError:
    try:
        plt.style.use('seaborn')
    except OSError:
        plt.style.use('default')
sns.set_palette("husl")

class TCPAnalyzer:
    def __init__(self):
        self.data = {}
        self.stats = {}
        
    def read_rx_data(self, filename, flow_name):
        """Đọc dữ liệu throughput từ file rx data"""
        if not os.path.exists(filename):
            print(f"⚠️  File {filename} không tồn tại")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(filename, sep='\t', header=None, names=['time', 'bytes'])
            df['flow'] = flow_name
            df['cumulative_bytes'] = df['bytes'].cumsum()
            df['throughput_mbps'] = (df['cumulative_bytes'] * 8) / (df['time'] * 1e6)
            df['instant_throughput'] = (df['bytes'] * 8) / 1e6  # Mbps tức thời
            return df
        except Exception as e:
            print(f"❌ Lỗi đọc file {filename}: {e}")
            return pd.DataFrame()
    
    def read_cwnd_data(self, filename, flow_name):
        """Đọc dữ liệu congestion window từ file cwnd data"""
        if not os.path.exists(filename):
            print(f"⚠️  File {filename} không tồn tại")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(filename, sep='\t', header=None, names=['time', 'cwnd'])
            df['flow'] = flow_name
            df['cwnd_kb'] = df['cwnd'] / 1024
            return df
        except Exception as e:
            print(f"❌ Lỗi đọc file {filename}: {e}")
            return pd.DataFrame()
    
    def load_all_data(self):
        """Tải tất cả dữ liệu từ các file"""
        print("📊 Đang tải dữ liệu từ các file...")
        
        # TCP flows
        self.data['newreno_rx'] = self.read_rx_data('enterprise-main-newreno-rx.data', 'TCP NewReno')
        self.data['newreno_cwnd'] = self.read_cwnd_data('enterprise-main-newreno-cwnd.data', 'TCP NewReno')
        self.data['reno_rx'] = self.read_rx_data('enterprise-reno-rx.data', 'TCP Reno')
        self.data['reno_cwnd'] = self.read_cwnd_data('enterprise-reno-cwnd.data', 'TCP Reno')
        
        # Competing flows
        self.data['comp1_rx'] = self.read_rx_data('enterprise-comp1-newreno-rx.data', 'Competing TCP 1')
        self.data['comp1_cwnd'] = self.read_cwnd_data('enterprise-comp1-newreno-cwnd.data', 'Competing TCP 1')
        self.data['comp2_rx'] = self.read_rx_data('enterprise-comp2-newreno-rx.data', 'Competing TCP 2')
        self.data['comp2_cwnd'] = self.read_cwnd_data('enterprise-comp2-newreno-cwnd.data', 'Competing TCP 2')
        
        # UDP flows
        self.data['udp1_rx'] = self.read_rx_data('enterprise-udp1-rx.data', 'UDP CBR 1')
        self.data['udp2_rx'] = self.read_rx_data('enterprise-udp2-rx.data', 'UDP CBR 2')
        
        print("✅ Đã tải xong tất cả dữ liệu")
    
    def calculate_statistics(self):
        """Tính toán thống kê chi tiết"""
        print("🔢 Đang tính toán thống kê...")
        
        for key, df in self.data.items():
            if df.empty:
                continue
                
            flow_name = df['flow'].iloc[0] if 'flow' in df.columns else key
            
            if 'bytes' in df.columns:  # RX data
                total_bytes = df['bytes'].sum()
                duration = df['time'].max() - df['time'].min() if len(df) > 1 else 0
                avg_throughput = (total_bytes * 8) / (duration * 1e6) if duration > 0 else 0
                packets = len(df)
                
                # Tính throughput theo cửa sổ trượt 5 giây
                df_windowed = df.copy()
                window_size = 5.0
                df_windowed['time_window'] = (df_windowed['time'] // window_size) * window_size
                windowed_stats = df_windowed.groupby('time_window')['bytes'].sum()
                windowed_throughput = (windowed_stats * 8) / (window_size * 1e6)
                
                self.stats[key] = {
                    'flow_name': flow_name,
                    'total_bytes': total_bytes,
                    'total_mb': total_bytes / 1e6,
                    'duration': duration,
                    'avg_throughput': avg_throughput,
                    'packets': packets,
                    'start_time': df['time'].min(),
                    'end_time': df['time'].max(),
                    'windowed_throughput': windowed_throughput,
                    'max_instant_throughput': df['instant_throughput'].max() if 'instant_throughput' in df else 0,
                    'min_instant_throughput': df['instant_throughput'].min() if 'instant_throughput' in df else 0,
                    'std_throughput': df['instant_throughput'].std() if 'instant_throughput' in df else 0
                }
                
            elif 'cwnd' in df.columns:  # CWND data
                max_cwnd = df['cwnd'].max()
                min_cwnd = df['cwnd'].min()
                avg_cwnd = df['cwnd'].mean()
                std_cwnd = df['cwnd'].std()
                
                # Tính biến động CWND
                df['cwnd_change'] = df['cwnd'].diff()
                increases = (df['cwnd_change'] > 0).sum()
                decreases = (df['cwnd_change'] < 0).sum()
                
                self.stats[key] = {
                    'flow_name': flow_name,
                    'max_cwnd': max_cwnd,
                    'min_cwnd': min_cwnd,
                    'avg_cwnd': avg_cwnd,
                    'std_cwnd': std_cwnd,
                    'max_cwnd_kb': max_cwnd / 1024,
                    'min_cwnd_kb': min_cwnd / 1024,
                    'avg_cwnd_kb': avg_cwnd / 1024,
                    'cwnd_increases': increases,
                    'cwnd_decreases': decreases,
                    'cwnd_stability': 1 - (std_cwnd / avg_cwnd) if avg_cwnd > 0 else 0
                }
        
        print("✅ Hoàn thành tính toán thống kê")
    
    def create_comprehensive_plots(self):
        """Tạo các biểu đồ phân tích đầy đủ"""
        print("🎨 Đang tạo biểu đồ phân tích đầy đủ...")
        
        # Figure 1: Throughput Analysis (2x2)
        fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig1.suptitle('📈 Phân Tích Throughput Chi Tiết', fontsize=16, fontweight='bold')
        
        # 1.1: Throughput tích lũy theo thời gian
        if not self.data['newreno_rx'].empty:
            ax1.plot(self.data['newreno_rx']['time'].values, self.data['newreno_rx']['throughput_mbps'].values, 
                    'g-', label='TCP NewReno', linewidth=2.5, alpha=0.8)
        if not self.data['reno_rx'].empty:
            ax1.plot(self.data['reno_rx']['time'].values, self.data['reno_rx']['throughput_mbps'].values, 
                    'r-', label='TCP Reno', linewidth=2.5, alpha=0.8)
        
        ax1.set_xlabel('Thời gian (giây)', fontsize=11)
        ax1.set_ylabel('Throughput tích lũy (Mbps)', fontsize=11)
        ax1.set_title('Throughput Tích Lũy Theo Thời Gian', fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 1.2: Throughput tức thời (moving average)
        window = 50  # Cửa sổ trung bình trượt
        if not self.data['newreno_rx'].empty and len(self.data['newreno_rx']) > window:
            newreno_smooth = self.data['newreno_rx']['instant_throughput'].rolling(window=window).mean()
            ax2.plot(self.data['newreno_rx']['time'].values, newreno_smooth.values, 
                    'g-', label='TCP NewReno (MA)', linewidth=2)
        if not self.data['reno_rx'].empty and len(self.data['reno_rx']) > window:
            reno_smooth = self.data['reno_rx']['instant_throughput'].rolling(window=window).mean()
            ax2.plot(self.data['reno_rx']['time'].values, reno_smooth.values, 
                    'r-', label='TCP Reno (MA)', linewidth=2)
        
        ax2.set_xlabel('Thời gian (giây)', fontsize=11)
        ax2.set_ylabel('Throughput tức thời (Mbps)', fontsize=11)
        ax2.set_title('Throughput Tức Thời (Moving Average)', fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # 1.3: Histogram phân phối throughput
        if not self.data['newreno_rx'].empty:
            ax3.hist(self.data['newreno_rx']['instant_throughput'].values, bins=50, alpha=0.6, 
                    color='green', label='TCP NewReno', density=True)
        if not self.data['reno_rx'].empty:
            ax3.hist(self.data['reno_rx']['instant_throughput'].values, bins=50, alpha=0.6, 
                    color='red', label='TCP Reno', density=True)
        
        ax3.set_xlabel('Throughput tức thời (Mbps)', fontsize=11)
        ax3.set_ylabel('Mật độ xác suất', fontsize=11)
        ax3.set_title('Phân Phối Throughput', fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # 1.4: Boxplot so sánh throughput
        throughput_data = []
        labels = []
        if not self.data['newreno_rx'].empty:
            throughput_data.append(self.data['newreno_rx']['instant_throughput'].values)
            labels.append('NewReno')
        if not self.data['reno_rx'].empty:
            throughput_data.append(self.data['reno_rx']['instant_throughput'].values)
            labels.append('Reno')
        
        if throughput_data:
            bp = ax4.boxplot(throughput_data, labels=labels, patch_artist=True)
            colors = ['lightgreen', 'lightcoral']
            for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
                patch.set_facecolor(color)
        
        ax4.set_ylabel('Throughput tức thời (Mbps)', fontsize=11)
        ax4.set_title('So Sánh Phân Phối Throughput', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('tcp_throughput_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Đã lưu: tcp_throughput_analysis.png")
        
        # Figure 2: Congestion Window Analysis (2x2)
        fig2, ((ax5, ax6), (ax7, ax8)) = plt.subplots(2, 2, figsize=(16, 12))
        fig2.suptitle('🔧 Phân Tích Congestion Window Chi Tiết', fontsize=16, fontweight='bold')
        
        # 2.1: CWND theo thời gian
        if not self.data['newreno_cwnd'].empty:
            ax5.plot(self.data['newreno_cwnd']['time'].values, self.data['newreno_cwnd']['cwnd_kb'].values, 
                    'g-', label='TCP NewReno', linewidth=2, alpha=0.8)
        if not self.data['reno_cwnd'].empty:
            ax5.plot(self.data['reno_cwnd']['time'].values, self.data['reno_cwnd']['cwnd_kb'].values, 
                    'r-', label='TCP Reno', linewidth=2, alpha=0.8)
        
        ax5.set_xlabel('Thời gian (giây)', fontsize=11)
        ax5.set_ylabel('Congestion Window (KB)', fontsize=11)
        ax5.set_title('Biến Động CWND Theo Thời Gian', fontweight='bold')
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3)
        
        # 2.2: CWND growth rate
        if not self.data['newreno_cwnd'].empty:
            newreno_growth = self.data['newreno_cwnd']['cwnd'].diff() / self.data['newreno_cwnd']['time'].diff()
            ax6.plot(self.data['newreno_cwnd']['time'].values[1:], newreno_growth.values[1:], 
                    'g-', label='TCP NewReno', alpha=0.7)
        if not self.data['reno_cwnd'].empty:
            reno_growth = self.data['reno_cwnd']['cwnd'].diff() / self.data['reno_cwnd']['time'].diff()
            ax6.plot(self.data['reno_cwnd']['time'].values[1:], reno_growth.values[1:], 
                    'r-', label='TCP Reno', alpha=0.7)
        
        ax6.set_xlabel('Thời gian (giây)', fontsize=11)
        ax6.set_ylabel('Tốc độ thay đổi CWND (bytes/s)', fontsize=11)
        ax6.set_title('Tốc Độ Thay Đổi CWND', fontweight='bold')
        ax6.legend(fontsize=10)
        ax6.grid(True, alpha=0.3)
        
        # 2.3: CWND histogram
        if not self.data['newreno_cwnd'].empty:
            ax7.hist(self.data['newreno_cwnd']['cwnd_kb'].values, bins=30, alpha=0.6, 
                    color='green', label='TCP NewReno', density=True)
        if not self.data['reno_cwnd'].empty:
            ax7.hist(self.data['reno_cwnd']['cwnd_kb'].values, bins=30, alpha=0.6, 
                    color='red', label='TCP Reno', density=True)
        
        ax7.set_xlabel('Congestion Window (KB)', fontsize=11)
        ax7.set_ylabel('Mật độ xác suất', fontsize=11)
        ax7.set_title('Phân Phối CWND', fontweight='bold')
        ax7.legend(fontsize=10)
        ax7.grid(True, alpha=0.3)
        
        # 2.4: CWND vs Throughput correlation
        if not self.data['newreno_rx'].empty and not self.data['newreno_cwnd'].empty:
            # Interpolate để match time stamps
            common_times = np.intersect1d(
                np.round(self.data['newreno_rx']['time'].values, 1),
                np.round(self.data['newreno_cwnd']['time'].values, 1)
            )
            if len(common_times) > 10:
                rx_interp = np.interp(common_times, self.data['newreno_rx']['time'].values, 
                                    self.data['newreno_rx']['instant_throughput'].values)
                cwnd_interp = np.interp(common_times, self.data['newreno_cwnd']['time'].values, 
                                      self.data['newreno_cwnd']['cwnd_kb'].values)
                ax8.scatter(cwnd_interp, rx_interp, alpha=0.6, color='green', 
                          label='TCP NewReno', s=20)
        
        if not self.data['reno_rx'].empty and not self.data['reno_cwnd'].empty:
            common_times = np.intersect1d(
                np.round(self.data['reno_rx']['time'].values, 1),
                np.round(self.data['reno_cwnd']['time'].values, 1)
            )
            if len(common_times) > 10:
                rx_interp = np.interp(common_times, self.data['reno_rx']['time'].values, 
                                    self.data['reno_rx']['instant_throughput'].values)
                cwnd_interp = np.interp(common_times, self.data['reno_cwnd']['time'].values, 
                                      self.data['reno_cwnd']['cwnd_kb'].values)
                ax8.scatter(cwnd_interp, rx_interp, alpha=0.6, color='red', 
                          label='TCP Reno', s=20)
        
        ax8.set_xlabel('Congestion Window (KB)', fontsize=11)
        ax8.set_ylabel('Throughput tức thời (Mbps)', fontsize=11)
        ax8.set_title('Tương Quan CWND vs Throughput', fontweight='bold')
        ax8.legend(fontsize=10)
        ax8.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('tcp_cwnd_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Đã lưu: tcp_cwnd_analysis.png")
        
        # Figure 3: Network Overview & Competing Flows
        fig3, ((ax9, ax10), (ax11, ax12)) = plt.subplots(2, 2, figsize=(16, 12))
        fig3.suptitle('🌐 Phân Tích Toàn Mạng & Luồng Cạnh Tranh', fontsize=16, fontweight='bold')
        
        # 3.1: All flows throughput
        colors = ['green', 'red', 'blue', 'orange', 'purple', 'brown']
        flow_names = ['TCP NewReno', 'TCP Reno', 'Competing TCP 1', 'Competing TCP 2', 'UDP CBR 1', 'UDP CBR 2']
        data_keys = ['newreno_rx', 'reno_rx', 'comp1_rx', 'comp2_rx', 'udp1_rx', 'udp2_rx']
        
        for i, (key, color, name) in enumerate(zip(data_keys, colors, flow_names)):
            if key in self.data and not self.data[key].empty:
                if len(self.data[key]) > 50:  # Smooth data if enough points
                    smooth_throughput = self.data[key]['instant_throughput'].rolling(window=30).mean()
                    ax9.plot(self.data[key]['time'].values, smooth_throughput.values, 
                            color=color, label=name, linewidth=2, alpha=0.8)
                else:
                    ax9.plot(self.data[key]['time'].values, self.data[key]['instant_throughput'].values, 
                            color=color, label=name, linewidth=2, alpha=0.8)
        
        ax9.set_xlabel('Thời gian (giây)', fontsize=11)
        ax9.set_ylabel('Throughput tức thời (Mbps)', fontsize=11)
        ax9.set_title('Tất Cả Luồng Dữ Liệu', fontweight='bold')
        ax9.legend(fontsize=9)
        ax9.grid(True, alpha=0.3)
        
        # 3.2: Network utilization over time
        time_range = np.arange(0, 200, 1)  # 1 second intervals
        total_utilization = np.zeros_like(time_range, dtype=float)
        
        for key in data_keys:
            if key in self.data and not self.data[key].empty:
                df = self.data[key]
                for t in time_range:
                    mask = (df['time'] >= t) & (df['time'] < t + 1)
                    if mask.any():
                        total_utilization[t] += df[mask]['instant_throughput'].mean()
        
        ax10.plot(time_range, total_utilization, 'b-', linewidth=2, label='Tổng utilization')
        ax10.axhline(y=5, color='red', linestyle='--', alpha=0.7, label='WAN limit (5 Mbps)')
        ax10.fill_between(time_range, total_utilization, alpha=0.3)
        
        ax10.set_xlabel('Thời gian (giây)', fontsize=11)
        ax10.set_ylabel('Network Utilization (Mbps)', fontsize=11)
        ax10.set_title('Sử Dụng Băng Thông Mạng', fontweight='bold')
        ax10.legend(fontsize=10)
        ax10.grid(True, alpha=0.3)
        
        # 3.3: Flow comparison bar chart
        flow_stats = []
        for key in ['newreno_rx', 'reno_rx', 'comp1_rx', 'comp2_rx']:
            if key in self.stats:
                flow_stats.append({
                    'name': self.stats[key]['flow_name'],
                    'throughput': self.stats[key]['avg_throughput'],
                    'total_mb': self.stats[key]['total_mb']
                })
        
        if flow_stats:
            names = [f['name'] for f in flow_stats]
            throughputs = [f['throughput'] for f in flow_stats]
            
            bars = ax11.bar(names, throughputs, color=['green', 'red', 'blue', 'orange'][:len(names)], alpha=0.7)
            ax11.set_ylabel('Throughput trung bình (Mbps)', fontsize=11)
            ax11.set_title('So Sánh Throughput Các Luồng TCP', fontweight='bold')
            ax11.tick_params(axis='x', rotation=45)
            ax11.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, val in zip(bars, throughputs):
                ax11.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                         f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 3.4: Performance comparison radar chart
        if 'newreno_rx' in self.stats and 'reno_rx' in self.stats:
            categories = ['Throughput', 'Stability', 'Efficiency', 'CWND Size', 'Responsiveness']
            
            # Normalize metrics to 0-1 scale for radar chart
            newreno_metrics = [
                self.stats['newreno_rx']['avg_throughput'] / 2.0,  # Normalize by max expected
                1 - (self.stats['newreno_rx']['std_throughput'] / self.stats['newreno_rx']['avg_throughput']) if self.stats['newreno_rx']['avg_throughput'] > 0 else 0,
                self.stats['newreno_rx']['total_mb'] / max(self.stats['newreno_rx']['total_mb'], self.stats['reno_rx']['total_mb']),
                (self.stats['newreno_cwnd']['avg_cwnd_kb'] / 200) if 'newreno_cwnd' in self.stats else 0.5,  # Normalize by typical max
                0.8  # Assumed based on NewReno characteristics
            ]
            
            reno_metrics = [
                self.stats['reno_rx']['avg_throughput'] / 2.0,
                1 - (self.stats['reno_rx']['std_throughput'] / self.stats['reno_rx']['avg_throughput']) if self.stats['reno_rx']['avg_throughput'] > 0 else 0,
                self.stats['reno_rx']['total_mb'] / max(self.stats['newreno_rx']['total_mb'], self.stats['reno_rx']['total_mb']),
                (self.stats['reno_cwnd']['avg_cwnd_kb'] / 200) if 'reno_cwnd' in self.stats else 0.4,
                0.6  # Assumed based on Reno characteristics
            ]
            
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]  # Complete the circle
            
            newreno_metrics += newreno_metrics[:1]
            reno_metrics += reno_metrics[:1]
            
            ax12 = plt.subplot(2, 2, 4, projection='polar')
            ax12.plot(angles, newreno_metrics, 'g-', linewidth=2, label='TCP NewReno')
            ax12.fill(angles, newreno_metrics, alpha=0.25, color='green')
            ax12.plot(angles, reno_metrics, 'r-', linewidth=2, label='TCP Reno')
            ax12.fill(angles, reno_metrics, alpha=0.25, color='red')
            
            ax12.set_xticks(angles[:-1])
            ax12.set_xticklabels(categories, fontsize=10)
            ax12.set_ylim(0, 1)
            ax12.set_title('So Sánh Hiệu Suất Tổng Thể', fontweight='bold', pad=20)
            ax12.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.savefig('tcp_network_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Đã lưu: tcp_network_analysis.png")
    
    def generate_detailed_report(self):
        """Tạo báo cáo chi tiết"""
        print("📝 Đang tạo báo cáo chi tiết...")
        
        report = []
        report.append("="*80)
        report.append("           BÁO CÁO PHÂN TÍCH CHI TIẾT TCP NEWRENO VS TCP RENO")
        report.append("="*80)
        report.append(f"Thời gian tạo báo cáo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("📋 TÓM TẮT ĐIỀU HÀNH")
        report.append("-" * 40)
        if 'newreno_rx' in self.stats and 'reno_rx' in self.stats:
            newreno_perf = self.stats['newreno_rx']['avg_throughput']
            reno_perf = self.stats['reno_rx']['avg_throughput']
            improvement = ((newreno_perf - reno_perf) / reno_perf * 100) if reno_perf > 0 else 0
            
            report.append(f"• TCP NewReno cho hiệu suất {improvement:.1f}% tốt hơn TCP Reno")
            report.append(f"• Throughput trung bình: NewReno {newreno_perf:.2f} Mbps vs Reno {reno_perf:.2f} Mbps")
            report.append(f"• Tổng dữ liệu truyền: NewReno {self.stats['newreno_rx']['total_mb']:.1f} MB vs Reno {self.stats['reno_rx']['total_mb']:.1f} MB")
            
            if 'newreno_cwnd' in self.stats and 'reno_cwnd' in self.stats:
                cwnd_improvement = ((self.stats['newreno_cwnd']['avg_cwnd'] - self.stats['reno_cwnd']['avg_cwnd']) / self.stats['reno_cwnd']['avg_cwnd'] * 100)
                report.append(f"• CWND trung bình: NewReno {self.stats['newreno_cwnd']['avg_cwnd_kb']:.0f} KB vs Reno {self.stats['reno_cwnd']['avg_cwnd_kb']:.0f} KB ({cwnd_improvement:+.1f}%)")
        
        report.append("")
        
        # Detailed Analysis
        report.append("🔍 PHÂN TÍCH CHI TIẾT")
        report.append("-" * 40)
        
        for key, stats in self.stats.items():
            if 'flow_name' not in stats:
                continue
                
            report.append(f"\n🔸 {stats['flow_name'].upper()}")
            report.append("  " + "─" * 30)
            
            if 'avg_throughput' in stats:  # RX data
                report.append(f"  📊 Throughput:")
                report.append(f"     • Trung bình: {stats['avg_throughput']:.3f} Mbps")
                report.append(f"     • Tối đa: {stats.get('max_instant_throughput', 0):.3f} Mbps")
                report.append(f"     • Tối thiểu: {stats.get('min_instant_throughput', 0):.3f} Mbps")
                report.append(f"     • Độ lệch chuẩn: {stats.get('std_throughput', 0):.3f} Mbps")
                
                report.append(f"  📦 Dữ liệu:")
                report.append(f"     • Tổng bytes: {stats['total_bytes']:,} bytes ({stats['total_mb']:.2f} MB)")
                report.append(f"     • Số gói tin: {stats['packets']:,}")
                report.append(f"     • Thời gian hoạt động: {stats['duration']:.1f} giây ({stats['start_time']:.1f}s → {stats['end_time']:.1f}s)")
                
                # Calculate efficiency
                efficiency = (stats['avg_throughput'] / 5.0) * 100  # Assuming 5 Mbps WAN
                report.append(f"     • Hiệu suất sử dụng WAN: {efficiency:.1f}%")
                
            elif 'avg_cwnd' in stats:  # CWND data
                report.append(f"  🔧 Congestion Window:")
                report.append(f"     • Trung bình: {stats['avg_cwnd']:.0f} bytes ({stats['avg_cwnd_kb']:.1f} KB)")
                report.append(f"     • Tối đa: {stats['max_cwnd']:,} bytes ({stats['max_cwnd_kb']:.1f} KB)")
                report.append(f"     • Tối thiểu: {stats['min_cwnd']:,} bytes ({stats['min_cwnd_kb']:.1f} KB)")
                report.append(f"     • Độ lệch chuẩn: {stats['std_cwnd']:.0f} bytes")
                report.append(f"     • Tăng/Giảm: {stats['cwnd_increases']}/{stats['cwnd_decreases']} lần")
                report.append(f"     • Độ ổn định: {stats['cwnd_stability']:.3f} (0-1)")
        
        # Network Analysis
        report.append("\n🌐 PHÂN TÍCH MẠNG TỔNG THỂ")
        report.append("-" * 40)
        
        # Calculate total network utilization
        total_throughput = sum(stats.get('avg_throughput', 0) for stats in self.stats.values() if 'avg_throughput' in stats)
        wan_utilization = (total_throughput / 5.0) * 100
        
        report.append(f"• Tổng throughput mạng: {total_throughput:.2f} Mbps")
        report.append(f"• Sử dụng băng thông WAN: {wan_utilization:.1f}% (5 Mbps)")
        report.append(f"• Trạng thái mạng: {'Quá tải' if wan_utilization > 100 else 'Bình thường' if wan_utilization > 80 else 'Tối ưu'}")
        
        # Recommendations
        report.append("\n💡 KHUYẾN NGHỊ")
        report.append("-" * 40)
        
        if 'newreno_rx' in self.stats and 'reno_rx' in self.stats:
            newreno_perf = self.stats['newreno_rx']['avg_throughput']
            reno_perf = self.stats['reno_rx']['avg_throughput']
            
            if newreno_perf > reno_perf * 1.1:
                report.append("✅ TCP NewReno cho hiệu suất vượt trội so với TCP Reno")
                report.append("   → Khuyến nghị sử dụng TCP NewReno cho các ứng dụng quan trọng")
            elif abs(newreno_perf - reno_perf) < 0.1:
                report.append("⚖️ Hiệu suất TCP NewReno và TCP Reno tương đương")
                report.append("   → Lựa chọn tùy thuộc vào yêu cầu cụ thể")
            
            if wan_utilization > 100:
                report.append("⚠️ Mạng đang quá tải")
                report.append("   → Cần tối ưu hóa traffic hoặc nâng cấp băng thông")
            
            if 'newreno_cwnd' in self.stats and 'reno_cwnd' in self.stats:
                if self.stats['newreno_cwnd']['cwnd_stability'] > self.stats['reno_cwnd']['cwnd_stability']:
                    report.append("📈 TCP NewReno có CWND ổn định hơn")
                    report.append("   → Phù hợp cho môi trường mạng có độ trễ cao")
        
        report.append("\n" + "="*80)
        report.append("HẾT BÁO CÁO")
        report.append("="*80)
        
        # Save report
        with open('tcp_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print("✅ Đã lưu báo cáo: tcp_analysis_report.txt")
        
        # Print summary to console
        print("\n" + "="*60)
        print("📋 TÓM TẮT KẾT QUẢ PHÂN TÍCH")
        print("="*60)
        for line in report[6:20]:  # Print summary section
            print(line)
        print("="*60)
    
    def run_full_analysis(self):
        """Chạy phân tích đầy đủ"""
        print("🚀 Bắt đầu phân tích đầy đủ TCP NewReno vs TCP Reno")
        print("="*60)
        
        self.load_all_data()
        self.calculate_statistics()
        self.create_comprehensive_plots()
        self.generate_detailed_report()
        
        print("\n🎉 HOÀN THÀNH PHÂN TÍCH ĐẦY ĐỦ!")
        print("📁 Các file được tạo:")
        print("   • tcp_throughput_analysis.png - Phân tích throughput")
        print("   • tcp_cwnd_analysis.png - Phân tích congestion window")
        print("   • tcp_network_analysis.png - Phân tích mạng tổng thể")
        print("   • tcp_analysis_report.txt - Báo cáo chi tiết")
        print("="*60)

if __name__ == "__main__":
    analyzer = TCPAnalyzer()
    analyzer.run_full_analysis() 
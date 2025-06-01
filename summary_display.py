#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script hiển thị tóm tắt kết quả phân tích TCP
"""

def print_colorful_summary():
    """In tóm tắt kết quả với màu sắc"""
    
    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{WHITE}           🚀 KẾT QUẢ PHÂN TÍCH TCP NEWRENO vs TCP RENO 🚀{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")
    
    # Hiệu suất tổng thể
    print(f"{BOLD}{BLUE}📊 HIỆU SUẤT TỔNG THỂ{RESET}")
    print(f"{CYAN}{'─'*40}{RESET}")
    print(f"🏆 {GREEN}TCP NewReno thắng với khoảng cách lớn!{RESET}")
    print(f"📈 Hiệu suất tốt hơn: {BOLD}{GREEN}+74.0%{RESET}")
    print(f"🎯 Throughput: {GREEN}1.03 Mbps{RESET} vs {RED}0.59 Mbps{RESET}")
    print(f"💾 Dữ liệu truyền: {GREEN}24.5 MB{RESET} vs {RED}6.0 MB{RESET}")
    print(f"🔧 CWND trung bình: {GREEN}53 KB{RESET} vs {RED}41 KB{RESET} ({GREEN}+26.8%{RESET})")
    
    print(f"\n{BOLD}{MAGENTA}🔍 CHI TIẾT SO SÁNH{RESET}")
    print(f"{CYAN}{'─'*40}{RESET}")
    
    # Bảng so sánh
    headers = ["Metric", "TCP NewReno", "TCP Reno", "Chênh lệch"]
    
    data = [
        ["Throughput TB", "1.035 Mbps", "0.595 Mbps", "+74.0%"],
        ["Dữ liệu tổng", "24.48 MB", "5.97 MB", "+310.0%"],
        ["CWND TB", "52.5 KB", "41.4 KB", "+26.8%"],
        ["CWND tối đa", "138.8 KB", "72.1 KB", "+92.5%"],
        ["Độ ổn định CWND", "0.496", "0.706", "-29.7%"],
        ["Thời gian hoạt động", "189.2s", "80.3s", "+135.8%"],
        ["Số gói tin", "16,764", "3,265", "+413.6%"],
        ["Hiệu quả WAN", "20.7%", "11.9%", "+74.0%"]
    ]
    
    # In header
    print(f"{BOLD}{WHITE}┌{'─'*20}┬{'─'*15}┬{'─'*15}┬{'─'*15}┐{RESET}")
    print(f"{BOLD}{WHITE}│{headers[0]:^20}│{headers[1]:^15}│{headers[2]:^15}│{headers[3]:^15}│{RESET}")
    print(f"{BOLD}{WHITE}├{'─'*20}┼{'─'*15}┼{'─'*15}┼{'─'*15}┤{RESET}")
    
    # In data rows
    for row in data:
        metric, newreno, reno, diff = row
        diff_color = GREEN if diff.startswith('+') else RED if diff.startswith('-') else WHITE
        print(f"│{YELLOW}{metric:<20}{RESET}│{GREEN}{newreno:^15}{RESET}│{RED}{reno:^15}{RESET}│{diff_color}{diff:^15}{RESET}│")
    
    print(f"{BOLD}{WHITE}└{'─'*20}┴{'─'*15}┴{'─'*15}┴{'─'*15}┘{RESET}")
    
    # Phân tích luồng cạnh tranh
    print(f"\n{BOLD}{YELLOW}🌐 LUỒNG CẠNH TRANH & MẠNG{RESET}")
    print(f"{CYAN}{'─'*40}{RESET}")
    print(f"🔗 Competing TCP 1: {BLUE}0.766 Mbps{RESET} (15.3% WAN)")
    print(f"🔗 Competing TCP 2: {BLUE}0.569 Mbps{RESET} (11.4% WAN)")
    print(f"📡 UDP CBR 1: {MAGENTA}0.967 Mbps{RESET} (19.3% WAN)")
    print(f"📡 UDP CBR 2: {MAGENTA}1.277 Mbps{RESET} (25.5% WAN)")
    print(f"🌍 Tổng utilization: {RED}{BOLD}104.2%{RESET} (Quá tải!)")
    
    # Khuyến nghị
    print(f"\n{BOLD}{GREEN}💡 KHUYẾN NGHỊ{RESET}")
    print(f"{CYAN}{'─'*40}{RESET}")
    print(f"✅ {GREEN}Sử dụng TCP NewReno cho các ứng dụng quan trọng{RESET}")
    print(f"📈 {GREEN}NewReno có hiệu suất và throughput vượt trội{RESET}")
    print(f"🔧 {GREEN}NewReno có CWND cao hơn, phù hợp với mạng có băng thông cao{RESET}")
    print(f"⚠️  {RED}Tuy nhiên TCP Reno có độ ổn định CWND tốt hơn{RESET}")
    print(f"🌐 {YELLOW}Cần tối ưu hóa traffic vì mạng đang quá tải (>100%){RESET}")
    
    # Thống kê thú vị
    print(f"\n{BOLD}{MAGENTA}🎲 THỐNG KÊ THÚ VỊ{RESET}")
    print(f"{CYAN}{'─'*40}{RESET}")
    print(f"🏃 NewReno chạy gần gấp {BOLD}2.5 lần{RESET} lâu hơn Reno")
    print(f"📦 NewReno truyền gấp {BOLD}4.1 lần{RESET} nhiều gói tin hơn")
    print(f"🎯 NewReno đạt CWND tối đa gần gấp {BOLD}đôi{RESET} Reno")
    print(f"⚡ Reno có độ dao động CWND thấp hơn (ổn định hơn)")
    print(f"🌊 NewReno 'ăn' băng thông nhiều hơn nhưng hiệu quả hơn")
    
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{WHITE}           📁 CÁC FILE ĐÃ TẠO{RESET}")
    print(f"{CYAN}{'─'*80}{RESET}")
    print(f"📊 {GREEN}tcp_throughput_analysis.png{RESET} - Phân tích throughput chi tiết")
    print(f"🔧 {GREEN}tcp_cwnd_analysis.png{RESET} - Phân tích congestion window")
    print(f"🌐 {GREEN}tcp_network_analysis.png{RESET} - Phân tích mạng tổng thể")
    print(f"📄 {GREEN}tcp_analysis_report.txt{RESET} - Báo cáo chi tiết đầy đủ")
    print(f"📈 {GREEN}tcp_comparison.png{RESET} - So sánh cơ bản")
    print(f"📊 {GREEN}tcp_summary.png{RESET} - Tóm tắt bằng biểu đồ")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")

if __name__ == "__main__":
    print_colorful_summary() 
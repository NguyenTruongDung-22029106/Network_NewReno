#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/csma-module.h"
#include "ns3/bridge-module.h"
#include "ns3/traffic-control-module.h"
#include "ns3/flow-monitor-module.h"

#include <vector> // Để sử dụng std::vector
#include <iomanip> // Để sử dụng std::setprecision

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("EnterpriseNetworkNewReno");

// --- HÀM TRỢ GIÚP ---
// Callback để theo dõi Cwnd của luồng TCP NewReno chính
static void
CwndChangeTracer(Ptr<OutputStreamWrapper> stream, uint32_t oldCwnd, uint32_t newCwnd)
{
    *stream->GetStream() << Simulator::Now().GetSeconds() << "\t" << newCwnd << std::endl;
}

// Callback để theo dõi throughput (đơn giản hơn) - file tổng hợp
static void
RxTraceSimple(std::string context, Ptr<const Packet> packet, const Address &from)
{
    static Ptr<OutputStreamWrapper> rxStream = nullptr;
    if (!rxStream) {
        AsciiTraceHelper ascii;
        rxStream = ascii.CreateFileStream("scratch/enterprise-all-rx.data");
    }
    
    *rxStream->GetStream() << Simulator::Now().GetSeconds() << "\t" 
                          << packet->GetSize() << "\t" 
                          << context << std::endl;
}

// Callback để theo dõi throughput (ghi vào file riêng từng flow)
static void
RxTraceToStream(Ptr<OutputStreamWrapper> stream, Ptr<const Packet> packet, const Address &from)
{
    *stream->GetStream() << Simulator::Now().GetSeconds() << "\t" << packet->GetSize() << std::endl;
}

// Hàm giúp tạo kết nối TCP (STATIC BỎ ĐI NẾU CÓ VẤN ĐỀ VỀ LINKING, nhưng để lại cũng không sao)
void // Bỏ static nếu có lỗi linking
SetupTcpConnection(Ptr<Node> sourceNode, Ptr<Node> sinkNode,
                   Ipv4Address sinkIp, uint16_t sinkPort,
                   double startTime, double stopTime,
                   std::string tcpVariant,
                   Ptr<OutputStreamWrapper> cwndStream = nullptr,
                   Ptr<OutputStreamWrapper> rxStream = nullptr,
                   uint32_t maxBytes = 0)
{
    Address dest(InetSocketAddress(sinkIp, sinkPort));
    PacketSinkHelper sinkHelper("ns3::TcpSocketFactory", InetSocketAddress(Ipv4Address::GetAny(), sinkPort));
    ApplicationContainer sinkApp = sinkHelper.Install(sinkNode);
    sinkApp.Start(Seconds(startTime - 0.1));
    sinkApp.Stop(Seconds(stopTime + 1.0));

    BulkSendHelper sourceHelper("ns3::TcpSocketFactory", dest);
    if (maxBytes > 0) {
        sourceHelper.SetAttribute("MaxBytes", UintegerValue(maxBytes));
    } else {
        sourceHelper.SetAttribute("SendSize", UintegerValue(1024));
        sourceHelper.SetAttribute("MaxBytes", UintegerValue(0));
    }

    ApplicationContainer sourceApp = sourceHelper.Install(sourceNode);
    sourceApp.Start(Seconds(startTime));
    sourceApp.Stop(Seconds(stopTime));

    // Connect traces after a delay to ensure applications are created
    Simulator::Schedule(Seconds(startTime + 0.05), [sinkApp, sourceApp, cwndStream, rxStream, tcpVariant]() {
        // Gắn trace RX vào file riêng nếu có truyền vào
        if (rxStream) {
            Ptr<PacketSink> sink = DynamicCast<PacketSink>(sinkApp.Get(0));
            if (sink) {
                sink->TraceConnectWithoutContext("Rx", MakeBoundCallback(&RxTraceToStream, rxStream));
                NS_LOG_INFO("RX trace connected for flow");
            } else {
                NS_LOG_WARN("Could not get PacketSink from application");
            }
        }

        // Connect Cwnd trace
        if (cwndStream && tcpVariant == "ns3::TcpNewReno")
        {
            Ptr<Application> app = sourceApp.Get(0);
            Ptr<BulkSendApplication> bsa = DynamicCast<BulkSendApplication>(app);
            if (bsa)
            {
                Ptr<Socket> tcpSocket = bsa->GetSocket();
                if (tcpSocket)
                {
                    tcpSocket->TraceConnectWithoutContext("CongestionWindow", MakeBoundCallback(&CwndChangeTracer, cwndStream));
                    NS_LOG_INFO("Cwnd trace connected for NewReno flow");
                }
                else
                {
                    NS_LOG_WARN("Could not get TCP socket from BulkSendApplication");
                }
            }
        }
    });
}

// Hàm giúp tạo kết nối UDP CBR (STATIC BỎ ĐI NẾU CÓ VẤN ĐỀ VỀ LINKING)
void // Bỏ static nếu có lỗi linking
SetupUdpCbrConnection(Ptr<Node> sourceNode, Ptr<Node> sinkNode,
                      Ipv4Address sinkIp, uint16_t sinkPort,
                      double startTime, double stopTime,
                      std::string dataRate, uint32_t packetSize = 1024,
                      Ptr<OutputStreamWrapper> rxStream = nullptr)
{
    Address dest(InetSocketAddress(sinkIp, sinkPort));
    PacketSinkHelper sinkHelper("ns3::UdpSocketFactory", InetSocketAddress(Ipv4Address::GetAny(), sinkPort));
    ApplicationContainer sinkApp = sinkHelper.Install(sinkNode);
    sinkApp.Start(Seconds(startTime - 0.1));
    sinkApp.Stop(Seconds(stopTime + 1.0));

    OnOffHelper sourceHelper("ns3::UdpSocketFactory", dest);
    sourceHelper.SetConstantRate(DataRate(dataRate), packetSize);

    ApplicationContainer sourceApp = sourceHelper.Install(sourceNode);
    sourceApp.Start(Seconds(startTime));
    sourceApp.Stop(Seconds(stopTime));

    // Gắn trace RX sau khi application được tạo
    if (rxStream) {
        Simulator::Schedule(Seconds(startTime + 0.05), [sinkApp, rxStream]() {
            Ptr<PacketSink> sink = DynamicCast<PacketSink>(sinkApp.Get(0));
            if (sink) {
                sink->TraceConnectWithoutContext("Rx", MakeBoundCallback(&RxTraceToStream, rxStream));
                NS_LOG_INFO("UDP RX trace connected for flow");
            } else {
                NS_LOG_WARN("Could not get UDP PacketSink from application");
            }
        });
    }
}


int
main(int argc, char* argv[])
{
    // --- Parameters ---
    LogComponentEnable("EnterpriseNetworkNewReno", LOG_LEVEL_INFO);

    double simulationTime = 200.0;
    uint32_t nClientsA = 5;
    uint32_t nServersB = 3;
    std::string lanDataRate = "100Mbps";
    std::string lanDelay = "2ms";
    std::string wanDataRate = "5Mbps";
    std::string wanDelay = "30ms";
    std::string wanQueueSize = "30p";

    double mainTcpStartTime = 1.0;
    double mainTcpStopTime = simulationTime - 10.0;
    double competingTcp1StartTime = 20.0;
    double competingTcp1StopTime = 180.0;
    double competingTcp2StartTime = 40.0;
    double competingTcp2StopTime = 160.0;
    double renoTcpStartTime = 0; // 60.0 to enable
    double renoTcpStopTime = 0;  // 140.0 to enable
    double udp1StartTime = 30.0;
    double udp1StopTime = 90.0;
    std::string udp1DataRate = "1Mbps";
    double udp2StartTime = 100.0;
    double udp2StopTime = 170.0;
    std::string udp2DataRate = "1.5Mbps";

    // --- Node Creation ---
    NS_LOG_INFO("Creating nodes...");
    NodeContainer clientsA;
    clientsA.Create(nClientsA);
    NodeContainer serversB;
    serversB.Create(nServersB);
    NodeContainer routers;
    routers.Create(2);
    Ptr<Node> routerLanA = routers.Get(0);
    Ptr<Node> routerWanB = routers.Get(1);
    NodeContainer switches;
    switches.Create(2);
    Ptr<Node> switchLanA = switches.Get(0);
    Ptr<Node> switchLanB = switches.Get(1);

    // --- Install Internet Stack ---
    NS_LOG_INFO("Installing internet stack...");
    InternetStackHelper stack;
    stack.Install(clientsA);
    stack.Install(serversB);
    stack.Install(routers);
    stack.Install(switches);
    
    // --- Configure TCP after stack installation ---
    Config::SetDefault("ns3::TcpL4Protocol::SocketType", StringValue("ns3::TcpNewReno"));
    Config::SetDefault("ns3::TcpSocket::SegmentSize", UintegerValue(1448));
    Config::SetDefault("ns3::TcpSocket::InitialCwnd", UintegerValue(10));
    Config::SetDefault("ns3::TcpSocketBase::Sack", BooleanValue(true));
    Config::SetDefault("ns3::TcpSocketBase::WindowScaling", BooleanValue(true));
    Config::SetDefault("ns3::TcpSocketBase::Timestamp", BooleanValue(true));
    Config::SetDefault("ns3::TcpSocket::RcvBufSize", UintegerValue(131072));
    Config::SetDefault("ns3::TcpSocket::SndBufSize", UintegerValue(131072));

    // --- Network Device and Channel Configuration ---
    NS_LOG_INFO("Configuring network links...");
    
    // LAN configuration using CSMA
    CsmaHelper csma;
    csma.SetChannelAttribute("DataRate", StringValue(lanDataRate));
    csma.SetChannelAttribute("Delay", StringValue(lanDelay));
    csma.SetQueue("ns3::DropTailQueue", "MaxSize", StringValue("100p"));

    // WAN configuration using PointToPoint
    PointToPointHelper p2pWan;
    p2pWan.SetDeviceAttribute("DataRate", StringValue(wanDataRate));
    p2pWan.SetChannelAttribute("Delay", StringValue(wanDelay));
    p2pWan.SetQueue("ns3::DropTailQueue", "MaxSize", StringValue(wanQueueSize));

    // Sử dụng std::vector thay cho VLA
    std::vector<NetDeviceContainer> clientToSwitchADevs(nClientsA);
    NetDeviceContainer switchAToRouterADev;

    // Install devices on LAN A
    for (uint32_t i = 0; i < nClientsA; ++i) {
        NodeContainer tempNodes;
        tempNodes.Add(clientsA.Get(i));
        tempNodes.Add(switchLanA);
        clientToSwitchADevs[i] = csma.Install(tempNodes);
    }
    
    NodeContainer switchRouterA;
    switchRouterA.Add(switchLanA);
    switchRouterA.Add(routerLanA);
    switchAToRouterADev = csma.Install(switchRouterA);

    // WAN link
    NetDeviceContainer wanLinkDevs = p2pWan.Install(routerLanA, routerWanB);

    // Install devices on LAN B
    NodeContainer routerSwitchB;
    routerSwitchB.Add(routerWanB);
    routerSwitchB.Add(switchLanB);
    NetDeviceContainer routerBToSwitchBDev = csma.Install(routerSwitchB);

    std::vector<NetDeviceContainer> switchToServerBDevs(nServersB);
    for (uint32_t i = 0; i < nServersB; ++i) {
        NodeContainer tempNodes;
        tempNodes.Add(switchLanB);
        tempNodes.Add(serversB.Get(i));
        switchToServerBDevs[i] = csma.Install(tempNodes);
    }

    // --- IP Addressing ---
    NS_LOG_INFO("Assigning IP addresses...");
    Ipv4AddressHelper ipv4;

    // Thay vì lưu trữ Ipv4InterfaceContainer, chúng ta sẽ lưu trực tiếp địa chỉ IP cần thiết.
    // Hoặc, nếu bạn thực sự cần Ipv4InterfaceContainer cho mục đích khác,
    // bạn cần khởi tạo chúng đúng cách. Hiện tại, chúng ta chỉ cần địa chỉ.
    std::vector<Ipv4Address> clientAIpAddrs(nClientsA);
    // std::vector<Ipv4Address> switchALanIpAddrs(nClientsA); // Địa chỉ trên switch ít quan trọng hơn trừ khi routing

    Ipv4Address routerASwitchIpAddr;
    Ipv4Address routerAWanIpAddr;
    Ipv4Address routerBWanIpAddr;
    Ipv4Address routerBSwitchIpAddr;
    std::vector<Ipv4Address> serverBIpAddrs(nServersB);


    // LAN A subnets (client i to switch A)
    for (uint32_t i = 0; i < nClientsA; ++i) {
        std::ostringstream subnet;
        subnet << "10.1." << i + 1 << ".0";
        ipv4.SetBase(subnet.str().c_str(), "255.255.255.0");
        Ipv4InterfaceContainer tempIfaces = ipv4.Assign(clientToSwitchADevs[i]);
        clientAIpAddrs[i] = tempIfaces.GetAddress(0); // client interface is 0
        // switchALanIpAddrs[i] = tempIfaces.GetAddress(1); // switch interface is 1
    }

    // LAN A subnet (switch A to router A)
    ipv4.SetBase("10.1.100.0", "255.255.255.0");
    Ipv4InterfaceContainer tempIfacesSAR = ipv4.Assign(switchAToRouterADev);
    // switchARouterIpAddr = tempIfacesSAR.GetAddress(0); // switch interface
    routerASwitchIpAddr = tempIfacesSAR.GetAddress(1); // router interface

    // WAN subnet
    ipv4.SetBase("10.2.1.0", "255.255.255.0");
    Ipv4InterfaceContainer tempIfacesWAN = ipv4.Assign(wanLinkDevs);
    routerAWanIpAddr = tempIfacesWAN.GetAddress(0);
    routerBWanIpAddr = tempIfacesWAN.GetAddress(1);

    // LAN B subnet (router B to switch B)
    ipv4.SetBase("10.3.100.0", "255.255.255.0");
    Ipv4InterfaceContainer tempIfacesRBSB = ipv4.Assign(routerBToSwitchBDev);
    routerBSwitchIpAddr = tempIfacesRBSB.GetAddress(0); // router interface
    // switchBRouterIpAddr = tempIfacesRBSB.GetAddress(1); // switch interface

    // LAN B subnets (switch B to server j)
    for (uint32_t i = 0; i < nServersB; ++i) {
        std::ostringstream subnet;
        subnet << "10.3." << i + 1 << ".0";
        ipv4.SetBase(subnet.str().c_str(), "255.255.255.0");
        Ipv4InterfaceContainer tempIfaces = ipv4.Assign(switchToServerBDevs[i]);
        // switchBServerIpAddrs[i] = tempIfaces.GetAddress(0); // switch interface
        serverBIpAddrs[i] = tempIfaces.GetAddress(1); // server interface
    }

    // --- Populate Routing Tables ---
    NS_LOG_INFO("Populating routing tables...");
    Ipv4GlobalRoutingHelper::PopulateRoutingTables();


    // --- Application Setup ---
    NS_LOG_INFO("Setting up applications...");
    uint16_t baseTcpPort = 9000;
    uint16_t baseUdpPort = 10000;

    AsciiTraceHelper ascii;
    Ptr<OutputStreamWrapper> mainCwndStream = ascii.CreateFileStream("scratch/enterprise-main-newreno-cwnd.data");
    Ptr<OutputStreamWrapper> mainRxStream = ascii.CreateFileStream("scratch/enterprise-main-newreno-rx.data");

    // Main TCP flow
    SetupTcpConnection(clientsA.Get(0), serversB.Get(0),
                       serverBIpAddrs[0], baseTcpPort,
                       mainTcpStartTime, mainTcpStopTime,
                       "ns3::TcpNewReno", mainCwndStream, mainRxStream);
    baseTcpPort++;

    // Competing TCP flows
    Ptr<OutputStreamWrapper> comp1CwndStream = ascii.CreateFileStream("scratch/enterprise-comp1-newreno-cwnd.data");
    Ptr<OutputStreamWrapper> comp1RxStream = ascii.CreateFileStream("scratch/enterprise-comp1-newreno-rx.data");
    
    SetupTcpConnection(clientsA.Get(1), serversB.Get(1 % nServersB),
                       serverBIpAddrs[1 % nServersB], baseTcpPort,
                       competingTcp1StartTime, competingTcp1StopTime,
                       "ns3::TcpNewReno", comp1CwndStream, comp1RxStream);
    baseTcpPort++;

    if (nClientsA > 2) {
        Ptr<OutputStreamWrapper> comp2CwndStream = ascii.CreateFileStream("scratch/enterprise-comp2-newreno-cwnd.data");
        Ptr<OutputStreamWrapper> comp2RxStream = ascii.CreateFileStream("scratch/enterprise-comp2-newreno-rx.data");
        
        SetupTcpConnection(clientsA.Get(2), serversB.Get(2 % nServersB),
                           serverBIpAddrs[2 % nServersB], baseTcpPort,
                           competingTcp2StartTime, competingTcp2StopTime,
                           "ns3::TcpNewReno", comp2CwndStream, comp2RxStream);
        baseTcpPort++;
    }

    if (renoTcpStartTime > 0 && nClientsA > 3) {
         NS_LOG_INFO("Setting up TCP Reno flow");
         Ptr<OutputStreamWrapper> renoCwndStream = ascii.CreateFileStream("scratch/enterprise-reno-cwnd.data");
         Ptr<OutputStreamWrapper> renoRxStream = ascii.CreateFileStream("scratch/enterprise-reno-rx.data");
         
         SetupTcpConnection(clientsA.Get(3), serversB.Get(0),
                            serverBIpAddrs[0], baseTcpPort,
                            renoTcpStartTime, renoTcpStopTime,
                            "ns3::TcpReno", renoCwndStream, renoRxStream);
         baseTcpPort++;
    }

    // UDP flows
    if (nClientsA > 0 && nServersB > 0) {
        Ptr<OutputStreamWrapper> udp1RxStream = ascii.CreateFileStream("scratch/enterprise-udp1-rx.data");
        SetupUdpCbrConnection(clientsA.Get(nClientsA - 1), serversB.Get(nServersB - 1),
                              serverBIpAddrs[nServersB - 1], baseUdpPort,
                              udp1StartTime, udp1StopTime, udp1DataRate, 1024, udp1RxStream);
        baseUdpPort++;
    }

    if (nClientsA > 1 && nServersB > 1) {
        Ptr<OutputStreamWrapper> udp2RxStream = ascii.CreateFileStream("scratch/enterprise-udp2-rx.data");
        SetupUdpCbrConnection(clientsA.Get(nClientsA - 2), serversB.Get(nServersB - 2),
                              serverBIpAddrs[nServersB - 2], baseUdpPort,
                              udp2StartTime, udp2StopTime, udp2DataRate, 1024, udp2RxStream);
    }

    // Connect simple packet traces for all PacketSink applications
    Config::Connect("/NodeList/*/ApplicationList/*/$ns3::PacketSink/Rx", 
                   MakeCallback(&RxTraceSimple));

    // Reduce logging verbosity - only enable essential logging
    LogComponentEnable("TcpSocketBase", LOG_LEVEL_WARN);
    LogComponentEnable("PacketSink", LOG_LEVEL_WARN);
    LogComponentEnable("BulkSendApplication", LOG_LEVEL_WARN);
    LogComponentEnable("OnOffApplication", LOG_LEVEL_WARN);

    // --- Simulation Run ---
    NS_LOG_INFO("Starting simulation for " << simulationTime << " seconds...");
    
    // Enable FlowMonitor for detailed statistics
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();
    
    Simulator::Stop(Seconds(simulationTime + 5.0));
    Simulator::Run();
    
    // Print FlowMonitor statistics
    monitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmon.GetClassifier());
    std::map<FlowId, FlowMonitor::FlowStats> stats = monitor->GetFlowStats();
    
    std::cout << "\n=== FLOW STATISTICS ===" << std::endl;
    std::cout << "FlowID\tSrc->Dst\t\tProto\tTxBytes\tRxBytes\tThroughput\tDelay\t\tJitter\t\tLoss" << std::endl;
    std::cout << "------\t--------\t\t-----\t-------\t-------\t----------\t-----\t\t------\t\t----" << std::endl;
    
    for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin(); i != stats.end(); ++i)
    {
        Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(i->first);
        std::cout << i->first << "\t";
        std::cout << t.sourceAddress << "->" << t.destinationAddress << "\t";
        if (t.protocol == 6) std::cout << "TCP\t";
        else if (t.protocol == 17) std::cout << "UDP\t";
        else std::cout << "Other\t";
        
        std::cout << i->second.txBytes << "\t";
        std::cout << i->second.rxBytes << "\t";
        
        if (i->second.rxBytes > 0)
        {
            double throughput = i->second.rxBytes * 8.0 / (simulationTime * 1000000.0); // Mbps
            std::cout << std::fixed << std::setprecision(2) << throughput << " Mbps\t";
            
            double avgDelay = i->second.delaySum.GetSeconds() / i->second.rxPackets;
            std::cout << std::fixed << std::setprecision(6) << avgDelay << "s\t";
            
            double avgJitter = i->second.jitterSum.GetSeconds() / (i->second.rxPackets - 1);
            std::cout << std::fixed << std::setprecision(6) << avgJitter << "s\t";
        }
        else
        {
            std::cout << "0.00 Mbps\t0.000000s\t0.000000s\t";
        }
        
        double lossRate = 0.0;
        if (i->second.txPackets > 0)
        {
            lossRate = (double)(i->second.txPackets - i->second.rxPackets) / i->second.txPackets * 100.0;
        }
        std::cout << std::fixed << std::setprecision(2) << lossRate << "%";
        
        std::cout << std::endl;
    }
    
    // Summary statistics
    uint64_t totalTxBytes = 0, totalRxBytes = 0;
    uint32_t totalTxPackets = 0, totalRxPackets = 0;
    Time totalDelay = Seconds(0);
    Time totalJitter = Seconds(0);
    
    for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin(); i != stats.end(); ++i)
    {
        totalTxBytes += i->second.txBytes;
        totalRxBytes += i->second.rxBytes;
        totalTxPackets += i->second.txPackets;
        totalRxPackets += i->second.rxPackets;
        totalDelay += i->second.delaySum;
        totalJitter += i->second.jitterSum;
    }
    
    std::cout << "\n=== OVERALL SUMMARY ===" << std::endl;
    std::cout << "Total Throughput: " << std::fixed << std::setprecision(2) 
              << (totalRxBytes * 8.0 / (simulationTime * 1000000.0)) << " Mbps" << std::endl;
    std::cout << "Average Delay: " << std::fixed << std::setprecision(6) 
              << (totalDelay.GetSeconds() / totalRxPackets) << " s" << std::endl;
    std::cout << "Average Jitter: " << std::fixed << std::setprecision(6) 
              << (totalJitter.GetSeconds() / (totalRxPackets - stats.size())) << " s" << std::endl;
    std::cout << "Packet Loss Rate: " << std::fixed << std::setprecision(2) 
              << ((double)(totalTxPackets - totalRxPackets) / totalTxPackets * 100.0) << " %" << std::endl;
    
    // Save FlowMonitor results to XML file
    monitor->SerializeToXmlFile("scratch/enterprise-flowmon-results.xml", true, true);
    
    Simulator::Destroy();

    NS_LOG_INFO("Simulation finished.");
    return 0;
}

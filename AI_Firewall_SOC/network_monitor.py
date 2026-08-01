"""
Network traffic monitor using Scapy
"""

import threading
import time
from collections import defaultdict
from datetime import datetime

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Scapy not installed. Run: pip3 install scapy")

class NetworkMonitor:
    def __init__(self, interface="en0", on_packet_callback=None):
        self.interface = interface
        self.on_packet_callback = on_packet_callback
        self.running = False
        self.sniffer_thread = None
        self.packet_stats = defaultdict(lambda: {
            "count": 0,
            "bytes": 0,
            "protocols": defaultdict(int),
            "first_seen": None,
            "last_seen": None
        })
        
    def start(self):
        """Start packet capture"""
        if not SCAPY_AVAILABLE:
            print("Cannot start monitoring: Scapy not installed")
            return False
            
        self.running = True
        self.sniffer_thread = threading.Thread(target=self._capture_packets)
        self.sniffer_thread.daemon = True
        self.sniffer_thread.start()
        print(f"Started monitoring on {self.interface}")
        return True
        
    def stop(self):
        """Stop packet capture"""
        self.running = False
        if self.sniffer_thread:
            self.sniffer_thread.join(timeout=2)
        print("Stopped monitoring")
        
    def _capture_packets(self):
        """Capture packets in a separate thread"""
        try:
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                store=False,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            print(f"Error capturing packets: {e}")
            
    def _process_packet(self, packet):
        """Process individual packet"""
        if not self.running:
            return
            
        # Extract packet info
        info = self._extract_packet_info(packet)
        if not info:
            return
            
        # Update statistics
        key = f"{info['src_ip']}->{info['dst_ip']}"
        stats = self.packet_stats[key]
        stats["count"] += 1
        stats["bytes"] += len(packet)
        stats["protocols"][info["protocol"]] += 1
        if stats["first_seen"] is None:
            stats["first_seen"] = info["timestamp"]
        stats["last_seen"] = info["timestamp"]
        
        # Call callback
        if self.on_packet_callback:
            self.on_packet_callback(info)
            
    def _extract_packet_info(self, packet):
        """Extract relevant info from packet"""
        info = {
            "timestamp": datetime.now(),
            "src_ip": None,
            "dst_ip": None,
            "protocol": "Unknown",
            "src_port": None,
            "dst_port": None,
            "size": len(packet) if packet else 0
        }
        
        if IP in packet:
            info["src_ip"] = packet[IP].src
            info["dst_ip"] = packet[IP].dst
            
            if TCP in packet:
                info["protocol"] = "TCP"
                info["src_port"] = packet[TCP].sport
                info["dst_port"] = packet[TCP].dport
            elif UDP in packet:
                info["protocol"] = "UDP"
                info["src_port"] = packet[UDP].sport
                info["dst_port"] = packet[UDP].dport
            elif ICMP in packet:
                info["protocol"] = "ICMP"
                
        return info if info["src_ip"] and info["dst_ip"] else None
        
    def get_statistics(self):
        """Get current statistics"""
        return dict(self.packet_stats)
        
    def get_total_packets(self):
        """Get total packet count"""
        return sum(stats["count"] for stats in self.packet_stats.values())

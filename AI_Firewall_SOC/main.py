#!/usr/bin/env python3
"""
Main entry point for Firewall AI SOC Analyst
"""

import sys
import os
import threading
from datetime import datetime

# Import modules
from config import *
from network_monitor import NetworkMonitor
from ai_analyzer import AIAnalyzer
from firewall_controller import FirewallController, FirewallSimulator
from gui_dashboard import FirewallSOCGUI

class FirewallSOCAnalyst:
    def __init__(self):
        print("=" * 60)
        print("🔒 FIREWALL AI SOC ANALYST 🔒")
        print("=" * 60)
        print(f"Mode: {MODE.upper()}")
        print(f"Interface: {INTERFACE}")
        print(f"LLM Enabled: {USE_LLM}")
        print("=" * 60)
        
        # Initialize components
        self.monitor = NetworkMonitor(interface=INTERFACE, on_packet_callback=self.on_packet)
        self.analyzer = AIAnalyzer(threshold=ANOMALY_THRESHOLD)
        
        # Initialize firewall (real or simulated)
        if MODE == "active":
            self.firewall = FirewallController(whitelist=WHITELIST_IPS, block_duration=BLOCK_DURATION)
            # Initialize pf firewall
            self.firewall.initialize_pf()
        else:
            self.firewall = FirewallSimulator(whitelist=WHITELIST_IPS)
            print("[INFO] Running in MONITOR mode - no real blocking")
            
        # Alert tracking for cooldown
        self.alert_cooldown = {}
        
    def on_packet(self, packet_info):
        """Callback when packet is captured"""
        # Analyze packet with AI
        analysis = self.analyzer.analyze_packet(packet_info)
        
        # Check if we should alert
        if analysis['threat_score'] >= 0.1:  # Only alert for non-info
            src_ip = analysis['src_ip']
            current_time = datetime.now()
            
            # Cooldown check
            if src_ip in self.alert_cooldown:
                time_diff = (current_time - self.alert_cooldown[src_ip]).total_seconds()
                if time_diff < ALERT_COOLDOWN:
                    return  # Skip alert due to cooldown
                    
            self.alert_cooldown[src_ip] = current_time
            
            # Add to GUI if running
            if hasattr(self, 'gui'):
                self.gui.add_alert(analysis)
                
    def train_ml(self):
        """Train ML model in background"""
        print("[AI] Training ML model on traffic patterns...")
        # Wait for some traffic first
        import time
        time.sleep(5)
        self.analyzer.train_ml_model()
        print("[AI] ML training complete")
        
    def run(self):
        """Run the SOC analyst"""
        # Start network monitor
        if not self.monitor.start():
            print("[ERROR] Failed to start network monitor")
            print("Try: sudo python3 main.py (needs root for packet capture)")
            sys.exit(1)
            
        # Train ML model in background
        training_thread = threading.Thread(target=self.train_ml)
        training_thread.daemon = True
        training_thread.start()
        
        # Start GUI
        print("[GUI] Starting dashboard...")
        self.gui = FirewallSOCGUI(self.monitor, self.analyzer, self.firewall)
        
        # Run GUI (blocks until closed)
        self.gui.run()
        
def check_requirements():
    """Check if all requirements are met"""
    print("Checking requirements...")
    
    # Check for root (needed for packet capture)
    if os.geteuid() != 0:
        print("\n⚠️  WARNING: Not running as root!")
        print("Packet capture requires root privileges.")
        print("Restart with: sudo python3 main.py\n")
        
    # Check for Scapy
    try:
        import scapy
        print("✓ Scapy installed")
    except ImportError:
        print("✗ Scapy missing - install: pip3 install scapy")
        
    # Check for sklearn
    try:
        import sklearn
        print("✓ scikit-learn installed")
    except ImportError:
        print("✗ scikit-learn missing - install: pip3 install scikit-learn")
        
    print("\n" + "=" * 60)
    
if __name__ == "__main__":
    # Check requirements
    check_requirements()
    
    # Create and run analyst
    analyst = FirewallSOCAnalyst()
    
    try:
        analyst.run()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

"""
Firewall controller for Mac (pfctl)
"""

import subprocess
import os
import time
from datetime import datetime

class FirewallController:
    def __init__(self, whitelist=None, block_duration=300):
        self.whitelist = whitelist or ["127.0.0.1", "192.168.1.1"]
        self.block_duration = block_duration
        self.blocked_ips = {}  # ip: timestamp
        self.is_mac = os.name == 'posix'  # Mac check
        
    def block_ip(self, ip, reason="Suspicious activity"):
        """Block IP using Mac's pfctl"""
        if ip in self.whitelist:
            print(f"Not blocking whitelisted IP: {ip}")
            return False
            
        if ip in self.blocked_ips:
            # Check if block expired
            if time.time() - self.blocked_ips[ip][0] > self.block_duration:
                self.unblock_ip(ip)
            else:
                return False
                
        try:
            # Add block rule to pf
            cmd = f'sudo pfctl -t blocked_ips -T add {ip}'
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            if result.returncode == 0:
                self.blocked_ips[ip] = (time.time(), reason)
                print(f"✓ BLOCKED: {ip} - {reason}")
                return True
            else:
                print(f"Failed to block {ip}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error blocking IP {ip}: {e}")
            return False
            
    def unblock_ip(self, ip):
        """Unblock an IP"""
        if ip not in self.blocked_ips:
            return False
            
        try:
            cmd = f'sudo pfctl -t blocked_ips -T delete {ip}'
            subprocess.run(cmd, shell=True, capture_output=True)
            del self.blocked_ips[ip]
            print(f"✓ UNBLOCKED: {ip}")
            return True
        except Exception as e:
            print(f"Error unblocking {ip}: {e}")
            return False
            
    def initialize_pf(self):
        """Initialize pf firewall for blocking"""
        if not self.is_mac:
            print("Not running on Mac, using simulation mode")
            return False
            
        try:
            # Create anchor file
            anchor_file = "/tmp/pf_anchor.conf"
            with open(anchor_file, "w") as f:
                f.write("table <blocked_ips> persist\n")
                f.write("block in from <blocked_ips> to any\n")
            
            # Load anchor
            subprocess.run(f'sudo pfctl -a "com.apple/2600" -f {anchor_file}', 
                          shell=True, capture_output=True)
            subprocess.run('sudo pfctl -e', shell=True, capture_output=True)
            print("PF Firewall initialized for IP blocking")
            return True
        except Exception as e:
            print(f"Failed to initialize pf: {e}")
            return False
            
    def get_blocked_ips(self):
        """Get list of currently blocked IPs"""
        return list(self.blocked_ips.keys())
        
    def get_block_stats(self):
        """Get blocking statistics"""
        return {
            "total_blocked": len(self.blocked_ips),
            "active_blocks": len([i for i in self.blocked_ips 
                                 if time.time() - self.blocked_ips[i][0] < self.block_duration])
        }


class FirewallSimulator:
    """Simulated firewall for testing (no real blocking)"""
    def __init__(self, whitelist=None):
        self.whitelist = whitelist or []
        self.blocked_ips = {}
        
    def block_ip(self, ip, reason=""):
        if ip in self.whitelist:
            return False
        self.blocked_ips[ip] = reason
        print(f"[SIMULATED] Would block: {ip} - {reason}")
        return True
        
    def unblock_ip(self, ip):
        if ip in self.blocked_ips:
            del self.blocked_ips[ip]
            print(f"[SIMULATED] Would unblock: {ip}")
            return True
        return False
        
    def get_blocked_ips(self):
        return list(self.blocked_ips.keys())
        
    def get_block_stats(self):
        return {"total_blocked": len(self.blocked_ips), "active_blocks": len(self.blocked_ips)}

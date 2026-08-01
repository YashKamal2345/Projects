"""
AI-based traffic analyzer with ML anomaly detection
"""

import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not installed. Run: pip3 install scikit-learn")

class AIAnalyzer:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.connection_history = defaultdict(list)
        self.isolation_forest = None
        self.is_trained = False
        self.threat_scores = {}
        
    def train_ml_model(self):
        """Train isolation forest on normal traffic patterns"""
        if not SKLEARN_AVAILABLE:
            return
            
        # Create feature vectors from connection history
        features = []
        for conn, history in self.connection_history.items():
            if len(history) > 10:
                # Extract features: packet rate, bytes per packet, protocol diversity
                recent = history[-50:]  # Last 50 packets
                packet_rates = []
                bytes_per_packet = []
                
                for i in range(1, len(recent)):
                    time_diff = (recent[i]["timestamp"] - recent[i-1]["timestamp"]).total_seconds()
                    if time_diff > 0:
                        packet_rates.append(1.0 / time_diff)
                    bytes_per_packet.append(recent[i].get("size", 0))
                
                if packet_rates:
                    features.append([
                        np.mean(packet_rates) if packet_rates else 0,
                        np.std(packet_rates) if len(packet_rates) > 1 else 0,
                        np.mean(bytes_per_packet) if bytes_per_packet else 0,
                        len(set(p.get("dst_port", 0) for p in recent)),
                        recent[-1].get("size", 0)
                    ])
        
        if len(features) > 20:
            features = np.array(features)
            self.isolation_forest = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            self.isolation_forest.fit(features)
            self.is_trained = True
            print(f"ML Model trained on {len(features)} connection patterns")
        
    def analyze_packet(self, packet_info):
        """Analyze a single packet for threats"""
        src_ip = packet_info["src_ip"]
        dst_ip = packet_info["dst_ip"]
        conn_key = f"{src_ip}->{dst_ip}"
        
        # Store in history
        self.connection_history[conn_key].append(packet_info)
        
        # Keep only last 200 packets per connection
        if len(self.connection_history[conn_key]) > 200:
            self.connection_history[conn_key] = self.connection_history[conn_key][-200:]
        
        # Calculate threat score
        threat_score = self._calculate_threat_score(packet_info, conn_key)
        
        # Determine severity
        severity = self._get_severity(threat_score)
        
        # Generate alert reason
        reasons = self._get_threat_reasons(packet_info, threat_score)
        
        return {
            "threat_score": threat_score,
            "severity": severity,
            "reasons": reasons,
            "timestamp": packet_info["timestamp"],
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "protocol": packet_info["protocol"],
            "dst_port": packet_info.get("dst_port")
        }
        
    def _calculate_threat_score(self, packet, conn_key):
        """Calculate threat score (0-1) based on multiple factors"""
        score = 0.0
        factors = []
        
        # Factor 1: Unusual destination port (common attack ports)
        attack_ports = {
            22: "SSH", 23: "Telnet", 3389: "RDP", 445: "SMB",
            1433: "MSSQL", 3306: "MySQL", 5900: "VNC", 8080: "Proxy"
        }
        if packet.get("dst_port") in attack_ports:
            score += 0.3
            factors.append(f"Attack port {packet['dst_port']} ({attack_ports[packet['dst_port']]})")
        
        # Factor 2: Packet rate anomaly (possible DoS)
        history = self.connection_history.get(conn_key, [])
        if len(history) > 10:
            recent = history[-10:]
            time_span = (recent[-1]["timestamp"] - recent[0]["timestamp"]).total_seconds()
            if time_span > 0:
                rate = len(recent) / time_span
                if rate > 100:  # >100 packets per second
                    score += 0.4
                    factors.append(f"High packet rate ({rate:.1f}/sec)")
        
        # Factor 3: ML anomaly detection
        if self.is_trained and SKLEARN_AVAILABLE:
            features = self._extract_features(conn_key)
            if features is not None:
                anomaly = self.isolation_forest.predict([features])[0]
                if anomaly == -1:
                    score += 0.3
                    factors.append("ML-detected anomaly")
        
        # Factor 4: ICMP flooding
        if packet["protocol"] == "ICMP":
            score += 0.2
            factors.append("ICMP traffic (potential ping flood)")
        
        # Factor 5: Small packets (scanning behavior)
        if packet.get("size", 0) < 100:
            score += 0.1
            factors.append("Small packet size (scanning)")
            
        return min(score, 1.0)
        
    def _extract_features(self, conn_key):
        """Extract features for ML model"""
        history = self.connection_history.get(conn_key, [])
        if len(history) < 20:
            return None
            
        recent = history[-20:]
        packet_rates = []
        bytes_per_packet = []
        
        for i in range(1, len(recent)):
            time_diff = (recent[i]["timestamp"] - recent[i-1]["timestamp"]).total_seconds()
            if time_diff > 0 and time_diff < 1:
                packet_rates.append(1.0 / time_diff)
            bytes_per_packet.append(recent[i].get("size", 0))
        
        return [
            np.mean(packet_rates) if packet_rates else 0,
            np.std(packet_rates) if len(packet_rates) > 1 else 0,
            np.mean(bytes_per_packet) if bytes_per_packet else 0,
            len(set(p.get("dst_port", 0) for p in recent))
        ]
        
    def _get_severity(self, score):
        """Convert score to severity level"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.3:
            return "MEDIUM"
        elif score >= 0.1:
            return "LOW"
        else:
            return "INFO"
            
    def _get_threat_reasons(self, packet, score):
        """Get human-readable threat reasons"""
        reasons = []
        
        if score >= 0.8:
            reasons.append("Immediate action required")
        if packet.get("dst_port") in [22, 3389, 445]:
            reasons.append(f"Sensitive port {packet['dst_port']} access")
        if score >= 0.6 and "rate" in str(reasons):
            reasons.append("Possible DoS attack")
            
        return reasons if reasons else ["Normal traffic"]

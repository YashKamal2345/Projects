"""
Configuration for Firewall AI SOC Analyst
"""

# Mode Configuration
MODE = "monitor"  # "monitor" (safe) or "active" (blocks IPs)
# WARNING: Active mode WILL block IPs using pfctl

# Network Configuration
INTERFACE = "en0"  # Mac WiFi interface (en0 = WiFi, en1 = Ethernet)
CAPTURE_COUNT = 0  # 0 = infinite
TIMEOUT = 60  # Seconds per capture session

# AI Configuration
USE_LLM = False  # Set to True if Ollama installed
LLM_MODEL = "tinyllama"
ANOMALY_THRESHOLD = 0.7  # 0-1, lower = more sensitive

# Blocking Rules
AUTO_BLOCK_CRITICAL = True
BLOCK_DURATION = 300  # Seconds to block (300 = 5 minutes)
WHITELIST_IPS = ["127.0.0.1", "192.168.1.1", "8.8.8.8"]  # Never block these

# Alert Settings
ALERT_COOLDOWN = 60  # Don't alert same IP more than once per minute

# Display
REFRESH_RATE = 1  # GUI refresh in seconds

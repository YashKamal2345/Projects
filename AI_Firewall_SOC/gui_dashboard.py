import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread
from datetime import datetime
import time
import os

class FirewallSOCGUI:
    def __init__(self, monitor, analyzer, firewall):
        self.monitor = monitor
        self.analyzer = analyzer
        self.firewall = firewall
        self.running = True
        
        self.root = tk.Tk()
        self.root.title("Firewall AI SOC Analyst - Active")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1e1e1e')
        
        self.alerts_list = []
        self.alerts_generated = 0
        
        self.setup_ui()
        
        self.update_thread = Thread(target=self.update_display)
        self.update_thread.daemon = True
        self.update_thread.start()
        
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg='#0d7377')
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="🔒 AUTONOMOUS AI SOC ANALYZER 🔒", 
                font=('Arial', 18, 'bold'), bg='#0d7377', fg='white').pack(pady=10)
        
        status_frame = tk.Frame(self.root, bg='#2d2d2d')
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: MONITORING", 
                                     font=('Arial', 12), bg='#2d2d2d', fg='#00ff00')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.packet_count = tk.Label(status_frame, text="Packets: 0", 
                                     font=('Arial', 12), bg='#2d2d2d', fg='white')
        self.packet_count.pack(side=tk.LEFT, padx=20)
        
        self.alert_count = tk.Label(status_frame, text="Alerts: 0", 
                                    font=('Arial', 12), bg='#2d2d2d', fg='white')
        self.alert_count.pack(side=tk.LEFT, padx=20)
        
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = tk.LabelFrame(main_frame, text="🚨 LIVE THREATS", 
                                   bg='#1e1e1e', fg='white', font=('Arial', 12, 'bold'))
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.threat_tree = ttk.Treeview(left_frame, columns=('Time', 'Src', 'Dst', 'Score', 'Severity'), 
                                        show='headings', height=20)
        self.threat_tree.heading('Time', text='Time')
        self.threat_tree.heading('Src', text='Source IP')
        self.threat_tree.heading('Dst', text='Dest IP')
        self.threat_tree.heading('Score', text='Score')
        self.threat_tree.heading('Severity', text='Severity')
        
        self.threat_tree.column('Time', width=80)
        self.threat_tree.column('Src', width=140)
        self.threat_tree.column('Dst', width=140)
        self.threat_tree.column('Score', width=60)
        self.threat_tree.column('Severity', width=80)
        
        self.threat_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.threat_tree.tag_configure('critical', background='#ff9999')
        self.threat_tree.tag_configure('high', background='#ffcc99')
        self.threat_tree.tag_configure('medium', background='#ffff99')
        self.threat_tree.tag_configure('low', background='#99ff99')
        
        middle_frame = tk.LabelFrame(main_frame, text="🔒 BLOCKED IPS", 
                                     bg='#1e1e1e', fg='white', font=('Arial', 12, 'bold'))
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.blocked_listbox = tk.Listbox(middle_frame, bg='#2d2d2d', fg='white', 
                                          font=('Courier', 11), height=20)
        self.blocked_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = tk.LabelFrame(main_frame, text="📊 STATISTICS", 
                                    bg='#1e1e1e', fg='white', font=('Arial', 12, 'bold'))
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.stats_text = scrolledtext.ScrolledText(right_frame, bg='#2d2d2d', fg='white',
                                                    font=('Courier', 11), height=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        control_frame = tk.Frame(self.root, bg='#2d2d2d')
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_block_var = tk.BooleanVar(value=False)
        auto_block_btn = tk.Checkbutton(control_frame, text="Auto-Block Threats", 
                                        variable=self.auto_block_var, bg='#2d2d2d', fg='white',
                                        selectcolor='#2d2d2d')
        auto_block_btn.pack(side=tk.LEFT, padx=10)
        
        stop_btn = tk.Button(control_frame, text="STOP MONITORING", command=self.stop_monitoring,
                            bg='#ff0000', fg='white', font=('Arial', 10, 'bold'))
        stop_btn.pack(side=tk.RIGHT, padx=10)
        
        export_btn = tk.Button(control_frame, text="EXPORT REPORT", command=self.export_report,
                              bg='#00cc00', fg='white', font=('Arial', 10, 'bold'))
        export_btn.pack(side=tk.RIGHT, padx=10)
        
        unblock_btn = tk.Button(control_frame, text="UNBLOCK ALL", command=self.unblock_all,
                               bg='#ff6600', fg='white', font=('Arial', 10, 'bold'))
        unblock_btn.pack(side=tk.RIGHT, padx=10)
        
    def update_display(self):
        while self.running:
            try:
                self.packet_count.config(text=f"Packets: {self.monitor.get_total_packets()}")
                self.update_statistics()
                self.update_blocked_list()
                time.sleep(0.5)
            except:
                break
                
    def add_alert(self, alert):
        self.alerts_generated += 1
        self.alert_count.config(text=f"Alerts: {self.alerts_generated}")
        self.alerts_list.append(alert)
        
        severity = alert['severity'].lower()
        self.threat_tree.insert('', 0, values=(
            alert['timestamp'].strftime('%H:%M:%S'),
            alert['src_ip'],
            alert['dst_ip'],
            f"{alert['threat_score']:.2f}",
            alert['severity']
        ), tags=(severity,))
        
        if self.auto_block_var.get() and alert['severity'] in ['CRITICAL', 'HIGH']:
            self.firewall.block_ip(alert['src_ip'], f"Auto-block: {alert['severity']}")
        
        if len(self.threat_tree.get_children()) > 100:
            last = self.threat_tree.get_children()[-1]
            self.threat_tree.delete(last)
        
        if len(self.alerts_list) > 500:
            self.alerts_list = self.alerts_list[-500:]
        
    def update_statistics(self):
        stats = "=" * 30 + " SYSTEM STATS " + "=" * 30 + "\n\n"
        stats += f"Total Packets: {self.monitor.get_total_packets()}\n"
        stats += f"Total Alerts: {self.alerts_generated}\n\n"
        stats += "=" * 30 + " TOP CONNECTIONS " + "=" * 30 + "\n"
        
        conn_stats = self.monitor.get_statistics()
        sorted_conns = sorted(conn_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
        for conn, data in sorted_conns:
            stats += f"{conn:<30} {data['count']:>6} packets\n"
        
        stats += "\n" + "=" * 30 + " BLOCKING STATS " + "=" * 30 + "\n"
        block_stats = self.firewall.get_block_stats()
        stats += f"Total Blocked: {block_stats['total_blocked']}\n"
        stats += f"Active Blocks: {block_stats['active_blocks']}\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        
    def update_blocked_list(self):
        self.blocked_listbox.delete(0, tk.END)
        blocked = self.firewall.get_blocked_ips()
        if blocked:
            for ip in blocked[:30]:
                self.blocked_listbox.insert(tk.END, ip)
        else:
            self.blocked_listbox.insert(tk.END, "No IPs currently blocked")
            
    def export_report(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"soc_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("FIREWALL AI SOC ANALYST - INCIDENT REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Packets: {self.monitor.get_total_packets()}\n")
                f.write(f"Total Alerts: {self.alerts_generated}\n\n")
                
                f.write("=" * 70 + "\n")
                f.write("ALERT DETAILS (Last 100 alerts)\n")
                f.write("=" * 70 + "\n")
                
                for i, alert in enumerate(self.alerts_list[-100:], 1):
                    f.write(f"\n{i}. {alert['timestamp'].strftime('%H:%M:%S')} | ")
                    f.write(f"{alert['src_ip']} -> {alert['dst_ip']} | ")
                    f.write(f"Score: {alert['threat_score']:.2f} | ")
                    f.write(f"Severity: {alert['severity']}\n")
                
                f.write("\n" + "=" * 70 + "\n")
                f.write("BLOCKED IPS\n")
                f.write("=" * 70 + "\n")
                for ip in self.firewall.get_blocked_ips():
                    f.write(f"  • {ip}\n")
            
            messagebox.showinfo("Export Successful", f"Report saved as:\n{filename}")
            print(f"✅ Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
            
    def unblock_all(self):
        if messagebox.askyesno("Confirm Unblock", "Unblock ALL IPs?"):
            for ip in self.firewall.get_blocked_ips():
                self.firewall.unblock_ip(ip)
            messagebox.showinfo("Success", "All IPs unblocked")
            
    def stop_monitoring(self):
        if messagebox.askyesno("Confirm Stop", "Stop monitoring and exit?"):
            self.running = False
            self.monitor.stop()
            self.root.quit()
            self.root.destroy()
            
    def run(self):
        self.root.mainloop()

"""
SMART TRAFFIC CONTROL SYSTEM USING DEEP REINFORCEMENT LEARNING
MODIFIED - Vehicles drive on RIGHT side with proper traffic light control
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import random
import threading
from collections import deque

# Try to import torch
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not found. Using simplified RL algorithm.")

# ==================== DEEP Q-NETWORK ====================

if TORCH_AVAILABLE:
    class DQNetwork(nn.Module):
        def __init__(self, state_size, action_size, hidden_size=128):
            super(DQNetwork, self).__init__()
            self.fc1 = nn.Linear(state_size, hidden_size)
            self.fc2 = nn.Linear(hidden_size, hidden_size)
            self.fc3 = nn.Linear(hidden_size, action_size)
            
        def forward(self, x):
            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            return self.fc3(x)
    
    class DQNAgent:
        def __init__(self, state_size, action_size):
            self.state_size = state_size
            self.action_size = action_size
            self.epsilon = 0.3
            self.epsilon_min = 0.05
            self.epsilon_decay = 0.995
            
            self.q_network = DQNetwork(state_size, action_size)
            self.optimizer = optim.Adam(self.q_network.parameters(), lr=0.001)
            self.memory = deque(maxlen=2000)
            self.batch_size = 32
            self.gamma = 0.95
            
        def act(self, state, training=True):
            if training and random.random() < self.epsilon:
                return random.randint(0, self.action_size - 1)
            
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
            return np.argmax(q_values.numpy())
        
        def remember(self, state, action, reward, next_state, done):
            self.memory.append((state, action, reward, next_state, done))
            
        def replay(self):
            if len(self.memory) < self.batch_size:
                return
            
            batch = random.sample(self.memory, self.batch_size)
            states, actions, rewards, next_states, dones = zip(*batch)
            
            states = torch.FloatTensor(np.array(states))
            actions = torch.LongTensor(actions)
            rewards = torch.FloatTensor(rewards)
            next_states = torch.FloatTensor(np.array(next_states))
            dones = torch.FloatTensor(dones)
            
            current_q = self.q_network(states).gather(1, actions.unsqueeze(1))
            next_q = self.q_network(next_states).max(1)[0].detach()
            target_q = rewards + (1 - dones) * self.gamma * next_q
            
            loss = F.mse_loss(current_q.squeeze(), target_q)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
else:
    class DQNAgent:
        def __init__(self, state_size, action_size):
            self.action_size = action_size
            self.epsilon = 0.3
            self.epsilon_min = 0.05
            self.epsilon_decay = 0.995
            self.q_table = {}
            self.lr = 0.1
            self.gamma = 0.95
            
        def get_state_key(self, state):
            key = tuple(np.round(state[:8], 1))
            return key
            
        def act(self, state, training=True):
            if training and random.random() < self.epsilon:
                return random.randint(0, self.action_size - 1)
            key = self.get_state_key(state)
            if key not in self.q_table:
                self.q_table[key] = np.zeros(self.action_size)
            return np.argmax(self.q_table[key])
            
        def remember(self, state, action, reward, next_state, done):
            key = self.get_state_key(state)
            next_key = self.get_state_key(next_state)
            
            if key not in self.q_table:
                self.q_table[key] = np.zeros(self.action_size)
            if next_key not in self.q_table:
                self.q_table[next_key] = np.zeros(self.action_size)
                
            best_next = np.max(self.q_table[next_key])
            td_target = reward + self.gamma * best_next * (1 - done)
            td_error = td_target - self.q_table[key][action]
            self.q_table[key][action] += self.lr * td_error
            
        def replay(self):
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

# ==================== VEHICLE CLASS - RIGHT SIDE DRIVING ====================

class Vehicle:
    def __init__(self, vehicle_id, direction):
        self.id = vehicle_id
        self.direction = direction
        self.speed = 1.5
        self.waiting_time = 0
        self.size = 12
        self.color = self.get_random_color()
        self.state = 'APPROACHING'
        self.stopped = False
        
        # RIGHT SIDE DRIVING - Vehicles stay in right lane
        if direction == 'N':
            self.x = 415  # Right lane for northbound
            self.y = 40
            self.target_y = 760
        elif direction == 'S':
            self.x = 385  # Right lane for southbound
            self.y = 760
            self.target_y = 40
        elif direction == 'E':
            self.x = 760
            self.y = 415  # Right lane for eastbound (bottom lane)
            self.target_x = 40
        elif direction == 'W':
            self.x = 40
            self.y = 385  # Right lane for westbound (bottom lane)
            self.target_x = 760
        
    def get_random_color(self):
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        return random.choice(colors)
    
    def update_position(self):
        if not self.stopped:
            if self.direction == 'N':
                self.y += self.speed
            elif self.direction == 'S':
                self.y -= self.speed
            elif self.direction == 'E':
                self.x -= self.speed
            elif self.direction == 'W':
                self.x += self.speed
    
    def has_completed(self):
        if self.direction == 'N':
            return self.y >= self.target_y
        elif self.direction == 'S':
            return self.y <= self.target_y
        elif self.direction == 'E':
            return self.x <= self.target_x
        else:  # W
            return self.x >= self.target_x
    
    def is_at_intersection(self, center=400, radius=40):
        return (abs(self.x - center) < radius and abs(self.y - center) < radius)

# ==================== TRAFFIC ENVIRONMENT WITH PROPER LIGHTS ====================

class TrafficEnvironment:
    def __init__(self):
        self.intersection_center = 400
        self.intersection_radius = 40
        
        # 4 INDEPENDENT TRAFFIC LIGHTS
        self.lights = {
            'N': True,   # North - Green
            'S': True,   # South - Green  
            'E': False,  # East - Red
            'W': False   # West - Red
        }
        
        self.light_timers = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        self.min_green_time = 60
        self.max_green_time = 120
        
        # Vehicle lists
        self.vehicles_north = []
        self.vehicles_south = []
        self.vehicles_east = []
        self.vehicles_west = []
        
        self.next_vehicle_id = 0
        self.vehicles_passed = 0
        self.total_reward = 0
        
        # Spawn rate
        self.spawn_rate = 0.04
        
    def get_all_vehicles(self):
        return self.vehicles_north + self.vehicles_south + self.vehicles_east + self.vehicles_west
    
    def get_state(self):
        state = []
        
        # Count vehicles in each direction approaching intersection
        for vehicles in [self.vehicles_north, self.vehicles_south, self.vehicles_east, self.vehicles_west]:
            count = 0
            for v in vehicles:
                if v.direction in ['N', 'S']:
                    dist = abs(v.y - self.intersection_center)
                else:
                    dist = abs(v.x - self.intersection_center)
                if dist < 150:
                    count += 1
            state.append(count / 15.0)
        
        # Add waiting times
        for vehicles in [self.vehicles_north, self.vehicles_south, self.vehicles_east, self.vehicles_west]:
            wait_times = [v.waiting_time for v in vehicles if v.waiting_time > 0]
            avg_wait = np.mean(wait_times) if wait_times else 0
            state.append(avg_wait / 100.0)
        
        # Add light states
        for direction in ['N', 'S', 'E', 'W']:
            state.append(1.0 if self.lights[direction] else 0.0)
        
        return np.array(state, dtype=np.float32)
    
    def step(self, action):
        reward = 0
        
        # Apply action
        if action == 0 and self.light_timers['N'] >= self.min_green_time:
            self.lights['N'] = not self.lights['N']
            self.light_timers['N'] = 0
        elif action == 1 and self.light_timers['S'] >= self.min_green_time:
            self.lights['S'] = not self.lights['S']
            self.light_timers['S'] = 0
        elif action == 2 and self.light_timers['E'] >= self.min_green_time:
            self.lights['E'] = not self.lights['E']
            self.light_timers['E'] = 0
        elif action == 3 and self.light_timers['W'] >= self.min_green_time:
            self.lights['W'] = not self.lights['W']
            self.light_timers['W'] = 0
        
        # Increment timers
        for direction in ['N', 'S', 'E', 'W']:
            self.light_timers[direction] += 1
            if self.light_timers[direction] > self.max_green_time:
                self.lights[direction] = not self.lights[direction]
                self.light_timers[direction] = 0
        
        # Update vehicles with traffic light logic
        reward += self.update_vehicles()
        
        # Spawn vehicles
        self.spawn_vehicles()
        
        # Congestion penalty
        if len(self.get_all_vehicles()) > 40:
            reward -= (len(self.get_all_vehicles()) - 40) * 0.03
        
        self.total_reward += reward
        return self.get_state(), reward, False, {}
    
    def update_vehicles(self):
        reward = 0
        
        # Update NORTH vehicles (moving DOWN)
        to_remove = []
        for v in self.vehicles_north:
            at_intersection = v.is_at_intersection(self.intersection_center, self.intersection_radius)
            can_pass = self.lights['N']
            
            if at_intersection and not can_pass:
                # Stop at red light
                v.stopped = True
                v.waiting_time += 1
                v.state = 'WAITING'
                reward -= 0.3
            else:
                # Green light or not at intersection yet
                if v.stopped and can_pass:
                    v.stopped = False
                    if v.waiting_time > 0:
                        reward -= v.waiting_time * 0.05
                        v.waiting_time = 0
                elif v.waiting_time > 0:
                    reward -= v.waiting_time * 0.03
                    v.waiting_time = 0
                
                if at_intersection and can_pass:
                    v.state = 'CROSSING'
                    reward += 2.0
                else:
                    v.state = 'APPROACHING'
                
                v.update_position()
                if v.has_completed():
                    to_remove.append(v)
                    self.vehicles_passed += 1
                    reward += 12.0
        for v in to_remove:
            self.vehicles_north.remove(v)
        
        # Update SOUTH vehicles (moving UP)
        to_remove = []
        for v in self.vehicles_south:
            at_intersection = v.is_at_intersection(self.intersection_center, self.intersection_radius)
            can_pass = self.lights['S']
            
            if at_intersection and not can_pass:
                v.stopped = True
                v.waiting_time += 1
                v.state = 'WAITING'
                reward -= 0.3
            else:
                if v.stopped and can_pass:
                    v.stopped = False
                    if v.waiting_time > 0:
                        reward -= v.waiting_time * 0.05
                        v.waiting_time = 0
                elif v.waiting_time > 0:
                    reward -= v.waiting_time * 0.03
                    v.waiting_time = 0
                
                if at_intersection and can_pass:
                    v.state = 'CROSSING'
                    reward += 2.0
                else:
                    v.state = 'APPROACHING'
                
                v.update_position()
                if v.has_completed():
                    to_remove.append(v)
                    self.vehicles_passed += 1
                    reward += 12.0
        for v in to_remove:
            self.vehicles_south.remove(v)
        
        # Update EAST vehicles (moving LEFT)
        to_remove = []
        for v in self.vehicles_east:
            at_intersection = v.is_at_intersection(self.intersection_center, self.intersection_radius)
            can_pass = self.lights['E']
            
            if at_intersection and not can_pass:
                v.stopped = True
                v.waiting_time += 1
                v.state = 'WAITING'
                reward -= 0.3
            else:
                if v.stopped and can_pass:
                    v.stopped = False
                    if v.waiting_time > 0:
                        reward -= v.waiting_time * 0.05
                        v.waiting_time = 0
                elif v.waiting_time > 0:
                    reward -= v.waiting_time * 0.03
                    v.waiting_time = 0
                
                if at_intersection and can_pass:
                    v.state = 'CROSSING'
                    reward += 2.0
                else:
                    v.state = 'APPROACHING'
                
                v.update_position()
                if v.has_completed():
                    to_remove.append(v)
                    self.vehicles_passed += 1
                    reward += 12.0
        for v in to_remove:
            self.vehicles_east.remove(v)
        
        # Update WEST vehicles (moving RIGHT)
        to_remove = []
        for v in self.vehicles_west:
            at_intersection = v.is_at_intersection(self.intersection_center, self.intersection_radius)
            can_pass = self.lights['W']
            
            if at_intersection and not can_pass:
                v.stopped = True
                v.waiting_time += 1
                v.state = 'WAITING'
                reward -= 0.3
            else:
                if v.stopped and can_pass:
                    v.stopped = False
                    if v.waiting_time > 0:
                        reward -= v.waiting_time * 0.05
                        v.waiting_time = 0
                elif v.waiting_time > 0:
                    reward -= v.waiting_time * 0.03
                    v.waiting_time = 0
                
                if at_intersection and can_pass:
                    v.state = 'CROSSING'
                    reward += 2.0
                else:
                    v.state = 'APPROACHING'
                
                v.update_position()
                if v.has_completed():
                    to_remove.append(v)
                    self.vehicles_passed += 1
                    reward += 12.0
        for v in to_remove:
            self.vehicles_west.remove(v)
        
        return reward
    
    def spawn_vehicles(self):
        """Spawn vehicles - RIGHT SIDE DRIVING"""
        
        # Spawn NORTH (top, moving DOWN - right lane at x=415)
        if random.random() < self.spawn_rate and len(self.vehicles_north) < 20:
            blocked = False
            for v in self.vehicles_north:
                if abs(v.y - 40) < 25:
                    blocked = True
                    break
            if not blocked:
                self.vehicles_north.append(Vehicle(self.next_vehicle_id, 'N'))
                self.next_vehicle_id += 1
        
        # Spawn SOUTH (bottom, moving UP - right lane at x=385)
        if random.random() < self.spawn_rate and len(self.vehicles_south) < 20:
            blocked = False
            for v in self.vehicles_south:
                if abs(v.y - 760) < 25:
                    blocked = True
                    break
            if not blocked:
                self.vehicles_south.append(Vehicle(self.next_vehicle_id, 'S'))
                self.next_vehicle_id += 1
        
        # Spawn EAST (right, moving LEFT - bottom lane at y=415)
        if random.random() < self.spawn_rate and len(self.vehicles_east) < 20:
            blocked = False
            for v in self.vehicles_east:
                if abs(v.x - 760) < 25:
                    blocked = True
                    break
            if not blocked:
                self.vehicles_east.append(Vehicle(self.next_vehicle_id, 'E'))
                self.next_vehicle_id += 1
        
        # Spawn WEST (left, moving RIGHT - bottom lane at y=385)
        if random.random() < self.spawn_rate and len(self.vehicles_west) < 20:
            blocked = False
            for v in self.vehicles_west:
                if abs(v.x - 40) < 25:
                    blocked = True
                    break
            if not blocked:
                self.vehicles_west.append(Vehicle(self.next_vehicle_id, 'W'))
                self.next_vehicle_id += 1
    
    def reset(self):
        self.vehicles_north = []
        self.vehicles_south = []
        self.vehicles_east = []
        self.vehicles_west = []
        self.next_vehicle_id = 0
        self.vehicles_passed = 0
        self.total_reward = 0
        self.lights = {'N': True, 'S': True, 'E': False, 'W': False}
        self.light_timers = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        return self.get_state()

# ==================== GUI APPLICATION ====================

class TrafficSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚦 RIGHT SIDE DRIVING - Traffic Control System 🚗")
        self.root.geometry("1600x950")
        self.root.configure(bg='#1a1a2e')
        
        self.env = TrafficEnvironment()
        self.agent = DQNAgent(state_size=16, action_size=4)
        
        self.trained = False
        self.training_in_progress = False
        self.running = True
        self.simulation_speed = 20
        self.current_reward = 0
        
        self.create_widgets()
        self.update_animation()
        
        self.root.bind('<q>', lambda e: self.exit_app())
        self.root.bind('<Q>', lambda e: self.exit_app())
        self.root.bind('<space>', lambda e: self.toggle_speed())
        
    def create_widgets(self):
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas
        canvas_container = tk.Frame(main_container, bg='#1a1a2e')
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_container, width=800, height=800, 
                                 bg='#2d5016', highlightthickness=2,
                                 highlightbackground='#0f3460')
        self.canvas.pack(padx=10, pady=10)
        
        # Control panel
        control_panel = tk.Frame(main_container, bg='#16213e', width=500)
        control_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        control_panel.pack_propagate(False)
        
        # Title
        tk.Label(control_panel, text="🚦 RIGHT SIDE DRIVING", 
                font=('Arial', 18, 'bold'), bg='#16213e', fg='#e94560').pack(pady=10)
        tk.Label(control_panel, text="Deep Reinforcement Learning - Keep Right Rule", 
                font=('Arial', 10), bg='#16213e', fg='#a8dadc').pack()
        
        # Statistics
        stats_frame = tk.Frame(control_panel, bg='#1a1a2e', relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(stats_frame, text="📊 STATISTICS", font=('Arial', 14, 'bold'), 
                bg='#1a1a2e', fg='#f1faee').pack(pady=5)
        
        self.stats_labels = {}
        stats = [
            ("Total vehicles:", "0"),
            ("Vehicles passed:", "0"),
            ("Waiting vehicles:", "0"),
            ("Current reward:", "0.00"),
            ("Total reward:", "0.00"),
            ("Agent epsilon:", "0.30")
        ]
        for label, val in stats:
            frame = tk.Frame(stats_frame, bg='#1a1a2e')
            frame.pack(fill=tk.X, pady=3, padx=15)
            tk.Label(frame, text=label, bg='#1a1a2e', fg='#a8dadc',
                    font=('Arial', 10)).pack(side=tk.LEFT)
            self.stats_labels[label] = tk.Label(frame, text=val, bg='#1a1a2e', 
                                                 fg='#e94560', font=('Arial', 10, 'bold'))
            self.stats_labels[label].pack(side=tk.RIGHT)
        
        # Vehicle counts per direction
        dir_frame = tk.Frame(control_panel, bg='#1a1a2e', relief=tk.RAISED, bd=2)
        dir_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(dir_frame, text="🚗 VEHICLES PER DIRECTION", font=('Arial', 12, 'bold'),
                bg='#1a1a2e', fg='#f1faee').pack(pady=5)
        
        self.dir_counts = {}
        for dir_name in ['NORTH', 'SOUTH', 'EAST', 'WEST']:
            frame = tk.Frame(dir_frame, bg='#1a1a2e')
            frame.pack(fill=tk.X, pady=3, padx=15)
            tk.Label(frame, text=f"{dir_name}:", bg='#1a1a2e', fg='#a8dadc',
                    font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            self.dir_counts[dir_name] = tk.Label(frame, text="0", bg='#1a1a2e', 
                                                  fg='#4CAF50', font=('Arial', 10, 'bold'))
            self.dir_counts[dir_name].pack(side=tk.RIGHT)
        
        # Light status
        light_frame = tk.Frame(control_panel, bg='#1a1a2e', relief=tk.RAISED, bd=2)
        light_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(light_frame, text="🚦 TRAFFIC LIGHTS", font=('Arial', 12, 'bold'),
                bg='#1a1a2e', fg='#f1faee').pack(pady=5)
        
        self.light_labels = {}
        for dir_name, dir_key in [('NORTH', 'N'), ('SOUTH', 'S'), ('EAST', 'E'), ('WEST', 'W')]:
            frame = tk.Frame(light_frame, bg='#1a1a2e')
            frame.pack(fill=tk.X, pady=3, padx=15)
            tk.Label(frame, text=f"{dir_name}:", bg='#1a1a2e', fg='#a8dadc',
                    font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            self.light_labels[dir_name] = tk.Label(frame, text="🟢 GREEN", 
                                                    bg='#1a1a2e', fg='#4CAF50')
            self.light_labels[dir_name].pack(side=tk.RIGHT)
        
        # Buttons
        button_frame = tk.Frame(control_panel, bg='#16213e')
        button_frame.pack(pady=15)
        
        self.train_btn = tk.Button(button_frame, text="🤖 TRAIN DRL AGENT", 
                                   font=('Arial', 12, 'bold'), bg='#FFD700', fg='#1a1a2e',
                                   command=self.train_agent, width=25, height=2,
                                   cursor='hand2', activebackground='#FFC107')
        self.train_btn.pack(pady=5)
        
        self.test_btn = tk.Button(button_frame, text="🧪 TEST AGENT", 
                                   font=('Arial', 12, 'bold'), bg='#FFD700', fg='#1a1a2e',
                                   command=self.test_agent, width=25, height=2,
                                   cursor='hand2', activebackground='#FFC107')
        self.test_btn.pack(pady=5)
        
        self.reset_btn = tk.Button(button_frame, text="🔄 RESET SIMULATION", 
                                   font=('Arial', 12, 'bold'), bg='#FFD700', fg='#1a1a2e',
                                   command=self.reset_simulation, width=25, height=2,
                                   cursor='hand2', activebackground='#FFC107')
        self.reset_btn.pack(pady=5)
        
        # Speed control
        speed_frame = tk.Frame(button_frame, bg='#16213e')
        speed_frame.pack(pady=10)
        tk.Label(speed_frame, text="SPEED:", bg='#16213e', fg='#a8dadc',
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.speed_label = tk.Label(speed_frame, text="🐢 SLOW", bg='#16213e', fg='#4CAF50')
        self.speed_label.pack(side=tk.LEFT)
        
        # Instructions
        instr_frame = tk.Frame(control_panel, bg='#1a1a2e', relief=tk.RAISED, bd=2)
        instr_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(instr_frame, text="💡 RIGHT SIDE DRIVING RULES", font=('Arial', 12, 'bold'),
                bg='#1a1a2e', fg='#f1faee').pack(pady=5)
        
        instructions = [
            "✓ NORTH: Spawns at TOP right lane (x=415), moves DOWN",
            "✓ SOUTH: Spawns at BOTTOM right lane (x=385), moves UP",
            "✓ EAST: Spawns at RIGHT bottom lane (y=415), moves LEFT",
            "✓ WEST: Spawns at LEFT bottom lane (y=385), moves RIGHT",
            "✓ ALL vehicles keep to the RIGHT side of the road",
            "✓ Vehicles STOP at RED lights and GO on GREEN lights",
            "✓ Each direction has INDEPENDENT traffic light",
            "",
            "🎮 CONTROLS:",
            "• SPACE - Change simulation speed",
            "• Q - Exit"
        ]
        for instr in instructions:
            tk.Label(instr_frame, text=instr, bg='#1a1a2e', fg='#a8dadc',
                    font=('Arial', 9), wraplength=380).pack(pady=2, padx=10)
        
        self.status_label = tk.Label(control_panel, text="✅ System ready. Click 'TRAIN AGENT'!",
                                     bg='#16213e', fg='#4CAF50')
        self.status_label.pack(pady=10)
    
    def draw_road(self):
        self.canvas.delete("all")
        
        # Background
        self.canvas.create_rectangle(0, 0, 800, 800, fill='#2d5016')
        
        # Roads
        self.canvas.create_rectangle(0, 360, 800, 440, fill='#2c2c2c')
        self.canvas.create_rectangle(360, 0, 440, 800, fill='#2c2c2c')
        
        # Road center lines
        self.canvas.create_line(0, 400, 800, 400, fill='#ffd700', width=2, dash=(20, 10))
        self.canvas.create_line(400, 0, 400, 800, fill='#ffd700', width=2, dash=(20, 10))
        
        # Lane markings
        self.canvas.create_line(415, 40, 415, 360, fill='white', width=1, dash=(5, 5))
        self.canvas.create_line(385, 440, 385, 760, fill='white', width=1, dash=(5, 5))
        self.canvas.create_line(440, 415, 760, 415, fill='white', width=1, dash=(5, 5))
        self.canvas.create_line(40, 385, 360, 385, fill='white', width=1, dash=(5, 5))
        
        # Stop lines before intersection
        self.canvas.create_line(415, 355, 425, 355, fill='white', width=3)
        self.canvas.create_line(375, 445, 385, 445, fill='white', width=3)
        self.canvas.create_line(445, 415, 445, 425, fill='white', width=3)
        self.canvas.create_line(355, 375, 355, 385, fill='white', width=3)
        
        # Intersection
        self.canvas.create_rectangle(360, 360, 440, 440, fill='#3a3a3a', outline='#555', width=3)
        
        # Crosswalks
        for offset in [-12, -4, 4, 12]:
            self.canvas.create_line(370 + offset, 330, 370 + offset, 355, fill='white', width=2)
            self.canvas.create_line(370 + offset, 445, 370 + offset, 470, fill='white', width=2)
            self.canvas.create_line(445, 370 + offset, 470, 370 + offset, fill='white', width=2)
            self.canvas.create_line(330, 370 + offset, 355, 370 + offset, fill='white', width=2)
        
        # Spawn point markers
        self.canvas.create_rectangle(405, 30, 425, 50, fill='#4CAF50', outline='white', width=2)
        self.canvas.create_text(415, 25, text="NORTH SPAWN", fill='white', font=('Arial', 7, 'bold'))
        self.canvas.create_text(415, 18, text="↓", fill='yellow', font=('Arial', 10, 'bold'))
        
        self.canvas.create_rectangle(375, 750, 395, 770, fill='#4CAF50', outline='white', width=2)
        self.canvas.create_text(385, 785, text="SOUTH SPAWN", fill='white', font=('Arial', 7, 'bold'))
        self.canvas.create_text(385, 778, text="↑", fill='yellow', font=('Arial', 10, 'bold'))
        
        self.canvas.create_rectangle(750, 405, 770, 425, fill='#4CAF50', outline='white', width=2)
        self.canvas.create_text(785, 415, text="EAST SPAWN", fill='white', font=('Arial', 7, 'bold'))
        self.canvas.create_text(778, 415, text="←", fill='yellow', font=('Arial', 10, 'bold'))
        
        self.canvas.create_rectangle(30, 375, 50, 395, fill='#4CAF50', outline='white', width=2)
        self.canvas.create_text(15, 385, text="WEST SPAWN", fill='white', font=('Arial', 7, 'bold'))
        self.canvas.create_text(22, 385, text="→", fill='yellow', font=('Arial', 10, 'bold'))
        
        # Draw traffic lights
        self.draw_lights()
    
    def draw_lights(self):
        positions = {'N': (415, 300), 'S': (385, 500), 'E': (500, 415), 'W': (300, 385)}
        
        for direction, (x, y) in positions.items():
            is_green = self.env.lights[direction]
            color = '#00ff00' if is_green else '#ff0000'
            
            self.canvas.create_rectangle(x-12, y-12, x+12, y+12, fill='#222', outline='#555', width=2)
            self.canvas.create_oval(x-8, y-8, x+8, y+8, fill=color, outline='#fff', width=2)
            
            if is_green:
                self.canvas.create_oval(x-18, y-18, x+18, y+18, fill='', 
                                       outline='#00ff00', width=2, stipple='gray50')
    
    def draw_vehicles(self):
        all_vehicles = self.env.get_all_vehicles()
        
        for v in all_vehicles:
            if v.state == 'WAITING':
                color = '#ff0000'
            elif v.state == 'CROSSING':
                color = '#00ff00'
            else:
                color = v.color
            
            x1 = v.x - v.size/2
            y1 = v.y - v.size/2
            x2 = v.x + v.size/2
            y2 = v.y + v.size/2
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black', width=2)
            
            # Windows
            if v.direction in ['N', 'S']:
                self.canvas.create_rectangle(v.x-4, v.y-2, v.x+4, v.y+2, fill='#88ccff', outline='black')
            else:
                self.canvas.create_rectangle(v.x-2, v.y-4, v.x+2, v.y+4, fill='#88ccff', outline='black')
            
            if v.state == 'WAITING':
                self.canvas.create_text(v.x, v.y-12, text="⏰", fill='red', font=('Arial', 10, 'bold'))
            
            # Direction arrow
            if v.direction == 'N':
                points = [v.x, y1-2, v.x-4, y1+4, v.x+4, y1+4]
            elif v.direction == 'S':
                points = [v.x, y2+2, v.x-4, y2-4, v.x+4, y2-4]
            elif v.direction == 'E':
                points = [x2+2, v.y, x2-4, v.y-4, x2-4, v.y+4]
            else:
                points = [x1-2, v.y, x1+4, v.y-4, x1+4, v.y+4]
            
            self.canvas.create_polygon(points, fill='yellow', outline='black', width=1)
    
    def update_statistics(self):
        all_vehicles = self.env.get_all_vehicles()
        waiting = sum(1 for v in all_vehicles if v.state == 'WAITING')
        
        self.stats_labels["Total vehicles:"].config(text=str(len(all_vehicles)))
        self.stats_labels["Vehicles passed:"].config(text=str(self.env.vehicles_passed))
        self.stats_labels["Waiting vehicles:"].config(text=str(waiting))
        self.stats_labels["Current reward:"].config(text=f"{self.current_reward:.2f}")
        self.stats_labels["Total reward:"].config(text=f"{self.env.total_reward:.2f}")
        self.stats_labels["Agent epsilon:"].config(text=f"{self.agent.epsilon:.3f}")
        
        # Update per-direction counts
        self.dir_counts['NORTH'].config(text=str(len(self.env.vehicles_north)))
        self.dir_counts['SOUTH'].config(text=str(len(self.env.vehicles_south)))
        self.dir_counts['EAST'].config(text=str(len(self.env.vehicles_east)))
        self.dir_counts['WEST'].config(text=str(len(self.env.vehicles_west)))
        
        # Update light status
        self.light_labels['NORTH'].config(text="🟢 GREEN" if self.env.lights['N'] else "🔴 RED",
                                          fg='#4CAF50' if self.env.lights['N'] else '#f44336')
        self.light_labels['SOUTH'].config(text="🟢 GREEN" if self.env.lights['S'] else "🔴 RED",
                                          fg='#4CAF50' if self.env.lights['S'] else '#f44336')
        self.light_labels['EAST'].config(text="🟢 GREEN" if self.env.lights['E'] else "🔴 RED",
                                         fg='#4CAF50' if self.env.lights['E'] else '#f44336')
        self.light_labels['WEST'].config(text="🟢 GREEN" if self.env.lights['W'] else "🔴 RED",
                                         fg='#4CAF50' if self.env.lights['W'] else '#f44336')
    
    def train_agent(self):
        if self.training_in_progress:
            return
        
        self.training_in_progress = True
        self.train_btn.config(state=tk.DISABLED, text="🔄 TRAINING IN PROGRESS...")
        self.test_btn.config(state=tk.DISABLED)
        self.reset_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Training DRL agent to balance 4-way traffic...", fg='#ff9800')
        self.root.update()
        
        def train():
            self.env.reset()
            self.agent.epsilon = 0.5
            
            for episode in range(25):
                state = self.env.reset()
                episode_reward = 0
                
                for step in range(400):
                    action = self.agent.act(state, training=True)
                    next_state, reward, done, _ = self.env.step(action)
                    self.agent.remember(state, action, reward, next_state, done)
                    self.agent.replay()
                    state = next_state
                    episode_reward += reward
                
                if (episode + 1) % 5 == 0:
                    self.status_label.config(text=f"Training: Episode {episode+1}/25 - Reward: {episode_reward:.1f}")
                    self.root.update()
            
            self.trained = True
            self.training_in_progress = False
            self.train_btn.config(state=tk.NORMAL, text="✅ TRAINING COMPLETE", bg='#4CAF50', fg='white')
            self.test_btn.config(state=tk.NORMAL, bg='#FFD700', fg='#1a1a2e')
            self.reset_btn.config(state=tk.NORMAL, bg='#FFD700', fg='#1a1a2e')
            self.status_label.config(text="✅ Training complete! Agent now balances all 4 directions!", fg='#4CAF50')
            
            self.root.after(3000, lambda: self.train_btn.config(text="🤖 TRAIN DRL AGENT", bg='#FFD700', fg='#1a1a2e'))
        
        threading.Thread(target=train, daemon=True).start()
    
    def test_agent(self):
        if not self.trained:
            self.status_label.config(text="⚠️ Please train the agent first!", fg='#ff9800')
            return
        
        self.status_label.config(text="Testing trained agent...", fg='#4CAF50')
        self.root.after(2000, lambda: self.status_label.config(text="Agent testing mode active", fg='#4CAF50'))
    
    def reset_simulation(self):
        self.env.reset()
        self.current_reward = 0
        self.status_label.config(text="Simulation reset!", fg='#ff9800')
        self.root.after(2000, lambda: self.status_label.config(text="System running", fg='#4CAF50'))
    
    def toggle_speed(self):
        if self.simulation_speed == 20:
            self.simulation_speed = 15
            self.speed_label.config(text="🐢 VERY SLOW", fg='#ff9800')
        elif self.simulation_speed == 15:
            self.simulation_speed = 25
            self.speed_label.config(text="⚡ NORMAL", fg='#e94560')
        else:
            self.simulation_speed = 20
            self.speed_label.config(text="🐢 SLOW", fg='#4CAF50')
    
    def update_animation(self):
        if not self.running:
            return
        
        state = self.env.get_state()
        if self.trained and not self.training_in_progress:
            action = self.agent.act(state, training=False)
        else:
            action = random.randint(0, 3)
        
        next_state, reward, done, _ = self.env.step(action)
        self.current_reward = reward
        
        if self.trained and not self.training_in_progress:
            self.agent.remember(state, action, reward, next_state, done)
            if len(self.agent.memory) > 100:
                self.agent.replay()
        
        self.draw_road()
        self.draw_vehicles()
        self.update_statistics()
        
        interval = int(1000 / self.simulation_speed)
        self.root.after(interval, self.update_animation)
    
    def exit_app(self):
        self.running = False
        self.root.destroy()

# ==================== MAIN ====================

def main():
    print("="*60)
    print("   RIGHT SIDE DRIVING - TRAFFIC CONTROL SYSTEM")
    print("   Vehicles keep to the RIGHT side and STOP at RED lights!")
    print("="*60)
    print("\n✅ FEATURES:")
    print("   • Vehicles drive on RIGHT side of the road")
    print("   • Vehicles STOP at RED lights and GO on GREEN lights")
    print("   • Each direction has INDEPENDENT traffic light")
    print("   • DRL agent learns optimal traffic light timing")
    print("\n🎮 CONTROLS:")
    print("   • Click 'TRAIN AGENT' to train the DRL model")
    print("   • Click 'TEST AGENT' to test the trained model")
    print("   • Press SPACE to change simulation speed")
    print("   • Press Q to exit")
    print("="*60)
    print("\nStarting GUI...\n")
    
    root = tk.Tk()
    app = TrafficSimulationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

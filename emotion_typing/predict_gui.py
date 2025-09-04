import tkinter as tk
import time
import joblib
import pandas as pd
import random
import math
from colorsys import hsv_to_rgb

model = joblib.load("emotion_model.pkl")
keystrokes = []

def on_key(event):
    current_time = time.time()
    keystrokes.append(current_time)
    # Add ripple effect when typing
    if hasattr(background, 'create_ripple'):
        background.create_ripple(event.x_root - root.winfo_x(), event.y_root - root.winfo_y())

def predict_emotion():
    if len(keystrokes) < 2:
        result_label.config(text="❌ Not enough data.")
        return
    delays = [keystrokes[i] - keystrokes[i - 1] for i in range(1, len(keystrokes))]
    df = pd.DataFrame(delays, columns=["delay"])
    prediction = model.predict(df[["delay"]])
    result = prediction[0]
    result_label.config(text=f"🧠 Detected Emotion: {result}")
    # Create celebration effect on prediction
    if hasattr(background, 'create_celebration'):
        background.create_celebration()

class AnimatedBackground:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg='#222222')
        self.canvas.pack(fill="both", expand=True)
        
        # Set initial window size
        self.width = 800
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        
        # Create a frame for UI elements
        self.ui_frame = tk.Frame(self.canvas, bg='#222222', bd=0)
        self.ui_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Animation parameters
        self.hue = 0
        self.particles = []
        self.ripples = []
        self.celebration_items = []
        self.create_particles(40)
        
        # Start animations
        self.animate_background()
        self.animate_particles()
        self.animate_ripples()
        self.animate_celebration()

    def hsv_to_hex(self, h, s=1, v=1):
        r, g, b = hsv_to_rgb(h, s, v)
        return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
    
    def create_particles(self, count):
        colors = ['#ff3366', '#66ff33', '#3366ff', '#ff33cc', '#33ccff']
        for _ in range(count):
            self.particles.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.randint(3, 8),
                'speed': random.uniform(0.5, 2),
                'color': random.choice(colors),
                'direction': random.uniform(0, 2 * math.pi),
                'type': random.choice(['circle', 'star', 'triangle'])
            })
    
    def animate_background(self):
        self.hue = (self.hue + 0.003) % 1
        self.canvas.delete("bg")
        
        # Create gradient background
        for i in range(0, self.height, 2):
            ratio = i / self.height
            r = int(34 + (ratio * 100))
            g = int(40 + (ratio * 80))
            b = int(49 + (ratio * 60))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, self.width, i, fill=color, width=2, tags="bg")
        
        self.root.after(40, self.animate_background)
    
    def animate_particles(self):
        self.canvas.delete("particle")
        
        for particle in self.particles:
            particle['x'] += math.cos(particle['direction']) * particle['speed']
            particle['y'] += math.sin(particle['direction']) * particle['speed']
            
            if particle['x'] < 0 or particle['x'] > self.width:
                particle['direction'] = math.pi - particle['direction']
            if particle['y'] < 0 or particle['y'] > self.height:
                particle['direction'] = -particle['direction']
            
            if particle['type'] == 'circle':
                self.canvas.create_oval(
                    particle['x'] - particle['size'],
                    particle['y'] - particle['size'],
                    particle['x'] + particle['size'],
                    particle['y'] + particle['size'],
                    fill=particle['color'], outline="", tags="particle"
                )
            elif particle['type'] == 'star':
                self.draw_star(particle['x'], particle['y'], particle['size'], particle['color'])
            else:  # triangle
                self.draw_triangle(particle['x'], particle['y'], particle['size'], particle['color'])
        
        self.root.after(30, self.animate_particles)
    
    def draw_star(self, x, y, size, color):
        points = []
        for i in range(5):
            angle = 4 * math.pi * i / 5
            points.extend([
                x + size * math.cos(angle),
                y + size * math.sin(angle)
            ])
            angle = 4 * math.pi * (i + 0.5) / 5
            points.extend([
                x + size/2 * math.cos(angle),
                y + size/2 * math.sin(angle)
            ])
        self.canvas.create_polygon(points, fill=color, outline="", tags="particle")
    
    def draw_triangle(self, x, y, size, color):
        points = [
            x, y - size,
            x - size * math.sqrt(3)/2, y + size/2,
            x + size * math.sqrt(3)/2, y + size/2
        ]
        self.canvas.create_polygon(points, fill=color, outline="", tags="particle")

    def create_ripple(self, x, y):
        self.ripples.append({
            'x': x,
            'y': y,
            'size': 5,
            'color': self.hsv_to_hex(random.random(), 0.8, 0.9),
            'alpha': 1.0
        })
    
    def animate_ripples(self):
        self.canvas.delete("ripple")
        new_ripples = []
        
        for ripple in self.ripples:
            ripple['size'] += 3
            ripple['alpha'] -= 0.03
            
            if ripple['alpha'] > 0:
                self.canvas.create_oval(
                    ripple['x'] - ripple['size'],
                    ripple['y'] - ripple['size'],
                    ripple['x'] + ripple['size'],
                    ripple['y'] + ripple['size'],
                    outline=ripple['color'], width=2, tags="ripple"
                )
                new_ripples.append(ripple)
        
        self.ripples = new_ripples
        self.root.after(30, self.animate_ripples)
    
    def create_celebration(self):
        for _ in range(20):
            self.celebration_items.append({
                'x': random.randint(100, self.width-100),
                'y': self.height,
                'size': random.randint(5, 15),
                'color': self.hsv_to_hex(random.random(), 0.9, 0.9),
                'speed': random.uniform(2, 5),
                'type': random.choice(['circle', 'star', 'triangle'])
            })
    
    def animate_celebration(self):
        self.canvas.delete("celebration")
        new_items = []
        
        for item in self.celebration_items:
            item['y'] -= item['speed']
            item['x'] += random.uniform(-1, 1)
            
            if item['y'] > 0:
                if item['type'] == 'circle':
                    self.canvas.create_oval(
                        item['x'] - item['size'],
                        item['y'] - item['size'],
                        item['x'] + item['size'],
                        item['y'] + item['size'],
                        fill=item['color'], outline="", tags="celebration"
                    )
                elif item['type'] == 'star':
                    self.draw_star(item['x'], item['y'], item['size'], item['color'])
                else:  # triangle
                    self.draw_triangle(item['x'], item['y'], item['size'], item['color'])
                new_items.append(item)
        
        self.celebration_items = new_items
        self.root.after(30, self.animate_celebration)

# Create main window
root = tk.Tk()
root.title("Emotion Detector")
root.geometry("800x600")

# Create animated background
background = AnimatedBackground(root)

# Add UI elements to the frame
tk.Label(background.ui_frame, 
         text="Emotion Detection from Keystrokes", 
         font=('Arial', 18, 'bold'), 
         bg='#222222', fg='#ffffff').pack(pady=(0,10))

tk.Label(background.ui_frame, 
         text="Type a sentence below, then click Predict", 
         font=('Arial', 12), 
         bg='#222222', fg='#aaaaaa').pack()

text_box = tk.Text(background.ui_frame, height=10, width=50, 
                  font=('Arial', 12), 
                  bg='#333333', fg='#ffffff',
                  insertbackground='#ffffff',
                  relief=tk.FLAT, highlightthickness=2,
                  highlightbackground='#666666', highlightcolor='#ff3366')
text_box.pack(pady=10)
text_box.bind("<Key>", on_key)

predict_btn = tk.Button(background.ui_frame, text="PREDICT EMOTION", 
                       command=predict_emotion,
                       font=('Arial', 14, 'bold'),
                       bg='#ff3366', fg='white',
                       activebackground='#ff5588', activeforeground='white',
                       relief=tk.FLAT, padx=30, pady=10, bd=0)
predict_btn.pack(pady=20)

result_label = tk.Label(background.ui_frame, text="", 
                       font=('Arial', 14, 'bold'), 
                       bg='#222222', fg='#ffcc00')
result_label.pack(pady=10)

root.mainloop()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import os
import base64
from io import BytesIO

# Create a doctor-themed background image using base64 encoded data
def create_medical_theme():
    # This would normally be an actual image, but we'll create a simple colored background
    return None

class XRayAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical X-Ray Diagnosis Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg='#e0f0ff')
        
        # Medical-themed colors
        self.colors = {
            'bg': '#e0f0ff',
            'header_bg': '#0066cc',
            'header_fg': 'white',
            'button_bg': '#0066cc',
            'button_fg': 'white',
            'result_bg': '#f0f8ff',
            'result_fg': '#003366'
        }
        
        # Conditions we might detect
        self.CONDITIONS = {
            0: {"name": "Normal", "desc": "No abnormalities detected."},
            1: {"name": "Pneumonia", "desc": "Lung inflammation detected. Consult a pulmonologist."},
            2: {"name": "Fracture", "desc": "Bone fracture detected. Consult an orthopedist."},
            3: {"name": "Other Abnormality", "desc": "Unusual finding detected. Further tests recommended."}
        }
        
        self.setup_ui()
        self.image_path = None
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors['header_bg'], height=100)
        header.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header, text="Medical X-Ray Diagnosis Assistant", 
                        font=("Arial", 20, "bold"), fg=self.colors['header_fg'], 
                        bg=self.colors['header_bg'])
        title.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instructions
        instructions = tk.Label(main_frame, 
                               text="Drag and drop or select an X-Ray image for analysis.\nThe AI will identify potential issues and highlight areas of concern.",
                               font=("Arial", 12), wraplength=600, justify=tk.CENTER,
                               bg=self.colors['bg'], fg='#333333')
        instructions.pack(pady=(0, 20))
        
        # Image display area
        img_frame = tk.Frame(main_frame, bg='white', relief=tk.SUNKEN, bd=2)
        img_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(img_frame, bg='white', width=400, height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas_text = self.canvas.create_text(200, 150, 
                                                  text="Drag X-Ray image here\nor click to select",
                                                  font=("Arial", 12), fill='gray',
                                                  justify=tk.CENTER)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        self.select_btn = tk.Button(button_frame, text="Select Image", 
                                   command=self.select_image,
                                   bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                                   font=("Arial", 12, "bold"), padx=20, pady=10)
        self.select_btn.pack(side=tk.LEFT, padx=10)
        
        self.analyze_btn = tk.Button(button_frame, text="Analyze Image", 
                                    command=self.analyze_image,
                                    bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                                    font=("Arial", 12, "bold"), padx=20, pady=10,
                                    state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.LEFT, padx=10)
        
        # Results area
        results_frame = tk.LabelFrame(main_frame, text="Analysis Results", 
                                     font=("Arial", 14, "bold"),
                                     bg=self.colors['bg'], fg=self.colors['result_fg'])
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(results_frame, height=8, font=("Arial", 11),
                                  bg=self.colors['result_bg'], fg=self.colors['result_fg'],
                                  wrap=tk.WORD, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.result_text.insert(tk.END, "Results will appear here after analysis.")
        self.result_text.config(state=tk.DISABLED)
        
        # Footer
        footer = tk.Frame(self.root, bg=self.colors['header_bg'], height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        disclaimer = tk.Label(footer, text="Note: This is a demonstration tool. Always consult a medical professional for diagnosis.",
                             font=("Arial", 9), fg=self.colors['header_fg'], 
                             bg=self.colors['header_bg'])
        disclaimer.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Configure drag and drop
        self.setup_drag_drop()
        
    def setup_drag_drop(self):
        self.canvas.bind("<Button-1>", self.select_image)
        
    def select_image(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Select X-Ray Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
        )
        if file_path:
            self.load_image(file_path)
            
    def load_image(self, file_path):
        self.image_path = file_path
        try:
            # For demonstration, we'll just show the file name
            # In a real application, you would load and display the image
            self.canvas.delete(self.canvas_text)
            filename = os.path.basename(file_path)
            self.canvas.create_text(200, 150, anchor=tk.CENTER, 
                                   text=f"Loaded: {filename}\n\nClick 'Analyze Image' to process",
                                   font=("Arial", 12), fill='black')
            self.analyze_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            
    def analyze_image(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please select an image first.")
            return
            
        try:
            # Show loading message
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Analyzing image... Please wait.")
            self.result_text.config(state=tk.DISABLED)
            self.root.update()
            
            # Simulate analysis delay
            self.root.after(2000, self.show_results)
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            
    def show_results(self):
        # Simulate analysis with random results for demonstration
        condition_idx = random.randint(0, 3)
        confidence = random.uniform(0.7, 0.95)
        
        condition = self.CONDITIONS[condition_idx]
        
        # Update results text
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        result_message = f"Diagnosis: {condition['name']}\n\n"
        result_message += f"Confidence: {confidence*100:.2f}%\n\n"
        result_message += f"Description: {condition['desc']}\n\n"
        result_message += "Note: This analysis is for demonstration purposes only.\n"
        result_message += "Please consult a medical professional for accurate diagnosis."
        
        self.result_text.insert(tk.END, result_message)
        self.result_text.config(state=tk.DISABLED)
        
        # Simulate highlighting areas on the canvas
        self.highlight_areas(condition_idx)
            
    def highlight_areas(self, condition_idx):
        # Clear canvas
        self.canvas.delete("all")
        
        # Display a simple representation of an X-ray
        self.canvas.create_rectangle(50, 50, 350, 250, fill="gray", outline="black")
        
        # Draw a simple body outline
        self.canvas.create_oval(150, 70, 250, 120, outline="white", width=2)  # Head
        self.canvas.create_rectangle(175, 120, 225, 200, outline="white", width=2)  # Torso
        
        # Draw "affected" areas based on condition
        if condition_idx == 0:  # Normal
            # Draw a green checkmark
            self.canvas.create_line(300, 70, 280, 90, fill="green", width=3)
            self.canvas.create_line(280, 90, 260, 70, fill="green", width=3)
            self.canvas.create_text(200, 230, text="No issues detected", fill="green", font=("Arial", 12, "bold"))
        elif condition_idx == 1:  # Pneumonia
            # Draw lung areas with red highlights
            self.canvas.create_oval(160, 130, 190, 160, outline="red", width=3)
            self.canvas.create_oval(210, 130, 240, 160, outline="red", width=3)
            self.canvas.create_text(200, 180, text="Lung inflammation detected", fill="red", font=("Arial", 10, "bold"))
        elif condition_idx == 2:  # Fracture
            # Draw a bone with fracture
            self.canvas.create_line(130, 130, 130, 200, fill="white", width=4)  # Arm bone
            self.canvas.create_line(130, 160, 120, 165, fill="red", width=3)  # Fracture line
            self.canvas.create_text(130, 220, text="Fracture detected", fill="red", font=("Arial", 10, "bold"))
        else:  # Other abnormality
            # Draw random highlighted areas
            for _ in range(3):
                x = random.randint(60, 340)
                y = random.randint(60, 240)
                self.canvas.create_oval(x-10, y-10, x+10, y+10, outline="red", width=2)
            self.canvas.create_text(200, 230, text="Abnormalities detected", fill="red", font=("Arial", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    app = XRayAnalyzer(root)
    root.mainloop()

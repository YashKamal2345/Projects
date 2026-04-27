import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import pytesseract
import re
from datetime import datetime
import threading
import time
import os
import random
import math

# PDF Support
try:
    import fitz
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Configure Tesseract - UPDATE THIS PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class AnimatedDoctor:
    """Professional animated doctor character"""
    
    def __init__(self, canvas, x, y, size=180):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.animation_running = True
        self.expression = "happy"
        self.create_doctor()
        self.start_blinking()
        self.start_idle_animation()
    
    def create_doctor(self):
        """Create detailed doctor character"""
        # White lab coat - body
        self.body = self.canvas.create_rectangle(
            self.x - self.size//3, self.y - self.size//5,
            self.x + self.size//3, self.y + self.size//1.8,
            fill='#FFFFFF', outline='#BDC3C7', width=2, tags='doctor'
        )
        
        # Lab coat details (buttons)
        self.button1 = self.canvas.create_oval(
            self.x - 5, self.y + self.size//8,
            self.x + 5, self.y + self.size//8 + 10,
            fill='#2C3E50', outline='#2C3E50', tags='doctor'
        )
        self.button2 = self.canvas.create_oval(
            self.x - 5, self.y + self.size//5,
            self.x + 5, self.y + self.size//5 + 10,
            fill='#2C3E50', outline='#2C3E50', tags='doctor'
        )
        
        # Collar
        self.collar_left = self.canvas.create_polygon(
            self.x - self.size//4, self.y - self.size//8,
            self.x - self.size//8, self.y - self.size//8 + 15,
            self.x, self.y - self.size//8,
            fill='#ECF0F1', outline='#BDC3C7', tags='doctor'
        )
        self.collar_right = self.canvas.create_polygon(
            self.x + self.size//4, self.y - self.size//8,
            self.x + self.size//8, self.y - self.size//8 + 15,
            self.x, self.y - self.size//8,
            fill='#ECF0F1', outline='#BDC3C7', tags='doctor'
        )
        
        # Head
        self.head = self.canvas.create_oval(
            self.x - self.size//3, self.y - self.size//1.8,
            self.x + self.size//3, self.y - self.size//6,
            fill='#FDDCB5', outline='#D4A574', width=2, tags='doctor'
        )
        
        # Hair
        self.hair = self.canvas.create_arc(
            self.x - self.size//3, self.y - self.size//1.8 - 5,
            self.x + self.size//3, self.y - self.size//6,
            start=0, extent=180, fill='#4A3728', outline='#4A3728', tags='doctor'
        )
        
        # Stethoscope
        self.steth_tube = self.canvas.create_line(
            self.x, self.y - self.size//4,
            self.x, self.y + self.size//6,
            fill='#2C3E50', width=3, tags='doctor',
            smooth=True
        )
        self.steth_head = self.canvas.create_oval(
            self.x - self.size//6, self.y + self.size//6 - self.size//10,
            self.x + self.size//6, self.y + self.size//6 + self.size//10,
            fill='#BDC3C7', outline='#2C3E50', width=2, tags='doctor'
        )
        
        # ID Badge
        self.badge = self.canvas.create_rectangle(
            self.x - self.size//5, self.y + self.size//9,
            self.x + self.size//5, self.y + self.size//4,
            fill='#1A73E8', outline='#0D47A1', width=1, tags='doctor'
        )
        self.badge_text = self.canvas.create_text(
            self.x, self.y + self.size//6,
            text="MediAI\nDr.", fill='white', 
            font=('Arial', int(self.size/15), 'bold'), tags='doctor'
        )
        
        # Eyes
        eye_offset = self.size//7
        eye_size = self.size//12
        
        self.left_eye = self.canvas.create_oval(
            self.x - eye_offset - eye_size, self.y - self.size//3.5,
            self.x - eye_offset + eye_size, self.y - self.size//3.5 + eye_size*2,
            fill='white', outline='#2C3E50', width=1, tags='doctor'
        )
        self.right_eye = self.canvas.create_oval(
            self.x + eye_offset - eye_size, self.y - self.size//3.5,
            self.x + eye_offset + eye_size, self.y - self.size//3.5 + eye_size*2,
            fill='white', outline='#2C3E50', width=1, tags='doctor'
        )
        
        # Pupils
        self.left_pupil = self.canvas.create_oval(
            self.x - eye_offset - eye_size//2, self.y - self.size//3.5 + eye_size//2,
            self.x - eye_offset, self.y - self.size//3.5 + eye_size*1.5,
            fill='#2C3E50', tags='doctor'
        )
        self.right_pupil = self.canvas.create_oval(
            self.x + eye_offset - eye_size//2, self.y - self.size//3.5 + eye_size//2,
            self.x + eye_offset, self.y - self.size//3.5 + eye_size*1.5,
            fill='#2C3E50', tags='doctor'
        )
        
        # Glasses (optional - looks more professional)
        self.left_glass = self.canvas.create_oval(
            self.x - eye_offset - eye_size - 2, self.y - self.size//3.5 - 2,
            self.x - eye_offset + eye_size + 2, self.y - self.size//3.5 + eye_size*2 + 2,
            outline='#1A73E8', width=2, tags='doctor'
        )
        self.right_glass = self.canvas.create_oval(
            self.x + eye_offset - eye_size - 2, self.y - self.size//3.5 - 2,
            self.x + eye_offset + eye_size + 2, self.y - self.size//3.5 + eye_size*2 + 2,
            outline='#1A73E8', width=2, tags='doctor'
        )
        self.glass_bridge = self.canvas.create_line(
            self.x - eye_offset - eye_size//2, self.y - self.size//3.5 + eye_size,
            self.x + eye_offset - eye_size//2, self.y - self.size//3.5 + eye_size,
            fill='#1A73E8', width=2, tags='doctor'
        )
        
        # Mouth (happy by default)
        self.mouth = self.canvas.create_arc(
            self.x - self.size//8, self.y - self.size//4,
            self.x + self.size//8, self.y - self.size//6,
            start=0, extent=-180, fill='#8B6914', outline='#8B6914', tags='doctor'
        )
        
        # Name tag
        self.name_tag = self.canvas.create_text(
            self.x, self.y + self.size//1.5,
            text="Dr. MediAI\nYour AI Doctor", fill='#1A73E8',
            font=('Arial', int(self.size/20), 'bold'), tags='doctor'
        )
    
    def start_blinking(self):
        """Animate blinking eyes"""
        def blink():
            if self.animation_running:
                self.canvas.itemconfig(self.left_pupil, state='hidden')
                self.canvas.itemconfig(self.right_pupil, state='hidden')
                self.canvas.after(150, lambda: self.canvas.itemconfig(self.left_pupil, state='normal'))
                self.canvas.after(150, lambda: self.canvas.itemconfig(self.right_pupil, state='normal'))
                self.canvas.after(3000, blink)
        blink()
    
    def start_idle_animation(self):
        """Subtle idle animation"""
        def animate():
            if self.animation_running:
                # Slight head tilt
                current_coords = self.canvas.coords(self.head)
                if current_coords:
                    # Gentle sway
                    pass
                self.canvas.after(5000, animate)
        animate()
    
    def set_expression(self, expression):
        """Change doctor's expression"""
        self.expression = expression
        if expression == "happy":
            self.canvas.itemconfig(self.mouth, start=0, extent=-180)
        elif expression == "thinking":
            self.canvas.itemconfig(self.mouth, start=0, extent=-90)
            self.show_thought_bubble("Analyzing...")
        elif expression == "worried":
            self.canvas.itemconfig(self.mouth, start=180, extent=180)
        elif expression == "speaking":
            self.canvas.itemconfig(self.mouth, start=0, extent=-120)
            self.animate_speech()
    
    def show_thought_bubble(self, text):
        """Show thought bubble"""
        bubble = self.canvas.create_oval(
            self.x - self.size//2, self.y - self.size - 30,
            self.x + self.size//2, self.y - self.size//1.5 - 30,
            fill='white', outline='#BDC3C7', width=1, tags='bubble'
        )
        bubble_text = self.canvas.create_text(
            self.x, self.y - self.size - 15,
            text=text, font=('Arial', 10), fill='#2C3E50', tags='bubble'
        )
        self.canvas.after(3000, lambda: self.canvas.delete('bubble'))
    
    def animate_speech(self):
        """Animate speaking mouth"""
        def speak():
            if self.expression == "speaking" and self.animation_running:
                self.canvas.itemconfig(self.mouth, start=0, extent=-120)
                self.canvas.after(200, lambda: self.canvas.itemconfig(self.mouth, start=0, extent=-180))
                self.canvas.after(500, speak)
        speak()
    
    def stop(self):
        self.animation_running = False

class CollapsibleSection:
    """Animated collapsible section for report categories"""
    
    def __init__(self, parent, title, icon, bg_color, text_color="#2C3E50"):
        self.parent = parent
        self.title = title
        self.icon = icon
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_expanded = False
        self.frame = None
        self.content_frame = None
        self.content_height = 0
        
        self.create_header()
    
    def create_header(self):
        """Create clickable header for section"""
        self.frame = tk.Frame(self.parent, bg=self.bg_color, relief=tk.RAISED, bd=1)
        self.frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Header button with hover effect
        self.header_btn = tk.Button(
            self.frame, 
            text=f"{self.icon}  {self.title}  ▶", 
            font=('Segoe UI', 12, 'bold'),
            bg=self.bg_color, 
            fg=self.text_color,
            anchor=tk.W,
            padx=15, pady=12,
            cursor='hand2',
            relief=tk.FLAT,
            command=self.toggle
        )
        self.header_btn.pack(fill=tk.X)
        
        # Hover effect
        def on_enter(e):
            self.header_btn.config(bg=self._darken_color(self.bg_color))
        
        def on_leave(e):
            if not self.is_expanded:
                self.header_btn.config(bg=self.bg_color)
            else:
                self.header_btn.config(bg=self.bg_color)
        
        self.header_btn.bind("<Enter>", on_enter)
        self.header_btn.bind("<Leave>", on_leave)
    
    def _darken_color(self, color):
        """Darken a color for hover effect"""
        if color == "#E8F4FD":
            return "#D0E8F5"
        elif color == "#FFF3E0":
            return "#FFE0B5"
        elif color == "#E8F5E9":
            return "#D0E8D0"
        elif color == "#FCE4EC":
            return "#F8BBD0"
        elif color == "#E3F2FD":
            return "#BBDEFB"
        return "#E0E0E0"
    
    def toggle(self):
        """Toggle section expansion with animation"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
    
    def expand(self):
        """Expand section with animation"""
        if self.content_frame:
            self.content_frame.destroy()
        
        self.content_frame = tk.Frame(self.frame, bg='white')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add content (to be filled by parent)
        self.on_expand(self.content_frame)
        
        self.header_btn.config(text=f"{self.icon}  {self.title}  ▼")
        self.is_expanded = True
        
        # Animate expansion
        self.animate_expand()
    
    def animate_expand(self):
        """Animate the expansion"""
        self.content_frame.update_idletasks()
        self.content_height = self.content_frame.winfo_reqheight()
        # Height animation would go here, but tkinter doesn't support it easily
        # We'll just show it directly
    
    def collapse(self):
        """Collapse section"""
        if self.content_frame:
            self.content_frame.destroy()
            self.content_frame = None
        self.header_btn.config(text=f"{self.icon}  {self.title}  ▶")
        self.is_expanded = False
    
    def on_expand(self, container):
        """Override this method to add content"""
        pass

class MedicalReportSystem:
    """Main application with animated collapsible sections"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MediAI Diabetes Care System - Interactive Medical Report")
        self.root.geometry("1500x950")
        self.root.configure(bg='#F0F4F8')
        
        self.analyzer = MedicalReportAnalyzer()
        self.selected_file = None
        self.report_data = None
        
        self.setup_ui()
        self.animate_background()
    
    def setup_ui(self):
        """Setup main UI with doctor avatar and report sections"""
        
        # Main container
        main_container = tk.Frame(self.root, bg='#F0F4F8')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top header with gradient
        header = tk.Frame(main_container, height=80, bg='#1A5276')
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🏥 MediAI Interactive Diabetes Care System", 
                        font=('Segoe UI', 20, 'bold'), bg='#1A5276', fg='white')
        title.pack(expand=True)
        
        # Content area with two columns
        content = tk.Frame(main_container, bg='#F0F4F8')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # LEFT PANEL - Doctor Avatar and Upload
        left_panel = tk.Frame(content, width=380, bg='white', relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Doctor Avatar Canvas
        doctor_canvas_frame = tk.Frame(left_panel, bg='#E8F4FD', padx=20, pady=20)
        doctor_canvas_frame.pack(fill=tk.X)
        
        self.doctor_canvas = tk.Canvas(doctor_canvas_frame, width=340, height=320, 
                                        bg='#E8F4FD', highlightthickness=0)
        self.doctor_canvas.pack()
        
        # Create animated doctor
        self.doctor = AnimatedDoctor(self.doctor_canvas, 170, 160, 160)
        
        # Speech bubble
        speech_frame = tk.Frame(left_panel, bg='#F0F3F4', relief=tk.GROOVE, bd=1)
        speech_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.speech_label = tk.Label(speech_frame, 
                                     text="👨‍⚕️ Hello! I'm Dr. MediAI.\nUpload your medical report\nfor a complete analysis!",
                                     font=('Segoe UI', 11), bg='#F0F3F4',
                                     fg='#2C3E50', wraplength=300, justify=tk.CENTER)
        self.speech_label.pack(pady=15)
        
        # Upload area
        upload_frame = tk.Frame(left_panel, bg='white', padx=20, pady=20)
        upload_frame.pack(fill=tk.X)
        
        upload_icon = tk.Label(upload_frame, text="📋📄", font=('Segoe UI', 40), bg='white')
        upload_icon.pack()
        
        self.upload_btn = tk.Button(upload_frame, text="📎 UPLOAD MEDICAL REPORT", 
                                    command=self.upload_file,
                                    font=('Segoe UI', 12, 'bold'),
                                    bg='#1A73E8', fg='white',
                                    padx=20, pady=12,
                                    cursor='hand2',
                                    relief=tk.FLAT)
        self.upload_btn.pack(pady=10, fill=tk.X)
        
        self.file_label = tk.Label(upload_frame, text="No file selected\nSupported: PDF, JPG, PNG",
                                  font=('Segoe UI', 9), bg='white', fg='#7F8C8D')
        self.file_label.pack()
        
        # Generate button
        self.generate_btn = tk.Button(left_panel, text="🔬 GENERATE INTERACTIVE REPORT", 
                                      command=self.generate_report,
                                      font=('Segoe UI', 13, 'bold'),
                                      bg='#4CAF50', fg='white',
                                      padx=20, pady=15,
                                      cursor='hand2',
                                      state=tk.DISABLED,
                                      relief=tk.FLAT)
        self.generate_btn.pack(fill=tk.X, padx=20, pady=20)
        
        # Loading indicator
        self.loading_frame = tk.Frame(left_panel, bg='white')
        self.loading_frame.pack(fill=tk.X, padx=20, pady=10)
        self.loading_frame.pack_forget()
        
        self.progress = ttk.Progressbar(self.loading_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=5)
        
        self.loading_text = tk.Label(self.loading_frame, text="Analyzing medical report...",
                                     font=('Segoe UI', 9), bg='white', fg='#1A73E8')
        self.loading_text.pack()
        
        # RIGHT PANEL - Interactive Report Sections
        right_panel = tk.Frame(content, bg='white', relief=tk.RAISED, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Scrollable area for sections
        canvas_frame = tk.Frame(right_panel, bg='white')
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store sections
        self.sections = []
        
        # Create collapsible sections
        self.create_info_sections()
        
        # Show welcome message
        self.show_welcome_message()
        
        # Status bar
        status_bar = tk.Frame(main_container, height=30, bg='#2C3E50')
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_bar, text="✅ System Ready", 
                                     font=('Segoe UI', 9), bg='#2C3E50', fg='white')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        version_label = tk.Label(status_bar, text="Interactive Version 5.0", 
                                 font=('Segoe UI', 9), bg='#2C3E50', fg='white')
        version_label.pack(side=tk.RIGHT, padx=10)
    
    def create_info_sections(self):
        """Create all collapsible sections"""
        
        sections_config = [
            ("📋", "PATIENT INFORMATION", "#E8F4FD"),
            ("🩸", "LABORATORY FINDINGS", "#FFF3E0"),
            ("🏥", "DIAGNOSIS ASSESSMENT", "#E8F5E9"),
            ("💊", "TREATMENT PLAN", "#FCE4EC"),
            ("🥗", "DIET & NUTRITION", "#E3F2FD"),
            ("💪", "EXERCISE PRESCRIPTION", "#F3E5F5"),
            ("📊", "MONITORING SCHEDULE", "#FFF8E1"),
            ("📅", "FOLLOW-UP SCHEDULE", "#E0F7FA"),
            ("🚨", "EMERGENCY WARNING SIGNS", "#FFEBEE"),
            ("✅", "ACTION ITEMS", "#E8EAF6")
        ]
        
        for icon, title, color in sections_config:
            section = CollapsibleSection(self.scrollable_frame, title, icon, color)
            section.on_expand = lambda container, t=title: self.populate_section(container, t)
            self.sections.append(section)
    
    def populate_section(self, container, section_title):
        """Populate a section with content"""
        
        if not self.report_data:
            label = tk.Label(container, text="Generate a report first to see content here.",
                            font=('Segoe UI', 11), bg='white', fg='#7F8C8D')
            label.pack(pady=20)
            return
        
        data = self.report_data
        
        if section_title == "PATIENT INFORMATION":
            self.create_patient_info(container, data)
        elif section_title == "LABORATORY FINDINGS":
            self.create_lab_findings(container, data)
        elif section_title == "DIAGNOSIS ASSESSMENT":
            self.create_diagnosis(container, data)
        elif section_title == "TREATMENT PLAN":
            self.create_treatment(container, data)
        elif section_title == "DIET & NUTRITION":
            self.create_diet(container, data)
        elif section_title == "EXERCISE PRESCRIPTION":
            self.create_exercise(container, data)
        elif section_title == "MONITORING SCHEDULE":
            self.create_monitoring(container, data)
        elif section_title == "FOLLOW-UP SCHEDULE":
            self.create_followup(container, data)
        elif section_title == "EMERGENCY WARNING SIGNS":
            self.create_emergency(container, data)
        elif section_title == "ACTION ITEMS":
            self.create_actions(container, data)
    
    def create_patient_info(self, container, data):
        """Create patient information display"""
        info_frame = tk.Frame(container, bg='white')
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        params = [
            ("Age", data.get('age', 'Not provided'), "years"),
            ("Weight", data.get('weight', 'Not provided'), "kg"),
            ("Height", data.get('height', 'Not provided'), "cm"),
            ("BMI", data.get('bmi', 'Not calculable'), ""),
            ("Blood Pressure", data.get('bp', 'Not provided'), "mmHg"),
            ("Analysis Date", datetime.now().strftime('%Y-%m-%d %H:%M'), "")
        ]
        
        for i, (label, value, unit) in enumerate(params):
            row = tk.Frame(info_frame, bg='white')
            row.pack(fill=tk.X, pady=8)
            
            tk.Label(row, text=f"• {label}:", font=('Segoe UI', 11, 'bold'),
                    bg='white', fg='#2C3E50', width=18, anchor=tk.W).pack(side=tk.LEFT)
            
            value_text = f"{value} {unit}" if value != 'Not provided' else "Not provided"
            tk.Label(row, text=value_text, font=('Segoe UI', 11),
                    bg='white', fg='#1A73E8').pack(side=tk.LEFT)
    
    def create_lab_findings(self, container, data):
        """Create laboratory findings display"""
        findings = data.get('findings', [])
        
        for finding in findings:
            frame = tk.Frame(container, bg='white')
            frame.pack(fill=tk.X, pady=5, padx=10)
            
            tk.Label(frame, text=finding, font=('Segoe UI', 10),
                    bg='white', fg='#2C3E50', wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)
    
    def create_diagnosis(self, container, data):
        """Create diagnosis display"""
        diagnosis = data.get('diagnosis', {})
        
        # Status card
        status_color = {
            'DIABETES': '#FFEBEE',
            'PRE-DIABETES': '#FFF3E0',
            'NORMAL': '#E8F5E9'
        }.get(diagnosis.get('status', 'NORMAL'), '#F5F5F5')
        
        status_frame = tk.Frame(container, bg=status_color, relief=tk.GROOVE, bd=1)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(status_frame, text=f"🏥 Primary Diagnosis: {diagnosis.get('status', 'Unknown')}",
                font=('Segoe UI', 13, 'bold'), bg=status_color, fg='#2C3E50').pack(pady=10)
        
        tk.Label(status_frame, text=f"Type: {diagnosis.get('type', 'Unknown')}",
                font=('Segoe UI', 11), bg=status_color, fg='#2C3E50').pack(pady=5)
        
        tk.Label(status_frame, text=f"Severity: {diagnosis.get('severity', 'Unknown')}",
                font=('Segoe UI', 11), bg=status_color, fg='#2C3E50').pack(pady=5)
    
    def create_treatment(self, container, data):
        """Create treatment plan display"""
        treatments = data.get('treatments', [])
        
        for treatment in treatments:
            frame = tk.Frame(container, bg='white')
            frame.pack(fill=tk.X, pady=8, padx=10)
            
            tk.Label(frame, text=f"💊 {treatment}", font=('Segoe UI', 10),
                    bg='white', fg='#2C3E50', wraplength=650, justify=tk.LEFT).pack(anchor=tk.W)
    
    def create_diet(self, container, data):
        """Create diet plan display"""
        diet = data.get('diet', {})
        
        meals = [
            ("Breakfast", diet.get('breakfast', 'Balanced breakfast')),
            ("Lunch", diet.get('lunch', 'Nutritious lunch')),
            ("Dinner", diet.get('dinner', 'Healthy dinner')),
            ("Snacks", diet.get('snacks', 'Healthy snacks'))
        ]
        
        for meal_name, meal_desc in meals:
            frame = tk.Frame(container, bg='#F8F9FA', relief=tk.GROOVE, bd=1)
            frame.pack(fill=tk.X, padx=10, pady=8)
            
            tk.Label(frame, text=f"🍽️ {meal_name}:", font=('Segoe UI', 11, 'bold'),
                    bg='#F8F9FA', fg='#2C3E50').pack(anchor=tk.W, padx=10, pady=5)
            
            tk.Label(frame, text=meal_desc, font=('Segoe UI', 10),
                    bg='#F8F9FA', fg='#555', wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)
    
    def create_exercise(self, container, data):
        """Create exercise plan display"""
        exercises = data.get('exercise', [])
        
        for ex in exercises:
            frame = tk.Frame(container, bg='white')
            frame.pack(fill=tk.X, pady=6, padx=10)
            
            tk.Label(frame, text=f"🏃 {ex}", font=('Segoe UI', 10),
                    bg='white', fg='#2C3E50', wraplength=650, justify=tk.LEFT).pack(anchor=tk.W)
    
    def create_monitoring(self, container, data):
        """Create monitoring schedule display"""
        monitoring = data.get('monitoring', [])
        
        for item in monitoring:
            frame = tk.Frame(container, bg='#E3F2FD', relief=tk.GROOVE, bd=1)
            frame.pack(fill=tk.X, padx=10, pady=6)
            
            tk.Label(frame, text=f"📊 {item}", font=('Segoe UI', 10),
                    bg='#E3F2FD', fg='#2C3E50', wraplength=650, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=8)
    
    def create_followup(self, container, data):
        """Create follow-up schedule display"""
        followup = data.get('followup', [])
        
        for item in followup:
            frame = tk.Frame(container, bg='white')
            frame.pack(fill=tk.X, pady=6, padx=10)
            
            tk.Label(frame, text=f"📅 {item}", font=('Segoe UI', 10),
                    bg='white', fg='#2C3E50', wraplength=650, justify=tk.LEFT).pack(anchor=tk.W)
    
    def create_emergency(self, container, data):
        """Create emergency warnings display"""
        emergencies = data.get('emergency', [])
        
        for item in emergencies:
            frame = tk.Frame(container, bg='#FFEBEE', relief=tk.GROOVE, bd=1)
            frame.pack(fill=tk.X, padx=10, pady=6)
            
            tk.Label(frame, text=f"🚨 {item}", font=('Segoe UI', 10, 'bold'),
                    bg='#FFEBEE', fg='#C62828', wraplength=650, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=8)
    
    def create_actions(self, container, data):
        """Create action items display"""
        actions = data.get('actions', [])
        
        for i, action in enumerate(actions, 1):
            frame = tk.Frame(container, bg='#E8EAF6', relief=tk.GROOVE, bd=1)
            frame.pack(fill=tk.X, padx=10, pady=6)
            
            tk.Label(frame, text=f"✅ {i}. {action}", font=('Segoe UI', 10),
                    bg='#E8EAF6', fg='#2C3E50', wraplength=650, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=8)
    
    def show_welcome_message(self):
        """Show welcome message in first section"""
        welcome_frame = tk.Frame(self.scrollable_frame, bg='white')
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        welcome_text = """
╔══════════════════════════════════════════════════════════════════╗
║                    WELCOME TO INTERACTIVE REPORT                 ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   📋 Click on any category above to expand and view details     ║
║                                                                  ║
║   🏥 HOW TO USE:                                                ║
║      1. Upload your medical report (PDF or Image)               ║
║      2. Click "Generate Interactive Report"                     ║
║      3. Click on any section to expand and view detailed info   ║
║                                                                  ║
║   📊 SECTIONS AVAILABLE:                                        ║
║      • Patient Information                                      ║
║      • Laboratory Findings                                      ║
║      • Diagnosis Assessment                                     ║
║      • Treatment Plan                                           ║
║      • Diet & Nutrition                                         ║
║      • Exercise Prescription                                    ║
║      • Monitoring Schedule                                      ║
║      • Follow-up Schedule                                       ║
║      • Emergency Warning Signs                                  ║
║      • Action Items                                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        label = tk.Label(welcome_frame, text=welcome_text, font=('Consolas', 10),
                        bg='white', fg='#2C3E50', justify=tk.LEFT)
        label.pack()
    
    def animate_background(self):
        """Animate background with floating particles"""
        # Simple background color transition
        colors = ['#F0F4F8', '#E8F0F5', '#F5F0E8', '#EDF5E8']
        self.color_idx = 0
        
        def change_bg():
            self.color_idx = (self.color_idx + 1) % len(colors)
            self.root.configure(bg=colors[self.color_idx])
            self.root.after(3000, change_bg)
        
        change_bg()
    
    def upload_file(self):
        """Handle file upload"""
        file_path = filedialog.askopenfilename(
            title="Select Medical Report",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"✓ {filename}\nReady for analysis", fg='#4CAF50')
            self.generate_btn.config(state=tk.NORMAL)
            self.status_label.config(text="📎 Report uploaded - Ready to generate")
            self.doctor.set_expression("happy")
            self.speech_label.config(text="👨‍⚕️ Great! Report received.\nClick 'Generate Interactive Report'!")
    
    def generate_report(self):
        """Generate interactive report"""
        if not self.selected_file:
            messagebox.showwarning("No File", "Please upload a medical report first!")
            return
        
        self.generate_btn.config(state=tk.DISABLED, text="⏳ ANALYZING...", bg='#FF9800')
        self.upload_btn.config(state=tk.DISABLED)
        self.loading_frame.pack()
        self.progress.start(10)
        self.status_label.config(text="🔬 AI Analysis in Progress...")
        self.doctor.set_expression("thinking")
        self.speech_label.config(text="👨‍⚕️ Analyzing your report...\nPlease wait!")
        
        thread = threading.Thread(target=self.perform_analysis)
        thread.start()
    
    def perform_analysis(self):
        """Perform analysis in background"""
        try:
            analyzer = MedicalReportAnalyzer()
            extracted_text = analyzer.extract_text(self.selected_file)
            
            if "Error" in extracted_text or "No text" in extracted_text:
                self.root.after(0, self.show_error, "Could not extract text from document.")
                return
            
            values = analyzer.extract_medical_values(extracted_text)
            
            if not values:
                self.root.after(0, self.show_error, "No medical values found in the document.")
                return
            
            # Process values into report data
            report_data = self.process_values(values, analyzer)
            self.report_data = report_data
            
            self.root.after(0, self.display_report)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Analysis error: {str(e)}")
        finally:
            self.root.after(0, self.hide_loading)
    
    def process_values(self, values, analyzer):
        """Process extracted values into organized report data"""
        
        # Calculate BMI
        bmi = None
        if 'weight' in values and 'height' in values and values['height'] > 0:
            bmi = values['weight'] / ((values['height']/100) ** 2)
        
        # Determine status
        status = "NORMAL"
        if 'fasting_glucose' in values:
            if values['fasting_glucose'] >= 126:
                status = "DIABETES"
            elif values['fasting_glucose'] >= 100:
                status = "PRE-DIABETES"
        if 'hba1c' in values:
            if values['hba1c'] >= 6.5:
                status = "DIABETES"
            elif values['hba1c'] >= 5.7:
                if status == "NORMAL":
                    status = "PRE-DIABETES"
        
        # Build findings
        findings = []
        if 'fasting_glucose' in values:
            fg = values['fasting_glucose']
            if fg >= 126:
                findings.append(f"🔴 Fasting Glucose: {fg} mg/dL - DIABETES RANGE")
            elif fg >= 100:
                findings.append(f"🟡 Fasting Glucose: {fg} mg/dL - PRE-DIABETES RANGE")
            else:
                findings.append(f"🟢 Fasting Glucose: {fg} mg/dL - NORMAL RANGE")
        
        if 'hba1c' in values:
            hba1c = values['hba1c']
            if hba1c >= 6.5:
                findings.append(f"🔴 HbA1c: {hba1c}% - DIABETES RANGE")
            elif hba1c >= 5.7:
                findings.append(f"🟡 HbA1c: {hba1c}% - PRE-DIABETES RANGE")
            else:
                findings.append(f"🟢 HbA1c: {hba1c}% - NORMAL RANGE")
        
        if 'total_cholesterol' in values:
            tc = values['total_cholesterol']
            if tc >= 240:
                findings.append(f"🔴 Total Cholesterol: {tc} mg/dL - HIGH")
            elif tc >= 200:
                findings.append(f"🟡 Total Cholesterol: {tc} mg/dL - BORDERLINE")
            else:
                findings.append(f"🟢 Total Cholesterol: {tc} mg/dL - DESIRABLE")
        
        # Build treatments
        treatments = []
        if status == "DIABETES":
            treatments = [
                "Metformin 500mg twice daily (first-line therapy)",
                "Monitor blood glucose 2-4 times daily",
                "Consider SGLT2 inhibitor or GLP-1 agonist if cardiovascular disease",
                "Basal insulin if HbA1c >9.0%",
                "Statin therapy for cardiovascular protection"
            ]
        elif status == "PRE-DIABETES":
            treatments = [
                "Intensive lifestyle modification as primary treatment",
                "Target weight loss: 5-7% of body weight",
                "Consider Metformin 500mg twice daily if high risk"
            ]
        else:
            treatments = [
                "No diabetes medications needed",
                "Continue preventive lifestyle habits",
                "Annual diabetes screening recommended"
            ]
        
        # Build diet plan
        if status == "DIABETES":
            diet = {
                'breakfast': "Oatmeal with berries and nuts + 1 boiled egg",
                'lunch': "Grilled chicken salad with quinoa and olive oil dressing",
                'dinner': "Baked salmon with roasted vegetables (broccoli, cauliflower) and brown rice",
                'snacks': "Greek yogurt, handful of almonds, apple slices with peanut butter"
            }
        elif status == "PRE-DIABETES":
            diet = {
                'breakfast': "Whole grain toast with avocado + 2 eggs",
                'lunch': "Lentil soup with whole grain bread",
                'dinner': "Turkey stir-fry with brown rice",
                'snacks': "Carrot sticks with hummus, orange"
            }
        else:
            diet = {
                'breakfast': "Oatmeal with fruits and honey",
                'lunch': "Mixed vegetable sandwich on whole grain",
                'dinner': "Grilled fish with steamed vegetables",
                'snacks': "Fresh fruits, nuts"
            }
        
        # Build exercise plan
        exercise = [
            "Aerobic Exercise: 30 minutes, 5 days/week (brisk walking, jogging, cycling)",
            "Strength Training: 2-3 times/week (bodyweight exercises, resistance bands)",
            "Flexibility: Daily stretching for 10-15 minutes",
            "Check blood sugar before and after exercise",
            "Stay hydrated - drink water before, during, and after"
        ]
        
        # Build monitoring schedule
        if status == "DIABETES":
            monitoring = [
                "Fasting glucose: Daily before breakfast (target 80-130 mg/dL)",
                "Before meals: 2-3 times per week",
                "2-hour postprandial: 2-3 times per week (target <180 mg/dL)",
                "Bedtime glucose: 2-3 times per week",
                "HbA1c: Every 3 months (target <7.0%)",
                "Lipid profile: Every 6-12 months",
                "Dilated eye exam: Annually",
                "Foot exam: Annually by podiatrist"
            ]
        elif status == "PRE-DIABETES":
            monitoring = [
                "Fasting glucose: 2-3 times weekly",
                "2-hour postprandial: 1-2 times weekly",
                "Repeat HbA1c in 3-6 months",
                "Annual glucose screening indefinitely"
            ]
        else:
            monitoring = [
                "Fasting glucose: Annually",
                "Maintain healthy lifestyle",
                "Monitor for symptoms: increased thirst, urination, fatigue"
            ]
        
        # Build follow-up schedule
        if status == "DIABETES":
            followup = [
                "Endocrinologist: Every 3-6 months",
                "Primary care: Every 6 months",
                "HbA1c check: Every 3 months",
                "Annual comprehensive assessments (eyes, feet, kidneys)"
            ]
        elif status == "PRE-DIABETES":
            followup = [
                "Follow-up in 3-6 months to reassess glucose status",
                "Annual diabetes screening",
                "Regular weight monitoring"
            ]
        else:
            followup = [
                "Annual physical examination",
                "Fasting glucose or HbA1c annually"
            ]
        
        # Build emergency signs
        emergency = [
            "Blood glucose <70 mg/dL not responding to treatment",
            "Blood glucose >300 mg/dL with ketones",
            "Confusion, difficulty speaking, or loss of consciousness",
            "Nausea, vomiting, abdominal pain with high glucose",
            "Chest pain or pressure",
            "Sudden severe headache or vision changes",
            "Non-healing wounds on feet"
        ]
        
        # Build action items
        if status == "DIABETES":
            actions = [
                "Schedule appointment with endocrinologist within 2 weeks",
                "Obtain glucose meter and testing supplies",
                "Begin glucose monitoring as recommended",
                "Fill prescriptions at pharmacy",
                "Schedule appointment with registered dietitian",
                "Purchase medical ID bracelet",
                "Share diagnosis with family/support system"
            ]
        elif status == "PRE-DIABETES":
            actions = [
                "Schedule follow-up in 3-6 months",
                "Start tracking daily food intake",
                "Begin exercise program (start with 10-minute walks)",
                "Aim for 5-7% weight loss",
                "Reduce sugary beverages",
                "Increase vegetable intake"
            ]
        else:
            actions = [
                "Schedule annual diabetes screening",
                "Maintain healthy weight",
                "Exercise 150 minutes weekly",
                "Eat balanced diet with whole foods",
                "Monitor for any symptoms"
            ]
        
        return {
            'age': values.get('age'),
            'weight': values.get('weight'),
            'height': values.get('height'),
            'bmi': f"{bmi:.1f}" if bmi else "Not calculable",
            'bp': f"{values.get('blood_pressure_systolic', 'Not provided')}/{values.get('blood_pressure_diastolic', 'Not provided')}",
            'findings': findings,
            'diagnosis': {
                'status': status,
                'type': "Type 2 Diabetes" if status == "DIABETES" else ("Prediabetes" if status == "PRE-DIABETES" else "No Diabetes"),
                'severity': "Moderate to Severe" if status == "DIABETES" else ("Early Stage" if status == "PRE-DIABETES" else "None")
            },
            'treatments': treatments,
            'diet': diet,
            'exercise': exercise,
            'monitoring': monitoring,
            'followup': followup,
            'emergency': emergency,
            'actions': actions
        }
    
    def display_report(self):
        """Display the interactive report"""
        # Refresh all sections by collapsing and expanding them
        for section in self.sections:
            if section.is_expanded:
                section.collapse()
        
        # Show success message
        self.status_label.config(text="✅ Report Generated - Click on sections to view details")
        self.doctor.set_expression("happy")
        self.speech_label.config(text="👨‍⚕️ Analysis complete!\nClick on any section to view\ndetailed medical information!")
        
        # Expand the first section automatically
        if self.sections:
            self.sections[0].expand()
        
        messagebox.showinfo("Report Generated", 
                           "✅ Interactive report generated successfully!\n\n"
                           "📋 Click on any category on the right panel\n"
                           "   to expand and view detailed information.\n\n"
                           "The report includes complete analysis of:\n"
                           "• Patient Information\n"
                           "• Laboratory Findings\n"
                           "• Diagnosis & Treatment\n"
                           "• Diet & Exercise Plans\n"
                           "• Monitoring & Follow-up\n"
                           "• Emergency Guidelines")
    
    def hide_loading(self):
        """Hide loading indicator"""
        self.progress.stop()
        self.loading_frame.pack_forget()
        self.generate_btn.config(state=tk.NORMAL, text="🔬 GENERATE INTERACTIVE REPORT", bg='#4CAF50')
        self.upload_btn.config(state=tk.NORMAL)
    
    def show_error(self, error_msg):
        """Show error message"""
        self.hide_loading()
        self.status_label.config(text="❌ Analysis Failed")
        self.doctor.set_expression("worried")
        self.speech_label.config(text="👨‍⚕️ I couldn't analyze\nthe report. Please\ntry again with a\nclear report!")
        messagebox.showerror("Analysis Error", error_msg)

# Include the MedicalReportAnalyzer class from previous code here
# (Keeping it as is from the previous working version)

class MedicalReportAnalyzer:
    """Medical report analyzer - same as before"""
    
    def extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf' and PDF_SUPPORT:
                text = ""
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text if text.strip() else "No text found"
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                img = cv2.imread(file_path)
                if img is None:
                    return "Could not read image"
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                text = pytesseract.image_to_string(thresh)
                return text if text.strip() else "No text found"
            else:
                return "Unsupported file format"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def extract_medical_values(self, text):
        values = {}
        patterns = {
            'fasting_glucose': r'(?:Fasting\s*Glucose|FBS|FBG)[:\s]*(\d+(?:\.\d+)?)',
            'postprandial_glucose': r'(?:Postprandial|PPBS|PPG)[:\s]*(\d+(?:\.\d+)?)',
            'hba1c': r'(?:HbA1c|A1c)[:\s]*(\d+(?:\.\d+)?)',
            'total_cholesterol': r'(?:Total\s*Cholesterol|TC)[:\s]*(\d+(?:\.\d+)?)',
            'triglycerides': r'(?:Triglycerides|TG)[:\s]*(\d+(?:\.\d+)?)',
            'hdl': r'(?:HDL)[:\s]*(\d+(?:\.\d+)?)',
            'ldl': r'(?:LDL)[:\s]*(\d+(?:\.\d+)?)',
            'age': r'(?:Age|AGE)[:\s]*(\d{1,3})',
            'weight': r'(?:Weight|WT)[:\s]*(\d+(?:\.\d+)?)',
            'height': r'(?:Height|HT)[:\s]*(\d+(?:\.\d+)?)',
            'blood_pressure_systolic': r'(?:BP|Blood\s*Pressure)[:\s]*(\d+)\s*\/',
            'blood_pressure_diastolic': r'(?:BP|Blood\s*Pressure)[:\s]*\d+\s*\/\s*(\d+)'
        }
        for param, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    values[param] = float(matches[0])
                except:
                    values[param] = matches[0]
        return values

def main():
    root = tk.Tk()
    app = MedicalReportSystem(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 1500) // 2
    y = (root.winfo_screenheight() - 950) // 2
    root.geometry(f'1500x950+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()

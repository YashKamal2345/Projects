import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import Image
import os

class VirtualWhiteboard:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Try to initialize camera with different approaches
        self.cap = None
        
        # First try the default camera (usually 0)
        self.cap = cv2.VideoCapture(0)
        
        # If that doesn't work, try different indices
        if not self.cap.isOpened():
            for i in range(1, 5):  # Try camera indices 1 to 4
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    print(f"Camera found at index {i}")
                    break
        
        if not self.cap or not self.cap.isOpened():
            print("Error: Could not find any camera.")
            print("Please check if your camera is connected and not being used by another application.")
            self.cap = None
            return
            
        self.cap.set(3, 1280)  # Width
        self.cap.set(4, 720)   # Height
        
        # Whiteboard parameters
        self.whiteboard = np.ones((720, 1280, 3), dtype=np.uint8) * 255
        self.prev_x, self.prev_y = 0, 0
        self.drawing = False
        
        # For smoothing the drawing
        self.smooth_points = []
        self.smooth_factor = 7  # Increased for better smoothing
        
        # Drawing tools
        self.current_tool = "pen"
        self.pen_size = 5
        self.eraser_size = 20
        self.current_color = (0, 0, 255)  # Default red
        
        # Board background options
        self.background_mode = "camera"  # "camera" or "black"
        
        # Colors available
        self.colors = [
            (0, 0, 255),    # Red
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 255, 255),  # Yellow
            (255, 0, 255),  # Magenta
            (255, 255, 0),  # Cyan
            (0, 0, 0),      # Black
            (255, 255, 255) # White (for eraser)
        ]
        
        # Color names for display
        self.color_names = [
            "Red", "Green", "Blue", "Yellow", 
            "Magenta", "Cyan", "Black", "White"
        ]
        
        # Tools available
        self.tools = ["pen", "eraser"]
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        # Create a simple UI using OpenCV
        self.ui = np.zeros((100, 1280, 3), dtype=np.uint8)
        
        # Draw color palette
        color_width = 1280 // (len(self.colors) + 1)  # Adjusted for background button
        for i, color in enumerate(self.colors):
            cv2.rectangle(self.ui, (i * color_width, 0), ((i+1) * color_width, 50), color, -1)
            cv2.rectangle(self.ui, (i * color_width, 0), ((i+1) * color_width, 50), (0, 0, 0), 2)
            # Add color name
            text_color = (255, 255, 255) if color == (0, 0, 0) else (0, 0, 0)
            cv2.putText(self.ui, self.color_names[i], (i * color_width + 5, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)
        
        # Draw tools
        tool_width = 1280 // (len(self.tools) + 2)  # Adjusted for extra buttons
        for i, tool in enumerate(self.tools):
            cv2.rectangle(self.ui, (i * tool_width, 50), ((i+1) * tool_width, 100), (200, 200, 200), -1)
            cv2.putText(self.ui, tool, (i * tool_width + 10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.rectangle(self.ui, (i * tool_width, 50), ((i+1) * tool_width, 100), (0, 0, 0), 2)
        
        # Add save and clear buttons
        cv2.rectangle(self.ui, (1280 - 150, 50), (1280 - 10, 100), (100, 100, 255), -1)
        cv2.putText(self.ui, "SAVE", (1280 - 140, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        cv2.rectangle(self.ui, (1280 - 300, 50), (1280 - 160, 100), (100, 255, 100), -1)
        cv2.putText(self.ui, "CLEAR", (1280 - 290, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Add background toggle button
        cv2.rectangle(self.ui, (1280 - 450, 50), (1280 - 310, 100), (200, 200, 100), -1)
        cv2.putText(self.ui, "BG TOGGLE", (1280 - 440, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    def is_index_finger_extended(self, hand_landmarks):
        # Check if only index finger is extended (others are folded)
        tips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.PINKY_TIP
        ]
        
        pips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.PINKY_PIP
        ]
        
        # Index finger is extended if its tip is above its PIP joint
        index_extended = hand_landmarks.landmark[tips[0]].y < hand_landmarks.landmark[pips[0]].y
        
        # Other fingers should be folded (tip below PIP joint)
        others_folded = all(hand_landmarks.landmark[tips[i]].y > hand_landmarks.landmark[pips[i]].y 
                           for i in range(1, 4))
        
        return index_extended and others_folded
    
    def select_tool(self, x, y):
        # Check if click is in tool area
        if y < 100:
            # Check colors
            color_width = 1280 // (len(self.colors) + 1)
            if y < 50:
                for i in range(len(self.colors)):
                    if i * color_width <= x < (i+1) * color_width:
                        self.current_color = self.colors[i]
                        self.current_tool = "pen"
                        print(f"Selected color: {self.color_names[i]}")
                        return
            
            # Check tools
            tool_width = 1280 // (len(self.tools) + 2)
            for i in range(len(self.tools)):
                if i * tool_width <= x < (i+1) * tool_width and 50 <= y < 100:
                    self.current_tool = self.tools[i]
                    print(f"Selected tool: {self.tools[i]}")
                    return
            
            # Check save button
            if 1280 - 150 <= x < 1280 - 10 and 50 <= y < 100:
                self.save_whiteboard()
                return
                
            # Check clear button
            if 1280 - 300 <= x < 1280 - 160 and 50 <= y < 100:
                self.whiteboard = np.ones((720, 1280, 3), dtype=np.uint8) * 255
                print("Whiteboard cleared")
                return
                
            # Check background toggle button
            if 1280 - 450 <= x < 1280 - 310 and 50 <= y < 100:
                self.background_mode = "black" if self.background_mode == "camera" else "camera"
                print(f"Background mode: {self.background_mode}")
                return
    
    def save_whiteboard(self):
        # Convert whiteboard to PIL Image
        img = Image.fromarray(self.whiteboard)
        
        # Create a simple file dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            img.save(file_path)
            print(f"Whiteboard saved to {file_path}")
    
    def smooth_point(self, x, y):
        # Add the new point to our list
        self.smooth_points.append((x, y))
        
        # Keep only the last few points
        if len(self.smooth_points) > self.smooth_factor:
            self.smooth_points.pop(0)
        
        # Calculate the weighted average of the points (more weight to recent points)
        weights = np.arange(1, len(self.smooth_points) + 1)
        total_weight = np.sum(weights)
        
        avg_x = int(np.sum([p[0] * w for p, w in zip(self.smooth_points, weights)]) / total_weight)
        avg_y = int(np.sum([p[1] * w for p, w in zip(self.smooth_points, weights)]) / total_weight)
        
        return avg_x, avg_y
    
    def draw_on_whiteboard(self, x, y):
        if self.drawing:
            # Smooth the point to reduce jitter
            smooth_x, smooth_y = self.smooth_point(x, y)
            
            if self.current_tool == "pen":
                cv2.line(self.whiteboard, (self.prev_x, self.prev_y), (smooth_x, smooth_y), self.current_color, self.pen_size)
            elif self.current_tool == "eraser":
                cv2.line(self.whiteboard, (self.prev_x, self.prev_y), (smooth_x, smooth_y), (255, 255, 255), self.eraser_size)
        
        self.prev_x, self.prev_y = x, y
    
    def run(self):
        if self.cap is None:
            print("Camera not available. Running in demo mode without camera.")
            # Create a demo mode without camera
            self.demo_mode()
            return
            
        print("Starting Virtual Whiteboard with camera...")
        print("INSTRUCTIONS:")
        print("1. To draw: Extend only your index finger (keep other fingers folded)")
        print("2. To select tool/color: Point with your index finger to the UI area")
        print("3. Press 'q' to quit, 'c' to clear, 's' to save, 'b' to toggle background")
        print("4. Make sure your hand is well-lit and visible to the camera")
        
        # Create a fullscreen window
        cv2.namedWindow("Virtual Whiteboard", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Virtual Whiteboard", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame. Switching to demo mode.")
                self.demo_mode()
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Get hand landmarks
            drawing_allowed = False
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks (only index finger for clarity)
                    index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    h, w, c = frame.shape
                    x = int(index_tip.x * w)
                    y = int(index_tip.y * h)
                    
                    # Draw only index finger tip
                    cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
                    
                    # Check if only index finger is extended
                    drawing_allowed = self.is_index_finger_extended(hand_landmarks)
                    
                    # Check if finger is in UI area
                    if y < 100:
                        cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
                        if not self.drawing:
                            self.select_tool(x, y)
                    else:
                        # Draw on whiteboard only if index finger is extended and others are folded
                        if drawing_allowed:
                            cv2.circle(frame, (x, y), 10, self.current_color, -1)
                            self.draw_on_whiteboard(x, y)
                            self.drawing = True
                        else:
                            self.drawing = False
                            self.smooth_points = []  # Reset smoothing when not drawing
            else:
                self.drawing = False
                drawing_allowed = False
                self.smooth_points = []  # Reset smoothing when no hand is detected
            
            # Create the display based on background mode
            if self.background_mode == "camera":
                # Combine whiteboard and camera feed
                combined = np.vstack((self.ui, self.whiteboard))
                
                # Resize frame to match whiteboard dimensions
                frame_resized = cv2.resize(frame, (1280, 720))
                combined[100:820, :] = cv2.addWeighted(frame_resized, 0.3, combined[100:820, :], 0.7, 0)
            else:
                # Use black background
                black_bg = np.zeros((720, 1280, 3), dtype=np.uint8)
                combined = np.vstack((self.ui, black_bg))
                
                # Add the whiteboard drawing on top
                combined[100:820, :] = cv2.addWeighted(self.whiteboard, 1.0, combined[100:820, :], 1.0, 0)
            
            # Display current tool and color
            color_name = self.color_names[self.colors.index(self.current_color)] if self.current_color in self.colors else "Custom"
            cv2.putText(combined, f"Tool: {self.current_tool} | Color: {color_name}", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Show drawing status
            status = "Ready to draw" if drawing_allowed else "Make a fist or extend only index finger to draw"
            cv2.putText(combined, status, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Show background mode
            bg_text = f"Background: {self.background_mode} (Press 'B' to toggle)"
            cv2.putText(combined, bg_text, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Show controls
            cv2.putText(combined, "Press 'Q' to quit | 'S' to save | 'C' to clear", (10, 210), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Show the combined image
            cv2.imshow("Virtual Whiteboard", combined)
            
            # Key controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('c') or key == ord('C'):
                self.whiteboard = np.ones((720, 1280, 3), dtype=np.uint8) * 255
                print("Whiteboard cleared")
            elif key == ord('s') or key == ord('S'):
                self.save_whiteboard()
            elif key == ord('b') or key == ord('B'):
                self.background_mode = "black" if self.background_mode == "camera" else "camera"
                print(f"Background mode: {self.background_mode}")
        
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def demo_mode(self):
        """Run without camera - for testing purposes"""
        print("Running in demo mode without camera")
        print("You can test the UI but hand tracking won't work")
        
        # Create a fullscreen window
        cv2.namedWindow("Virtual Whiteboard (Demo Mode)", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Virtual Whiteboard (Demo Mode)", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Create a blank black image as a placeholder for camera feed
        placeholder = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.putText(placeholder, "Camera not available", (400, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(placeholder, "Press 'q' to quit", (450, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        while True:
            # Create the display based on background mode
            if self.background_mode == "camera":
                # Combine whiteboard and placeholder
                combined = np.vstack((self.ui, self.whiteboard))
                combined[100:820, :] = cv2.addWeighted(placeholder, 0.3, combined[100:820, :], 0.7, 0)
            else:
                # Use black background
                black_bg = np.zeros((720, 1280, 3), dtype=np.uint8)
                combined = np.vstack((self.ui, black_bg))
                
                # Add the whiteboard drawing on top
                combined[100:820, :] = cv2.addWeighted(self.whiteboard, 1.0, combined[100:820, :], 1.0, 0)
            
            # Display current tool and color
            color_name = self.color_names[self.colors.index(self.current_color)] if self.current_color in self.colors else "Custom"
            cv2.putText(combined, f"Tool: {self.current_tool} | Color: {color_name} (Demo Mode)", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(combined, "Camera not available - running in demo mode", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Show background mode
            bg_text = f"Background: {self.background_mode} (Press 'B' to toggle)"
            cv2.putText(combined, bg_text, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Show the combined image
            cv2.imshow("Virtual Whiteboard (Demo Mode)", combined)
            
            # Key controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('c') or key == ord('C'):
                self.whiteboard = np.ones((720, 1280, 3), dtype=np.uint8) * 255
                print("Whiteboard cleared")
            elif key == ord('s') or key == ord('S'):
                self.save_whiteboard()
            elif key == ord('b') or key == ord('B'):
                self.background_mode = "black" if self.background_mode == "camera" else "camera"
                print(f"Background mode: {self.background_mode}")
        
        cv2.destroyAllWindows()

# Main program
if __name__ == "__main__":
    print("Initializing Virtual Whiteboard...")
    print("Make sure you have installed the required packages:")
    print("1. Open Command Prompt")
    print("2. Run: pip install opencv-python mediapipe numpy Pillow")
    print()
    
    # Check if required packages are installed
    try:
        whiteboard = VirtualWhiteboard()
        whiteboard.run()
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install the required packages using the instructions above.")
    except Exception as e:
        print(f"An error occurred: {e}")

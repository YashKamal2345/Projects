import tkinter as tk
import time
import csv

keystrokes = []

def on_key(event):
    current_time = time.time()
    keystrokes.append((event.char, current_time))

def save_and_quit():
    emotion = emotion_entry.get().strip().lower()
    if emotion not in ['happy', 'sad', 'angry', 'confused']:
        print("❌ Please enter a valid emotion.")
        return

    with open(f"keystrokes_{emotion}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "time"])
        for k, t in keystrokes:
            writer.writerow([k, t])
    print(f"✅ Typing data saved as keystrokes_{emotion}.csv")
    root.destroy()

# GUI setup
root = tk.Tk()
root.title("Typing Emotion Recorder")

tk.Label(root, text="Enter your emotion (happy/sad/angry/confused):").pack()
emotion_entry = tk.Entry(root)
emotion_entry.pack()

tk.Label(root, text="Now type your sentence:").pack()
text_box = tk.Text(root, height=10, width=50)
text_box.pack()
text_box.bind("<Key>", on_key)

tk.Button(root, text="Save & Quit", command=save_and_quit).pack()

root.mainloop()

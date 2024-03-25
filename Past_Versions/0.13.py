import cv2
import dlib
import ctypes
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

class BlinkDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VisageGuard – Intelligent Facial Recognition for Enhanced PC Security")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        self.autostart_var = tk.IntVar()
        self.blink_detection_var = tk.IntVar(value=1)
        self.cap = None
        self.thread = None
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = self.load_predictor()
        self.ear_threshold = 0.25  # Default EAR threshold for blink detection
        self.max_blink_duration = 5  # Default maximum blink duration in seconds

        # Start on startup checkbox
        self.autostart_checkbox = ttk.Checkbutton(root, text="Start on Startup", variable=self.autostart_var)
        self.autostart_checkbox.pack(pady=5)

        # Toggle blinking detection checkbox
        self.blink_detection_checkbox = ttk.Checkbutton(root, text="Blink Detection", variable=self.blink_detection_var, command=self.toggle_blink_detection)
        self.blink_detection_checkbox.pack(pady=5)

        # Settings button
        self.settings_button = ttk.Button(root, text="Settings", command=self.show_settings)
        self.settings_button.pack(pady=5)

        # Start button
        self.start_button = ttk.Button(root, text="Start", command=self.start_detection)
        self.start_button.pack(pady=5)

        # Stop button
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

    def load_predictor(self):
        predictor_path = Path(__file__).parent / "shape_predictor_68_face_landmarks.dat"
        if not predictor_path.exists():
            messagebox.showerror("Error", "The dlib facial landmark predictor file was not found.")
            self.root.quit()
        return dlib.shape_predictor(str(predictor_path))

    def toggle_blink_detection(self):
        if self.blink_detection_var.get() == 0:
            self.stop_detection()
        else:
            self.start_detection()

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x150")
        settings_window.resizable(False, False)

        # EAR threshold entry
        ear_threshold_label = ttk.Label(settings_window, text="EAR Threshold:")
        ear_threshold_label.pack(pady=5)
        ear_threshold_entry = ttk.Entry(settings_window)
        ear_threshold_entry.insert(0, str(self.ear_threshold))
        ear_threshold_entry.pack(pady=5)

        # Max blink duration entry
        max_blink_duration_label = ttk.Label(settings_window, text="Max Blink Duration (s):")
        max_blink_duration_label.pack(pady=5)
        max_blink_duration_entry = ttk.Entry(settings_window)
        max_blink_duration_entry.insert(0, str(self.max_blink_duration))
        max_blink_duration_entry.pack(pady=5)

        def save_settings():
            try:
                self.ear_threshold = float(ear_threshold_entry.get())
                self.max_blink_duration = int(max_blink_duration_entry.get())
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input values. Please enter a valid number.")

        save_button = ttk.Button(settings_window, text="Save", command=save_settings)
        save_button.pack(pady=5)

    def start_detection(self):
        if self.blink_detection_var.get() == 0:
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Failed to open the camera.")
            return

        self.thread = threading.Thread(target=self.detect_blink)
        self.thread.daemon = True
        self.thread.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_detection(self):
        if self.cap is not None:
            self.cap.release()
        self.thread = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def detect_blink(self):
        counter = 0
        blinking = False
        last_blink_time = time.time()
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces_dlib = self.detector(gray)

            if len(faces_dlib) == 0:
                counter = 0
                continue

            for face in faces_dlib:
                shape = self.predictor(gray, face)
                shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

                left_eye = shape[42:48]
                right_eye = shape[36:42]

                left_ear = self.eye_aspect_ratio(left_eye)
                right_ear = self.eye_aspect_ratio(right_eye)

                ear = (left_ear + right_ear) / 2.0

                if ear < self.ear_threshold:
                    counter += 1
                    if counter >= 3:
                        blinking = True
                        last_blink_time = time.time()
                else:
                    counter = 0
                    blinking = False

            if blinking and time.time() - last_blink_time > self.max_blink_duration:
                self.lock_pc()
                break

            if blinking:
                print("Blink Detected")

    def eye_aspect_ratio(self, eye):
        a = self.dist(eye[1], eye[5])
        b = self.dist(eye[2], eye[4])
        c = self.dist(eye[0], eye[3])
        ear = (a + b) / (2.0 * c)
        return ear

    def dist(self, p1, p2):
        return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

    def lock_pc(self):
        user32 = ctypes.windll.user32
        user32.LockWorkStation()
        self.stop_detection()
        messagebox.showinfo("PC Locked", "Your PC has been locked due to prolonged eye closure.")

def main():
    root = tk.Tk()
    app = BlinkDetectionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_detection)
    root.mainloop()

if __name__ == "__main__":
    main()

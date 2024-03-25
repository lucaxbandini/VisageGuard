# Importing necessary libraries
import cv2
import dlib
import ctypes
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

# Define the main application class for Blink Detection
class BlinkDetectionApp:
    def __init__(self, root):
        # Initializing the application window
        self.root = root
        self.root.title("VisageGuard – Intelligent Facial Recognition for Enhanced PC Security")  # Title of the application window
        self.root.geometry("700x500")  # Size of the window
        self.root.resizable(False, False)  # Making the window non-resizable
        self.autostart_var = tk.IntVar()  # Variable for auto-start option
        self.detection_var = tk.IntVar(value=1)  # Variable for facial recognition option
        self.cap = None  # Variable to hold the video capture object
        self.thread = None  # Variable to hold the threading object
        self.detector = dlib.get_frontal_face_detector()  # Face detector object
        self.predictor = self.load_predictor()  # Facial landmark predictor object
        self.ear_threshold = 0.25  # Default EAR threshold for blink detection
        self.max_blink_duration = 5  # Default maximum blink duration in seconds
        self.face_detected = False  # Flag to track if a face is detected
        self.video_label = None  # Label to display the video feed

        # Create a canvas for the video feed
        self.canvas = tk.Canvas(root, width=640, height=480)
        self.canvas.pack()

        # Auto-start checkbox
        self.autostart_checkbox = ttk.Checkbutton(root, text="Start on Startup", variable=self.autostart_var)
        self.autostart_checkbox.pack(pady=5, side=tk.TOP, anchor=tk.W, padx=10)

        # Facial recognition toggle checkbox
        self.detection_checkbox = ttk.Checkbutton(root, text="Facial Recognition", variable=self.detection_var, command=self.toggle_detection)
        self.detection_checkbox.pack(pady=5, side=tk.TOP, anchor=tk.W, padx=10)

        # Settings button
        self.settings_button = ttk.Button(root, text="Settings", command=self.show_settings)
        self.settings_button.pack(pady=5, side=tk.TOP, anchor=tk.W, padx=10)

        # Start button
        self.start_button = ttk.Button(root, text="Start", command=self.start_detection)
        self.start_button.pack(pady=5, side=tk.TOP, anchor=tk.W, padx=10)

        # Stop button
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(pady=5, side=tk.TOP, anchor=tk.W, padx=10)

        # Create a label for the video feed
        self.video_label = tk.Label(self.canvas)
        self.video_label.pack()

    # Function to load the facial landmark predictor
    def load_predictor(self):
        predictor_path = Path(__file__).parent / "shape_predictor_68_face_landmarks.dat"
        if not predictor_path.exists():
            messagebox.showerror("Error", "The dlib facial landmark predictor file was not found.")
            self.root.quit()
        return dlib.shape_predictor(str(predictor_path))

    # Function to toggle facial recognition detection
    def toggle_detection(self):
        if self.detection_var.get() == 0:
            self.stop_detection()
        else:
            self.start_detection()

    # Function to show the settings window
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

        # Save settings button
        def save_settings():
            try:
                self.ear_threshold = float(ear_threshold_entry.get())
                self.max_blink_duration = int(max_blink_duration_entry.get())
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input values. Please enter a valid number.")

        save_button = ttk.Button(settings_window, text="Save", command=save_settings)
        save_button.pack(pady=5)

    # Function to start facial recognition detection
    def start_detection(self):
        if self.detection_var.get() == 0:
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

    # Function to stop facial recognition detection
    def stop_detection(self):
        if self.cap is not None:
            self.cap.release()
        if self.thread is not None:
            self.thread.join()
        self.thread = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    # Function to detect blinks using facial recognition
    def detect_blink(self):
        counter = 0
        blinking = False
        last_blink_time = time.time()
        last_face_time = time.time()
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces_dlib = self.detector(gray)

            if len(faces_dlib) == 0:
                counter = 0
                blinking = False
                self.face_detected = False
                if time.time() - last_face_time > 5:
                    self.lock_pc()
                    break
            else:
                self.face_detected = True
                last_face_time = time.time()

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

            # Display the frame in the GUI
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.video_label.configure(image=photo)
            self.video_label.image = photo

        self.cap.release()
        cv2.destroyAllWindows()

    # Function to calculate eye aspect ratio
    def eye_aspect_ratio(self, eye):
        a = self.dist(eye[1], eye[5])
        b = self.dist(eye[2], eye[4])
        c = self.dist(eye[0], eye[3])
        ear = (a + b) / (2.0 * c)
        return ear

    # Function to calculate distance between two points
    def dist(self, p1, p2):
        return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

    # Function to lock the PC
    def lock_pc(self):
        user32 = ctypes.windll.user32
        user32.LockWorkStation()
        self.stop_detection()
        messagebox.showinfo("PC Locked", "Your PC has been locked due to prolonged eye closure or no face detected.")

# Main function to start the application
def main():
    root = tk.Tk()
    app = BlinkDetectionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_detection)
    root.mainloop()

# Check if the script is being run directly
if __name__ == "__main__":
    main()

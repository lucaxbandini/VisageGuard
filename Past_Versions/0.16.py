import cv2
import dlib
import ctypes
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

class BlinkDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VisageGuard – Intelligent Facial Recognition for Enhanced PC Security")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)  # Allow resizing
        self.dark_mode = False
        self.bg_color = "#FFFFFF"
        self.fg_color = "#000000"
        self.autostart_var = tk.IntVar()
        self.detection_var = tk.IntVar(value=1)
        self.cap = None
        self.thread = None
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = self.load_predictor()
        self.ear_threshold = 0.25
        self.max_blink_duration = 5
        self.max_face_detection_duration = 5
        self.max_no_blink_duration = 10
        self.face_detected = False
        self.video_label = None

        # Set window icon
        icon_path = Path(__file__).parent / "cutout.png"
        self.root.iconbitmap(icon_path)

        # Create a frame for the video feed and buttons
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for the video feed
        self.canvas = tk.Canvas(self.main_frame, width=640, height=480, bg=self.bg_color)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a frame for the buttons
        self.button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.button_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        # Dark mode toggle
        self.dark_mode_button = ttk.Button(self.button_frame, text="Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.pack(pady=5, anchor=tk.W)

        # Start on startup checkbox
        self.autostart_checkbox = ttk.Checkbutton(self.button_frame, text="Start on Startup", variable=self.autostart_var, style="TCheckbutton")
        self.autostart_checkbox.pack(pady=5, anchor=tk.W)

        # Toggle detection checkbox
        self.detection_checkbox = ttk.Checkbutton(self.button_frame, text="Facial Recognition", variable=self.detection_var, command=self.toggle_detection, style="TCheckbutton")
        self.detection_checkbox.pack(pady=5, anchor=tk.W)

        # Settings button
        self.settings_button = ttk.Button(self.button_frame, text="Settings", command=self.show_settings, style="TButton")
        self.settings_button.pack(pady=5, anchor=tk.W)

        # Start button
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_detection, style="TButton")
        self.start_button.pack(pady=5, anchor=tk.W)

        # Stop button
        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_detection, state=tk.DISABLED, style="TButton")
        self.stop_button.pack(pady=5, anchor=tk.W)

        # Create a label for the video feed
        self.video_label = tk.Label(self.canvas, bg=self.bg_color)
        self.video_label.pack()

        # Update style based on initial settings
        self.update_style()

    def load_predictor(self):
        predictor_path = Path(__file__).parent / "shape_predictor_68_face_landmarks.dat"
        if not predictor_path.exists():
            messagebox.showerror("Error", "The dlib facial landmark predictor file was not found.")
            self.root.quit()
        return dlib.shape_predictor(str(predictor_path))

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.update_style()

    def update_style(self):
        if self.dark_mode:
            self.bg_color = "#333333"
            self.fg_color = "#FFFFFF"
            self.root.configure(bg=self.bg_color)
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TButton", background=self.bg_color, foreground=self.fg_color)
            style.configure("TCheckbutton", background=self.bg_color, foreground=self.fg_color)
            style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
            style.configure("TEntry", background=self.bg_color, foreground=self.fg_color)
        else:
            self.bg_color = "#FFFFFF"
            self.fg_color = "#000000"
            self.root.configure(bg=self.bg_color)
            style = ttk.Style()
            style.theme_use("default")
            style.configure("TButton")
            style.configure("TCheckbutton")
            style.configure("TLabel")
            style.configure("TEntry")

        self.button_frame.configure(bg=self.bg_color)
        self.canvas.configure(bg=self.bg_color)
        self.video_label.configure(bg=self.bg_color)

    def toggle_detection(self):
        if self.detection_var.get() == 0:
            self.stop_detection()
        else:
            self.start_detection()

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x300")
        settings_window.resizable(False, False)

        # Create a scrollable frame for settings
        settings_frame = tk.Frame(settings_window, bg=self.bg_color)
        settings_canvas = tk.Canvas(settings_frame, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(settings_frame, orient=tk.VERTICAL, command=settings_canvas.yview)
        scrollable_frame = tk.Frame(settings_canvas, bg=self.bg_color)

        scrollable_frame.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))

        settings_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        settings_canvas.configure(yscrollcommand=scrollbar.set)

        settings_frame.pack(fill=tk.BOTH, expand=True)
        settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # EAR threshold entry
        ear_threshold_label = ttk.Label(scrollable_frame, text="EAR Threshold:", style="TLabel")
        ear_threshold_label.pack(pady=5)
        ear_threshold_entry = ttk.Entry(scrollable_frame, style="TEntry")
        ear_threshold_entry.insert(0, str(self.ear_threshold))
        ear_threshold_entry.pack(pady=5)

        # Max blink duration entry
        max_blink_duration_label = ttk.Label(scrollable_frame, text="Max Blink Duration (s):", style="TLabel")
        max_blink_duration_label.pack(pady=5)
        max_blink_duration_entry = ttk.Entry(scrollable_frame, style="TEntry")
        max_blink_duration_entry.insert(0, str(self.max_blink_duration))
        max_blink_duration_entry.pack(pady=5)

        # Max face detection duration entry
        max_face_detection_duration_label = ttk.Label(scrollable_frame, text="Max Face Detection Duration (s):", style="TLabel")
        max_face_detection_duration_label.pack(pady=5)
        max_face_detection_duration_entry = ttk.Entry(scrollable_frame, style="TEntry")
        max_face_detection_duration_entry.insert(0, str(self.max_face_detection_duration))
        max_face_detection_duration_entry.pack(pady=5)

        # Max no blink duration entry
        max_no_blink_duration_label = ttk.Label(scrollable_frame, text="Max No Blink Duration (s):", style="TLabel")
        max_no_blink_duration_label.pack(pady=5)
        max_no_blink_duration_entry = ttk.Entry(scrollable_frame, style="TEntry")
        max_no_blink_duration_entry.insert(0, str(self.max_no_blink_duration))
        max_no_blink_duration_entry.pack(pady=5)

        def save_settings():
            try:
                self.ear_threshold = float(ear_threshold_entry.get())
                self.max_blink_duration = int(max_blink_duration_entry.get())
                self.max_face_detection_duration = int(max_face_detection_duration_entry.get())
                self.max_no_blink_duration = int(max_no_blink_duration_entry.get())
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input values. Please enter a valid number.")

        save_button = ttk.Button(scrollable_frame, text="Save", command=save_settings, style="TButton")
        save_button.pack(pady=5)

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

    def stop_detection(self):
        if self.cap is not None:
            self.cap.release()
        if self.thread is not None:
            self.thread.join()
        self.thread = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def detect_blink(self):
        counter = 0
        blinking = False
        last_blink_time = time.time()
        last_face_time = time.time()
        last_no_blink_time = time.time()
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
                if time.time() - last_face_time > self.max_face_detection_duration:
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
                        last_no_blink_time = time.time()
                        if counter >= 3:
                            blinking = True
                            last_blink_time = time.time()
                    else:
                        counter = 0
                        blinking = False

                        if time.time() - last_no_blink_time > self.max_no_blink_duration:
                            self.lock_pc()
                            break

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
        reason = "Your PC has been locked due to "
        if not self.face_detected:
            reason += "no face detected for a prolonged period."
        elif time.time() - last_no_blink_time > self.max_no_blink_duration:
            reason += "no blinking detected for a prolonged period."
        else:
            reason += "prolonged eye closure."
        messagebox.showinfo("PC Locked", reason)

def main():
    root = tk.Tk()
    app = BlinkDetectionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_detection)
    root.mainloop()

if __name__ == "__main__":
    main()

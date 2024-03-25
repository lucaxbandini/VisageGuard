# Let's import the libraries we need
import cv2  # For working with images and videos
import dlib  # For detecting faces and facial landmarks
import ctypes  # For locking the PC
import time  # For time-related functions
import tkinter as tk  # For creating the graphical user interface
from PIL import Image, ImageTk, ImageOps  # For image manipulation
import threading  # For running tasks concurrently

# Let's load our face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Make sure to download this file

# Define some constants for blink detection
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 3

# Initialize some variables
COUNTER = 0
BLINKING = False
last_blink_time = time.time()  # Keep track of the last blink time

# Let's set up our global variables
detection_active = False  # To control whether detection is active or not
dark_mode = False  # To toggle between light and dark mode

# Function to calculate eye aspect ratio
def eye_aspect_ratio(eye):
    A = dist(eye[1], eye[5])
    B = dist(eye[2], eye[4])
    C = dist(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Function to calculate euclidean distance between two points
def dist(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

# Function to lock the PC
def lock_pc():
    user32 = ctypes.windll.User32
    user32.LockWorkStation()

# Function to start/stop detection
def toggle_detection():
    global detection_thread, detection_active
    if not detection_active:
        detection_active = True
        detection_thread = threading.Thread(target=start_detection)
        detection_thread.daemon = True
        detection_thread.start()
        start_button.config(text="Stop Detection")
    else:
        stop_detection()
        start_button.config(text="Start Detection")

# Function to start detection
def start_detection():
    global detection_active, cap
    cap = cv2.VideoCapture(0)
    detection_active = True
    while detection_active:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            if len(faces) == 0:
                lock_pc()
            for face in faces:
                shape = predictor(gray, face)
                shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]
                left_eye = shape[42:48]
                right_eye = shape[36:42]
                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                ear = (left_ear + right_ear) / 2.0
                if ear < EYE_AR_THRESH:
                    global COUNTER, BLINKING, last_blink_time
                    COUNTER += 1
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        BLINKING = True
                        last_blink_time = time.time()
                else:
                    COUNTER = 0
                    BLINKING = False
            if not BLINKING and time.time() - last_blink_time > blink_timeout.get():
                lock_pc()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if dark_mode:
                frame = Image.fromarray(frame).convert('L')
                frame = ImageOps.invert(frame)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            panel.config(image=frame)
            panel.image = frame
    cap.release()
    cv2.destroyAllWindows()

# Function to stop detection
def stop_detection():
    global detection_active
    detection_active = False

# Function to toggle dark mode
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        root.config(bg='black')
        panel.config(bg='black', fg='white')
        start_button.config(bg='gray', fg='white')
        settings_menu.config(bg='black', fg='white')
        timeout_slider.config(bg='black', fg='white')
    else:
        root.config(bg='white')
        panel.config(bg='white', fg='black')
        start_button.config(bg='white', fg='black')
        settings_menu.config(bg='white', fg='black')
        timeout_slider.config(bg='white', fg='black')

# Let's create our graphical user interface
root = tk.Tk()
root.title("VisageGuard – Intelligent Facial Recognition for Enhanced PC Security")

panel = tk.Label(root)
panel.pack(padx=10, pady=10)

start_button = tk.Button(root, text="Start Detection", command=toggle_detection)
start_button.pack(padx=10, pady=5)

settings_menu = tk.Menu(root)
root.config(menu=settings_menu)

settings_submenu = tk.Menu(settings_menu, tearoff=0)
settings_submenu.add_command(label="Toggle Dark Mode", command=toggle_dark_mode)
settings_menu.add_cascade(label="Settings", menu=settings_submenu)

blink_timeout = tk.DoubleVar()
blink_timeout.set(4)
timeout_slider = tk.Scale(root, from_=1, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Blink Timeout (seconds)", variable=blink_timeout)
timeout_slider.pack(padx=10, pady=5)

toggle_detection()

root.mainloop()

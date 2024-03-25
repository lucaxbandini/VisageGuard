# Import necessary libraries
import cv2  # For image processing
import dlib  # For face detection and landmarks
import ctypes  # For locking the PC
import time  # For time-related functions
import tkinter as tk  # For creating GUI
from PIL import Image, ImageTk, ImageOps  # For image manipulation
import threading  # For running tasks concurrently

# Load face detector and landmark predictor
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Download this file

# Constants for blink detection
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 3

# Initialize counters and flags
blink_counter = 0
is_blinking = False
last_blink_time = time.time()  # Store time of last detected blink

# Global variables for detection status and dark mode
detection_active = False
dark_mode = False

# Function to calculate eye aspect ratio
def calculate_eye_aspect_ratio(eye_landmarks):
    # Calculate distances between eye landmarks
    vertical_dist1 = dist(eye_landmarks[1], eye_landmarks[5])
    vertical_dist2 = dist(eye_landmarks[2], eye_landmarks[4])
    horizontal_dist = dist(eye_landmarks[0], eye_landmarks[3])

    # Compute eye aspect ratio
    ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)
    return ear

# Function to calculate Euclidean distance between two points
def dist(point1, point2):
    return ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) ** 0.5

# Function to lock the PC
def lock_pc():
    ctypes.windll.User32.LockWorkStation()

# Function to start/stop face detection
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

# Function to start face detection
def start_detection():
    global detection_active, video_capture
    video_capture = cv2.VideoCapture(0)  # Access the camera
    detection_active = True
    while detection_active:
        ret, frame = video_capture.read()  # Capture frame-by-frame
        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
            faces = face_detector(gray_frame)  # Detect faces in the frame
            if len(faces) == 0:
                lock_pc()  # Lock the PC if no faces are detected
            for face in faces:
                landmarks = landmark_predictor(gray_frame, face)  # Detect facial landmarks
                landmarks = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]  # Extract landmarks

                left_eye_landmarks = landmarks[42:48]  # Extract left eye landmarks
                right_eye_landmarks = landmarks[36:42]  # Extract right eye landmarks

                left_eye_ear = calculate_eye_aspect_ratio(left_eye_landmarks)  # Calculate left eye aspect ratio
                right_eye_ear = calculate_eye_aspect_ratio(right_eye_landmarks)  # Calculate right eye aspect ratio

                avg_ear = (left_eye_ear + right_eye_ear) / 2.0  # Average eye aspect ratio

                # Check if eyes are blinked
                if avg_ear < EYE_AR_THRESH:
                    global blink_counter, is_blinking, last_blink_time
                    blink_counter += 1
                    if blink_counter >= EYE_AR_CONSEC_FRAMES:
                        is_blinking = True
                        last_blink_time = time.time()  # Update last blink time
                else:
                    blink_counter = 0
                    is_blinking = False

            # Lock PC if blinking is not detected for more than 2 seconds
            if not is_blinking and time.time() - last_blink_time > blink_timeout.get():
                lock_pc()

            # Display the frame in the GUI
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if dark_mode:
                frame = Image.fromarray(frame).convert('L')
                frame = ImageOps.invert(frame)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            panel.config(image=frame)
            panel.image = frame

    # Release camera and close OpenCV windows when detection is stopped
    video_capture.release()
    cv2.destroyAllWindows()

# Function to stop face detection
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

# Create GUI window
root = tk.Tk()
root.title("VisageGuard – Intelligent Facial Recognition for Enhanced PC Security")

# Load and resize logo image
logo_image = Image.open("Logo.jpg")
logo_image = logo_image.resize((30, 30), Image.BICUBIC)
logo_image = ImageTk.PhotoImage(logo_image)

# Set logo as window icon
root.iconphoto(True, logo_image)

# Add minimize, maximize, and close buttons to the window
minimize_btn = tk.Button(root, text="-", command=root.iconify, bd=0)
minimize_btn.place(x=root.winfo_screenwidth()-50, y=0, width=20, height=20)

maximize_btn = tk.Button(root, text="[]", command=root.state, bd=0)
maximize_btn.place(x=root.winfo_screenwidth()-30, y=0, width=20, height=20)

close_btn = tk.Button(root, text="x", command=root.destroy, bd=0)
close_btn.place(x=root.winfo_screenwidth()-10, y=0, width=20, height=20)

# Create panel to display camera feed
panel = tk.Label(root)
panel.pack(padx=10, pady=10)

# Create button to start/stop detection
start_button = tk.Button(root, text="Start Detection", command=toggle_detection)
start_button.pack(padx=10, pady=5)

# Create settings menu
settings_menu = tk.Menu(root)
root.config(menu=settings_menu)

# Add dark mode toggle option to settings menu
settings_submenu = tk.Menu(settings_menu, tearoff=0)
settings_submenu.add_command(label="Toggle Dark Mode", command=toggle_dark_mode)
settings_menu.add_cascade(label="Settings", menu=settings_submenu)

# Create slider for blink timeout
blink_timeout = tk.DoubleVar()
blink_timeout.set(4)  # Default value
timeout_slider = tk.Scale(root, from_=1, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Blink Timeout (seconds)", variable=blink_timeout)
timeout_slider.pack(padx=10, pady=5)

# Automatically start detection
toggle_detection()

# Start Tkinter main loop
root.mainloop()

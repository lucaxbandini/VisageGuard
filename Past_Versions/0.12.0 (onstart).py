import cv2  # Importing OpenCV for image processing
import dlib  # Importing dlib for face detection and landmark prediction
import ctypes  # For locking the PC
import time  # For time-related functions
import tkinter as tk  # For creating GUI
from PIL import Image, ImageTk, ImageOps  # For image manipulation
import threading  # For running tasks concurrently
import winreg  # For managing Windows registry keys
import os  # For operating system related tasks

# Load face detector and landmark predictor
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # File for facial landmarks

# Constants for eye aspect ratio
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 3

# Initialize counters and flags
blink_counter = 0
is_blinking = False
last_blink_time = time.time()  # Variable to store the time of the last detected blink

# Define detection_active at the global level
detection_active = False

# Define dark mode variable
dark_mode = False

# Function to calculate eye aspect ratio
def calculate_eye_aspect_ratio(eye_landmarks):
    # Compute the Euclidean distances between the sets of eye landmarks
    vertical_dist1 = dist(eye_landmarks[1], eye_landmarks[5])
    vertical_dist2 = dist(eye_landmarks[2], eye_landmarks[4])

    # Compute the Euclidean distance between the horizontal eye landmarks
    horizontal_dist = dist(eye_landmarks[0], eye_landmarks[3])

    # Compute the eye aspect ratio
    ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)

    # Return the eye aspect ratio
    return ear

# Function to calculate Euclidean distance between two points
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
        detection_thread.daemon = True  # Daemonize thread to stop it when the main program exits
        detection_thread.start()
        start_button.config(text="Stop Detection")
        # Enable auto-start on PC login
        set_auto_start(True)
    else:
        stop_detection()
        start_button.config(text="Start Detection")
        # Disable auto-start on PC login
        set_auto_start(False)

# Function to set auto-start on PC login
def set_auto_start(enable=True):
    key = winreg.HKEY_CURRENT_USER
    run_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "SecureVisage"
    exe_path = os.path.abspath(__file__)
    if enable:
        with winreg.OpenKey(key, run_key_path, 0, winreg.KEY_WRITE) as key_handle:
            winreg.SetValueEx(key_handle, app_name, 0, winreg.REG_SZ, exe_path)
    else:
        try:
            with winreg.OpenKey(key, run_key_path, 0, winreg.KEY_WRITE) as key_handle:
                winreg.DeleteValue(key_handle, app_name)
        except FileNotFoundError:
            pass

# Function to start detection
def start_detection():
    global detection_active, cap
    cap = cv2.VideoCapture(0)  # Access the camera
    detection_active = True  # Declare detection_active as a global variable
    while detection_active:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret:
            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the grayscale frame
            faces = face_detector(gray)

            # If no faces detected, lock the PC
            if len(faces) == 0:
                lock_pc()

            # Loop over detected faces
            for face in faces:
                # Detect facial landmarks
                shape = landmark_predictor(gray, face)
                shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

                # Extract left and right eye landmarks
                left_eye = shape[42:48]
                right_eye = shape[36:42]

                # Calculate eye aspect ratio for left and right eyes
                left_ear = calculate_eye_aspect_ratio(left_eye)
                right_ear = calculate_eye_aspect_ratio(right_eye)

                # Average the eye aspect ratio
                ear = (left_ear + right_ear) / 2.0

                # Check if the eye aspect ratio is below the threshold
                if ear < EYE_AR_THRESH:
                    global blink_counter, is_blinking, last_blink_time
                    blink_counter += 1

                    # If eyes are closed for a sufficient number of frames, consider it as blinking
                    if blink_counter >= EYE_AR_CONSEC_FRAMES:
                        is_blinking = True
                        last_blink_time = time.time()  # Update last blink time
                else:
                    # If eyes are open, reset the counter
                    blink_counter = 0
                    is_blinking = False

            # Check if blinking isn't detected for more than 2 seconds
            if not is_blinking and time.time() - last_blink_time > blink_timeout.get():
                lock_pc()

            # Display the resulting frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if dark_mode:
                frame = Image.fromarray(frame).convert('L')
                frame = ImageOps.invert(frame)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            panel.config(image=frame)
            panel.image = frame

    # Release the camera and close OpenCV windows when detection is stopped
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

# Function to minimize the window
def minimize_window():
    root.iconify()

# Function to maximize/restore the window
def maximize_window():
    root.state('zoomed' if root.state() == 'normal' else 'normal')

# Function to close the window
def close_window():
    stop_detection()
    root.destroy()

# Create Tkinter window
root = tk.Tk()
root.title("VisageGuard – Intelligent Facial Recognition for Enhanced PC Security")

# Load and resize the logo image
logo_image = Image.open("Logo.jpg")
logo_image = logo_image.resize((30, 30), Image.BICUBIC)
logo_image = ImageTk.PhotoImage(logo_image)

# Set the logo as the window icon
root.iconphoto(True, logo_image)

# Add minimize button
minimize_btn = tk.Button(root, text="-", command=minimize_window, bd=0)
minimize_btn.place(x=root.winfo_screenwidth()-50, y=0, width=20, height=20)

# Add maximize button
maximize_btn = tk.Button(root, text="[]", command=maximize_window, bd=0)
maximize_btn.place(x=root.winfo_screenwidth()-30, y=0, width=20, height=20)

# Add close button
close_btn = tk.Button(root, text="x", command=close_window, bd=0)
close_btn.place(x=root.winfo_screenwidth()-10, y=0, width=20, height=20)

# Create a panel to display the camera feed
panel = tk.Label(root)
panel.pack(padx=10, pady=10)

# Create a button to start/stop detection
start_button = tk.Button(root, text="Start Detection", command=toggle_detection)
start_button.pack(padx=10, pady=5)

# Create a settings menu
settings_menu = tk.Menu(root)
root.config(menu=settings_menu)

# Function to toggle auto-start on login
def toggle_auto_start():
    enable_auto_start = auto_start_var.get()
    set_auto_start(enable_auto_start)

# Add dark mode toggle option to the settings menu
settings_submenu = tk.Menu(settings_menu, tearoff=0)
settings_submenu.add_command(label="Toggle Dark Mode", command=toggle_dark_mode)

# Add auto-start on login option
auto_start_var = tk.BooleanVar()
auto_start_var.set(False)  # Default value
settings_submenu.add_checkbutton(label="Start on Login", variable=auto_start_var, command=toggle_auto_start)

settings_menu.add_cascade(label="Settings", menu=settings_submenu)

# Create a slider for blink timeout
blink_timeout = tk.DoubleVar()
blink_timeout.set(4)  # Default value
timeout_slider = tk.Scale(root, from_=1, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Blink Timeout (seconds)", variable=blink_timeout)
timeout_slider.pack(padx=10, pady=5)

# Automatically start detection
toggle_detection()

# Start the Tkinter main loop
root.mainloop()

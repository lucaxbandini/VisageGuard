import cv2  # Import the OpenCV library for image processing
import dlib  # Import the dlib library for facial detection and landmark prediction
import ctypes  # Import the ctypes library for locking the PC
import time  # Import the time module for time-related operations
import tkinter as tk  # Import tkinter for GUI
from PIL import Image, ImageTk  # Import PIL for image handling
import threading  # Import threading for concurrent execution

# Load face detector and landmark predictor
detector = dlib.get_frontal_face_detector()  # Initialize the face detector
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Load the facial landmark predictor

# Constants for eye aspect ratio and blinking detection
EYE_AR_THRESH = 0.25  # Set the threshold for eye aspect ratio
EYE_AR_CONSEC_FRAMES = 3  # Set the number of consecutive frames for blinking detection

# Initialize counters and booleans for blinking detection
COUNTER = 0  # Counter to track consecutive frames with closed eyes
BLINKING = False  # Boolean flag to indicate blinking state
last_blink_time = time.time()  # Variable to store the time of the last detected blink

# Define detection_active and dark_mode at the global level
detection_active = False
dark_mode = False

# Function to calculate eye aspect ratio
def eye_aspect_ratio(eye):
    # Compute the Euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist(eye[1], eye[5])
    B = dist(eye[2], eye[4])

    # Compute the Euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist(eye[0], eye[3])

    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

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
    else:
        stop_detection()
        start_button.config(text="Start Detection")

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
            faces = detector(gray)

            # If no faces detected, lock the PC
            if len(faces) == 0:
                lock_pc()

            # Loop over detected faces
            for face in faces:
                # Detect facial landmarks
                shape = predictor(gray, face)
                shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

                # Extract left and right eye landmarks
                left_eye = shape[42:48]
                right_eye = shape[36:42]

                # Calculate eye aspect ratio for left and right eyes
                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)

                # Average the eye aspect ratio
                ear = (left_ear + right_ear) / 2.0

                # Check if the eye aspect ratio is below the threshold
                if ear < EYE_AR_THRESH:
                    global COUNTER, BLINKING, last_blink_time
                    COUNTER += 1

                    # If eyes are closed for a sufficient number of frames,
                    # consider it as blinking
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        BLINKING = True
                        last_blink_time = time.time()  # Update last blink time
                else:
                    # If eyes are open, reset the counter
                    COUNTER = 0
                    BLINKING = False

            # Check if blinking isn't detected for more than 2 seconds
            if not BLINKING and time.time() - last_blink_time > blink_timeout.get():
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
        panel.config(bg='black')
        start_button.config(bg='gray', fg='white')
        settings_menu.config(bg='black', fg='white')
    else:
        root.config(bg='white')
        panel.config(bg='white')
        start_button.config(bg='white', fg='black')
        settings_menu.config(bg='white', fg='black')

# Create Tkinter window
root = tk.Tk()
root.title("VisageGuard – Intelligent Facial Recognition for Enhanced PC Security")

# Create a panel to display the camera feed
panel = tk.Label(root)
panel.pack(padx=10, pady=10)

# Create a button to start/stop detection
start_button = tk.Button(root, text="Start Detection", command=toggle_detection)
start_button.pack(padx=10, pady=5)

# Create a settings menu
settings_menu = tk.Menu(root)
root.config(menu=settings_menu)

# Add dark mode toggle option to the settings menu
settings_submenu = tk.Menu(settings_menu, tearoff=0)
settings_submenu.add_command(label="Toggle Dark Mode", command=toggle_dark_mode)
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

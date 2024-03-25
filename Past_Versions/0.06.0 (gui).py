# Import necessary libraries
import cv2  # For computer vision tasks
import dlib  # For face detection and landmark prediction
import ctypes  # For system functions like locking the PC
import tkinter as tk  # For creating the GUI
import time
from PIL import Image, ImageTk  # For handling images in tkinter

# Load face detector and landmark predictor
detector = dlib.get_frontal_face_detector()  # Initialize the face detector
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Load the facial landmark predictor

# Constants for eye aspect ratio and blinking detection
EYE_AR_THRESH = 0.25  # Threshold for eye aspect ratio to detect blinking
EYE_AR_CONSEC_FRAMES = 3  # Number of consecutive frames for blinking detection

# Initialize counters and flags
COUNTER = 0  # Counter for consecutive frames with eyes closed
BLINKING = False  # Flag to track blinking status
last_blink_time = 0  # Variable to store the time of the last detected blink

# Function to calculate eye aspect ratio
def eye_aspect_ratio(eye_landmarks):
    # Calculate distances between eye landmarks
    vertical_left = dist(eye_landmarks[1], eye_landmarks[5])
    vertical_right = dist(eye_landmarks[2], eye_landmarks[4])
    horizontal = dist(eye_landmarks[0], eye_landmarks[3])

    # Compute the eye aspect ratio
    ear = (vertical_left + vertical_right) / (2.0 * horizontal)
    return ear

# Function to calculate euclidean distance between two points
def dist(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

# Function to lock the PC
def lock_pc():
    ctypes.windll.User32.LockWorkStation()  # Lock the PC using system functions

# Function to start/stop liveness detection
def toggle_detection():
    global detection_active
    if not detection_active:
        start_detection()
        start_button.config(text="Stop Detection")
    else:
        stop_detection()
        start_button.config(text="Start Detection")

# Function to start liveness detection
def start_detection():
    global detection_active, BLINKING, last_blink_time
    detection_active = True
    while detection_active:
        # Capture frame-by-frame from the camera
        ret, frame = cap.read()

        if ret:  # Check if frame is successfully captured
            # Convert the frame to grayscale for processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces using the dlib detector
            faces = detector(gray)

            # If no faces are detected, lock the PC
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
                    COUNTER += 1

                    # If eyes are closed for a sufficient number of frames, consider it as blinking
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        BLINKING = True
                        last_blink_time = time.time()  # Update last blink time
                else:
                    # If eyes are open, reset the counter
                    COUNTER = 0
                    BLINKING = False

            # Check if blinking isn't detected for more than 3 seconds and lock PC
            if not BLINKING and time.time() - last_blink_time > 3:
                lock_pc()

            # Display the resulting frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            panel.config(image=frame)
            panel.image = frame

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Function to stop liveness detection
def stop_detection():
    global detection_active
    detection_active = False

# Create tkinter window
root = tk.Tk()
root.title("Liveness Detection and PC Locking")

# Create a panel to display the camera feed
panel = tk.Label(root)
panel.pack(padx=10, pady=10)

# Create a button to start/stop liveness detection
start_button = tk.Button(root, text="Start Detection", command=toggle_detection)
start_button.pack(padx=10, pady=5)

# Access the camera
cap = cv2.VideoCapture(0)

# Flag to track if detection is active
detection_active = False

# Start the tkinter main loop
root.mainloop()

# Release the camera and close OpenCV windows
cap.release()
cv2.destroyAllWindows()

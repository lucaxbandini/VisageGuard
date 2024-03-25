import cv2  # Importing the OpenCV library for computer vision
import dlib  # Importing the dlib library for face detection and landmark prediction
import ctypes  # Importing a library for system functions like locking the PC
import time  # Importing the time module for time-related operations

# Load face detector and landmark predictor
detector = dlib.get_frontal_face_detector()  # Initializing the face detector
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Loading the facial landmark predictor

# Constants for eye aspect ratio and blinking detection
EYE_AR_THRESH = 0.25  # Setting the threshold for eye aspect ratio
EYE_AR_CONSEC_FRAMES = 3  # Setting the number of consecutive frames for blinking detection

# Initialize counters and booleans
COUNTER = 0  # Counter for consecutive frames with eyes closed
BLINKING = False  # Boolean to track blinking status
last_blink_time = time.time()  # Variable to store the time of the last detected blink

# Function to calculate eye aspect ratio
def eye_aspect_ratio(eye):
    # Compute the euclidean distances between eye landmarks
    A = dist(eye[1], eye[5])
    B = dist(eye[2], eye[4])

    # Compute the euclidean distance between the horizontal eye landmark
    C = dist(eye[0], eye[3])

    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # Return the eye aspect ratio
    return ear

# Function to calculate euclidean distance between two points
def dist(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

# Function to lock the PC
def lock_pc():
    user32 = ctypes.windll.User32  # Accessing the system's user32 library
    user32.LockWorkStation()  # Locking the PC

# Access the camera
cap = cv2.VideoCapture(0)  # Initializing the camera

# Main loop for video processing
while True:
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
                # If eyes are open, reset the counter and blinking status
                COUNTER = 0
                BLINKING = False

        # Check if blinking isn't detected for more than 3 seconds and lock PC
        if not BLINKING and time.time() - last_blink_time > 3:
            lock_pc()

    # Display the resulting frame
    cv2.imshow('Liveness Detection', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close OpenCV windows
cap.release()
cv2.destroyAllWindows()

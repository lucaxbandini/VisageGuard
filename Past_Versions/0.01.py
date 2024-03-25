import cv2  # Importing the library for image processing
import dlib  # Importing the library for facial landmark detection
import ctypes  # Importing a library to manage system functions (like locking the PC)

# Load the face detector and the facial landmark predictor
detector = dlib.get_frontal_face_detector()  # Initializing the face detector
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Loading the facial landmark predictor

# Constants for eye aspect ratio
EYE_AR_THRESH = 0.25  # Setting the threshold for eye aspect ratio
EYE_AR_CONSEC_FRAMES = 3  # Setting the number of consecutive frames for blinking detection

# Initializing counters and booleans for blinking detection
COUNTER = 0
TOTAL = 0
BLINKING = False

# Function to calculate the eye aspect ratio
def eye_aspect_ratio(eye):
    # Calculating the distances between eye landmarks to compute the eye aspect ratio
    A = dist(eye[1], eye[5])
    B = dist(eye[2], eye[4])
    C = dist(eye[0], eye[3])

    # Computing the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # Returning the eye aspect ratio
    return ear

# Function to calculate the euclidean distance between two points
def dist(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

# Function to lock the PC
def lock_pc():
    user32 = ctypes.windll.User32  # Accessing the system's user32 library
    user32.LockWorkStation()  # Locking the PC

# Accessing the camera
cap = cv2.VideoCapture(0)  # Initializing the camera

# Loading the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Main loop for video processing
while True:
    # Capturing frame-by-frame from the camera
    ret, frame = cap.read()

    # Converting the frame to grayscale for processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detecting faces in the grayscale frame
    faces = detector(gray)

    # If no faces are detected, lock the PC
    if len(faces) == 0:
        lock_pc()

    # Looping over the detected faces
    for face in faces:
        # Detecting facial landmarks using the predictor
        shape = predictor(gray, face)
        shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

        # Extracting left and right eye landmarks
        left_eye = shape[42:48]
        right_eye = shape[36:42]

        # Calculating the eye aspect ratio for left and right eyes
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)

        # Averaging the eye aspect ratio
        ear = (left_ear + right_ear) / 2.0

        # Checking if the eye aspect ratio is below the threshold
        if ear < EYE_AR_THRESH:
            COUNTER += 1

            # If eyes are closed for a sufficient number of frames, consider it as blinking
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                BLINKING = True
        else:
            # If eyes are open, reset the counter and blinking status
            COUNTER = 0
            BLINKING = False

    # Displaying blinking status on the frame
    if BLINKING:
        cv2.putText(frame, "Blinking", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Displaying the resulting frame
    cv2.imshow('Liveness Detection', frame)

    # Breaking the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Releasing the camera and closing OpenCV windows
cap.release()
cv2.destroyAllWindows()

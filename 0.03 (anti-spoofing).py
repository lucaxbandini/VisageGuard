import cv2  # Importing the library for image processing
import dlib  # Importing the library for facial landmark detection
import ctypes  # Importing a library to manage system functions (like locking the PC)

# Load the face detector and landmark predictor
detector = dlib.get_frontal_face_detector()  # Initializing the face detector
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Loading the facial landmark predictor

# Constants for eye aspect ratio and anti-spoofing
EYE_AR_THRESH = 0.25  # Setting the threshold for eye aspect ratio
EYE_AR_CONSEC_FRAMES = 3  # Setting the number of consecutive frames for blinking detection
FACE_NOT_DETECTED_COUNTER = 0  # Counter for face not detected
FACE_NOT_DETECTED_TIMEOUT = 30  # Lock PC if no face is detected for 30 frames
COUNTER = 0  # Counter for blinking detection
BLINKING = False  # Boolean to track blinking status

# Function to calculate eye aspect ratio
def eye_aspect_ratio(eye):
    # Calculate the euclidean distances between eye landmarks
    A = dist(eye[1], eye[5])
    B = dist(eye[2], eye[4])

    # Calculate the euclidean distance between the horizontal eye landmark
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

# Function to perform anti-spoofing check
def anti_spoofing_check(face_image):
    # Implement your anti-spoofing check here
    # Here, let's assume a simple check where we always consider the face genuine
    return True

# Access the camera
cap = cv2.VideoCapture(0)  # Initializing the camera

# Main loop for video processing
while True:
    # Capture frame-by-frame from the camera
    ret, frame = cap.read()

    # Convert the frame to grayscale for processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces using the dlib detector
    faces_dlib = detector(gray)

    # Check if no face is detected
    if len(faces_dlib) == 0:
        FACE_NOT_DETECTED_COUNTER += 1
        if FACE_NOT_DETECTED_COUNTER >= FACE_NOT_DETECTED_TIMEOUT:
            lock_pc()
            FACE_NOT_DETECTED_COUNTER = 0
        continue
    else:
        FACE_NOT_DETECTED_COUNTER = 0  # Reset the counter if a face is detected

    # Loop over detected faces
    for face in faces_dlib:
        # Extract facial landmarks
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
        else:
            # If eyes are open, reset the counter and blinking status
            COUNTER = 0
            BLINKING = False

        # Extract face coordinates and dimensions
        x = face.left()
        y = face.top()
        w = face.width()
        h = face.height()

        # Extract face region
        face_image = gray[y:y+h, x:x+w]

        # Perform anti-spoofing check
        is_genuine = anti_spoofing_check(face_image)

        # Draw a rectangle around the face
        if is_genuine:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Spoofed", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Draw blinking status on the frame
    if BLINKING:
        cv2.putText(frame, "Blinking", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Display the resulting frame
    cv2.imshow('Liveness Detection', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close OpenCV windows
cap.release()
cv2.destroyAllWindows()

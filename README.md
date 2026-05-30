# What is VisageGuard?

VisageGuard is a biometric authentication and workstation protection system developed in Python. It leverages facial recognition and liveness detection to verify user identity, automatically lock workstations when authentication fails or an unauthorized user is detected, and strengthen endpoint security through continuous identity verification.

The project was developed as a cybersecurity capstone project and demonstrates practical applications of computer vision, machine learning, and access control technologies in endpoint security.

# Key Features

* Biometric user authentication using facial recognition
* Blink-based liveness detection to mitigate photo spoofing attempts
* Automated workstation locking on unauthorized access
* Multi-user enrollment and management
* Real-time facial detection and identity verification
* Configurable authentication settings
* Local endpoint security monitoring
* Python-based desktop application with graphical user interface

# Technologies Used

- Python
- OpenCV
- dlib
- Tkinter
- face_recognition
- Cryptography
- Computer Vision
- Machine Learning

# Security Concepts Demonstrated

- Biometric Authentication
- Access Control
- Identity Verification
- Endpoint Security
- User Monitoring
- Anti-Spoofing Techniques
- Secure Application Development
  
# Setup

For a complete step-by-step guide, click [here](https://github.com/lucaxbandini/VisageGuard/blob/main/Step-By-Step-Guide.md).

**Must be on Python 3.11.3, Visual Studio Community 2022, Microsoft C++ Build Tools must be installed**

Download [Python 3.11.3](https://www.python.org/downloads/release/python-3113/).

Download [PyCharm](https://www.jetbrains.com/pycharm/download/?section=windows).

Download [Visual Studio Community 2022](https://visualstudio.microsoft.com/downloads/?q=build+tools) (When selecting packages to download, choose "Python development" and "Desktop development with C++". Make sure "C++ Cmake tools for Windows" is selected in the right pane).

**Make sure to fully install Visual Studio Community 2022 before installing Microsoft C++ build tools. This will take some time.**

Download [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (make sure to install any workload that explicitly includes C++ programming).

## Installing Dlib

Download [Cmake](https://cmake.org/download/) (check the box that adds a path for the current user).

Create a new PyCharm project with the latest version of VisageGuard. Leave all settings as default, but make sure "Python version" is set to "Python311".(when asked to bypass Windows Defender, allow it).

Download [dlib-19.24.1-cp311-cp311-win_amd64.whl](https://github.com/Murtaza-Saeed/dlib/blob/master/dlib-19.24.1-cp311-cp311-win_amd64.whl), and place it in the project's directory. Then open the PyCharm terminal and use "py -m pip install .\dlib-19.24.1-cp311-cp311-win_amd64.whl".

In the terminal of the PyCharm project, use "pip install cmake", then "pip install dlib".

View this [article](https://medium.com/analytics-vidhya/how-to-install-dlib-library-for-python-in-windows-10-57348ba1117f) if you have any other issues.

## Setting up the PyCharm project

In the PyCharm project terminal, install the remaining required packages by using "pip install opencv-python, face_recognition, cryptography, fernet".

Download [cutout.png](https://github.com/lucaxbandini/VisageGuard/tree/main/Photos/cutout.png) and [shape_predictor_68_face_landmarks.dat](https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat). Place these files in the same .venv directory as the current version file.

After this, you can run VisageGuard to try it for yourself by clicking the green run button at the top of the project screen.

# Everything Should Look Like This at the End

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/73d8134e-b338-492b-8ac4-9a4f2ef9215d)

# Before You Run...

- You will be locked out of your PC. VisageGuard will stop when this happens so you can get back into your PC. Don't worry about permanently getting locked out. However, if it does happen, restart your PC.

- On versions past 0.16, pressing "Start" before enrolling a user will automatically lock your PC.

- Versions 0.18, 0.19, and 0.21 are a little weird with detecting known faces. If either gives you problems, use version 0.17 or 0.17.1
  
- If you use either of the alternative versions listed above, they will appear to lag a little but run as intended. I hadn't optimized the camera feed yet.

# Known Issues

- Detection startup may require several seconds.
- Application restart required after workstation lock.
- UI performance improvements planned.

# Features to be Added (Listed by Priority)
  
- A better UI
  
- A proper dark mode





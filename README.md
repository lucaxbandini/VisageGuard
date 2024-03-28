# What is VisageGuard?

VisageGuard is a PC locker that works based on facial recognition. 

# Setup

** Must be on Python 3.11.3, Visual Studio Community 2022, Microsoft C++ Build Tools must be installed **

Download PyCharm [here](https://www.jetbrains.com/pycharm/).

Download Visual Studio Community 2022 [here](https://visualstudio.microsoft.com/downloads/?q=build+tools) (make sure to install any workload that explicitly includes C++).

**Make sure to fully install Visual Studio Community 2022 before starting to install Microsoft C++ build tools.**

Download Microsoft C++ Build Tools [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (make sure you install any workload that explicitly includes C++ programming).

## Installing Dlib

Download Cmake [here](https://cmake.org/download/) (check the box that adds a path for the current user).

Create a new PyCharm project with the latest version of VisageGuard (when asked to bypass Windows Defender, allow it).

Download this [file](https://github.com/Murtaza-Saeed/dlib/blob/master/dlib-19.24.1-cp311-cp311-win_amd64.whl), and place it in the project's directory. Then open the PyCharm terminal and use "py -m pip install .\dlib-19.24.1-cp311-cp311-win_amd64.whl".

In the terminal of the PyCharm project, use "pip install cmake", then "pip install dlib".

View this [article](https://medium.com/analytics-vidhya/how-to-install-dlib-library-for-python-in-windows-10-57348ba1117f) if you have any other issues.

## Setting up the PyCharm project

In the PyCharm project terminal, install the remaining required packages by using "pip install (opencv-python, face_recognition)".

Download cutout.png from [Photos](https://github.com/lucaxbandini/VisageGuard/tree/main/Photos), and ["shape_predictor_68_face_landmarks.dat"](https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat), and place them in the same .venv as the current version file.

After this, you can run VisageGuard to try it for yourself by clicking the green run button at the top of the project screen.

# Everything Should Look Like This at the End

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/73d8134e-b338-492b-8ac4-9a4f2ef9215d)

# Current Known Issues

- Pressing "Start" will not immediately start detection; give it a few seconds and a window will appear.

- Pressing "Stop" while detection is running will cause the program to freeze.

- In the settings tab, pressing the "Enter" button on your keyboard will not work; click "Save".

- After your PC locks, press "Stop", then press "Start" to restart detection.

- Dark mode does not work as intended.

# Features to be Added (Listed by Priority)

- User enrollment
  
- Enhanced performance and error handling
  
- A better UI
  
- A proper dark mode





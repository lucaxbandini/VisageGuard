**As recommended, this step-by-step guide will allow you to easily test VisageGuard. Please make sure to follow each step carefully.**

# Preliminary Set-up

## Downloading Python 3.11.3
To download Python 3.11.3, follow this [link](https://www.python.org/downloads/release/python-3113/). Scroll down and choose the correct version for your operating system (I have Windows, so I'll choose "Windows installer (64-bit)).

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/c946aa3d-dfe2-48d5-8d9a-55d951cf1bed)

## Downloading PyCharm
To download PyCharm, follow this [link](https://www.jetbrains.com/pycharm/download/?section=windows). Scroll down and install PyCharm Community Edition.

Upon opening PyCharm for the first time, it will ask you if you want to import settings. Choose "Do not import settings".

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/69e7fed8-e771-465d-9689-6b2007797d95)

## Downloading Visual Studio Community 2022
To download Visual Studio Community 2022, follow this [link](https://visualstudio.microsoft.com/downloads/?q=build+tools). Choose the community edition. When selecting packages to download, choose "Python development" and "Desktop development with C++".

Most importantly, make sure that "C++ CMake tools for Windows" is installed. It is located on the right side of the installation screen under "Desktop development with C++".

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/13265b69-06d9-4fcc-8d1a-ab12bda86e7b)

**Make sure to fully install Visual Studio Community 2022 before installing Microsoft C++ build tools. This will take some time.**

## Downloading Microsoft C++ Build Tools
To download Microsoft C++ Build Tools, follow this [link](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

Most importantly, select "Desktop development with C++" and make sure that "C++ CMake tools for Windows" is installed. It is located on the right side of the installation screen under "Desktop development with C++".

# Installing Dlib

Download [Cmake](https://cmake.org/download/) ( Choose "Windows x64 Installer". During installation, check the box that adds a path for the current user).

Create a new PyCharm project by clicking the Menu button at the top of the PyCharm window, then on "New Project". Leave all settings as default, except for "Python version"; make sure it is set to "Python311".

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/05d64660-4b13-44d0-a6e4-4a0492fdcc3b)

A Microsoft Defender alert will appear at the bottom right corner of the PyCharm window: click automatically, then yes.

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/c4f1cc2d-d7cc-4b45-afda-788007c2d0e0)

Download the current version of VisageGuard from [here](https://github.com/lucaxbandini/VisageGuard/tree/main) and add it to the PyCharm project. Do this by right-clicking on .venv, hovering over "Open In" and then choosing explorer. Click into the .venv folder and place the latest version's file.

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/1f4f1780-6b3a-4ada-a845-6b97626e2e95)

As you can see, the file will be added to the project.

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/eb0f3895-deb8-422a-b6cc-f3d7b624ad67)

Download [dlib-19.24.1-cp311-cp311-win_amd64.whl](https://github.com/Murtaza-Saeed/dlib/blob/master/dlib-19.24.1-cp311-cp311-win_amd64.whl). When the page opens, click on "View Raw" to download the file. Place this in the main project file folder in explorer, outside of .venv.

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/37642a24-f81c-4d09-9578-522b3d123224)

Then, in PyCharm, open the terminal at the bottom-left of the project window. Paste "py -m pip install .\dlib-19.24.1-cp311-cp311-win_amd64.whl" into it and run it by pressing enter on your keyboard.

After this, paste "pip install cmake", then "pip install dlib".

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/8ecfa357-9da7-4710-9897-a4826bec7c47)

# Completing Setup

In the terminal, install the remaining required packages with "pip install opencv-python, face_recognition, cryptography, fernet".

Download [cutout.png](https://github.com/lucaxbandini/VisageGuard/tree/main/Photos/cutout.png) and [shape_predictor_68_face_landmarks.dat](https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat). Just as earlier, place these files inside of the .venv folder.

After this, you can run VisageGuard to try it for yourself by clicking the green run button at the top of the project screen.

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/0dc6295b-b6c2-4e25-a88e-d20dcf81176b)

# Project Folder Should Look Like This at the End

![image](https://github.com/lucaxbandini/VisageGuard/assets/152310492/73d8134e-b338-492b-8ac4-9a4f2ef9215d)


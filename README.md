# Face-Detection-PC-Locker
PC locker that works based on facial recognition
# Installing Dlib
Download this file: https://github.com/Murtaza-Saeed/dlib/blob/master/dlib-19.24.1-cp311-cp311-win_amd64.whl, then open terminal where you downloaded it to. Use "py -m pip install .\dlib-19.24.1-cp311-cp311-win_amd64.whl"
In PyCharm, use "pip install cmake", then "pip3 install dlib"

# To use
** Must be on Python 3.11.3, Visual Studio Community 2022 must be installed as well **

Open the current version of VisageGuard in PyCharm, and install all required packages "pip install (opencv-python, face_recognition)".

Download "shape_predictor_68_face_landmarks.dat" from https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat, and place it in the same .venv as the current version.

After this, you should be able to run VisageGuard to try it for yourself!

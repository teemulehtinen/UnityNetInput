# Receiving Unity game input over network as UDP messages

This repository contains a [Unity3D](https://unity3d.com/) 2018.3.2f1 game
project. A GameObject named `Marker` has a `PositionListener` script attached
that listens for incoming positions as UDP messages. It moves the GameObject
accordingly in the Scene.

A Python script `bowler.py` exists to generate and send different object
trajectories to the Unity listener. This may be usefull in testing.
Once latest [Python](https://www.python.org/downloads/) is installed
the script will execute by double clicking or from command line.

![ScreenToGif](https://raw.githubusercontent.com/teemulehtinen/UnityNetInput/master/UnityNetInput.gif "ScreenToGif")

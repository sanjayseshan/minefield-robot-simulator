# Minefield Robot Simulator Game 

My project is to build a robot simulation game. The simulator features a randomly generated field complete with objects (cubes and balls) and obstacles such as barriers (walls). The goal is for the player to complete a series of tasks in this generated world. The user controls the robot using a command-based interface or keyboard interface that allows control over the robot’s acceleration in each direction. The players must navigate the robot to push the cubes and balls into pre-defined targets. Placing an object in a target will give the player points and once all objects are delivered, the level is complete. The user is then taken to a new, harder level which has more objects and obstacles.
The main deliverables of this project will be a 3D field, a physics simulator, and multiple levels of game play which get increasing difficulty for the player. A multiplayer mode is available using sockets to connect to a client program.

## Running program:
* Required modules:
```
numpy (pip install numpy)
threading
sockets
```
* Execution:
```
Single player:
python project.py

Multiplayer:
Server - python project.py
Client - python client.py

Note: if your display is smaller than 1920x1200 px resolution, you need to adjust the last line of code in the main program(s) to fit your screen. Otherwise, UI components may be cut off. 1920x1200 resolution is optimal.
```

* Shortcuts: none; see Help screen (or help.png) for usage


Unless otherwise stated, all code and pictures are by the author, Sanjay Seshan.
## Sanjay Seshan

"""
Main program that loads the tkinter graphics
Manages the game settings
Generates a simulated field and runs the simulator
Executes terminal commands
"""

## 112 graphics 
## from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
from cmu_112_graphics import *
import math
import time
import random
from RGB import *
from shapes import *
from operations import *
from items import *
import sys
import socket
import pickle
import threading
import struct
from TKItems import *

## Main simulation class that defines a single level with difficulty
class Simulator(object):
    def __init__(self, width, height, app, settings, level, difficulty, 
                multiplayer=True):
        ## configure basic variables
        self.width, self.height = width, height
        self.app = app
        self.settings = settings
        self.level = level
        self.difficulty = difficulty
        ## define fixed items on the field (robot, floor, outer wall)
        self.robot = Robot(20, 20)
        self.xz = Wall(-200,0,-200,200,0,100, color=RGB(255,255,255), 
                floor=True)
        self.wall1 = Wall(-200,0,-200,200,20,-195, color=RGB(200,200,255))
        self.wall2 = Wall(-200,0,-200,-195,20,100, color=RGB(200,200,255), 
            outer=True)
        self.wall3 = Wall(200,0,-200,195,20,100, color=RGB(200,200,255), 
            outer=True)
        self.wall4 = Wall(-200,0,100,200,20,95, color=RGB(200,200,255))

        ## list of objects by classification
        self.objects = [self.wall1, self.wall2, self.wall3, self.robot,
                        self.wall4]
        self.movingItems = [self.robot]
        self.fixedItems = [self.wall1, self.wall2, self.wall3, 
                            self.wall4]
        self.targets = []

        self.multiplayer = multiplayer
        self.robot2 = Robot(20, 20, 30, 0, -30, color=RGB(50,50,50))
        if multiplayer:
            self.objects.append(self.robot2)
            self.movingItems.append(self.robot2)

        ## UI interaction vars
        self.perspective = PointR3(5,30,5)
        self.thirdPerson = False

        ## calculate objects to generate based on level and difficulty; 
        ## generate field
        boxes = walls = max((self.difficulty+self.level)//2,1)
        targets = max((self.difficulty+self.level)//6, 1)
        balls = max((self.difficulty+self.level)//8, 1)
        self.mines = boxes + balls
        self.minesDisposed = 0
        self.timeout = 0.3
        self.generateField(boxes, walls, targets, balls)

        ## define vars to determine refresh rate (time and changing pos)
        self.ti = time.time()
        self.lastMid = PointR3(-999, -999, -999)

    ## check if a mine (moving item) intersects with an existing 
    ## object on the field
    def checkIntersections(self):
        for i in range(len(self.movingItems)):
            obj1 = self.movingItems[i]
            ## check amongst other mines
            for obj2 in self.movingItems[i+1:]:
                if obj1 in obj2:
                    return True
            ## check with target
            for target in self.targets:
                if (obj1 in target):
                    return True
            ## check with walls
            for wall in self.fixedItems:
                if (obj1 in wall):
                    return True
        return False

    ## randomly generate field without overlaps
    def generateField(self, boxes=1, walls=1, targets=1, balls=1):
        works = False
        while not works:
            works = (self.generateWalls(walls) and
                    self.generateBoxes(boxes) and
                    self.generateBalls(balls) and 
                    self.generateTargets(targets))
        ## place floor last
        self.objects.append(self.xz)
        self.fixedItems.append(self.xz)

    ## generate vertical and horizontal walls
    def generateWalls(self, walls):
        ti = time.time()
        for _ in range(walls):
            ## randomly decide to be vertical or horizontal wall
            ## test a initial wall
            if random.randint(0,1) == 0:
                ## get random dimensions (vertical wall)
                altdim = random.randint(-180,180)
                maini0 = random.randint(-180,80)
                mainf0 = random.randint(-180,80)
                maini = min(maini0, mainf0)
                mainf = max(maini0, mainf0)
                ## create wall
                wall = Wall(altdim,0,maini,
                        altdim+5,20,mainf, 
                        color=RGB(0,0,255))
                ## create wall with 20m buffer
                wallTmp = Wall(altdim-20,0,maini-20,
                            altdim+25,20,mainf+20, 
                            color=RGB.getRandom())
            else:
                ## get random dimensions (horizontal wall)
                altdim = random.randint(-180,80)
                maini0 = random.randint(-180,180)
                mainf0 = random.randint(-180,180)
                maini = min(maini0, mainf0)
                mainf = max(maini0, mainf0)
                wall = Wall(maini,0,altdim,
                        mainf,20,altdim+5, 
                        color=RGB.getRandom())
                wallTmp = Wall(maini-20,0,altdim-20,
                        mainf+20,20,altdim+25, 
                        color=RGB(0,0,255))
            ## check to see that the buffered wall does not overlap with another
            ## wall
            works = True
            for wallOld in self.fixedItems:
                if wallTmp in wallOld:
                    works = False

            ## Wall must be between 20 and 70m in length
            if abs(mainf-maini) > 70 or abs(mainf-maini) < 30:
                works = False
            self.objects.append(wall)
            self.fixedItems.append(wall)
            ## if checks fail, calculate a new wall and recheck
            while not works:
                if time.time() - ti> self.timeout: return False
                self.objects.pop()
                self.fixedItems.pop()
                ## randomly decide to be vertical or horizontal wall
                if random.randint(0,1) == 0:
                    ## get random dimensions (vertical wall)
                    altdim = random.randint(-180,180)
                    maini0 = random.randint(-180,80)
                    mainf0 = random.randint(-180,80)
                    maini = min(maini0, mainf0)
                    mainf = max(maini0, mainf0)
                    ## create wall
                    wall = Wall(altdim,0,maini,
                            altdim+5,20,mainf, 
                            color=RGB(0,0,255))
                    ## create wall with 20m buffer
                    wallTmp = Wall(altdim-20,0,maini-20,
                                altdim+25,20,mainf+20, 
                                color=RGB.getRandom())
                else:
                    ## get random dimensions (horizontal wall)
                    altdim = random.randint(-180,80)
                    maini0 = random.randint(-180,180)
                    mainf0 = random.randint(-180,180)
                    maini = min(maini0, mainf0)
                    mainf = max(maini0, mainf0)
                    wall = Wall(maini,0,altdim,
                            mainf,20,altdim+5, 
                            color=RGB(0,0,255))
                    wallTmp = Wall(maini-20,0,altdim-20,
                            mainf+20,20,altdim+25, 
                            color=RGB.getRandom())
                ## check to see that the buffered wall does not overlap with 
                ## another wall
                works = True
                for wallOld in self.fixedItems:
                    if wallTmp in wallOld:
                        works = False
                if abs(mainf-maini) > 80 or abs(mainf-maini) < 30:
                    works = False
                self.objects.append(wall)
                self.fixedItems.append(wall)
        return True

    ## Generates boxes (mines) in random positions
    def generateBoxes(self, boxes):
        ti = time.time()
        for i in range(boxes):
            ## try a random box
            item = Box(10,10,random.randint(-180,180),0,random.randint(-180,70),
                20, RGB.getRandom())
            self.movingItems.append(item)
            self.objects.append(item)
            ## if overlaps with another item, regenerate
            while self.checkIntersections():
                if time.time() - ti > self.timeout: return False
                self.movingItems.pop()
                self.objects.pop()
                item = Box(10,10,random.randint(-180,180),0,
                    random.randint(-180,70), 20, RGB.getRandom())
                self.movingItems.append(item)
                self.objects.append(item)
        return True

    ## generate balls (mines) in random positions
    def generateBalls(self, balls):
        for i in range(balls):
            ti = time.time()
            ## test a ball
            item = self.ball = Ball(5, random.randint(-180,180),5,
                random.randint(-180,70), mass=2)
            self.movingItems.append(item)
            self.objects.append(item)
            ## if ball overlaps somewhere, regenerate
            while self.checkIntersections():
                if time.time() - ti > self.timeout: return False
                self.movingItems.pop()
                self.objects.pop()
                item = self.ball = Ball(5, random.randint(-180,180),5,
                    random.randint(-180,70), mass=2)
                self.movingItems.append(item)
                self.objects.append(item)
        return True

    ## find position for targets randomly
    def generateTargets(self, targets):
        for i in range(targets):
            ti = time.time()
            ## test position as a box
            randX = random.randint(-170,170)
            randZ = random.randint(-170,70)
            item = Box(20,20,randX,0,randZ,5, RGB.getRandom())
            self.movingItems.append(item)
            self.objects.append(item)
            ## if testing box fails, regenerate
            while self.checkIntersections():
                if time.time() - ti > self.timeout: return False
                self.movingItems.pop()
                self.objects.pop()
                randX = random.randint(-170,170)
                randZ = random.randint(-170,70)
                item = Box(20,20,randX,0,randZ,5, RGB.getRandom())
                self.movingItems.append(item)
                self.objects.append(item)
            ## replace testing box with actual target
            self.movingItems.pop()
            self.objects.pop()
            target = Target(randX,0,randZ,20)
            self.objects.append(target)
            self.targets.append(target)
        return True

    ## update positions and view of every item
    def timerFired(self):
        ## sort objects for ordering on screen (sorted by traced intersections 
        ## to camera)
        myApp.timerDelay = time.time()-self.ti
        self.ti = time.time()
        self.objects.sort()
        self.handleCollisions()
        self.updateView()

    ## check if moving items are intersecting each other, a target, or a wall
    def handleCollisions(self):
        for i in range(0, len(self.movingItems)):
            obj1 = self.movingItems[i]
            obj1.update(myApp.timerDelay)
            ## if the object is not moving, skip
            if obj1.getVelocity() == (0,0,0):
                continue
            ## check for colission with another mine and robot
            for obj2 in self.movingItems[i+1:]:
                if obj1 in obj2:
                    obj2.handleCollision(obj1)
            ## check if within a target; if so --> +1 pts 
            for target in self.targets:
                if (obj1 in target):
                    obj1.updateVelocity(0, 0, 0)
                    self.minesDisposed += 1
                    self.app.score += 1
            ## check if hit wall
            for wall in self.fixedItems:
                if (obj1 in wall):
                    wall.handleCollision(obj1)

    ## in 1st person, update view to be centered at the robot's position
    def updateView(self):
        if self.thirdPerson:
            return
        ## only reset drawing cache if robot moved
        if self.robot.midpoint() != self.lastMid:
            PointR3.R3R2 = {}
        self.lastMid = self.robot.midpoint()
        Matrix.c = (self.perspective + self.robot.midpoint()).asMatrix()
        
    ## zoom in/out on scroll 
    def mouseScrolled(self, event):
        PointR3.R3R2 = {}
        dir = -event.delta/abs(event.delta)
        ## adjust view based on scrolling location and rotate about the current
        ## perspective angle
        dx = (event.x-self.width/2)*2/self.width * dir * 3
        dy = (event.y-self.height/2)*2/self.height * dir * 3
        point = PointR3(dx, dy, dir).rotateX(Matrix.theta[0])\
                .rotateY(Matrix.theta[1]).rotateZ(Matrix.theta[2])
        self.perspective.translate(point.x, point.y, point.z)
        Matrix.c += Matrix([[dx],[dy],[dir]])

    ## track the mouse position on click
    def mousePressed(self, event):
        self.startX, self.startY = event.x, event.y

    ## shift angle of view when dragged
    def mouseDragged(self, event):
        try:
            PointR3.R3R2 = {}
            t0,t1,t2 = Matrix.theta
            ## adjust the Y view angle on drag (from click position)
            dirX = (event.x - self.startX)/abs(event.x - self.startX)
            dirY = -(event.x - self.startX)/abs(event.x - self.startX)
            t1 += dirY/50
            Matrix.theta = (t0,t1,t2)
        except:
            pass

    ## handle key presses
    def keyPressed(self, event):
        try:
            ## toggle first/third person on F1/F2
            if event.key == "F1":
                PointR3.R3R2 = {}
                self.thirdPerson = False
                self.perspective = PointR3(5,30,5)
                Matrix.theta = (-math.pi/10,0,0)
            elif event.key == "F2":
                PointR3.R3R2 = {}
                self.thirdPerson = True
                Matrix.c = Matrix([[0],[100],[200]])
                Matrix.theta = (-math.pi/10,0,0)
            ## if not terminal mode, use WASD controls
            elif not self.app.useTerminal:
                self.remoteKey(event)
        except:
            pass

    ## handle WASD keys to accelerate 20m/s^2 in each direction
    def remoteKey(self, event):
        a = 5
        if event.key == "w":
            self.robot.accelerate(0,0,-a,myApp.timerDelay)
        elif event.key == "a":
            self.robot.accelerate(a,0,0,myApp.timerDelay)
        elif event.key == "s":
            self.robot.accelerate(0,0,a,myApp.timerDelay)
        elif event.key == "d":
            self.robot.accelerate(-a,0,0,myApp.timerDelay)


    ## draw objects to the screen
    def redrawAll(self, canvas):
        self.drawObjects(canvas)
        ## update framerate and timerDelay for physics calculations
        try:
            framerate = 1/(time.time()-self.ti)
        except:
            framerate = 20
        canvas.create_text(self.width-40, 20, 
                        text="FPS: "+ str(int(framerate)))
        ## Draw current level stats --> mines disposed
        canvas.create_text(9*self.width/10, 10*self.height/12, 
                text="Mines Disposed: "+\
                str(self.minesDisposed)+"/"+str(self.mines),
                font="Time 28 bold")

    ## draw bot, mines, and walls
    def drawObjects(self,canvas):
        for obj in self.objects:
            obj.draw(canvas)

## Settings UI
class Settings(object):
    def __init__(self, width, height, app):
        ## define basic vars and modes
        self.width, self.height = width, height
        self.modes = ["command", "keyboard"]
        self.mode = 1
        self.app = app
        ## define buttons for changing modes, difficulty, and level, and to start
        self.modeBtn = TKButton("Input Mode:\n"+self.modes[self.mode], 
                    self.width/5-100, self.height/3, 200, 100, self.changeMode)
        self.difficulty = 0
        self.difficultyBtn = TKButton("Difficulty:\n"+str(self.difficulty), 
                    2*self.width/5-100, self.height/3, 200, 100, 
                    self.changeDifficulty)
        self.level = 0
        self.levelBtn = TKButton("Level:\n"+str(self.level), 
                    3*self.width/5-100, self.height/3, 200, 100, 
                    self.changeLevel)
        self.multiplayer = False
        self.multiplayerBtn = TKButton("Multiplayer:\n"+str(self.multiplayer), 
                    4*self.width/5-100, self.height/3, 200, 100, 
                    self.changeMultiplayer)
        self.start = TKButton("Start!", self.width/2-50, 2*self.height/3, 
                        100, 50, self.startGame)
        self.btns = [self.modeBtn, self.start, self.difficultyBtn, 
                        self.levelBtn, self.multiplayerBtn]
        self.games = [None] * 10

    ## draw all the buttons and title
    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill="lightgrey")
        canvas.create_text(self.width/2, 200, text="Minefield Robot Simulator", 
                        fill="black", font="Times 28")
        for button in self.btns:
            button.draw(canvas)
        if self.multiplayer:
            canvas.create_text(self.width/2, 4*self.height/5, font="Arial 20",
                text="Connect to "+socket.gethostbyname(socket.gethostname()))

    ## call start game to generate a game or load existing level
    def startGame(self, button):
        if self.games[self.level] == None:
            self.games[self.level] = Simulator(self.width, self.height, 
                        self.app, self, self.level, self.difficulty, 
                        multiplayer=self.multiplayer)
        self.app.simulator = self.games[self.level]
        self.app.gameStarted = True
        PointR3.R3R2 = {}

    ## alternate between terminal/keyboard mode
    def changeMode(self, button):
        self.mode = (self.mode + 1)%2
        button.text = "Input Mode:\n"+self.modes[self.mode]
        self.app.useTerminal = self.mode == 0

    def changeMultiplayer(self, button):
        self.multiplayer = not self.multiplayer
        button.text = "Multiplayer:\n"+str(self.multiplayer)

    ## set difficulty
    def changeDifficulty(self, button):
        self.difficulty = (self.difficulty + 1)%8
        button.text = "Difficulty:\n"+str(self.difficulty)

    ## set level
    def changeLevel(self, button):
        self.level = (self.level + 1)%8
        button.text = "Level:\n"+str(self.level)

    ## check button presses
    def mousePressed(self, event):
        for button in self.btns:
                button.mousePressed(event)

    ## check button releases
    def mouseReleased(self, event):
        for button in self.btns:
                button.mouseReleased(event)

## Class to handle multiplayer connections
## Basic socket connection aspects derived from 
## https://github.com/sanjayseshan/pacman/blob/master/ui/scorer.py
class SocketHandler(object):
    def __init__(self, app, host="0.0.0.0", port=8000):
        self.app = app
        self.host = host
        self.port = port
        ## basic socket properties (set up to use TCP)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.connection = None

    ## runs in separate thread; waiting for connection
    def connect(self):
        self.sock.listen(5)
        print("server active on", self.host, self.port)
        while True:
            conn, addresstup = self.sock.accept()
            address, _ = addresstup
            ## on connection, open handlers
            threading.Thread(target = self.send, args=(conn,address)).start()
            threading.Thread(target = self.receive, args=(conn,address)).start()

    ## continously send objects to client
    ## derived structure from 
    ## https://github.com/sanjayseshan/pacman/blob/master/ghost/pacman/move.py
    def send(self, client, address):
        self.connection = client
        print("connection accepted", client, address)
        ## broadcast all objects in the simulator to the client
        while True:
            if self.app.simulator != None:
                L = [self.app.simulator.objects, self.app.simulator.movingItems, 
                    self.app.simulator.fixedItems, self.app.simulator.targets, 
                    self.app.simulator.robot, self.app.simulator.robot2, 
                    self.app.simulator.mines, self.app.simulator.minesDisposed, 
                    self.app.score]
                if not self.broadcast(L):
                    self.connection = None
                    print("ending")
                    return
            time.sleep(0.1)

    ## broadcast data to client
    ## derived broadcast code from 
    ## https://github.com/sanjayseshan/pacman/blob/master/ghost/pacman/move.py
    ## and 
    ## https://pythonprogramming.net/pickle-objects-sockets-tutorial-python-3/
    def broadcast(self, data):
        ## encode strings
        if type(data) == str:
            send_str = str(str(data)).encode()
            send_msg = struct.pack('!I', len(send_str))
            send_msg += send_str
        ## otherwise, dump objects as encoded data with proper header size
        else:
            send_str = pickle.dumps(data)
            HEADERSIZE = 10
            send_msg = bytes(f"{len(send_str):<{HEADERSIZE}}", 'utf-8')+send_str
        try:
            ## send data
            self.connection.sendall(send_msg)
            return True
        except Exception as e:
            print(e)
            return False ## disconnected

    ## wait for data to be received --> process WASD arrows on robot2
    ## derived recieving and decoding code from from 
    ## https://github.com/sanjayseshan/pacman/blob/master/ghost/pacman/move.py
    def receive(self, client, address):
        while True:
            try:
                if self.connection != None:
                    ## collect data until proper sized string is collected
                    data = ''
                    data_len_str= client.recv( struct.calcsize("!I") )
                    data_len = (struct.unpack("!I", data_len_str))[0]
                    while (data_len > 0):
                        data += client.recv( data_len ).decode()
                        data_len -= len(data)
                    ## if WASD key, accelerate robot2
                    if data != '' and self.app.simulator != None:
                        a = 5
                        if data == "w":
                            self.app.simulator.robot2.accelerate(0,0,-a,
                                myApp.timerDelay)
                        elif data == "a":
                            self.app.simulator.robot2.accelerate(a,0,0, 
                                myApp.timerDelay)
                        elif data == "s":
                            self.app.simulator.robot2.accelerate(0,0,a,
                                myApp.timerDelay)
                        elif data == "d":
                            self.app.simulator.robot2.accelerate(-a,0,0,myApp.
                                timerDelay)
            except Exception as e: ## lost connection
                return

## App that runs the Simulator
## basic structure from 
## https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
class myApp(App):
    timerDelay = 0.030 ## in seconds
    def appStarted(self):
        ## Define UI components  
        self.timerDelay = int(myApp.timerDelay*1000)
        self.mouseMovedDelay = int(myApp.timerDelay*1000)
        self.gameStarted = False
        self.simulator = None
        self.score = 0
        self.settings = Settings(self.width, self.height, self)
        self.terminal = Terminal(self)
        self.useTerminal = False
        self.showHelp = False
        self.home = TKButton("Home", self.width-200, 100, 100, 50, self.home)
        self.help = TKButton("Help", self.width-200, 200, 100, 50, self.help)
        self.btns = [self.home, self.help]
        self.helpImage = self.loadImage('help.png')
        self.socket = SocketHandler(self)
        threading.Thread(target=self.socket.connect).start()

    ## show home screen
    def home(self, button):
        self.gameStarted = False
        self.simulator = None

    ## show help screen
    def help(self, button):
        self.showHelp = not self.showHelp

    ## check mousedpressed in each component
    def mousePressed(self, event):
        if self.gameStarted:
            self.simulator.mousePressed(event)            
        else:
            self.settings.mousePressed(event)
        for button in self.btns:
                button.mousePressed(event)

    ## check mousereleased and other events:
    def mouseReleased(self, event):
        if not self.gameStarted:
            self.settings.mouseReleased(event)   
        for button in self.btns:
                button.mouseReleased(event)

    def mouseDragged(self, event):
        if self.gameStarted:
            self.simulator.mouseDragged(event)  

    def mouseScrolled(self, event):
        if self.gameStarted:
            self.simulator.mouseScrolled(event)  

    def keyPressed(self, event):
        if self.gameStarted:
            self.simulator.keyPressed(event)
        if self.useTerminal:
            self.terminal.keyPressed(event)

    def timerFired(self):
        try:
            if self.gameStarted:
                self.simulator.timerFired() 
            if self.useTerminal:
                self.terminal.timerFired()
        except Exception as e:
            print(e)

    ## draw components and score. If score == 20, draw "You Win!"
    def redrawAll(self, canvas):
        if self.gameStarted:
            self.simulator.redrawAll(canvas) 
        else:
            self.settings.redrawAll(canvas)
        for button in self.btns:
            button.draw(canvas)
        canvas.create_text(9*self.width/10, 11*self.height/12, 
                        text="Score: "+str(self.score)+"/20",
                        font="Time 28 bold")
        if self.score == 20:
            canvas.create_text(self.width/2, self.height/12, 
                            text="You Win!!", fill="red",
                            font="Arial 40 bold") 
        if self.useTerminal:
            self.terminal.redrawAll(canvas)
            
        if self.showHelp:
            canvas.create_image(0, 0, 
                image=ImageTk.PhotoImage(self.helpImage), anchor="nw")

    ## on stop, kill all threads
    def appStopped(self):
        sys.exit()

## Recommended screen resolution is 1920x1200
if __name__ == "__main__":
    myApp(width=1920, height=1177, mvcCheck=False)
    
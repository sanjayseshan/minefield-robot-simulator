import socket
import struct
import pickle
import threading
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

class SocketClient(object):
    ## derived settings from 
    ## https://github.com/sanjayseshan/pacman/blob/master/ghost/pacman/move.py
    def __init__(self, app, host="localhost", port=8000):
        self.host = host
        self.port = port
        self.app = app
        ## basic client setup with TCP to send without delay
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        threading.Thread(target = self.process).start()

    ## process data being sent to the client --> objects
    ## connection & receiving aspects derived from 
    ## https://github.com/sanjayseshan/pacman/blob/master/ghost/pacman/move.py
    ## and 
    ## https://pythonprogramming.net/pickle-objects-sockets-tutorial-python-3/
    def process(self):
        ## connect to server
        self.sock.connect((self.host, self.port))
        while True:
            data = ''
            try: 
                ## read data length
                HEADERSIZE = 10
                data_len_str = self.sock.recv(16)
                try:
                    data_len = int(data_len_str[:HEADERSIZE])
                except:
                    continue
                ## receive data until appropriate buffer length
                data = b''
                data += data_len_str
                while (data_len > 0):
                    data += self.sock.recv( data_len )
                    data_len -= len(data)
                try:
                    ## cast the transferred objects to their appropriate 
                    ## simulator locations
                    (self.app.simulator.objects, self.app.simulator.movingItems, 
                    self.app.simulator.fixedItems, self.app.simulator.targets, 
                    self.app.simulator.robot, self.app.simulator.robot2, 
                    self.app.simulator.mines, self.app.simulator.minesDisposed, 
                    self.app.score) = pickle.loads(data[HEADERSIZE:])
                    self.app.simulator.objects.sort()
                except Exception as e:
                    print(e)
            ## on disconnect, attempt to reconnect
            except Exception as e: 
                print("FAIL TO RECEIVE.." + str(e.args) + "..RECONNECTING")
                try:
                    self.sock.close()
                    self.sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM)
                    self.sock.setsockopt(socket.IPPROTO_TCP, 
                        socket.TCP_NODELAY, 1)
                    self.sock.connect((self.host, self.port))
                    print("Connected! to " + self.host)
                except:
                    pass
    
    ## send message to server (keypress)
    ## derived sending code from 
    ## https://github.com/sanjayseshan/pacman/blob/master/ghost/pacman/move.py
    def send(self, message):
        ## encode string with length
        send_str = str(message).encode()
        send_msg = struct.pack('!I', len(send_str))
        send_msg += send_str
        ## send or fail --> reconnect
        try:
            self.sock.sendall(send_msg)
        except Exception as e:
            print("FAILURE TO SEND.." + str(e.args) + "..RECONNECTING")
            try:
                self.sock.connect((self.host, self.port))
                print("connected to " + self.host)
                print("sending " + send_msg)
                self.sock.sendall(send_msg)
            except:
                pass       


## Main simulation class that mirrors a server's
class SimulatorClient(object):
    def __init__(self, width, height, app):
        ## configure basic variables
        self.width, self.height = width, height
        self.app = app
        ## list of objects by classification (empty --> filled by server)
        self.objects = []
        self.movingItems = []
        self.fixedItems = []
        self.targets = []
        self.minesDisposed = 0
        self.mines = 10
        ## UI interaction vars
        self.perspective = PointR3(5,30,5)
        self.robot = None
        self.robot2 = None
        self.thirdPerson = True
        ## define vars to determine refresh rate (time and changing pos)
        self.ti = time.time()
        self.lastMid = PointR3(-999, -999, -999)

    ## update positions and view of every item
    def timerFired(self):
        ## sort objects for ordering on screen (sorted by traced intersections 
        ## to camera)
        myAppClient.timerDelay = time.time()-self.ti
        self.ti = time.time()
        self.updateView()

    ## in 1st person, update view to be centered at the robot's position
    def updateView(self):
        ## update view around robot2 if applicable
        try:
            if self.thirdPerson:
                return
            ## only reset drawing cache if robot moved
            if self.robot2.midpoint() != self.lastMid:
                PointR3.R3R2 = {}
            self.lastMid = self.robot2.midpoint()
            Matrix.c = (self.perspective + self.robot2.midpoint()).asMatrix()
        except:
            pass
                
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
            elif len(event.key) == 1:
                self.app.socket.send(event.key)
        except:
            pass

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

## App that runs the Simulator
## basic structure from 
## https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
class myAppClient(App):
    timerDelay = 0.030 ## in seconds
    def appStarted(self):
        ## Define UI components  
        ## threading.Thread(target=self.timerFired2).start()
        self.timerDelay = int(myAppClient.timerDelay*1000)
        self.mouseMovedDelay = int(myAppClient.timerDelay*1000)
        self.gameStarted = True ## no settings screen in client
        self.score = 0
        self.simulator = SimulatorClient(self.width, self.height, self)
        self.terminal = Terminal(self, client=True)
        self.useTerminal = True ## keep terminal open to connect
        self.showHelp = False
        self.help = TKButton("Help", self.width-200, 200, 100, 50, self.help)
        self.btns = [self.help]
        self.helpImage = self.loadImage('help.png')
        self.socket = None

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
        if self.gameStarted:
            self.simulator.timerFired() 
        if self.useTerminal:
            self.terminal.timerFired()
        
    ## draw components and score. If score == 20, draw "You Win!"
    ## put connection instructions
    def redrawAll(self, canvas):
        if self.socket == None:
            canvas.create_text(self.width/2, self.height/2, font="Arial 30",
        text="To connect type in terminal 'connect({ip address of server})'\n\
Note: accelerate commands do not work in client mode")
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
                            font="Times 40 bold") 
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
    myAppClient(width=1920, height=1177, mvcCheck=False)
    
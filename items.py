from RGB import *
from shapes import *
from operations import *
from items import *

## moving item class as wrapper for acceleration, position, momentum, etc.
## basis of physics simulator
class MovingItem(object):
    def __init__(self, width, height, elasticity, mass, x=0, y=0, z=0):
        ## basic properties
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.mass = mass
        self.elasticity = elasticity
        self.isEnabled = True

    ## accelerate object (integral approx with timerDelay)
    def accelerate(self, ax, ay, az, timerDelay):
        self.vx += ax * timerDelay
        self.vy += ay * timerDelay
        self.vz += az * timerDelay

    ## manage friction force --> F_f = mu*F_N
    def friction(self, timerDelay, mu=0.5, g=9.8):
        dirX = -(self.vx+0.001)/abs(self.vx+0.001)
        dirZ = -(self.vz+0.001)/abs(self.vz+0.001)
        self.vx += g * mu * dirX * timerDelay if self.vx != 0 else 0
        self.vz += g * mu * dirZ * timerDelay if self.vz != 0 else 0

    ## update calculates new position, friction, and gravity
    def update(self, timerDelay):
        self.updatePos(timerDelay)
        self.friction(timerDelay)
        self.gravity(timerDelay)
    
    ## calculate gravity if v_y != 0 --> F_g = m*g
    def gravity(self, timerDelay):
        if self.getVelocity()[1] != 0:
            vx = self.getVelocity()[0]
            vy = self.getVelocity()[1]
            vz = self.getVelocity()[2]
            vy -= 9.8*timerDelay
            self.updateVelocity(vx, vy, vz)

    ## momentum calculator with other object
    def handleCollision(self, other):
        if isinstance(other, MovingItem) and self.isEnabled and other.isEnabled:
            m1, m2 = self.mass, other.mass
            vi1x,vi1y,vi1z = self.getVelocity()
            vi2x,vi2y,vi2z = other.getVelocity()
            
            ## elastic collission
            if self.elasticity == 1:
                vf1x = ((m1 - m2)*vi1x + 2*m2*vi2x)/(m1 + m2)
                vf2x = (2*m1*vi1x - (m1 - m2)*vi2x)/(m1 + m2)
                vf1y = ((m1 - m2)*vi1y + 2*m2*vi2y)/(m1 + m2)
                vf2y = (2*m1*vi1y - (m1 - m2)*vi2y)/(m1 + m2)
                vf1z = ((m1 - m2)*vi1z + 2*m2*vi2z)/(m1 + m2)
                vf2z = (2*m1*vi1z - (m1 - m2)*vi2z)/(m1 + m2)
            ## perfectly inelastic collission
            elif self.elasticity == 0:            
                vf1x = vf2x = (m1*vi1x+m2*vi2x)/(m1+m2)
                vf1y = vf2y = (m1*vi1y+m2*vi2y)/(m1+m2)
                vf1z = vf2z = (m1*vi1z+m2*vi2z)/(m1+m2)

            other.updateVelocity(vf2x, vf2y, vf2z)
            self.updateVelocity(vf1x, vf1y, vf1z)

## Robot is the user controlled moving item as a black cube
class Robot(Cube, MovingItem):
    def __init__(self, width, height, x=0, y=0, z=0, mass=40, color=None):
        Cube.__init__(self, width, x, y, z, color=color)
        MovingItem.__init__(self, width, height, 1, mass, x, y, z)

    ## integral approx. using velocity to update position
    def updatePos(self, timerDelay):
        if abs(self.vx) < 0.1:  self.vx = 0
        if abs(self.vy) < 0.1:  self.vy = 0
        if abs(self.vz) < 0.1:  self.vz = 0
        if (self.vx, self.vy, self.vz) == (0, 0, 0): return
        for point in self.points:
            point.translate((self.vx * timerDelay), 
                            (self.vy * timerDelay), 
                            (self.vz * timerDelay))

    ## update velocity linearly
    def updateVelocity(self, vx, vy, vz):
        self.vx = vx
        self.vy = vy
        self.vz = vz
    
    def getVelocity(self):
        return (self.vx, self.vy, self.vz)


## Ball (a mine) is a moving sphere
class Ball(Sphere, MovingItem):
    def __init__(self, r, x=0, y=0, z=0, mass=10):
        self.r = r
        Sphere.__init__(self, r, 0, 0, 0)
        MovingItem.__init__(self, 2*r, 2*r, 1, mass, x, y, z)
        for point in self.points:
            point.translate(x,y,z)
        self.omegaX, self.omegaY, self.omegaZ = 0, 0, 0

    ## use rotational physics for calculating position instead of linear physics
    ## also calculates angle of ball for rolling effect
    ## integral approximation
    def updatePos(self, timerDelay):
        if abs(self.omegaX) < 3:  self.omegaX = 0
        if abs(self.omegaY) < 3:  self.omegaY = 0
        if abs(self.omegaZ) < 3:  self.omegaZ = 0
        self.rotateMid(self.omegaX * timerDelay, 
                        self.omegaY * timerDelay, 
                        self.omegaZ * timerDelay)
        for point in self.points:
            point.translate((self.omegaX * timerDelay * self.r), 
                            (self.omegaY * timerDelay * self.r), 
                            (self.omegaZ * timerDelay * self.r))

    ## use rotational physics instead of linear physics to accelerate
    def accelerate(self, alphaX, alphaY, alphaZ, timerDelay):
        self.omegaX += alphaX * timerDelay
        self.omegaY += alphaY * timerDelay
        self.omegaZ += alphaZ * timerDelay

    ## use rotational physics instead of linear physics to slow down ball
    ## Note that friction torque is in same direction for ball, 
    ## but still slows down
    def friction(self, timerDelay, mu=0.1, g=9.8):
        dirX = -(self.omegaX+0.001)/abs(self.omegaX+0.001)
        dirY = -(self.omegaY+0.001)/abs(self.omegaY+0.001)
        dirZ = -(self.omegaZ+0.001)/abs(self.omegaZ+0.001)
        self.omegaX += g*mu*dirX * timerDelay if self.omegaX != 0 else 0
        self.omegaY += g*mu*dirY * timerDelay if self.omegaY != 0 else 0
        self.omegaZ += g*mu*dirZ * timerDelay if self.omegaZ != 0 else 0

    ## update angular velocity given linear velocity
    def updateVelocity(self, vx, vy, vz):
        self.omegaX = vx/self.r
        self.omegaY = vy/self.r
        self.omegaZ = vz/self.r
    
    def getVelocity(self):
        return (self.omegaX*self.r, self.omegaY*self.r, self.omegaZ*self.r)

## Box (a mine) is a moving cube (integral approximation)
class Box(Cube, MovingItem):
    def __init__(self, width, height, x=0, y=0, z=0, mass=10, color=None):
        if color == None:
            color = RGB(0,0,0)
        assert(width==height)
        Cube.__init__(self, width, x, y, z, color)
        MovingItem.__init__(self, width, height, 1, mass, x, y, z)

    ## update position linearly
    def updatePos(self, timerDelay):
        if abs(self.vx) < 3:  self.vx = 0
        if abs(self.vy) < 3:  self.vy = 0
        if abs(self.vz) < 3:  self.vz = 0
        for point in self.points:
            point.translate((self.vx * timerDelay), 
                            (self.vy * timerDelay), 
                            (self.vz * timerDelay))

    def updateVelocity(self, vx, vy, vz):
        self.vx = vx
        self.vy = vy
        self.vz = vz
    
    def getVelocity(self):
        return (self.vx, self.vy, self.vz)


## target is fixed and checks to see if it contains a wireframe
class Target(Cube):
    def __init__(self,x0,y0,z0,l):
        self.x0, self.y0, self.z0 = x0, y0, z0
        super().__init__(l, x0, y0, z0, color=RGB(255,255,255))
        self.contains = set()

    ## check if an object is within the target completely
    def __contains__(self, key):
        ## Vectors/Points can be contained
        if isinstance(key, PointR3):
            point = key
            ## must be fully in
            return (point.x >= self.x0 and point.x <= self.x0+self.L and
                point.y >= self.y0 and point.y <= self.y0+self.L and
                point.z >= self.z0 and point.z <= self.z0+self.L)
        ## Wireframe checks if all points are within the target
        elif isinstance(key, Wireframe):
            if isinstance(key, Ball):
                for point in key.skipR:
                    if not point in self:
                        return False
            else:
                for point in key.points:
                    if not point in self:
                        return False
            self.contains.add(key)
            key.isEnabled = False
            return True

    ## Draw a hollow box without faces; draw no. of contents in target
    def draw(self, canvas):
        for edge in self.edges:
            edge.draw(canvas, disabled=False)
        for point in self.points:
            point.draw(canvas, RGB(0,0,0), disabled=False)
        PointR3.create_text(canvas, self.midpoint(), str(len(self.contains)), 
            "red", "Times 28 bold")

## Wall is a fixed wireframe, essentially a 3d plane with thickness
## calculates position of points, edges, and planes
class Wall(RectangularPrism):
    def __init__(self, x0, y0, z0, x1, y1, z1, color=None, floor=False, 
                outer=False):
        self.floor = floor
        self.outer = outer
        if color == None:
            color = RGB(0,100,100)
        super().__init__(x0, y0, z0, x1, y1, z1, color=color)

    def __repr__(self):
        return \
    f"Wall({self.x0}, {self.y0}, {self.z0}, {self.x1}, {self.y1}, {self.z1})"

    ## check if another item is intercepting the wall
    def isIntercepting(self, other):
        return other in self

    ## overrides contains to first check if floor --> if so, condition is just
    ## y > 0
    def __contains__(self, other):
        if self.floor:
            for edge in other.edges:
                if edge.point1.y >= 0:
                    return True
            return False
        else:
            return super().__contains__(other)
    
    ## wall are fixed so momentum flips the object
    def handleCollision(self, other):
        vx, vy, vz = other.getVelocity()
        ## if floor, bounce up again with decay rate
        decay = 0.4
        if self.floor:
            other.updateVelocity(vx, -vy*decay, vz)
        ## if horizontal wall:
        elif abs(self.x1-self.x0) > abs(self.z1-self.z0):
            ## if left/right side, flip vx
            selfPtsX = [point.x for point in self.points]
            otherPtsX = [point.x for point in other.points]
            if ((min(otherPtsX) < min(selfPtsX) and 
                max(otherPtsX) > min(selfPtsX)) or \
               (min(otherPtsX) < max(selfPtsX) and 
                max(otherPtsX) > max(selfPtsX)) or \
               (max(otherPtsX) < min(selfPtsX) and 
                min(otherPtsX) > max(selfPtsX))):
                other.updateVelocity(-vx, vy, vz)
            ## if front/back side, flip vz
            else:
                other.updateVelocity(vx, vy, -vz)
        ## if vertical wall:
        else:
            selfPtsZ = [point.z for point in self.points]
            otherPtsZ = [point.z for point in other.points]
            ## if left/right side, flip vz
            if ((min(otherPtsZ) < min(selfPtsZ) and 
                max(otherPtsZ) > min(selfPtsZ)) or \
               (min(otherPtsZ) < max(selfPtsZ) and 
                max(otherPtsZ) > max(selfPtsZ)) or \
               (max(otherPtsZ) < min(selfPtsZ) and 
                min(otherPtsZ) > max(selfPtsZ))):
                other.updateVelocity(vx, vy, -vz)
            ## if front/back side, flip vx
            else:
                other.updateVelocity(-vx, vy, vz)

    ## less than for sorting printing order; floor is always printed last
    def __lt__(self, other):
        if self.floor:
            return True
        return super().__lt__(other)

    ## find midpoint --> irrelevant if is floor
    def midpoint(self):
        return PointR3(-999, -999, -999) if self.floor else super().midpoint()

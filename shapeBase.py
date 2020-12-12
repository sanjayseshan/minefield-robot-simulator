"""
Defines basic properties needed to make a shape:
Vector --> PointR3, PointR2 --> forms verticies of shape
Edge (of a shape)
Plane --> pseudo bouned plane that forms a face of a shape
"""
from operations import Matrix
from RGB import *

## Basic Vector class with standard operations for vectors
class Vector(object):
    def __init__(self, vector):
        self.vector = vector

    def asMatrix(self):
        return Matrix([[self.vector[i]] for i in range(len(self.vector))])

    def __repr__(self):
        return str(self.vector)

    ## various properties of vectors implemented
    ## magnitude/square magnitude
    def magnitude(self):
        return sum([i**2 for i in self.vector])**0.5  

    def squareMagnitude(self):
        return sum([i**2 for i in self.vector])  

    ## vectors can be equal
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.vector == other.vector 
        else:
            return self.vector == other

    ## subtract/add by component
    def __sub__(self, other):
        new = []
        for i in range(len(self.vector)):
            new.append(self.vector[i]-other.vector[i])
        if len(new) == 3:
            return PointR3(new[0], new[1], new[2])
        return Vector(tuple(new))

    def __add__(self, other):
        new = []
        for i in range(len(self.vector)):
            new.append(self.vector[i]+other.vector[i])
        if len(new) == 3:
            return PointR3(new[0], new[1], new[2])
        return Vector(tuple(new))

    ## divide and multiply by scalars per component
    def __truediv__(self, other):
        new = []
        for x in self.vector: 
            new.append(x/other)
        return Vector(tuple(new))

    def __rtruediv__(self, other):
        new = []
        for x in self.vector: 
            new.append(other/x)
        return Vector(tuple(new))


    def __mul__(self, other):
        new = []
        for x in self.vector: 
            new.append(x*other)
        return Vector(tuple(new))

    def __rmul__(self, other):
        new = []
        for x in self.vector: 
            new.append(other*x)
        return Vector(tuple(new))

## Point in R3/3D is a type of vector
## can also be rotated and translated
## can be projected to R2 space
class PointR3(Vector):
    R3R2 = {}

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        super().__init__((x,y,z))

    def __repr__(self):
        return f"R3({self.x},{self.y},{self.z})"

    def getPoint(self):
        return self.x, self.y, self.z

    ## in R3, make add/sub more efficient as there is a known length
    def __sub__(self, other):
        return PointR3(self.x-other.x, self.y-other.y, self.z-other.z)

    def __add__(self, other):
        return PointR3(self.x+other.x, self.y+other.y, self.z+other.z)

    ## can translate points
    def translate(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz
        self.vector = self.x, self.y, self.z
    
    ## can rotate points by using the matrix class's rotation matricies
    def rotateX(self, angle):
        new = self.asMatrix()
        new.rotateX(angle)
        out = new.asVector()
        self.x, self.y, self.z = out.x, out.y, out.z
        self.vector = self.x, self.y, self.z
        return self

    def rotateY(self, angle):
        new = self.asMatrix()
        new.rotateY(angle)
        out = new.asVector()
        self.x, self.y, self.z = out.x, out.y, out.z
        self.vector = self.x, self.y, self.z
        return self

    def rotateZ(self, angle):
        new = self.asMatrix()
        new.rotateZ(angle)
        out = new.asVector()
        self.x, self.y, self.z = out.x, out.y, out.z
        self.vector = self.x, self.y, self.z
        return self

    ## project to R2 using matrix projection
    ## also caches projection to speed up repeated calculations
    def toR2(self):
        if (self.x, self.y, self.z) in PointR3.R3R2:
            return PointR3.R3R2[(self.x, self.y, self.z)]
        else:
            point, z = Matrix.projectR3R2(self.asMatrix())
            point = point.asVector()
            PointR3.R3R2[(self.x, self.y, self.z)] = point, z
            return point, z
    
    ## draws a point on the screen assuming the point is in front of the camera
    ## i.e. z < 0
    def draw(self, canvas, color, size=1, disabled=True):
        if not disabled:
            point, z = self.toR2()
            x, y = point.getPoint()
            if z > 0:
                return
            canvas.create_oval(x-size,y-size,x+size,y+size, 
                fill=color.getRawColor(), width=0)

    ## draw text at an anchored point in R3 --> project to R2
    @staticmethod
    def create_text(canvas, point, text, fill, font):
        if point.toR2()[1] > 0:
            return
        x0,y0 = point.toR2()[0].getPoint()
        canvas.create_text(x0, y0, text=text, fill=fill, font=font)

## Point in R2 class --> subclass of a vector
class PointR2(Vector):
    ## holds x,y coords
    def __init__(self, x, y):
        self.x, self.y = x, y
        super().__init__((x,y))
    
    def getPoint(self):
        return self.x, self.y

    def __repr__(self):
        return f"R2({self.x},{self.y})"

    ## draw on screen
    def draw(self, canvas, color, size=1):
        x, y = self.x, self.y
        canvas.create_oval(x-size,y-size,x+size,y+size, 
            fill=color.getRawColor(), width=0)

    ## adding and subtracting made more efficient as know length
    def __sub__(self, other):
        return PointR3(self.x-other.x, self.y-other.y)

    def __add__(self, other):
        return PointR3(self.x+other.x, self.y+other.y)

## Define a edge as two points that form an edge
class Edge(object):
    def __init__(self,point1, point2):
        self.point1, self.point2 = point1, point2
    
    ## converts an edge that might be partly off screen to fit on screen
    def edgeToScreen(self):
        pt1, pt1z = self.point1.toR2()
        pt2, pt2z = self.point2.toR2()
        ## check if off screen
        ## if both points in edge are off screen, skip
        if pt1z > -10 and pt2z > -10:
            return (None, None)
        ## if just one point is off screen, adjuse that position linearly to 
        ## fit to the edge of the screen
        elif pt1z > -10:
            ratio = (-pt2z-10)/(pt1z-pt2z)
            tmp = (self.point1 - self.point2) * ratio + self.point2
            return tmp.toR2()[0], self.point2.toR2()[0]
        elif pt2z > -10:
            ratio = (-pt1z-10)/(pt2z-pt1z)
            tmp = (self.point2 - self.point1) * ratio + self.point1
            return self.point1.toR2()[0], tmp.toR2()[0]
        ## if both are on screen, return the normal projection
        else:
            return self.point1.toR2()[0], self.point2.toR2()[0]

    ## draw a line between the projected points from edgeToScreen()
    def draw(self, canvas, color=None, disabled=True):
        if not disabled:
            if color == None:
                color = RGB(0,0,0)
            point = self.edgeToScreen()
            if point != (None, None):
                canvas.create_line(point[0].x, point[0].y, point[1].x, point[1].y, 
                    width=3, fill=color.getRawColor())

    def __repr__(self):
        return f"Edge({self.point1}, {self.point2})"

    ## find the intersection between two edges
    def findIntersection(self, other):
        if isinstance(other, Edge):
            ## get coordinates and dir/slope vector of each edge
            selfDir = self.point1 - self.point2
            dx1, dy1, dz1 = selfDir.getPoint()
            sx1 = self.point1.x
            sz1 = self.point1.z
            otherDir = other.point1 - other.point2
            dx2, dy2, dz2 = otherDir.getPoint()
            sx2 = other.point1.x
            sz2 = other.point1.z
            ## solve parametric line equation using the simplified version of
            """
            Ax=b
            A = [[dx1 -dx2]  
                 dz1 -dz2]
            x = [[t1], 
                 [t2]]
            b = [[sx2-sx1],
                 [sz2-sz1]]
            """
            try:
                t1 = ((sx2-sx1)*dz2-(sz2-sz1)*dx2)/(dx1*dz2-dz1*dx2)
            except Exception as e: ## edges are parallel
                return None 
            x1 = sx1 + dx1 * t1
            y1 = 0
            z1 = sz1 + dz1 * t1

            ## check if intersection is within the bounds of the edges
            if (int(x1) >= int(min([self.point1.x, self.point2.x])) and
                int(z1) >= int(min([self.point1.z, self.point2.z])) and
                int(x1) >= int(min([other.point1.x, other.point2.x])) and
                int(z1) >= int(min([other.point1.z, other.point2.z])) and
                int(x1) <= int(max([self.point1.x, self.point2.x])) and
                int(z1) <= int(max([self.point1.z, self.point2.z])) and
                int(x1) <= int(max([other.point1.x, other.point2.x])) and
                int(z1) <= int(max([other.point1.z, other.point2.z]))):
                return PointR3(x1,y1,z1)
            return None

    ## implements contains to check if intersection exists
    def __contains__(self, other):
        return self.findIntersection(other) != None        

## Plane defined by two or more edges (generally 4)
## 
class Plane(object):
    drawPlanes = True
    def __init__(self, edges, color=None):
        if color == None:
            color = RGB(0,0,0).getRandColor()
        self.edges = edges
        self.color = color.getRandColor()
    
    ## create a list of 2d points from each edge
    def getPointList(self):
        L = []
        ## convert the edges to 2d points that fit on screen
        point1, point2 = self.edges[0].edgeToScreen()
        if point1 != None:
            L.append(point1.x)
            L.append(point1.y)
            L.append(point2.x)
            L.append(point2.y)
        point1, point2 = self.edges[3].edgeToScreen()
        if point1 != None:
            L.append(point1.x)
            L.append(point1.y)
            L.append(point2.x)
            L.append(point2.y)
        point1, point2 = self.edges[1].edgeToScreen()
        if point1 != None:
            L.append(point2.x)
            L.append(point2.y)
            L.append(point1.x)
            L.append(point1.y)
        point1, point2 = self.edges[2].edgeToScreen()
        if point1 != None:
            L.append(point2.x)
            L.append(point2.y)        
            L.append(point1.x)
            L.append(point1.y)
        return L

    ## draw the plane on screen using the point list
    def draw(self, canvas):
        if not Plane.drawPlanes:
            return
        points = self.getPointList()
        if points != []:
            canvas.create_polygon(points, fill=self.color)

## Define a wireframe (object) as having color, points, edges, and planes (faces)
class Wireframe(object):
    def __init__(self, color=None):
        ## define basic properties
        if color == None:
            color = RGB(0,0,0)
        self.color = color 
        self.points = []
        self.drawPoints = []
        self.edges = [] 
        self.planes = []
        self.skipR = [] ## special for spheres to not translate certain points

    ## add point to list on type R3, add to skipR if specified
    def addPoint(self, point, ptype="normal"):
        if type(point) == PointR3:
            if ptype == "skipR":
                self.skipR.append(point)
            self.points.append(point)

    ## add edge to list
    def addEdge(self, edge):
        if type(edge) == Edge:
            self.edges.append(edge)

    ## add plane/face to list
    def addPlane(self, plane):
        if type(plane) == Plane:
            self.planes.append(plane)

    ## midpoint is the average position of all the points
    def midpoint(self):
        mX = sum([point.x for point in self.points]) / len(self.points)
        mY = sum([point.y for point in self.points]) / len(self.points)
        mZ = sum([point.z for point in self.points]) / len(self.points)
        return PointR3(mX, mY, mZ)

    ## Check if there is an intersection with another wireframe object
    def __contains__(self, other):
        ## if distance >30m, not going to intercept, unless it is a line
        ## or a wall
        if ((self.midpoint() - other.midpoint()).magnitude() > 30 and 
            not "Wall" in str(type(self)) and not "Line" in str(type(other))
            and not "Line" in str(type(self))):
            return False      
        ## check all edges until an intersection is found (or not)
        for edge1 in self.edges:
            if (edge1.point1.y == 0 or edge1.point2.y == 0):
                for edge2 in other.edges:
                    if (edge2.point1.y == 0 or edge2.point2.y == 0):
                        if edge1.__contains__(edge2):
                            return True
        return False

    ## less than function to sort wireframes in proper drawing order
    def __lt__(self, other):
        otherPoints = []
        ## the floor always comes last
        if "Wall" in str(type(other)):
            if other.floor:
                return False
        c = Matrix.c
        ## for every point in self and other, create a line that extends to the
        ## camera --> check for intersection with the other and self objects
        ## determines rank (False = > and True = <) 
        for point in other.points+[other.midpoint()]:
            if point.y == 0:
                line = Line(c.asVector().x, 0, c.asVector().z, point.x, 0, 
                            point.z) 
                if line in self:
                    return False
        for point in self.points+[self.midpoint()]:
            if point.y == 0:
                line = Line(c.asVector().x, 0, c.asVector().z, point.x, 0, 
                            point.z) 
                if line in other:
                    return True

        ## if not intersection was found, rank by magnitude of distance to 
        ## camera from each point in self and other
        myPoints = []
        for point in self.points+[self.midpoint()]:
            c = Matrix.c
            d = (point.asMatrix() - c)
            a = d.asVector().squareMagnitude()
            myPoints.append(a)  
        otherPoints = []
        for point in other.points+[other.midpoint()]:
            c = Matrix.c
            d = (point.asMatrix() - c)
            a = d.asVector().squareMagnitude()
            otherPoints.append(a)  
        ## rank by smallest magnitudes
        if max(myPoints)<max(otherPoints):
            return False
        return True

    ## convert points to matrix
    def asMatrix(self):
        matrix = []
        for point in self.points:
            x,y,z = point.getPoint()
            matrix.append([x,y,z])
        return matrix

    ## Rotate a wireframe --> rotate all points
    def rotateX(self, angle):
        for point in self.points:
            if point not in self.skipR: ## skips if special point in sphere
                point.rotateX(angle)

    def rotateY(self, angle):
        for point in self.points:
            if point not in self.skipR:
                point.rotateY(angle)

    def rotateZ(self, angle):
        for point in self.points:
            if point not in self.skipR:
                point.rotateZ(angle)

    ## rotate object around midpoint
    def rotateMid(self, angleX, angleY, angleZ):
        ## find midpoint
        mX, mY, mZ = self.midpoint().getPoint()
        ## move to center
        for point in self.points:
            point.translate(-mX, -mY, -mZ)
        ## rotate object
        self.rotateX(angleX)
        self.rotateY(angleY)
        self.rotateZ(angleZ)
        ## return to orig position
        for point in self.points:
            point.translate(mX, mY, mZ)

    ## draw all parts of object
    def draw(self, canvas):
        for plane in self.planes:
            plane.draw(canvas)
        for edge in self.edges:
            edge.draw(canvas)
        for point in self.points:
            point.draw(canvas, RGB(0,0,0))

## Line class as two points and one edge
class Line(Wireframe):
    def __init__(self, x0, y0, z0, x1, y1, z1):
        super().__init__()
        point1 = PointR3(x0,y0,z0)
        super().addPoint(point1)
        point2 = PointR3(x1,y1,z1)
        super().addPoint(point2)
        self.addEdge(Edge(point1, point2))

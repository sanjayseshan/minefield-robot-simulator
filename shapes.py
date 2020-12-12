"""
Program that defines the basic shapes:
RectangularPrism
Cube
Sphere
"""

from RGB import *
from operations import *
from shapeBase import *

## define a rectangular prism's points, edges, and faces (planes)
## extends Wireframe
class RectangularPrism(Wireframe):
    def __init__(self, x0, y0, z0, x1, y1, z1, color=None):
        if color == None:
            color = RGB(0,100,100)
        super().__init__(color)
        self.x0, self.y0, self.z0, self.x1, self.y1, self.z1 = \
            x0, y0, z0, x1, y1, z1
        self.color = color
        ## define points
        for x in (x0,x1):
            for y in (y0,y1):
                for z in (z0,z1):
                    point = PointR3(x,y,z)
                    super().addPoint(point)
        ## define edges
        edges = [None] * 12
        edges[0] = Edge(self.points[0], self.points[1])
        edges[1] = Edge(self.points[0], self.points[2])
        edges[2] = Edge(self.points[0], self.points[4])
        edges[3] = Edge(self.points[1], self.points[3])
        edges[4] = Edge(self.points[1], self.points[5])
        edges[5] = Edge(self.points[2], self.points[3])
        edges[6] = Edge(self.points[2], self.points[6])
        edges[7] = Edge(self.points[3], self.points[7])
        edges[8] = Edge(self.points[4], self.points[5])
        edges[9] = Edge(self.points[4], self.points[6])
        edges[10] = Edge(self.points[5], self.points[7])
        edges[11] = Edge(self.points[6], self.points[7])
        for edge in edges: self.addEdge(edge)
        ## define faces
        faces = [None] * 6
        faces[0] = Plane([edges[0], edges[5], edges[1], edges[3]], color)
        faces[1] = Plane([edges[4], edges[7], edges[3], edges[10]], color)
        faces[2] = Plane([edges[2], edges[6], edges[1], edges[9]], color)
        faces[3] = Plane([edges[8], edges[11], edges[9], edges[10]], color)
        faces[4] = Plane([edges[6], edges[7], edges[5], edges[11]], color)
        faces[5] = Plane([edges[2], edges[4], edges[0], edges[8]], color)
        for face in faces: self.addPlane(face)

## Define Cube's as an extension of a RectangularPrism
class Cube(RectangularPrism):
    def __init__(self, l, x0, y0, z0, color=None):
        if color == None:
            color = RGB(20,20,20)
        self.L = l
        ## pass cube into super() with appropriate coordinates
        x1 = x0 + l
        y1 = y0 + l
        z1 = z0 + l
        super().__init__(x0, y0, z0, x1, y1, z1, color=color)

## define sphere's points and edges within wireframe.
class Sphere(Wireframe):
    def __init__(self, r, x0, y0, z0):
        super().__init__()
        ## calculate position of each point in a sphere using
        ## r^2 = x^2 + y^2 + z^2 --> iterate across x then y to get +/- z
        for x in range(x0-r,x0+r+1,1):
            yR = int(math.sqrt(r**2-x**2))
            for y in range(y0-yR,y0+yR+1,1):
                z = (math.sqrt(r**2-x**2-y**2))
                point = PointR3(x,y,z0+z)
                super().addPoint(point)
                point = PointR3(x,y,z0-z)
                super().addPoint(point)
        
        ## simplify calculations by approximating the sphere as points within
        ## a cube
        l = 2*r
        pts = []
        y0-=r
        x0-=r
        z0-=r
        ## add in cube's points that should not rotate (skipR)
        for x in (x0,x0+l):
            for y in (y0,y0+l):
                for z in (z0,z0+l):
                    point = PointR3(x,y,z)
                    pts.append(point)
                    super().addPoint(point, ptype="skipR")
        ## add in edges
        for i in range(len(pts)):
            pointI = pts[i]
            for pointF in pts[i:]:
                if (Vector(tuple(np.array(pointI.getPoint()) -
                        np.array(pointF.getPoint()))).magnitude() <= l ):
                    super().addEdge(Edge(pointI, pointF))

    ## draw sphere using different color per index to show spherical 
    ## shape better 
    def draw(self, canvas):
        ct = 0
        for point in self.points[:-8]:
            ct+=1
            color = RGB(ct, 255-ct, ct//2)
            point.draw(canvas, color, size=15, disabled=False)



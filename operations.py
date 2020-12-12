"""
Contains the basic classes for operations:
Matrix
"""
import math
import numpy as np

## Matrix class that uses numpy arrays and custom wrappers for point projections
class Matrix(object):
    ## projection variables
    ## c = camera
    ## e = distance to plane
    ## theta = perspective andle
    c = None
    e = (1000,600,500)
    theta = (-math.pi/10,0,0)
    
    def __init__(self, L):
        self.matrix = np.array(L)

    ## wrappers for various numpy operations (adding, multiplying, etc.) to 
    ## return Matrix object
    def __mul__(self, other):
        return Matrix(np.dot(self.matrix, other.matrix).tolist())

    def __add__(self, other):
        return Matrix((self.matrix+other.matrix).tolist())

    def __sub__(self, other):
        return Matrix((self.matrix-other.matrix).tolist())

    ## rotate a matrix in each direction
    def rotateX(self, angle):
        self.matrix = np.dot(Matrix.rotateXMatrix(angle).matrix,self.matrix) 

    def rotateY(self, angle):
        self.matrix = np.dot(Matrix.rotateYMatrix(angle).matrix,self.matrix) 

    def rotateZ(self, angle):
        self.matrix = np.dot(Matrix.rotateZMatrix(angle).matrix,self.matrix) 

    ## return a column matrix as a vector (or as a point if length is 2 or 3)
    def asVector(self):
        matrix = self.matrix.tolist()
        if len(matrix) == 3 and len(matrix[0]) == 1:
            return PointR3(matrix[0][0],matrix[1][0],matrix[2][0])
        elif len(matrix) == 2 and len(matrix[0]) == 1:
            return PointR2(matrix[0][0],matrix[1][0])
        elif len(matrix[0]) == 1:
            L = []
            for entry in self.matrix.tolist():
                L.append(entry[0])
            return Vector(tuple(L))

    ## pretty print
    def __repr__(self):
        return "Matrix("+str(self.matrix.tolist())+")"

    ## project a R3 vector to R2 --> 3D to 2D
    ## works largely only for points in front of screen
    ## following derived from 
    ## https://en.wikipedia.org/wiki/3D_projection##Mathematical_formula
    @staticmethod
    def projectR3R2(matrix):
        c = Matrix.c
        e = Matrix.e
        ## calculate projection matricies
        ProjM = (Matrix.rotateXMatrix(Matrix.theta[0])*
                        Matrix.rotateYMatrix(Matrix.theta[1])*
                        Matrix.rotateZMatrix(Matrix.theta[2]))
        projE = Matrix([[1,0,e[0]/e[2]],
                            [0,1,e[1]/e[2]],
                            [0,0,1/e[2]   ]])
        ## find 2d vector and return it; also return relative depth to camera
        d = ProjM * (matrix - c)
        f = projE * d
        pt = f.asVector().getPoint()
        bx,by = (pt[0]/pt[2], pt[1]/pt[2])
        return Matrix([[bx],[by]]), d.asVector().z

    ## define standard rotation matricies
    @staticmethod
    def rotateXMatrix(angle):    
        c = math.cos(angle)
        s = math.sin(angle)
        return Matrix([[1, 0, 0],
                        [0,  c, s],
                        [0, -s, c]])
    @staticmethod
    def rotateYMatrix(angle):    
        c = math.cos(angle)
        s = math.sin(angle)
        return Matrix([[ c, 0, -s],
                        [0,  1, 0],
                        [s,  0, c]])
    @staticmethod
    def rotateZMatrix(angle):    
        c = math.cos(angle)
        s = math.sin(angle)
        return Matrix([[c, s, 0],
                       [-s, c, 0],
                       [0, 0, 1]])

## set dependencies, including camera position
Matrix.c = Matrix([[0],[100],[200]])
from shapeBase import *

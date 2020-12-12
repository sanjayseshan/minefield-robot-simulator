"""
Program that handles RGB colors
"""

import random

## class to define a color as RGB and pull slightly different colors for each
## plane on an object to make it seem more 3D
class RGB(object):
    def __init__(self, r, g, b):
        ## RGB components
        self.r = r
        self.g = g
        self.b = b

    ## return color as is
    def getRawColor(self):
        return RGB.rgbString(self.r, self.g, self.b)

    ## get totally random color
    @staticmethod
    def getRandom():
        return RGB(random.randint(0,255), random.randint(0,255), 
                    random.randint(0,255))

    ## get slightly different color that is 0->(+/-)5/255 RGB different than 
    ## orig, so planes look more 3D
    def getRandColor(self):
        dc = 5
        val = RGB.rgbString(self.r+random.randint(-dc,dc), 
                self.g+random.randint(-dc,dc), 
                self.b+random.randint(-dc,dc))
        while (val == None):
            val = RGB.rgbString(self.r+random.randint(-dc,dc), 
                    self.g+random.randint(-dc,dc), 
                    self.b+random.randint(-dc,dc))
        return val       

    ## convert RGB to hex string
    ## from https://www.cs.cmu.edu/~112/notes/notes-graphics.html
    @staticmethod
    def rgbString(r, g, b):
        if r<0 or r>255 or g<0 or g>255 or b<0 or b>255: return None
        return f'#{r:02x}{g:02x}{b:02x}'
import pyglet
from math import cos, sin, sqrt, acos, asin, atan
#this should be a wrapper so I canhave multiple different types of orbits that take the same input
#but have a different output

class Control:
    keyDown = False
    mouseDown = False
    camera = None
    debug = False
    def __init__(self, window, camera):
        window.on_key_press = self.key_press
        window.on_key_release = self.key_release
        window.on_mouse_motion = self.mouse_motion
        window.on_mouse_drag = self.mouse_drag
        window.on_mouse_press = self.mouse_press
        window.on_mouse_release = self.mouse_release
        window.on_mouse_scroll = self.mouse_scroll
        self.camera = camera
        self.setup()

    def setup(self):
        pass

    def update(self, vector):
        pass

    def key_press(self, symbol, modifier):
        if self.debug:
            print("key press: "+ str(symbol))
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
    
    def key_release(self, symbol, modifier):
        if self.debug:
            print("key release: "+ str(symbol))

    def mouse_motion(self, x, y, dx, dy):
        if self.debug:
            print("mouse motion at. x: "+ str(x)+" y: "+str(y))

    def mouse_press(self, x, y, button, modifier):
        if self.debug:
            print("mouse press: "+ str(button))

    def mouse_release(self, x, y, button, modifier):
        if self.debug:
            print("mouse release: "+ str(button))

    def mouse_drag(self, x, y, dx, dy, button, modifier):
        if self.debug:
            print("mouse drag at. x: "+ str(x)+" y: "+str(y))

    def mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.debug:
            print("mouse scroll at. x: "+ str(x)+" y: "+str(y))


class Orbit(Control):
    def setup(self):
        self.lookfrom = self.camera.lookfrom
        self.zoom = mag(self.lookfrom)
        self.thetax = atan(self.lookfrom[0]/self.lookfrom[2])
        dist = mag([self.lookfrom[0], 0, self.lookfrom[2]])
        self.thetay = atan(self.lookfrom[1]/dist)
        #calculate thetax and theta y

    def update(self):
        rval = self.mouseDown
        self.mouseDown = False
        tempx = [sin(self.thetax), 0.0, cos(self.thetax)]
        tempy = [0.0, sin(self.thetay), 0.0]
        tempx = normalize(tempx)
        mag = cos(self.thetay)
        mag = [mag, mag, mag]
        tempx = mul(tempx, mag)
        self.lookfrom = mul(normalize(add(tempx, tempy)), [self.zoom, self.zoom, self.zoom])
        #global camera
        self.camera.lookfrom = self.lookfrom
        self.camera.update_view()
        return rval

    def mouse_drag(self, x, y, dx, dy, button, modifier):
        super(Orbit, self).mouse_drag(x, y, dx, dy, button, modifier)
        self.thetax -= dx*0.01
        self.thetay -= dy*0.01
        self.mouseDown = True
        #calculate position on floor circle
        #then calculate elevation
            #elevation x will dictate the length of floor x
        #use basic vector manipulation for this

    def mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.zoom += scroll_y
        self.mouseDown = True

def mag(a):
    return sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])

def minus(a, b):
    return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]

def add(a, b):
    return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]

def mul(a, b):
    return [a[0]*b[0], a[1]*b[1], a[2]*b[2]]

def div(a, b):
    return [a[0]/b[0], a[1]/b[1], a[2]/b[2]]

def normalize(a):
    size = mag(a)
    return [a[0]/size, a[1]/size, a[2]/size]

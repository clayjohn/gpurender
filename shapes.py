import pyglet
import ctypes
from material import *

class Hitable_list:
    hitables = []
    def update(self, pn):
        #pass all objects to the shader
        for i in range(len(self.hitables)):
            self.hitables[i].update(i, pn)
            pyglet.gl.glUniform1i(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer("NUM_OBJECTS".encode('ascii'))), int(len(self.hitables)))

    def add(self, shape):
        self.hitables.append(shape)


class Hitable:
    position = []
    size = 0
    rotation = []
    shape = 0
    material = None
    def __init__(self, *args):
        #for now take three arrays for args
        if len(args) >= 1:
            self.position = args[0]
        else:
            print("not enough arguments supplied to Hitable")
        if len(args) >=2:
            self.size = args[1]
        else:
            self.size = 0.5
        if len(args) >= 3:
            self.rotation = args[2]
        else:
            self.rotation = [0.0, 1.0, 0.0]
        if len(args) >= 4:
            self.material = args[3]
        else:
            self.material = Lambertian((1.0, 0.5, 0.5))

    def get_locations(self, i, pn):
        pass

    def update(self, i, pn):
        ##update position
        name = "hitables["+str(i)+"].pos"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.position[0], self.position[1], self.position[2])
        #update size
        name = "hitables["+str(i)+"].size"
        pyglet.gl.glUniform1f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.size)
        ##update rotation
        name = "hitables["+str(i)+"].dir"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.rotation[0], self.rotation[1], self.rotation[2])
        ##update type
        name = "hitables["+str(i)+"].type"
        pyglet.gl.glUniform1i(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), int(self.shape))
        self.material.update(i, pn)

class Sphere(Hitable):
    def __init__(self, *args):
        super(Sphere, self).__init__(*args)
        self.shape = 1


class Cube(Hitable):
    def __init__(self, *args):
        super(Cube, self).__init__(*args)
        self.shape = 2


class Plane(Hitable):
    def __init__(self, *args):
        super(Plane, self).__init__(*args)
        self.shape = 3


class Triangle(Hitable):
    def __init__(self, *args):
        super(Triangle, self).__init__(*args)
        self.shape = 4

class Disk(Hitable):
    def __init__(self, *args):
        super(Disk, self).__init__(*args)
        self.shape = 5

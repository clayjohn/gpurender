import pyglet
from pyglet import gl
import ctypes


class Material:
    albedo = []
    specular = []
    emitted = []
    reflectivity = 0.0 #same as fuzz
    mat = 0

    def __init__(self, *args):
        if len(args) >= 1:
            self.albedo = args[0]
        else:
            self.albedo = [1.0, 0.5, 0.5]
        if len(args) >=2:
            self.specular = args[1]
        else:
            self.specular = [1.0, 1.0, 1.0]
        if len(args) >= 3:
            self.emitted = args[2]
        else:
            self.emitted = [0.0, 0.0, 0.0]
        if len(args) >= 4:
            self.reflectivity = args[3]
        else:
            self.reflectivity = 0.0


    def update(self, i, pn):
        ##update diffuse color
        name = "materials["+str(i)+"].albedo"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.albedo[0], self.albedo[1], self.albedo[2])
        #update specular color
        name = "materials["+str(i)+"].specular"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.specular[0], self.specular[1], self.specular[2])
        ##update emission color
        name = "materials["+str(i)+"].emitted"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.emitted[0], self.emitted[1], self.emitted[2])
        ##update fuzz
        name = "materials["+str(i)+"].fuzz"
        pyglet.gl.glUniform1f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.reflectivity)
        ##update type
        name = "materials["+str(i)+"].type"
        pyglet.gl.glUniform1i(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), int(self.mat))


class Lambertian(Material):
    def __init__(self, color):
        super(Lambertian, self).__init__(color)
        self.mat = 1


class Metal(Material):
    def __init__(self, color, fuzz):
        super(Metal, self).__init__(color, (1, 1, 1), (0, 0, 0), fuzz)
        self.mat = 2


class Dialectric(Material):
    def __init__(self, ref):
        super(Dialectric, self).__init__((0, 0, 0), (0, 0, 0), (0, 0, 0), ref)
        self.mat = 3

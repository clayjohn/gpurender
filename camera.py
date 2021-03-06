from math import pi, tan, sqrt
import pyglet
import ctypes

class Camera:
    origin = [0, 0, 0]
    lower_left_corner = [-2, -1, -1]
    horizontal = [4, 0, 0]
    vertical = [0, 2, 0]
    w = []
    u = []
    v = []
    radius = 1.0

    lookfrom = None
    lookat = None
    vup = None
    vfov = None
    aspect = None
    aperture = None
    focus_dist = None

    def __init__(self, lookfrom, lookat, vup, vfov, aspect, aperture, focus_dist):
        self.lookfrom = lookfrom
        self.lookat = lookat
        self.vup = vup
        self.vfov = vfov
        self.aspect = aspect
        self.aperture = aperture
        self.focus_dist = focus_dist
        self.update_view()

    def update_view(self):
        self.radius = self.aperture / 2
        theta = self.vfov
        half_height = tan(theta/2)
        half_width = half_height * self.aspect
        self.origin = self.lookfrom
        w = unit_vector([self.lookfrom[0]-self.lookat[0], self.lookfrom[1]-self.lookat[1], self.lookfrom[2]-self.lookat[2]])
        u = unit_vector(cross(self.vup, w))
        v = cross(w, u)
        self.lower_left_corner = [self.origin[0]-half_width*self.focus_dist*u[0]-half_height*self.focus_dist*v[0]-self.focus_dist*w[0],
                                  self.origin[1]-half_width*self.focus_dist*u[1]-half_height*self.focus_dist*v[1]-self.focus_dist*w[1],
                                  self.origin[2]-half_width*self.focus_dist*u[2]-half_height*self.focus_dist*v[2]-self.focus_dist*w[2]]
        self.horizontal = [2*half_width*self.focus_dist*u[0], 2*half_width*self.focus_dist*u[1], 2*half_width*self.focus_dist*u[2]]
        self.vertical = [2*half_height*self.focus_dist*v[0], 2*half_height*self.focus_dist*v[1], 2*half_height*self.focus_dist*v[2]]
        self.w = w
        self.u = u
        self.v = v

    def update(self, pn):
        #update origin
        name = "camera.origin"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.origin[0], self.origin[1], self.origin[2])
        ##update lower_left_corner 
        name = "camera.corner"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.lower_left_corner[0], self.lower_left_corner[1], self.lower_left_corner[2])
        ##update horizontal
        name = "camera.width"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.horizontal[0], self.horizontal[1], self.horizontal[2])
        ##update vertical
        name = "camera.height"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.vertical[0], self.vertical[1], self.vertical[2])
        #update w
        name = "camera.w"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.w[0], self.w[1], self.w[2])
        #update u
        name = "camera.u"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.u[0], self.u[1], self.u[2])
        #update v
        name = "camera.v"
        pyglet.gl.glUniform3f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.v[0], self.v[1], self.v[2])
        #update lens_radius
        name = "camera.lens_radius"
        pyglet.gl.glUniform1f(pyglet.gl.glGetUniformLocation(pn, ctypes.create_string_buffer(name.encode('ascii'))), self.radius)
                     
def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c

def unit_vector(x):
    l = sqrt(x[0]*x[0]+x[1]*x[1]+x[2]*x[2])
    return [x[0]/l, x[1]/l, x[2]/l]

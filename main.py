import pyglet
from pyglet import gl
import ctypes
import math
from time import time
from glhelper import *
from shapes import *
from material import *
from camera import *
from math import pi, cos, sqrt
from random import random

WIDTH = 800
HEIGHT = 400

FB_WIDTH = 800# WIDTH
FB_HEIGHT = 400# HEIGHT


render_program = None
copy_program = None
framebuffer = None
window = None
world = Hitable_list()
camera = None

passes = 0
start_time = time()
fps_display = pyglet.clock.ClockDisplay()


def random_scene():
    global world
    n = 256
    world.add(Sphere((0, -1000, 0), 1000, [0, 0, 0], Lambertian((0.5, 0.5, 0.5))))
    for i in range(-8, 8, 2):
        for j in range(-8, 8, 2):
            choose_mat = random()
            center = [i+0.9*random(), 0.2, j*0.9*random()]
            d = [center[0]-4, center[1]-0.2, center[2]]
            if sqrt(d[0]*d[0]+d[1]*d[1]+d[2]*d[2])>0.9:
                if choose_mat<0.8:
                    mat = Lambertian([random()*random(), random()*random(), random()*random()])
                elif choose_mat<0.95:
                    mat = Metal([0.5*(1+random()), 0.5*(1+random()), 0.5*(1+random())], 0.5*random())
                else:
                    mat = Dialectric(1.5)
                world.add(Sphere(center, 0.2, [0,0,0], mat))
    world.add(Sphere((0, 1, 0), 1.0, [0,0,0], Dialectric(1.5)))
    world.add(Sphere((-4, 1, 0), 1.0, [0,0,0], Lambertian((0.4, 0.2, 0.1))))
    world.add(Sphere((4, 1, 0), 1.0, [0,0,0], Metal((0.7, 0.6, 0.5), 0.0)))

def draw():
    global framebuffer, targetbuffer, passes
    render_to_texture()
    passes += 1
    copy_texture_to_screen()
    framebuffer, targetbuffer = targetbuffer, framebuffer
    fps_display.draw()

def render_to_texture():
    global world
    # select the target to draw into
    with framebuffer:
        gl.glViewport(0, 0, FB_WIDTH, FB_HEIGHT)

        # clear the destination
        gl.glClearColor(0.5, 0.6, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # send the vertex data
        render_program.send_data([
            ((-1.0, -1.0), (1.0, 0.0, 0.0, 1.0)),
            ((1.0, -1.0), (0.0, 1.0, 0.0, 1.0)),
            ((1.0, 1.0), (0.0, 0.0, 1.0, 1.0)),
            ((-1.0, -1.0), (1.0, 0.0, 0.0, 1.0)),
            ((-1.0, 1.0), (0.0, 1.0, 0.0, 1.0)),
            ((1.0, 1.0), (0.0, 0.0, 1.0, 1.0))])

        # draw using the vertex array for vertex information
        with render_program, targetbuffer.rendered_texture:
            pyglet.gl.glUniform2f(pyglet.gl.glGetUniformLocation(render_program.program_name, ctypes.create_string_buffer('resolution'.encode('ascii'))), FB_WIDTH, FB_HEIGHT)
            pyglet.gl.glUniform1f(pyglet.gl.glGetUniformLocation(render_program.program_name, ctypes.create_string_buffer('time'.encode('ascii'))), (time()-start_time))
            world.update(render_program.program_name)
            camera.update(render_program.program_name)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)


def copy_texture_to_screen():
    # clear the destination
    gl.glClearColor(0.4, 0.4, 0.4, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # send the vertex data
    copy_program.send_data([
        ((-1.0, -1.0), (0.0, 0.0)),
        ((1.0, -1.0), (1.0, 0.0)),
        ((1.0, 1.0), (1.0, 1.0)),
        ((-1.0, 1.0), (0.0, 1.0)),
        ((1.0, 1.0), (0.0, 1.0)),
        ((-1.0, -1.0), (1.0, 1.0))])

    # draw
    with copy_program, framebuffer.rendered_texture:
        # copy over uniforms
        # TODO make more complex uniform objects so we dont need to search up location
        pyglet.gl.glUniform1f(pyglet.gl.glGetUniformLocation(copy_program.program_name, ctypes.create_string_buffer('passes'.encode('ascii'))), passes)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)


def main():
    global window
    window = pyglet.window.Window(WIDTH, HEIGHT)

    global framebuffer
    framebuffer = Framebuffer(FB_WIDTH, FB_HEIGHT, WIDTH, HEIGHT)

    global targetbuffer
    targetbuffer = Framebuffer(FB_WIDTH, FB_HEIGHT, WIDTH, HEIGHT)

    global render_program
    render_program = setup_render_program()

    global copy_program
    copy_program = setup_copy_program()

    global camera
    lookfrom = [13, 2, 3]
    lookat = [0, 0, 0]
    #dist = [lookfrom[0]-lookat[0], lookfrom[1]-lookat[1], lookfrom[2]-lookat[2]]
    #dist = sqrt(dist[0]*dist[0]+dist[1]*dist[1]+dist[2]*dist[2])
    dist = 10.0
    aperture = 0.1
    camera = Camera(lookfrom, lookat, [0, 1, 0], pi/9, WIDTH/HEIGHT, aperture, dist)
    
    R = cos(pi/4)
    #set up the world
    random_scene()
    #global world
    #world.add(Sphere([0, 0, -1], 0.5, [0,0,0], Lambertian((0.1, 0.2, 0.5))))
    #world.add(Sphere([0, -100.5, -1], 100, [0, 0, 0], Lambertian((0.8, 0.8, 0))))
    #world.add(Sphere([1, 0, -1], 0.5, [0, 0, 0], Metal((0.8, 0.6, 0.2), 1.0)))
    #world.add(Sphere([-1, 0, -1], 0.5, [0, 0, 0], Dialectric(1.5)))
    #world.add(Sphere([-1, 0, -1], -0.45, [0, 0, 0], Dialectric(1.5)))
    #world.add(Sphere([-R, 0, -1], R, [0, 0, 0], Lambertian((0, 0, 1))))
    #world.add(Sphere([R, 0, -1], R, [0, 0, 0], Lambertian((1, 0, 0))))

    print('OpenGL Version {}'.format(window.context.get_info().get_version()))
    window.on_draw = draw
    pyglet.clock.schedule_interval(lambda dt: None, 0.01)
    pyglet.app.run()


if __name__ == '__main__':
    main()

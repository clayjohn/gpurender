import pyglet
from pyglet import gl
import ctypes
import math
from time import time
from glhelper import *
from shapes import *
from material import *
from camera import *
from controls import *
from math import pi, cos, sqrt
from random import random

WIDTH = 400
HEIGHT = 400

FB_WIDTH = 200# WIDTH
FB_HEIGHT = 200# HEIGHT


render_program = None
copy_program = None
framebuffer = None
window = None
world = Hitable_list()
camera = None
controls = None
passes_label = None
time_label = None
fps_label = None

passes = 1
start_time = time()

# TODO save uniform locations of variables
# TODO BVH for objects
# TODO Store references to materials instead of unique materials
# TODO remove the amount of uniforms
    ## pass as texture


def random_scene():
    global world
    #world.add(Sphere((0, -1000, 0), 1000, [0, 0, 0], Lambertian((0.5, 0.5, 0.5))))
    world.add(Plane((0, 0, 0), 5, (1, 1, 0.1), DiffuseLight((0.5, 0.5, 0.5))))
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
                world.add(Sphere(center, 0.2, [0,1,0], mat))
    world.add(Sphere((0, 1, 0), 1.0, [0,1,0], Dialectric(2.0)))
    world.add(Sphere((-4, 1, 0), 1.0, [0,1,0], Lambertian((0.4, 0.2, 0.1))))
    world.add(Sphere((4, 1, 0), 1.0, [0,0,0], Metal((0.7, 0.6, 0.5), 0.0)))
    #world.add(Sphere((4, 1, 0), 1.0, [0,1,0], DiffuseLight((3.0, 3.0, 3.0))))

def refresh_buffer():
    global passes, start_time
    with targetbuffer:
        gl.glViewport(0, 0, FB_WIDTH, FB_HEIGHT)

        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    passes = 1
    start_time = time()

def update_labels():
    global passes_label, time_label, fps_label
    passes_label.text = "Passes: " + str(passes)
    time_label.text = "Time: " + "{0:.2f}".format(time()-start_time)
    fps_label.text = "FPS: " + "{0:.2f}".format(pyglet.clock.get_fps())
    passes_label.draw()
    time_label.draw()
    fps_label.draw()

def draw():
    global framebuffer, targetbuffer, passes
    #update_camera()
    if controls.update():
        refresh_buffer()
    render_to_texture()
    copy_texture_to_screen()
    passes += 1
    framebuffer, targetbuffer = targetbuffer, framebuffer
    update_labels()

def render_to_texture():
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

    global passes_label, time_label, fps_label
    passes_label = pyglet.text.Label("Passes: " + str(passes),
                          font_name='Times New Roman',
                          font_size=12,
                          x=6, y=window.height-6,
                          anchor_x='left', anchor_y='top')
    time_label = pyglet.text.Label("Time: " + str(time()-start_time),
                          font_name='Times New Roman',
                          font_size=12,
                          x=6, y=window.height-24,
                          anchor_x='left', anchor_y='top')

    fps_label = pyglet.text.Label("FPS: : " + str(passes),
                          font_name='Times New Roman',
                          font_size=12,
                          x=6, y=window.height-42,
                          anchor_x='left', anchor_y='top')
    
    global camera
    lookfrom = [278, 278, -800]
    lookat = [278, 278, 0]
    #dist = [lookfrom[0]-lookat[0], lookfrom[1]-lookat[1], lookfrom[2]-lookat[2]]
    #dist = sqrt(dist[0]*dist[0]+dist[1]*dist[1]+dist[2]*dist[2])
    dist = 10.0
    aperture = 0.0
    camera = Camera(lookfrom, lookat, [0, 1, 0], pi/4.5, WIDTH/HEIGHT, aperture, dist)
    
    global controls
    controls = Orbit(window, camera)

    #set up the world
    #random_scene()
    global world
    world.add(Disk((0, 278, 278),555, (1, 0, 0), Lambertian((0.65, 0.05, 0.05))))
    world.add(Disk((555, 278, 278),555, (-1, 0, 0), Lambertian((0.12, 0.45, 0.15))))
    world.add(Disk((278, 0, 278),555, (0, 1, 0), Lambertian((0.73, 0.73, 0.73))))
    world.add(Disk((278, 554, 278),99, (0, -1, 0), DiffuseLight((15, 15, 15))))
    world.add(Disk((278, 555, 278),555, (0, -1, 0), Lambertian((0.73, 0.73, 0.73))))
    world.add(Disk((278, 278, 555),555, (0, 0, -1), Lambertian((0.73, 0.73, 0.73))))
    world.add(Sphere((228, 100, 128), 100, (0, 0, 0), Dialectric(1.5)))


    print('OpenGL Version {}'.format(window.context.get_info().get_version()))
    window.on_draw = draw
    pyglet.clock.schedule_interval(lambda dt: None, 0.01)
    pyglet.app.run()


if __name__ == '__main__':
    main()

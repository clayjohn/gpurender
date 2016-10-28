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
texture_buffer = None

passes = 0
start_time = time()

# TODO save uniform locations of variables
# TODO BVH for objects (not necessary for now)
# TODO Store references to materials instead of unique materials
# TODO remove the amount of uniforms
    ## pass as texture
# TODO add triangles (maybe similar to quad is easiest)
# TODO add transformations
# TODO density changes
# TODO global fog
# TODO Isosurfaces??
    ## inside a bounding volume of course
# TODO clean up object creation (remove unnecessary fields)
# TODO figure out plane size issue

           
def setup_data_buffer(indata):
    PIXEL = pyglet.gl.GL_FLOAT * 4
    data = (PIXEL*1)((0.9, 0.4, 0.2, 1.0))
    name = pyglet.gl.GLuint(0)
    pyglet.gl.glGenBuffers(1, ctypes.byref(name))
    pyglet.gl.glBindBuffer(pyglet.gl.GL_TEXTURE_BUFFER, name)
    pyglet.gl.glBufferData(pyglet.gl.GL_TEXTURE_BUFFER, ctypes.sizeof(data), data, pyglet.gl.GL_STATIC_DRAW)

    texture = BufferTexture()
    with texture:
        pyglet.gl.glTexBuffer(pyglet.gl.GL_TEXTURE_BUFFER, pyglet.gl.GL_RGBA32F, name)
    pyglet.gl.glBindBuffer(pyglet.gl.GL_TEXTURE_BUFFER, 0)
    return texture

def random_scene():
    global world
    world.add(Sphere((0, -1000, 0), 1000, [0, 0, 0], Lambertian((0.5, 0.5, 0.5))))
    #world.add(Plane((0, 0, 0), 5, (1, 1, 0.1), DiffuseLight((0.5, 0.5, 0.5))))
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

    passes = 0
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
    global framebuffer, targetbuffer, passes, controls
    if controls.update():
        refresh_buffer()
    render_to_texture()
    passes += 1
    copy_texture_to_screen()
    framebuffer, targetbuffer = targetbuffer, framebuffer
    #if not controls.save_frame:
        #update_labels()
    #else:
        #pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot.png')
        #controls.save_frame = False

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
    with copy_program, framebuffer.rendered_texture, texture_buffer:
        # copy over uniforms
        # TODO make more complex uniform objects so we dont need to search up location
            pyglet.gl.glUniform1f(pyglet.gl.glGetUniformLocation(copy_program.program_name, ctypes.create_string_buffer('passes'.encode('ascii'))), passes)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)


def main():
    global window
    config = pyglet.gl.Config(major_version = 3, minor_version = 3)
    window = pyglet.window.Window(WIDTH, HEIGHT, vsync=False, config = config)
    
    print("finished with window")

    global framebuffer
    framebuffer = Framebuffer(FB_WIDTH, FB_HEIGHT, WIDTH, HEIGHT)

    global targetbuffer
    targetbuffer = Framebuffer(FB_WIDTH, FB_HEIGHT, WIDTH, HEIGHT)

    global texture_buffer
    texture_buffer = BufferTexture()

    print("finished framebuffers")
    global render_program
    render_program = setup_render_program()
    print('finished render program')
    global copy_program
    copy_program = setup_copy_program()
    print('copy program setup')
    print("making labels")
    global passes_label, time_label, fps_label
    #passes_label = pyglet.text.Label("Passes: " + str(passes),
    #                      font_name='Times New Roman',
    #                      font_size=12,
    #                      x=6, y=window.height-6,
    #                      anchor_x='left', anchor_y='top')
    #time_label = pyglet.text.Label("Time: " + str(time()-start_time),
    #                      font_name='Times New Roman',
    #                      font_size=12,
    #                      x=6, y=window.height-24,
    #                      anchor_x='left', anchor_y='top')
#
    #fps_label = pyglet.text.Label("FPS: : " + str(passes),
    #                      font_name='Times New Roman',
    #                      font_size=12,
    #                      x=6, y=window.height-42,
    #                      anchor_x='left', anchor_y='top')
    
    global camera
    lookfrom = [278, 278, -800]#[1, 3, -8]#
    lookat = [278, 278, 0]#[0, 0, 0]#
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
    world.add(Plane((0, 278, 278),278, (1, 0, 0), Lambertian((0.65, 0.05, 0.05))))
    world.add(Plane((555, 278, 278),278, (-1, 0, 0), Lambertian((0.12, 0.45, 0.15))))
    world.add(Plane((278, 0, 278),278, (0, 1, 0), Lambertian((0.73, 0.73, 0.73))))
    world.add(Plane((278, 554, 278),99, (0, -1, 0), DiffuseLight((15, 15, 15))))
    world.add(Plane((278, 555, 278),278, (0, -1, 0), Lambertian((0.73, 0.73, 0.73))))
    world.add(Plane((278, 278, 555),278, (0, 0, -1), Lambertian((0.73, 0.73, 0.73))))
    world.add(ConstantMedium(Cube((215, 80, 150), 80, (0, 0, 0), Isotropic((0.9, 0.2, 0.4)))))
    world.add((Cube((215, 80, 150), 80, (0, 0, 0), Dialectric(1.5))))
    world.add(ConstantMedium(Sphere((350, 80, 380), 80, (0, 0, 0), Isotropic((0.2, 0.4, 0.9)))))
    world.add((Sphere((350, 80, 380), 80, (0, 0, 0), Dialectric(1.5))))
    #world.add(Plane((0, 0, 0), 0, (0, 1, 0), Lambertian((0.45, 0.43, 0.39))))
    #world.add(Sphere((1, 1, 1), 1, (0, 1, 0), Metal((0.7, 0.7, 0.7), 0.1)))
    #world.add(ConstantMedium(Sphere((-1, 1, 0), 1, (0, 1, 0), Isotropic((0.7, 0.2, 0.2)))))
    #world.add(Sphere((-1, 1, 0), 1, (0, 1, 0), Dialectric(1.5)))
    #world.add(ConstantMedium(Sphere((-1, 2.5, 0), 0.5, (0, 1, 0), Isotropic((0.7, 0.2, 0.2)))))
    #world.add(Sphere((-1, 2.5, 0), 0.5, (0, 1, 0), Dialectric(1.5)))
    #world.add(ConstantMedium(Sphere((-1, 3.25, 0), 0.25, (0, 1, 0), Isotropic((0.7, 0.2, 0.2)))))
    #world.add(Sphere((-1, 3.25, 0), 0.25, (0, 1, 0), Dialectric(1.5)))
    #world.add(Sphere((0, 9, 0), 4.5, (0,0,0), DiffuseLight((5, 5, 5))))
    #world.add(ConstantMedium(Plane((1, 1, 0), 1, (-1, 0, 0), Isotropic((0.5, 0.5, 0.5)))))
    #world.add((Plane((1, 1, 0), 1, (-1, 1, 0), Dialectric(1.5))))
    #world.add((Plane((0, 1, 0), 1, (-1, 0, 0), Dialectric(1.5))))
    #world.add((Plane((2, 1, 0), 1, (-1, 0, 0), Dialectric(1.5))))
    #world.add((Plane((1, 2, 0), 1, (0, 1, 0), Dialectric(1.5))))

    print('OpenGL Version {}'.format(window.context.get_info().get_version()))
    window.on_draw = draw
    #cannot use pyglets text drawing if this is not used
    #but also cannot use this with opengl 3.3
    #pyglet.clock.schedule_interval(lambda dt: None, 0.01)
    #pyglet.app.run()
    #custom main loop to avoid compatibility mode
    i = 0
    while (i < 100):
        i += 1
        draw()
        window.flip()


if __name__ == '__main__':
    main()

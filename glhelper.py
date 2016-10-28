'''
Author: leovt (Leonhard Vogt)
License: GNU GENERAL PUBLIC LICENSE - Version 3, 29 June 2007

Example code for using glsl and vertex buffer objects with pyglet
'''
import sys
import warnings
import pyglet
from pyglet import gl
import ctypes

TYPE_NAME_TO_TYPE = {
    gl.GL_FLOAT: gl.GLfloat,
    gl.GL_DOUBLE: gl.GLdouble,
    gl.GL_INT: gl.GLint,
    gl.GL_UNSIGNED_INT: gl.GLuint,
    gl.GL_BYTE: gl.GLbyte,
    gl.GL_UNSIGNED_BYTE: gl.GLubyte,
    gl.GL_SHORT: gl.GLshort,
    gl.GL_UNSIGNED_SHORT: gl.GLushort,
}

def compile_shader(shader_type, shader_source):
    '''
    Compile a shader and print error messages.
    '''
    shader_name = gl.glCreateShader(shader_type)
    src_buffer = ctypes.create_string_buffer(shader_source)
    buf_pointer = ctypes.cast(ctypes.pointer(ctypes.pointer(src_buffer)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
    length = ctypes.c_int(len(shader_source) + 1)
    gl.glShaderSource(shader_name, 1, buf_pointer, ctypes.byref(length))
    gl.glCompileShader(shader_name)

    # test if compilation is succesful and print status messages
    success = gl.GLint(0)
    gl.glGetShaderiv(shader_name, gl.GL_COMPILE_STATUS, ctypes.byref(success))

    length = gl.GLint(0)
    gl.glGetShaderiv(shader_name, gl.GL_INFO_LOG_LENGTH, ctypes.byref(length))
    log_buffer = ctypes.create_string_buffer(length.value)
    gl.glGetShaderInfoLog(shader_name, length, None, log_buffer)

    log_message = log_buffer.value[:length.value].decode('ascii').strip()
    if log_message:
        sys.stderr.write(log_message + '\n')

    if not success:
        raise ValueError('Compiling of the shader failed.')

    return shader_name


def link_program(program_name):
    '''
    link a glsl program and print error messages.
    '''
    gl.glLinkProgram(program_name)

    success = gl.GLint(0)
    gl.glGetProgramiv(program_name, gl.GL_LINK_STATUS, ctypes.byref(success))

    length = gl.GLint(0)
    gl.glGetProgramiv(program_name, gl.GL_INFO_LOG_LENGTH, ctypes.byref(length))
    log_buffer = ctypes.create_string_buffer(length.value)
    gl.glGetProgramInfoLog(program_name, length, None, log_buffer)

    log_message = log_buffer.value[:length.value].decode('ascii').strip()
    if log_message:
        sys.stderr.write(log_message + '\n')

    if not success:
        raise ValueError('Linking of the shader program failed.')


class ShaderProgram:
    def __init__(self, vertex_shader, fragment_shader, attributes):
        # compile and link
        self.program_name = gl.glCreateProgram()
        gl.glAttachShader(self.program_name, compile_shader(gl.GL_VERTEX_SHADER, vertex_shader))
        gl.glAttachShader(self.program_name, compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader))
        link_program(self.program_name)

        # vertex type
        class VERTEX(ctypes.Structure):
            _fields_ = [ (name, TYPE_NAME_TO_TYPE[tname] * size)
                        for (name, tname, size) in attributes ]
        self.VERTEX = VERTEX

        # vertex array and buffer
        self.vertex_array_name = gl.GLuint(0)
        self.vertex_buffer_name = gl.GLuint(0)
        gl.glGenVertexArrays(1, ctypes.byref(self.vertex_array_name))
        gl.glGenBuffers(1, ctypes.byref(self.vertex_buffer_name))

        gl.glBindVertexArray(self.vertex_array_name)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer_name)
        for (name, tname, size) in attributes:
            location = gl.glGetAttribLocation(self.program_name,
                                              ctypes.create_string_buffer(name.encode('ascii')))
            if location < 0:
                warnings.warn('Attribute %r is not present.' % name, stacklevel=2)
                continue
            gl.glEnableVertexAttribArray(location)
            gl.glVertexAttribPointer(location, size, tname, False,
                                     ctypes.sizeof(VERTEX),
                                     ctypes.c_void_p(getattr(VERTEX, name).offset))
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)


    def __enter__(self):
        gl.glUseProgram(self.program_name)
        gl.glBindVertexArray(self.vertex_array_name)

    def __exit__(self, *unused):
        gl.glUseProgram(0)
        gl.glBindVertexArray(0)


    def send_data(self, data):
        data = (self.VERTEX * len(data))(*data)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer_name)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data), data, gl.GL_DYNAMIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)



def setup_render_program():
    
    vs = 'shaders/render.vert'
    fs = 'shaders/render.frag'
    vertex_shader = open(vs, 'rb').read()
    fragment_shader = open(fs, 'rb').read()

    return ShaderProgram(vertex_shader, fragment_shader, [
        ('position', gl.GL_FLOAT, 2),
        ('color', gl.GL_FLOAT, 4),
    ])

def setup_copy_program():
    
    vs = 'shaders/display.vert'
    fs = 'shaders/display.frag'
    vertex_shader = open(vs, 'rb').read()
    fragment_shader = open(fs, 'rb').read()

    return ShaderProgram(vertex_shader, fragment_shader, [
        ('position', gl.GL_FLOAT, 2),
        ('texcoord', gl.GL_FLOAT, 2),
    ])


class Texture:
    def __init__(self):
        self.name = gl.GLuint(0)
        gl.glGenTextures(1, ctypes.byref(self.name))

    def __enter__(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.name)

    def __exit__(self, *unused):
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

class BufferTexture(Texture):
    def __enter__(self):
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_BUFFER, self.name)

    def __exit__(self, *unused):
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_BUFFER, 0)


class Framebuffer:
    def __init__(self, width, height, wwidth, wheight):
        self.width = width
        self.height = height
        self.windowwidth = wwidth
        self.windowheight = wheight
        self.framebuffer = gl.GLuint(0)
        self.rendered_texture = Texture()

        gl.glGenFramebuffers(1, ctypes.byref(self.framebuffer))

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer)

        # Set up the texture as the target for color output
        with self.rendered_texture:
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F, self.width, self.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, 0)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.rendered_texture.name, 0)

        if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
            raise ValueError('Framebuffer not set up completely')

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)


    def __enter__(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer)
        draw_buffers = (gl.GLenum * 1)(gl.GL_COLOR_ATTACHMENT0)
        gl.glDrawBuffers(1, draw_buffers)
        gl.glViewport(0, 0, self.width, self.height)


    def __exit__(self, *unused):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glViewport(0, 0, self.windowwidth, self.windowheight)



import os
from platform import release
from PIL import Image 
from tkinter import EXTENDED
import OpenGL.GL as GL             # standard Python OpenGL wrapper
import glfw                        # lean window system wrapper for OpenGL
import numpy as np                 # all matrix manipulations & OpenGL args
from transform import Trackball, identity

from core import Shader, Mesh, VertexArray,  load
from transform import *
import assimpcy  
from animation import *

class Viewer:
    """ GLFW viewer window, with classic initialization & graphics loop """
    def __init__(self, width=640, height=480):

        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # initialize trackball
        self.trackball = Trackball()
        self.mouse = (0, 0)

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_scroll_callback(self.win, self.on_scroll)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 0.1)
        GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)

        # initially empty list of object to draw
        self.drawables = []

    def run(self):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            # clear draw buffer, but also need to clear Z-buffer! (Exercise 1)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # comment this, uncomment next
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            win_size = glfw.get_window_size(self.win)



            view = self.trackball.view_matrix()
            projection = self.trackball.projection_matrix(win_size)

            # DrawSkyBox(view=view, projection=projection,
            #                   model=identity())
            
            # draw our scene objects
            for drawable in self.drawables:
                drawable.draw(view=view, projection=projection,
                              model=identity())

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def add(self, *drawables):
        """ add objects to draw in this window """
        self.drawables.extend(drawables)

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT or action == glfw.RELEASE:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key, action)

    def on_mouse_move(self, win, xpos, ypos):
        """ Rotate on left-click & drag, pan on right-click & drag """
        old = self.mouse
        self.mouse = (xpos, glfw.get_window_size(win)[1] - ypos)
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT):
            self.trackball.drag(old, self.mouse, glfw.get_window_size(win))
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT):
            self.trackball.pan(old, self.mouse)

    def on_scroll(self, win, _deltax, deltay):
        """ Scroll controls the camera distance to trackball center """
        self.trackball.zoom(deltay, glfw.get_window_size(win)[1])

class SkyBoxTexture:
    """ Helper class to create and automatically destroy textures """
    def __init__(self, tex_files):
        
        
        self.glid = GL.glGenTextures(1)
        self.type = GL.GL_TEXTURE_CUBE_MAP
        
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.glid)

        for i in range(6):
            try:

                tex = Image.open(tex_files[i]).convert('RGBA')
                GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGBA, tex.width, tex.height,
                            0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tex.tobytes())


            except FileNotFoundError:
                print("ERROR: unable to load texture file %s" % tex_files[i])

        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)
        
    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)



class skybox:
    def __init__(self, shader, attributes, text_files) :
        self.text_files = text_files
        self.shader = shader
        # self.attributes = attributes
        self.vertex_array = VertexArray(shader, attributes)
        


    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        GL.glUseProgram(self.shader.glid)
        self.shader.set_uniforms({**uniforms})
        
        sky = SkyBoxTexture(tex_files=self.text_files)
        self.vertex_array.execute(primitives)

        

def DrawSkyBox(**uniforms):
    text_files = ["objects/sky/right.jpg", "objects/sky/left.jpg", "objects/sky/top.jpg", "objects/sky/bottom.jpg", "objects/sky/front.jpg", "objects/sky/back.jpg"]
    skyboxShader = Shader("SkyBox.vert", "SkyBox.frag")
    GL.glUseProgram(skyboxShader.glid)
    skyboxShader.set_uniforms({**uniforms})
    vertex_array = VertexArray(skyboxShader, attributes)
    sky = SkyBoxTexture(tex_files=text_files)
    vertex_array.execute(GL.GL_TRIANGLES)



class Mesh:
    """ Basic mesh class, attributes and uniforms passed as arguments """
    def __init__(self, shader, attributes, uniforms=None, index=None):
        self.shader = shader
        self.uniforms = uniforms or dict()
        self.vertex_array = VertexArray(shader, attributes, index)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        GL.glUseProgram(self.shader.glid)
        self.shader.set_uniforms({**self.uniforms, **uniforms})
        self.vertex_array.execute(primitives)

skyboxatt = [
    (-1.0,  1.0, -1.0),
    (-1.0, -1.0, -1.0),
    ( 1.0, -1.0, -1.0),
    ( 1.0, -1.0, -1.0),
    ( 1.0,  1.0, -1.0),
    (-1.0,  1.0, -1.0),
    (-1.0, -1.0,  1.0),
    (-1.0, -1.0, -1.0),
    (-1.0,  1.0, -1.0),
    (-1.0,  1.0, -1.0),
    (-1.0,  1.0,  1.0),
    (-1.0, -1.0,  1.0),
    ( 1.0, -1.0, -1.0),
    ( 1.0, -1.0,  1.0),
    ( 1.0,  1.0,  1.0),
    ( 1.0,  1.0,  1.0),
    ( 1.0,  1.0, -1.0),
    ( 1.0, -1.0, -1.0),
    (-1.0, -1.0,  1.0),
    (-1.0,  1.0,  1.0),
    ( 1.0,  1.0,  1.0),
    ( 1.0,  1.0,  1.0),
    ( 1.0, -1.0,  1.0),
    (-1.0, -1.0,  1.0),
    (-1.0,  1.0, -1.0),
    ( 1.0,  1.0, -1.0),
    ( 1.0,  1.0,  1.0),
    ( 1.0,  1.0,  1.0),
    (-1.0,  1.0,  1.0),
    (-1.0,  1.0, -1.0),
    (-1.0, -1.0, -1.0),
    (-1.0, -1.0,  1.0),
    ( 1.0, -1.0, -1.0),
    ( 1.0, -1.0, -1.0),
    (-1.0, -1.0,  1.0),
    ( 1.0, -1.0,  1.0)
]
attributes = dict(
        position=np.array(tuple(skyboxatt),"f"))

if __name__ == "__main__" :
    viewer = Viewer()

    
    fairy_shader = Shader("fairy.vert", "fairy.frag")
    text_files = ["objects/sky2/right.png", "objects/sky2/left.png", "objects/sky2/top.png", "objects/sky2/bottom.png", "objects/sky2/front.png", "objects/sky2/back.png"]
    skyboxShader = Shader("SkyBox.vert", "SkyBox.frag")
    sky = skybox(skyboxShader, attributes, text_files)
    # viewer.add(*load('cube.obj', fairy_shader, tex_file= "sky.jpg"))
    viewer.add(sky)
    viewer.run()

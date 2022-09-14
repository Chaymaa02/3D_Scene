#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

from cmath import pi
from ctypes import pointer
from platform import release
import random
from tkinter import EXTENDED
import OpenGL.GL as GL
from cv2 import transform             # standard Python OpenGL wrapper
import glfw                        # lean window system wrapper for OpenGL
import numpy as np                 # all matrix manipulations & OpenGL args
from transform import Trackball, identity

from core import Shader, Mesh, Viewer, load
from transform import *
import assimpcy  
from animation import *
from math import cos, sin


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
                    drawable.key_handler(key)

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

# class Plant(Mesh) :

#     def __init__(self, shader, lsystem):

#         angle =22.5
#         position_tuple = ()
#         color_tuple = ()
#         write = False
#         pointeur = [0,0,0]
#         direction = 0
#         n = len(lsystem)
#         pas = 0.2

#         for i in range(n):
#             if  lsystem[i] == "F":
#                 pointeur[0] += pas*cos(direction)
#                 pointeur[1] += pas*sin(direction)
            
#             if lsystem[i] == "[":
#                 write = True
                
#             if lsystem[i] == "]":
#                 write = False

#             if lsystem[i] == "+":
#                 direction += angle

#             if lsystem[i] == "-":
#                 direction -= angle

#             if write:
#                 position_tuple += (tuple(pointeur))
#                 color_tuple += ((0,1,0))


#         # position = np.array(position_tuple, 'f')
#         # color = np.array(color_tuple, 'f')
#         position = np.array(((0, .5, 0), (-.5, -.5, 0), (.5, -.5, 0)), 'f')
#         color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')
#         self.color = (1, 1, 0)
#         attributes = dict(position=position, color=color)
#         super().__init__(shader, attributes=attributes)

#     def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
#         super().draw(primitives=primitives, global_color=self.color, **uniforms)

#     def key_handler(self, key):
#         if key == glfw.KEY_C:
#             self.color = (0, 0, 0)


def lsystem(axiom,nb) :
    for _ in range(nb):
        n = len(axiom)
        sh = ""
        for i in range(n):
            # if axiom[i] == "X":
            #     sh += "F-[[X]+X]+F[+FX]-X"
            if axiom[i] == "F" :
                sh += "FF-[-F+F+F]+[+F-F-F]"
            else :
                sh += axiom[i]
        axiom = sh
    return axiom


class Branch(Node):
    def __init__(self, shader):
        super().__init__()
        self.add(*load('objects/green/branch.obj', shader, tex_file= "objects/green/branch.jpg"))  

class Plant(Node):
        def __init__(self, transform):
            super().__init__(transform= transform)
            angle =22.5
            angle = angle*pi/180
            position_tuple = []
            color_tuple = []
            pointeur = [0,0,0]
            direction = 0
            lsystem_char = lsystem("F", 3)
            # lsystem_char = "[FF+F]"
            n = len(lsystem_char)
            pas = 0.1
            states = []
            dir = []
            fairy_shader = Shader("fairy.vert", "fairy.frag")
            branch_load = Branch(fairy_shader)
            axe = (0,0,1)
            for i in range(n):
                if  lsystem_char[i] == "F":
                    #scale(0.01,0.005,0.005)
                    branch = Node(transform= translate(pointeur[0], pointeur[1],0) @ rotate(axe, -direction*180/pi) @ rotate((0,0,1), 90) @ scale(0.01,0.005,0.005))
                    branch.add(branch_load)
                    self.add(branch)

                    position_tuple.append(tuple(pointeur))
                    color_tuple.append((0,1,0))

                    if cos(direction) >= 0 :
                        signe = 1
                    else :
                        signe = -1

                    pointeur[0] += pas*sin(direction)
                    pointeur[1] += pas*cos(direction)

                    position_tuple.append(tuple(pointeur))
                    color_tuple.append((0,1,0))
            
                    pt = [pointeur[0] - signe*0.01,pointeur[1],0]
                    position_tuple.append(tuple(pt))
                    color_tuple.append((0,1,0))



                if lsystem_char[i] == "[":

                    states.append(pointeur[:])
                    dir.append(direction)
                    
                if lsystem_char[i] == "]":
                    # l = [(1,0,0),(0,0,1)]
                    # random.random()
                    # axe = random.choice(l)
                    pointeur = states.pop()
                    direction = dir.pop()

                if lsystem_char[i] == "+":
                    direction += angle

                if lsystem_char[i] == "-":
                    direction -= angle

        def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
            """ When redraw requested, interpolate our node transform from keys """
            
            super().draw(primitives=primitives, **uniforms)

def main():
    viewer = Viewer()
    color_shader = Shader("color.vert", "color.frag")
    # viewer.add(Plant(color_shader, lsystem= lsystem("F", 4)))
    position = np.array(((0, .5, 0), (-.5, -.5, 0), (.5, -.5, 0)), 'f')
    color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')
    plant = Plant(transform= scale(0.1,0.1,0.1))

    viewer.add(plant)

    viewer.run()

if __name__ == '__main__':
    main()   
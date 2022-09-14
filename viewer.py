#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""
from re import S
from water import Water
from cmath import pi
from math import cos, sin
from texture import Texture, Textured
from platform import release
from tkinter import EXTENDED
import OpenGL.GL as GL             # standard Python OpenGL wrapper
import glfw                        # lean window system wrapper for OpenGL
import numpy as np                 # all matrix manipulations & OpenGL args
from transform import Trackball, identity
from objects import *
from core import Shader, Mesh, Viewer, load
from transform import *
import assimpcy  
from animation import *
from skybox import *
from ground import Terrain
from plants import Plant
from itertools import cycle

# ------------  Exercise 1 and 2: Scene object classes ------------------------
class Node:
    """ Scene graph transform and parameter broadcast node """
    def __init__(self, children=(), transform=identity()):
        self.transform = transform
        self.world_transform = identity()
        self.children = list(iter(children))

    def add(self, *drawables):
        """ Add drawables to this node, simply updating children list """
        self.children.extend(drawables)

    def draw(self, model=identity(), **other_uniforms):
        """ Recursive draw, passing down updated model matrix. """
        self.world_transform = model @ self.transform # TODO: replace with correct transform
        for child in self.children:
            child.draw(model=self.world_transform, **other_uniforms)

    def key_handler(self, key):
        """ Dispatch keyboard events to children with key handler """
        for child in (c for c in self.children if hasattr(c, 'key_handler')):
            child.key_handler(key)

class Cylinder(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, shader):
        super().__init__()
        self.add(*load('cylinder.obj', shader))  # just load cylinder from file
# ------------  Viewer class & window management ------------------------------

track_top = Trackball( pitch = 20,distance= 8)
track_top.pos2d = vec(0.0, -1.8)
track_fairy = Trackball_fairy()
cycle_track = cycle([track_top, track_fairy])
cycle_mode = cycle([  np.array([0.4,0.4,0.4,0]) , np.array([0,0,0,0]) ])
class Viewer:
    """ GLFW viewer window, with classic initialization & graphics loop """
    def __init__(self, width=4*640, height=4*480):

        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)
        self.mode = np.array([0,0,0,0])
        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        self.position_fairy = np.array([0,0.35,-0.2])

        # initialize trackball
        self.trackball = next(cycle_track)
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
        # GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)

        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

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

            GL.glDepthMask(GL.GL_FALSE)
            DrawSkyBox(view=view, projection=projection,
                              model=identity(), mode = self.mode)
            GL.glDepthMask(GL.GL_TRUE)
            # draw our scene objects
            for drawable in self.drawables:
                if isinstance (drawable,Water) :
                    GL.glEnable(GL.GL_BLEND)
                    drawable.draw(view=view, projection=projection,
                              model=identity(), mode = self.mode)
                    GL.glDisable(GL.GL_BLEND)
                elif isinstance (drawable,Fairy) :
                    drawable.draw(view=view, projection=projection,
                                model=identity(), mode = -self.mode/2)
                else :
                    drawable.draw(view=view, projection=projection,
                                model=identity(), mode = self.mode, position_fairy = self.position_fairy)

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
            
            if key == glfw.KEY_N and action == glfw.PRESS:
                self.mode = next(cycle_mode)

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    if isinstance (drawable,Fairy) :
                        drawable.key_handler(key, action)
                    else :
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

class Wing(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, shader):
        super().__init__()
        self.add(*load('objects/fairy/wing.obj', shader))  

class Cylinder(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, shader):
        super().__init__()
        self.add(*load('cylinder.obj', shader)) 

class Body(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, shader):
        super().__init__()
        light_dir = (0, -1, 0)
        self.add(*load('objects/fairy/fairy.obj', shader, tex_file="objects/fairy/fairy.png", light_dir = light_dir))  

class Fairy(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, transform, viewer):
        super().__init__()
        self.tz = transform[2,3]
        self.ty = transform[1,3]
        self.translation = identity()
        self.rot_angle = 0

        self.model = transform
        self.transform = transform
        # self.pos = vec(self.transform[0,3], self.transform[2,3])
        self.viewer = viewer
        self.plant = Plant( scale(0.1,0.1,0.1))
        self.W_pressed = 0
        self.keyframes = TransformKeyFrames({0: vec(0,0,0)},{glfw.get_time(): quaternion()},{0: 1})
    
        # translate_keys = {0: vec(0,0,0)}
        # rotate_keys = {glfw.get_time(): quaternion()}
        # scale_keys = {0: 1}
        # self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)
    def key_handler(self, key, action):
        if key == glfw.KEY_W :
            if action == glfw.PRESS :
                translate_keys = {0: vec(0,0,0)}
                rotate_keys = {glfw.get_time(): quaternion(), glfw.get_time()+2: quaternion_from_euler(0, 0, -80)}
                scale_keys = {0: 1}
                self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)
                

            if action == glfw.RELEASE :
                if self.W_pressed == 1:
                    self.W_pressed = 0
                translate_keys = {0: vec(0,0,0)}
                rotate_keys = { glfw.get_time()+2: quaternion()}
                scale_keys = {0: 1}
                self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)

            if action == glfw.REPEAT:
                self.W_pressed = 1
                self.translation =  translate(-0.01*sin(self.rot_angle*pi/180),0,-0.01*cos(self.rot_angle*pi/180)) @ self.translation
                z = -0.01*cos(self.rot_angle*pi/180)
                track_fairy.follow_fairy_z += z
                x = -0.01*sin(self.rot_angle*pi/180)
                track_fairy.follow_fairy_x +=  x
                self.viewer.position_fairy += np.array([x,0,z])

            self.transform = self.translation @ translate(0,self.ty,self.tz) @ rotate((0,1,0), self.rot_angle) @ self.keyframes.value(glfw.get_time()) @ translate(0,-self.ty,-self.tz) @ self.model

        if key == glfw.KEY_A :
            if action == glfw.PRESS or action == glfw.REPEAT:

                self.rot_angle +=3
                track_fairy.rotate_view_fairy_z(self.rot_angle)
                self.transform = self.translation @ translate(0,self.ty,self.tz) @ rotate((0,1,0), self.rot_angle) @ translate(0,-self.ty,-self.tz) @ self.model


        if key == glfw.KEY_D :
            if action == glfw.PRESS :
                self.rot_angle -=3


            if action == glfw.REPEAT:
                self.rot_angle -=3
            track_fairy.rotate_view_fairy_z(self.rot_angle)
            self.transform = self.translation @ translate(0,0,self.tz) @ rotate((0,1,0), self.rot_angle) @ translate(0,0,-self.tz) @ self.model


        if key == glfw.KEY_SPACE :
            if action == glfw.PRESS :
                self.viewer.trackball = next(cycle_track)



                

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        """ When redraw requested, interpolate our node transform from keys """
        super().draw(primitives=primitives, **uniforms)
        
def populate_terrain (viewer, shader1, shader2):
    mush = load("objects/mush/mush.obj", shader1, "objects/mush/mush.jpg")

    house1 = Node (transform = translate(-4,0.02,-3) @ rotate((1,0,0), -90) @ scale(0.068,0.068,0.068))
    house1.add(*mush)

    house2 = Node (transform = translate(-3, 0.02,-4) @ rotate((1,0,0), -90) @ scale(0.068,0.068,0.068))
    house2.add(*mush)

    house3 = Node (transform = translate(-3, 0.02,-2) @ rotate((1,0,0), -90) @ scale(0.068,0.068,0.068))
    house3.add(*mush)

    house4 = Node (transform = translate(-2, 0.02,-1) @ rotate((1,0,0), -90) @ scale(0.068,0.068,0.068))
    house4.add(*mush)

    house5 = Node (transform = translate(-2, 0.02,-3) @ rotate((1,0,0), -90) @ scale(0.068,0.068,0.0685))
    house5.add(*mush)

    house6 = Node (transform = translate(-4, 0.02,-1) @ rotate((1,0,0), -90) @ scale(0.068,0.068,0.068))
    house6.add(*mush)

    house7 = Node (transform = translate(-1, 0.02,-2) @ rotate((1,0,0), -90) @ scale(0.068,0.068,0.068))
    house7.add(*mush)

    house8 = Node (transform = translate(-1, 0.02,-4) @ rotate((1,0,0), -90) @ scale(0.068,0.068,0.068))
    house8.add(*mush)

    mush2 = load("objects/mush/Mushrooms_03.FBX", shader2)
    mushroom1 = Node (transform = translate(-5, 0, 0)   @ scale(0.05,0.05,0.05))
    mushroom1.add(*mush2)

    mushroom2 = Node (transform = translate(-2.7, 0, -1)   @ scale(0.05,0.05,0.05))
    mushroom2.add(*mush2)

    mushroom3 = Node (transform = translate(-5.9, 0, -3.6)   @ scale(0.05,0.05,0.05))
    mushroom3.add(*mush2)

    mushroom4 = Node (transform = translate(-3.9, 0, -4.2)   @ scale(0.05,0.05,0.05))
    mushroom4.add(*mush2)


    file = "objects/mush/Constructed_FenceWood.FBX"
    L = to_center(file)
    x_init = L[0]
    y_init = L[1]
    z_init = L[2]


    fence = load("objects/mush/13076_Gothic_Wood_Fence_Panel_v2_l3.obj", shader1, tex_file="objects/mush/Gothic_Wood_Fence_Pane_diffuse.jpg") 
    bush_cote1 = Node (transform = translate(-3.75, 0, -3) @ rotate((1,0,0), -90) @ rotate((0,0,1), -90) @ scale(0.003, 0.003,0.003))
    bush_cote1.add(*fence)

    bush_cote2 = Node (transform = translate(-3, 0, -3.4) @ rotate((1,0,0), -90)  @ scale(0.003, 0.003,0.003))
    bush_cote2.add(*fence)

    bush_cote3 = Node (transform = translate(-2.6, 0, -4) @ rotate((1,0,0), -90) @ rotate((0,0,1), -90) @ scale(0.003, 0.003,0.003))
    bush_cote3.add(*fence)

    bush_cote4 = Node (transform = translate(-1, 0, -3.4) @ rotate((1,0,0), -90)  @ scale(0.003, 0.003,0.003))
    bush_cote4.add(*fence)

    bush_cote5 = Node (transform = translate(-0.65, 0, -4) @ rotate((1,0,0), -90) @ rotate((0,0,1), -90) @ scale(0.003, 0.003,0.003))
    bush_cote5.add(*fence)

    bush_cote6 = Node (transform = translate(-1.6, 0, -1) @ rotate((1,0,0), -90) @ rotate((0,0,1), -90) @ scale(0.003, 0.003,0.003))
    bush_cote6.add(*fence)


    # # add_butterfly(viewer)
    # animate = Shader("animate.vert", "animate.frag")
    # viewer.add(Wolf(animate, transform= translate(-0.7, 0, -1.75) @ rotate((0,1,0), -90) @ scale(0.003, 0.003, 0.003)))
    # viewer.add(Dragon(animate,  transform= translate(0.7, 0, -1) @ rotate((0,1,0), -90) @ scale(0.00008, 0.00008, 0.00008)))

    viewer.add(house1, house2, house3, house4, house5, house6, house7, house8, mushroom1, mushroom2, mushroom3, mushroom4, bush_cote1)
    viewer.add(bush_cote2, bush_cote3, bush_cote4, bush_cote5, bush_cote6)

def to_center (file):
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_JoinIdenticalVertices | pp.aiProcess_FlipUVs
        flags |= pp.aiProcess_OptimizeMeshes | pp.aiProcess_Triangulate
        flags |= pp.aiProcess_GenSmoothNormals
        flags |= pp.aiProcess_ImproveCacheLocality
        flags |= pp.aiProcess_RemoveRedundantMaterials
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []

    px = []

    for _, mesh in enumerate(scene.mMeshes):
        px = mesh.mVertices[:,0]
        py = mesh.mVertices[:,1]
        pz = mesh.mVertices[:,2]
    
    return [min(px), min(py), min(pz) ]

# -------------- main program and scene setup --------------------------------
def main():
    """ create window, add shaders & scene objects, then run rendering loop """
    viewer = Viewer()
    color_shader = Shader("color.vert", "color.frag")
    fairy_shader = Shader("fairy.vert", "fairy.frag")
    animate = Shader("animate.vert", "animate.frag")

    file = 'objects/fairy/wing.obj'
    L = to_center( file )
    x_init = L[0]
    y_init = L[1]
    z_init = L[2]

    # cylinder = Cylinder(color_shader)
    # corps = Node(transform= translate(0.5,-y_init,0) @ scale(0.01,0.1,0.01))
    # corps.add(cylinder)

    # place instances of our basic objects
    # viewer.add(Pyramid(color_shader))
    # viewer.add(Triangle(color_shader))
    
    text_files = ["objects/sky2/right.png", "objects/sky2/left.png", "objects/sky2/top.png", "objects/sky2/bottom.png", "objects/sky2/front.png", "objects/sky2/back.png"]
    skyboxShader = Shader("SkyBox.vert", "SkyBox.frag")
    sky = skybox(skyboxShader, attributes, text_files)
    # viewer.add(*load('powder/powder.png', fairy_shader))
    # viewer.add(sky)


    wing_load = Wing(color_shader)
    Body_load = Body(fairy_shader)

    wing = Node(transform=  translate(0,0,0) @ rotate((0,1,0),-30.0)  @ scale(0.13,0.13,0.13)  @  translate(-x_init,-y_init,-z_init)  )
    wing2 = Node(transform=  translate(0,0,0) @ rotate((0,1,0),-150.0)  @ scale(0.13,0.13,0.13)  @  translate(-x_init,-y_init,-z_init)  )
    body = Node(transform= translate(0,-0.5,-0.05) @ rotate((0,0,1),90.0)  @rotate((1,0,0),180.0)  @ rotate((0,1,0),90.0)  @ scale(0.005,0.005,0.005))

    wing.add(wing_load)
    wing2.add(wing_load)
    body.add(Body_load)

    fairy = Fairy(viewer = viewer, transform= translate(0,0.2,0) @ scale(0.2,0.2,0.2))
    # viewer.trackball.pos2d = fairy.pos


    translate_keys = {0: vec(0,0,0), 2:vec(0,0,0)}
    rotate_keys = {0: quaternion(), 0.5: quaternion_from_euler(0, -45, 0) , 1: quaternion()}
    scale_keys = {0: 1}
    keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys)
    keynode.add(wing)

    translate_keys = {0: vec(0,0,0), 2:vec(0,0,0)}
    rotate_keys = {0: quaternion(), 0.5: quaternion_from_euler(0, 45, 0) , 1: quaternion()}
    scale_keys = {0: 1}
    keynode2 = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys)
    keynode2.add(wing2)

    fairy.add(body,keynode,keynode2)

    viewer.add(fairy)

    colorr_shader = Shader("color1.vert", "color1.frag")
    bumpyTerrain = Terrain(9000, 9000, colorr_shader, colorr_shader)

    wrap, filter = GL.GL_MIRRORED_REPEAT,  (GL.GL_LINEAR, GL.GL_LINEAR)

    texture = Texture("objects/ground/ground1.jpg", wrap, *filter)
    texturePath = Texture("objects/ground/sol.jpg", wrap, *filter)
    terrain = bumpyTerrain.draw()
    textured = Textured( terrain[0], diffuse_map=texture)
    texturedPath = Textured(terrain [1], diffuse_map=texturePath)
    viewer.add(textured)
    viewer.add(texturedPath)

    populate_terrain(viewer, fairy_shader, color_shader)


    n = Node(transform = translate(0,0,-12) @ rotate((1,0,0), -90) @ scale(0.05,0.05,0.05) )
    n.add(*load("objects/mush/mush.obj", fairy_shader, "objects/mush/mush.jpg"))
    viewer.add(n)


# -------------- add objects -------------
    add_butterfly(viewer, animate)
    # mush = load('objects/Seagull/seagul.FBX',animate, tex_file='objects/Seagull/gull.png')
    # s = Seagul(translate(0, 0, 0), mush)
    # s1 = Seagul(translate(-0.1, 0.2, 0), mush)
    # s2 = Seagul(translate(0.2, -0.1, 0), mush)
    # s.add(s1, s2)
    # viewer.add(s)
    viewer.add(Wolf(animate, transform= translate(-0.7, 0, -1.75) @ rotate((0,1,0), -90) @ scale(0.003, 0.003, 0.003)))
    add_fish(viewer, animate)
    add_boat(viewer, fairy_shader)



    water_shader = Shader("water.vert", "water.frag")
    water = Water(3000,3000,water_shader, transform = translate(0,-0.1,0))
    water2 = Water(3000,3000,water_shader, transform = translate(-4.5,-0.1,-5.5))
    viewer.add(water)
    viewer.add(water2)


    viewer.run()


if __name__ == '__main__':
    main()                  # main function keeps variables locally scoped

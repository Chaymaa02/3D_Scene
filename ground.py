
#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

from distutils import text_file
from random import *
from math import cos, ceil, floor, sqrt
from syslog import LOG_LOCAL0

import OpenGL.GL as GL             # standard Python OpenGL wrapper
import glfw                        # lean window system wrapper for OpenGL
import numpy as np                 # all matrix manipulations & OpenGL args
import noise
from texture import Texture, Textured
from transform import Trackball, identity, rotate, scale, translate
from core import Node, Shader, Mesh, load
import assimpcy
from itertools import cycle



# ------------  Viewer class & window management ------------------------------
class Viewer:
    """ GLFW viewer window, with classic initialization & graphics loop """
    def __init__(self, width=900, height=700):

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
        # GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)

        # initially empty list of object to draw
        self.drawables = []

    def run(self):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            # clear draw buffer, but also need to clear Z-buffer! (Exercise 1)
            #GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # comment this, uncomment next
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
        if action == glfw.PRESS or action == glfw.REPEAT:
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





#--------------------------------------------------------------------------------
#------------------ MY CODE -----------------------------------------------------


def normalize (x, y, z):
    m = sqrt(x**2 + y**2 + z**2)
    L = []
    if (m>0):
        L.append(x/m)
        L.append(y/m)
        L.append(z/m)
    return L


###Perlinn things!!

class PerlinNoise:
    def __init__(self):
        self.repeatx =1024
        self.repeaty = 1024

    def PerlinNoise (self, x, y, oct = 6, scale = 200, persist = 0.5, lacun = 0.025 ):
        shape = [self.repeatx,self.repeaty]
        res = noise.pnoise2(x/scale, 
                                    y/scale, 
                                    octaves=oct, 
                                    persistence=persist, 
                                    lacunarity=lacun, 
                                    repeatx=shape[0], 
                                    repeaty=shape[1], 
                                    base=0)
        

        return res * 120



    def defineNormal (self, x, y):
        if (x == 0):
            x = 1
        
        if (y == 0):
            y = 1
        
        hleft = self.PerlinNoise(x-1, y)
        hright = self.PerlinNoise(x+1, y) 
        hdown = self.PerlinNoise(x, y+1)
        hup = self.PerlinNoise(x, y-1)


        return normalize(hleft-hright, 2, hdown-hup)



class Terrain:
    def __init__(self, width, height, shaderTerrain, shaderPath ):

        self.width = width
        self.height = height
        self.shaderTerrain = shaderTerrain
        self.shaderPath = shaderPath
        self.nbSamples = 180
        self.Vertices_Ground, self.Normals_Ground, self.Faces_Ground = [], [], []
        self.Vertices_Path, self.Normals_Path, self.Faces_Path= [], [], []
        self.dict_Path = {}


    def build_top_left (self, i, j, hw, hh):


        persistence = 1.25
        lacunarity = 0
        scale = 200
        octaves = 2


        perlin = PerlinNoise()

        offsetx = -self.width/2
        offsety = -200

        w = self.width
        h = self.height

        a1,b1 = floor(i * hw)+ offsetx  , floor(j * hh)  + offsety
        b1 = -b1
        a1 = -a1

        if ( (w/12 < floor(i *hw ) < 5*w/12 and h/12 < floor(j *hh ) < 5*h/12) or  (7*w/12 < floor(i *hw ) < 11*w/12 and 7*h/12 < floor(j *hh ) < 11*h/12)):
            self.Vertices_Ground.append([a1/900 , -w/16000 , b1/700])
            L = perlin.defineNormal(a1, b1)
            self.Normals_Ground.append([L[0], L[1], L[2] ])
        else:
            self.Vertices_Ground.append([a1/900 , perlin.PerlinNoise(a1, b1,  persist = persistence, lacun=lacunarity, scale=scale, oct=octaves) / 200 , b1/700])
            L = perlin.defineNormal(a1, b1)
            self.Normals_Ground.append([L[0], L[1], L[2] ])


    def build_top_right (self, i, j, hw, hh):

        perlin = PerlinNoise() 

        persistence = 2
        lacunarity = 0
        scale = 200
        octaves = 3

        w = self.width
        h = self.height

        offsetx = -self.width/2
        offsety = -200

        a1,b1 = floor(i * hw)+ offsetx  , floor(j * hh)  + offsety
        b1 = -b1
        a1 = -a1



        noise = perlin.PerlinNoise(a1, b1,  persist = persistence, lacun=lacunarity, scale=scale, oct=octaves) / 200 
        
        value = 0
        x = floor(i *hw )
        if ( x < w/6 or  x>  5*w/6):
            value = 0.08 * abs( x - w/6) / w
        elif (x< 2*w/6 or x>  4*w/6 ):
            value = 0.03 * abs( x - 2*w/6) / w


        self.Vertices_Ground.append([a1/900 , noise+ value , b1/700])
        L = perlin.defineNormal(a1, b1)
        self.Normals_Ground.append([L[0], L[1], L[2] ])





    def draw(self):
        """ Returns A list of Meshes Constituting the Whole Terrain"""

        #Filling the lists of the lists containing the important elements of the ground / Paths
        
        perlin = PerlinNoise()
        
        offsetx = -self.width/2
        offsety = -200
        hw = self.width / self.nbSamples
        hh =  self.height / self.nbSamples

        into_x = False
        into_y = False
        
        for i in range (0, self.nbSamples):
            largy = 0
            for j in range (0, self.nbSamples):
                
                a1,b1 = floor(i * hw)+ offsetx  , floor(j * hh)  + offsety
                b1 = -b1
                a1 = -a1

                if ( (self.width/2) - 250 <  floor(i * hw) < (self.width/2) + 250 or (self.height/2) - 250 < floor(j * hw) < (self.height/2) + 250 ) :

                    # Note Down the first elts i and where the path starts
                    if not into_x and not into_y:
                        start_path_y = j
                        into_y = True
                    
                        

                    if ( (self.height/2) - 250 <  floor(j * hw) < (self.height/2) + 250 ) :
                        largy += 1
                        if((self.width/2) - 250 <  floor(i * hw) < (self.width/2) + 250):
                            if not into_x  :
                                start_path_x = i
                                into_x = True


                    self.dict_Path[(i, j)] = len(self.Vertices_Path)
                    #the Paths has an altitude of zero:
                    L = perlin.defineNormal(a1, b1)
                    self.Vertices_Path.append([a1/900 , 0 , b1/700])
                    self.Normals_Path.append([L[0], L[1], L[2] ])
                    self.Vertices_Ground.append([a1/900 , 0 , b1/700])
                    self.Normals_Ground.append([L[0], L[1], L[2] ])

                elif ( (floor(j * hw) < self.height/2 and floor(i * hw) < self.width/2) or (floor(j * hw) > self.height/2 and floor(i * hw) > self.width/2)  ):
                    self.build_top_left(i, j, hw, hh)
                
                else:
                    self.build_top_right(i, j, hw, hh)

        print("///////", start_path_x)

        # print(self.Vertices_Path)

        count = True
        m = 0
        k = 0
        # largy += 1
        #Order the Faces in their respective lists

        
        for i in range(1, self.nbSamples - 1):
            
            for j in range (1, self.nbSamples - 1):
                pt1,pt2 = i*self.nbSamples+j , i*self.nbSamples+j+1
                pt3, pt4= (i+1) * self.nbSamples + j, (i+1)*self.nbSamples+j+1

                height_cond = ((self.height/2) - 250 <  floor((j-1) * hh) < (self.height/2) + 250) 
                width_cond = (self.width/2) - 250 <  floor((i-1) * hw) < (self.width/2) + 250
                

                if height_cond and not width_cond and (j<largy + start_path_y - 1):
                    pt1_path = self.dict_Path[(i, j)]
                    pt2_path = self.dict_Path[(i, j+1)]
                    pt3_path = self.dict_Path[(i+1, j)]
                    pt4_path = self.dict_Path[(i+1, j+1)]

                   
                    
                    self.Faces_Path += [pt1_path, pt2_path, pt3_path, pt3_path, pt2_path, pt4_path] #, pt3_path, pt4_path, pt2_path

                   


                    

                elif ( width_cond) and (i<start_path_x+largy-1):

                    weeelll = 18
                    pt1_path = self.dict_Path[(i, j)]
                    pt2_path = self.dict_Path[(i, j+1)]
                    pt3_path = self.dict_Path[(i+1, j)]
                    pt4_path = self.dict_Path[(i+1, j+1)]
                    

                    self.Faces_Path += [pt1_path, pt2_path, pt3_path, pt3_path, pt2_path, pt4_path]
                else:
                    self.Faces_Ground += [pt1, pt2, pt3, pt3, pt2, pt4]

                cond = floor((j+1) * hh) >= (self.height/2) + 250 and floor((j-1) * hh) < (self.height/2) + 250
                if  cond or floor((i+1) * hw) >= (self.width/2) + 250 and floor((i-1) * hw) < (self.width/2) + 250 :
                    # if not width_cond or not height_cond:
                    self.Faces_Ground += [pt1, pt2, pt3, pt3, pt2, pt4]

                cond = floor((j+1) * hh) >=  (self.height/2) - 250 and floor((j-1) * hh) < (self.height/2) - 250
                if  cond or floor((i+1) * hw) >=  (self.width/2) - 250 and floor((i-1) * hw) < (self.width/2) - 250 :
                    # if not width_cond or not height_cond:
                    self.Faces_Ground += [pt1, pt2, pt3, pt3, pt2, pt4]
                
                




        #Transforming the lists to numpy arrays
        nVertices_Terrain = np.array(self.Vertices_Ground)
        nNormals_Terrain = np.array(self.Normals_Ground, dtype=np.float32)

        nVertices_Path = np.array(self.Vertices_Path)
        nNormals_Path = np.array(self.Normals_Path, dtype=np.float32)


        #Building The Meshes Of the ground and the paths
        mesh = Mesh(self.shaderTerrain, attributes=dict(position=nVertices_Terrain, color=nNormals_Terrain),
                   index=self.Faces_Ground)
        
        path = Mesh(self.shaderPath, attributes=dict(position= nVertices_Path, color=nNormals_Path),
                   index=self.Faces_Path)
        


        return mesh, path





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
        self.world_transform =  model @ self.transform   # TODO: compute model matrix
        for child in self.children:
            child.draw(model=self.world_transform, **other_uniforms)

    def key_handler(self, key):
        """ Dispatch keyboard events to children with key handler """
        for child in (c for c in self.children if hasattr(c, 'key_handler')):
            child.key_handler(key)

class Shroom (Node):
    """ Cute Imported Mushroom"""
    def __init__(self, shader):
        super().__init__()
        self.add(*load('mush.obj', shader, tex_file= "20951_Mushroom_Diffuse.jpg"))  # just load cylinder from file
        # self.add(*load('bunny.obj', shader, tex_file= "bunny.png"))


# -------------- main program and scene setup --------------------------------
def main():
    """ create window, add shaders & scene objects, then run rendering loop """
    viewer = Viewer()
    color_shader = Shader("color.vert", "color.frag")
    shroom_shader = Shader("shroom.vert", "shroom.frag")

    # place instances of our basic objects
    #viewer.add(Pyramid(color_shader))
    
    ss = Shroom(shroom_shader)
    mush = Node(transform = rotate((1,0,0), -90) @ scale(0.028, 0.028, 0.028) @ translate(2, 0, 0))
    mush.add(ss)
    viewer.add(mush)

    

    
    bumpyTerrain = Terrain(6000, 6000, color_shader, color_shader)
    #viewer.add(*load('SeaHorse.obj', color_shader))
    #viewer.add(bumpyTerrain.draw())

    wraps = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                            GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
    filters = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                              (GL.GL_LINEAR, GL.GL_LINEAR),
                              (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])

    wrap, filter = GL.GL_MIRRORED_REPEAT,  (GL.GL_LINEAR, GL.GL_LINEAR)
    file = "texture.jpg"

    texture = Texture("texture.jpg", wrap, *filter)
    texturePath = Texture("rocks.jpg", wrap, *filter)
    terrain = bumpyTerrain.draw()
    textured = Textured( terrain[0], diffuse_map=texture)
    texturedPath = Textured(terrain [1], diffuse_map=texturePath)
    viewer.add(textured)
    viewer.add(texturedPath)

    # viewer.add(*[mesh for mesh in load("shroom.obj", color_shader)])

    

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                  # main function keeps variables locally scoped



    

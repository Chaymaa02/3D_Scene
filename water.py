#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

from cmath import pi, sin
from distutils import text_file
from random import *
from math import cos, ceil, floor, sqrt
from syslog import LOG_LOCAL0
# from viewer import Viewer
import OpenGL.GL as GL             # standard Python OpenGL wrapper
import glfw                        # lean window system wrapper for OpenGL
import numpy as np                 # all matrix manipulations & OpenGL args
import noise
from texture import Texture, Textured
from transform import Trackball, identity, quaternion, rotate, scale, translate
from core import Node, Shader, Mesh, load
import assimpcy
from itertools import cycle


class Water(Node) :
    def __init__(self, width, height, shaderWater , transform):
        
        super().__init__()
        self.transform = transform
        self.texture = Texture("water.png", GL.GL_REPEAT, GL.GL_LINEAR)
        self.width = width
        self.height = height
        self.shader = shaderWater

    
    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        """ When redraw requested, interpolate our node transform from keys """

        self.nbSamples = 180
        self.Vertices_Water, self.Normals_Water, self.Faces_Water = [], [], []



        offsetx = -self.width/2 - 2000
        offsety = -200 + 550
        hw = self.width / self.nbSamples
        hh =  self.height / self.nbSamples
        waveLength = 1
        waveAmplitude = 0.08
        for i in range (0, self.nbSamples):
            for j in range (0, self.nbSamples):
                
                a1,b1 = floor(i * hw)+ offsetx  , floor(j * hh)  + offsety
                b1 = -b1
                a1 = -a1
                #the Paths has an altitude of zero:
                # L = perlin.defineNormal(a1, b1)
                x = a1/900
                z = b1/700 

                waveTime = glfw.get_time()
                radian_x = (x/waveLength + waveTime/2) * 2 * pi
                radian_z = (z/waveLength + waveTime/2) * 2 * pi
                offset = waveAmplitude*0.5*(sin(radian_z) + cos(radian_x))
                
                x += offset
                z  += offset
                y = offset

                self.Vertices_Water.append([x , y , z])
                # self.Normals_Path.append([L[0], L[1], L[2] ])
                # self.Vertices_Water.append([a1/900 , 0 , b1/700])
                # self.Normals_Ground.append([L[0], L[1], L[2] ])

        for i in range(1, self.nbSamples - 1):
            
            for j in range (1, self.nbSamples - 1):
                pt1,pt2 = i*self.nbSamples+j , i*self.nbSamples+j+1
                pt3, pt4= (i+1) * self.nbSamples + j, (i+1)*self.nbSamples+j+1
               
                self.Faces_Water += [pt1, pt2, pt3, pt3, pt2, pt4]


        nVertices_Water = np.array(self.Vertices_Water)
        # nNormals_Terrain = np.array(self.Normals_Ground, dtype=np.float32)


        #Building The Meshes Of the ground and the paths
        mesh = Mesh(self.shader, attributes=dict(position=nVertices_Water),
                   index=self.Faces_Water, uniforms= dict(global_color = (0,0,1)))
        self.children = list()
        self.add(mesh)
        
        # GL.glActiveTexture(GL.GL_TEXTURE0 + 0)
        GL.glBindTexture(self.texture.type, self.texture.glid)
        uniforms["diffuse_map"] = 0
        super().draw(primitives=primitives, **uniforms)



def main():
    pass
    # viewer = Viewer()
    # water_shader = Shader("water.vert", "water.frag")
    # water = Water(1000,1000,water_shader)
    # water_mesh = water.draw()
    # viewer.add(water_mesh)
    # viewer.run()

if __name__ == '__main__':
    main()  
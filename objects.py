import OpenGL.GL as GL
import glfw
from core import load, Node, Shader
from animation import TransformKeyFrames
from transform import vec, quaternion, quaternion_from_euler, translate, rotate, scale
from math import cos, sin


class Object(Node):
    def __init__(self, shader,  transform, file, tex_file, trans_keys, rot_keys, scale_keys, repeat=10):
        super().__init__()
        light_dir = (0, -1, 0)
        self.add(*load(file,shader,tex_file=tex_file ,light_dir=light_dir))
        self.rep = repeat
        self.keyframes = TransformKeyFrames(trans_keys, rot_keys, scale_keys)
        self.trans = transform

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        """ When redraw requested, interpolate our node transform from keys """
        self.transform =  self.keyframes.value(glfw.get_time()%self.rep) @ self.trans
        self.world_transform = self.transform
        for child in self.children:
             child.draw(model=self.world_transform)
        super().draw(primitives=primitives, **uniforms)



def add_butterfly(viewer, animate):
    z = -1
    x=-1
    trans_keys = {glfw.get_time(): vec(x-1, 0.5, z), glfw.get_time()+2: vec(x, 0.4, z), glfw.get_time()+4: vec(x+0.5, 0.5, z), glfw.get_time()+6: vec(x+1, 0.4, z-0.5),
     glfw.get_time()+8: vec(x+1.5, 0.5, z-1), glfw.get_time()+10: vec(x+2, 0.4, z-1.5), glfw.get_time()+12: vec(x+2.5, 0.5, z-2), glfw.get_time()+14: vec(x+3, 0.4, z-2.5)}
    rot_keys = {glfw.get_time(): quaternion()}
    scale_keys = {glfw.get_time(): 0.003, glfw.get_time()+2: 0.003, glfw.get_time()+5: 0.002, glfw.get_time()+8: 0.002 ,glfw.get_time()+10: 0.002 ,glfw.get_time()+12: 0}
    butterfly = Object(animate, translate(-0.5,0,0),'objects/Butterfly/butterfly3.FBX', 'objects/Butterfly/butterfly.png',trans_keys, rot_keys, scale_keys, 20)
    viewer.add(butterfly)

    z = -7
    x=2
    trans_keys = {glfw.get_time(): vec(x+1, 0.5, z), glfw.get_time()+2: vec(x, 0.4, z), glfw.get_time()+4: vec(x-0.5, 0.5, z), glfw.get_time()+6: vec(x-1, 0.4, z-0.5),
     glfw.get_time()+8: vec(x-1.5, 0.5, z-1), glfw.get_time()+10: vec(x-2, 0.4, z-1.5), glfw.get_time()+12: vec(x-2.5, 0.5, z-2), glfw.get_time()+14: vec(x-3, 0.4, z-2.5)}
    rot_keys = {glfw.get_time(): quaternion()}
    scale_keys = {glfw.get_time(): 0.003, glfw.get_time()+2: 0.003, glfw.get_time()+5: 0.002, glfw.get_time()+8: 0.002 ,glfw.get_time()+10: 0.002 ,glfw.get_time()+12: 0}
    butterfly = Object(animate, translate(-0.5,0,0),'objects/Butterfly/butterfly2.FBX', 'objects/Butterfly/butterfly.png', trans_keys, rot_keys, scale_keys, 20)
    viewer.add(butterfly)
    #................
    xb = -0.5
    yb=0.5
    zb=-1
    mush = load('objects/Butterfly/butterfly2.FBX', animate, 'objects/Butterfly/butterfly.png')
    b = Node (transform= translate(xb, yb, zb-0.1) @ rotate((0,1,0), -90) @ scale(0.003, 0.003, 0.003))
    b.add(*mush)
    b1 = Node (transform=translate(xb+0.1, yb-0.1, zb) @ rotate((0,1,0), 180) @ scale(0.003, 0.003, 0.003))
    b1.add(*mush)
    b2 = Node (transform=translate(xb-0.1, yb, zb) @ scale(0.003, 0.003, 0.003))
    b2.add(*mush)
    viewer.add(b, b1, b2)
    



class Seagul(Node):
    def __init__(self, transform, mush):
        super().__init__()
        self.transform = transform
        self.add(mush)
        z = -2.5
        x=-2
        y = 1
        trans_keys = {glfw.get_time(): vec(x-1, y, z), glfw.get_time()+2: vec(x, y+0.1, z), glfw.get_time()+4: vec(x+1, y, z), glfw.get_time()+6: vec(x+2, y+0.1, z-0.5), glfw.get_time()+8: vec(x+3, y, z-1), glfw.get_time()+10: vec(x+4, y+0.1, z-1.5)}
        rot_keys = {glfw.get_time()+8: quaternion(), glfw.get_time()+10: quaternion_from_euler(0, 0, 0),
                   glfw.get_time()+3: quaternion_from_euler(0, 0, 0), glfw.get_time()+4: quaternion()}
        scale_keys = {glfw.get_time(): 0.003, glfw.get_time()+2: 0.003, glfw.get_time()+5: 0.003, glfw.get_time()+8: 0.003 ,glfw.get_time()+10: 0.003 ,glfw.get_time()+12: 0}
        self.keyframes = TransformKeyFrames(trans_keys, rot_keys, scale_keys)
        self.trans = transform

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        """ When redraw requested, interpolate our node transform from keys """
        self.transform = self.trans @ self.keyframes.value(glfw.get_time()%30)
        self.world_transform = self.transform
        for child in self.children:
             child.draw(model=self.world_transform)
        super().draw(primitives=primitives, **uniforms)
    

class Wolf(Node):
    def __init__(self, shader, transform):
        super().__init__()
        self.transform = transform
        light_dir = (0, -1, 0)
        self.add(*load('objects/Wolf/Wolf.fbx'
        ,shader
        ,tex_file='objects/Wolf/Wolf_Body.jpg'
        ,light_dir=light_dir))



def add_fish(viewer, animate):
    x, y, z = (3,-0.3,-1.5)
    trans_keys = {glfw.get_time(): vec(x, y, z), glfw.get_time()+2: vec(x, y, z-0.5), glfw.get_time()+4: vec(x, y, z-1), glfw.get_time()+6: vec(x, y, z-1.5),
    glfw.get_time()+8: vec(x+0.2, y, z-2), glfw.get_time()+10: vec(x+0.2, y, z-2.5)}
    rot_keys = {glfw.get_time(): quaternion_from_euler(0, 180, 0), glfw.get_time()+2: quaternion_from_euler(0, 180, 0), glfw.get_time()+4: quaternion_from_euler(0,180, 0)
    ,glfw.get_time()+6: quaternion_from_euler(0, 160, 0), glfw.get_time()+8: quaternion_from_euler(0, 160, 0)}
    scale_keys = {glfw.get_time(): 0.0002, glfw.get_time()+2: 0.0002, glfw.get_time()+5: 0.0002, glfw.get_time()+8: 0.0002 ,glfw.get_time()+10: 0.0002 }
    fish1 = Object(animate, translate(0,0,0)
    , 'objects/Fish/ReefFish3/ReefFish3.fbx'
    , 'objects/Fish/ReefFish3/ReefFish3_Normal.png', trans_keys, rot_keys, scale_keys)
    x, y, z = (2.7,-0.2,-1.5)
    trans_keys = {glfw.get_time()+1: vec(x, y, z), glfw.get_time()+3: vec(x, y, z-0.5), glfw.get_time()+5: vec(x, y, z-1), glfw.get_time()+7: vec(x, y, z-1.5),
    glfw.get_time()+9: vec(x+0.2, y, z-2), glfw.get_time()+11: vec(x+0.2, y, z-2.5)}
    rot_keys = {glfw.get_time(): quaternion_from_euler(0, 180, 0), glfw.get_time()+2: quaternion_from_euler(0, 180, 0), glfw.get_time()+4: quaternion_from_euler(0,180, 0)
    ,glfw.get_time()+6: quaternion_from_euler(0, 200, 0), glfw.get_time()+8: quaternion_from_euler(0, 200, 0)}
    scale_keys = {glfw.get_time(): 0.0002, glfw.get_time()+2: 0.0002, glfw.get_time()+5: 0.0002, glfw.get_time()+8: 0.0002 ,glfw.get_time()+10: 0.0002 }
    fish2 = Object(animate, translate(0,0,0)
    ,'objects/Fish/ReefFish4/ReefFish4.fbx'
    , 'objects/Fish/ReefFish4/reefFish4_Base_Color.png', trans_keys, rot_keys, scale_keys)
    #######################
    x, y, z = (2,-0.4,-2)
    trans_keys = {glfw.get_time(): vec(x-0.5, y, z), glfw.get_time()+2: vec(x, y, z), glfw.get_time()+4: vec(x+0.5, y, z), glfw.get_time()+6: vec(x+1, y, z-0.5),
    glfw.get_time()+8: vec(x+1.5, y, z-0.5), glfw.get_time()+10: vec(x+2, y, z-1)}
    rot_keys = {glfw.get_time(): quaternion_from_euler(0, 90, 0), glfw.get_time()+2: quaternion_from_euler(0, 90, 0), glfw.get_time()+4: quaternion_from_euler(0,90, 0)
    ,glfw.get_time()+6: quaternion_from_euler(0, 100, 0), glfw.get_time()+8: quaternion_from_euler(0, 100, 0)}
    scale_keys = {glfw.get_time(): 0.0002, glfw.get_time()+2: 0.0002, glfw.get_time()+5: 0.0002, glfw.get_time()+8: 0.0002 ,glfw.get_time()+10: 0.0002 }
    fish3 = Object(animate,  translate(0,0,0)
    , 'objects/Fish/ReefFish5/ReefFish5.fbx'
    , 'objects/Fish/ReefFish5/ReefFish5_Base_Color.png', trans_keys, rot_keys, scale_keys) 
    x, y, z = (2,-0.5,-3.5) 
    trans_keys = {glfw.get_time()+1: vec(x-0.5, y, z), glfw.get_time()+3: vec(x, y, z), glfw.get_time()+5: vec(x+0.5, y, z), glfw.get_time()+7: vec(x+1, y, z-0.5),
    glfw.get_time()+9: vec(x+1.5, y, z-0.5), glfw.get_time()+11: vec(x+2, y, z-1)}
    rot_keys = {glfw.get_time(): quaternion_from_euler(0, 90, 0), glfw.get_time()+2: quaternion_from_euler(0, 90, 0), glfw.get_time()+4: quaternion_from_euler(0,90, 0)
    ,glfw.get_time()+6: quaternion_from_euler(0, 100, 0), glfw.get_time()+8: quaternion_from_euler(0, 100, 0)}
    scale_keys = {glfw.get_time(): 0.0002, glfw.get_time()+2: 0.0002, glfw.get_time()+5: 0.0002, glfw.get_time()+8: 0.0002 ,glfw.get_time()+10: 0.0002 }
    fish4 = Object(animate,  translate(0,0,0)
    , 'objects/Fish/ReefFish3/ReefFish3.fbx'
    , 'objects/Fish/ReefFish3/ReefFish3_Normal.png', trans_keys, rot_keys, scale_keys)
    ############################
    x, y, z = (2.3,-0.2,-1.3)
    trans_keys = {glfw.get_time(): vec(x-0.2, y, z), glfw.get_time()+1: vec(x, y+0.2, z-0.2), glfw.get_time()+2: vec(x+0.2, y+0.4, z-0.4),
    glfw.get_time()+3: vec(x+0.4, y+0.2, z-0.6), glfw.get_time()+4: vec(x+0.6, y, z-0.8), glfw.get_time()+6: vec(x+0.6, y-0.2, z-0.8)}
    rot_keys = {glfw.get_time(): quaternion_from_euler(0, 180, 0), glfw.get_time()+1: quaternion_from_euler(0, 110, 0), glfw.get_time()+3: quaternion_from_euler(0,110, 30)
    ,glfw.get_time()+4: quaternion_from_euler(0, 110, 50), glfw.get_time()+5: quaternion_from_euler(0, 110, 90), glfw.get_time()+6: quaternion_from_euler(0, 110, 90)}
    scale_keys = {glfw.get_time(): 0.0002, glfw.get_time()+2: 0.0002, glfw.get_time()+3: 0.0002, glfw.get_time()+7: 0.0002 ,glfw.get_time()+10: 0.0002}
    fish5 = Object(animate,  translate(0,0,0) 
    ,'objects/Fish/ReefFish4/ReefFish4.fbx'
    , 'objects/Fish/ReefFish4/reefFish4_Base_Color.png', trans_keys, rot_keys, scale_keys)
    x, y, z = (2.3,-0.2,-3.5)
    trans_keys = {glfw.get_time(): vec(x-0.2, y, z), glfw.get_time()+1: vec(x, y+0.2, z+0.2), glfw.get_time()+2: vec(x+0.2, y+0.4, z+0.4),
    glfw.get_time()+3: vec(x+0.4, y+0.2, z+0.6), glfw.get_time()+4: vec(x+0.6, y, z+0.8), glfw.get_time()+6: vec(x+0.6, y-0.2, z+0.8)}
    rot_keys = {glfw.get_time(): quaternion_from_euler(0, 180, 0), glfw.get_time()+1: quaternion_from_euler(0, 110, 0), glfw.get_time()+3: quaternion_from_euler(0,110, 30)
    ,glfw.get_time()+4: quaternion_from_euler(0, 110, 50), glfw.get_time()+5: quaternion_from_euler(0, 110, 90), glfw.get_time()+6: quaternion_from_euler(0, 110, 90)}
    scale_keys = {glfw.get_time(): 0.0002, glfw.get_time()+2: 0.0002, glfw.get_time()+3: 0.0002, glfw.get_time()+7: 0.0002 ,glfw.get_time()+10: 0.0002}
    fish6 = Object(animate, translate(0,0,0)
    , 'objects/Fish/ReefFish5/ReefFish5.fbx'
    , 'objects/Fish/ReefFish5/ReefFish5_Base_Color.png', trans_keys, rot_keys, scale_keys)
    viewer.add(fish1, fish2, fish3, fish4, fish5, fish6)


def add_boat(viewer, shader):
    x, y, z = -3,-0.16,-10
    trans_keys = {glfw.get_time()+1: vec(x, y+0.1, z), glfw.get_time()+2: vec(x+0.2, y, z),
    glfw.get_time()+3: vec(x+0.4, y+0.1, z), glfw.get_time()+4: vec(x+0.6, y, z), glfw.get_time()+5: vec(x+0.6, y+0.1, z)
    , glfw.get_time()+6: vec(x+0.6, y, z), glfw.get_time()+7: vec(x+0.4, y+0.1, z), glfw.get_time()+8: vec(x+0.2, y, z)
    , glfw.get_time()+9: vec(x, y+0.1, z), glfw.get_time()+10: vec(x-0.2, y, z), glfw.get_time()+11: vec(x-0.4, y+0.1, z)}
    rot_keys = {glfw.get_time(): quaternion()}
    scale_keys = {glfw.get_time(): 0.02}
    boat= Object(shader,  translate(0, 0, 0)
    ,'objects/Boats/Sloop.FBX'
    , 'objects/Boats/Ships 1.tga', trans_keys, rot_keys, scale_keys, 12)
    viewer.add(boat)

# -------------- add objects -------------
    # add_butterfly(viewer, animate)
    
    # s = Seagul(animate, translate(0, 0, 0))
    # s1 = Seagul(animate, translate(-0.1, 0.2, 0))
    # s2 = Seagul(animate, translate(0.2, -0.1, 0))
    # s.add(s1, s2)
    # viewer.add(s)
    # viewer.add(Wolf(animate, transform= translate(-0.7, 0, -1.75) @ rotate((0,1,0), -90) @ scale(0.003, 0.003, 0.003)))
    # add_fish(viewer, animate)

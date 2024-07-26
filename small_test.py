import bpy
import blender_blob_utils
import setup_scene
import mathutils
import bmesh
import math

def get_outward_direction(v: bmesh.types.BMVert):
    nextV = v.link_edges[1].other_vert(v)
    preV = v.link_edges[0].other_vert(v)
    
    if(v.index == 0):
        nextV, preV = preV, nextV

    n = mathutils.Vector((nextV.co.x - v.co.x, nextV.co.y - v.co.y))
    p = mathutils.Vector((preV.co.x - v.co.x, preV.co.y - v.co.y))
    a = n.angle_signed(p)
    #I want half a rotation clockwize. With a signed angle we have two cases. 
    if(a<0):
        a+=math.tau #trust me
    matrix = mathutils.Matrix.Rotation(-a/2, 2)
    n.rotate(matrix) #should rotate clockwise, now N stands for normals and not next ;-)
    n.length = v.link_edges[0].calc_length()/2
    return n.normalized()

    

def main():

    b = bpy.data.objects["Circle"]
    for obj in bpy.data.objects:
        if (obj.name == "Circle"):
            continue
        bpy.data.objects.remove(object=obj)
    bm = blender_blob_utils.bmesh_from_blob(b)
    for v in bm.verts:
        n = get_outward_direction(v)
        n.length = 0.1
        x = v.co.x + n.x
        y = v.co.y + n.y
        z = v.co.z
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z), size=0.01)
    bm.free()

    print("test finish")


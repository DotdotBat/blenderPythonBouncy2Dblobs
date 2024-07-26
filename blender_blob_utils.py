import bpy
import random
import bmesh
from blob import Blob as SimulationBlob

def move_object_to_collection(obj: bpy.types.Object, col: bpy.types.Collection):
    """Removes the object from all current collections and puts it in a the specified collection"""
    current_collection_list = obj.users_collection
    
    for prev_col in current_collection_list:
        prev_col.objects.unlink(obj)

    col.objects.link(object=obj)

def add_blob_at(x, y, z, r, vert_number):
    bpy.ops.mesh.primitive_circle_add(radius=r, location=(x,y,z), vertices=vert_number)
    blob = bpy.context.object
    blob_collection = bpy.data.collections["Blobs"]
    move_object_to_collection(blob, blob_collection)
    blob.show_in_front = True #The base is exactly on the same z level, since it's filled, the curve will be better visible with this property
    return blob

# def get_chain_distance_between_verticies_from_indexes(index1, index2):
#     edges_num_on_inner_arc = abs(index1 - index2) #clockwise
#     total_edges_num = goals.active_goal.blob_vert_number
#     edges_num_on_outher_arc = total_edges_num - edges_num_on_inner_arc
#     edges_num = min(edges_num_on_inner_arc, edges_num_on_outher_arc)
#     link_length = goals.active_goal.link_length
#     chain_length = edges_num*link_length
#     return chain_length


def remove_random_blob():
    blobs_list = bpy.data.collections["Blobs"].objects
    random_blob = random.choice(blobs_list)
    bpy.data.objects.remove(object=random_blob)

   
def get_blobs_number():
    return len(bpy.data.collections["Blobs"].objects)

def bmesh_from_blob(blob:bpy.types.Object):
    bm1 = bmesh.new()
    bm1.from_mesh(blob.data)
    bm1.verts.ensure_lookup_table()
    bm1.edges.ensure_lookup_table()
    return bm1

def get_blob_area(blob:bpy.types.Object):
    bm1 = bmesh_from_blob(blob=blob)
    bmesh.ops.triangle_fill(bm1,edges=bm1.edges)
    area = 0.0
    for face in bm1.faces:
        area += face.calc_area() 
    bm1.free()
    return area

# def add_point_to_blob(blob:bpy.types.Object):
#     bm = bmesh_from_blob(blob)
#     bm.verts.ensure_lookup_table()
#     bm.edges.ensure_lookup_table()
#     edge = bm.edges[-1]

#     vert = edge.verts[0]
#     new_edge, new_vert = bmesh.utils.edge_split(edge, vert, 0.5)
#     new_edge.index = edge.index+1
#     new_vert.index = vert.index+1
#     bm.to_mesh(blob.data)
#     bm.free()


# def remove_point_from_blob(blob:bpy.types.Object):
#     bm = bmesh_from_blob(blob)
#     bm.verts.ensure_lookup_table()
#     vert = bm.verts[-1]
#     bmesh.utils.vert_dissolve(vert)
#     bm.to_mesh(blob.data)
#     bm.free()

# def get_circumference(blob: bpy.types.Object):
#     bm1 = bmesh_from_blob(blob=blob)
#     sum = 0.0
#     for edge in bm1.edges:
#         sum += edge.calc_length() 
#     bm1.free()
#     return sum

# def get_outward_direction(v: bmesh.types.BMVert):
#     nextV = v.link_edges[1].other_vert(v)
#     preV = v.link_edges[0].other_vert(v)
    
#     if(v.index == 0):
#         nextV, preV = preV, nextV

#     n = mathutils.Vector((nextV.co.x - v.co.x, nextV.co.y - v.co.y))
#     p = mathutils.Vector((preV.co.x - v.co.x, preV.co.y - v.co.y))
#     a = n.angle_signed(p)
#     #I want half a rotation clockwize. With a signed angle we have two cases. 
#     if(a<0):
#         a+=math.tau #trust me
#     matrix = mathutils.Matrix.Rotation(-a/2, 2)
#     n.rotate(matrix) #should rotate clockwise, now N stands for normals and not next ;-)
#     n.length = v.link_edges[0].calc_length()/2
#     return n.normalized()

def update_verts_pos(blob:bpy.types.Object, vert_positions):
    #particles have an x and y coordinate
    bm = bmesh_from_blob(blob)
    bm.verts.ensure_lookup_table()
    for index, v in enumerate(bm.verts):
        new_position = vert_positions[index]
        v.co.x , v.co.y = new_position.x, new_position.y
    bm.to_mesh(blob.data)
    bm.free()


def place_blob_mesh(blob:SimulationBlob):
    obj = add_blob_at(0, 0, 0, blob.radius, len(blob.particles))
    blob.blender_object = obj
    blob.update_mesh()




def convert_to_blender_coordinates(x, y):
    #should be based on the base object bound box but as a quick and dirty solution lets leave it at that. 
    #p5 coordinates are in pixels, and blender coordinates are in meters. 
    z = 0 
    # x/= 1000
    # y/= 1000
    return x, y, z

def to_p5_coord(x, y):
    return x, y

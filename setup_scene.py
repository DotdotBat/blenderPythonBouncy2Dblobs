import bpy
import random
from blender_blob_utils import add_blob_at as add_blob_to_blender
from typing import Callable


def ensure_base_object_exists():
    if "Base" not in bpy.data.objects or bpy.data.objects.__len__==0:
        print("did not found a base object, So I am creating a subdivided plane and calling it \"Base\"")
        
        set_root_collection_as_active() 
        bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0), scale=(1, 1, 1))
        plane = bpy.context.active_object
        plane.name = "Base"
        # To not make the code dependant on square planes we will change the shape a bit.
        # modifier = plane.modifiers.new(name="Subdivision", type="SUBSURF")
        # bpy.ops.object.modifier_apply(modifier="Subdivision")
    return bpy.data.objects["Base"]

def create_blob_collection():
    blob_collection = bpy.data.collections.new(name="Blobs")
    # the new collection is created in the blender file, 
    # but to see it in the outliner we have to link it to the scene collection
    scene_collection = bpy.context.scene.collection
    scene_collection.children.link(blob_collection)
    return blob_collection

def insure_blob_collection_exists():
    if "Blobs" not in bpy.data.collections:
        print("Did not found the blob collection, so I am adding it")
        blobs = create_blob_collection()
    return bpy.data.collections["Blobs"]


def point_is_within_base_shape(x:float, y:float, z:float, base_shape:bpy.types.Object):
    """check that point is on mesh of a horizontal shaped plane"""
    precision_error_tolerance = 0.005; # seems reasonable to me, the simulation will push the blob in if it is off shape
    success_bool, on_mesh_point, normal_vector, face_index = base_shape.closest_point_on_mesh([x, y ,z])
    p = on_mesh_point
    distance_to_mesh = abs(p.x -x) + abs(p.y-y) + abs(p.z-z)
    point_is_on_mesh = (distance_to_mesh < precision_error_tolerance)
    return point_is_on_mesh 




def pick_random_location_within_simple_bound_box(box:dict):
    """assumes the bound box was created with get_simple_bound_box"""
    x = random.uniform(box["x1"], box["x2"])
    y = random.uniform(box["y1"], box["y2"])
    z = box["z"]
    return x, y, z

def get_random_location_on_mesh(base:bpy.types.Object):
    bound_box = get_simple_bound_box(base)
    attempts_num = 10
    for _ in range(attempts_num):#try multiple times
        x, y, z = pick_random_location_within_simple_bound_box(bound_box)
        if(point_is_within_base_shape(x, y, z, base)):
            return x,y,z
    #here only if we did not succeed after all the attempts
    print("Random location pick failed ", attempts_num, "times. Using closest point method")
    x, y, z = pick_random_location_within_simple_bound_box(bound_box)
    success_bool, on_mesh_point, normal_vector, face_index = base.closest_point_on_mesh([x, y ,z])
    x, y, z = on_mesh_point.x, on_mesh_point.y, on_mesh_point.z
    return x, y, z


# outdated
# def distribute_blobs_on(plane_shape: bpy.types.Object, blobs_num:int):
#     """distribute blobs on the base object"""
#     base = bpy.data.objects["Base"]
#     for _ in range(blobs_num):
#         x, y, z = get_random_location_on_mesh(base)
#         add_blob_to_blender(x, y, z) #doesn't generate blob in the simulation, so it will just stand there, doing nothing
        
    
 
def get_simple_bound_box(flat_horizontal_object: bpy.types.Object):
    """Creates an object with properties z, x1, y1, x2, y2, width, and height."""
    box = flat_horizontal_object.bound_box
    assert box[0][2] == box[6][2], "The base object is not a flat horizontal mesh"
    
    # Define a class to hold the bounding box properties
    class BoundingBox:
        def __init__(self, z, x1, y1, x2, y2):
            self.z = z
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.width = x2 - x1
            self.height = y2 - y1
    
    # Instantiate the BoundingBox class with the appropriate values
    bounding_box = BoundingBox(
        z=box[0][2],
        x1=box[0][0],
        x2=box[6][0],
        y1=box[0][1],
        y2=box[6][1]
    )
    
    return bounding_box


def run_function_every_frame(func: Callable):
    """Will be called at the start of every frame with the current Scene as an argument - func(scene) """
    bpy.app.handlers.frame_change_pre.append(func)


def set_root_collection_as_active():
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection

def empty_collection(col: bpy.types.Collection):
    for obj in col.objects:
        bpy.data.objects.remove(object=obj)
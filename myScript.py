import bpy
import time

import scipy.datasets
import scipy.stats
import scipy.version
import simulation
import geometry_utils


#my modules
from setup_scene import ensure_base_object_exists, insure_blob_collection_exists, run_function_every_frame, get_simple_bound_box, empty_collection
import scipy
from scipy.stats import qmc as quasi_monte_carlo

import gpu
import numpy as np
def init__main():

    makeMeTrue = False;
    333333333333333333333333333333333333333333333333333333333
    num_vertices = 1000
    vertices = np.zeros((num_vertices, 6), dtype=np.float32)  # x, y, z, vx, vy, vz
    # Example initialization (replace with actual initial conditions)
    vertices[:, :3] = np.random.rand(num_vertices, 3) * 10 - 5  # Random positions in [-5, 5]
    vertices[:, 3:] = np.zeros((num_vertices, 3))  # Zero initial velocities

    vertices[0][0] = int(makeMeTrue)


    makeMeTrue = bool(vertices[0][0])
    333333333333333333333333333333333333333333333333333333333
    print("current variable content: ", makeMeTrue)
    if makeMeTrue:
        print("Success!! You have the gpu flipped a bool")
    else:
        print("try again")
    


    return
    start_time = time.time()
    base = ensure_base_object_exists()
    blobs_collection = insure_blob_collection_exists()
    bound_box = get_simple_bound_box(base)
    empty_collection(blobs_collection)
    simulation.bottomBorderY = bound_box.y1
    simulation.topBorderY = bound_box.y2
    simulation.leftBorderX = bound_box.x1
    simulation.rightBorderX = bound_box.x2


    simulation.setup()
    for _ in range (16):
        simulation.update(bpy.context.scene, None)


    # bpy.app.handlers.frame_change_pre.clear()
    # run_function_every_frame(simulation.simulate_on_frame)
    bpy.app.handlers.frame_change_pre.clear()
    run_function_every_frame(simulation.update)
    print("Setup finished in", round(1000* (time.time()-start_time), 2), "milliseconds")
    
    
    









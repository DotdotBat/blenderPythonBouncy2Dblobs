import bpy
import sys
import os
import importlib

filepath = bpy.data.filepath

dir = os.path.dirname(filepath)

if not dir in sys.path:
   sys.path.append(dir )


import setup_scene
import joint
import hash_grid
import particle
import geometry_utils
import blender_blob_utils
import blob
import simulation
import myScript
import shapely



bpy.app.handlers.frame_change_pre.clear();#because I keep forgetting to add it when I try to quickly test something out. 

#here the order matters. go from leaf to root

importlib.reload(hash_grid)
importlib.reload(particle)
importlib.reload(joint)
importlib.reload(geometry_utils)
importlib.reload(blender_blob_utils)
importlib.reload(setup_scene)
importlib.reload(blob)
importlib.reload(simulation)
importlib.reload(myScript)



myScript.init__main()

# import cProfile
# cProfile.run("import bpy; myScript.init__main()", "blender.prof")

# import pstats
# p = pstats.Stats("blender.prof")
# p.sort_stats("cumulative").print_stats(20)
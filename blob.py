import shapely
from particle import Particle, ChainableParticle, Coordinate2D
from joint import DistanceJoint
import random
import bpy
import blender_blob_utils
import math
import geometry_utils
from shapely import Polygon


class Blob:
    def __init__(self, area, current_area, root_particle, particles, joints, radius):
        self.area = area
        self.current_area = current_area
        self.area_diff = 0
        self.root_particle:Particle = root_particle
        self.particles:list[ChainableParticle] = particles
        self.joints:list[DistanceJoint] = joints
        self.radius = radius
        self.update()
        
    blender_object: bpy.types.Object = None
    shapely_polygon: Polygon = None

    def update(self):
        #set new polygon
        verts = [(v.x, v.y) for v in self.particles]
        self.shapely_polygon = Polygon(shell=verts)
        self.current_area = self.shapely_polygon.area
        self.area_diff = self.area - self.current_area
        #recalculate area related stuff
        

    def update_mesh(self):
        vert_positions = [Coordinate2D(p.x, p.y) for p in self.particles]
        c = vert_positions.copy()
        for index, vp in enumerate(vert_positions):
            c[index].x, c[index].y, z = blender_blob_utils.convert_to_blender_coordinates(vp.x, vp.y)
        blender_blob_utils.update_verts_pos(self.blender_object, c)

    @property
    def area_diff(self):
        return self._area_diff

    @area_diff.setter
    def area_diff(self, value):
        self._area_diff = value

def generate_blob(offset_x, offset_y, radius, effective_vertex_distance, hash_grid):
    num_points = math.floor((radius * math.pi * 2) / effective_vertex_distance)
    vertices = [
        ChainableParticle(
          x=math.cos(i / num_points * 2 * math.pi) * radius + offset_x,
          y=math.sin(i / num_points * 2 * math.pi) * radius + offset_y,
          z=0,
          radius=effective_vertex_distance,
          damping=0.9,
          friction=0.1,
          mass=1,
          index=i
        ) for i in range(num_points)
    ]

    root_particle = vertices[0]
    root_particle.set_is_root(True)
    

    for particle in vertices:
        particle.set_client(hash_grid.create_client(particle))

    joints = []
    for v in vertices:
        i = v.index
        i1 = (i+1)%len(vertices)
        i2 = (i+2)%len(vertices)
        i3 = (i+3)%len(vertices)
        v1 = vertices[i1]
        v2 = vertices[i2]
        v3 = vertices[i3]
        joints.append(DistanceJoint(v, v1, effective_vertex_distance * 1, 0.9))
        joints.append(DistanceJoint(v, v2, effective_vertex_distance * 2.5, 0.7))
        joints.append(DistanceJoint(v, v3, effective_vertex_distance * 4, 0.1))
        
    area = geometry_utils.polygon_area(vertices) * random.uniform(0.6, 0.9)
    blob = Blob(area, area, root_particle, vertices, joints, radius)

    for particle in blob.particles:
        particle.parent = blob

    for particle in blob.particles:
        particle.set_immediate_siblings()

    return blob



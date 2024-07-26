import scipy.interpolate
from hash_grid import HashGrid
from blob import Blob, generate_blob
from particle import ChainableParticle, Coordinate2D
import math
import random
import geometry_utils
import blender_blob_utils
from dataclasses import dataclass
import scipy

max_vertex_count = 300  # Increase to get more blobs. Not really a max but more of a guideline for the setup :)
substeps = 16  # How many physics steps per frame
max_radius = 0.3  # relative to min canvas length [min(width, height)]
min_radius = 0.07  # relative to min canvas length [min(width, height)]
min_thickness_multiplier = 0.05
vertex_distance = 0.02  # How far apart are the vertices (relative to min canvas length) (smaller number == more cpu work)

@dataclass
class Controller():
    area:float
    circumference_multiplier: float


# mx = 0
# my = 0
blobs: list[Blob] = []
particles: list[ChainableParticle] = []
distance_joints: list[Blob]= []
hash_grid : HashGrid = None
goal : Controller = None
effective_vertex_distance = 0
min_thickness = 0


#borders 
leftBorderX = -500
rightBorderX = 500
topBorderY = 500
bottomBorderY = -500

def setup():
    global min_thickness, blobs, particles, distance_joints, hash_grid, effective_vertex_distance, goal
    width = rightBorderX - leftBorderX
    height = topBorderY - bottomBorderY
    #get base object boundary
    min_length = min(width, height)
    #calculate radius of blobs
    spacing = min_length * (max_radius )
    poisson_radius =spacing/max(width, height)
    #fill a unit square with poisson disk sampling
    spaced_points = geometry_utils.get_unit_square_poisson_distribution(poisson_radius)
    #translate the points to base object
    
    for p in spaced_points:
        p[0] = lerp(leftBorderX, rightBorderX, p[0])
        p[1] = lerp(bottomBorderY, topBorderY,p[1])
    # random.shuffle(spaced_points)
    print(spaced_points)
    if len(spaced_points) < 5:
        raise Warning("The poisson disk distribution is rather short", spaced_points)

    
    effective_vertex_distance = vertex_distance * min_length 
    hash_grid = HashGrid(topY=topBorderY, rightX=rightBorderX, bottomY=bottomBorderY, leftX=leftBorderX, cell_size=effective_vertex_distance * 2)
    particles = []
    distance_joints = []
    blobs= []
    min_thickness = min_length*min_thickness_multiplier
    total_area = 0
    max_area = (width) * (height) * 0.8

    point_picker_index = 0
    while total_area < max_area and len(particles) < max_vertex_count and point_picker_index < len(spaced_points):
        radius_limit = (max_area - total_area) / (math.pi * 2)
        radius = min(radius_limit, (random.random() ** 3 * (max_radius - min_radius) + min_radius) * min_length)
        x = spaced_points[point_picker_index][0]
        y = spaced_points[point_picker_index][1]
        point_picker_index +=1
        blob = generate_blob(offset_y=y, offset_x=x, radius=radius, effective_vertex_distance=effective_vertex_distance, hash_grid=hash_grid)
        blender_blob_utils.place_blob_mesh(blob)
        total_area += blob.area
        blobs.append(blob)
        particles.extend(blob.particles)
        distance_joints.extend(blob.joints)
    
    #jiggle the blobs a bit
    for particle in particles:
        angle = random.uniform(0, math.tau)
        # random unit vector
        x = math.sin(angle)
        y = math.cos(angle)
        magnitude = random.uniform(0, effective_vertex_distance/4)
        x *= magnitude
        y *= magnitude
        particle.move(x, y)
    particle_validity_check()
    
def check_NaN_or_inf(n):
    if math.isnan(n) or math.isinf(n) or n>10 or n < -10:
        raise ValueError("This should be a float: ", n)
    

def particle_validity_check():
    global particles
    for p in particles:
        check_NaN_or_inf(p.x)
        check_NaN_or_inf(p.y)



def update_hashgrid_clients_of_particles():
    for particle in particles:
        particle.update_client()

def apply_gravity_to_all_particles(dt):
    for particle in particles:
            particle.add_force(0, -0.0001)

def apply_smoothing_offset_to_all_particles(dt):
    
    for p in particles:
        ns = p.next_sibling
        ps = p.prev_sibling
        middleX = ns.x/2 + ps.x/2
        middleY = ns.y/2 + ps.y/2
        offsetX = middleX - p.x
        offsetY = middleY - p.y
        offsetX*=dt
        offsetY*=dt
        p.add_offset(offsetX, offsetY)

def apply_blob_volume_corrections_to_particles(dt):
    for v in particles:
        v0 = v.prev_sibling
        v1 = v.next_sibling
        line_normal = geometry_utils.get_line_normal(v0.x, v0.y, v1.x, v1.y)
        circumference = v.parent.radius*math.tau
        dir = v.parent.area_diff/circumference
        check_NaN_or_inf(dir)
        check_NaN_or_inf(line_normal.x)
        dir *= dt
        
        v.add_offset(line_normal.x * dir, line_normal.y * dir)

def update_distance_joints(dt):
    for joint in distance_joints:
        joint.update(dt)

def apply_inner_collision(dt):
    for particle in particles:
        radius = min_thickness
        nearby_particles = hash_grid.query(particle.x, particle.y, radius)
        for other in nearby_particles:
            if particle.parent != other.parent or particle == other:
                continue
            closeness = particle.chain_distance(other)
            radius = min_thickness
            if closeness < 4:
                radius = min_thickness*closeness/4
            handle_collision(particle, other, radius, dt)

def constrain_particles_within_base_shape():
    for particle in particles:
        particle.constrain( left=   leftBorderX,
                            top=    topBorderY,
                            right=  rightBorderX, 
                            bottom= bottomBorderY)

def apply_accumulated_offset_to_particles():
    for particle in particles:
        particle.apply_accumulated_offset()

def damp_speed_of_particles(dt):
    for particle in particles:
        particle.damp_speed(dt)

def add_intertia_as_offset(dt):
    for particle in particles:
        particle.move_with_inertia(dt)

def show_changes_in_blender():
    for blob in blobs:
        blob.update_mesh()

def collide_blobs(dt):
    for blob in blobs:
        #todo: find near blobs
        nearby_blobs = blobs.copy() #just for now 
        nearby_blobs.remove(blob)
        for other in nearby_blobs:
            if geometry_utils.are_blobs_touching(blob, other):
                offset_list = geometry_utils.get_collision_handling_offsets(blob, other)
                for (index, x, y) in offset_list:
                    x, y = x/2, y/2
                    x, y = x*dt, y*dt
                    if index<0 or index > len(blob.particles)-1:
                        raise ValueError(index, x, y)
                    blob.particles[index].add_offset(x, y)

        



def update(scene, second_argument):
    frame_number = scene.frame_current
    dt = 1 / 64
    sdt = dt / substeps
    update_hashgrid_clients_of_particles()
    for substep in range(substeps):
        apply_gravity_to_all_particles(sdt)
        apply_smoothing_offset_to_all_particles(sdt)
        apply_blob_volume_corrections_to_particles(sdt)
        update_distance_joints(sdt)
        collide_blobs(sdt)

        add_intertia_as_offset(sdt)
        apply_accumulated_offset_to_particles()
        constrain_particles_within_base_shape()
        damp_speed_of_particles(sdt)
        # particle_validity_check()  
        for blob in blobs:
            blob.update()  
    show_changes_in_blender()
 


def handle_collision(particle:ChainableParticle, other:ChainableParticle, radius, dt):    
    force = particle.test_collision(other.x, other.y, radius)
    if force:
        particle.add_offset(force.x * 0.5 * dt, force.y * 0.5 * dt)
        other.add_offset(-force.x * 0.5 * dt, -force.y * 0.5 * dt)



def lerp(start, end, amount):
    return start + (end - start) * amount
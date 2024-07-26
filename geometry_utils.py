import math
from particle import Coordinate2D
import shapely
from shapely.geometry import Polygon, Point
from shapely.ops import nearest_points



EPSILON = 0.00001

def get_line_normal(x1, y1, x2, y2):
    x = (y2 - y1)
    y = -(x2 - x1)
    return Coordinate2D(x, y)
    

def normalize(coord:Coordinate2D):
    mag = math.sqrt(coord.x * coord.x + coord.y * coord.y)
    if mag > EPSILON:
        x = coord.x/mag
        y = coord.y/mag
        return Coordinate2D(x,y)
    
    return Coordinate2D(0, 0)

def limit(coord:Coordinate2D, max_length):
    if not coord:
        return None
    mag = math.sqrt(coord.x * coord.x + coord.y * coord.y)
    if mag > max_length:
        normal = normalize(coord)
        return Coordinate2D(coord.x * max_length, coord.y * max_length)
    return coord

def rotate(x, y, rot):
    return Coordinate2D(
        x * math.cos(rot) - y * math.sin(rot),
        x * math.sin(rot) + y * math.cos(rot)
    ) 

def polygon_from_blob(blob):
    return blob.shapely_polygon
    
    return p

def blob_area(blob):
    p = polygon_from_blob(blob)
    return p.area

def polygon_area(particles):
    verts = [(v.x, v.y) for v in particles]
    points = shapely.points(coords=verts)
    p = Polygon(verts)
    return p.area

def are_blobs_touching(blob, other):
    p1 = polygon_from_blob(blob)
    p2 = polygon_from_blob(other)
    return p1.overlaps(p2)
    


def get_collision_handling_offsets(blob, other):
    """returns a list of tuples [(point_index, escape_offset_x, y)]"""
    results = []
    check_poly = polygon_from_blob(other)

    # Iterate over the exterior coordinates of the first polygon
    for index, point_coord in enumerate(blob.particles):
        shapely_point = Point((point_coord.x, point_coord.y))

        # Check if the point is within the other polygon
        if shapely_point.within(check_poly):
            # Find the nearest point on the boundary of the second polygon using nearest_points
            _, nearest_boundary_point = nearest_points(shapely_point,
                                                       check_poly.boundary)

            # Calculate the vector difference between the inside point and the nearest boundary point
            dx = nearest_boundary_point.x - shapely_point.x
            dy = nearest_boundary_point.y - shapely_point.y

            # Append a tuple with the point index and escape vector components
            results.append((index, dx, dy))

    # if not results:
    #     raise Warning("An expensive function was called to calculate escape points where none exist", results)
    return results

from numpy.random import default_rng as numpy_random_engine
from scipy.stats import qmc as quasi_monte_carlo

def get_unit_square_poisson_distribution(radius):
    random_generator = numpy_random_engine()
    poisson_engine = quasi_monte_carlo.PoissonDisk(d=2, radius=radius, seed=random_generator)
    sample = poisson_engine.fill_space()
    return sample
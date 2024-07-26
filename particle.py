
import math
# from blob import Blob

class Coordinate2D:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y

    def __str__(self):
        return f'2D point at ({self.x},{self.y})'



class Particle(Coordinate2D):
    def __init__(self, x, y, z=0.0, radius=10, damping=0.9, friction=0.1, mass=1, parent=None, index = -1):
        super().__init__(x, y)
        self.index = index
        self.prevX = x
        self.prevY = y
        self.offsetX = 0
        self.offsetY = 0
        self.vx = 0
        self.vy = 0
        self.radius = radius
        self.damping = damping
        self.friction = friction
        self.mass = mass
        self.parent = parent
        self.client = None


    def set_client(self, client):
        self.client = client

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def add_force(self, fx, fy):
        self.vx += fx
        self.vy += fy

    def add_offset(self, dx, dy):
        self.offsetX += dx
        self.offsetY += dy

    def apply_accumulated_offset(self):
        self.x += self.offsetX
        self.y += self.offsetY

    def attract(self, otherX, otherY, strength=1):
        diffx = otherX - self.x
        diffy = otherY - self.y
        mag = diffx * diffx + diffy * diffy
        if mag > 0.1:
            magSqrt = 1 / math.sqrt(mag)
            self.add_force(diffx * magSqrt * strength, diffy * magSqrt * strength)

    def repel(self, otherX, otherY, radius=1, strength=1):
        diffx = self.x - otherX
        diffy = self.y - otherY
        mag = diffx * diffx + diffy * diffy
        combinedRadius = radius + self.radius
        minDist = combinedRadius * combinedRadius
        if mag > 0 and mag < minDist:
            magSqrt = 1 / math.sqrt(mag)
            forceX = diffx * magSqrt * strength
            forceY = diffy * magSqrt * strength
            self.add_force(forceX, forceY)
            return Coordinate2D(forceX, forceY)
        return None

    def test_collision(self, otherX, otherY, radius):
        diffx = otherX - self.x
        diffy = otherY - self.y
        diffMag = diffx * diffx + diffy * diffy
        if diffMag < 0.0001:
            return None
        
        combinedRadius = radius + self.radius
        if diffMag > combinedRadius ** 2:
            return None
    
        forceMag = math.sqrt(diffMag) - combinedRadius
        invMag = 1 / diffMag
        fx = diffx * invMag * forceMag
        fy = diffy * invMag * forceMag
        return Coordinate2D(fx, fy)
    

    def collide(self, otherX, otherY, radius):
        diffx = otherX - self.x
        diffy = otherY - self.y
        diffMag = diffx * diffx + diffy * diffy
        combinedRadius = radius + self.radius
        if diffMag < combinedRadius ** 2:
            forceMag = math.sqrt(diffMag) - combinedRadius
            invMag = 1 / diffMag
            fx = diffx * invMag * forceMag
            fy = diffy * invMag * forceMag
            self.move(fx, fy)
            self.prevX = self.lerp(self.prevX, self.x, self.friction)
            self.prevY = self.lerp(self.prevY, self.y, self.friction)
            return Coordinate2D(fx, fy)
        return None
    def __str__(self):
        return super().__str__()

    def constrain(self, left, top, right, bottom):
        left += self.radius
        top -= self.radius
        right -= self.radius
        bottom += self.radius
        collide = False
        if self.x > right:
            self.x = right
            collide = True
        elif self.x < left:
            self.x = left
            collide = True
        if self.y < bottom:
            self.y = bottom
            collide = True
        elif self.y > top:
            self.y = top
            collide = True
        if collide:
            self.prevX = self.lerp(self.prevX, self.x, self.friction)
            self.prevY = self.lerp(self.prevY, self.y, self.friction)

    def get_velocity(self):
        return Coordinate2D(self.vx, self.vy)

    def get_velocity_mag(self):
        return math.sqrt(self.vx * self.vx + self.vy * self.vy)

    def move_with_inertia(self, dt=1):
        self.prevX = self.x
        self.prevY = self.y
        self.add_offset(self.vx * dt, self.vy * dt)
    
    def chain_distance(self, other):
        if self.parent != other.parent:
            return math.inf
        one_dir = abs(self.index - other.index)
        total_points_num = len(self.parent.particles)
        second_dir = total_points_num - one_dir
        return min(one_dir, second_dir)

    def damp_speed(self, dt=1):
        m = self.damping * dt
        self.vx = (self.x + self.offsetX - self.prevX) * m
        self.vy = (self.y + self.offsetY - self.prevY) * m

    def update_client(self):
        if self.client:
            self.client.update()

    @staticmethod
    def lerp(start, end, amount):
        return start + (end - start) * amount


class ChainableParticle(Particle):
    
    def set_is_root(self, is_root):
        self.is_root = is_root
    
    def set_immediate_siblings(self):
        p = self.get_neighbor_by_index_offset(-1)
        self.set_prev_sibling(p)

        n = self.get_neighbor_by_index_offset(1)
        self.set_next_sibling(n)


    def set_next_sibling(self, sibling):
        self.next_sibling = sibling

    def set_prev_sibling(self, sibling):
        self.prev_sibling = sibling

    def get_neighbor_by_index_offset(self, index_offset:int):
        particles = self.parent.particles
        neighbor_index = self.index + index_offset
        # in case we are out of range, and yes I have checked that modulo wraps around negative numbers. 
        neighbor_index = neighbor_index % len(particles) 
        return particles[neighbor_index]

    def __str__(self):
        return super().__str__()
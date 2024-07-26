import math
from particle import Particle

class DistanceJoint:
    def __init__(self, pointA, pointB, length, strength):
        self.pointA:Particle = pointA
        self.pointB:Particle = pointB
        self.original_len = length
        self.len = length
        self.strength = strength


    def update(self, dt=1):
        diffx = self.pointB.x - self.pointA.x
        diffy = self.pointB.y - self.pointA.y
        mag = math.sqrt(diffx * diffx + diffy * diffy)
        diff_mag = self.len - mag
        if mag > 0:
            dA = (((self.pointA.mass / (self.pointA.mass + self.pointB.mass)) * diff_mag * self.strength) / mag) * -dt
            dB = (((self.pointB.mass / (self.pointA.mass + self.pointB.mass)) * diff_mag * self.strength) / mag) * dt
            self.pointA.add_offset(diffx * dA, diffy * dA)
            self.pointB.add_offset(diffx * dB, diffy * dB)



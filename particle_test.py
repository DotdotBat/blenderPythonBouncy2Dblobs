from particle import Coordinate2D, Particle, ChainableParticle
import math
import unittest
from unittest.mock import Mock

class TestParticleFunctions(unittest.TestCase):
    def setUp(self):
        # Mock coordinates to avoid issues with floating point precision
        self.mock_coord = Coordinate2D(0.0, 0.0)
        self.mock_other_coord = Coordinate2D(1.0, 1.0)

        self.particle = ChainableParticle(0.0, 0.0)
        self.particle.radius = 5.0
        self.particle.damping = 0.8
        self.particle.mass = 10.0

    def test_attract_same_particle(self):
        self.particle.attract(self.particle.x, self.particle.y)
        self.assertEqual(self.particle.vx, 0)
        self.assertEqual(self.particle.vy, 0)

    def test_attract_different_particles(self):
        other_particle = Particle(2.0, 2.0)
        strength = 3.0
        self.particle.attract(other_particle.x, other_particle.y, strength)
        expected_vx = -strength * (2.0 - self.particle.x) / math.sqrt((2.0 - 0.0)**2 + (2.0 - 0.0)**2)
        expected_vy = -strength * (2.0 - self.particle.y) / math.sqrt((2.0 - 0.0)**2 + (2.0 - 0.0)**2)

        self.assertAlmostEqual(self.particle.vx, expected_vx, places=4)
        self.assertAlmostEqual(self.particle.vy, expected_vy, places=4)

    def test_repel_same_radius(self):
        result = self.particle.repel(self.particle.x, self.particle.y)
        self.assertIsNone(result)

    def test_repel_different_particles_no_intersection(self):
        other_particle = Particle(8.0, 8.0)
        other_particle.radius = 4.0
        result = self.particle.repel(other_particle.x, other_particle.y)
        self.assertIsNotNone(result)

        expected_force = Coordinate2D(-1.0 / math.sqrt(2), -1.0 / math.sqrt(2))
        self.assertCoordinate2DEqual(result, expected_force)

    def test_repel_different_particles_intersection(self):
        other_particle = Particle(4.0, 4.0)
        result = self.particle.repel(other_particle.x, other_particle.y)
        self.assertIsNotNone(result)

        expected_force = Coordinate2D(0.5, 0.5)
        self.assertCoordinate2DEqual(result, expected_force)

    def test_collide_with_self(self):
        radius = self.particle.radius
        self.particle.collide(self.particle.x, self.particle.y, radius)
        self.assertEqual(self.particle.x, 0.0)
        self.assertEqual(self.particle.y, 0.0)

    def test_collide_different_particles(self):
        other_particle = Particle(4.0, 4.0)
        radius_sum = self.particle.radius + other_particle.radius
        other_particle.collide(self.particle.x, self.particle.y, radius_sum)

        # Particles should bounce off each other
        self.assertAlmostEqual(self.particle.x, 4.0 - 5.0)
        self.assertAlmostEqual(self.particle.y, 4.0)

    def test_constrain_particle_inside_box(self):
        left, top, right, bottom = -10.0, -10.0, 10.0, 10.0
        self.particle.constrain(left, top, right, bottom)
        self.assertAlmostEqual(self.particle.x, 0.0)
        self.assertAlmostEqual(self.particle.y, 0.0)

    def test_constrain_particle_left_edge(self):
        left, top, right, bottom = -10.0, 0.0, 5.0, 5.0
        self.particle.x = -11.0
        self.particle.constrain(left, top, right, bottom)
        self.assertEqual(self.particle.x, left + self.particle.radius)

    def test_constrain_particle_right_edge(self):
        left, top, right, bottom = -5.0, 0.0, 10.0, 5.0
        self.particle.x = 6.0
        self.particle.constrain(left, top, right, bottom)
        self.assertEqual(self.particle.x, right - self.particle.radius)

    def test_constrain_particle_top_edge(self):
        left, top, right, bottom = -5.0, -5.0, 5.0, 10.0
        self.particle.y = -6.0
        self.particle.constrain(left, top, right, bottom)
        self.assertEqual(self.particle.y, top + self.particle.radius)

    def test_constrain_particle_bottom_edge(self):
        left, top, right, bottom = -5.0, 6.0, 5.0, 10.0
        self.particle.y = 11.0
        self.particle.constrain(left, top, right, bottom)
        self.assertEqual(self.particle.y, bottom - self.particle.radius)

    def test_get_velocity_initial_state(self):
        self.assertCoordinate2DEqual(self.particle.get_velocity(), Coordinate2D(0.0, 0.0))

    def test_get_velocity_after_change(self):
        self.particle.vx = 0.5
        self.particle.vy = -0.3
        expected_velocity = Coordinate2D(0.5, -0.3)
        self.assertCoordinate2DEqual(self.particle.get_velocity(), expected_velocity)

    def test_get_velocity_mag_initial_state(self):
        self.assertEqual(self.particle.get_velocity_mag(), 0.0)

    def test_get_velocity_mag_after_change(self):
        self.particle.vx = 0.4
        self.particle.vy = 0.6
        expected_mag = math.sqrt(0.4**2 + 0.6**2)
        self.assertAlmostEqual(self.particle.get_velocity_mag(), expected_mag, places=4)

    def test_update_no_damping(self):
        dt = 0.1
        self.particle.vx = 0.3
        self.particle.vy = -0.2
        self.particle.move_with_inertia(dt)
        expected_x = 0.0 + 0.3 * dt
        expected_y = 0.0 - 0.2 * dt
        self.assertAlmostEqual(self.particle.x, expected_x, places=4)
        self.assertAlmostEqual(self.particle.y, expected_y, places=4)

    def test_update_with_damping(self):
        dt = 0.1
        self.particle.vx = 0.3
        self.particle.vy = -0.2
        self.particle.move_with_inertia(dt)
        self.particle.damp_speed(dt)
        expected_x = 0.0 + 0.3 * dt * self.particle.damping
        expected_y = 0.0 - 0.2 * dt * self.particle.damping
        self.assertAlmostEqual(self.particle.x, expected_x, places=4)
        self.assertAlmostEqual(self.particle.y, expected_y, places=4)

    def test_update_client_mock_client(self):
        # Mock a client and its update method
        self.particle.client = Mock(spec=['update'])
        self.particle.update_client()
        self.particle.client.update.assert_called_once()

    def test_lerp_start_equals_end(self):
        self.assertEqual(Particle.lerp(0.0, 0.0, 0.5), 0.0)

    def test_lerp_midpoint(self):
        self.assertAlmostEqual(Particle.lerp(1.0, 9.0, 0.5), 5.0)

    def test_lerp_start_does_not_equal_end(self):
        self.assertAlmostEqual(Particle.lerp(-1.0, 2.0, 0.2), 0.4)

    def assertCoordinate2DEqual(self, coord1, coord2):
        self.assertEqual(coord1.x, coord2.x)
        self.assertEqual(coord1.y, coord2.y)

class TestChainableParticleFunctions(unittest.TestCase):
    def setUp(self):
        self.particle1 = ChainableParticle(0.0, 0.0)
        self.particle2 = ChainableParticle(5.0, 5.0)
        self.particle3 = ChainableParticle(10.0, 10.0)

    def test_set_is_root_true(self):
        self.particle1.set_is_root(True)
        self.assertTrue(self.particle1.is_root)

    def test_set_is_root_false(self):
        self.particle1.set_is_root(False)
        self.assertFalse(self.particle1.is_root)

    def test_set_next_sibling_with_instance(self):
        self.particle1.set_next_sibling(self.particle2)
        self.assertIs(self.particle1.next_sibling, self.particle2)

    def test_set_next_sibling_with_attribute(self):
        self.particle1.next_sibling = self.particle3
        self.assertIs(self.particle1.next_sibling, self.particle3)

    def test_set_prev_sibling_with_instance(self):
        self.particle1.set_prev_sibling(self.particle2)
        self.assertIs(self.particle1.prev_sibling, self.particle2)

    def test_set_prev_sibling_with_attribute(self):
        self.particle1.prev_sibling = self.particle3
        self.assertIs(self.particle1.prev_sibling, self.particle3)

# Run the tests
if __name__ == "__main__":
    unittest.main()

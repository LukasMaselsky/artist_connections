import unittest
from artist_connections.helpers.helpers import rgba_to_hex

# python -m unittest -v tests.tests

class RgbaToHexTest(unittest.TestCase):
    def test_zero(self):
        res = rgba_to_hex(0, 0, 0, 0)

        self.assertEqual(res, "#00000000")

    def test_max(self):
        res = rgba_to_hex(255, 255, 255, 1)

        self.assertEqual(res, "#ffffffff")

    def test_out_of_bounds(self):
        self.assertRaises(ValueError, rgba_to_hex, 256, 255, 255, 1)

    def test_negative(self):
        self.assertRaises(ValueError, rgba_to_hex, -1, 0, 0, 0)

    


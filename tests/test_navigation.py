import unittest

from navigation import (
    blh_to_neu,
    blh_to_xyz,
    body_to_neu,
    neu_to_blh,
    neu_to_body,
    xyz_to_blh,
)


class NavigationTests(unittest.TestCase):
    def test_blh_xyz(self):
        blh = (30.531679065, 114.357268025, 28.1568)
        xyz = blh_to_xyz(*blh)
        expected = (-2267750.1466, 5009154.5075, 3221294.3800)
        for actual, reference in zip(xyz, expected):
            self.assertAlmostEqual(actual, reference, delta=0.02)

        recovered = xyz_to_blh(*xyz)
        for actual, reference in zip(recovered, blh):
            self.assertAlmostEqual(actual, reference, places=7)

    def test_blh_neu(self):
        origin = (30.531679065, 114.357268025, 28.1568)
        target = (30.532, 114.358, 45.0)
        recovered = neu_to_blh(blh_to_neu(target, origin), origin)
        for actual, reference in zip(recovered, target):
            self.assertAlmostEqual(actual, reference, places=7)

    def test_body_neu(self):
        body = (1.0, 0.2, 0.1)
        attitude = (35.0, 5.0, -3.0)
        recovered = neu_to_body(body_to_neu(body, *attitude), *attitude)
        for actual, reference in zip(recovered, body):
            self.assertAlmostEqual(actual, reference, places=12)


if __name__ == "__main__":
    unittest.main()

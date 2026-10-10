import unittest
from math import sqrt

from navigation import (
    blh_to_neu,
    blh_to_xyz,
    body_to_neu,
    neu_to_blh,
    neu_to_body,
    xyz_to_blh,
    xyz_to_neu,
    neu_to_xyz,
)


class NavigationTests(unittest.TestCase):
    def test_blh_xyz(self):
        blh = (30.531679065, 114.357268025, 28.1568)
        xyz = blh_to_xyz(*blh)
        expected = (-2267750.1466, 5009154.5075, 3221294.3800)
        for actual, reference in zip(xyz, expected):
            self.assertAlmostEqual(actual, reference, delta=1e-4)

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
        # 旋转只改变方向，不改变向量长度。
        neu = body_to_neu(body, *attitude)
        self.assertAlmostEqual(sum(v * v for v in neu), sum(v * v for v in body))

    def test_blh_axes(self):
        # 赤道上经度 0 度、90 度分别位于 ECEF 的 X、Y 正轴。
        for blh, expected in [
            ((0, 0, 0), (6378137.0, 0, 0)),
            ((0, 90, 10), (0, 6378147.0, 0)),
        ]:
            with self.subTest(blh=blh):
                for actual, reference in zip(blh_to_xyz(*blh), expected):
                    self.assertAlmostEqual(actual, reference, delta=1e-8)

    def test_blh_xyz_quadrants_and_poles(self):
        for blh in [
            (0, -120, 0), (-30, -70, -20), (45, 150, 1000),
            (89.999999, 114, 100), (-89.999999, -60, 100),
            (90, 0, 100), (-90, 0, 100),
        ]:
            with self.subTest(blh=blh):
                recovered = xyz_to_blh(*blh_to_xyz(*blh))
                for actual, reference in zip(recovered[:2], blh[:2]):
                    self.assertAlmostEqual(actual, reference, delta=1e-9)
                self.assertAlmostEqual(recovered[2], blh[2], delta=1e-6)

    def test_geocentre_rejected(self):
        with self.assertRaises(ValueError):
            xyz_to_blh(0, 0, 0)

    def test_xyz_neu_axes(self):
        # 在赤道、零经度处，北向=Z、东向=Y、天向=X。
        origin = (0, 0, 0)
        xyz = (6378137.0 + 3, 2, 1)
        self.assertEqual(xyz_to_neu(xyz, origin), (1, 2, 3))
        self.assertEqual(neu_to_xyz((1, 2, 3), origin), xyz)
        self.assertEqual(xyz_to_neu(blh_to_xyz(*origin), origin), (0, 0, 0))

    def test_body_axes_zero(self):
        # 零姿态时，载体系右、前、上分别对应东、北、天。
        for body, expected in [
            ((1, 0, 0), (0, 1, 0)),
            ((0, 1, 0), (1, 0, 0)),
            ((0, 0, 1), (0, 0, 1)),
        ]:
            self.assertEqual(body_to_neu(body, 0, 0, 0), expected)
            self.assertEqual(neu_to_body(expected, 0, 0, 0), body)

    def test_body_single_angles(self):
        # 独立检查方向，避免一对互逆但方向错误的矩阵也通过回算测试。
        c = sqrt(3) / 2
        cases = [
            ((0, 1, 0), (90, 0, 0), (0, 1, 0)),  # 航向东，前向指东
            ((0, 1, 0), (0, 30, 0), (c, 0, 0.5)),  # 抬头，前向有正 U
            ((1, 0, 0), (0, 0, 30), (0, c, -0.5)),  # 右倾，右向有负 U
        ]
        for body, attitude, expected in cases:
            with self.subTest(attitude=attitude):
                for actual, reference in zip(body_to_neu(body, *attitude), expected):
                    self.assertAlmostEqual(actual, reference, places=12)
                for actual, reference in zip(neu_to_body(expected, *attitude), body):
                    self.assertAlmostEqual(actual, reference, places=12)


if __name__ == "__main__":
    unittest.main()

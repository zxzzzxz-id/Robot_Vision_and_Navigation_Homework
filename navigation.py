"""导航中常用坐标系转换。

BLH 中纬度和经度使用度，大地高及直角坐标使用米。
NEU 的分量顺序为北、东、天。
载体系采用右、前、上，姿态角采用 Lecture 2 第 90 页的 Z-X-Y 顺序。
"""

from math import atan, atan2, cos, degrees, hypot, radians, sin, sqrt


# WGS-84 椭球参数
A = 6378137.0
F = 1 / 298.257223563
E2 = F * (2 - F)
B_AXIS = A * (1 - F)


def _mat_vec(matrix, vector):
    """计算 3×3 矩阵与三维向量的乘积。"""

    x, y, z = vector
    return tuple(row[0] * x + row[1] * y + row[2] * z for row in matrix)


def _transpose(matrix):
    """计算 3×3 矩阵的转置。"""

    return tuple(tuple(matrix[j][i] for j in range(3)) for i in range(3))


def blh_to_xyz(latitude_deg, longitude_deg, height):
    """WGS-84 大地坐标 BLH 转空间直角坐标 XYZ。"""

    latitude = radians(latitude_deg)
    longitude = radians(longitude_deg)
    sin_b = sin(latitude)
    cos_b = cos(latitude)

    # 卯酉圈曲率半径
    n = A / sqrt(1 - E2 * sin_b**2)

    x = (n + height) * cos_b * cos(longitude)
    y = (n + height) * cos_b * sin(longitude)
    z = (n * (1 - E2) + height) * sin_b
    return x, y, z


def xyz_to_blh(x, y, z):
    """空间直角坐标 XYZ 迭代转为 WGS-84 大地坐标 BLH。"""

    p = hypot(x, y)
    longitude = atan2(y, x)

    # 极点处 p=0，需要单独计算
    if p < 1e-9:
        if abs(z) < 1e-9:
            raise ValueError("地心处无法确定大地纬度和经度")
        latitude = 90.0 if z >= 0 else -90.0
        return latitude, 0.0, abs(z) - B_AXIS

    # 按讲义第 51 页迭代求纬度
    tan_b = z / p
    for _ in range(100):
        new_tan_b = (
            z + A * E2 * tan_b / sqrt(1 + (1 - E2) * tan_b**2)
        ) / p
        if abs(new_tan_b - tan_b) < 1e-12:
            tan_b = new_tan_b
            break
        tan_b = new_tan_b

    latitude = atan(tan_b)
    n = A / sqrt(1 - E2 * sin(latitude) ** 2)
    # 高纬度时 cos(B) 很小，改用 Z 方程求高，避免除以接近零的数。
    if abs(latitude) <= radians(45):
        height = p / cos(latitude) - n
    else:
        height = z / sin(latitude) - n * (1 - E2)
    return degrees(latitude), degrees(longitude), height


def _xyz_to_neu_matrix(latitude_deg, longitude_deg):
    """地心地固坐标系到当地 NEU 坐标系的方向余弦矩阵。"""

    b = radians(latitude_deg)
    l = radians(longitude_deg)
    return (
        (-sin(b) * cos(l), -sin(b) * sin(l), cos(b)),
        (-sin(l), cos(l), 0.0),
        (cos(b) * cos(l), cos(b) * sin(l), sin(b)),
    )


def xyz_to_neu(point_xyz, origin_blh):
    """XYZ 点转为以 origin_blh 为原点的当地 NEU 坐标。"""

    x, y, z = point_xyz
    b0, l0, h0 = origin_blh
    x0, y0, z0 = blh_to_xyz(b0, l0, h0)
    delta_xyz = (x - x0, y - y0, z - z0)
    return _mat_vec(_xyz_to_neu_matrix(b0, l0), delta_xyz)


def neu_to_xyz(point_neu, origin_blh):
    """当地 NEU 点转为空间直角坐标 XYZ。"""

    b0, l0, h0 = origin_blh
    x0, y0, z0 = blh_to_xyz(b0, l0, h0)
    matrix = _xyz_to_neu_matrix(b0, l0)
    dx, dy, dz = _mat_vec(_transpose(matrix), point_neu)
    return x0 + dx, y0 + dy, z0 + dz


def blh_to_neu(point_blh, origin_blh):
    """BLH 点转为当地 NEU 坐标。"""

    return xyz_to_neu(blh_to_xyz(*point_blh), origin_blh)


def neu_to_blh(point_neu, origin_blh):
    """当地 NEU 点转为 BLH。"""

    return xyz_to_blh(*neu_to_xyz(point_neu, origin_blh))


def _body_to_neu_matrix(yaw_deg, pitch_deg, roll_deg):
    """由讲义第 90 页的 Z-X-Y 矩阵得到 Body（右前上）到 NEU 的矩阵。

    讲义的坐标轴旋转矩阵 A 将 ENU 分量转为载体系分量。
    先转置得到 Body -> ENU，再交换前两行得到 Body -> NEU。
    """

    psi = radians(yaw_deg)       # 偏航角
    theta = radians(pitch_deg)   # 俯仰角
    gamma = radians(roll_deg)    # 横滚角
    sp, cp = sin(psi), cos(psi)
    st, ct = sin(theta), cos(theta)
    sg, cg = sin(gamma), cos(gamma)

    enu_to_body = (
        (cg * cp + sg * st * sp, -cg * sp + sg * st * cp, -sg * ct),
        (ct * sp, ct * cp, st),
        (sg * cp - cg * st * sp, -sg * sp - cg * st * cp, cg * ct),
    )
    body_to_enu = _transpose(enu_to_body)
    return body_to_enu[1], body_to_enu[0], body_to_enu[2]


def body_to_neu(vector_body, yaw_deg, pitch_deg, roll_deg):
    """右前上载体系向量转 NEU；航向北起顺时针，俯仰抬头为正，横滚右倾为正。

    两个坐标系原点重合，只旋转向量；零姿态时载体前向指北、右向指东。
    """

    matrix = _body_to_neu_matrix(yaw_deg, pitch_deg, roll_deg)
    return _mat_vec(matrix, vector_body)


def neu_to_body(vector_neu, yaw_deg, pitch_deg, roll_deg):
    """NEU 向量转为右前上载体系向量，角度约定与 body_to_neu 相同。"""

    matrix = _body_to_neu_matrix(yaw_deg, pitch_deg, roll_deg)
    return _mat_vec(_transpose(matrix), vector_neu)

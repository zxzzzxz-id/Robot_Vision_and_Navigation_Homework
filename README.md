# 导航常用坐标系转换课程作业

## 1. 作业内容

本作业根据课程讲义中的坐标系定义和转换公式，使用 Python 实现以下功能：

1. WGS-84 椭球下大地坐标 BLH 与空间直角坐标 XYZ 的相互转换；
2. 地球坐标系 XYZ 与当地地理坐标系 NEU 的相互转换；
3. 载体坐标系与地理坐标系 NEU 的相互转换；
4. 使用讲义中的武汉 IGS 站数据进行计算，并输出 SVG 可视化结果。

其中，BLH 与 XYZ 的公式、地理坐标系旋转矩阵以及欧拉角旋转顺序主要参考 Lecture 2；坐标和姿态的定义参考 Lecture 1 和 Lecture 4。

## 2. 坐标约定

- `BLH = (B, L, H)`：大地纬度、大地经度和大地高；
- `XYZ = (X, Y, Z)`：WGS-84 地心地固坐标；
- `NEU = (North, East, Up)`：北、东、天；
- 载体坐标系采用 x 轴向前、y 轴向右、z 轴向上；
- 角度输入和输出均为度，长度单位为米。

## 3. 主要算法

### 3.1 BLH 转 XYZ

WGS-84 椭球参数为：

```text
a = 6378137.0 m
f = 1 / 298.257223563
e² = f(2-f)
```

卯酉圈曲率半径：

```text
N = a / sqrt(1 - e²sin²B)
```

转换公式：

```text
X = (N + H)cosBcosL
Y = (N + H)cosBsinL
Z = [N(1-e²) + H]sinB
```

### 3.2 XYZ 转 BLH

经度使用 `L = atan2(Y, X)` 计算。纬度采用讲义中的迭代方法：

```text
p = sqrt(X² + Y²)
tan(B0) = Z / p

tan(Bi) = [Z + ae²tan(Bi-1) /
           sqrt(1 + (1-e²)tan²(Bi-1))] / p
```

相邻两次迭代结果之差小于 `1e-12` 时停止，最后计算：

```text
H = p / cosB - N
```

### 3.3 XYZ 与 NEU

先用参考点的 BLH 计算其 ECEF 坐标，再求目标点与参考点的坐标差：

```text
Δr = r - r0
NEU = C × Δr
```

ECEF 到 NEU 的方向余弦矩阵为：

```text
[-sinBcosL,  -sinBsinL,  cosB]
[-sinL,       cosL,       0   ]
[ cosBcosL,   cosBsinL,  sinB]
```

逆变换使用该矩阵的转置。

### 3.4 载体系与 NEU

欧拉角采用讲义中的 Z-X-Y 顺序：偏航角 `psi`、俯仰角 `theta`、横滚角 `gamma`。

```text
A = Ry(gamma) Rx(theta) Rz(psi)
v_neu  = A v_body
v_body = A^T v_neu
```

## 4. 程序运行

程序只使用 Python 标准库，不需要安装第三方库。

```bash
# 运行三个转换示例并生成 output/result.svg
python main.py

# 运行测试
python -m unittest discover -s tests -v
```

## 5. 文件说明

```text
navigation.py               三类坐标转换函数
main.py                     计算示例
tests/test_navigation.py    简单测试
output/result.svg           计算结果示意图，可用浏览器打开
```

## 6. 计算结果

讲义中的武汉 IGS 站坐标为：

```text
BLH = (30.531679065°, 114.357268025°, 28.1568 m)
XYZ = (-2267750.1466, 5009154.5075, 3221294.3800) m
```

程序计算得到：

```text
XYZ = (-2267750.1466, 5009154.5075, 3221294.3800) m
```

同时对 BLH 与 XYZ、BLH 与 NEU、载体系与 NEU 进行了双向转换测试，结果均能还原到原始数据允许的数值精度范围内。

"""课程作业计算示例。"""

from pathlib import Path

from navigation import (
    blh_to_neu,
    blh_to_xyz,
    body_to_neu,
    neu_to_body,
    xyz_to_blh,
)


def show(name, values, digits=6):
    text = ", ".join(f"{value:.{digits}f}" for value in values)
    print(f"{name}: ({text})")


def save_visualization(wuhan_xyz, local_neu, vector_neu):
    """将三组计算结果保存为浏览器可打开的 SVG 图。"""

    x, y, z = wuhan_xyz
    north, east, up = local_neu
    body_n, body_e, body_u = vector_neu
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560" viewBox="0 0 1000 560">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#334155"/></marker></defs>
<rect width="1000" height="560" fill="#f1f5f9"/>
<g font-family="Microsoft YaHei,Arial" fill="#1e293b">
<text x="40" y="50" font-size="26" font-weight="bold">导航常用坐标系转换结果</text>

<rect x="30" y="80" width="300" height="430" rx="12" fill="white" stroke="#cbd5e1"/>
<text x="50" y="120" font-size="20" font-weight="bold">1. BLH → XYZ</text>
<ellipse cx="180" cy="260" rx="100" ry="78" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
<line x1="180" y1="260" x2="112" y2="205" stroke="#dc2626" stroke-width="3" marker-end="url(#arrow)"/>
<circle cx="112" cy="205" r="5" fill="#dc2626"/>
<text x="70" y="190" font-size="14">武汉 IGS 站</text>
<text x="50" y="385" font-size="14">X = {x:.4f} m</text>
<text x="50" y="415" font-size="14">Y = {y:.4f} m</text>
<text x="50" y="445" font-size="14">Z = {z:.4f} m</text>

<rect x="350" y="80" width="300" height="430" rx="12" fill="white" stroke="#cbd5e1"/>
<text x="370" y="120" font-size="20" font-weight="bold">2. BLH → NEU</text>
<circle cx="485" cy="310" r="5" fill="#1e293b"/>
<line x1="485" y1="310" x2="485" y2="175" stroke="#2563eb" stroke-width="3" marker-end="url(#arrow)"/>
<line x1="485" y1="310" x2="610" y2="310" stroke="#16a34a" stroke-width="3" marker-end="url(#arrow)"/>
<line x1="485" y1="310" x2="425" y2="250" stroke="#dc2626" stroke-width="3" marker-end="url(#arrow)"/>
<circle cx="{485 + east * 5:.1f}" cy="{310 - north * 5:.1f}" r="6" fill="#f59e0b"/>
<text x="495" y="180" font-size="14">N</text><text x="600" y="335" font-size="14">E</text><text x="400" y="245" font-size="14">U</text>
<text x="370" y="400" font-size="14">N = {north:.4f} m</text>
<text x="370" y="430" font-size="14">E = {east:.4f} m</text>
<text x="370" y="460" font-size="14">U = {up:.4f} m</text>

<rect x="670" y="80" width="300" height="430" rx="12" fill="white" stroke="#cbd5e1"/>
<text x="690" y="120" font-size="20" font-weight="bold">3. Body → NEU</text>
<circle cx="805" cy="310" r="5" fill="#1e293b"/>
<line x1="805" y1="310" x2="805" y2="175" stroke="#2563eb" stroke-width="3" marker-end="url(#arrow)"/>
<line x1="805" y1="310" x2="930" y2="310" stroke="#16a34a" stroke-width="3" marker-end="url(#arrow)"/>
<line x1="805" y1="310" x2="{805 + body_e * 85:.1f}" y2="{310 - body_n * 85:.1f}" stroke="#f97316" stroke-width="4" marker-end="url(#arrow)"/>
<text x="815" y="180" font-size="14">N</text><text x="920" y="335" font-size="14">E</text>
<text x="690" y="400" font-size="14">N = {body_n:.6f}</text>
<text x="690" y="430" font-size="14">E = {body_e:.6f}</text>
<text x="690" y="460" font-size="14">U = {body_u:.6f}</text>
</g></svg>"""

    output = Path("output/result.svg")
    output.parent.mkdir(exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    return output


def main():
    # 1. 讲义中的武汉 IGS 站
    wuhan_blh = (30.531679065, 114.357268025, 28.1568)
    wuhan_xyz = blh_to_xyz(*wuhan_blh)
    print("1. BLH 与 XYZ 转换")
    show("XYZ / m", wuhan_xyz, 4)
    show("回算 BLH", xyz_to_blh(*wuhan_xyz), 9)

    # 2. 附近一点相对武汉 IGS 站的局部坐标
    target_blh = (30.531779065, 114.357368025, 38.1568)
    local_neu = blh_to_neu(target_blh, wuhan_blh)
    print("\n2. BLH 与 NEU 转换")
    show("NEU / m", local_neu, 4)

    # 3. 载体系与地理坐标系转换
    vector_body = (1.0, 0.2, 0.1)
    attitude = (35.0, 5.0, -3.0)  # 偏航角、俯仰角、横滚角
    vector_neu = body_to_neu(vector_body, *attitude)
    print("\n3. 载体系与 NEU 转换")
    show("Body -> NEU", vector_neu)
    show("NEU -> Body", neu_to_body(vector_neu, *attitude))

    output = save_visualization(wuhan_xyz, local_neu, vector_neu)
    print(f"\n可视化结果：{output}")


if __name__ == "__main__":
    main()

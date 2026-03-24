import cadquery as cq
from config import *

try:
    from ocp_vscode import show_object
    HAVE_VIEWER = True
except ImportError:
    HAVE_VIEWER = False

total_w = cols * cell_size + outer_wall_thickness * 2
total_h = rows * cell_size + outer_wall_thickness * 2

# 1. 外形の作成
lid = (cq.Workplane("XY")
       .box(total_w, total_h, base_height, centered=(True, True, False))
       .edges("|Z").fillet(corner_radius))

# 2. ハニカムグリッドの座標計算
dx = (mesh_size * 1.5/2) + (mesh_thickness * 0.8) # X方向のピッチ
dy = (mesh_size * 1.732/2) + (mesh_thickness * 0.8) # Y方向のピッチ

mask_w = total_w - outer_wall_thickness * 2.5
mask_h = total_h - outer_wall_thickness * 2.5

pts = []
nx = int(mask_w / dx) + 1
ny = int(mask_h / dy) + 1

for i in range(-nx, nx):
    for j in range(-ny, ny):
        x = i * dx
        y = j * dy
        if i % 2 == 1:
            y += dy / 2
        if abs(x) < mask_w / 2 and abs(y) < mask_h / 2:
            pts.append((x, y))

# 3. 高速化の肝：スケッチを使って一括で穴を開ける
# 以前のように1つずつ cut() せず、一度に全てのポリゴンを描画して貫通させる
lid = (lid.faces(">Z").workplane()
       .pushPoints(pts)
       .polygon(6, mesh_size)
       .cutThruAll())

# 4. ネジ穴の追加
lid = (lid.faces(">Z").workplane()
       .rect(total_w - outer_wall_thickness, total_h - outer_wall_thickness, forConstruction=True)
       .vertices()
       .hole(m3_hole_dia))

# 表示
if HAVE_VIEWER:
    show_object(lid)
cq.exporters.export(lid, 'maze_cover.stl')
cq.exporters.export(lid, 'maze_cover.step')
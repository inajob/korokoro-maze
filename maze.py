import cadquery as cq
import random
from config import *

try:
    from ocp_vscode import show_object
    HAVE_VIEWER = True
except ImportError:
    HAVE_VIEWER = False

def generate_maze_walls(r, c):
    v_walls = [[True] * (c + 1) for _ in range(r)]
    h_walls = [[True] * c for _ in range(r + 1)]
    visited = [[False] * c for _ in range(r)]
    def walk(x, y):
        visited[y][x] = True
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]; random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < c and 0 <= ny < r and not visited[ny][nx]:
                if dx == 1: v_walls[y][x+1] = False
                elif dx == -1: v_walls[y][x] = False
                elif dy == 1: h_walls[y+1][x] = False
                elif dy == -1: h_walls[y][x] = False
                walk(nx, ny)
    walk(0, 0)
    return v_walls, h_walls

v_walls, h_walls = generate_maze_walls(rows, cols)

# 1. 外形とくり抜き (Z=0を接地面に固定)
total_w = cols * cell_size + outer_wall_thickness * 2
total_h = rows * cell_size + outer_wall_thickness * 2
full_height = base_height + total_height_above_base

# ベースの作成
result = (cq.Workplane("XY")
          .box(total_w, total_h, full_height, centered=(True, True, False))
          .edges("|Z").fillet(corner_radius))

# 内部を掘り下げる
inner_w = cols * cell_size
inner_h = rows * cell_size
result = result.faces(">Z").workplane().rect(inner_w, inner_h).cutBlind(-total_height_above_base)

# 2. 内部壁の絶対座標リストを作成
start_x = -inner_w / 2
start_y = -inner_h / 2

v_wall_points = []
for r in range(rows):
    for c in range(1, cols):
        if v_walls[r][c]:
            v_wall_points.append((start_x + c * cell_size, start_y + r * cell_size + cell_size / 2))

h_wall_points = []
for r in range(1, rows):
    for c in range(cols):
        if h_walls[r][c]:
            h_wall_points.append((start_x + c * cell_size + cell_size / 2, start_y + r * cell_size))

# 3. 壁を一括配置 (pushPointsを使うことで絶対座標で配置)
# 垂直壁
if v_wall_points:
    v_walls_union = (cq.Workplane("XY")
                     .workplane(offset=base_height)
                     .pushPoints(v_wall_points)
                     .box(inner_wall_thickness, cell_size + inner_wall_thickness, total_height_above_base, centered=(True, True, False)))
    result = result.union(v_walls_union)

# 水平壁
if h_wall_points:
    h_walls_union = (cq.Workplane("XY")
                     .workplane(offset=base_height)
                     .pushPoints(h_wall_points)
                     .box(cell_size + inner_wall_thickness, inner_wall_thickness, total_height_above_base, centered=(True, True, False)))
    result = result.union(h_walls_union)

# 4. M3貫通穴とスタート/ゴール穴
result = (result.faces(">Z").workplane()
          .rect(total_w - outer_wall_thickness, total_h - outer_wall_thickness, forConstruction=True)
          .vertices().hole(m3_hole_dia))

hole_start = (start_x + cell_size / 2, start_y + cell_size / 2)
hole_end = (start_x + inner_w - cell_size / 2, start_y + inner_h - cell_size / 2)

result = (result.faces(">Z").workplane()
          .pushPoints([hole_start, hole_end])
          .circle(hole_radius).cutThruAll())

# 出力
if HAVE_VIEWER:
    show_object(result)
cq.exporters.export(result, 'maze.stl')
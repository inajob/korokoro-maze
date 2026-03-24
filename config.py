# --- 共通パラメータ ---
rows, cols = 8, 8
cell_size = 19.0
outer_wall_thickness = 8.0
corner_radius = 3.0
m3_hole_dia = 4
base_height = 0.5  # 底板およびカバーの厚み

# --- 迷路本体 (maze.py) 専用 ---
inner_wall_thickness = 1.2
total_height_above_base = 17.0
hole_radius = 8.5

# --- カバー (maze-cover.py) 専用 ---
mesh_size = 7.5        # 六角形の外接円半径
mesh_thickness = 1.2   # 線幅

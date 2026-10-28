"""ClockWise pixel-art generator.

Generates GBA-Pokemon-style pixel art: terrain tiles, buildings, a player
character, and a composed mock screenshot of the game. Run from repo root:

    python3 Tools/artgen/generate_art.py
"""
import os
import random
from PIL import Image, ImageDraw

random.seed(42)

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
ART = os.path.join(ROOT, "Assets", "Art")

T = 16  # tile size in px

# ---------------------------------------------------------------- palette --
OUT = (41, 38, 52)          # outline
GRASS = (124, 190, 100)
GRASS_D = (108, 172, 86)
GRASS_SPECK = (92, 154, 74)
TALL = (84, 150, 72)
TALL_D = (66, 126, 58)
PATH = (224, 198, 150)
PATH_D = (202, 172, 124)
PATH_EDGE = (166, 134, 94)
WATER = (80, 140, 215)
WATER_L = (130, 182, 240)
WATER_D = (58, 110, 182)
SAND = (236, 220, 170)
TREE = (62, 134, 76)
TREE_L = (94, 166, 100)
TREE_D = (42, 104, 60)
TRUNK = (124, 86, 58)
TRUNK_D = (96, 64, 44)
FLOWER_R = (232, 96, 96)
FLOWER_Y = (244, 208, 96)
FLOWER_W = (246, 246, 246)

WALL = (236, 224, 200)
WALL_D = (208, 192, 164)
WALL_STONE = (216, 214, 222)
WALL_STONE_D = (184, 182, 196)
ROOF_R = (212, 92, 80)
ROOF_R_D = (172, 62, 56)
ROOF_B = (92, 122, 198)
ROOF_B_D = (64, 90, 158)
ROOF_T = (88, 172, 156)
ROOF_T_D = (58, 134, 122)
ROOF_G = (130, 130, 142)
ROOF_G_D = (98, 98, 112)
WIN = (140, 196, 232)
WIN_D = (98, 150, 196)
DOOR = (140, 96, 60)
DOOR_D = (108, 72, 46)
SIGN_BG = (246, 240, 222)
GOLD = (236, 190, 80)
GOLD_D = (196, 148, 52)
WHITE = (246, 246, 246)
CLOCKFACE = (250, 248, 238)

# character colours
HAIR = (104, 70, 44)
HAIR_L = (140, 98, 60)
SKIN = (240, 194, 152)
SKIN_D = (212, 162, 122)
JACKET = (64, 112, 192)
JACKET_D = (46, 84, 152)
PANTS = (74, 68, 96)
SHOE = (122, 80, 52)

NPC_HAIR = (58, 58, 66)
NPC_SHIRT = (196, 88, 100)
NPC_PANTS = (90, 110, 90)

CHAR_KEY = {
    ".": None, "K": OUT, "H": HAIR, "h": HAIR_L, "S": SKIN, "s": SKIN_D,
    "E": OUT, "J": JACKET, "j": JACKET_D, "P": PANTS, "B": SHOE, "W": WHITE,
}

# ------------------------------------------------------------- tiny font --
# 3x5 pixel font for signs / UI
FONT = {
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "G": ["011", "100", "101", "101", "011"],
    "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"],
    "J": ["001", "001", "001", "101", "010"],
    "K": ["101", "110", "100", "110", "101"],
    "L": ["100", "100", "100", "100", "111"],
    "M": ["101", "111", "111", "101", "101"],
    "N": ["101", "111", "111", "111", "101"],
    "O": ["010", "101", "101", "101", "010"],
    "P": ["110", "101", "110", "100", "100"],
    "Q": ["010", "101", "101", "110", "011"],
    "R": ["110", "101", "110", "110", "101"],
    "S": ["011", "100", "010", "001", "110"],
    "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"],
    "V": ["101", "101", "101", "101", "010"],
    "W": ["101", "101", "111", "111", "101"],
    "X": ["101", "101", "010", "101", "101"],
    "Y": ["101", "101", "010", "010", "010"],
    "Z": ["111", "001", "010", "100", "111"],
    "0": ["010", "101", "101", "101", "010"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["110", "001", "010", "100", "111"],
    "3": ["110", "001", "010", "001", "110"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"],
    "6": ["011", "100", "110", "101", "010"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["010", "101", "010", "101", "010"],
    "9": ["010", "101", "011", "001", "110"],
    "$": ["011", "110", "011", "110", "010"],
    ":": ["000", "010", "000", "010", "000"],
    "-": ["000", "000", "111", "000", "000"],
    ",": ["000", "000", "000", "010", "100"],
    ".": ["000", "000", "000", "000", "010"],
    "5x": [],
    " ": ["000", "000", "000", "000", "000"],
}


def draw_text(px, x, y, text, color):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    px[cx + gx, y + gy] = color
        cx += 4
    return cx - x - 1  # text width


def text_width(text):
    return len(text) * 4 - 1


def new_img(w, h, bg=None):
    img = Image.new("RGBA", (w, h), bg or (0, 0, 0, 0))
    return img, img.load()


# ---------------------------------------------------------------- tiles ----
def tile_grass(variant=0):
    img, px = new_img(T, T, GRASS)
    rng = random.Random(variant * 7 + 3)
    for _ in range(5):
        x, y = rng.randrange(1, T - 1), rng.randrange(1, T - 1)
        px[x, y] = GRASS_SPECK
        px[x + 1, y] = GRASS_D
    for _ in range(4):
        x, y = rng.randrange(T), rng.randrange(T)
        px[x, y] = GRASS_D
    return img


TUFT = [
    "X.X.X.X",
    "XXX.XXX",
    ".XXXXX.",
    "XXXXXXX",
    ".XXXXX.",
]


def tile_tall_grass():
    img, px = new_img(T, T, GRASS)
    for (ox, oy) in [(0, 1), (8, 2), (4, 9)]:
        for ty, row in enumerate(TUFT):
            for tx, ch in enumerate(row):
                if ch != "X":
                    continue
                x, y = ox + tx, oy + ty
                if 0 <= x < T and 0 <= y < T:
                    px[x, y] = TALL_D if ty >= 3 else TALL
    return img


def tile_path():
    img, px = new_img(T, T, PATH)
    rng = random.Random(5)
    for _ in range(6):
        x, y = rng.randrange(T), rng.randrange(T)
        px[x, y] = PATH_D
    return img


def tile_path_edge(side):
    """side in n,s,e,w — path tile with grass-facing edge shading."""
    img = tile_path()
    px = img.load()
    for i in range(T):
        if side == "n":
            px[i, 0] = PATH_EDGE
            px[i, 1] = PATH_D
        elif side == "s":
            px[i, T - 1] = PATH_EDGE
        elif side == "w":
            px[0, i] = PATH_EDGE
            px[1, i] = PATH_D
        elif side == "e":
            px[T - 1, i] = PATH_EDGE
    return img


def tile_water(frame=0):
    img, px = new_img(T, T, WATER)
    rng = random.Random(11 + frame)
    for _ in range(3):
        x, y = rng.randrange(1, T - 4), rng.randrange(T)
        for dx in range(3):
            px[x + dx, y] = WATER_L
    for _ in range(2):
        x, y = rng.randrange(1, T - 3), rng.randrange(T)
        for dx in range(2):
            px[x + dx, y] = WATER_D
    return img


def tile_flowers(color):
    img = tile_grass(2)
    px = img.load()
    for (fx, fy) in [(3, 3), (10, 8), (5, 11)]:
        px[fx, fy - 1] = color
        px[fx - 1, fy] = color
        px[fx + 1, fy] = color
        px[fx, fy + 1] = color
        px[fx, fy] = FLOWER_Y if color != FLOWER_Y else FLOWER_W
    return img


def sprite_tree():
    """16x24 round-canopy tree."""
    img, px = new_img(T, 24)
    d = ImageDraw.Draw(img)
    # canopy
    d.ellipse([1, 1, 14, 16], fill=TREE, outline=OUT)
    d.ellipse([3, 3, 9, 9], fill=TREE_L)
    for (x, y) in [(10, 5), (4, 11), (11, 11)]:
        px[x, y] = TREE_L
    for (x, y) in [(6, 13), (9, 14), (12, 9)]:
        px[x, y] = TREE_D
    # bottom shadow of canopy
    d.arc([1, 1, 14, 16], 20, 160, fill=TREE_D)
    # trunk
    d.rectangle([6, 16, 9, 22], fill=TRUNK, outline=OUT)
    px[7, 18] = TRUNK_D
    px[8, 20] = TRUNK_D
    return img


# ------------------------------------------------------------ character ----
PLAYER_DOWN = [
    "................",
    "....KKKKKKKK....",
    "...KHHHHHHHHK...",
    "..KHHHHHHHHHHK..",
    "..KHhHHHHHHHHK..",
    "..KHHHHHHHHHHK..",
    "..KHSSSSSSSSHK..",
    "..KSSESSSSESSK..",
    "..KSSESSSSESSK..",
    "...KSSSssSSSK...",
    "....KssssssK....",
    "...KJJJJJJJJK...",
    "..KJJJjJJjJJJK..",
    "..KSJJJJJJJJSK..",
    "..KKKjJJJJjKKK..",
    "....KPPKKPPK....",
    "....KPPKKPPK....",
    "....KPPKKPPK....",
    "....KBBKKBBK....",
    "....KKKK.KKKK...",
]

PLAYER_UP = [
    "................",
    "....KKKKKKKK....",
    "...KHHHHHHHHK...",
    "..KHHhHHHHHHHK..",
    "..KHHHHHHHHHHK..",
    "..KHHHHHHHHHHK..",
    "..KHHHHHHHHHHK..",
    "..KHHHHHHHHHHK..",
    "..KHHHHHHHHHHK..",
    "...KHHHHHHHHK...",
    "....KssssssK....",
    "...KJJJJJJJJK...",
    "..KJJJJJJJJJJK..",
    "..KSJJjJJjJJSK..",
    "..KKKjJJJJjKKK..",
    "....KPPKKPPK....",
    "....KPPKKPPK....",
    "....KPPKKPPK....",
    "....KBBKKBBK....",
    "....KKKK.KKKK...",
]

PLAYER_LEFT = [
    "................",
    "....KKKKKKKK....",
    "...KHHHHHHHHK...",
    "..KHHHHHHHHHHK..",
    "..KHhHHHHHHHHK..",
    "..KHHHHHHHHHHK..",
    "..KHSSSSSHHHHK..",
    "..KSESSSSHHHHK..",
    "..KSESSSsHHHK...",
    "...KSSSssHHK....",
    "....KssssKK.....",
    "...KJJJJJJK.....",
    "..KJJjJJJJJK....",
    "..KJJJJJJJJK....",
    "..KKSjJJJjKK....",
    "....KPPPPK......",
    "....KPPPPK......",
    "....KPPKPPK.....",
    "....KBBKBBK.....",
    "....KKK.KKK.....",
]


def draw_char_map(rows, keymap=None):
    keymap = keymap or CHAR_KEY
    h = len(rows)
    w = len(rows[0])
    img, px = new_img(w, h)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            c = keymap[ch]
            if c:
                px[x, y] = c
    return img


def walk_frame(base_img, leg="l"):
    """Crude walk frame: raise one leg by shifting its pixels up 1px."""
    img = base_img.copy()
    px = img.load()
    w, h = img.size
    half = w // 2
    x0, x1 = (0, half) if leg == "l" else (half, w)
    for y in range(h - 1, h - 6, -1):
        for x in range(x0, x1):
            px[x, y] = px[x, y - 1]
    for x in range(x0, x1):
        px[x, h - 6] = (0, 0, 0, 0)
    return img


def recolor(img, mapping):
    img = img.copy()
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if c[:3] in mapping and c[3] > 0:
                px[x, y] = mapping[c[:3]]
    return img


def make_player_sheet():
    down = draw_char_map(PLAYER_DOWN)
    up = draw_char_map(PLAYER_UP)
    left = draw_char_map(PLAYER_LEFT)
    right = left.transpose(Image.FLIP_LEFT_RIGHT)
    rows = []
    for base in (down, left, right, up):
        rows.append([walk_frame(base, "l"), base, walk_frame(base, "r")])
    sheet, _ = new_img(16 * 3, 20 * 4)
    for ry, frames in enumerate(rows):
        for rx, f in enumerate(frames):
            sheet.paste(f, (rx * 16, ry * 20), f)
    return sheet, down, up, left, right


def make_npc(base_down):
    return recolor(base_down, {
        HAIR: NPC_HAIR, HAIR_L: (90, 90, 100),
        JACKET: NPC_SHIRT, JACKET_D: (156, 62, 76),
        PANTS: NPC_PANTS,
    })


# ------------------------------------------------------------ buildings ----
def building(w, h, roof, roof_d, wall, wall_d, sign_text=None, win_rows=1,
             door=True, columns=False):
    """Generic Pokemon-ish front-facing building, size in px."""
    img, px = new_img(w, h)
    d = ImageDraw.Draw(img)
    roof_h = max(10, h // 3)
    wall_top = roof_h

    # wall
    d.rectangle([2, wall_top, w - 3, h - 1], fill=wall, outline=OUT)
    # wall shading under roof + left edge
    d.line([3, wall_top + 1, w - 4, wall_top + 1], fill=wall_d)
    d.line([3, wall_top + 1, 3, h - 2], fill=wall_d)
    # roof (slightly wider than wall, with ridge)
    d.polygon([(0, roof_h), (4, 2), (w - 5, 2), (w - 1, roof_h)],
              fill=roof, outline=OUT)
    d.line([(2, roof_h - 2), (w - 3, roof_h - 2)], fill=roof_d)
    d.line([(4, 3), (w - 5, 3)], fill=tuple(min(255, c + 28) for c in roof))
    d.line([(0, roof_h), (w - 1, roof_h)], fill=OUT)
    # eave shadow on wall
    d.line([3, wall_top + 2, w - 4, wall_top + 2], fill=wall_d)

    # windows
    wall_h = h - wall_top
    n_win = max(2, (w - 16) // 18)
    for row in range(win_rows):
        wy = wall_top + 5 + row * 12
        if wy + 8 > h - (12 if door else 4):
            break
        for i in range(n_win):
            wx = 7 + i * ((w - 14 - 8) // max(1, n_win - 1) if n_win > 1 else 0)
            d.rectangle([wx, wy, wx + 7, wy + 7], fill=WIN, outline=OUT)
            d.line([wx + 1, wy + 1, wx + 3, wy + 1], fill=WHITE)
            d.line([wx + 4, wy + 4, wx + 6, wy + 6], fill=WIN_D)
            d.line([wx, wy + 4, wx + 7, wy + 4], fill=OUT)

    # columns (bank style)
    if columns:
        for cx in (6, w - 11):
            d.rectangle([cx, wall_top + 3, cx + 4, h - 2], fill=WALL_STONE,
                        outline=OUT)
            d.line([cx + 1, wall_top + 4, cx + 1, h - 3], fill=WHITE)
            d.line([cx + 3, wall_top + 4, cx + 3, h - 3], fill=WALL_STONE_D)

    # door
    if door:
        dw = 10
        dx = (w - dw) // 2
        d.rectangle([dx, h - 13, dx + dw - 1, h - 1], fill=DOOR, outline=OUT)
        d.line([dx + 1, h - 12, dx + dw - 2, h - 12], fill=DOOR_D)
        d.rectangle([dx + 2, h - 10, dx + dw - 3, h - 5], fill=DOOR_D)
        px[dx + dw - 3, h - 8] = GOLD

    # sign plaque
    if sign_text:
        tw = text_width(sign_text)
        sw = tw + 4
        sx = (w - sw) // 2
        sy = wall_top + 3
        d.rectangle([sx, sy, sx + sw, sy + 8], fill=SIGN_BG, outline=OUT)
        draw_text(px, sx + 3, sy + 2, sign_text, OUT)
    return img


def building_clocktower():
    """Tall centerpiece clock tower, 48x88."""
    w, h = 48, 88
    img, px = new_img(w, h)
    d = ImageDraw.Draw(img)
    # tower body
    d.rectangle([10, 26, w - 11, h - 1], fill=WALL_STONE, outline=OUT)
    d.line([11, 27, 11, h - 2], fill=WALL_STONE_D)
    d.line([12, 27, w - 12, 27], fill=WALL_STONE_D)
    # spire roof
    d.polygon([(6, 26), (w // 2, 2), (w - 7, 26)], fill=ROOF_B, outline=OUT)
    d.polygon([(12, 26), (w // 2, 8), (w - 13, 26)], fill=ROOF_B_D)
    d.line([(6, 26), (w - 7, 26)], fill=OUT)
    # finial
    d.line([(w // 2, 2), (w // 2, 0)], fill=GOLD)
    px[w // 2, 0] = GOLD
    # clock face
    cx, cy, r = w // 2, 40, 9
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CLOCKFACE, outline=OUT)
    d.ellipse([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], outline=GOLD)
    for (mx, my) in [(cx, cy - r + 2), (cx, cy + r - 2), (cx - r + 2, cy),
                     (cx + r - 2, cy)]:
        px[mx, my] = OUT
    d.line([cx, cy, cx, cy - 5], fill=OUT)        # minute hand
    d.line([cx, cy, cx + 4, cy + 1], fill=OUT)    # hour hand
    px[cx, cy] = GOLD_D
    # lower window + door
    d.rectangle([cx - 4, 56, cx + 4, 63], fill=WIN, outline=OUT)
    d.line([cx - 3, 57, cx - 1, 57], fill=WHITE)
    d.rectangle([cx - 5, h - 14, cx + 5, h - 1], fill=DOOR, outline=OUT)
    d.rectangle([cx - 3, h - 11, cx + 3, h - 5], fill=DOOR_D)
    px[cx + 3, h - 8] = GOLD
    # stone banding
    for by in (52, 68):
        d.line([11, by, w - 12, by], fill=WALL_STONE_D)
    return img


def building_garage():
    """Startup garage, 56x44: small house + big garage door."""
    w, h = 56, 44
    img, px = new_img(w, h)
    d = ImageDraw.Draw(img)
    roof_h = 14
    d.rectangle([2, roof_h, w - 3, h - 1], fill=WALL, outline=OUT)
    d.line([3, roof_h + 1, w - 4, roof_h + 1], fill=WALL_D)
    d.polygon([(0, roof_h), (4, 2), (w - 5, 2), (w - 1, roof_h)],
              fill=ROOF_T, outline=OUT)
    d.line([(2, roof_h - 2), (w - 3, roof_h - 2)], fill=ROOF_T_D)
    d.line([(4, 3), (w - 5, 3)], fill=(116, 196, 180))
    d.line([(0, roof_h), (w - 1, roof_h)], fill=OUT)
    # garage door with slats
    d.rectangle([6, 22, 29, h - 1], fill=(170, 170, 182), outline=OUT)
    for sy in range(24, h - 2, 3):
        d.line([7, sy, 28, sy], fill=(132, 132, 146))
    # window
    d.rectangle([36, 24, 45, 32], fill=WIN, outline=OUT)
    d.line([37, 25, 40, 25], fill=WHITE)
    d.line([36, 28, 45, 28], fill=OUT)
    # sign
    tw = text_width("STARTUP")
    sx = (w - tw - 4) // 2
    d.rectangle([sx, 15, sx + tw + 4, 23], fill=SIGN_BG, outline=OUT)
    draw_text(px, sx + 3, 17, "STARTUP", OUT)
    return img


# ---------------------------------------------------------------- scene ----
MAP_W, MAP_H = 30, 20


def build_scene():
    scene, _ = new_img(MAP_W * T, MAP_H * T)

    # --- terrain layer ---------------------------------------------------
    grass_tiles = [tile_grass(v) for v in range(4)]
    path = tile_path()
    water = [tile_water(f) for f in range(2)]
    tall = tile_tall_grass()
    flowers_r = tile_flowers(FLOWER_R)
    flowers_w = tile_flowers(FLOWER_W)

    grid = [["g"] * MAP_W for _ in range(MAP_H)]

    def rect(x0, y0, x1, y1, ch):
        for yy in range(y0, y1 + 1):
            for xx in range(x0, x1 + 1):
                if 0 <= xx < MAP_W and 0 <= yy < MAP_H:
                    grid[yy][xx] = ch

    # pond bottom-left
    rect(2, 15, 7, 18, "w")
    rect(3, 14, 6, 14, "w")
    # main horizontal path
    rect(1, 10, 28, 11, "p")
    # vertical path: tower plaza down to bottom
    rect(13, 6, 16, 17, "p")
    # branch to bank (left building) and office (right building)
    rect(4, 8, 13, 9, "p")
    rect(16, 8, 25, 9, "p")
    # branch to garage
    rect(22, 12, 24, 16, "p")
    # plaza in front of tower
    rect(12, 8, 17, 9, "p")
    # tall grass patches
    rect(8, 13, 11, 15, "t")
    rect(18, 3, 20, 5, "t")
    # flowers
    for (fx, fy, ch) in [(10, 12, "f"), (17, 13, "F"), (11, 16, "f"),
                         (26, 10, "F"), (2, 12, "f"), (27, 6, "f"),
                         (19, 16, "F"), (6, 5, "f")]:
        if grid[fy][fx] == "g":
            grid[fy][fx] = ch

    rng = random.Random(7)
    for y in range(MAP_H):
        for x in range(MAP_W):
            ch = grid[y][x]
            if ch == "g":
                img = grass_tiles[rng.randrange(4)]
            elif ch == "p":
                img = path
            elif ch == "w":
                img = water[(x + y) % 2]
            elif ch == "t":
                img = tall
            elif ch == "f":
                img = flowers_r
            else:
                img = flowers_w
            scene.paste(img, (x * T, y * T))

    d = ImageDraw.Draw(scene)
    # path edges (simple pass: darken path pixels bordering grass)
    px = scene.load()
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x] != "p":
                continue
            for (dx, dy) in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_W and 0 <= ny < MAP_H and \
                        grid[ny][nx] in ("g", "t", "f", "F"):
                    if dy == -1:
                        d.line([x * T, y * T, x * T + 15, y * T],
                               fill=PATH_EDGE)
                    elif dy == 1:
                        d.line([x * T, y * T + 15, x * T + 15, y * T + 15],
                               fill=PATH_EDGE)
                    elif dx == -1:
                        d.line([x * T, y * T, x * T, y * T + 15],
                               fill=PATH_EDGE)
                    else:
                        d.line([x * T + 15, y * T, x * T + 15, y * T + 15],
                               fill=PATH_EDGE)
    # pond edge
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x] != "w":
                continue
            for (dx, dy) in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_W and 0 <= ny < MAP_H and grid[ny][nx] != "w":
                    if dy == -1:
                        d.line([x * T, y * T, x * T + 15, y * T], fill=WATER_D)
                        d.line([x * T, y * T + 1, x * T + 15, y * T + 1],
                               fill=WATER_L)
                    elif dy == 1:
                        d.line([x * T, y * T + 15, x * T + 15, y * T + 15],
                               fill=WATER_D)
                    elif dx == -1:
                        d.line([x * T, y * T, x * T, y * T + 15], fill=WATER_D)
                    else:
                        d.line([x * T + 15, y * T, x * T + 15, y * T + 15],
                               fill=WATER_D)

    # --- props & buildings ----------------------------------------------
    tree = sprite_tree()

    def paste(img, tx, ty):
        """Paste with bottom-left anchored at tile (tx,ty) bottom."""
        scene.paste(img, (tx * T, (ty + 1) * T - img.size[1]), img)

    bank = building(72, 52, ROOF_B, ROOF_B_D, WALL_STONE, WALL_STONE_D,
                    sign_text="BANK", columns=True)
    office = building(76, 60, ROOF_G, ROOF_G_D, WALL, WALL_D,
                      sign_text="9-5 INC", win_rows=2)
    house = building(52, 44, ROOF_R, ROOF_R_D, WALL, WALL_D)
    tower = building_clocktower()
    garage = building_garage()

    # border trees (top, sides)
    for x in range(0, MAP_W, 2):
        paste(tree, x, 1)
    for y in range(3, MAP_H, 2):
        paste(tree, 0, y) if y not in (15, 17) else None
        paste(tree, MAP_W - 1, y)
    for x in range(0, MAP_W, 2):
        if not (2 <= x <= 7) and not (13 <= x <= 16) and not (22 <= x <= 24):
            paste(tree, x, MAP_H - 1)

    scene.paste(bank, (4 * T, 8 * T - bank.size[1]), bank)
    scene.paste(office, (21 * T, 8 * T - office.size[1]), office)
    scene.paste(tower, (int(13.5 * T), 8 * T - tower.size[1]), tower)
    scene.paste(house, (8 * T, 8 * T - house.size[1] - 4), house) if False else None
    scene.paste(garage, (21 * T + 8, 12 * T + garage.size[1] - garage.size[1]), garage)

    # a couple of loose trees inside
    paste(tree, 10, 5)
    paste(tree, 2, 13)
    paste(tree, 27, 13)

    # --- characters -------------------------------------------------------
    sheet, down, up, left, right = make_player_sheet()
    npc = make_npc(down)
    # player on the vertical path
    scene.paste(down, (14 * T + 4, 12 * T + 8), down)
    # npc near the bank
    scene.paste(npc, (7 * T, 9 * T + 6), npc)

    return scene, sheet, down


# ------------------------------------------------------------------- ui ----
def add_ui(scene):
    img = scene.copy()
    px = img.load()
    d = ImageDraw.Draw(img, "RGBA")
    panel = (252, 250, 240, 255)

    # top-left: day/time panel
    d.rectangle([4, 4, 78, 21], fill=panel, outline=OUT)
    d.line([5, 20, 77, 20], fill=(210, 200, 176))
    # tiny clock icon
    d.ellipse([8, 7, 18, 17], fill=CLOCKFACE, outline=OUT)
    d.line([13, 12, 13, 9], fill=OUT)
    d.line([13, 12, 16, 12], fill=OUT)
    draw_text(px, 23, 7, "DAY 3", OUT)
    draw_text(px, 23, 14, "08:42", (72, 112, 180))

    # top-right: money panel
    w = img.size[0]
    d.rectangle([w - 70, 4, w - 5, 15], fill=panel, outline=OUT)
    d.ellipse([w - 66, 6, w - 59, 13], fill=GOLD, outline=GOLD_D)
    draw_text(px, w - 63, 7, "$", OUT)
    draw_text(px, w - 55, 7, "1,250", OUT)

    # bottom dialogue box
    h = img.size[1]
    d.rectangle([8, h - 42, w - 9, h - 6], fill=panel, outline=OUT)
    d.rectangle([10, h - 40, w - 11, h - 8], outline=(210, 200, 176))
    draw_text(px, 16, h - 34, "TIME IS MONEY. SPEND", OUT)
    draw_text(px, 16, h - 26, "BOTH WISELY.", OUT)
    draw_text(px, w - 24, h - 14, "-", (72, 112, 180))
    return img


def upscale(img, k=3):
    return img.resize((img.size[0] * k, img.size[1] * k), Image.NEAREST)


def make_tileset():
    tiles = [tile_grass(0), tile_grass(1), tile_grass(2), tile_grass(3),
             tile_tall_grass(), tile_path(), tile_path_edge("n"),
             tile_path_edge("s"), tile_path_edge("w"), tile_path_edge("e"),
             tile_water(0), tile_water(1), tile_flowers(FLOWER_R),
             tile_flowers(FLOWER_W)]
    cols = 7
    rows = (len(tiles) + cols - 1) // cols
    sheet, _ = new_img(cols * T, rows * T)
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * T, (i // cols) * T))
    return sheet


def main():
    scene, player_sheet, player_down = build_scene()
    mock = add_ui(scene)

    os.makedirs(os.path.join(ART, "Showcase"), exist_ok=True)
    os.makedirs(os.path.join(ART, "Tiles"), exist_ok=True)
    os.makedirs(os.path.join(ART, "Characters"), exist_ok=True)
    os.makedirs(os.path.join(ART, "Buildings"), exist_ok=True)

    upscale(mock, 3).save(os.path.join(ART, "Showcase", "clockwise_mockup.png"))
    mock.save(os.path.join(ART, "Showcase", "clockwise_mockup_1x.png"))

    make_tileset().save(os.path.join(ART, "Tiles", "terrain_tileset.png"))
    player_sheet.save(os.path.join(ART, "Characters", "player_walk.png"))
    make_npc(player_down).save(os.path.join(ART, "Characters", "npc_banker.png"))

    building(72, 52, ROOF_B, ROOF_B_D, WALL_STONE, WALL_STONE_D,
             sign_text="BANK", columns=True).save(
        os.path.join(ART, "Buildings", "bank.png"))
    building(76, 60, ROOF_G, ROOF_G_D, WALL, WALL_D, sign_text="9-5 INC",
             win_rows=2).save(os.path.join(ART, "Buildings", "office.png"))
    building_clocktower().save(os.path.join(ART, "Buildings", "clocktower.png"))
    building_garage().save(os.path.join(ART, "Buildings", "garage.png"))
    sprite_tree().save(os.path.join(ART, "Buildings", "tree.png"))

    print("done")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Space Shooter - เกมยิงยานอวกาศ เขียนด้วย tkinter เพียวๆ
ไม่ต้องติดตั้ง library อะไรเพิ่มเลย (ใช้แค่ของที่มากับ Python)

วิธีเล่น:
    python main.py

ปุ่มควบคุม:
    ลูกศร / WASD     บังคับยาน
    Space / J        ยิง (กดค้างได้)
    X / Shift / K    ใช้สกิลพิเศษของยาน
    P / Esc          พักเกม
    Enter            เริ่มเกม / เล่นใหม่

หน้าเลือกยาน:
    ← →  เลือก     ↑ ↓  สลับแถวยาน/อาวุธ     Enter  เริ่ม     (คลิกเมาส์ได้)
"""

import json
import math
import os
import random
import time
import tkinter as tk

# ---------------------------------------------------------------- ค่าคงที่
W, H = 800, 620
TICK = 16                      # ms ต่อเฟรม (~60 fps)

BG = "#05060f"
CYAN = "#4fd2ff"
HOT = "#ff4d6d"
GOLD = "#ffd84d"
DIM = "#5f6f94"

FONT = "Consolas"
FONT_TH = "Tahoma"             # ฟอนต์ที่มีอักษรไทยบน Windows

FIRE_PALETTE = ["#fffbe6", "#ffe36b", "#ffa52b", "#ff5a2b", "#b32020", "#5a1010"]
SPARK_PALETTE = ["#eafaff", "#9fe8ff", "#4fd2ff", "#2a86ff", "#17408f", "#0b1a3a"]
GOLD_PALETTE = ["#fff6c9", "#ffe36b", "#ffc23d", "#b8860b", "#5c430a"]
SMOKE_PALETTE = ["#e8eef7", "#aab4c4", "#6f7a8c", "#3c4352", "#1d212b"]

SAVE_PATH = os.path.join(os.path.expanduser("~"), ".space_shooter_save.json")

# ---------------------------------------------------------------- ยานให้เลือก
# รูปทรงเป็นพิกัดหน่วย (คูณด้วยขนาดยานตอนวาด)
SHIPS = [
    {
        "name": "FALCON", "title": "ยานจู่โจมความเร็วสูง",
        "desc": "เร็วที่สุด ตัวเล็กหลบง่าย แต่เกราะบาง",
        "speed": 7.4, "lives": 2, "hitbox": 8, "power": 0.9,
        "skill": "dash", "skill_name": "DASH", "skill_cd": 150,
        "skill_desc": "พุ่งตัวหลบไปทางที่กำลังบิน + อมตะชั่วครู่",
        "color": "#7ef9ff", "wing": "#1b9bff", "flame_w": 0.3, "flame_y": 0.5,
        "body": [(0, -1.6), (-0.4, 0.7), (0, 0.35), (0.4, 0.7)],
        "wings": [(0, -0.5), (-1.5, 0.75), (-1.1, 1.0), (0, 0.55),
                  (1.1, 1.0), (1.5, 0.75)],
        "stats": (5, 2, 3, 4),
    },
    {
        "name": "NOVA", "title": "ยานรบอเนกประสงค์",
        "desc": "สมดุลทุกด้าน เหมาะกับมือใหม่",
        "speed": 5.6, "lives": 3, "hitbox": 12, "power": 1.0,
        "skill": "emp", "skill_name": "EMP", "skill_cd": 720,
        "skill_desc": "คลื่นพลังล้างกระสุนศัตรูทั้งจอ + ดาเมจศัตรูทุกตัว",
        "color": CYAN, "wing": "#1b6dff", "flame_w": 0.36, "flame_y": 0.64,
        "body": [(0, -1.35), (-0.72, 0.8), (0, 0.3), (0.72, 0.8)],
        "wings": [(0, -0.2), (-1.3, 0.95), (-0.45, 0.55), (0.45, 0.55),
                  (1.3, 0.95)],
        "stats": (3, 3, 3, 3),
    },
    {
        "name": "TITAN", "title": "ยานป้อมปราการหนัก",
        "desc": "ช้าแต่ถึก ชีวิตเยอะ ยิงแรงกว่าลำอื่น",
        "speed": 4.3, "lives": 4, "hitbox": 15, "power": 1.25,
        "skill": "barrier", "skill_name": "BARRIER", "skill_cd": 840,
        "skill_desc": "โล่พลังงาน 4.5 วิ ดูดกระสุนและเผาศัตรูที่เข้าใกล้",
        "color": "#ffb347", "wing": "#a0522d", "flame_w": 0.55, "flame_y": 0.95,
        "body": [(0, -1.2), (-0.5, -0.7), (-0.9, 0.4), (-0.6, 0.95),
                 (0.6, 0.95), (0.9, 0.4), (0.5, -0.7)],
        "wings": [(-0.8, -0.3), (-1.6, 0.2), (-1.6, 1.0), (-0.7, 0.8),
                  (0.7, 0.8), (1.6, 1.0), (1.6, 0.2), (0.8, -0.3)],
        "stats": (2, 5, 4, 3),
    },
]

# ---------------------------------------------------------------- อาวุธให้เลือก
WEAPONS = [
    {
        "name": "BLASTER", "title": "ปืนเลเซอร์คู่", "kind": "blaster",
        "desc": "ยิงตรงคู่ เสถียร ใช้ง่าย อัปเกรดแล้วยิงเฉียงเพิ่ม",
        "cd": 8, "dmg": 1.0, "color": CYAN, "stats": (3, 4, 2),
    },
    {
        "name": "SCATTER", "title": "ปืนลูกซองอวกาศ", "kind": "scatter",
        "desc": "กระจายเป็นวงกว้าง ระยะสั้น ยิ่งเข้าประชิดยิ่งแรง",
        "cd": 17, "dmg": 1.0, "color": "#ffb347", "stats": (5, 2, 4),
    },
    {
        "name": "PIERCER", "title": "ลำแสงทะลุทะลวง", "kind": "laser",
        "desc": "ลำแสงรัวเร็ว ทะลุศัตรูได้หลายตัว แต่ดาเมจต่อนัดต่ำ",
        "cd": 4, "dmg": 0.45, "color": "#c77dff", "stats": (2, 5, 3),
    },
    {
        "name": "SEEKER", "title": "มิสไซล์นำวิถี", "kind": "missile",
        "desc": "มิสไซล์ไล่ล่าเป้าหมายเอง ยิงช้าแต่ระเบิดเป็นวงกว้าง",
        "cd": 26, "dmg": 2.4, "color": "#b0ff5a", "stats": (4, 1, 5),
    },
]

# ---------------------------------------------------------------- ไอเทม
#        ตัวอักษร: (สี, ชนิด, น้ำหนักโอกาสดรอป)
POWERUPS = {
    "P": (GOLD, "power", 30),
    "R": ("#b0ff5a", "rapid", 20),
    "O": ("#ffb347", "shield", 20),
    "E": ("#7ef9ff", "energy", 18),
    "+": ("#ff6b9d", "life", 12),
}
POWERUP_LETTERS = list(POWERUPS.keys())
POWERUP_WEIGHTS = [POWERUPS[k][2] for k in POWERUP_LETTERS]


# ---------------------------------------------------------------- ฟังก์ชันช่วย
def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def is_thai(text):
    return any(u"฀" <= ch <= u"๿" for ch in text)


def font_for(text, size, bold=True):
    fam = FONT_TH if is_thai(text) else FONT
    return (fam, size, "bold") if bold else (fam, size)


def ship_coords(points, x, y, s):
    out = []
    for px, py in points:
        out.append(x + px * s)
        out.append(y + py * s)
    return out


def draw_ship(c, ship, x, y, s, tags):
    """วาดยานแบบนิ่งๆ (ใช้ในหน้าเลือกยาน)"""
    fw, fy = ship["flame_w"] * s, ship["flame_y"] * s
    c.create_polygon(x - fw, y + fy, x + fw, y + fy, x, y + fy + s * 1.1,
                     fill="#ff8a2b", outline="", tags=tags)
    c.create_polygon(ship_coords(ship["wings"], x, y, s), fill=ship["wing"],
                     outline="", tags=tags)
    c.create_polygon(ship_coords(ship["body"], x, y, s), fill=ship["color"],
                     outline="#eafaff", tags=tags)
    c.create_oval(x - 0.28 * s, y - 0.8 * s, x + 0.28 * s, y - 0.15 * s,
                  fill="#fff4b0", outline="", tags=tags)


def draw_weapon_icon(c, w, x, y, tags):
    col, kind = w["color"], w["kind"]
    if kind == "blaster":
        for dx in (-8, 8):
            c.create_oval(x + dx - 4, y - 11, x + dx + 4, y + 11,
                          outline=col, width=2, tags=tags)
            c.create_oval(x + dx - 1.5, y - 6, x + dx + 1.5, y + 6,
                          fill="#ffffff", outline="", tags=tags)
    elif kind == "scatter":
        for ring, d in ((0, 10), (1, 21)):
            for i in range(5 + ring * 2):
                n = 5 + ring * 2
                a = math.radians(-90 + (i - (n - 1) / 2.0) * (60.0 / (n - 1)))
                px, py = x + math.cos(a) * d, y + 12 + math.sin(a) * d
                c.create_oval(px - 2.5, py - 2.5, px + 2.5, py + 2.5,
                              fill=col, outline="", tags=tags)
    elif kind == "laser":
        for dx, wd in ((-11, 3), (0, 6), (11, 3)):
            c.create_line(x + dx, y + 14, x + dx, y - 16, fill=col, width=wd,
                          capstyle="round", tags=tags)
        c.create_line(x, y + 14, x, y - 16, fill="#ffffff", width=2, tags=tags)
    else:
        for dx in (-10, 10):
            x2 = x + dx * 1.6
            c.create_line(x + dx, y + 12, x2, y - 10, fill=col, width=4, tags=tags)
            c.create_oval(x2 - 3, y - 13, x2 + 3, y - 7, fill="#ffffff",
                          outline="", tags=tags)
            for k in range(3):
                sy = y + 16 + k * 5
                c.create_oval(x + dx - 2, sy - 2, x + dx + 2, sy + 2,
                              fill=SMOKE_PALETTE[k + 1], outline="", tags=tags)


def draw_stat(c, x, y, label, value, color, seg_x, seg_w, tags):
    c.create_text(x, y, text=label, anchor="w", fill="#8fa3c8",
                  font=(FONT, 8, "bold"), tags=tags)
    for i in range(5):
        sx = seg_x + i * (seg_w + 3)
        c.create_rectangle(sx, y - 4, sx + seg_w, y + 4,
                           fill=color if i < value else "#1a2240",
                           outline="", tags=tags)


def load_save():
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def write_save(data):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        pass


def safe_int(v, default):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------- ฐานของวัตถุ
class Entity(object):
    """วัตถุในเกมทุกชิ้น ถือ canvas item ของตัวเอง แล้วย้ายพิกัดทุกเฟรม"""

    def __init__(self, game, x, y, r):
        self.g = game
        self.c = game.canvas
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.r = r
        self.alive = True
        self.ids = []

    def kill(self):
        if self.alive:
            self.alive = False
            for i in self.ids:
                self.c.delete(i)
            self.ids = []

    def hits(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        rr = self.r + other.r
        return dx * dx + dy * dy <= rr * rr

    def offscreen(self, pad=60):
        return (self.x < -pad or self.x > W + pad or
                self.y < -pad or self.y > H + pad)

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def redraw(self):
        pass


# ---------------------------------------------------------------- ยานผู้เล่น
class Player(Entity):
    SIZE = 14

    def __init__(self, game, ship, weapon):
        Entity.__init__(self, game, W / 2, H - 90, ship["hitbox"])
        self.ship = ship
        self.weapon = weapon
        self.speed = ship["speed"]
        self.level = 1               # เลเวลอาวุธ 1-3
        self.cool = 0
        self.rapid = 0               # ทุกตัวนับเป็นเฟรมที่เหลือ
        self.shield = 0
        self.barrier = 0
        self.invuln = 100
        self.dash = 0
        self.dash_v = (0.0, 0.0)
        self.dir = (0.0, -1.0)       # ทิศทางล่าสุดที่บิน (ใช้กับ DASH)
        self.charge = ship["skill_cd"]
        self.thrust = False
        self.side = 1
        c = self.c
        self.ids = [
            c.create_polygon(0, 0, 0, 0, 0, 0, fill="#ff8a2b", outline=""),        # เปลวไฟ
            c.create_polygon(0, 0, 0, 0, 0, 0, fill=ship["wing"], outline=""),     # ปีก
            c.create_polygon(0, 0, 0, 0, 0, 0, fill=ship["color"],
                             outline="#eafaff"),                                    # ลำตัว
            c.create_oval(0, 0, 0, 0, fill="#fff4b0", outline=""),                 # ห้องนักบิน
            c.create_oval(0, 0, 0, 0, outline="", width=2),                        # โล่
        ]

    @property
    def skill_ready(self):
        return self.charge >= self.ship["skill_cd"]

    def control(self, keys):
        dx = dy = 0.0
        if "left" in keys:
            dx -= 1
        if "right" in keys:
            dx += 1
        if "up" in keys:
            dy -= 1
        if "down" in keys:
            dy += 1
        if dx or dy:
            n = math.hypot(dx, dy)
            dx, dy = dx / n, dy / n
            self.dir = (dx, dy)
        self.thrust = dy < 0 or self.dash > 0
        if self.dash > 0:
            self.vx, self.vy = self.dash_v
        else:
            self.vx = dx * self.speed
            self.vy = dy * self.speed

    def update(self):
        Entity.update(self)
        self.x = clamp(self.x, 22, W - 22)
        self.y = clamp(self.y, 70, H - 30)
        for a in ("cool", "rapid", "shield", "barrier", "invuln", "dash"):
            v = getattr(self, a)
            if v > 0:
                setattr(self, a, v - 1)
        if self.charge < self.ship["skill_cd"]:
            self.charge += 1
        if self.dash > 0:
            self.g.spawn_sparks(self.x, self.y + 4, 2, SPARK_PALETTE,
                                spread=0.8, life=14, size=4)

    def shoot(self):
        if self.cool > 0:
            return
        w, g, lv = self.weapon, self.g, self.level
        dmg = w["dmg"] * self.ship["power"]
        col = w["color"]
        x, y = self.x, self.y - 18
        self.cool = w["cd"] * (0.6 if self.rapid else 1.0)

        if w["kind"] == "blaster":
            pattern = {1: ((-7, 0), (7, 0)),
                       2: ((-7, 0), (7, 0), (-11, -7), (11, 7)),
                       3: ((-9, 0), (0, 0), (9, 0), (-13, -9), (13, 9))}[lv]
            for dx, ang in pattern:
                g.add_pbullet(x + dx, y, ang, 12.5, dmg, col)

        elif w["kind"] == "scatter":
            n = 3 + 2 * lv
            spread = 22 + 6 * lv
            for i in range(n):
                ang = -spread + 2.0 * spread * i / (n - 1) + random.uniform(-3, 3)
                g.add_pbullet(x, y, ang, random.uniform(10, 12.5), dmg, col,
                              life=19 + 3 * lv)

        elif w["kind"] == "laser":
            pattern = {1: ((0, 0),),
                       2: ((-6, 0), (6, 0)),
                       3: ((-9, -3), (0, 0), (9, 3))}[lv]
            for dx, ang in pattern:
                g.add_pbullet(x + dx, y - 6, ang, 17, dmg, col, style="beam",
                              rad=4, pierce=1 + lv)

        else:  # missile
            if lv == 1:
                self.side = -self.side
                launch = ((self.side * 14, self.side * 28),)
            elif lv == 2:
                launch = ((-14, -28), (14, 28))
            else:
                launch = ((-14, -28), (0, 0), (14, 28))
            for dx, ang in launch:
                g.add_pbullet(x + dx, y + 8, ang, 5.5, dmg, col, style="missile",
                              rad=5, life=170, homing=0.11, splash=44)

        g.spawn_sparks(x, y, 3, SPARK_PALETTE, spread=1.5, life=8)

    def take_hit(self):
        """คืน True ถ้าโดนจริง (เสียชีวิต 1 ดวง)"""
        if self.invuln > 0 or self.barrier > 0 or self.dash > 0:
            return False
        if self.shield > 0:
            self.shield = 0
            self.invuln = 60
            self.g.spawn_sparks(self.x, self.y, 26, SPARK_PALETTE, spread=4.5, life=26)
            return False
        self.invuln = 110
        self.rapid = 0
        self.level = max(1, self.level - 1)
        return True

    def redraw(self):
        c, x, y, s, sh = self.c, self.x, self.y, self.SIZE, self.ship
        f = random.uniform(0.75, 1.6) if self.thrust else random.uniform(0.25, 0.7)
        fw, fy = sh["flame_w"] * s, sh["flame_y"] * s
        c.coords(self.ids[0], x - fw, y + fy, x + fw, y + fy, x, y + fy + 15 * f)
        c.coords(self.ids[1], *ship_coords(sh["wings"], x, y, s))
        c.coords(self.ids[2], *ship_coords(sh["body"], x, y, s))
        c.coords(self.ids[3], x - 0.28 * s, y - 0.8 * s, x + 0.28 * s, y - 0.15 * s)

        # กะพริบตอนอมตะชั่วคราว
        blink = self.invuln > 0 and (self.invuln // 4) % 2 == 0
        c.itemconfig(self.ids[2], fill="#13314d" if blink else sh["color"])
        c.itemconfig(self.ids[1], fill="#102a52" if blink else sh["wing"])

        ring = self.ids[4]
        if self.barrier > 0:
            r = 34 + math.sin(self.barrier * 0.3) * 2
            col = GOLD if self.barrier > 60 or (self.barrier // 5) % 2 else "#7a5c10"
            c.itemconfig(ring, outline=col, width=3)
            c.coords(ring, x - r, y - r, x + r, y + r)
        elif self.shield > 0:
            col = "#7ef9ff" if (self.shield // 5) % 2 == 0 else "#2a86ff"
            c.itemconfig(ring, outline=col, width=2)
            c.coords(ring, x - 27, y - 27, x + 27, y + 27)
        else:
            c.itemconfig(ring, outline="")
            c.coords(ring, -60, -60, -50, -50)


# ---------------------------------------------------------------- กระสุน
class Bullet(Entity):
    """กระสุนทุกแบบ: orb (ลูกกลม), beam (ลำแสงทะลุ), missile (นำวิถี)"""

    def __init__(self, game, x, y, vx, vy, friendly, color, rad=3, dmg=1.0,
                 style="orb", life=0, pierce=0, homing=0.0, splash=0):
        Entity.__init__(self, game, x, y, rad)
        self.vx, self.vy = vx, vy
        self.friendly = friendly
        self.dmg = dmg
        self.style = style
        self.life = life             # 0 = บินจนออกจอ
        self.pierce = pierce         # ทะลุได้อีกกี่ตัว
        self.homing = homing         # มุมเลี้ยวสูงสุดต่อเฟรม (เรเดียน)
        self.splash = splash         # รัศมีระเบิด
        self.maxspeed = math.hypot(vx, vy) * (1.9 if homing else 1.0)
        self.hit = set()
        self.target = None
        self.age = 0
        c = self.c
        if style == "beam":
            self.ids = [c.create_line(0, 0, 0, 0, fill=color, width=5, capstyle="round"),
                        c.create_line(0, 0, 0, 0, fill="#ffffff", width=2)]
        elif style == "missile":
            self.ids = [c.create_line(0, 0, 0, 0, fill=color, width=4),
                        c.create_oval(0, 0, 0, 0, fill="#ffffff", outline="")]
        else:
            self.ids = [c.create_oval(0, 0, 0, 0, fill="", outline=color),
                        c.create_oval(0, 0, 0, 0, fill="#ffffff" if friendly else color,
                                      outline="")]

    def update(self):
        self.age += 1
        if self.homing:
            if self.target is None or not self.target.alive or self.age % 10 == 0:
                self.target = self.g.nearest_enemy(self.x, self.y)
            cur = math.atan2(self.vy, self.vx)
            if self.target is not None:
                want = math.atan2(self.target.y - self.y, self.target.x - self.x)
                diff = (want - cur + math.pi) % (2 * math.pi) - math.pi
                cur += clamp(diff, -self.homing, self.homing)
            sp = min(self.maxspeed, math.hypot(self.vx, self.vy) + 0.3)
            self.vx, self.vy = math.cos(cur) * sp, math.sin(cur) * sp
            if self.age % 2 == 0:
                self.g.spawn_sparks(self.x - self.vx, self.y - self.vy, 1,
                                    SMOKE_PALETTE, spread=0.4, life=16, size=2.5)
        Entity.update(self)
        if self.life:
            self.life -= 1
            if self.life <= 0:
                self.kill()
                return
        if self.offscreen(30):
            self.kill()

    def redraw(self):
        c, x, y = self.c, self.x, self.y
        if self.style == "beam":
            tx, ty = x - self.vx * 1.5, y - self.vy * 1.5
            c.coords(self.ids[0], tx, ty, x, y)
            c.coords(self.ids[1], tx, ty, x, y)
        elif self.style == "missile":
            sp = math.hypot(self.vx, self.vy) or 1.0
            ux, uy = self.vx / sp, self.vy / sp
            c.coords(self.ids[0], x - ux * 11, y - uy * 11, x, y)
            c.coords(self.ids[1], x - 2.5, y - 2.5, x + 2.5, y + 2.5)
        else:
            r = self.r
            c.coords(self.ids[0], x - r * 1.9, y - r * 2.4, x + r * 1.9, y + r * 2.4)
            c.coords(self.ids[1], x - r * 0.75, y - r * 1.4, x + r * 0.75, y + r * 1.4)


# ---------------------------------------------------------------- ศัตรู
ENEMY_SPEC = {
    #            hp  r   score  outline    fill
    "grunt":   (1, 14, 100, "#ff8f6b", "#8f2f1f"),
    "zig":     (2, 15, 160, "#ffd84d", "#8f6a10"),
    "shooter": (3, 16, 260, "#ff4d6d", "#7a1030"),
    "tank":    (9, 23, 480, "#b388ff", "#3b2470"),
}


class Enemy(Entity):
    def __init__(self, game, kind, x, y):
        hp, r, score, outline, fill = ENEMY_SPEC[kind]
        Entity.__init__(self, game, x, y, r)
        self.kind = kind
        self.hp = self.maxhp = float(hp + game.wave // 4)
        self.score = score
        self.flash = 0
        self.t = random.random() * 6.28
        self.fire_cd = random.randint(50, 110)
        self.hover_y = random.randint(90, 230)

        if kind == "grunt":
            self.vy = 1.7 + game.wave * 0.07
        elif kind == "zig":
            self.vy = 1.5 + game.wave * 0.06
            self.vx = random.choice((-2.4, 2.4))
        elif kind == "shooter":
            self.vy = 1.9
        else:
            self.vy = 1.1

        c = self.c
        self.ids = [
            c.create_polygon(0, 0, 0, 0, 0, 0, fill=fill, outline=outline, width=2),
            c.create_oval(0, 0, 0, 0, fill=outline, outline=""),
            c.create_rectangle(0, 0, 0, 0, fill="#2a0d18", outline=""),     # หลอดเลือด
            c.create_rectangle(0, 0, 0, 0, fill=outline, outline=""),
        ]
        self.fill = fill

    def points(self):
        """รูปทรงตามชนิดของศัตรู"""
        x, y, r = self.x, self.y, self.r
        if self.kind == "grunt":
            return (x, y + r, x - r, y - r * 0.7, x, y - r * 0.25, x + r, y - r * 0.7)
        if self.kind == "zig":
            return (x - r, y, x - r * 0.4, y - r, x + r * 0.4, y - r,
                    x + r, y, x + r * 0.4, y + r, x - r * 0.4, y + r)
        if self.kind == "shooter":
            return (x, y + r * 1.1, x - r * 1.15, y + r * 0.1, x - r * 0.5, y - r,
                    x + r * 0.5, y - r, x + r * 1.15, y + r * 0.1)
        return (x - r, y - r * 0.6, x, y - r, x + r, y - r * 0.6,
                x + r * 0.7, y + r * 0.8, x - r * 0.7, y + r * 0.8)

    def update(self):
        self.t += 0.05
        if self.kind == "grunt":
            self.vx = math.sin(self.t) * 1.9
        elif self.kind == "zig":
            if self.x < self.r + 6 or self.x > W - self.r - 6:
                self.vx = -self.vx
        elif self.kind == "shooter":
            if self.y >= self.hover_y:
                self.vy = 0
                self.vx = math.sin(self.t * 0.7) * 2.6
                self.fire_cd -= 1
                if self.fire_cd <= 0:
                    self.fire_cd = random.randint(70, 130)
                    self.g.aimed_shot(self.x, self.y + 14, 3.6, HOT)
        else:  # tank
            self.vx = math.sin(self.t * 0.4) * 1.3
            self.fire_cd -= 1
            if self.fire_cd <= 0:
                self.fire_cd = random.randint(90, 140)
                for a in (-20, 0, 20):
                    self.g.add_ebullet(self.x, self.y + 18, a, 3.2, "#b388ff")

        Entity.update(self)
        self.x = clamp(self.x, self.r, W - self.r)
        if self.flash > 0:
            self.flash -= 1
        if self.y > H + 50:
            self.kill()

    def damage(self, n):
        self.hp -= n
        self.flash = 4
        if self.hp <= 0:
            self.g.on_enemy_destroyed(self)
            self.kill()
            return True
        return False

    def redraw(self):
        c = self.c
        c.coords(self.ids[0], *self.points())
        c.itemconfig(self.ids[0], fill="#ffffff" if self.flash else self.fill)
        k = self.r * 0.3
        c.coords(self.ids[1], self.x - k, self.y - k, self.x + k, self.y + k)
        if self.maxhp >= 3 and self.hp < self.maxhp:
            bw = self.r * 2
            x1, y1 = self.x - self.r, self.y - self.r - 9
            c.coords(self.ids[2], x1, y1, x1 + bw, y1 + 4)
            c.coords(self.ids[3], x1, y1, x1 + bw * max(0.0, self.hp / self.maxhp), y1 + 4)
        else:
            c.coords(self.ids[2], -20, -20, -20, -20)
            c.coords(self.ids[3], -20, -20, -20, -20)


# ---------------------------------------------------------------- บอส
class Boss(Entity):
    def __init__(self, game, wave):
        Entity.__init__(self, game, W / 2, -70, 46)
        self.tier = wave // 5
        self.hp = self.maxhp = float(55 + wave * 14)
        self.score = 3000 + wave * 250
        self.kind = "boss"
        self.flash = 0
        self.t = 0.0
        self.frames = 0
        self.spin = 0.0
        self.entering = True
        self.cd_fan = 70
        self.cd_aim = 40
        self.cd_rain = 120
        c = self.c
        self.ids = [
            c.create_polygon(0, 0, 0, 0, 0, 0, fill="#2b1040", outline=HOT, width=3),
            c.create_oval(0, 0, 0, 0, fill=HOT, outline=GOLD, width=2),
            c.create_rectangle(0, 0, 0, 0, fill="#2a0d18", outline=""),
            c.create_rectangle(0, 0, 0, 0, fill=HOT, outline=""),
            c.create_text(W / 2, 66, text="MOTHERSHIP  Mk.%d" % self.tier,
                          fill=HOT, font=(FONT, 10, "bold")),
        ]

    def update(self):
        self.t += 0.03
        if self.entering:
            self.y += 2.2
            if self.y >= 120:
                self.entering = False
                self.t = 0.0
            return
        self.frames += 1
        self.x = W / 2 + math.sin(self.t) * (W / 2 - 90)
        self.y = 120 + math.sin(self.t * 2.3) * 22
        if self.flash > 0:
            self.flash -= 1

        g = self.g
        low = self.hp < self.maxhp * 0.5
        self.cd_aim -= 1
        if self.cd_aim <= 0:
            self.cd_aim = 26 if low else 40
            g.aimed_shot(self.x, self.y + 40, 5.2, GOLD, rad=4)
        self.cd_fan -= 1
        if self.cd_fan <= 0:
            self.cd_fan = 80 if low else 110
            for a in range(-70, 71, 14 if low else 20):
                g.add_ebullet(self.x, self.y + 36, a, 3.4, HOT)
        if low:
            self.cd_rain -= 1
            if self.cd_rain <= 0:
                self.cd_rain = 150
                for i in range(9):
                    g.add_ebullet(60 + i * 85, 10, 0, 2.8, "#b388ff")
        # บอสรุ่นที่ 2 ขึ้นไปมีกระสุนหมุนวน
        if self.tier >= 2 and self.frames % 260 < 100 and self.frames % 6 == 0:
            self.spin += 19
            for k in (0, 120, 240):
                g.add_ebullet(self.x, self.y, self.spin + k, 2.6, "#7ef9ff")

    def damage(self, n):
        if self.entering:
            return False
        self.hp -= n
        self.flash = 3
        if self.hp <= 0:
            self.g.on_enemy_destroyed(self)
            self.kill()
            return True
        return False

    def redraw(self):
        c, x, y, r = self.c, self.x, self.y, self.r
        c.coords(self.ids[0],
                 x - r, y - r * 0.4, x - r * 0.55, y - r * 0.95,
                 x + r * 0.55, y - r * 0.95, x + r, y - r * 0.4,
                 x + r * 0.75, y + r * 0.5, x, y + r,
                 x - r * 0.75, y + r * 0.5)
        c.itemconfig(self.ids[0], fill="#ffffff" if self.flash else "#2b1040")
        e = 15 + math.sin(self.t * 6) * 3
        c.coords(self.ids[1], x - e, y - e * 0.7, x + e, y + e * 0.7)
        bw = 320.0
        c.coords(self.ids[2], W / 2 - bw / 2 - 2, 40, W / 2 + bw / 2 + 2, 54)
        frac = max(0.0, self.hp / self.maxhp)
        c.coords(self.ids[3], W / 2 - bw / 2, 42, W / 2 - bw / 2 + bw * frac, 52)


# ---------------------------------------------------------------- ไอเทม
class PowerUp(Entity):
    def __init__(self, game, x, y, letter=None):
        Entity.__init__(self, game, x, y, 13)
        self.letter = letter or random.choices(POWERUP_LETTERS, POWERUP_WEIGHTS)[0]
        self.color, self.kindname, _ = POWERUPS[self.letter]
        self.vy = 1.7
        self.t = random.random() * 6.0
        c = self.c
        self.ids = [
            c.create_oval(0, 0, 0, 0, fill="", outline=self.color, width=2),
            c.create_text(0, 0, text=self.letter, fill=self.color,
                          font=(FONT, 13, "bold")),
        ]

    def update(self):
        self.t += 0.12
        self.vx = math.sin(self.t) * 1.1
        Entity.update(self)
        if self.y > H + 30:
            self.kill()

    def redraw(self):
        r = self.r + math.sin(self.t * 2) * 2
        self.c.coords(self.ids[0], self.x - r, self.y - r, self.x + r, self.y + r)
        self.c.coords(self.ids[1], self.x, self.y)

    def apply(self, p):
        """ใช้ไอเทม แล้วคืนข้อความที่จะลอยขึ้นจอ"""
        g = self.g
        if self.kindname == "power":
            if p.level < 3:
                p.level += 1
                return "POWER UP  Lv%d" % p.level
            g.score += 500
            return "MAX POWER +500"
        if self.kindname == "rapid":
            p.rapid = 60 * 12
            return "RAPID FIRE"
        if self.kindname == "shield":
            p.shield = 60 * 15
            return "SHIELD"
        if self.kindname == "energy":
            p.charge = p.ship["skill_cd"]
            return "SKILL READY"
        g.lives = min(6, g.lives + 1)
        return "1UP"


# ---------------------------------------------------------------- เอฟเฟกต์
class Particle(Entity):
    def __init__(self, game, x, y, vx, vy, life, palette, size):
        Entity.__init__(self, game, x, y, 1)
        self.vx, self.vy = vx, vy
        self.life = self.maxlife = max(1, life)
        self.palette = palette
        self.size = size
        self.ci = -1
        self.ids = [self.c.create_oval(0, 0, 0, 0, fill=palette[0], outline="")]

    def update(self):
        Entity.update(self)
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= 1
        if self.life <= 0:
            self.kill()

    def redraw(self):
        f = self.life / float(self.maxlife)
        i = int((1.0 - f) * (len(self.palette) - 1))
        if i != self.ci:
            self.ci = i
            self.c.itemconfig(self.ids[0], fill=self.palette[i])
        s = max(1.0, self.size * f)
        self.c.coords(self.ids[0], self.x - s, self.y - s, self.x + s, self.y + s)


class Shockwave(Entity):
    """วงแหวนขยายตัว ใช้กับระเบิด / สกิล"""

    def __init__(self, game, x, y, rmax, palette, life=24, width=3):
        Entity.__init__(self, game, x, y, 0)
        self.rmax = rmax
        self.life = self.maxlife = life
        self.palette = palette
        self.ci = -1
        self.ids = [self.c.create_oval(0, 0, 0, 0, outline=palette[0], width=width)]

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()

    def redraw(self):
        f = 1.0 - self.life / float(self.maxlife)
        r = 4 + (self.rmax - 4) * (1 - (1 - f) ** 2)
        i = int(f * (len(self.palette) - 1))
        if i != self.ci:
            self.ci = i
            self.c.itemconfig(self.ids[0], outline=self.palette[i])
        self.c.coords(self.ids[0], self.x - r, self.y - r, self.x + r, self.y + r)


class FloatText(Entity):
    """ตัวเลขคะแนน / ข้อความที่ลอยขึ้นแล้วหายไป"""

    def __init__(self, game, x, y, text, color, size=11, life=48):
        Entity.__init__(self, game, x, y, 0)
        self.vy = -0.9
        self.life = life
        self.ids = [self.c.create_text(x, y, text=text, fill=color,
                                       font=font_for(text, size))]

    def update(self):
        Entity.update(self)
        self.vy *= 0.97
        self.life -= 1
        if self.life <= 0:
            self.kill()

    def redraw(self):
        self.c.coords(self.ids[0], self.x, self.y)


# ---------------------------------------------------------------- ตัวเกม
class Game(object):
    KEYMAP = {
        "left": "left", "a": "left",
        "right": "right", "d": "right",
        "up": "up", "w": "up",
        "down": "down", "s": "down",
        "space": "space", "j": "space",
    }
    SKILL_KEYS = ("x", "k", "shift_l", "shift_r")
    LISTS = ("enemies", "pbullets", "ebullets", "powerups", "particles", "effects")

    def __init__(self, root):
        self.root = root
        root.title("Space Shooter - tkinter")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=W, height=H, bg=BG,
                                highlightthickness=0)
        self.canvas.pack()

        self.keys = set()
        root.bind("<KeyPress>", self.on_down)
        root.bind("<KeyRelease>", self.on_up)
        root.bind("<FocusOut>", self.on_focus_out)
        self.canvas.bind("<Button-1>", self.on_click)

        self.frame = 0
        self.make_stars()
        self.make_hud()

        save = load_save()
        self.best = max(0, safe_int(save.get("best"), 0))
        self.sel_ship = clamp(safe_int(save.get("ship"), 1), 0, len(SHIPS) - 1)
        self.sel_weapon = clamp(safe_int(save.get("weapon"), 0), 0, len(WEAPONS) - 1)
        self.sel_row = 0
        self.hitzones = []

        self.player = None
        self.new_game()
        self.player.kill()          # ยังไม่ให้เห็นยานจนกว่าจะเลือกเสร็จ
        self.state = "select"
        self.draw_select()

    # ---- ดาวพื้นหลัง 3 ชั้น (parallax)
    def make_stars(self):
        self.stars = []
        for _ in range(110):
            layer = random.randint(0, 2)
            sp = (0.5, 1.2, 2.3)[layer]
            col = ("#2b3a63", "#5f7bb5", "#cfe3ff")[layer]
            sz = (1, 1.5, 2.2)[layer]
            x, y = random.uniform(0, W), random.uniform(0, H)
            i = self.canvas.create_oval(x, y, x + sz, y + sz, fill=col, outline="")
            self.stars.append([i, x, y, sp, sz])

    def update_stars(self):
        c = self.canvas
        for s in self.stars:
            s[2] += s[3]
            if s[2] > H:
                s[2] = -2
                s[1] = random.uniform(0, W)
            c.coords(s[0], s[1], s[2], s[1] + s[4], s[2] + s[4])

    def make_hud(self):
        c = self.canvas
        self.hud = {
            "score": c.create_text(14, 12, anchor="nw", fill=CYAN,
                                   font=(FONT, 15, "bold")),
            "wave": c.create_text(W / 2, 12, anchor="n", fill=GOLD,
                                  font=(FONT, 14, "bold")),
            "lives": c.create_text(W - 14, 12, anchor="ne", fill=HOT,
                                   font=(FONT, 15, "bold")),
            "buff": c.create_text(14, 38, anchor="nw", fill="#7ef9ff",
                                  font=(FONT, 11)),
            "combo": c.create_text(W - 14, 38, anchor="ne", fill=GOLD,
                                   font=(FONT, 12, "bold")),
            "skill": c.create_text(14, H - 22, anchor="w", fill="#dfe8ff",
                                   font=(FONT, 11, "bold")),
            "skill_bg": c.create_rectangle(0, 0, 0, 0, fill="#1a2240", outline=""),
            "skill_fg": c.create_rectangle(0, 0, 0, 0, fill="#2a86ff", outline=""),
            "ready": c.create_text(300, H - 22, anchor="w", fill=GOLD,
                                   font=(FONT, 10, "bold")),
            "weapon": c.create_text(W - 14, H - 22, anchor="e", fill="#dfe8ff",
                                    font=(FONT, 11, "bold")),
        }

    # ---- เริ่ม / รีเซ็ต
    def new_game(self):
        for name in self.LISTS:
            for e in getattr(self, name, []):
                e.kill()
            setattr(self, name, [])
        if self.player:
            self.player.kill()

        ship = SHIPS[self.sel_ship]
        self.score = 0
        self.lives = ship["lives"]
        self.wave = 0
        self.queue = []
        self.spawn_cd = 0
        self.wave_gap = 90
        self.wave_done = False
        self.wave_damage = 0
        self.combo = 0
        self.combo_t = 0
        self.banner = 0
        self.banner_text = ""
        self.banner_color = GOLD
        self.shake = 0
        self.player = Player(self, ship, WEAPONS[self.sel_weapon])

    def start(self):
        self.new_game()
        self.clear_overlay()
        self.keys.clear()
        self.state = "play"
        self.save()
        self.next_wave()

    def save(self):
        write_save({"best": self.best, "ship": self.sel_ship,
                    "weapon": self.sel_weapon})

    def to_select(self):
        self.best = max(self.best, self.score)
        self.save()
        self.new_game()
        self.player.kill()
        self.keys.clear()
        self.state = "select"
        self.draw_select()

    def pause(self):
        self.state = "pause"
        self.keys.clear()
        self.show_overlay([
            ("PAUSED", 44, GOLD),
            ("P / Esc  เล่นต่อ", 16, "#ffffff"),
            ("Q  กลับไปหน้าเลือกยาน", 13, DIM),
        ])

    def resume(self):
        self.state = "play"
        self.clear_overlay()
        self.keys.clear()

    # ---- คลื่นศัตรู (ทุก 5 เวฟเจอบอส)
    def next_wave(self):
        self.wave += 1
        self.wave_done = False
        self.wave_damage = 0
        if self.wave % 5 == 0:
            self.enemies.append(Boss(self, self.wave))
            self.flash_banner("!! BOSS WAVE %d !!" % self.wave, HOT)
            return
        n = 4 + self.wave
        pool = ["grunt"] * 5
        if self.wave >= 2:
            pool += ["zig"] * 3
        if self.wave >= 3:
            pool += ["shooter"] * 3
        if self.wave >= 4:
            pool += ["tank"]
        self.queue = [random.choice(pool) for _ in range(n)]
        self.spawn_cd = 20
        self.flash_banner("WAVE %d" % self.wave, GOLD)

    def flash_banner(self, text, color):
        self.banner = 110
        self.banner_text = text
        self.banner_color = color

    def diff(self):
        """ตัวคูณความเร็วกระสุนศัตรู เพิ่มขึ้นตามเวฟ"""
        return min(1.6, 1.0 + 0.035 * (self.wave - 1))

    def multiplier(self):
        return 1 + min(4, self.combo // 6)

    # ---- ตัวช่วยสร้างวัตถุ
    def add_pbullet(self, x, y, angle_deg, speed, dmg, color, **kw):
        a = math.radians(angle_deg - 90)
        self.pbullets.append(Bullet(self, x, y, math.cos(a) * speed,
                                    math.sin(a) * speed, True, color,
                                    dmg=dmg, **kw))

    def add_ebullet(self, x, y, angle_deg, speed, color, rad=3):
        a = math.radians(angle_deg + 90)
        speed *= self.diff()
        self.ebullets.append(Bullet(self, x, y, math.cos(a) * speed,
                                    math.sin(a) * speed, False, color, rad))

    def aimed_shot(self, x, y, speed, color, rad=3):
        dx = self.player.x - x
        dy = self.player.y - y
        d = math.hypot(dx, dy) or 1.0
        speed *= self.diff()
        self.ebullets.append(Bullet(self, x, y, dx / d * speed, dy / d * speed,
                                    False, color, rad))

    def spawn_sparks(self, x, y, n, palette, spread=3.0, life=20, size=3.0):
        if len(self.particles) > 420:
            return
        for _ in range(n):
            a = random.uniform(0, 6.2832)
            s = random.uniform(0.3, 1.0) * spread
            self.particles.append(Particle(self, x, y, math.cos(a) * s,
                                           math.sin(a) * s,
                                           int(life * random.uniform(0.6, 1.3)),
                                           palette, size))

    def add_text(self, x, y, text, color, size=11):
        if len(self.effects) < 60:
            self.effects.append(FloatText(self, x, y, text, color, size))

    def nearest_enemy(self, x, y):
        best, bd = None, 1e18
        for e in self.enemies:
            if not e.alive or e.y < -10 or getattr(e, "entering", False):
                continue
            d = (e.x - x) ** 2 + (e.y - y) ** 2
            if d < bd:
                best, bd = e, d
        return best

    def explode(self, x, y, radius, dmg, exclude=None):
        """ระเบิดวงกว้างของมิสไซล์"""
        self.effects.append(Shockwave(self, x, y, radius, FIRE_PALETTE, life=14, width=3))
        self.spawn_sparks(x, y, 8, FIRE_PALETTE, spread=3.0, life=16, size=3.0)
        for e in self.enemies:
            if e.alive and e is not exclude:
                if (e.x - x) ** 2 + (e.y - y) ** 2 <= (radius + e.r) ** 2:
                    e.damage(dmg)

    def on_enemy_destroyed(self, e):
        self.combo += 1
        self.combo_t = 150
        mult = self.multiplier()
        pts = int(e.score * mult)
        self.score += pts
        if mult > 1:
            self.add_text(e.x, e.y - e.r, "+%d x%d" % (pts, mult), GOLD)
        else:
            self.add_text(e.x, e.y - e.r, "+%d" % pts, "#ffffff", 10)

        big = e.kind == "boss"
        self.spawn_sparks(e.x, e.y, 60 if big else 18, FIRE_PALETTE,
                          spread=7.0 if big else 3.6,
                          life=40 if big else 22,
                          size=6.0 if big else 3.4)
        self.shake = max(self.shake, 14 if big else 4)
        if big:
            self.effects.append(Shockwave(self, e.x, e.y, 260, FIRE_PALETTE, life=36, width=6))
            for dx, letter in ((-40, "P"), (0, "+"), (40, None)):
                self.powerups.append(PowerUp(self, e.x + dx, e.y, letter))
        elif random.random() < 0.13:
            self.powerups.append(PowerUp(self, e.x, e.y))

    # ---- สกิลพิเศษของยาน
    def use_skill(self):
        p = self.player
        if not p.alive or not p.skill_ready:
            return
        p.charge = 0
        kind = p.ship["skill"]
        if kind == "dash":
            dx, dy = p.dir
            p.dash = 10
            p.dash_v = (dx * 17, dy * 17)
            p.invuln = max(p.invuln, 26)
            self.effects.append(Shockwave(self, p.x, p.y, 40, SPARK_PALETTE,
                                          life=12, width=2))
        elif kind == "emp":
            for b in self.ebullets:
                if b.alive:
                    if random.random() < 0.5:
                        self.spawn_sparks(b.x, b.y, 2, SPARK_PALETTE, spread=1.5, life=12)
                    b.kill()
            for e in self.enemies:
                if e.alive:
                    e.damage(5.0 * p.ship["power"])
            self.effects.append(Shockwave(self, p.x, p.y, 560, SPARK_PALETTE,
                                          life=32, width=6))
            self.shake = max(self.shake, 10)
            self.add_text(p.x, p.y - 34, "EMP!", CYAN, 16)
        else:  # barrier
            p.barrier = 270
            self.effects.append(Shockwave(self, p.x, p.y, 90, GOLD_PALETTE,
                                          life=18, width=4))
            self.add_text(p.x, p.y - 40, "BARRIER", GOLD, 13)

    # ---- ลูปหลัก (ชดเชยเวลาที่ใช้ไป เพื่อให้เฟรมเรตนิ่ง)
    def loop(self):
        t0 = time.perf_counter()
        try:
            self.step()
        finally:
            spent = int((time.perf_counter() - t0) * 1000)
            self.root.after(max(1, TICK - spent), self.loop)

    def step(self):
        self.frame += 1
        self.update_stars()
        if self.state == "play":
            self.update_play()
        elif self.state == "over":
            self.update_world()      # ให้ฉากหลังยังเคลื่อนไหวหลังแพ้
            self.prune()
        for e in self.all_entities():
            e.redraw()
        self.update_hud()
        self.update_banner()
        self.apply_shake()

    def all_entities(self):
        out = [self.player] if self.player.alive else []
        for name in self.LISTS:
            out.extend(e for e in getattr(self, name) if e.alive)
        return out

    def update_world(self):
        for e in self.all_entities():
            e.update()

    def prune(self):
        for name in self.LISTS:
            setattr(self, name, [e for e in getattr(self, name) if e.alive])

    def update_play(self):
        p = self.player
        p.control(self.keys)
        if "space" in self.keys:
            p.shoot()

        # ปล่อยศัตรูตามคิว / ขึ้นเวฟใหม่เมื่อเคลียร์หมด
        if self.queue:
            self.spawn_cd -= 1
            if self.spawn_cd <= 0:
                self.spawn_cd = max(14, 40 - self.wave * 2)
                kind = self.queue.pop()
                self.enemies.append(
                    Enemy(self, kind, random.randint(50, W - 50), -30))
        elif not self.enemies:
            if not self.wave_done:
                self.wave_done = True
                self.wave_gap = 90
                if self.wave_damage == 0:
                    bonus = 200 * self.wave
                    self.score += bonus
                    self.flash_banner("PERFECT WAVE  +%d" % bonus, "#b0ff5a")
            self.wave_gap -= 1
            if self.wave_gap <= 0:
                self.next_wave()

        self.update_world()
        self.collide()
        self.prune()

        if self.combo_t > 0:
            self.combo_t -= 1
            if self.combo_t == 0:
                self.combo = 0

    def collide(self):
        p = self.player

        # กระสุนเรา -> ศัตรู (รองรับกระสุนทะลุ + ระเบิดวงกว้าง)
        for b in self.pbullets:
            if not b.alive:
                continue
            for e in self.enemies:
                if not e.alive or e in b.hit or not b.hits(e):
                    continue
                if not e.damage(b.dmg):
                    self.spawn_sparks(b.x, b.y, 4, SPARK_PALETTE,
                                      spread=2.0, life=12, size=2.5)
                if b.splash:
                    self.explode(b.x, b.y, b.splash, b.dmg * 0.6, exclude=e)
                if b.pierce > 0:
                    b.pierce -= 1
                    b.hit.add(e)
                else:
                    b.kill()
                    break

        if self.state != "play":
            return

        # โล่ BARRIER ดูดกระสุนและเผาศัตรูที่เข้าใกล้
        if p.barrier > 0:
            br = 34
            for b in self.ebullets:
                if b.alive and (b.x - p.x) ** 2 + (b.y - p.y) ** 2 <= (br + b.r) ** 2:
                    b.kill()
                    self.spawn_sparks(b.x, b.y, 3, GOLD_PALETTE, spread=1.5, life=10)
            for e in self.enemies:
                if e.alive and (e.x - p.x) ** 2 + (e.y - p.y) ** 2 <= (br + e.r) ** 2:
                    e.damage(0.25 * p.ship["power"])

        # กระสุนศัตรู -> เรา
        for b in self.ebullets:
            if b.alive and b.hits(p):
                b.kill()
                self.hurt_player()
                if self.state != "play":
                    return

        # ชนตัวศัตรูตรงๆ
        for e in self.enemies:
            if e.alive and e.hits(p):
                if e.kind != "boss":
                    e.damage(3)
                self.hurt_player()
                if self.state != "play":
                    return

        # เก็บไอเทม
        for u in self.powerups:
            if u.alive and u.hits(p):
                label = u.apply(p)
                self.score += 50
                self.add_text(u.x, u.y - 18, label, u.color, 12)
                self.spawn_sparks(u.x, u.y, 16, SPARK_PALETTE, spread=3.0, life=20)
                u.kill()

    def hurt_player(self):
        p = self.player
        if not p.take_hit():
            return
        self.lives -= 1
        self.wave_damage += 1
        self.combo = 0
        self.combo_t = 0
        self.shake = 16
        self.spawn_sparks(p.x, p.y, 40, FIRE_PALETTE, spread=5.5, life=32, size=5.0)
        for b in self.ebullets:
            b.kill()
        if self.lives <= 0:
            self.game_over()

    def game_over(self):
        self.state = "over"
        new_best = self.score > self.best
        self.best = max(self.best, self.score)
        self.save()
        self.player.kill()
        lines = [("GAME OVER", 52, HOT)]
        if new_best:
            lines.append(("NEW HIGH SCORE!", 18, GOLD))
        lines += [
            ("คะแนน  %d" % self.score, 22, "#ffffff"),
            ("สูงสุด  %d   |   ถึงเวฟ %d" % (self.best, self.wave), 15, GOLD),
            ("%s + %s" % (SHIPS[self.sel_ship]["name"],
                          WEAPONS[self.sel_weapon]["name"]), 13, "#7ea8d8"),
            ("", 6, BG),
            ("Enter เล่นอีกครั้ง    C เปลี่ยนยาน/อาวุธ    Esc ออก", 13, CYAN),
        ]
        self.show_overlay(lines)

    # ---- ข้อความบนจอ
    def clear_overlay(self):
        self.canvas.delete("overlay")

    def show_overlay(self, lines):
        self.clear_overlay()
        c = self.canvas
        c.create_rectangle(0, 0, W, H, fill="#000000", stipple="gray50",
                           outline="", tags="overlay")
        total = sum(sz + 16 for _, sz, _ in lines)
        y = H / 2 - total / 2
        for text, size, col in lines:
            c.create_text(W / 2, y, text=text, fill=col, anchor="n",
                          font=font_for(text, size), tags="overlay")
            y += size + 16

    # ---- หน้าเลือกยาน + อาวุธ
    def row_label(self, c, y, text, focus):
        c.create_text(28, y, anchor="w", text=text,
                      fill=GOLD if focus else DIM,
                      font=(FONT_TH, 12, "bold"), tags="overlay")
        if focus:
            c.create_text(W - 28, y, anchor="e", text="◀  ▶  เปลี่ยน",
                          fill=GOLD, font=(FONT_TH, 10), tags="overlay")

    def card(self, c, x1, y1, w, h, color, sel, focus):
        c.create_rectangle(x1, y1, x1 + w, y1 + h,
                           fill="#0f1736" if sel else "#080c1e",
                           outline=color if sel else "#26304f",
                           width=3 if (sel and focus) else (2 if sel else 1),
                           tags="overlay")

    def draw_select(self):
        c = self.canvas
        T = "overlay"
        c.delete(T)
        self.hitzones = []
        c.create_rectangle(0, 0, W, H, fill="#000000", stipple="gray50",
                           outline="", tags=T)
        c.create_text(W / 2, 30, text="SPACE  SHOOTER", fill=CYAN,
                      font=(FONT, 28, "bold"), tags=T)
        c.create_text(W / 2, 62, text="เลือกยานและอาวุธก่อนออกรบ",
                      fill="#7ea8d8", font=(FONT_TH, 12), tags=T)

        # แถวที่ 1: ยาน
        focus = self.sel_row == 0
        self.row_label(c, 88, "1   เลือกยาน", focus)
        cw, ch, gap = 236, 196, 18
        x0 = (W - (3 * cw + 2 * gap)) / 2.0
        y1 = 102
        for i, s in enumerate(SHIPS):
            x1 = x0 + i * (cw + gap)
            sel = i == self.sel_ship
            self.card(c, x1, y1, cw, ch, s["color"], sel, focus)
            cx = x1 + cw / 2.0
            draw_ship(c, s, cx, y1 + 44, 17, T)
            c.create_text(cx, y1 + 92, text=s["name"],
                          fill=s["color"] if sel else "#dfe8ff",
                          font=(FONT, 15, "bold"), tags=T)
            c.create_text(cx, y1 + 112, text=s["title"], fill="#8fa3c8",
                          font=(FONT_TH, 10), tags=T)
            for j, lab in enumerate(("SPEED", "ARMOR", "POWER", "SKILL")):
                draw_stat(c, x1 + 18, y1 + 134 + j * 15, lab, s["stats"][j],
                          s["color"], x1 + 96, 22, T)
            self.hitzones.append((x1, y1, x1 + cw, y1 + ch, 0, i))
        s = SHIPS[self.sel_ship]
        c.create_text(W / 2, 312, text="%s   |   ชีวิต %d" % (s["desc"], s["lives"]),
                      fill="#dfe8ff", font=(FONT_TH, 10), tags=T)
        c.create_text(W / 2, 330, text="สกิล [X] %s : %s" % (s["skill_name"], s["skill_desc"]),
                      fill=s["color"], font=(FONT_TH, 10), tags=T)

        # แถวที่ 2: อาวุธ
        focus = self.sel_row == 1
        self.row_label(c, 354, "2   เลือกอาวุธ", focus)
        cw, ch, gap = 178, 160, 12
        x0 = (W - (4 * cw + 3 * gap)) / 2.0
        y1 = 368
        for i, w in enumerate(WEAPONS):
            x1 = x0 + i * (cw + gap)
            sel = i == self.sel_weapon
            self.card(c, x1, y1, cw, ch, w["color"], sel, focus)
            cx = x1 + cw / 2.0
            draw_weapon_icon(c, w, cx, y1 + 32, T)
            c.create_text(cx, y1 + 68, text=w["name"],
                          fill=w["color"] if sel else "#dfe8ff",
                          font=(FONT, 14, "bold"), tags=T)
            c.create_text(cx, y1 + 88, text=w["title"], fill="#8fa3c8",
                          font=(FONT_TH, 10), tags=T)
            for j, lab in enumerate(("DAMAGE", "RATE", "AREA")):
                draw_stat(c, x1 + 14, y1 + 110 + j * 15, lab, w["stats"][j],
                          w["color"], x1 + 82, 15, T)
            self.hitzones.append((x1, y1, x1 + cw, y1 + ch, 1, i))
        w = WEAPONS[self.sel_weapon]
        c.create_text(W / 2, 541, text=w["desc"], fill="#dfe8ff",
                      font=(FONT_TH, 10), tags=T)

        # ปุ่มเริ่ม
        bx1, by1, bx2, by2 = W / 2 - 130, 558, W / 2 + 130, 590
        c.create_rectangle(bx1, by1, bx2, by2, fill="#1b2d5c", outline=GOLD,
                           width=2, tags=T)
        c.create_text(W / 2, (by1 + by2) / 2, text="ENTER  เริ่มเกม", fill=GOLD,
                      font=(FONT_TH, 14, "bold"), tags=T)
        self.hitzones.append((bx1, by1, bx2, by2, 2, 0))
        c.create_text(20, 606, anchor="w",
                      text="← → เลือก     ↑ ↓ สลับแถว     คลิกการ์ดได้     Esc ออก",
                      fill=DIM, font=(FONT_TH, 9), tags=T)
        c.create_text(W - 20, 606, anchor="e", text="HIGH SCORE %06d" % self.best,
                      fill=GOLD, font=(FONT, 10, "bold"), tags=T)

    def select_key(self, k):
        if k in ("left", "a"):
            self.select_move(-1)
        elif k in ("right", "d"):
            self.select_move(1)
        elif k in ("up", "w"):
            self.sel_row = 0
        elif k in ("down", "s"):
            self.sel_row = 1
        elif k == "tab":
            self.sel_row = 1 - self.sel_row
        elif k in ("return", "kp_enter", "space"):
            self.start()
            return
        elif k == "escape":
            self.root.destroy()
            return
        else:
            return
        self.draw_select()

    def select_move(self, d):
        if self.sel_row == 0:
            self.sel_ship = (self.sel_ship + d) % len(SHIPS)
        else:
            self.sel_weapon = (self.sel_weapon + d) % len(WEAPONS)

    def on_click(self, ev):
        if self.state != "select":
            return
        x, y = self.canvas.canvasx(ev.x), self.canvas.canvasy(ev.y)
        for x1, y1, x2, y2, row, idx in self.hitzones:
            if x1 <= x <= x2 and y1 <= y <= y2:
                if row == 2:
                    self.start()
                    return
                self.sel_row = row
                if row == 0:
                    self.sel_ship = idx
                else:
                    self.sel_weapon = idx
                self.draw_select()
                return

    # ---- HUD
    def update_banner(self):
        self.canvas.delete("banner")
        if self.banner <= 0:
            return
        self.banner -= 1
        if self.banner % 20 < 14 or self.banner < 40:
            self.canvas.create_text(W / 2, H / 2 - 60, text=self.banner_text,
                                    fill=self.banner_color, anchor="c",
                                    font=(FONT, 30, "bold"), tags="banner")

    def update_hud(self):
        c = self.canvas
        hidden = self.state == "select"
        for i in self.hud.values():
            c.itemconfig(i, state="hidden" if hidden else "normal")
        if hidden:
            return

        p = self.player
        ship, w = p.ship, p.weapon
        c.itemconfig(self.hud["score"], text="SCORE %06d" % self.score)
        c.itemconfig(self.hud["wave"], text="WAVE %d" % self.wave)
        c.itemconfig(self.hud["lives"], text="LIVES " + u"♥" * max(0, self.lives))

        buf = []
        if p.alive:
            if p.rapid:
                buf.append("RAPID %ds" % (p.rapid // 60 + 1))
            if p.shield:
                buf.append("SHIELD %ds" % (p.shield // 60 + 1))
            if p.barrier:
                buf.append("BARRIER %ds" % (p.barrier // 60 + 1))
        c.itemconfig(self.hud["buff"], text="   ".join(buf))

        if self.combo >= 2:
            c.itemconfig(self.hud["combo"],
                         text="COMBO %d  x%d" % (self.combo, self.multiplier()))
        else:
            c.itemconfig(self.hud["combo"], text="")

        # หลอดสกิลมุมซ้ายล่าง
        frac = min(1.0, p.charge / float(ship["skill_cd"]))
        x1, bw = 150, 140
        c.itemconfig(self.hud["skill"], text="[X] " + ship["skill_name"])
        c.coords(self.hud["skill_bg"], x1, H - 27, x1 + bw, H - 17)
        c.coords(self.hud["skill_fg"], x1, H - 27, x1 + bw * frac, H - 17)
        if frac >= 1.0:
            c.itemconfig(self.hud["skill_fg"],
                         fill=GOLD if (self.frame // 8) % 2 == 0 else "#ffe9a0")
            c.itemconfig(self.hud["ready"], text="READY")
        else:
            c.itemconfig(self.hud["skill_fg"], fill="#2a86ff")
            c.itemconfig(self.hud["ready"], text="")

        c.itemconfig(self.hud["weapon"], text="%s  Lv%d" % (w["name"], p.level))
        c.itemconfig(self.hud["weapon"], fill=w["color"])

        # ให้ HUD / overlay อยู่บนสุดเสมอ
        for i in self.hud.values():
            c.tag_raise(i)
        c.tag_raise("overlay")

    def apply_shake(self):
        """จอสั่นตอนระเบิด: เลื่อน scrollregion ของ canvas เล็กน้อย"""
        if self.shake > 0:
            self.shake -= 1
            d = self.shake * 0.5
            ox, oy = random.uniform(-d, d), random.uniform(-d, d)
            self.canvas.configure(scrollregion=(ox, oy, W + ox, H + oy))
        else:
            self.canvas.configure(scrollregion=(0, 0, W, H))

    # ---- คีย์บอร์ด
    def on_down(self, ev):
        k = ev.keysym.lower()
        if self.state == "select":
            self.select_key(k)
            return
        if k in self.KEYMAP:
            self.keys.add(self.KEYMAP[k])
            return
        if k in self.SKILL_KEYS:
            if self.state == "play":
                self.use_skill()
            return
        if self.state == "play":
            if k in ("p", "escape"):
                self.pause()
        elif self.state == "pause":
            if k in ("p", "escape"):
                self.resume()
            elif k == "q":
                self.to_select()
        elif self.state == "over":
            if k in ("return", "kp_enter"):
                self.start()
            elif k == "c":
                self.to_select()
            elif k == "escape":
                self.root.destroy()

    def on_up(self, ev):
        k = ev.keysym.lower()
        if k in self.KEYMAP:
            self.keys.discard(self.KEYMAP[k])

    def on_focus_out(self, ev):
        # สลับหน้าต่างแล้วปุ่มค้าง -> ล้างปุ่ม และพักเกมให้อัตโนมัติ
        self.keys.clear()
        if self.state == "play":
            self.pause()


def main():
    root = tk.Tk()
    game = Game(root)
    game.loop()
    root.mainloop()


if __name__ == "__main__":
    main()

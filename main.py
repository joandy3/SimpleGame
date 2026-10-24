# -*- coding: utf-8 -*-
"""
Space Shooter - เกมยิงยานอวกาศ เขียนด้วย tkinter เพียวๆ
ไม่ต้องติดตั้ง library อะไรเพิ่มเลย (tkinter มาพร้อม Python)
พัฒนาโดย LoongPong
วิธีเล่น:
    python main.py

ปุ่มควบคุม:
    ลูกศร / WASD   บังคับยาน
    Space          ยิง (กดค้างได้)
    P              พักเกม
    Enter          เริ่มเกม / เล่นใหม่
    Esc            ออกจากเกม
"""

import math
import random
import tkinter as tk

# ---------------------------------------------------------------- ค่าคงที่
W, H = 800, 620
TICK = 16                      # ms ต่อเฟรม (~60 fps)

BG = "#05060f"
CYAN = "#4fd2ff"
HOT = "#ff4d6d"
GOLD = "#ffd84d"

FIRE_PALETTE = ["#fffbe6", "#ffe36b", "#ffa52b", "#ff5a2b", "#b32020", "#5a1010"]
SPARK_PALETTE = ["#eafaff", "#9fe8ff", "#4fd2ff", "#2a86ff", "#17408f", "#0b1a3a"]

POWERUPS = {
    "S": ("#7ef9ff", "spread"),
    "R": ("#b0ff5a", "rapid"),
    "O": ("#ffb347", "shield"),
    "+": ("#ff6b9d", "life"),
}


def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


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

    def __init__(self, game):
        Entity.__init__(self, game, W / 2, H - 90, 13)
        self.speed = 5.6
        self.cool = 0
        self.spread = 0          # เหลืออีกกี่เฟรม
        self.rapid = 0
        self.shield = 0
        self.invuln = 100
        self.thrust = False
        c = self.c
        self.ids = [
            c.create_polygon(0, 0, 0, 0, 0, 0, fill="#ff8a2b", outline=""),      # เปลวไฟ
            c.create_polygon(0, 0, 0, 0, 0, 0, fill="#1b6dff", outline=""),      # ปีก
            c.create_polygon(0, 0, 0, 0, 0, 0, fill=CYAN, outline="#eafaff"),    # ลำตัว
            c.create_oval(0, 0, 0, 0, fill="#fff4b0", outline=""),               # ห้องนักบิน
            c.create_oval(0, 0, 0, 0, outline="", width=2),                      # โล่
        ]

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
        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071
        self.thrust = dy < 0
        self.vx = dx * self.speed
        self.vy = dy * self.speed

    def update(self):
        Entity.update(self)
        self.x = clamp(self.x, 22, W - 22)
        self.y = clamp(self.y, 70, H - 30)
        for a in ("cool", "spread", "rapid", "shield", "invuln"):
            v = getattr(self, a)
            if v > 0:
                setattr(self, a, v - 1)

    def shoot(self):
        if self.cool > 0:
            return
        self.cool = 5 if self.rapid else 9
        y = self.y - 18
        if self.spread:
            for ang in (-26, -9, 9, 26):
                self.g.add_pbullet(self.x, y, ang)
        else:
            self.g.add_pbullet(self.x - 7, y, 0)
            self.g.add_pbullet(self.x + 7, y, 0)
        self.g.spawn_sparks(self.x, y, 3, SPARK_PALETTE, spread=1.5, life=8)

    def take_hit(self):
        """คืน True ถ้าเสียชีวิตจริง (โล่ช่วยกันได้)"""
        if self.invuln > 0:
            return False
        if self.shield > 0:
            self.shield = 0
            self.invuln = 60
            self.g.spawn_sparks(self.x, self.y, 26, SPARK_PALETTE, spread=4.5, life=26)
            return False
        self.invuln = 110
        self.spread = self.rapid = 0
        return True

    def redraw(self):
        c, x, y, s = self.c, self.x, self.y, self.SIZE
        f = random.uniform(0.75, 1.6) if self.thrust else random.uniform(0.25, 0.7)
        c.coords(self.ids[0], x - 5, y + 9, x + 5, y + 9, x, y + 9 + 15 * f)
        c.coords(self.ids[1],
                 x, y - s * 0.2,
                 x - s * 1.3, y + s * 0.95,
                 x - s * 0.45, y + s * 0.55,
                 x + s * 0.45, y + s * 0.55,
                 x + s * 1.3, y + s * 0.95)
        c.coords(self.ids[2],
                 x, y - s * 1.35,
                 x - s * 0.72, y + s * 0.8,
                 x, y + s * 0.3,
                 x + s * 0.72, y + s * 0.8)
        c.coords(self.ids[3], x - 4, y - 11, x + 4, y - 2)

        # กะพริบตอนอมตะชั่วคราว
        blink = self.invuln > 0 and (self.invuln // 4) % 2 == 0
        c.itemconfig(self.ids[2], fill="#13314d" if blink else CYAN)
        c.itemconfig(self.ids[1], fill="#102a52" if blink else "#1b6dff")

        if self.shield > 0:
            ring = "#7ef9ff" if (self.shield // 5) % 2 == 0 else "#2a86ff"
            c.itemconfig(self.ids[4], outline=ring)
            c.coords(self.ids[4], x - 27, y - 27, x + 27, y + 27)
        else:
            c.itemconfig(self.ids[4], outline="")
            c.coords(self.ids[4], -60, -60, -50, -50)


# ---------------------------------------------------------------- กระสุน
class Bullet(Entity):
    def __init__(self, game, x, y, vx, vy, friendly, color, rad=3, dmg=1):
        Entity.__init__(self, game, x, y, rad)
        self.vx, self.vy = vx, vy
        self.friendly = friendly
        self.dmg = dmg
        glow = self.c.create_oval(0, 0, 0, 0, fill="", outline=color)
        core = self.c.create_oval(0, 0, 0, 0, fill="#ffffff" if friendly else color,
                                  outline="")
        self.ids = [glow, core]

    def update(self):
        Entity.update(self)
        if self.offscreen(24):
            self.kill()

    def redraw(self):
        r = self.r
        self.c.coords(self.ids[0], self.x - r * 1.9, self.y - r * 2.4,
                      self.x + r * 1.9, self.y + r * 2.4)
        self.c.coords(self.ids[1], self.x - r * 0.75, self.y - r * 1.4,
                      self.x + r * 0.75, self.y + r * 1.4)


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
        self.hp = self.maxhp = hp + game.wave // 4
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


# ---------------------------------------------------------------- บอส
class Boss(Entity):
    def __init__(self, game, wave):
        Entity.__init__(self, game, W / 2, -70, 46)
        self.hp = self.maxhp = 55 + wave * 14
        self.score = 3000 + wave * 250
        self.kind = "boss"
        self.flash = 0
        self.t = 0.0
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
        ]

    def update(self):
        self.t += 0.03
        if self.entering:
            self.y += 2.2
            if self.y >= 120:
                self.entering = False
                self.t = 0.0
            return
        self.x = W / 2 + math.sin(self.t) * (W / 2 - 90)
        self.y = 120 + math.sin(self.t * 2.3) * 22
        if self.flash > 0:
            self.flash -= 1

        low = self.hp < self.maxhp * 0.5
        self.cd_aim -= 1
        if self.cd_aim <= 0:
            self.cd_aim = 26 if low else 40
            self.g.aimed_shot(self.x, self.y + 40, 5.2, GOLD, rad=4)
        self.cd_fan -= 1
        if self.cd_fan <= 0:
            self.cd_fan = 80 if low else 110
            for a in range(-70, 71, 14 if low else 20):
                self.g.add_ebullet(self.x, self.y + 36, a, 3.4, HOT)
        if low:
            self.cd_rain -= 1
            if self.cd_rain <= 0:
                self.cd_rain = 150
                for i in range(9):
                    self.g.add_ebullet(60 + i * 85, 10, 0, 2.8, "#b388ff")

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
        # แถบพลังชีวิตบอส
        bw = 320.0
        c.coords(self.ids[2], W / 2 - bw / 2 - 2, 40, W / 2 + bw / 2 + 2, 54)
        frac = max(0.0, self.hp / float(self.maxhp))
        c.coords(self.ids[3], W / 2 - bw / 2, 42, W / 2 - bw / 2 + bw * frac, 52)


# ---------------------------------------------------------------- ไอเทม
class PowerUp(Entity):
    def __init__(self, game, x, y):
        Entity.__init__(self, game, x, y, 13)
        self.letter = random.choice(list(POWERUPS.keys()))
        self.color, self.kindname = POWERUPS[self.letter]
        self.vy = 1.7
        self.t = 0.0
        c = self.c
        self.ids = [
            c.create_oval(0, 0, 0, 0, fill="", outline=self.color, width=2),
            c.create_text(0, 0, text=self.letter, fill=self.color,
                          font=("Consolas", 13, "bold")),
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
        if self.kindname == "spread":
            p.spread = 60 * 14
        elif self.kindname == "rapid":
            p.rapid = 60 * 12
        elif self.kindname == "shield":
            p.shield = 60 * 12
        else:
            self.g.lives = min(5, self.g.lives + 1)


# ---------------------------------------------------------------- เศษระเบิด
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


# ---------------------------------------------------------------- ตัวเกม
class Game(object):
    KEYMAP = {
        "left": "left", "a": "left",
        "right": "right", "d": "right",
        "up": "up", "w": "up",
        "down": "down", "s": "down",
        "space": "space",
    }

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

        self.make_stars()
        c = self.canvas
        self.hud = {
            "score": c.create_text(14, 12, anchor="nw", fill=CYAN,
                                   font=("Consolas", 15, "bold")),
            "wave": c.create_text(W / 2, 12, anchor="n", fill=GOLD,
                                  font=("Consolas", 14, "bold")),
            "lives": c.create_text(W - 14, 12, anchor="ne", fill=HOT,
                                   font=("Consolas", 15, "bold")),
            "buff": c.create_text(14, 38, anchor="nw", fill="#7ef9ff",
                                  font=("Consolas", 11)),
        }

        self.best = 0
        self.player = None
        self.state = "menu"
        self.new_game()
        self.show_menu()

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

    # ---- เริ่มเกมใหม่
    def new_game(self):
        for name in ("pbullets", "ebullets", "enemies", "powerups", "particles"):
            for e in getattr(self, name, []):
                e.kill()
            setattr(self, name, [])
        if self.player:
            self.player.kill()

        self.score = 0
        self.lives = 3
        self.wave = 0
        self.queue = []
        self.spawn_cd = 0
        self.wave_gap = 60
        self.banner = 0
        self.banner_text = ""
        self.banner_color = GOLD
        self.shake = 0
        self.player = Player(self)

    def start(self):
        self.new_game()
        self.clear_overlay()
        self.keys.clear()
        self.state = "play"
        self.next_wave()

    # ---- คลื่นศัตรู (ทุก 5 เวฟเจอบอส)
    def next_wave(self):
        self.wave += 1
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

    # ---- ตัวช่วยสร้างวัตถุ
    def add_pbullet(self, x, y, angle_deg):
        a = math.radians(angle_deg - 90)
        self.pbullets.append(Bullet(self, x, y, math.cos(a) * 12.5,
                                    math.sin(a) * 12.5, True, CYAN))

    def add_ebullet(self, x, y, angle_deg, speed, color, rad=3):
        a = math.radians(angle_deg + 90)
        self.ebullets.append(Bullet(self, x, y, math.cos(a) * speed,
                                    math.sin(a) * speed, False, color, rad))

    def aimed_shot(self, x, y, speed, color, rad=3):
        dx = self.player.x - x
        dy = self.player.y - y
        d = math.hypot(dx, dy) or 1.0
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

    def on_enemy_destroyed(self, e):
        self.score += e.score
        big = e.kind == "boss"
        self.spawn_sparks(e.x, e.y, 60 if big else 18, FIRE_PALETTE,
                          spread=7.0 if big else 3.6,
                          life=40 if big else 22,
                          size=6.0 if big else 3.4)
        self.shake = max(self.shake, 14 if big else 4)
        if big or random.random() < 0.14:
            self.powerups.append(PowerUp(self, e.x, e.y))

    # ---- ลูปหลัก
    def loop(self):
        try:
            self.step()
        finally:
            self.root.after(TICK, self.loop)

    def step(self):
        self.update_stars()
        if self.state == "play":
            self.update_play()
        for e in self.all_entities():
            e.redraw()
        self.update_hud()
        self.update_banner()
        self.apply_shake()

    def all_entities(self):
        out = [self.player] if self.player.alive else []
        for lst in (self.enemies, self.pbullets, self.ebullets,
                    self.powerups, self.particles):
            out.extend(e for e in lst if e.alive)
        return out

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
            self.wave_gap -= 1
            if self.wave_gap <= 0:
                self.wave_gap = 90
                self.next_wave()

        for e in self.all_entities():
            e.update()

        self.collide()

        for name in ("enemies", "pbullets", "ebullets", "powerups", "particles"):
            setattr(self, name, [e for e in getattr(self, name) if e.alive])

    def collide(self):
        p = self.player

        # กระสุนเรา -> ศัตรู
        for b in self.pbullets:
            if not b.alive:
                continue
            for e in self.enemies:
                if e.alive and b.hits(e):
                    b.kill()
                    if not e.damage(b.dmg):
                        self.spawn_sparks(b.x, b.y, 5, SPARK_PALETTE,
                                          spread=2.0, life=12, size=2.5)
                    break

        if self.state != "play":
            return

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
                u.apply(p)
                self.score += 50
                self.spawn_sparks(u.x, u.y, 16, SPARK_PALETTE, spread=3.0, life=20)
                u.kill()

    def hurt_player(self):
        if not self.player.take_hit():
            return
        self.lives -= 1
        self.shake = 16
        self.spawn_sparks(self.player.x, self.player.y, 40, FIRE_PALETTE,
                          spread=5.5, life=32, size=5.0)
        for b in self.ebullets:
            b.kill()
        if self.lives <= 0:
            self.game_over()
        else:
            self.player.x, self.player.y = W / 2, H - 90

    def game_over(self):
        self.state = "over"
        self.best = max(self.best, self.score)
        self.player.kill()
        self.show_overlay([
            ("GAME OVER", 52, HOT),
            ("คะแนน  %d" % self.score, 22, "#ffffff"),
            ("สูงสุด  %d   |   ถึงเวฟ %d" % (self.best, self.wave), 15, GOLD),
            ("", 8, BG),
            ("กด Enter เพื่อเล่นอีกครั้ง   |   Esc ออก", 14, CYAN),
        ])

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
                          font=("Consolas", size, "bold"), tags="overlay")
            y += size + 16

    def show_menu(self):
        self.show_overlay([
            ("SPACE  SHOOTER", 44, CYAN),
            ("tkinter เพียวๆ ไม่ต้องลง library เพิ่ม", 14, "#7ea8d8"),
            ("", 8, BG),
            ("ลูกศร / WASD  บังคับยาน", 15, "#ffffff"),
            ("Space  ยิง      P  พักเกม", 15, "#ffffff"),
            ("ไอเทม:  S สเปรด   R ยิงเร็ว   O โล่   + ชีวิต", 13, GOLD),
            ("", 8, BG),
            ("กด Enter เพื่อเริ่ม", 20, GOLD),
        ])

    def update_banner(self):
        self.canvas.delete("banner")
        if self.banner <= 0:
            return
        self.banner -= 1
        if self.banner % 20 < 14 or self.banner < 40:
            self.canvas.create_text(W / 2, H / 2 - 60, text=self.banner_text,
                                    fill=self.banner_color, anchor="c",
                                    font=("Consolas", 30, "bold"), tags="banner")

    def update_hud(self):
        c = self.canvas
        c.itemconfig(self.hud["score"], text="SCORE %06d" % self.score)
        c.itemconfig(self.hud["wave"], text="WAVE %d" % self.wave)
        c.itemconfig(self.hud["lives"], text="LIVES " + "♥" * max(0, self.lives))
        p = self.player
        buf = []
        if p.alive:
            if p.spread:
                buf.append("SPREAD %ds" % (p.spread // 60 + 1))
            if p.rapid:
                buf.append("RAPID %ds" % (p.rapid // 60 + 1))
            if p.shield:
                buf.append("SHIELD %ds" % (p.shield // 60 + 1))
        c.itemconfig(self.hud["buff"], text="   ".join(buf))
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
        if k in self.KEYMAP:
            self.keys.add(self.KEYMAP[k])
            return
        if k == "escape":
            self.root.destroy()
        elif k in ("return", "kp_enter"):
            if self.state in ("menu", "over"):
                self.start()
        elif k == "p" and self.state in ("play", "pause"):
            if self.state == "play":
                self.state = "pause"
                self.show_overlay([("PAUSED", 44, GOLD),
                                   ("กด P เพื่อเล่นต่อ", 16, "#ffffff")])
            else:
                self.state = "play"
                self.clear_overlay()
                self.keys.clear()

    def on_up(self, ev):
        k = ev.keysym.lower()
        if k in self.KEYMAP:
            self.keys.discard(self.KEYMAP[k])


def main():
    root = tk.Tk()
    game = Game(root)
    game.loop()
    root.mainloop()


if __name__ == "__main__":
    main()

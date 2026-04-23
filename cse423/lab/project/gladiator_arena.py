import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
WINDOW_W, WINDOW_H = 1000, 800
ARENA_SIZE   = 500        # half-extent of the arena floor
WALL_HEIGHT  = 120
TILE_COUNT   = 10         # tiles per side for checkerboard
TILE_SIZE    = (ARENA_SIZE * 2) / TILE_COUNT

PLAYER_SPEED   = 8
PLAYER_ROT_SPD = 5
BULLET_SPEED   = 14
MAX_BULLETS    = 10
ENEMY_COUNT    = 5
COMBO_TIMEOUT  = 180      # frames before combo resets (~3 s at 60 fps)
ROUND_DISPLAY_FRAMES = 120

ENEMY_TYPE_BRUTE   = 0
ENEMY_TYPE_SPEEDER = 1
ENEMY_TYPE_TANK    = 2

ENEMY_HP    = {ENEMY_TYPE_BRUTE: 3, ENEMY_TYPE_SPEEDER: 1, ENEMY_TYPE_TANK: 5}
ENEMY_SCORE = {ENEMY_TYPE_BRUTE: 20, ENEMY_TYPE_SPEEDER: 10, ENEMY_TYPE_TANK: 30}
ENEMY_SPEED = {ENEMY_TYPE_BRUTE: 1.8, ENEMY_TYPE_SPEEDER: 3.2, ENEMY_TYPE_TANK: 0.9}
ENEMY_COLOR = {
    ENEMY_TYPE_BRUTE:   (0.85, 0.2, 0.2),
    ENEMY_TYPE_SPEEDER: (0.2, 0.8, 0.3),
    ENEMY_TYPE_TANK:    (0.2, 0.3, 0.9),
}

# ─────────────────────────────────────────────
#  GAME STATE
# ─────────────────────────────────────────────
# --- Camera ---
cam_angle   = 45.0      # horizontal orbit angle (degrees)
cam_height  = 500.0
cam_radius  = 800.0
fovY        = 60.0
first_person = False

# --- Player ---
player_x    = 0.0
player_y    = 0.0
player_angle = 0.0      # facing direction in degrees (around Z)
player_hp   = 100
player_stamina = 100.0
blocking    = False
speed_boost = False

# --- Sword swing ---
swing_active  = False
swing_angle   = 0.0     # current arm rotation during swing
swing_dir     = 1
swing_timer   = 0

# --- Death ---
player_dead  = False
player_death_angle = 0.0  # tilts to 90 for lie-down

# --- Game ---
score       = 0
combo       = 1
combo_timer = 0
kills_this_combo = 0
game_round  = 1
kills_this_round = 0
round_announce_timer = 0
game_over   = False
victory     = False
frame_count = 0

# --- Enemies ---
# Each enemy: [x, y, hp, type, dead_timer, hit_flash, pulse_phase, death_angle]
enemies = []

# --- Bullets ---
# Each bullet: [x, y, dx, dy, alive]
bullets = []

# --- Collectibles on floor ---
collectibles = []   # [x, y, collected]

# --- Animation counter ---
anim_counter = 0.0

# ─────────────────────────────────────────────
#  INIT / RESET
# ─────────────────────────────────────────────
def spawn_enemy():
    """Spawn one enemy at random arena edge."""
    side = random.randint(0, 3)
    margin = ARENA_SIZE - 30
    if side == 0:
        x, y = random.uniform(-margin, margin), -margin
    elif side == 1:
        x, y = random.uniform(-margin, margin),  margin
    elif side == 2:
        x, y = -margin, random.uniform(-margin, margin)
    else:
        x, y =  margin, random.uniform(-margin, margin)
    etype = random.randint(0, 2)
    hp = ENEMY_HP[etype]
    # [x, y, hp, type, dead_timer, hit_flash, pulse_phase, death_angle]
    return [x, y, hp, etype, 0, 0, random.uniform(0, 6.28), 0.0]

def spawn_collectibles():
    global collectibles
    collectibles = []
    for _ in range(6):
        x = random.uniform(-ARENA_SIZE + 60, ARENA_SIZE - 60)
        y = random.uniform(-ARENA_SIZE + 60, ARENA_SIZE - 60)
        collectibles.append([x, y, False])

def reset_game():
    global player_x, player_y, player_angle, player_hp, player_stamina
    global blocking, speed_boost, swing_active, swing_angle, swing_timer
    global player_dead, player_death_angle
    global score, combo, combo_timer, kills_this_combo
    global game_round, kills_this_round, round_announce_timer
    global game_over, victory, frame_count, anim_counter
    global enemies, bullets, cam_angle, cam_height, first_person, fovY

    player_x, player_y  = 0.0, 0.0
    player_angle         = 0.0
    player_hp            = 100
    player_stamina       = 100.0
    blocking = speed_boost = False
    swing_active = False
    swing_angle = swing_timer = 0
    player_dead = False
    player_death_angle = 0.0
    score = 0
    combo = 1
    combo_timer = kills_this_combo = 0
    game_round = 1
    kills_this_round = 0
    round_announce_timer = 0
    game_over = victory = False
    frame_count = anim_counter = 0
    cam_angle  = 45.0
    cam_height = 500.0
    fovY       = 60.0
    first_person = False
    enemies = [spawn_enemy() for _ in range(ENEMY_COUNT)]
    bullets = []
    spawn_collectibles()

# ─────────────────────────────────────────────
#  DRAW HELPERS
# ─────────────────────────────────────────────
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text_color(x, y, text, r, g, b, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(r, g, b)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# ─────────────────────────────────────────────
#  ARENA DRAWING
# ─────────────────────────────────────────────
def draw_checkerboard_floor():
    """Dynamically generate checkerboard — no hardcoding."""
    glBegin(GL_QUADS)
    for row in range(TILE_COUNT):
        for col in range(TILE_COUNT):
            x0 = -ARENA_SIZE + col * TILE_SIZE
            y0 = -ARENA_SIZE + row * TILE_SIZE
            x1 = x0 + TILE_SIZE
            y1 = y0 + TILE_SIZE
            if (row + col) % 2 == 0:
                glColor3f(0.85, 0.82, 0.75)
            else:
                glColor3f(0.35, 0.30, 0.25)
            glVertex3f(x0, y0, 0)
            glVertex3f(x1, y0, 0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x0, y1, 0)
    glEnd()

def draw_arena_walls():
    """Four coloured vertical boundary walls."""
    S = ARENA_SIZE
    H = WALL_HEIGHT
    glBegin(GL_QUADS)
    # North wall — blue
    glColor3f(0.15, 0.25, 0.75)
    glVertex3f(-S, S, 0);  glVertex3f(S, S, 0)
    glVertex3f(S, S, H);   glVertex3f(-S, S, H)
    # South wall — green
    glColor3f(0.15, 0.65, 0.25)
    glVertex3f(-S, -S, 0); glVertex3f(S, -S, 0)
    glVertex3f(S, -S, H);  glVertex3f(-S, -S, H)
    # East wall — red
    glColor3f(0.75, 0.15, 0.15)
    glVertex3f(S, -S, 0);  glVertex3f(S, S, 0)
    glVertex3f(S, S, H);   glVertex3f(S, -S, H)
    # West wall — gold
    glColor3f(0.85, 0.70, 0.10)
    glVertex3f(-S, -S, 0); glVertex3f(-S, S, 0)
    glVertex3f(-S, S, H);  glVertex3f(-S, -S, H)
    glEnd()

def draw_pillar(x, y):
    """Corner pillar: stacked cylinders + sphere top."""
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.6, 0.55, 0.45)
    q = gluNewQuadric()
    # Base drum
    gluCylinder(q, 18, 18, 80, 12, 4)
    glTranslatef(0, 0, 80)
    # Mid drum
    glColor3f(0.5, 0.45, 0.35)
    gluCylinder(q, 14, 14, 40, 12, 4)
    glTranslatef(0, 0, 40)
    # Capital sphere
    glColor3f(0.7, 0.65, 0.5)
    gluSphere(gluNewQuadric(), 20, 12, 12)
    glPopMatrix()

def draw_arena_pillars():
    S = ARENA_SIZE
    for cx, cy in [(-S, -S), (S, -S), (S, S), (-S, S)]:
        draw_pillar(cx, cy)

def draw_torch(x, y):
    """Wall torch: cylinder stick + pulsing sphere flame."""
    glPushMatrix()
    glTranslatef(x, y, WALL_HEIGHT * 0.7)
    # Stick
    glColor3f(0.4, 0.25, 0.1)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 20, 8, 2)
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0, 0, 22)
    # Flame pulse
    flame_scale = 1.0 + 0.3 * math.sin(anim_counter * 0.1)
    glScalef(flame_scale, flame_scale, flame_scale)
    glColor3f(1.0, 0.5, 0.05)
    gluSphere(gluNewQuadric(), 9, 8, 8)
    glPopMatrix()

def draw_torches():
    S = ARENA_SIZE - 5
    for tx, ty in [(0, S), (0, -S), (S, 0), (-S, 0)]:
        draw_torch(tx, ty)

def draw_collectibles():
    for c in collectibles:
        if not c[2]:
            glPushMatrix()
            glTranslatef(c[0], c[1], 8)
            spin = (anim_counter * 2) % 360
            glRotatef(spin, 0, 0, 1)
            glColor3f(1.0, 0.85, 0.0)
            glutSolidCube(16)
            glPopMatrix()

def draw_crowd():
    """Simple crowd silhouettes around the arena perimeter."""
    S = ARENA_SIZE + 40
    count = 16
    for i in range(count):
        angle = (i / count) * 360.0
        rad = math.radians(angle)
        cx = S * math.cos(rad)
        cy = S * math.sin(rad)
        glPushMatrix()
        glTranslatef(cx, cy, 0)
        # Body
        glColor3f(0.3 + 0.05 * (i % 5), 0.2, 0.4 + 0.05 * (i % 3))
        gluCylinder(gluNewQuadric(), 8, 6, 35, 8, 2)
        glTranslatef(0, 0, 40)
        # Head
        glColor3f(0.8, 0.65, 0.5)
        gluSphere(gluNewQuadric(), 9, 8, 8)
        # Raised arm (wave animation)
        glPushMatrix()
        wave = 20.0 * math.sin(anim_counter * 0.05 + i)
        glRotatef(wave, 1, 0, 0)
        glTranslatef(10, 0, 5)
        glColor3f(0.7, 0.55, 0.4)
        gluCylinder(gluNewQuadric(), 3, 2, 18, 6, 2)
        glPopMatrix()
        glPopMatrix()

# ─────────────────────────────────────────────
#  PLAYER DRAWING
# ─────────────────────────────────────────────
def draw_player():
    global player_death_angle
    glPushMatrix()
    glTranslatef(player_x, player_y, 0)
    glRotatef(player_angle, 0, 0, 1)      # facing direction

    # Death lie-down
    if player_dead:
        if player_death_angle < 90.0:
            player_death_angle += 2.0
        glRotatef(player_death_angle, 0, 1, 0)

    # --- Feet (cubes) ---
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.6)
    glTranslatef(-10, 0, 5)
    glutSolidCube(10)
    glTranslatef(20, 0, 0)
    glutSolidCube(10)
    glPopMatrix()

    # --- Lower legs (cylinders) ---
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.6)
    glTranslatef(-10, 0, 10)
    gluCylinder(gluNewQuadric(), 5, 4, 22, 8, 2)
    glTranslatef(20, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 22, 8, 2)
    glPopMatrix()

    # --- Upper legs (cylinders) ---
    glPushMatrix()
    glColor3f(0.25, 0.25, 0.65)
    glTranslatef(-10, 0, 32)
    gluCylinder(gluNewQuadric(), 6, 5, 22, 8, 2)
    glTranslatef(20, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 5, 22, 8, 2)
    glPopMatrix()

    # --- Torso (cube) ---
    glPushMatrix()
    glColor3f(0.25, 0.5, 0.25)
    glTranslatef(0, 0, 66)
    glScalef(1.0, 0.7, 1.0)
    glutSolidCube(36)
    glPopMatrix()

    # --- Neck (cylinder) ---
    glPushMatrix()
    glColor3f(0.75, 0.6, 0.5)
    glTranslatef(0, 0, 86)
    gluCylinder(gluNewQuadric(), 4, 4, 10, 8, 2)
    glPopMatrix()

    # --- Head (sphere) ---
    glPushMatrix()
    glColor3f(0.8, 0.65, 0.5)
    glTranslatef(0, 0, 100)
    gluSphere(gluNewQuadric(), 14, 12, 12)
    # Eyes
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(6, -12, 2)
    gluSphere(gluNewQuadric(), 2.5, 6, 6)
    glTranslatef(-12, 0, 0)
    gluSphere(gluNewQuadric(), 2.5, 6, 6)
    glPopMatrix()

    # --- LEFT arm: upper + lower + hand + shield ---
    glPushMatrix()
    glTranslatef(-22, 0, 72)
    glColor3f(0.25, 0.5, 0.25)
    gluCylinder(gluNewQuadric(), 5, 4, 20, 8, 2)   # upper arm
    glTranslatef(0, 0, 20)
    glColor3f(0.75, 0.6, 0.5)
    gluCylinder(gluNewQuadric(), 4, 3, 18, 8, 2)   # lower arm
    glTranslatef(0, 0, 18)
    # Shield (cube, raised when blocking)
    shield_tilt = -60.0 if blocking else -10.0
    glRotatef(shield_tilt, 1, 0, 0)
    glColor3f(0.5, 0.4, 0.1)
    glScalef(1.2, 0.25, 1.6)
    glutSolidCube(14)
    glPopMatrix()

    # --- RIGHT arm: upper + lower + hand + sword ---
    glPushMatrix()
    glTranslatef(22, 0, 72)
    # Apply swing rotation to right arm
    arm_angle = swing_angle if swing_active else 0.0
    glRotatef(arm_angle, 1, 0, 0)
    glColor3f(0.25, 0.5, 0.25)
    gluCylinder(gluNewQuadric(), 5, 4, 20, 8, 2)   # upper arm
    glTranslatef(0, 0, 20)
    glColor3f(0.75, 0.6, 0.5)
    gluCylinder(gluNewQuadric(), 4, 3, 18, 8, 2)   # lower arm
    glTranslatef(0, 0, 18)
    # Sword (cylinder blade)
    glColor3f(0.75, 0.75, 0.8)
    glRotatef(-15, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 1, 40, 8, 2)   # blade
    glTranslatef(0, 0, -6)
    glColor3f(0.6, 0.45, 0.1)
    glutSolidCube(8)                               # crossguard
    glPopMatrix()

    glPopMatrix()  # end player

def draw_facing_indicator():
    """Small cube in front of player showing facing direction."""
    rad = math.radians(player_angle)
    fx = player_x + 30 * math.sin(rad)
    fy = player_y + 30 * math.cos(rad)
    glPushMatrix()
    glTranslatef(fx, fy, 4)
    glColor3f(0.0, 1.0, 1.0)
    glutSolidCube(6)
    glPopMatrix()

# ─────────────────────────────────────────────
#  ENEMY DRAWING
# ─────────────────────────────────────────────
def draw_enemy(e):
    ex, ey, hp, etype, dead_timer, hit_flash, pulse_phase, death_angle = e
    if dead_timer > 0:
        return  # fully dead / respawning

    pulse = 1.0 + 0.15 * math.sin(anim_counter * 0.08 + pulse_phase)

    # Hit flash: override color
    if hit_flash > 0:
        r, g, b = 1.0, 1.0, 1.0
    else:
        r, g, b = ENEMY_COLOR[etype]

    glPushMatrix()
    glTranslatef(ex, ey, 0)

    # Death lie-down animation
    if death_angle > 0:
        glRotatef(min(death_angle, 90.0), 0, 1, 0)

    glScalef(pulse, pulse, pulse)

    if etype == ENEMY_TYPE_BRUTE:
        # Large sphere body + small sphere head + cube shoulders
        glColor3f(r, g, b)
        glTranslatef(0, 0, 30)
        gluSphere(gluNewQuadric(), 28, 14, 14)   # body
        glTranslatef(0, 0, 44)
        glColor3f(r * 0.8, g * 0.8, b * 0.8)
        gluSphere(gluNewQuadric(), 16, 12, 12)   # head
        # Shoulders
        glColor3f(r, g * 0.7, b * 0.7)
        glTranslatef(-36, 0, -20)
        glutSolidCube(18)
        glTranslatef(72, 0, 0)
        glutSolidCube(18)

    elif etype == ENEMY_TYPE_SPEEDER:
        # Small sphere body + cylinder legs
        glColor3f(r, g, b)
        glTranslatef(0, 0, 38)
        gluSphere(gluNewQuadric(), 18, 12, 12)   # body
        glTranslatef(0, 0, 28)
        glColor3f(r * 0.85, g * 0.85, b * 0.85)
        gluSphere(gluNewQuadric(), 11, 10, 10)   # head
        # Legs (2 cylinders)
        glColor3f(r, g, b)
        glTranslatef(-8, 0, -38)
        leg_tilt = 15.0 * math.sin(anim_counter * 0.15 + pulse_phase)
        glRotatef(leg_tilt, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 3, 28, 8, 2)
        glRotatef(-leg_tilt, 1, 0, 0)
        glTranslatef(16, 0, 0)
        glRotatef(-leg_tilt, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 3, 28, 8, 2)

    else:  # TANK
        # Big cube body + sphere head + cylinder arms
        glColor3f(r, g, b)
        glTranslatef(0, 0, 40)
        glScalef(1.3, 1.0, 1.2)
        glutSolidCube(50)                        # body
        glScalef(1/1.3, 1.0, 1/1.2)
        glTranslatef(0, 0, 52)
        glColor3f(r * 0.9, g * 0.9, b * 0.9)
        gluSphere(gluNewQuadric(), 20, 14, 14)   # head
        # Arms
        glColor3f(r, g, b)
        glTranslatef(-45, 0, -25)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 7, 5, 35, 8, 2)
        glRotatef(-90, 0, 1, 0)
        glTranslatef(90, 0, 0)
        glRotatef(-90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 7, 5, 35, 8, 2)

    glPopMatrix()

# ─────────────────────────────────────────────
#  BULLETS
# ─────────────────────────────────────────────
def fire_bullet():
    if len(bullets) >= MAX_BULLETS:
        return
    rad = math.radians(player_angle)
    dx = math.sin(rad) * BULLET_SPEED
    dy = math.cos(rad) * BULLET_SPEED
    bullets.append([player_x, player_y, dx, dy, True])

def draw_bullets():
    for b in bullets:
        if b[4]:
            glPushMatrix()
            glTranslatef(b[0], b[1], 14)
            spin = (anim_counter * 5) % 360
            glRotatef(spin, 1, 1, 0)
            glColor3f(1.0, 0.8, 0.1)
            glutSolidCube(10)
            glPopMatrix()

# ─────────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────────
def bar_string(val, max_val, length=10):
    filled = int((val / max_val) * length)
    filled = max(0, min(length, filled))
    return '#' * filled + '.' * (length - filled)

def draw_hud():
    # HP bar
    hp_color = (0.2, 0.9, 0.2) if player_hp > 50 else (0.9, 0.5, 0.1) if player_hp > 25 else (0.9, 0.1, 0.1)
    draw_text_color(10, WINDOW_H - 28,  f"HP  [{bar_string(player_hp, 100)}] {player_hp}/100", *hp_color)
    # Stamina bar
    draw_text_color(10, WINDOW_H - 50, f"STA [{bar_string(int(player_stamina), 100)}] {int(player_stamina)}/100", 0.3, 0.7, 1.0)
    # Score
    draw_text_color(10, WINDOW_H - 78, f"Score: {score}", 1.0, 0.9, 0.2)
    # Combo
    if combo > 1:
        draw_text_color(10, WINDOW_H - 102, f"Combo: x{combo}!", 1.0, 0.4, 0.1)
    # Round
    draw_text_color(WINDOW_W - 180, WINDOW_H - 28, f"Round: {game_round}", 0.9, 0.8, 0.3)
    # Enemies alive
    alive = sum(1 for e in enemies if e[4] == 0)
    draw_text_color(WINDOW_W - 180, WINDOW_H - 52, f"Enemies: {alive}", 0.9, 0.3, 0.3)
    # Camera mode
    mode = "1st Person" if first_person else "3rd Person"
    draw_text_color(WINDOW_W - 180, WINDOW_H - 76, f"Cam: {mode}", 0.7, 0.7, 0.7)
    # Controls
    draw_text_color(10, 80, "WASD:Move  Space:Slash  LClick:Throw", 0.6, 0.6, 0.6, GLUT_BITMAP_HELVETICA_12)
    draw_text_color(10, 64, "RClick:Block  Shift:Sprint  Z/X:Zoom", 0.6, 0.6, 0.6, GLUT_BITMAP_HELVETICA_12)
    draw_text_color(10, 48, "Arrows:Camera  R:Restart", 0.6, 0.6, 0.6, GLUT_BITMAP_HELVETICA_12)
    # Blocking indicator
    if blocking:
        draw_text_color(WINDOW_W//2 - 50, WINDOW_H - 100, "[ BLOCKING ]", 0.3, 0.6, 1.0)
    # Sprint indicator
    if speed_boost and player_stamina > 0:
        draw_text_color(WINDOW_W//2 - 40, WINDOW_H - 78, "[ SPRINT ]", 0.3, 1.0, 0.5)
    # Round announcement
    if round_announce_timer > 0:
        draw_text_color(WINDOW_W//2 - 80, WINDOW_H//2, f"ROUND  {game_round}", 1.0, 0.8, 0.1, GLUT_BITMAP_TIMES_ROMAN_24)

def draw_game_over_screen():
    draw_text_color(WINDOW_W//2 - 100, WINDOW_H//2 + 30, "GAME  OVER", 0.9, 0.1, 0.1, GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text_color(WINDOW_W//2 - 80, WINDOW_H//2 - 10, f"Final Score: {score}", 1.0, 0.9, 0.2, GLUT_BITMAP_HELVETICA_18)
    draw_text_color(WINDOW_W//2 - 90, WINDOW_H//2 - 40, "Press  R  to  Restart", 0.8, 0.8, 0.8, GLUT_BITMAP_HELVETICA_18)

def draw_victory_screen():
    draw_text_color(WINDOW_W//2 - 90, WINDOW_H//2 + 30, "VICTORY!", 0.2, 1.0, 0.3, GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text_color(WINDOW_W//2 - 80, WINDOW_H//2 - 10, f"Final Score: {score}", 1.0, 0.9, 0.2, GLUT_BITMAP_HELVETICA_18)
    draw_text_color(WINDOW_W//2 - 90, WINDOW_H//2 - 40, "Press  R  to  Play Again", 0.8, 0.8, 0.8, GLUT_BITMAP_HELVETICA_18)

# ─────────────────────────────────────────────
#  CAMERA
# ─────────────────────────────────────────────
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_W / WINDOW_H, 1.0, 3000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        # Camera at player head, looking in facing direction
        rad = math.radians(player_angle)
        eye_x = player_x
        eye_y = player_y
        eye_z = 105.0
        look_x = eye_x + math.sin(rad) * 200
        look_y = eye_y + math.cos(rad) * 200
        look_z = 100.0
        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, look_z,
                  0, 0, 1)
    else:
        # Orbit camera: cam_angle rotates around arena
        rad = math.radians(cam_angle)
        cx = cam_radius * math.cos(rad)
        cy = cam_radius * math.sin(rad)
        cz = cam_height
        gluLookAt(cx, cy, cz,
                  0, 0, 40,
                  0, 0, 1)

# ─────────────────────────────────────────────
#  LOGIC / UPDATE
# ─────────────────────────────────────────────
def check_bullet_enemy_collision():
    global score, combo, combo_timer, kills_this_combo, kills_this_round, game_round, round_announce_timer, victory
    for b in bullets:
        if not b[4]:
            continue
        for e in enemies:
            if e[4] > 0:
                continue
            dist = math.hypot(b[0] - e[0], b[1] - e[1])
            hit_radius = 35 if e[3] == ENEMY_TYPE_TANK else 26 if e[3] == ENEMY_TYPE_BRUTE else 20
            if dist < hit_radius:
                b[4] = False
                e[2] -= 1          # reduce enemy HP
                e[5] = 8           # hit flash frames
                if e[2] <= 0:
                    e[4] = 60      # respawn timer (frames)
                    # Score
                    combo_timer = COMBO_TIMEOUT
                    kills_this_combo += 1
                    if kills_this_combo > 1:
                        combo = min(kills_this_combo, 8)
                    pts = ENEMY_SCORE[e[3]] * combo
                    score += pts
                    kills_this_round += 1
                    if kills_this_round >= 10:
                        kills_this_round = 0
                        game_round += 1
                        round_announce_timer = ROUND_DISPLAY_FRAMES
                        if game_round > 5:
                            victory = True

def check_melee_enemy_collision():
    """Melee sword sweep: checks enemies in front arc."""
    global score, combo, combo_timer, kills_this_combo, kills_this_round, game_round, round_announce_timer, victory
    if not swing_active:
        return
    if swing_timer != 1:   # only on first frame of swing
        return
    rad = math.radians(player_angle)
    for e in enemies:
        if e[4] > 0:
            continue
        dist = math.hypot(player_x - e[0], player_y - e[1])
        if dist < 90:
            # Check if enemy is in 120° forward arc
            to_ex = e[0] - player_x
            to_ey = e[1] - player_y
            if dist == 0:
                continue
            dot = (math.sin(rad) * to_ex + math.cos(rad) * to_ey) / dist
            if dot > math.cos(math.radians(60)):
                e[2] -= 2
                e[5] = 12
                if e[2] <= 0:
                    e[4] = 60
                    combo_timer = COMBO_TIMEOUT
                    kills_this_combo += 1
                    combo = min(kills_this_combo if kills_this_combo > 1 else 1, 8)
                    score += ENEMY_SCORE[e[3]] * combo
                    kills_this_round += 1
                    if kills_this_round >= 10:
                        kills_this_round = 0
                        game_round += 1
                        round_announce_timer = ROUND_DISPLAY_FRAMES
                        if game_round > 5:
                            victory = True

def check_player_enemy_collision():
    """Enemies that touch the player deal damage."""
    global player_hp, player_dead, game_over
    for e in enemies:
        if e[4] > 0:
            continue
        dist = math.hypot(player_x - e[0], player_y - e[1])
        if dist < 45:
            damage = 1 if blocking else 2
            player_hp -= damage
            # Push enemy back slightly
            if dist > 0:
                nx = (e[0] - player_x) / dist
                ny = (e[1] - player_y) / dist
                e[0] += nx * 5
                e[1] += ny * 5
            if player_hp <= 0:
                player_hp = 0
                player_dead = True
                game_over = True

def check_collectible_pickup():
    global player_hp, player_stamina
    for c in collectibles:
        if c[2]:
            continue
        dist = math.hypot(player_x - c[0], player_y - c[1])
        if dist < 30:
            c[2] = True
            player_hp = min(100, player_hp + 20)
            player_stamina = min(100.0, player_stamina + 30.0)

def update_enemies():
    """Move enemies toward player; handle respawn; update death anim."""
    speed_mult = 1.0 + (game_round - 1) * 0.2
    for e in enemies:
        if e[4] > 0:
            e[4] -= 1
            if e[4] == 0:
                # Respawn
                new_e = spawn_enemy()
                e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7] = new_e
            # Animate death tilt
            if e[7] < 90.0:
                e[7] += 4.0
            continue
        if e[5] > 0:
            e[5] -= 1
        # Chase player
        dist = math.hypot(player_x - e[0], player_y - e[1])
        if dist > 2:
            spd = ENEMY_SPEED[e[3]] * speed_mult
            nx = (player_x - e[0]) / dist
            ny = (player_y - e[1]) / dist
            e[0] += nx * spd
            e[1] += ny * spd
        # Clamp to arena
        e[0] = max(-ARENA_SIZE + 20, min(ARENA_SIZE - 20, e[0]))
        e[1] = max(-ARENA_SIZE + 20, min(ARENA_SIZE - 20, e[1]))

def update_bullets():
    for b in bullets:
        if b[4]:
            b[0] += b[2]
            b[1] += b[3]
            if abs(b[0]) > ARENA_SIZE or abs(b[1]) > ARENA_SIZE:
                b[4] = False

def update_swing():
    global swing_active, swing_angle, swing_dir, swing_timer
    if swing_active:
        swing_timer += 1
        swing_angle += swing_dir * 12.0
        if swing_angle > 100.0:
            swing_dir = -1
        if swing_angle < 0.0:
            swing_active = False
            swing_angle = 0.0
            swing_timer = 0
            swing_dir = 1

def update_combo():
    global combo, combo_timer, kills_this_combo
    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo = 1
        kills_this_combo = 0

def update_stamina():
    global player_stamina
    if speed_boost and player_stamina > 0:
        player_stamina = max(0.0, player_stamina - 0.4)
    elif swing_active:
        player_stamina = max(0.0, player_stamina - 0.1)
    else:
        player_stamina = min(100.0, player_stamina + 0.15)

def update_round_timer():
    global round_announce_timer
    if round_announce_timer > 0:
        round_announce_timer -= 1

def respawn_collectibles_if_all_taken():
    if all(c[2] for c in collectibles):
        spawn_collectibles()

# ─────────────────────────────────────────────
#  INPUT HANDLERS
# ─────────────────────────────────────────────
def keyboardListener(key, x, y):
    global player_x, player_y, player_angle, player_stamina
    global swing_active, swing_dir, swing_angle, swing_timer
    global fovY, speed_boost, game_over, victory

    if key == b'r':
        reset_game()
        return

    if game_over or victory:
        return

    rad = math.radians(player_angle)
    spd = PLAYER_SPEED * (1.6 if (speed_boost and player_stamina > 0) else 1.0)

    if key == b'w':
        nx = player_x + math.sin(rad) * spd
        ny = player_y + math.cos(rad) * spd
        nx = max(-ARENA_SIZE + 20, min(ARENA_SIZE - 20, nx))
        ny = max(-ARENA_SIZE + 20, min(ARENA_SIZE - 20, ny))
        player_x, player_y = nx, ny

    elif key == b's':
        nx = player_x - math.sin(rad) * spd
        ny = player_y - math.cos(rad) * spd
        nx = max(-ARENA_SIZE + 20, min(ARENA_SIZE - 20, nx))
        ny = max(-ARENA_SIZE + 20, min(ARENA_SIZE - 20, ny))
        player_x, player_y = nx, ny

    elif key == b'a':
        player_angle = (player_angle - PLAYER_ROT_SPD) % 360

    elif key == b'd':
        player_angle = (player_angle + PLAYER_ROT_SPD) % 360

    elif key == b' ':
        if not swing_active and player_stamina > 10:
            swing_active = True
            swing_angle = 0.0
            swing_dir = 1
            swing_timer = 0
            player_stamina = max(0, player_stamina - 10)

    elif key == b'z':
        fovY = max(20.0, fovY - 5.0)

    elif key == b'x':
        fovY = min(120.0, fovY + 5.0)

    # Shift for sprint
    elif key == b'\x10':  # Shift (fallback)
        speed_boost = not speed_boost

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global cam_angle, cam_height, speed_boost

    if key == GLUT_KEY_LEFT:
        cam_angle = (cam_angle - 3.0) % 360
    elif key == GLUT_KEY_RIGHT:
        cam_angle = (cam_angle + 3.0) % 360
    elif key == GLUT_KEY_UP:
        cam_height = min(1200.0, cam_height + 20.0)
    elif key == GLUT_KEY_DOWN:
        cam_height = max(80.0, cam_height - 20.0)
    elif key == GLUT_KEY_SHIFT_L or key == GLUT_KEY_SHIFT_R:
        speed_boost = not speed_boost

    glutPostRedisplay()


def mouseListener(button, state, x, y):
    global blocking, first_person

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not (game_over or victory) and not player_dead:
            fire_bullet()

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if not (game_over or victory):
            first_person = not first_person

    # Middle mouse button toggles blocking
    elif button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            blocking = True
        else:
            blocking = False

    glutPostRedisplay()

# ─────────────────────────────────────────────
#  IDLE & DISPLAY
# ─────────────────────────────────────────────
def idle():
    global anim_counter, frame_count, blocking

    if not (game_over or victory or player_dead):
        update_enemies()
        update_bullets()
        update_swing()
        update_combo()
        update_stamina()
        update_round_timer()
        check_bullet_enemy_collision()
        check_melee_enemy_collision()
        check_player_enemy_collision()
        check_collectible_pickup()
        respawn_collectibles_if_all_taken()

    anim_counter += 1
    frame_count   += 1

    glutPostRedisplay()


def showScreen():
    glClearColor(0.02, 0.02, 0.05, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_W, WINDOW_H)

    setup_camera()

    # ── World geometry ──
    draw_checkerboard_floor()
    draw_arena_walls()
    draw_arena_pillars()
    draw_torches()
    draw_crowd()
    draw_collectibles()
    draw_facing_indicator()
    draw_player()

    for e in enemies:
        draw_enemy(e)

    draw_bullets()

    # ── HUD (2D overlay) ──
    glDisable(GL_DEPTH_TEST)
    draw_hud()
    if game_over:
        draw_game_over_screen()
    if victory:
        draw_victory_screen()
    glEnable(GL_DEPTH_TEST)

    glutSwapBuffers()

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    reset_game()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Gladiator Arena")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()

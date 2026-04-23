from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# =============================================================================
# GAME ENGINE VARIABLES
# =============================================================================

# Player / Camera
player_pos  = [0.0, -80.0, 50.0]   # X, Y, Z  (Z is height / up-axis)
yaw         = 90.0                   # Horizontal look angle (degrees)
pitch       = -15.0                  # Vertical   look angle (degrees)

# Mouse state
last_mouse_x = 500
last_mouse_y = 400
mouse_sensitivity = 0.18

# Window

WINDOW_W = 1000
WINDOW_H = 800

# Projection
fovY        = 90
GRID_LENGTH = 600

# Voxel world
BLOCK_SIZE  = 25            # World-units per block
world_blocks = {}           # (ix, iy, iz) -> (r, g, b)

# Held block colour (cycles with keys 1-5)
PALETTE = [
    (0.55, 0.27, 0.07),     # 1  Wood / dirt brown
    (0.25, 0.70, 0.25),     # 2  Grass green
    (0.55, 0.55, 0.55),     # 3  Stone grey
    (0.90, 0.80, 0.20),     # 4  Sand / gold
    (0.25, 0.55, 0.90),     # 5  Water / ice blue
]
held_color_index = 0

# HUD / state
score        = 0            # blocks broken
blocks_placed = 0
game_mode    = "Survival"   # "Survival" | "Creative"
cheat_mode   = False        # show hidden info
show_help    = True

# Gravity / jumping (Survival only)
vel_z        = 0.0
GRAVITY      = -1.2
JUMP_VEL     = 14.0
on_ground    = False

# =============================================================================
# WORLD GENERATION
# =============================================================================

def _set(ix, iy, iz, color):
    world_blocks[(ix, iy, iz)] = color

def init_world():
    """Generate a basic voxel terrain: flat grass, some hills, trees, a path."""
    random.seed(42)

    # --- Flat grass base layer ---
    for ix in range(-14, 15):
        for iy in range(-14, 15):
            _set(ix, iy, 0, (0.22, 0.68, 0.22))        # grass top
            _set(ix, iy, -1, (0.45, 0.30, 0.15))       # dirt below

    # --- Stone underground (2 layers) ---
    for ix in range(-14, 15):
        for iy in range(-14, 15):
            for iz in [-2, -3]:
                _set(ix, iy, iz, (0.50, 0.50, 0.50))

    # --- Small hills (random raised land) ---
    for _ in range(10):
        cx = random.randint(-10, 10)
        cy = random.randint(-10, 10)
        for ix in range(cx-2, cx+3):
            for iy in range(cy-2, cy+3):
                if abs(ix-cx) + abs(iy-cy) <= 3:
                    _set(ix, iy, 1, (0.22, 0.68, 0.22))
                    if abs(ix-cx) + abs(iy-cy) <= 1:
                        _set(ix, iy, 2, (0.22, 0.68, 0.22))

    # --- Dirt path down the middle ---
    for iy in range(-14, 15):
        _set(0, iy, 0, (0.60, 0.45, 0.25))
        _set(1, iy, 0, (0.60, 0.45, 0.25))

    # --- Trees ---
    tree_spots = [(-6, -6), (6, -8), (-8, 5), (5, 6), (-3, 10),
                  (10, -3), (-11, 2), (3, -11)]
    for tx, ty in tree_spots:
        # Guard: place only if ground exists
        if (tx, ty, 0) in world_blocks:
            # Trunk (3 blocks)
            for iz in range(1, 4):
                _set(tx, ty, iz, (0.36, 0.20, 0.08))
            # Leaf canopy
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    for dz in [4, 5]:
                        if abs(dx) + abs(dy) <= 3:
                            _set(tx+dx, ty+dy, dz, (0.10, 0.50, 0.10))
            # Pointy top
            _set(tx, ty, 6, (0.10, 0.50, 0.10))

    # --- Small cabin in one corner ---
    # Walls (wood)
    for side in range(5):
        _set(-12+side, -12,   1, (0.45, 0.25, 0.10))
        _set(-12+side, -8,    1, (0.45, 0.25, 0.10))
        _set(-12,      -12+side, 1, (0.45, 0.25, 0.10))
        _set(-8,       -12+side, 1, (0.45, 0.25, 0.10))
    # Roof (stone)
    for ix in range(-12, -7):
        for iy in range(-12, -7):
            _set(ix, iy, 2, (0.55, 0.55, 0.55))

init_world()


# =============================================================================
# UTILITY HELPERS
# =============================================================================

def _look_dir():
    """Return the normalised forward look direction as (dx, dy, dz)."""
    ry = math.radians(yaw)
    rp = math.radians(pitch)
    return (
        math.cos(ry) * math.cos(rp),
        math.sin(ry) * math.cos(rp),
        math.sin(rp),
    )

def _block_under_player():
    """Return block index directly below the player's feet."""
    bx = round(player_pos[0] / BLOCK_SIZE)
    by = round(player_pos[1] / BLOCK_SIZE)
    bz = int(math.floor(player_pos[2] / BLOCK_SIZE)) - 1
    return (bx, by, bz)

def _player_on_block():
    """True if there is a block directly below the player."""
    return _block_under_player() in world_blocks

def _raycast(steps=120, reach=200.0):
    """
    March a ray from the camera outward.
    Returns (hit_block, prev_block) or (None, None).
    """
    dx, dy, dz = _look_dir()
    step = reach / steps
    cx, cy, cz = player_pos[0], player_pos[1], player_pos[2]
    prev = None
    for _ in range(steps):
        bx = round(cx / BLOCK_SIZE)
        by = round(cy / BLOCK_SIZE)
        bz = round(cz / BLOCK_SIZE)
        key = (bx, by, bz)
        if key in world_blocks:
            return key, prev
        prev = key
        cx += dx * step
        cy += dy * step
        cz += dz * step
    return None, None


# =============================================================================
# DRAWING PRIMITIVES
# =============================================================================

def draw_cube_unit():
    """Draw a 1×1×1 cube centred at origin using GL_QUADS with normals."""
    s = 0.5
    glBegin(GL_QUADS)
    # +Y face (back)
    glNormal3f(0, 1, 0)
    glVertex3f(-s,  s, -s); glVertex3f( s,  s, -s)
    glVertex3f( s,  s,  s); glVertex3f(-s,  s,  s)
    # -Y face (front)
    glNormal3f(0, -1, 0)
    glVertex3f(-s, -s,  s); glVertex3f( s, -s,  s)
    glVertex3f( s, -s, -s); glVertex3f(-s, -s, -s)
    # +X face (right)
    glNormal3f(1, 0, 0)
    glVertex3f( s, -s,  s); glVertex3f( s,  s,  s)
    glVertex3f( s,  s, -s); glVertex3f( s, -s, -s)
    # -X face (left)
    glNormal3f(-1, 0, 0)
    glVertex3f(-s, -s, -s); glVertex3f(-s,  s, -s)
    glVertex3f(-s,  s,  s); glVertex3f(-s, -s,  s)
    # +Z face (top)
    glNormal3f(0, 0, 1)
    glVertex3f(-s, -s,  s); glVertex3f( s, -s,  s)
    glVertex3f( s,  s,  s); glVertex3f(-s,  s,  s)
    # -Z face (bottom)
    glNormal3f(0, 0, -1)
    glVertex3f(-s, -s, -s); glVertex3f( s, -s, -s)
    glVertex3f( s,  s, -s); glVertex3f(-s,  s, -s)
    glEnd()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draw 2-D HUD text at screen pixel (x, y)."""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_crosshair():
    """Render a simple + crosshair in the screen centre."""
    cx, cy = WINDOW_W / 2, WINDOW_H / 2
    size = 10
    glColor3f(1, 1, 1)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(cx - size, cy); glVertex2f(cx + size, cy)
    glVertex2f(cx, cy - size); glVertex2f(cx, cy + size)
    glEnd()
    glLineWidth(1)


def draw_block_outline(bx, by, bz):
    """Wireframe outline around the targeted block."""
    s = BLOCK_SIZE * 0.52          # slightly larger than block
    wx = bx * BLOCK_SIZE
    wy = by * BLOCK_SIZE
    wz = bz * BLOCK_SIZE
    glLineWidth(2)
    glColor3f(0, 0, 0)
    glDisable(GL_LIGHTING)
    # Draw 12 edges of the box
    corners = [
        (wx-s, wy-s, wz-s), (wx+s, wy-s, wz-s),
        (wx+s, wy+s, wz-s), (wx-s, wy+s, wz-s),
        (wx-s, wy-s, wz+s), (wx+s, wy-s, wz+s),
        (wx+s, wy+s, wz+s), (wx-s, wy+s, wz+s),
    ]
    edges = [
        (0,1),(1,2),(2,3),(3,0),    # bottom ring
        (4,5),(5,6),(6,7),(7,4),    # top ring
        (0,4),(1,5),(2,6),(3,7),    # verticals
    ]
    glBegin(GL_LINES)
    for a, b in edges:
        glVertex3fv(corners[a]); glVertex3fv(corners[b])
    glEnd()
    glLineWidth(1)


# =============================================================================
# WORLD RENDER
# =============================================================================

def draw_shapes():
    """Render all voxels and draw an outline on the targeted block."""
    # --- Lighting setup ---
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_POSITION, [200.0, 200.0, 400.0, 0.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.85, 0.85, 0.80, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.30, 0.30, 0.35, 1.0])

    # --- Draw every block ---
    for (ix, iy, iz), color in world_blocks.items():
        glPushMatrix()
        glColor3f(*color)
        glTranslatef(ix * BLOCK_SIZE, iy * BLOCK_SIZE, iz * BLOCK_SIZE)
        glScalef(BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        draw_cube_unit()
        glPopMatrix()

    glDisable(GL_LIGHTING)

    # --- Outline targeted block ---
    hit, _ = _raycast()
    if hit:
        draw_block_outline(*hit)


# =============================================================================
# INPUT HANDLERS
# =============================================================================

def keyboardListener(key, x, y):
    """WASD + Space/C movement, palette swap, modes, reset."""
    global player_pos, held_color_index, game_mode, cheat_mode, show_help
    global vel_z, score, blocks_placed

    speed = 8.0 if game_mode == "Creative" else 5.0
    ry = math.radians(yaw)

    forward_x = math.cos(ry)
    forward_y = math.sin(ry)
    right_x   =  math.sin(ry)
    right_y   = -math.cos(ry)

    # --- Movement ---
    if key == b'w':
        player_pos[0] += forward_x * speed
        player_pos[1] += forward_y * speed
    if key == b's':
        player_pos[0] -= forward_x * speed
        player_pos[1] -= forward_y * speed
    if key == b'a':
        player_pos[0] -= right_x * speed
        player_pos[1] -= right_y * speed
    if key == b'd':
        player_pos[0] += right_x * speed
        player_pos[1] += right_y * speed

    # Jump / fly-up
    if key == b' ':
        if game_mode == "Creative":
            player_pos[2] += speed
        elif on_ground:
            vel_z = JUMP_VEL

    # Fly-down (Creative) / descend
    if key == b'x':
        if game_mode == "Creative":
            player_pos[2] -= speed

    # --- Palette selection (1-5) ---
    if key == b'1': held_color_index = 0
    if key == b'2': held_color_index = 1
    if key == b'3': held_color_index = 2
    if key == b'4': held_color_index = 3
    if key == b'5': held_color_index = 4

    # --- Game-mode toggle ---
    if key == b'g':
        game_mode = "Creative" if game_mode == "Survival" else "Survival"
        vel_z = 0.0

    # --- Cheat / debug overlay ---
    if key == b'c':
        cheat_mode = not cheat_mode

    # --- Help toggle ---
    if key == b'h':
        show_help = not show_help

    # --- Reset ---
    if key == b'r':
        world_blocks.clear()
        score = 0
        blocks_placed = 0
        player_pos[:] = [0.0, -80.0, 50.0]
        vel_z = 0.0
        init_world()

    # --- Quit ---
    if key == b'\x1b':   # Escape
        import sys; sys.exit(0)


def specialKeyListener(key, x, y):
    """Arrow keys: look left/right, tilt up/down."""
    global yaw, pitch
    step = 3.0
    if key == GLUT_KEY_LEFT:
        yaw -= step
    if key == GLUT_KEY_RIGHT:
        yaw += step
    if key == GLUT_KEY_UP:
        pitch = min(89.0, pitch + step)
    if key == GLUT_KEY_DOWN:
        pitch = max(-89.0, pitch - step)


def passiveMouseListener(x, y):
    """Track mouse movement for smooth first-person look."""
    global yaw, pitch, last_mouse_x, last_mouse_y

    dx = x - last_mouse_x
    dy = y - last_mouse_y

    yaw   += dx * mouse_sensitivity
    pitch -= dy * mouse_sensitivity
    pitch  = max(-89.0, min(89.0, pitch))

    last_mouse_x = x
    last_mouse_y = y


def mouseListener(button, state, x, y):
    """Left-click = break block; Right-click = place block."""
    global score, blocks_placed

    if state != GLUT_DOWN:
        return

    hit, prev = _raycast()

    # --- Break block (left) ---
    if button == GLUT_LEFT_BUTTON and hit:
        bx, by, bz = hit
        if bz >= 0:          # prevent breaking bedrock (layer -3)
            del world_blocks[hit]
            score += 1

    # --- Place block (right) ---
    if button == GLUT_RIGHT_BUTTON and hit and prev:
        world_blocks[prev] = PALETTE[held_color_index]
        blocks_placed += 1


# =============================================================================
# PHYSICS (idle tick)
# =============================================================================

def apply_physics():
    """Simple gravity + ground collision for Survival mode."""
    global vel_z, player_pos, on_ground

    if game_mode != "Survival":
        on_ground = False
        return

    vel_z += GRAVITY * 0.05          # gravity step
    player_pos[2] += vel_z * 0.1

    # Check block directly below
    bx = round(player_pos[0] / BLOCK_SIZE)
    by = round(player_pos[1] / BLOCK_SIZE)
    bz = int(math.floor(player_pos[2] / BLOCK_SIZE)) - 1
    foot_height = (bz + 1) * BLOCK_SIZE

    if (bx, by, bz) in world_blocks:
        if player_pos[2] <= foot_height + 0.5:
            player_pos[2] = foot_height + 0.5
            vel_z = 0.0
            on_ground = True
    else:
        on_ground = False

    # Hard floor so player can't fall forever
    if player_pos[2] < -4 * BLOCK_SIZE:
        player_pos[2] = 60.0
        vel_z = 0.0


# =============================================================================
# CAMERA
# =============================================================================

def setupCamera():
    """First-person perspective camera."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_W / WINDOW_H, 0.5, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    ry = math.radians(yaw)
    rp = math.radians(pitch)

    lx = player_pos[0] + math.cos(ry) * math.cos(rp)
    ly = player_pos[1] + math.sin(ry) * math.cos(rp)
    lz = player_pos[2] + math.sin(rp)

    gluLookAt(
        player_pos[0], player_pos[1], player_pos[2],
        lx, ly, lz,
        0, 0, 1
    )


# =============================================================================
# HUD OVERLAY
# =============================================================================

def draw_hud():
    """All 2-D screen text and UI elements."""
    # Save 3-D state, switch to ortho
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    # -- Crosshair --
    draw_crosshair()

    # -- Top-left info --
    draw_text(12, WINDOW_H - 26,  f"Mode : {game_mode}", GLUT_BITMAP_HELVETICA_18)
    draw_text(12, WINDOW_H - 50,  f"Blocks Broken : {score}",    GLUT_BITMAP_HELVETICA_18)
    draw_text(12, WINDOW_H - 74,  f"Blocks Placed : {blocks_placed}", GLUT_BITMAP_HELVETICA_18)

    # -- Held block colour swatch label --
    pname = ["Brown","Green","Stone","Sand","Blue"][held_color_index]
    draw_text(12, WINDOW_H - 100, f"Held  : [{held_color_index+1}] {pname}", GLUT_BITMAP_HELVETICA_18)

    # -- Cheat debug info --
    if cheat_mode:
        px, py, pz = [round(v, 1) for v in player_pos]
        draw_text(12, WINDOW_H - 130, f"Pos   : ({px}, {py}, {pz})", GLUT_BITMAP_HELVETICA_12)
        draw_text(12, WINDOW_H - 148, f"Yaw   : {round(yaw,1)}   Pitch : {round(pitch,1)}",
                  GLUT_BITMAP_HELVETICA_12)
        bx = round(player_pos[0]/BLOCK_SIZE)
        by = round(player_pos[1]/BLOCK_SIZE)
        bz = round(player_pos[2]/BLOCK_SIZE)
        draw_text(12, WINDOW_H - 166, f"Block : ({bx},{by},{bz})  World blocks: {len(world_blocks)}",
                  GLUT_BITMAP_HELVETICA_12)
        hit, _ = _raycast()
        draw_text(12, WINDOW_H - 184, f"Target: {hit}", GLUT_BITMAP_HELVETICA_12)

    # -- Help overlay --
    if show_help:
        hy = 140
        draw_text(WINDOW_W - 290, hy,      "[ Controls ]",          GLUT_BITMAP_HELVETICA_18)
        draw_text(WINDOW_W - 290, hy - 24, "W/A/S/D  - Move",       GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 40, "SPACE    - Jump / Up",   GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 56, "X        - Fly Down",    GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 72, "Mouse    - Look Around", GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 88, "LMB      - Break Block", GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 104,"RMB      - Place Block", GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 120,"1-5      - Pick Colour", GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 136,"G        - Toggle Mode", GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 152,"C        - Debug info",  GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 168,"R        - Reset World", GLUT_BITMAP_HELVETICA_12)
        draw_text(WINDOW_W - 290, hy - 184,"H        - Hide Help",   GLUT_BITMAP_HELVETICA_12)

    # Restore
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# =============================================================================
# GLUT CALLBACKS
# =============================================================================

def idle():
    """Runs continuously — physics tick + redraw trigger."""
    apply_physics()
    glutPostRedisplay()


def showScreen():
    """Main render callback."""
    glClearColor(0.52, 0.74, 0.94, 1.0)       # Sky blue background
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_W, WINDOW_H)

    setupCamera()   # position first-person camera
    draw_shapes()   # render the voxel world
    draw_hud()      # 2-D overlay on top

    glutSwapBuffers()


# =============================================================================
# MAIN
# =============================================================================

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Minecraft Clone - PyOpenGL")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutPassiveMotionFunc(passiveMouseListener)   # smooth mouse-look
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()

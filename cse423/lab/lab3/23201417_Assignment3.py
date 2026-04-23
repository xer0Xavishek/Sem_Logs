from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import time
import random

# ========================= Game Constants =========================

BULLET_SPEED = 1111
ENEMY_SPEED = 55
ENEMY_GROWTH_SPEED = 0.09
ENEMY_MIN_RADIUS = 15
ENEMY_MAX_RADIUS = 22
NUM_ENEMIES = 5
MAX_MISSED_BULLETS = 10
INITIAL_LIFE = 5
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800


# ========================= Game Variables =========================
game_over = False
cheating = False
bullets = []
enemies = []
lives = 5
bullets_missed = 0
score = 0
last_time = time.perf_counter()


# =============================Camera===============================
camera_radius = 500
camera_height = 500
camera_angle = 0
camera_mode = "3rd"
fovY = 100
frozen_camera_angle = 0


# =============================Player===============================
player_x, player_y, player_z = 0, 0, 0
player_angle = 0
player_speed = 111
player_rotation_speed = 111
moving_front = False
moving_back = False
rotating_left = False
rotating_right = False

# ==============================Enemy===============================
got_enemy = []
auto_aim_camera = False


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_player():
    global game_over, player_angle, player_x, player_y, player_z
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    glScalef(0.66, 0.66, 0.66)
    if game_over:
        glRotatef(90, 1, 0, 0)
    else:
        glRotatef(player_angle, 0, 0, 1)

    # ===Body===
    glPushMatrix()
    glColor3f(85 / 255, 107 / 255, 46 / 255)

    glScalef(2, 1, 2)
    glTranslatef(0, 0, 25)
    glutSolidCube(33)
    glPopMatrix()

    # ===Legs===
    glPushMatrix()
    glColor3f(0.0, 0.0, 1.0)
    # left
    glPushMatrix()
    glTranslatef(-20, 0, -30)
    gluCylinder(gluNewQuadric(), 5, 15, 50, 10, 10)
    glPopMatrix()
    # right
    glPushMatrix()
    glTranslatef(20, 0, -30)
    gluCylinder(gluNewQuadric(), 5, 15, 50, 10, 10)
    glPopMatrix()
    glPopMatrix()

    # ===Head===
    glPushMatrix()
    glColor3f(0, 0, 0)
    glTranslatef(0, 0, 99)
    gluSphere(gluNewQuadric(), 22, 12, 12)
    glPopMatrix()

    # ===Arms===
    glPushMatrix()
    glColor3f(255 / 255, 224 / 255, 189 / 255)
    # left
    glPushMatrix()
    glTranslatef(-30, 0, 66)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 50, 15, 10)
    glPopMatrix()
    # right
    glPushMatrix()
    glTranslatef(30, 0, 66)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 50, 15, 10)
    glPopMatrix()
    glPopMatrix()

    # ===Gun===
    glPushMatrix()
    glColor3f(192 / 255, 192 / 255, 192 / 255)
    glTranslatef(0, 0, 66)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 75, 15, 10)
    glPopMatrix()

    glPopMatrix()


def draw_grid():
    blocks = 20
    size = WINDOW_WIDTH / blocks
    diff = -WINDOW_WIDTH / 2
    for i in range(blocks):
        for j in range(blocks):
            if (i + j) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.7, 0.5, 0.95)

            x1 = diff + j * size
            x2 = x1 + size
            y1 = diff + i * size
            y2 = y1 + size

            glBegin(GL_QUADS)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
            glEnd()


def draw_boundary():
    k = WINDOW_WIDTH // 2
    wall = 99
    glBegin(GL_QUADS)

    # Left Wall
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-k, -k, 0)
    glVertex3f(-k, k, 0)
    glVertex3f(-k, k, wall)
    glVertex3f(-k, -k, wall)

    # Right Wall
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(k, k, 0)
    glVertex3f(k, -k, 0)
    glVertex3f(k, -k, wall)
    glVertex3f(k, k, wall)

    # Top Wall
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-k, k, 0)
    glVertex3f(k, k, 0)
    glVertex3f(k, k, wall)
    glVertex3f(-k, k, wall)

    # Bottom Wall
    glColor3f(0.11, 0.66, 0.77)
    glVertex3f(k, -k, 0)
    glVertex3f(-k, -k, 0)
    glVertex3f(-k, -k, wall)
    glVertex3f(k, -k, wall)

    glEnd()


def draw_bullets():
    glColor3f(1.0, 0.0, 0.0)
    for b in bullets:
        glPushMatrix()
        glTranslatef(*b["pos"])
        gluSphere(gluNewQuadric(), 11, 16, 12)
        glPopMatrix()


def shoot_bullet():
    global player_x, player_y, player_angle, bullets
    rad = math.radians(player_angle)
    dir_x = -math.sin(rad)
    dir_y = math.cos(rad)

    gun_offset = 75

    start_x = player_x + dir_x * gun_offset
    start_y = player_y + dir_y * gun_offset
    start_z = 40

    vel_x = dir_x * BULLET_SPEED
    vel_y = dir_y * BULLET_SPEED
    vel_z = 0

    bullets.append({"pos": [start_x, start_y, start_z], "vel": [vel_x, vel_y, vel_z]})


def update_bullets(delta_time):
    global bullets, bullets_missed, score, game_over

    BORDER = WINDOW_WIDTH / 2
    to_remove = []
    enemies_hit = []

    for bullet in bullets:
        vx = bullet["vel"][0]
        vy = bullet["vel"][1]

        distance_this_frame = math.hypot(vx, vy) * delta_time
        steps = max(1, int(distance_this_frame / 50) + 1)
        step_dx = vx * delta_time / steps
        step_dy = vy * delta_time / steps

        out_of_bounds = False
        hit_enemy = False

        for _ in range(steps):
            bullet["pos"][0] += step_dx
            bullet["pos"][1] += step_dy

            px = bullet["pos"][0]
            py = bullet["pos"][1]

            if abs(px) > BORDER or abs(py) > BORDER:
                out_of_bounds = True
                break

            for e in enemies:
                dx = px - e["x"]
                dy = py - e["y"]
                dist = math.hypot(dx, dy)
                if dist < e["current_radius"] + 12:
                    hit_enemy = True
                    enemies_hit.append(e)
                    score += 1
                    break

            if hit_enemy:
                break

        if out_of_bounds or hit_enemy:
            to_remove.append(bullet)
            if out_of_bounds:
                bullets_missed += 1
                print(f"Bullets Missed: {bullets_missed}")
                if bullets_missed >= MAX_MISSED_BULLETS:
                    game_over = True

    for b in to_remove:
        if b in bullets:
            bullets.remove(b)

    for e in enemies_hit:
        while True:
            new_x = random.randint(-450, 450)
            new_y = random.randint(-450, 450)
            dist = math.hypot(player_x - new_x, player_y - new_y)
            if dist > 222:
                e["x"] = new_x
                e["y"] = new_y
                e["current_radius"] = ENEMY_MIN_RADIUS
                e["flag"] = 1
                break


def draw_enemies():
    quadric = gluNewQuadric()
    for e in enemies:
        glPushMatrix()
        glTranslatef(e["x"], e["y"], e["current_radius"])

        # Pulsing
        scale = e["current_radius"] / 20.0
        glScalef(scale, scale, scale)

        # ===Body===
        glColor3f(1.0, 0.0, 0.0)
        gluSphere(quadric, 40, 20, 20)

        # ===Head===
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, 0, 40)
        gluSphere(quadric, 20, 20, 20)

        glPopMatrix()


def generate_enemies():
    global enemies
    enemies.clear()
    for _ in range(NUM_ENEMIES):
        while True:
            x = random.randint(-450, 450)
            y = random.randint(-450, 450)
            dist = math.hypot(x - player_x, y - player_y)
            if dist > 222:
                enemies.append(
                    {"x": x, "y": y, "current_radius": ENEMY_MIN_RADIUS, "flag": 1}
                )
                break


def update_enemies(delta_time):
    global lives, game_over, enemies
    if game_over:
        return

    for e in enemies:
        # Chase player
        dx = player_x - e["x"]
        dy = player_y - e["y"]
        dist = math.hypot(dx, dy)

        if dist > 5:
            e["x"] += (dx / dist) * ENEMY_SPEED * delta_time
            e["y"] += (dy / dist) * ENEMY_SPEED * delta_time

        # Pulsing animation
        e["current_radius"] += e["flag"] * ENEMY_GROWTH_SPEED * 120 * delta_time
        if e["current_radius"] >= ENEMY_MAX_RADIUS:
            e["current_radius"] = ENEMY_MAX_RADIUS
            e["flag"] = -1
        elif e["current_radius"] <= ENEMY_MIN_RADIUS:
            e["current_radius"] = ENEMY_MIN_RADIUS
            e["flag"] = 1

        player_collision_dist = 70 + e["current_radius"]
        if dist < player_collision_dist:
            lives -= 1
            print(f"Remaining Player Lives: {lives}")
            if lives <= 0:
                game_over = True
                return

            while True:
                new_x = random.randint(-450, 450)
                new_y = random.randint(-450, 450)
                new_dist = math.hypot(player_x - new_x, player_y - new_y)
                if new_dist > 222:
                    e["x"] = new_x
                    e["y"] = new_y
                    break
            e["current_radius"] = ENEMY_MIN_RADIUS
            e["flag"] = 1


def setupCamera():
    global player_x, player_y, player_angle, camera_mode, camera_radius, camera_height, camera_angle
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 2000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == "3rd":
        x = camera_radius * math.sin(math.radians(camera_angle))
        y = camera_radius * math.cos(math.radians(camera_angle))
        z = camera_height
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

    elif camera_mode == "1st":
        if auto_aim_camera and cheating:
            rad = math.radians(frozen_camera_angle)
        else:
            rad = math.radians(player_angle)

        dx = -math.sin(rad)
        dy = math.cos(rad)

        offset = 11
        cam_x = player_x + dx * offset
        cam_y = player_y + dy * offset
        cam_z = 88

        look_dist = 250
        look_x = player_x + dx * look_dist
        look_y = player_y + dy * look_dist
        look_z = 45

        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)


def showScreen():
    global lives, bullets_missed, score
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    setupCamera()
    draw_grid()
    draw_boundary()
    draw_enemies()

    if not game_over:
        draw_bullets()
        draw_player()
        draw_text(11, 750, f"Player Lives Remaining: {lives}")
        draw_text(10, 725, f"Game Score: {score}")
        draw_text(10, 700, f"Player Bullet Missed: {bullets_missed}")
    else:
        draw_player()
        draw_text(385, 750, f"---------------------------")
        draw_text(410, 725, f"    Game Over. Your Score: {score}")
        draw_text(400, 700, f" Press 'R' to RESTART the Game")
        draw_text(385, 675, f"---------------------------")

    glutSwapBuffers()


def keyboardListener(key, x, y):
    global last_time, auto_aim_camera, camera_mode, player_x, player_y, player_z, player_angle, game_over, score, bullets_missed, lives, camera_angle, cheating, moving_front, moving_back, rotating_left, rotating_right, frozen_camera_angle
    key = key.decode("utf-8").lower()
    if key == "w":
        moving_front = True
    elif key == "s":
        moving_back = True
    elif key == "a":
        rotating_left = True
    elif key == "d":
        rotating_right = True
    elif key == "c":
        cheating = not cheating
        if not cheating:
            auto_aim_camera = False
            got_enemy.clear()
    elif key == "v":
        if cheating and camera_mode == "1st":
            auto_aim_camera = not auto_aim_camera
            if auto_aim_camera:
                frozen_camera_angle = player_angle
    elif key == "r":
        if game_over:
            enemies.clear()
            generate_enemies()
            bullets.clear()
            game_over = not game_over
            lives = 5
            score = 0
            bullets_missed = 0
            player_x, player_y, player_z = 0, 0, 0
            player_angle = 0
            camera_mode = "3rd"
            cheating = False
            auto_aim_camera = False
            last_time = time.perf_counter()

    glutPostRedisplay()


def key_up(key, x, y):
    global moving_front, moving_back, rotating_left, rotating_right
    key = key.decode("utf-8").lower()
    if key == "w":
        moving_front = False
    elif key == "s":
        moving_back = False
    elif key == "a":
        rotating_left = False
    elif key == "d":
        rotating_right = False


def specialKeyListener(key, x, y):
    global camera_radius, camera_angle, camera_height

    if key == GLUT_KEY_UP:
        camera_height += 11
    if key == GLUT_KEY_DOWN:
        camera_height -= 11
    if key == GLUT_KEY_LEFT:
        camera_angle += 1.1
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 1.1


def mouseListener(button, state, x, y):
    global camera_mode, game_over

    if not game_over:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            shoot_bullet()
            print("Bullet Fired!")

        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            camera_mode = "1st" if camera_mode == "3rd" else "3rd"


def idle():
    global last_time, player_angle, cheating, got_enemy, auto_aim_camera, player_x, player_y, player_z
    current_time = time.perf_counter()
    delta_time = current_time - last_time
    last_time = current_time

    if not game_over:
        update_bullets(delta_time)
        update_enemies(delta_time)
        if cheating:
            move_speed = player_speed * delta_time
            if moving_front:
                player_y -= move_speed
            if moving_back:
                player_y += move_speed
            if rotating_left:
                player_x += move_speed
            if rotating_right:
                player_x -= move_speed
        else:
            if moving_front or moving_back:
                rad = math.radians(player_angle)
                dx = -math.sin(rad)
                dy = math.cos(rad)
                direction = 1 if moving_front else -1
                player_x += dx * direction * player_speed * delta_time
                player_y += dy * direction * player_speed * delta_time

        if cheating:
            player_angle += 777 * delta_time
            if player_angle >= 360:
                player_angle -= 360
                got_enemy.clear()

            rad = math.radians(player_angle)
            dir_x = -math.sin(rad)
            dir_y = math.cos(rad)

            for e in enemies:
                if e not in got_enemy:
                    dx = e["x"] - player_x
                    dy = e["y"] - player_y
                    dist = math.hypot(dx, dy)
                    if dist > 50:
                        proj_x = player_x + dist * dir_x
                        proj_y = player_y + dist * dir_y
                        tolerance = e["current_radius"]
                        if (
                            abs(e["x"] - proj_x) < tolerance
                            and abs(e["y"] - proj_y) < tolerance
                        ):
                            got_enemy.append(e)
                            shoot_bullet()

        else:
            if rotating_left:
                player_angle += player_rotation_speed * delta_time
            if rotating_right:
                player_angle -= player_rotation_speed * delta_time

        # Keep player inside boundaries
        player_x = max(-500, min(500, player_x))
        player_y = max(-500, min(500, player_y))

    glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"23201427_Avishek_Biswas_Bullet Frenzy")
    generate_enemies()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutKeyboardUpFunc(key_up)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()

"""
Hiccup's Adventure - Simplified 3D Game
Uses ONLY allowed OpenGL functions with reusable components
TRUE 1:1 replacement with proper 3D, camera controls, and game logic
"""
import sys
import os
import math
import time
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from primitives import *
from dialogue_system_simple import DialogueSystem
from stage_complete import StageCompleteScreen

class Game:
    def __init__(self):
        self.width = 1000
        self.height = 800
        
        # Game states
        self.STATE_MENU = 0
        self.STATE_DIALOGUE = 1
        self.STATE_PUZZLE = 2
        self.STATE_MAZE = 3
        self.STATE_COMBAT = 4
        self.STATE_STAGE_COMPLETE = 5
        self.state = self.STATE_MENU
        
        # Menu
        self.menu_selection = 0
        self.menu_options = ['START', 'EXIT']
        self.menu_rotation = 0
        
        # Camera
        self.camera_angle = 0
        self.camera_dist = 300
        
        # Mouse
        self.mouse_x = self.width // 2
        self.mouse_y = self.height // 2
        self.mouse_captured = False
        
        # Cheat mode
        self.cheat_mode = False
        
        # Stage tracking
        self.current_stage = 1
        self.stages_complete = [False, False, False]
        
        # Dialogue and stage systems
        self.dialogue_system = DialogueSystem()
        self.dialogue_system.integrated_mode = True
        self.dialogue_system.window_width = self.width
        self.dialogue_system.window_height = self.height
        
        self.stage_complete = StageCompleteScreen()
        self.stage_complete.integrated_mode = True
        self.stage_complete.window_width = self.width
        self.stage_complete.window_height = self.height
        
        # Dialogue sequences
        self.dialogues = {
            'intro': {
                'character': 'Hiccup',
                'lines': [
                    "Where am I? Everything is so dark...",
                    "I can't remember anything about myself.",
                    "I need to find my memories."
                ]
            },
            'stage1_intro': {
                'character': 'Mysterious Voice',
                'lines': [
                    "Lost one, you seek what was taken from you.",
                    "Your memories lie scattered across three realms.",
                    "Solve the puzzle to reclaim your first memory."
                ]
            },
            'stage2_intro': {
                'character': 'Mysterious Voice',
                'lines': [
                    "You have recovered a fragment of your past.",
                    "But the path ahead grows darker.",
                    "Navigate the maze to find the next memory."
                ]
            },
            'stage3_intro': {
                'character': 'Memory Guardian',
                'lines': [
                    "So, you have come at last.",
                    "I am the keeper of your deepest memories.",
                    "Prove your worth in combat!"
                ]
            },
            'ending': {
                'character': 'Hiccup',
                'lines': [
                    "The Guardian... it's fading away...",
                    "Wait! I remember now! Everything is coming back!",
                    "My name is Hiccup. I'm a Viking from Berk.",
                    "I have a dragon... Toothless! My best friend!",
                    "I was exploring ancient ruins when I fell...",
                    "But I made it through. I found myself again.",
                    "Time to go home. Toothless is waiting for me!",
                    "Thank you for helping me remember who I am."
                ]
            }
        }
        
        self.current_dialogue = None
        
        # Hopping Game - Stage 1: Jump across moving platforms
        self.hopping_player_pos = [0, 0, 50]  # x, y, z (z is height)
        self.hopping_player_vel = [0, 0, 0]
        self.hopping_player_on_ground = True
        self.hopping_player_current_platform = 0  # Which platform player is on
        self.hopping_camera_yaw = 90  # Looking toward finish
        self.hopping_camera_pitch = -10
        self.hopping_platforms = []
        self.hopping_finish_pos = [800, 0, 0]  # Finish line position
        self.hopping_game_over = False
        self.hopping_won = False
        self.init_hopping()
        
        # Maze - 3D first-person navigation
        self.maze_size = 15
        self.maze = [[1] * self.maze_size for _ in range(self.maze_size)]
        self.maze_camera_pos = [90, 90, 50]  # Start position (grid 1,1) - center of cell at 60*1.5 = 90
        self.maze_camera_yaw = 0
        self.maze_camera_pitch = 0
        self.maze_exit_pos = [13, 13]
        self.maze_complete = False
        self.init_maze()
        # Ensure starting position and surrounding area are clear
        self.maze[1][1] = 0
        self.maze[1][2] = 0
        self.maze[2][1] = 0
        
        # Combat - Real-time action combat with weapons
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_stamina = 100
        self.player_max_stamina = 100
        
        self.guardian_hp = 300  # Increased HP for boss
        self.guardian_max_hp = 300
        
        # Weapon system
        self.current_weapon = 0  # 0=sword, 1=gun
        self.weapons = [
            {'name': 'SWORD', 'damage': (20, 30), 'range': 50, 'cooldown': 0.3, 'stamina': 15},
            {'name': 'GUN', 'damage': (15, 25), 'range': 200, 'cooldown': 0.5, 'stamina': 10}
        ]
        self.weapon_cooldown = 0
        
        # Special move
        self.special_move_cooldown = 0
        self.special_move_ready = True
        self.special_move_charge = 100
        self.special_move_max_charge = 100
        self.is_using_special = False
        self.special_animation = 0
        
        # Combat state - bigger arena
        self.arena_size = 200  # Increased from 100
        self.player_pos = [-150, 0, 0]  # Start further back
        self.guardian_pos = [150, 0, 0]  # Boss at far end
        self.player_velocity = [0, 0, 0]
        self.guardian_velocity = [0, 0, 0]
        
        # Arena elements (pillars for cover)
        self.arena_pillars = [
            {'pos': [-80, -80, 0], 'size': 30},
            {'pos': [-80, 80, 0], 'size': 30},
            {'pos': [80, -80, 0], 'size': 30},
            {'pos': [80, 80, 0], 'size': 30},
            {'pos': [0, -100, 0], 'size': 25},
            {'pos': [0, 100, 0], 'size': 25},
        ]
        
        # Minions system
        self.minions = []
        self.minion_spawn_cooldown = 0
        self.minion_spawn_interval = 5.0  # Spawn minions every 5 seconds
        self.max_minions = 4  # Maximum minions at once
        
        # Combat actions
        self.is_attacking = False
        self.is_dodging = False
        self.dodge_cooldown = 0
        self.attack_animation = 0
        
        # Projectiles (for gun)
        self.projectiles = []
        self.guardian_projectiles = []
        
        # Guardian AI
        self.guardian_state = 'idle'  # idle, chase, charging, attacking, retreat
        self.guardian_attack_cooldown = 10.0  # Start with 10 second cooldown
        self.guardian_charge_time = 0  # Time spent charging attack
        self.guardian_charge_max = 3.0  # 3 seconds to charge before attack (buildup)
        self.guardian_attack_radius = 0  # Visual radius of splash attack
        self.guardian_attack_warning = False  # Show warning indicator
        self.guardian_color = [0.6, 0.2, 0.2]  # Color that changes during charge
        
        # Combat animations
        self.combat_animation = 0
        self.guardian_animation = 0
        self.combat_camera_angle = 0
        self.combat_camera_yaw = 0  # Camera yaw (left/right)
        self.combat_camera_pitch = 0  # Camera pitch (up/down)
        self.combat_first_person = False  # Toggle between first and third person
        self.hit_flash = 0
        self.screen_shake = 0
        
        # Combat log
        self.combat_log = []
    
    
    def init_hopping(self):
        """Initialize hopping game - jump across moving platforms to reach finish"""
        self.hopping_platforms = []
        
        # Starting platform (fixed)
        self.hopping_platforms.append({
            'pos': [0, 0, 0],
            'size': [80, 80, 30],
            'color': (0.2, 0.5, 0.2),
            'moving': False,
            'vel': [0, 0],
            'range': 0,
            'start_pos': [0, 0, 0]
        })
        
        # Moving platforms - move horizontally, slower speed
        platform_configs = [
            {'pos': [140, -120, 0], 'speed': 30, 'range': 140},
            {'pos': [280, 100, 0], 'speed': -35, 'range': 130},
            {'pos': [420, -80, 0], 'speed': 32, 'range': 120},
            {'pos': [560, 90, 0], 'speed': -38, 'range': 140},
            {'pos': [700, -100, 0], 'speed': 35, 'range': 130},
        ]
        
        for i, cfg in enumerate(platform_configs):
            self.hopping_platforms.append({
                'pos': cfg['pos'].copy(),
                'start_pos': cfg['pos'].copy(),
                'size': [70, 70, 25],  # Smaller = harder
                'color': (0.3 + i * 0.1, 0.3, 0.5 + i * 0.05),
                'moving': True,
                'vel': [0, cfg['speed']],
                'range': cfg['range']
            })
        
        # Finish platform (fixed)
        self.hopping_platforms.append({
            'pos': [840, 0, 0],
            'size': [100, 100, 30],
            'color': (0.2, 0.8, 0.2),
            'moving': False,
            'vel': [0, 0],
            'range': 0,
            'start_pos': [840, 0, 0]
        })
        
        # Reset player - real physics
        self.hopping_player_pos = [0, 0, 60]
        self.hopping_player_vel = [0, 0, 0]
        self.hopping_player_on_ground = True
        self.hopping_player_current_platform = 0
        self.hopping_game_over = False
        self.hopping_won = False
    
    def update_hopping(self, dt):
        """Update hopping game - slow motion jumps"""
        if self.hopping_game_over or self.hopping_won:
            return
        
        # Update moving platforms
        for plat in self.hopping_platforms:
            if plat['moving']:
                plat['pos'][1] += plat['vel'][1] * dt
                if abs(plat['pos'][1] - plat['start_pos'][1]) > plat['range']:
                    plat['vel'][1] = -plat['vel'][1]
        
        # Slow motion gravity when in air
        if self.hopping_player_on_ground:
            gravity = 200
        else:
            gravity = 80  # Slow motion gravity
        
        self.hopping_player_vel[2] -= gravity * dt
        
        # Slow motion movement in air
        if self.hopping_player_on_ground:
            speed_mult = 1.0
        else:
            speed_mult = 0.4  # Slow motion
        
        # Update position
        self.hopping_player_pos[0] += self.hopping_player_vel[0] * dt * speed_mult
        self.hopping_player_pos[1] += self.hopping_player_vel[1] * dt * speed_mult
        self.hopping_player_pos[2] += self.hopping_player_vel[2] * dt * speed_mult
        
        # Check platform collisions
        self.hopping_player_on_ground = False
        landed_platform = -1
        
        for i, plat in enumerate(self.hopping_platforms):
            px, py, pz = plat['pos']
            sx, sy, sz = plat['size']
            
            # Check if player is within platform X/Y bounds
            if (px - sx/2 < self.hopping_player_pos[0] < px + sx/2 and
                py - sy/2 < self.hopping_player_pos[1] < py + sy/2):
                
                platform_top = pz + sz
                # Check if landing on platform
                if (self.hopping_player_pos[2] <= platform_top + 30 and 
                    self.hopping_player_pos[2] > pz and
                    self.hopping_player_vel[2] <= 0):
                    
                    self.hopping_player_pos[2] = platform_top + 25
                    self.hopping_player_vel[2] = 0
                    self.hopping_player_vel[0] = 0  # Stop forward motion on land
                    self.hopping_player_vel[1] = 0  # Stop side motion on land
                    self.hopping_player_on_ground = True
                    landed_platform = i
        
        # Update current platform
        if landed_platform >= 0:
            self.hopping_player_current_platform = landed_platform
            # Move with platform
            plat = self.hopping_platforms[landed_platform]
            if plat['moving']:
                self.hopping_player_pos[1] += plat['vel'][1] * dt
        
        # Fell off!
        if self.hopping_player_pos[2] < -100:
            self.hopping_game_over = True
        
        # Win condition
        if self.hopping_player_current_platform == len(self.hopping_platforms) - 1 and self.hopping_player_on_ground:
            self.hopping_won = True
    
    def hopping_jump(self):
        """Jump - just enough to reach next platform"""
        if not self.hopping_player_on_ground or self.hopping_game_over or self.hopping_won:
            return
        
        # Jump tuned to land on next platform (140 units forward)
        self.hopping_player_vel[2] = 120  # Up - slower
        self.hopping_player_vel[0] = 200  # Forward - tuned for distance
        self.hopping_player_on_ground = False
    
    def hopping_move(self, direction):
        """Move player - A/D to adjust position"""
        if self.hopping_game_over:
            return
        
        speed = 100
        
        if direction == 'left':
            self.hopping_player_vel[1] = speed  # Positive Y = left on screen
        elif direction == 'right':
            self.hopping_player_vel[1] = -speed  # Negative Y = right on screen
        elif direction == 'up':
            if self.hopping_player_on_ground:
                self.hopping_player_vel[0] = 30
        elif direction == 'down':
            if self.hopping_player_on_ground:
                self.hopping_player_vel[0] = -30
        elif direction == 'stop':
            if self.hopping_player_on_ground:
                self.hopping_player_vel[1] = 0
    
    def init_maze(self):
        """Generate 3D maze using recursive backtracking"""
        # Initialize all walls
        for i in range(self.maze_size):
            for j in range(self.maze_size):
                self.maze[i][j] = 1
        
        # Carve paths
        def carve(x, y):
            self.maze[y][x] = 0
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.maze_size - 1 and 0 < ny < self.maze_size - 1:
                    if self.maze[ny][nx] == 1:
                        self.maze[y + dy // 2][x + dx // 2] = 0
                        carve(nx, ny)
        
        carve(1, 1)
        self.maze[1][1] = 0
        self.maze[13][13] = 0
    
    def init_gl(self):
        """Initialize OpenGL - ONLY allowed functions"""
        glClearColor(0.02, 0.02, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 200, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.4, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 1.0, 1])
    
    def setup_3d(self):
        """Setup 3D projection - ALLOWED"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width / self.height, 1, 2000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def setup_2d(self):
        """Setup 2D projection - ALLOWED"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
    
    def draw_text(self, text, x, y, color=(1, 1, 1)):
        """Draw text - ALLOWED"""
        glColor3f(*color)
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    def draw_centered_text(self, text, y, color=(1, 1, 1)):
        """Draw centered text - ALLOWED"""
        width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in text)
        self.draw_text(text, (self.width - width) / 2, y, color)
    
    def draw_menu(self):
        """Draw menu screen"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 3D background
        self.setup_3d()
        gluLookAt(
            math.cos(self.camera_angle * 0.01) * self.camera_dist, math.sin(self.camera_angle * 0.01) * self.camera_dist, 150, 0, 0, 0, 0, 0, 1
            )
        
        glColor3f(0.05, 0.05, 0.1)
        draw_ground(500)
        
        # Floating crystals
        for i in range(5):
            angle = i * 72 + self.camera_angle
            x = math.cos(math.radians(angle)) * 100
            y = math.sin(math.radians(angle)) * 100
            z = 50 + 20 * math.sin(self.camera_angle * 0.02 + i)
            
            glPushMatrix()
            glTranslatef(x, y, z)
            glRotatef(self.camera_angle * 2, 0, 0, 1)
            glColor3f(0.3 + i * 0.1, 0.2, 0.5 + i * 0.1)
            draw_crystal(15)
            glPopMatrix()
        
        # 2D UI
        self.setup_2d()
        self.draw_centered_text("HICCUP'S ADVENTURE", self.height - 100, (0.9, 0.8, 0.3))
        self.draw_centered_text("A Journey of Memory", self.height - 140, (0.6, 0.6, 0.8))
        
        for i, option in enumerate(self.menu_options):
            y = self.height // 2 - i * 50
            color = (1, 1, 1) if i == self.menu_selection else (0.5, 0.5, 0.5)
            text = f"> {option} <" if i == self.menu_selection else option
            self.draw_centered_text(text, y, color)
        
        self.draw_centered_text("UP/DOWN: Select  ENTER: Confirm  C: Cheat", 50, (0.5, 0.5, 0.5))
        
        if self.cheat_mode:
            self.draw_centered_text("[CHEAT MODE]", 80, (1, 0.3, 0.3))
    
    def draw_hopping(self):
        """Draw hopping game - jump across moving platforms"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 3D third-person view (behind and above player)
        self.setup_3d()
        
        # Camera follows player from behind
        cam_distance = 250
        cam_height = 180
        cam_x = self.hopping_player_pos[0] - cam_distance
        cam_y = self.hopping_player_pos[1]
        cam_z = self.hopping_player_pos[2] + cam_height
        
        look_x = self.hopping_player_pos[0] + 150
        look_y = self.hopping_player_pos[1]
        look_z = self.hopping_player_pos[2]
        
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)
        
        # Draw void/ground far below
        glColor3f(0.02, 0.02, 0.05)
        glPushMatrix()
        glTranslatef(500, 0, -200)
        draw_ground(1500)
        glPopMatrix()
        
        # Draw platforms
        for i, plat in enumerate(self.hopping_platforms):
            glPushMatrix()
            px, py, pz = plat['pos']
            sx, sy, sz = plat['size']
            glTranslatef(px, py, pz + sz/2)
            
            # Highlight current platform
            if i == self.hopping_player_current_platform:
                glColor3f(plat['color'][0] + 0.3, plat['color'][1] + 0.3, plat['color'][2])
            else:
                glColor3f(*plat['color'])
            
            glScalef(sx/60, sy/60, sz/60)
            draw_cube(60)
            glPopMatrix()
        
        # Draw finish line indicator
        glPushMatrix()
        glTranslatef(840, 0, 100 + 10 * math.sin(self.camera_angle * 0.05))
        glRotatef(self.camera_angle * 2, 0, 0, 1)
        glColor3f(0.3, 1.0, 0.3)
        draw_crystal(30)
        glPopMatrix()
        
        # Draw player character
        glPushMatrix()
        glTranslatef(self.hopping_player_pos[0], self.hopping_player_pos[1], self.hopping_player_pos[2])
        glRotatef(90, 0, 0, 1)
        glColor3f(0.3, 0.5, 0.8)
        draw_character(25)
        glPopMatrix()
        
        # 2D UI
        self.setup_2d()
        self.draw_centered_text("HOP TO THE FINISH!", self.height - 50, (0.9, 0.8, 0.3))
        self.draw_centered_text("WASD: Move  SPACE: Jump  R: Restart  P: Skip", 50, (0.6, 0.6, 0.7))
        
        # Progress
        self.draw_text(f"Platform: {self.hopping_player_current_platform + 1}/{len(self.hopping_platforms)}", 20, self.height - 80, (0.8, 0.8, 0.9))
        
        if self.hopping_game_over:
            self.draw_centered_text("FELL! Press R to restart", self.height // 2, (1.0, 0.3, 0.3))
        
        if self.hopping_won or self.cheat_mode:
            self.draw_centered_text("STAGE COMPLETE! Press SPACE for next stage", self.height // 2, (0.3, 1.0, 0.3))
    
    def draw_maze(self):
        """Draw 3D maze with first-person camera"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 3D first-person view
        self.setup_3d()
        
        # Calculate look direction
        look_x = self.maze_camera_pos[0] + math.cos(math.radians(self.maze_camera_yaw)) * math.cos(math.radians(self.maze_camera_pitch))
        look_y = self.maze_camera_pos[1] + math.sin(math.radians(self.maze_camera_yaw)) * math.cos(math.radians(self.maze_camera_pitch))
        look_z = self.maze_camera_pos[2] + math.sin(math.radians(self.maze_camera_pitch))
        
        gluLookAt(
            self.maze_camera_pos[0], self.maze_camera_pos[1], self.maze_camera_pos[2],
            look_x, look_y, look_z,
            0, 0, 1
        )
        
        # Draw ground
        glColor3f(0.03, 0.03, 0.06)
        draw_ground(self.maze_size * 60)
        
        # Draw maze walls
        for i in range(self.maze_size):
            for j in range(self.maze_size):
                if self.maze[i][j] == 1:
                    glPushMatrix()
                    glTranslatef(j * 60, i * 60, 40)
                    glColor3f(0.2, 0.15, 0.25)
                    draw_cube(60)
                    glPopMatrix()
        
        # Draw exit crystal
        glPushMatrix()
        glTranslatef(
            self.maze_exit_pos[1] * 60,
            self.maze_exit_pos[0] * 60,
            30 + 10 * math.sin(self.camera_angle * 0.05)
        )
        glRotatef(self.camera_angle * 2, 0, 0, 1)
        glColor3f(0.2, 0.8, 0.2)
        draw_crystal(20)
        glPopMatrix()
        
        # 2D UI
        self.setup_2d()
        self.draw_centered_text("MAZE CHALLENGE", self.height - 50, (0.9, 0.8, 0.3))
        self.draw_centered_text("WASD: Move  QE: Up/Down  Mouse: Look  P: Skip", 50, (0.6, 0.6, 0.7))
        self.draw_centered_text("Find the green crystal!", 80, (0.5, 0.9, 0.5))
        
        # Check if at exit
        grid_x = int(self.maze_camera_pos[0] // 60)
        grid_y = int(self.maze_camera_pos[1] // 60)
        if [grid_y, grid_x] == self.maze_exit_pos or self.cheat_mode:
            self.maze_complete = True
            self.draw_centered_text("MAZE COMPLETE! Press SPACE for next stage", self.height // 2, (0.3, 0.9, 0.3))
    
    def draw_combat(self):
        """Draw real-time action combat with switchable first/third person camera"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Camera setup with screen shake
        self.setup_3d()
        shake_x = random.uniform(-self.screen_shake, self.screen_shake)
        shake_y = random.uniform(-self.screen_shake, self.screen_shake)
        
        if self.combat_first_person:
            # First-person camera - at player position looking forward
            angle_rad = math.radians(self.combat_camera_yaw)
            gun_dir_x = -math.sin(angle_rad)
            gun_dir_y = -math.cos(angle_rad)
            
            cam_x = self.player_pos[0] + shake_x
            cam_y = self.player_pos[1] + shake_y
            cam_z = self.player_pos[2] + 50  # Eye height
            
            look_x = self.player_pos[0] + 100 * gun_dir_x
            look_y = self.player_pos[1] + 100 * gun_dir_y
            look_z = self.player_pos[2]
            
            gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)
        else:
            # Third-person camera - behind and above player
            cam_distance = 120
            cam_height = 60
            
            cam_x = self.player_pos[0] - math.cos(math.radians(self.combat_camera_yaw)) * cam_distance + shake_x
            cam_y = self.player_pos[1] - math.sin(math.radians(self.combat_camera_yaw)) * cam_distance + shake_y
            cam_z = self.player_pos[2] + cam_height
            
            look_x = self.player_pos[0] + math.cos(math.radians(self.combat_camera_yaw)) * 30
            look_y = self.player_pos[1] + math.sin(math.radians(self.combat_camera_yaw)) * 30
            look_z = self.player_pos[2] + 30
            
            gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)
        
        # Arena ground - bigger
        glColor3f(0.02, 0.02, 0.04)
        draw_ground(500)
        
        # Arena boundaries - bigger arena
        glColor3f(0.15, 0.1, 0.2)
        for i in range(8):
            angle = i * 45
            x = math.cos(math.radians(angle)) * self.arena_size
            y = math.sin(math.radians(angle)) * self.arena_size
            glPushMatrix()
            glTranslatef(x, y, 20)
            draw_cube(15)
            glPopMatrix()
        
        # Arena pillars (cover elements)
        glColor3f(0.2, 0.15, 0.25)
        for pillar in self.arena_pillars:
            glPushMatrix()
            glTranslatef(pillar['pos'][0], pillar['pos'][1], pillar['size'])
            draw_cube(pillar['size'])
            glPopMatrix()
        
        # Player character and weapons
        if not self.combat_first_person:
            # Draw player character in third-person
            glPushMatrix()
            glTranslatef(self.player_pos[0], self.player_pos[1], 25)
            glRotatef(self.combat_camera_yaw - 90, 0, 0, 1)  # Face the direction
            glColor3f(0.3, 0.5, 0.8)  # Blue player
            draw_character(25)
            glPopMatrix()
        
        # Draw weapon (visible in both modes, positioned differently)
        angle_rad = math.radians(self.combat_camera_yaw)
        gun_dir_x = -math.sin(angle_rad)
        gun_dir_y = -math.cos(angle_rad)
        
        if self.current_weapon == 0:  # Sword
            # Sword extends from player's hand position
            if not self.combat_first_person:
                # Third-person sword - visible extending from player
                glPushMatrix()
                glTranslatef(self.player_pos[0], self.player_pos[1], 25)  # Character center
                glRotatef(self.combat_camera_yaw - 90, 0, 0, 1)  # Face same direction as character
                
                # Sword in right hand
                glPushMatrix()
                glTranslatef(6.25, 0, 17)  # Right arm position (0.25*25 for X, 0.2*25 for Z)
                glRotatef(90, 0, 0, 1)  # Point forward
                
                # Blade
                glColor3f(0.8, 0.8, 0.9)  # Silver
                glPushMatrix()
                glScalef(0.15, 0.1, 2.5)
                draw_cube(10)
                glPopMatrix()
                
                # Handle
                glPushMatrix()
                glTranslatef(0, 0, -15)
                glColor3f(0.4, 0.3, 0.2)  # Brown
                glScalef(0.18, 0.18, 0.8)
                draw_cube(10)
                glPopMatrix()
                glPopMatrix()
                glPopMatrix()
            else:
                # First-person sword - visible in front of camera
                glPushMatrix()
                glTranslatef(25, 35, -15)
                glRotatef(45, 0, 0, 1)
                
                # Blade
                glColor3f(0.8, 0.8, 0.9)
                glPushMatrix()
                glScalef(0.15, 0.1, 2.5)
                draw_cube(10)
                glPopMatrix()
                
                # Handle
                glPushMatrix()
                glTranslatef(0, 0, -15)
                glColor3f(0.4, 0.3, 0.2)
                glScalef(0.18, 0.18, 0.8)
                draw_cube(10)
                glPopMatrix()
                glPopMatrix()
        else:  # Gun
            # Gun points in the direction the camera is looking
            angle_rad = math.radians(self.combat_camera_yaw)
            
            if not self.combat_first_person:
                # Third-person: camera looks toward cos(yaw), sin(yaw)
                aim_dir_x = math.cos(angle_rad)
                aim_dir_y = math.sin(angle_rad)
                
                # Gun starts from player center and extends forward
                gun_start_x = self.player_pos[0]
                gun_start_y = self.player_pos[1]
                gun_start_z = 35  # Hand height
                
                gun_end_x = gun_start_x + 50 * aim_dir_x
                gun_end_y = gun_start_y + 50 * aim_dir_y
                gun_end_z = gun_start_z
                
                # Draw gun line
                glDisable(GL_LIGHTING)
                glColor3f(0.5, 0.5, 0.5)
                glLineWidth(6)
                glBegin(GL_LINES)
                glVertex3f(gun_start_x, gun_start_y, gun_start_z)
                glVertex3f(gun_end_x, gun_end_y, gun_end_z)
                glEnd()
                glLineWidth(1)
                glEnable(GL_LIGHTING)
                
                # Muzzle flash when firing
                if self.is_attacking and self.attack_animation < 3:
                    glPushMatrix()
                    glTranslatef(gun_end_x, gun_end_y, gun_end_z)
                    glColor3f(1.0, 0.9, 0.3)
                    draw_crystal(5)
                    glPopMatrix()
            else:
                # First-person: gun straight in center, from bottom going forward
                aim_dir_x = -math.sin(angle_rad)
                aim_dir_y = -math.cos(angle_rad)
                
                # Gun starts at player position (bottom of view) and goes straight forward
                gun_base_x = self.player_pos[0]
                gun_base_y = self.player_pos[1]
                gun_base_z = self.player_pos[2] + 10  # Low, at player's hand level
                
                gun_tip_x = gun_base_x + 60 * aim_dir_x  # Long, extends far forward
                gun_tip_y = gun_base_y + 60 * aim_dir_y
                gun_tip_z = gun_base_z  # Same height - straight, not angled
                
                # Draw gun barrel - straight line from player forward
                glDisable(GL_LIGHTING)
                glColor3f(0.5, 0.5, 0.5)
                glLineWidth(12)
                glBegin(GL_LINES)
                glVertex3f(gun_base_x, gun_base_y, gun_base_z)
                glVertex3f(gun_tip_x, gun_tip_y, gun_tip_z)
                glEnd()
                glLineWidth(1)
                glEnable(GL_LIGHTING)
                
                # Muzzle flash when firing
                if self.is_attacking and self.attack_animation < 3:
                    glPushMatrix()
                    glTranslatef(gun_tip_x, gun_tip_y, gun_tip_z)
                    glColor3f(1.0, 0.9, 0.3)
                    draw_crystal(5)
                    glPopMatrix()
        
        # Special move animation at player position
        if self.is_using_special:
            glPushMatrix()
            glTranslatef(self.player_pos[0], self.player_pos[1], 25)
            glRotatef(self.special_animation * 30, 0, 0, 1)
            glColor3f(0.9, 0.2, 0.9)
            glScalef(2.0 + self.special_animation * 0.1, 2.0 + self.special_animation * 0.1, 1.0)
            draw_crystal(20)
            glPopMatrix()
        
        # Minions with swords
        for minion in self.minions:
            glPushMatrix()
            glTranslatef(minion['pos'][0], minion['pos'][1], 15)
            glColor3f(0.4, 0.1, 0.1)  # Dark red
            draw_character(20)  # Smaller than guardian
            
            # Minion's sword - held in hand
            glPushMatrix()
            glTranslatef(5, 0, 4)  # Right arm position (0.25*20 for X, 0.2*20 for Z)
            glRotatef(90, 0, 0, 1)  # Point forward
            glColor3f(0.7, 0.7, 0.8)  # Silver blade
            # Blade
            glPushMatrix()
            glScalef(0.1, 0.08, 1.5)
            draw_cube(8)
            glPopMatrix()
            # Handle
            glPushMatrix()
            glTranslatef(0, 0, -8)
            glColor3f(0.3, 0.2, 0.1)  # Brown handle
            glScalef(0.12, 0.12, 0.5)
            draw_cube(8)
            glPopMatrix()
            glPopMatrix()
            glPopMatrix()
        
        # Guardian
        glPushMatrix()
        glTranslatef(self.guardian_pos[0], self.guardian_pos[1], 35)
        
        # Use fixed guardian color to prevent blinking
        glColor3f(*self.guardian_color)
        
        draw_character(50)
        
        # Guardian energy core with smooth pulse
        pulse = 0.7 + 0.3 * math.sin(self.guardian_animation * 0.02)
        glPushMatrix()
        glTranslatef(0, 0, 15)
        glColor3f(0.9 * pulse, 0.2, 0.9 * pulse)
        draw_crystal(15)
        glPopMatrix()
        glPopMatrix()
        
        # Draw projectiles
        for proj in self.projectiles:
            glPushMatrix()
            glTranslatef(proj['pos'][0], proj['pos'][1], proj['pos'][2])
            if proj.get('type') == 'bullet':
                # Bullet projectiles - bright yellow with glow
                # Core bullet
                glColor3f(1.0, 1.0, 0.3)  # Bright yellow
                draw_cube(6)
                
                # Outer glow
                glPushMatrix()
                glColor3f(1.0, 0.8, 0.0)  # Orange glow
                glScalef(1.8, 1.8, 1.8)
                draw_cube(6)
                glPopMatrix()
                
                # Trail effect - draw a line behind the bullet
                glDisable(GL_LIGHTING)
                glColor3f(1.0, 0.7, 0.0)
                glBegin(GL_LINES)
                glVertex3f(0, 0, 0)
                glVertex3f(-proj['vel'][0] * 0.5, -proj['vel'][1] * 0.5, 0)
                glEnd()
                glEnable(GL_LIGHTING)
            else:
                # Default projectiles
                glColor3f(1.0, 0.9, 0.2)
                draw_cube(8)
            glPopMatrix()
        
        for proj in self.guardian_projectiles:
            glPushMatrix()
            glTranslatef(proj['pos'][0], proj['pos'][1], proj['pos'][2])
            glColor3f(0.9, 0.2, 0.9)
            draw_crystal(8)
            glPopMatrix()
        
        # Hit effects removed - no flying orange boxes
        
        # Charge warning - show expanding red circle on ground
        if self.guardian_attack_warning and self.guardian_attack_radius > 0:
            glPushMatrix()
            glTranslatef(self.guardian_pos[0], self.guardian_pos[1], 1)
            
            # Draw warning circle
            charge_percent = self.guardian_charge_time / self.guardian_charge_max
            glColor3f(1.0, 0.2 + 0.3 * math.sin(self.guardian_animation * 0.2), 0.0)
            
            glBegin(GL_LINE_LOOP)
            for i in range(32):
                angle = i * (360 / 32)
                x = math.cos(math.radians(angle)) * self.guardian_attack_radius
                y = math.sin(math.radians(angle)) * self.guardian_attack_radius
                glVertex3f(x, y, 0)
            glEnd()
            
            # Draw inner warning markers
            for i in range(8):
                angle = i * 45 + self.guardian_animation * 2
                x = math.cos(math.radians(angle)) * self.guardian_attack_radius * 0.8
                y = math.sin(math.radians(angle)) * self.guardian_attack_radius * 0.8
                glPushMatrix()
                glTranslatef(x, y, 5)
                glColor3f(1.0, 0.0, 0.0)
                draw_cube(3)
                glPopMatrix()
            
            glPopMatrix()
        
        # 2D UI
        self.setup_2d()
        
        # Title
        self.draw_centered_text("GUARDIAN BATTLE - REAL-TIME COMBAT", self.height - 30, (0.9, 0.3, 0.3))
        
        # Player HUD (left side)
        hud_x = 20
        hud_y = self.height - 80
        
        # HP Bar
        self.draw_text(f"HP: {self.player_hp}/{self.player_max_hp}", hud_x, hud_y, (0.3, 0.9, 0.3))
        bar_width = 200
        hp_fill = int(bar_width * (self.player_hp / self.player_max_hp))
        glColor3f(0.3, 0.7, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(hud_x, hud_y - 20)
        glVertex2f(hud_x + hp_fill, hud_y - 20)
        glVertex2f(hud_x + hp_fill, hud_y - 10)
        glVertex2f(hud_x, hud_y - 10)
        glEnd()
        
        # Stamina Bar
        self.draw_text(f"Stamina: {int(self.player_stamina)}/{self.player_max_stamina}", hud_x, hud_y - 40, (0.9, 0.7, 0.2))
        stam_fill = int(bar_width * (self.player_stamina / self.player_max_stamina))
        glColor3f(0.8, 0.6, 0.1)
        glBegin(GL_QUADS)
        glVertex2f(hud_x, hud_y - 60)
        glVertex2f(hud_x + stam_fill, hud_y - 60)
        glVertex2f(hud_x + stam_fill, hud_y - 50)
        glVertex2f(hud_x, hud_y - 50)
        glEnd()
        
        # Weapon indicator
        weapon = self.weapons[self.current_weapon]
        weapon_color = (0.9, 0.9, 0.3) if self.weapon_cooldown <= 0 else (0.5, 0.5, 0.5)
        self.draw_text(f"Weapon: {weapon['name']} [TAB to switch]", hud_x, hud_y - 80, weapon_color)
        
        # Special Move Bar
        special_color = (0.9, 0.3, 0.9) if self.special_move_ready else (0.4, 0.2, 0.4)
        self.draw_text(f"Special: {'READY [Q]' if self.special_move_ready else 'CHARGING...'}", hud_x, hud_y - 110, special_color)
        special_fill = int(bar_width * (self.special_move_charge / self.special_move_max_charge))
        glColor3f(0.8, 0.2, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(hud_x, hud_y - 130)
        glVertex2f(hud_x + special_fill, hud_y - 130)
        glVertex2f(hud_x + special_fill, hud_y - 120)
        glVertex2f(hud_x, hud_y - 120)
        glEnd()
        
        # Guardian HUD (right side)
        hud_x = self.width - 220
        self.draw_text(f"Guardian HP: {self.guardian_hp}/{self.guardian_max_hp}", hud_x, hud_y, (0.9, 0.3, 0.3))
        guardian_hp_fill = int(bar_width * (self.guardian_hp / self.guardian_max_hp))
        glColor3f(0.9, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(hud_x, hud_y - 20)
        glVertex2f(hud_x + guardian_hp_fill, hud_y - 20)
        glVertex2f(hud_x + guardian_hp_fill, hud_y - 10)
        glVertex2f(hud_x, hud_y - 10)
        glEnd()
        
        self.draw_text(f"State: {self.guardian_state.upper()}", hud_x, hud_y - 40, (0.7, 0.5, 0.8))
        
        # Controls
        camera_mode = "First Person" if self.combat_first_person else "Third Person"
        self.draw_centered_text(f"WASD: Move  SPACE/Click: Attack  R: Dodge  V: Toggle Camera ({camera_mode})  TAB: Switch  Q: Special  P: Skip", 60, (0.6, 0.6, 0.7))
        
        # Combat log
        log_y = 140
        for i, msg in enumerate(self.combat_log[-2:]):
            self.draw_centered_text(msg, log_y - i * 25, (0.9, 0.9, 0.3))
        
        # Victory/Defeat
        if self.guardian_hp <= 0:
            self.draw_centered_text("VICTORY! Press ENTER to continue", self.height // 2, (0.3, 0.9, 0.3))
        elif self.player_hp <= 0:
            self.draw_centered_text("DEFEAT! Press ENTER to retry", self.height // 2, (0.9, 0.3, 0.3))
    
    def display(self):
        """Main display"""
        if self.state == self.STATE_MENU:
            self.draw_menu()
        elif self.state == self.STATE_DIALOGUE:
            self.dialogue_system.draw_scene()
        elif self.state == self.STATE_PUZZLE:
            self.draw_hopping()
        elif self.state == self.STATE_MAZE:
            self.draw_maze()
        elif self.state == self.STATE_COMBAT:
            self.draw_combat()
        elif self.state == self.STATE_STAGE_COMPLETE:
            self.stage_complete.display()
        
        glutSwapBuffers()
    
    def check_puzzle_solved(self):
        """Check if player has reached the goal platform"""
        if self.cheat_mode:
            return True
        
        # Check if player is on or near the goal platform
        dist_to_goal = math.sqrt(
            (self.puzzle_camera_pos[0] - self.puzzle_goal_pos[0])**2 +
            (self.puzzle_camera_pos[1] - self.puzzle_goal_pos[1])**2 +
            (self.puzzle_camera_pos[2] - self.puzzle_goal_pos[2])**2
        )
        
        # Player needs to be close to the goal platform
        if dist_to_goal < 100:
            return True
        
        return False
    
    def start_dialogue(self, dialogue_key):
        """Start a dialogue sequence"""
        if dialogue_key in self.dialogues:
            dialogue = self.dialogues[dialogue_key]
            self.dialogue_system.character_name = dialogue['character']
            self.dialogue_system.dialogue_lines = dialogue['lines']
            self.dialogue_system.current_line = 0
            self.dialogue_system.dialogue_active = True
            self.dialogue_system.show_next_line()
            self.current_dialogue = dialogue_key
            self.state = self.STATE_DIALOGUE
    
    def start_stage(self, stage_num):
        """Start a new stage directly (no intro screen)"""
        self.current_stage = stage_num
        
        # Transition directly to gameplay
        if stage_num == 1:
            self.state = self.STATE_PUZZLE
            self.mouse_captured = True
            glutSetCursor(GLUT_CURSOR_NONE)
        elif stage_num == 2:
            self.state = self.STATE_MAZE
            self.mouse_captured = True
            glutSetCursor(GLUT_CURSOR_NONE)
        elif stage_num == 3:
            self.state = self.STATE_COMBAT
            self.player_hp = self.player_max_hp
            self.guardian_hp = self.guardian_max_hp
            self.mouse_captured = True  # Enable mouse for combat
            glutSetCursor(GLUT_CURSOR_NONE)  # Hide cursor for mouse look
    
    def complete_stage(self, stage_num):
        """Complete a stage and show completion screen"""
        self.stages_complete[stage_num - 1] = True
        self.stage_complete.start_completion(stage_num, auto_advance=False)
        self.state = self.STATE_STAGE_COMPLETE
        # Reset screen shake when stage completes
        self.screen_shake = 0
        self.hit_flash = 0
    
    def check_block_collision(self, new_pos, exclude_index=None):
        """Check if a position collides with any block"""
        collision_radius = 50  # Half the block size
        for i, block in enumerate(self.puzzle_blocks):
            if i == exclude_index:
                continue
            dist = math.sqrt(
                (new_pos[0] - block['pos'][0])**2 +
                (new_pos[1] - block['pos'][1])**2
            )
            if dist < collision_radius * 2:
                return True
        return False
    
    def move_selected_block(self, direction):
        """Move selected puzzle block with collision detection"""
        if self.puzzle_selected is None:
            return
        
        block = self.puzzle_blocks[self.puzzle_selected]
        
        # Can't move fixed blocks
        if not block['movable']:
            print("Can't move this block - it's fixed!")
            return
        
        move_dist = 60
        
        # Calculate new position
        new_pos = block['pos'].copy()
        if direction == 'i':  # Forward (Y+)
            new_pos[1] += move_dist
        elif direction == 'k':  # Backward (Y-)
            new_pos[1] -= move_dist
        elif direction == 'j':  # Left (X-)
            new_pos[0] -= move_dist
        elif direction == 'l':  # Right (X+)
            new_pos[0] += move_dist
        elif direction == 'u':  # Up (Z+) - stack blocks
            new_pos[2] += move_dist
        elif direction == 'o':  # Down (Z-)
            new_pos[2] = max(0, new_pos[2] - move_dist)  # Don't go below ground
        
        # Check collision with other blocks (only for horizontal movement)
        if direction in ['i', 'k', 'j', 'l']:
            if not self.check_block_collision(new_pos, self.puzzle_selected):
                block['pos'] = new_pos
                self.puzzle_moves += 1
            else:
                print("Can't move block - collision detected!")
        else:
            # Vertical movement always allowed
            block['pos'] = new_pos
            self.puzzle_moves += 1
        
        self.puzzle_solved = self.check_puzzle_solved()
    
    def check_puzzle_camera_collision(self, new_x, new_y, new_z):
        """Check if camera position collides with puzzle blocks"""
        camera_radius = 20  # Camera collision radius
        
        for block in self.puzzle_blocks:
            block_half_size = block.get('size', 60) / 2
            
            # Calculate 3D distance from camera to block center
            dist_xy = math.sqrt(
                (new_x - block['pos'][0])**2 +
                (new_y - block['pos'][1])**2
            )
            
            # Check if camera is at the same height as the block
            block_bottom = block['pos'][2]
            block_top = block['pos'][2] + block.get('size', 60)
            
            # Only check collision if camera is at block height
            if block_bottom - 20 <= new_z <= block_top + 20:
                # Collision if distance is less than sum of radii
                if dist_xy < (camera_radius + block_half_size):
                    return True
        return False
    
    def move_puzzle_camera(self, direction):
        """Move puzzle camera with collision detection"""
        speed = 20
        forward_x = math.cos(math.radians(self.puzzle_camera_yaw))
        forward_y = math.sin(math.radians(self.puzzle_camera_yaw))
        right_x = math.cos(math.radians(self.puzzle_camera_yaw + 90))
        right_y = math.sin(math.radians(self.puzzle_camera_yaw + 90))
        
        new_x, new_y, new_z = self.puzzle_camera_pos[0], self.puzzle_camera_pos[1], self.puzzle_camera_pos[2]
        
        if direction == 'w':
            new_x += forward_x * speed
            new_y += forward_y * speed
        elif direction == 's':
            new_x -= forward_x * speed
            new_y -= forward_y * speed
        elif direction == 'a':
            new_x -= right_x * speed
            new_y -= right_y * speed
        elif direction == 'd':
            new_x += right_x * speed
            new_y += right_y * speed
        elif direction == 'q':
            new_z += speed
            self.puzzle_camera_pos[2] = new_z
            return
        elif direction == 'e':
            new_z = max(10, new_z - speed)
            self.puzzle_camera_pos[2] = new_z
            return
        
        # Check collision with blocks
        if not self.check_puzzle_camera_collision(new_x, new_y, new_z):
            self.puzzle_camera_pos[0] = new_x
            self.puzzle_camera_pos[1] = new_y
    
    def check_maze_collision(self, x, y):
        """Check if position would collide with a wall block"""
        # Blocks are 60x60 units, centered at grid_x*60, grid_y*60
        # Each block extends from center-30 to center+30 in both X and Y
        
        collision_margin = 35  # Player needs to stay 35 units away from block center
        
        for i in range(self.maze_size):
            for j in range(self.maze_size):
                if self.maze[i][j] == 1:  # This is a wall
                    # Block center is at (j*60, i*60)
                    block_x = j * 60
                    block_y = i * 60
                    
                    # Check if player is too close to this block
                    dist_x = abs(x - block_x)
                    dist_y = abs(y - block_y)
                    
                    # If within collision margin in both axes, it's a collision
                    if dist_x < collision_margin and dist_y < collision_margin:
                        return True
        
        return False
    
    def move_maze_camera(self, direction):
        """Move maze camera with collision detection"""
        speed = 20
        forward_x = math.cos(math.radians(self.maze_camera_yaw))
        forward_y = math.sin(math.radians(self.maze_camera_yaw))
        right_x = math.cos(math.radians(self.maze_camera_yaw + 90))
        right_y = math.sin(math.radians(self.maze_camera_yaw + 90))
        
        new_x, new_y = self.maze_camera_pos[0], self.maze_camera_pos[1]
        
        if direction == 'w':
            new_x += forward_x * speed
            new_y += forward_y * speed
        elif direction == 's':
            new_x -= forward_x * speed
            new_y -= forward_y * speed
        elif direction == 'a':
            new_x -= right_x * speed
            new_y -= right_y * speed
        elif direction == 'd':
            new_x += right_x * speed
            new_y += right_y * speed
        elif direction == 'q':
            self.maze_camera_pos[2] += speed
            return
        elif direction == 'e':
            self.maze_camera_pos[2] = max(10, self.maze_camera_pos[2] - speed)
            return
        
        # Check collision with walls
        if not self.check_maze_collision(new_x, new_y):
            self.maze_camera_pos[0] = new_x
            self.maze_camera_pos[1] = new_y
    
    def player_attack(self):
        """Player attacks with current weapon"""
        if self.weapon_cooldown > 0 or self.is_dodging:
            return
        
        weapon = self.weapons[self.current_weapon]
        
        # Check stamina
        if self.player_stamina < weapon['stamina']:
            self.combat_log.append("Not enough stamina!")
            return
        
        # Consume stamina
        self.player_stamina -= weapon['stamina']
        self.weapon_cooldown = weapon['cooldown']
        self.is_attacking = True
        self.attack_animation = 0
        
        # Calculate distance to guardian
        dist = math.sqrt(
            (self.player_pos[0] - self.guardian_pos[0])**2 +
            (self.player_pos[1] - self.guardian_pos[1])**2
        )
        
        if weapon['name'] == 'SWORD':
            # Melee attack - check all targets in range
            hit_something = False
            
            # Check minions first (they're closer and more important to hit)
            for minion in self.minions[:]:
                minion_dist = math.sqrt(
                    (self.player_pos[0] - minion['pos'][0])**2 +
                    (self.player_pos[1] - minion['pos'][1])**2
                )
                if minion_dist < weapon['range']:
                    damage = random.randint(*weapon['damage'])
                    minion['hp'] -= damage
                    self.hit_flash = 5
                    self.screen_shake = 3
                    self.combat_log.append(f"Sword hit minion! {damage} damage!")
                    hit_something = True
                    # Don't break - can hit multiple minions with one swing
            
            # Also check guardian
            if dist < weapon['range']:
                damage = random.randint(*weapon['damage'])
                self.guardian_hp -= damage
                self.hit_flash = 10
                self.screen_shake = 5
                self.combat_log.append(f"Sword hit Guardian! {damage} damage!")
                hit_something = True
            
            if not hit_something:
                self.combat_log.append("Sword missed!")
        
        elif weapon['name'] == 'GUN':
            # Ranged attack - shoot in the direction the camera is looking
            angle_rad = math.radians(self.combat_camera_yaw)
            
            if not self.combat_first_person:
                # Third-person: camera looks toward cos(yaw), sin(yaw)
                direction_x = math.cos(angle_rad)
                direction_y = math.sin(angle_rad)
            else:
                # First-person: camera looks toward -sin(yaw), -cos(yaw)
                direction_x = -math.sin(angle_rad)
                direction_y = -math.cos(angle_rad)
            
            # Spawn bullet from player position
            spawn_x = self.player_pos[0]
            spawn_y = self.player_pos[1]
            spawn_z = 30  # Gun height
            
            self.projectiles.append({
                'pos': [spawn_x, spawn_y, spawn_z],
                'vel': [direction_x * 25, direction_y * 25, 0],  # Faster bullets
                'damage': random.randint(*weapon['damage']),
                'type': 'bullet'
            })
            
            self.screen_shake = 2
            self.combat_log.append("Gun fired!")
    
    def player_dodge(self):
        """Player dodges"""
        if self.dodge_cooldown > 0 or self.is_dodging:
            return
        
        if self.player_stamina < 20:
            self.combat_log.append("Not enough stamina to dodge!")
            return
        
        self.player_stamina -= 20
        self.is_dodging = True
        self.dodge_cooldown = 1.0
        self.attack_animation = 0
        self.combat_log.append("Dodged!")
    
    def move_player(self, direction):
        """Move player in combat arena relative to camera direction (FPS style)"""
        speed = 2.0
        
        # Convert yaw to radians for trigonometric functions
        # In First Person, the 'forward' vector is calculated from the yaw
        yaw_rad = math.radians(self.combat_camera_yaw)
        
        # Calculate Forward vector
        # FPS Standard: 0 degrees yaw often looks down the -Y or -Z axis
        # Based on your gluLookAt logic:
        if self.combat_first_person:
            # Forward vector is where we are looking
            forward_x = -math.sin(yaw_rad)
            forward_y = -math.cos(yaw_rad)
            # Strafe vector is perpendicular (rotate 90 degrees)
            right_x = math.cos(yaw_rad)
            right_y = -math.sin(yaw_rad)
        else:
            # Third person logic (matches your original orbital style)
            forward_x = math.cos(yaw_rad)
            forward_y = math.sin(yaw_rad)
            right_x = math.cos(yaw_rad + math.pi / 2)
            right_y = math.sin(yaw_rad + math.pi / 2)

        # Apply movement to velocity
        if direction == 'w':  # Move forward
            self.player_velocity[0] = forward_x * speed
            self.player_velocity[1] = forward_y * speed
        elif direction == 's':  # Move backward
            self.player_velocity[0] = -forward_x * speed
            self.player_velocity[1] = -forward_y * speed
        elif direction == 'a':  # Strafe Left
            self.player_velocity[0] = -right_x * speed
            self.player_velocity[1] = -right_y * speed
        elif direction == 'd':  # Strafe Right
            self.player_velocity[0] = right_x * speed
            self.player_velocity[1] = right_y * speed
    
    def player_special_move(self):
        """Player uses special move - devastating area attack"""
        if not self.special_move_ready or self.special_move_charge < self.special_move_max_charge:
            self.combat_log.append("Special move not ready!")
            return
        
        # Use special move
        self.special_move_charge = 0
        self.special_move_ready = False
        self.is_using_special = True
        self.special_animation = 0
        self.screen_shake = 15
        
        # Calculate distance to guardian
        dist = math.sqrt(
            (self.player_pos[0] - self.guardian_pos[0])**2 +
            (self.player_pos[1] - self.guardian_pos[1])**2
        )
        
        # Area of effect attack - hits if guardian is within range
        if dist < 150:
            damage = random.randint(40, 60)
            self.guardian_hp -= damage
            self.hit_flash = 20
            self.combat_log.append(f"SPECIAL MOVE! Devastating blow! {damage} damage!")
            # Visual projectiles removed per user request
        else:
            self.combat_log.append("Special move missed - too far!")
        
        self.combat_log.append("Special move used! Recharging...")
    
    def update_combat(self, dt):
        """Update real-time combat state"""
        if self.guardian_hp <= 0 or self.player_hp <= 0:
            return
        
        # Update cooldowns
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= dt
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= dt
        if self.special_move_cooldown > 0:
            self.special_move_cooldown -= dt
        
        # Charge special move
        if self.special_move_charge < self.special_move_max_charge:
            self.special_move_charge += 0.5  # Charge rate
            if self.special_move_charge >= self.special_move_max_charge:
                self.special_move_charge = self.special_move_max_charge
                self.special_move_ready = True
        
        # Update special animation
        if self.is_using_special:
            self.special_animation += 1
            if self.special_animation > 30:
                self.is_using_special = False
        
        # Update attack animation
        if self.is_attacking:
            self.attack_animation += 1
            if self.attack_animation > 15:
                self.is_attacking = False
        
        # Update dodge animation
        if self.is_dodging:
            self.attack_animation += 1
            if self.attack_animation > 20:
                self.is_dodging = False
        
        # Update player position (slower movement)
        self.player_pos[0] += self.player_velocity[0]
        self.player_pos[1] += self.player_velocity[1]
        
        # Keep player in arena - bigger arena
        self.player_pos[0] = max(-self.arena_size, min(self.arena_size, self.player_pos[0]))
        self.player_pos[1] = max(-self.arena_size, min(self.arena_size, self.player_pos[1]))
        
        # Apply friction
        self.player_velocity[0] *= 0.8
        self.player_velocity[1] *= 0.8
        
        # Regenerate stamina
        self.player_stamina = min(self.player_max_stamina, self.player_stamina + 0.3)
        
        # Minion spawning
        self.minion_spawn_cooldown -= dt
        if self.minion_spawn_cooldown <= 0 and len(self.minions) < self.max_minions:
            self.spawn_minion()
            self.minion_spawn_cooldown = self.minion_spawn_interval
        
        # Update minions
        self.update_minions(dt)
        
        # Update projectiles
        for proj in self.projectiles[:]:
            proj['pos'][0] += proj['vel'][0]
            proj['pos'][1] += proj['vel'][1]
            
            # Check collision with guardian
            dist = math.sqrt(
                (proj['pos'][0] - self.guardian_pos[0])**2 +
                (proj['pos'][1] - self.guardian_pos[1])**2
            )
            if dist < 30:
                self.guardian_hp -= proj['damage']
                self.hit_flash = 10
                self.screen_shake = 5
                self.combat_log.append(f"Gun hit Guardian! {proj['damage']} damage!")
                self.projectiles.remove(proj)
                continue
            
            # Check collision with minions
            for minion in self.minions[:]:
                minion_dist = math.sqrt(
                    (proj['pos'][0] - minion['pos'][0])**2 +
                    (proj['pos'][1] - minion['pos'][1])**2
                )
                if minion_dist < 25:  # Larger hit radius
                    minion['hp'] -= proj['damage']
                    self.combat_log.append(f"Gun hit minion! {proj['damage']} damage!")
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    break
            
            # Remove if out of bounds
            if abs(proj['pos'][0]) > 300 or abs(proj['pos'][1]) > 300:
                if proj in self.projectiles:
                    self.projectiles.remove(proj)
        
        # Update guardian projectiles
        for proj in self.guardian_projectiles[:]:
            proj['pos'][0] += proj['vel'][0]
            proj['pos'][1] += proj['vel'][1]
            
            # Update lifetime if it exists
            if 'lifetime' in proj:
                proj['lifetime'] -= dt
                if proj['lifetime'] <= 0:
                    self.guardian_projectiles.remove(proj)
                    continue
            
            # Check collision with player (if not dodging and projectile has damage)
            if proj.get('damage', 0) > 0 and not self.is_dodging:
                dist = math.sqrt(
                    (proj['pos'][0] - self.player_pos[0])**2 +
                    (proj['pos'][1] - self.player_pos[1])**2
                )
                if dist < 25:
                    self.player_hp -= proj['damage']
                    self.player_hp = max(1, self.player_hp)  # Testing: prevent death
                    self.hit_flash = 10
                    self.combat_log.append(f"Guardian hit you! {proj['damage']} damage!")
                    self.guardian_projectiles.remove(proj)
                    continue
            
            # Remove if out of bounds
            if abs(proj['pos'][0]) > 200 or abs(proj['pos'][1]) > 200:
                self.guardian_projectiles.remove(proj)
        
        # Guardian AI
        self.update_guardian_ai(dt)
        
        # Cheat mode
        if self.cheat_mode:
            self.player_hp = self.player_max_hp
            self.guardian_hp = 0
    
    def spawn_minion(self):
        """Spawn a fast minion with sword near the guardian"""
        # Spawn minion near guardian
        angle = random.uniform(0, 360)
        distance = random.uniform(40, 60)
        spawn_x = self.guardian_pos[0] + math.cos(math.radians(angle)) * distance
        spawn_y = self.guardian_pos[1] + math.sin(math.radians(angle)) * distance
        
        self.minions.append({
            'pos': [spawn_x, spawn_y],
            'hp': 30,
            'max_hp': 30,
            'speed': 3.0,  # Increased from 1.5 - much faster!
            'damage': 10,
            'attack_cooldown': 0
        })
        self.combat_log.append("Guardian spawned a minion!")
    
    def update_minions(self, dt):
        """Update all minions - chase player and attack"""
        for minion in self.minions[:]:
            # Calculate distance to player
            dist = math.sqrt(
                (self.player_pos[0] - minion['pos'][0])**2 +
                (self.player_pos[1] - minion['pos'][1])**2
            )
            
            # Chase player
            if dist > 30:  # If not in melee range
                direction_x = (self.player_pos[0] - minion['pos'][0]) / dist
                direction_y = (self.player_pos[1] - minion['pos'][1]) / dist
                minion['pos'][0] += direction_x * minion['speed']
                minion['pos'][1] += direction_y * minion['speed']
            else:
                # In melee range - attack
                minion['attack_cooldown'] -= dt
                if minion['attack_cooldown'] <= 0 and not self.is_dodging:
                    self.player_hp -= minion['damage']
                    self.player_hp = max(1, self.player_hp)  # Testing: prevent death
                    self.hit_flash = 5
                    self.combat_log.append(f"Minion hit you! {minion['damage']} damage!")
                    minion['attack_cooldown'] = 1.5  # Attack every 1.5 seconds
            
            # Check if minion is dead
            if minion['hp'] <= 0:
                self.minions.remove(minion)
                self.combat_log.append("Minion defeated!")
    
    def update_guardian_ai(self, dt):
        """Update guardian AI behavior with charge-up attacks"""
        if self.guardian_hp <= 0:
            self.guardian_state = 'defeated'
            return
        
        # Calculate distance to player
        dist = math.sqrt(
            (self.player_pos[0] - self.guardian_pos[0])**2 +
            (self.player_pos[1] - self.guardian_pos[1])**2
        )
        
        # Update attack cooldown
        if self.guardian_attack_cooldown > 0:
            self.guardian_attack_cooldown -= dt
        
        # STATE MACHINE
        if self.guardian_state == 'charging':
            # Charging up for splash attack
            self.guardian_charge_time += dt
            
            # Visual feedback - color gets brighter and redder as charge increases
            charge_percent = min(1.0, self.guardian_charge_time / self.guardian_charge_max)
            self.guardian_color = [
                0.6 + 0.4 * charge_percent,  # Red increases
                0.2 - 0.1 * charge_percent,  # Green decreases
                0.2 - 0.1 * charge_percent   # Blue decreases
            ]
            
            # Expand warning radius
            self.guardian_attack_radius = 80 * charge_percent
            self.guardian_attack_warning = True
            
            # When fully charged, unleash attack
            if self.guardian_charge_time >= self.guardian_charge_max:
                self.execute_splash_attack()
                self.guardian_state = 'idle'
                self.guardian_charge_time = 0
                self.guardian_attack_cooldown = 10.0  # 10 second cooldown before next attack
                self.guardian_attack_warning = False
                self.guardian_attack_radius = 0
                self.guardian_color = [0.6, 0.2, 0.2]  # Reset color
            
            return
        
        # Determine next state based on HP, distance, and cooldown
        hp_percent = self.guardian_hp / self.guardian_max_hp
        
        if self.guardian_attack_cooldown <= 0:
            # Ready to attack - start charging
            if dist < 150:  # Within attack range
                self.guardian_state = 'charging'
                self.guardian_charge_time = 0
                self.combat_log.append("Guardian is charging an attack!")
                return
        
        # Movement states when not attacking
        if dist > 120:
            self.guardian_state = 'chase'
        elif dist < 60:
            self.guardian_state = 'retreat'
        else:
            self.guardian_state = 'idle'
        
        # Execute movement - Guardian is slow and menacing
        if self.guardian_state == 'chase':
            # Move towards player slowly
            direction = [
                (self.player_pos[0] - self.guardian_pos[0]) / dist,
                (self.player_pos[1] - self.guardian_pos[1]) / dist
            ]
            self.guardian_pos[0] += direction[0] * 0.8  # Decreased from 1.5 - slower
            self.guardian_pos[1] += direction[1] * 0.8
        
        elif self.guardian_state == 'retreat':
            # Move away from player slowly
            direction = [
                (self.player_pos[0] - self.guardian_pos[0]) / dist,
                (self.player_pos[1] - self.guardian_pos[1]) / dist
            ]
            self.guardian_pos[0] -= direction[0] * 1.0  # Decreased from 2 - slower
            self.guardian_pos[1] -= direction[1] * 1.0
        
        # Keep guardian in arena
        self.guardian_pos[0] = max(-self.arena_size, min(self.arena_size, self.guardian_pos[0]))
        self.guardian_pos[1] = max(-self.arena_size, min(self.arena_size, self.guardian_pos[1]))
    
    def execute_splash_attack(self):
        """Execute the guardian's splash attack"""
        # Calculate distance to player
        dist = math.sqrt(
            (self.player_pos[0] - self.guardian_pos[0])**2 +
            (self.player_pos[1] - self.guardian_pos[1])**2
        )
        
        # Check if player is in splash radius and not dodging
        if dist < 80 and not self.is_dodging:
            damage = random.randint(25, 40)
            self.player_hp -= damage
            self.player_hp = max(1, self.player_hp)  # Testing: prevent death
            self.hit_flash = 15
            self.screen_shake = 10
            self.combat_log.append(f"SPLASH ATTACK! {damage} damage!")
        elif dist < 80 and self.is_dodging:
            self.combat_log.append("Dodged the splash attack!")
        else:
            self.combat_log.append("Guardian's attack missed!")
        
        # Visual effect removed per user request (no flying boxes)
    
    def guardian_special_attack(self):
        """Guardian uses special attack - spiral projectile barrage"""
        self.combat_log.append("GUARDIAN SPECIAL ATTACK!")
        self.screen_shake = 10
        self.guardian_color = (0.9, 0.1, 0.9)  # Change color briefly
        
        # Fire projectiles in a spiral pattern
        for i in range(12):
            angle = i * 30
            direction = [
                math.cos(math.radians(angle)),
                math.sin(math.radians(angle))
            ]
            self.guardian_projectiles.append({
                'pos': [self.guardian_pos[0], self.guardian_pos[1], 35],
                'vel': [direction[0] * 10, direction[1] * 10, 0],
                'damage': random.randint(15, 25)
            })
        
        # Reset color after a moment
        def reset_color():
            self.guardian_color = (0.6, 0.2, 0.2)
        
        # Color will reset in update loop
        
        # Keep guardian in arena
        arena_size = 100
        self.guardian_pos[0] = max(-arena_size, min(arena_size, self.guardian_pos[0]))
        self.guardian_pos[1] = max(-arena_size, min(arena_size, self.guardian_pos[1]))
    
    def keyboard(self, key, x, y):
        """Handle keyboard"""
        if key == b'\x1b':  # ESC
            if self.state != self.STATE_MENU:
                self.state = self.STATE_MENU
                self.mouse_captured = False
                glutSetCursor(GLUT_CURSOR_INHERIT)
            else:
                glutLeaveMainLoop()
        
        elif key == b'c' or key == b'C':
            self.cheat_mode = not self.cheat_mode
            print(f"Cheat mode: {'ON' if self.cheat_mode else 'OFF'}")
        
        elif self.state == self.STATE_MENU:
            if key == b'\r' or key == b' ':
                if self.menu_selection == 0:
                    # Start game with intro dialogue
                    self.start_dialogue('intro')
                else:
                    glutLeaveMainLoop()
        
        elif self.state == self.STATE_DIALOGUE:
            if key == b' ':
                finished = self.dialogue_system.advance_dialogue()
                if finished:
                    # Dialogue finished, transition to next state
                    if self.current_dialogue == 'intro':
                        self.start_dialogue('stage1_intro')
                    elif self.current_dialogue == 'stage1_intro':
                        self.start_stage(1)
                    elif self.current_dialogue == 'stage2_intro':
                        self.start_stage(2)
                    elif self.current_dialogue == 'stage3_intro':
                        self.start_stage(3)
                    elif self.current_dialogue == 'ending':
                        # Game complete, return to menu
                        self.state = self.STATE_MENU
                        self.mouse_captured = False
                        glutSetCursor(GLUT_CURSOR_INHERIT)
        
        elif self.state == self.STATE_STAGE_COMPLETE:
            # Any key advances from completion screen
            self.stage_complete.end_completion()
            if self.current_stage == 1:
                self.start_dialogue('stage2_intro')
            elif self.current_stage == 2:
                self.start_dialogue('stage3_intro')
            elif self.current_stage == 3:
                # After stage 3 complete, show ending dialogue
                self.start_dialogue('ending')
        
        elif self.state == self.STATE_PUZZLE:
            # Hopping game controls - WASD to move, SPACE to jump
            if key == b' ':
                if self.hopping_won:
                    self.complete_stage(1)
                    self.mouse_captured = False
                    glutSetCursor(GLUT_CURSOR_INHERIT)
                else:
                    self.hopping_jump()
            elif key == b'w' or key == b'W':
                self.hopping_move('up')
            elif key == b's' or key == b'S':
                self.hopping_move('down')
            elif key == b'a' or key == b'A':
                self.hopping_move('left')
            elif key == b'd' or key == b'D':
                self.hopping_move('right')
            elif key == b'r' or key == b'R':
                self.init_hopping()  # Restart anytime
            elif key == b'p' or key == b'P':
                self.hopping_won = True
        
        elif self.state == self.STATE_MAZE:
            if key in b'wasdqeWASDQE':
                self.move_maze_camera(chr(key[0]).lower())
            elif key == b'p' or key == b'P':
                self.complete_stage(2)
                self.mouse_captured = False
                glutSetCursor(GLUT_CURSOR_INHERIT)
            elif key == b' ' and (self.maze_complete or self.cheat_mode):
                self.complete_stage(2)
                self.mouse_captured = False
                glutSetCursor(GLUT_CURSOR_INHERIT)
        
        elif self.state == self.STATE_COMBAT:
            if key == b' ':
                if self.guardian_hp <= 0:
                    print("Victory! Stage 3 complete!")
                    self.complete_stage(3)
                    self.mouse_captured = False
                    glutSetCursor(GLUT_CURSOR_INHERIT)
                elif self.player_hp <= 0:
                    print("Retrying combat...")
                    self.player_hp = self.player_max_hp
                    self.player_stamina = self.player_max_stamina
                    self.guardian_hp = self.guardian_max_hp
                    self.player_pos = [-80, 0, 0]
                    self.guardian_pos = [80, 0, 0]
                    self.projectiles = []
                    self.guardian_projectiles = []
                    self.combat_log = []
                else:
                    self.player_attack()
            elif key in b'wasdWASD':
                self.move_player(chr(key[0]).lower())
            elif key in b'vV':  # Toggle first/third person
                self.combat_first_person = not self.combat_first_person
                mode = "First Person" if self.combat_first_person else "Third Person"
                self.combat_log.append(f"Camera: {mode}")
                print(f"Camera Mode: {mode}")
            elif key in b'qQ':  # Special move
                self.player_special_move()
            elif key in b'rR':  # Dodge
                self.player_dodge()
            elif key in b'pP':  # Skip combat
                print("Skipping combat...")
                self.guardian_hp = 0
                self.combat_log.append("Combat skipped!")
            elif key == b'\t':  # TAB key
                self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
                self.combat_log.append(f"Switched to {self.weapons[self.current_weapon]['name']}")
            elif key == b'\r':  # ENTER key
                if self.guardian_hp <= 0 or self.player_hp <= 0:
                    if self.guardian_hp <= 0:
                        print("Victory! Stage 3 complete!")
                        self.complete_stage(3)
                        self.mouse_captured = False
                        glutSetCursor(GLUT_CURSOR_INHERIT)
                    else:
                        print("Retrying combat...")
                        self.player_hp = self.player_max_hp
                        self.player_stamina = self.player_max_stamina
                        self.guardian_hp = self.guardian_max_hp
                        self.player_pos = [-80, 0, 0]
                        self.guardian_pos = [80, 0, 0]
                        self.projectiles = []
                        self.guardian_projectiles = []
                        self.combat_log = []
                        self.special_move_charge = self.special_move_max_charge
                        self.special_move_ready = True
        
        glutPostRedisplay()
    
    def special_keyboard(self, key, x, y):
        """Handle special keys"""
        if self.state == self.STATE_MENU:
            if key == GLUT_KEY_UP:
                self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
            elif key == GLUT_KEY_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
        
        elif self.state == self.STATE_COMBAT:
            # SHIFT key for dodge (special key code varies, so we handle it in keyboard)
            pass
        
        glutPostRedisplay()
    
    def keyboard_up(self, key, x, y):
        """Handle key release for combat and hopping movement"""
        if self.state == self.STATE_COMBAT:
            if key in b'wasdWASD':
                # Stop movement when key is released
                direction = chr(key[0]).lower()
                if direction == 'w' or direction == 's':
                    self.player_velocity[1] = 0
                elif direction == 'a' or direction == 'd':
                    self.player_velocity[0] = 0
        elif self.state == self.STATE_PUZZLE:
            # Stop hopping movement when key released
            if key in b'wasdWASD':
                self.hopping_move('stop')
    
    def mouse(self, button, state, x, y):
        """Handle mouse clicks"""
        if self.state == self.STATE_PUZZLE and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # In hopping game, click does nothing special (use keyboard)
            pass
        
        elif self.state == self.STATE_COMBAT and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # Mouse click to attack in combat
            if self.current_weapon == 1:  # Gun - shoot toward mouse position
                self.player_attack()
            else:  # Sword - regular attack
                self.player_attack()
    
    def passive_motion(self, x, y):
        """Handle mouse movement for camera"""
        if not self.mouse_captured:
            return
        
        # Calculate mouse delta
        dx = x - self.mouse_x
        dy = y - self.mouse_y
        
        sensitivity = 0.2
        
        if self.state == self.STATE_PUZZLE:
            # Hopping game uses fixed camera, no mouse control needed
            pass
        
        elif self.state == self.STATE_MAZE:
            self.maze_camera_yaw -= dx * sensitivity
            self.maze_camera_pitch -= dy * sensitivity
            self.maze_camera_pitch = max(-89, min(89, self.maze_camera_pitch))
        
        elif self.state == self.STATE_COMBAT:
            # Camera rotation - works for both first and third person
            if self.combat_first_person == False:
                self.combat_camera_yaw -= dx * sensitivity
            else:
                self.combat_camera_yaw += dx * sensitivity
            # No pitch control (camera stays horizontal)
            
        
        # Reset mouse to center
        self.mouse_x = self.width // 2
        self.mouse_y = self.height // 2
        glutWarpPointer(self.mouse_x, self.mouse_y)
    
    def update(self):
        """Update animation"""
        self.camera_angle += 0.5
        self.menu_rotation += 0.5
        self.combat_animation += 1
        self.guardian_animation += 1
        self.combat_camera_angle += 0.3
        
        # Update hit flash (always)
        if self.hit_flash > 0:
            self.hit_flash -= 1
        
        # Update screen shake (always, not just in combat)
        if self.screen_shake > 0:
            self.screen_shake -= 0.5
        
        # Update hopping game
        if self.state == self.STATE_PUZZLE:
            self.update_hopping(0.016)  # ~60 FPS
        
        # Update combat (real-time)
        if self.state == self.STATE_COMBAT:
            self.update_combat(0.016)  # ~60 FPS
        
        # Update dialogue system
        if self.state == self.STATE_DIALOGUE:
            self.dialogue_system.update_text_animation()
        
        # Update stage complete
        if self.state == self.STATE_STAGE_COMPLETE:
            self.stage_complete.update()
        
        glutPostRedisplay()
    
    def run(self):
        """Run game"""
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(100, 100)
        glutCreateWindow(b"Hiccup's Adventure - 3D Game")
        
        self.init_gl()
        
        glutDisplayFunc(self.display)
        glutKeyboardFunc(self.keyboard)
        try:
            glutKeyboardUpFunc(self.keyboard_up)
        except:
            pass  # KeyboardUpFunc not available in all GLUT implementations
        glutSpecialFunc(self.special_keyboard)
        glutMouseFunc(self.mouse)
        glutPassiveMotionFunc(self.passive_motion)
        glutIdleFunc(self.update)
        
        print("=" * 60)
        print("HICCUP'S ADVENTURE - 3D Game (Simplified)")
        print("=" * 60)
        print("Controls:")
        print("  Menu: UP/DOWN, ENTER")
        print("  Puzzle: WASD to move, QE to move up/down, Mouse to look")
        print("          Click to select block, IJKL to move block horizontally")
        print("          UO to stack blocks up/down, P to skip")
        print("  Maze: WASD to move, QE to move up/down, Mouse to look around")
        print("        P to skip")
        print("  Combat: WASD to move, SPACE to attack, E to dodge")
        print("          TAB to switch weapon, ENTER to retry/continue")
        print("  C: Toggle cheat mode (anywhere)")
        print("  ESC: Back to menu / Exit")
        print("=" * 60)
        print("\nStarting game...")
        
        glutMainLoop()

if __name__ == "__main__":
    game = Game()
    game.run()

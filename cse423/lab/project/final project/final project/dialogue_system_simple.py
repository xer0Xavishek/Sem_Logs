"""
Dialogue System for Hiccup's Adventure
Uses ONLY allowed OpenGL functions - no glutSolid* or gluCylinder
"""
import sys
import os
import math
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from primitives import *


class DialogueSystem:
    """Modern 3D dialogue system with character models using only allowed functions"""
    
    def __init__(self):
        self.window_width = 800
        self.window_height = 600
        
        # Dialogue state
        self.dialogue_active = False
        self.character_name = ""
        self.dialogue_lines = []
        self.current_line = 0
        self.current_dialogue = ""
        self.displayed_text = ""
        self.char_index = 0
        self.text_complete = False
        
        # Text animation
        self.text_speed = 0.03
        self.last_char_time = 0
        
        # 3D scene animation
        self.scene_rotation = 0
        self.character_bob = 0
        self.particle_time = 0
        
        # Character data
        self.characters = {
            'Hiccup': {
                'color': (0.2, 0.5, 0.3),
                'accent': (0.4, 0.7, 0.4),
                'model': 'viking'
            },
            'Mysterious Voice': {
                'color': (0.4, 0.2, 0.6),
                'accent': (0.6, 0.3, 0.8),
                'model': 'spirit'
            },
            'Memory Guardian': {
                'color': (0.6, 0.2, 0.2),
                'accent': (0.8, 0.3, 0.3),
                'model': 'guardian'
            }
        }
        
        # Colors
        self.colors = {
            'text': (0.95, 0.95, 0.98),
            'name': (0.95, 0.85, 0.3),
            'box_bg': (0.05, 0.05, 0.1),
            'box_border': (0.3, 0.25, 0.4)
        }
    
    def init_opengl(self):
        """Initialize OpenGL settings"""
        glClearColor(0.02, 0.02, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def setup_3d_projection(self):
        """Set up 3D perspective projection"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, self.window_width / self.window_height, 1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Atmospheric lighting
        light_pos = [50.0, -100.0, 150.0, 1.0]
        light_ambient = [0.15, 0.15, 0.2, 1.0]
        light_diffuse = [0.7, 0.7, 0.9, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    
    def setup_2d_projection(self):
        """Set up 2D orthographic projection for UI"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.window_width, 0, self.window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
    
    def draw_text(self, text, x, y, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
        """Draw text at specified position"""
        glColor3f(*color)
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))
    
    def draw_centered_text(self, text, y, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
        """Draw centered text"""
        text_width = sum(glutBitmapWidth(font, ord(c)) for c in text)
        x = (self.window_width - text_width) / 2.0
        self.draw_text(text, x, y, color, font)
    
    def draw_viking_character(self, x, y, z, scale=1.0, color=(0.2, 0.5, 0.3)):
        """Draw a 3D Viking character using primitives"""
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(scale, scale, scale)
        
        bob = 2 * math.sin(self.character_bob * 0.02)
        glTranslatef(0, 0, bob)
        
        # Body
        glColor3f(*color)
        draw_cube(30)
        
        # Head
        glPushMatrix()
        glTranslatef(0, 0, 35)
        glColor3f(0.9, 0.75, 0.6)
        draw_cube(25)
        glPopMatrix()
        
        # Hair
        glPushMatrix()
        glTranslatef(0, -5, 43)
        glColor3f(0.35, 0.2, 0.1)
        draw_cube(20)
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_spirit_character(self, x, y, z, scale=1.0, color=(0.4, 0.2, 0.6)):
        """Draw a 3D spirit character using primitives"""
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(scale, scale, scale)
        
        bob = 5 * math.sin(self.character_bob * 0.015)
        glTranslatef(0, 0, bob)
        
        glEnable(GL_BLEND)
        
        # Ethereal body - diamond shape
        glColor4f(color[0], color[1], color[2], 0.6)
        draw_crystal(30)
        
        # Inner glow
        pulse = 0.4 + 0.2 * math.sin(self.character_bob * 0.08)
        glColor4f(0.8, 0.6, 1.0, pulse)
        draw_crystal(18)
        
        # Eyes
        glColor4f(1.0, 1.0, 1.0, 0.9)
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 8, 15, 20)
            draw_cube(8)
            glPopMatrix()
        
        # Floating particles
        glColor4f(0.7, 0.5, 0.9, 0.5)
        for i in range(6):
            angle = i * 60 + self.particle_time * 2
            radius = 40 + 10 * math.sin(self.particle_time * 0.05 + i)
            px = math.cos(math.radians(angle)) * radius
            py = math.sin(math.radians(angle)) * radius
            pz = 20 * math.sin(self.particle_time * 0.03 + i * 0.5)
            
            glPushMatrix()
            glTranslatef(px, py, pz)
            draw_cube(5)
            glPopMatrix()
        
        glDisable(GL_BLEND)
        glPopMatrix()

    def draw_guardian_character(self, x, y, z, scale=1.0, color=(0.6, 0.2, 0.2)):
        """Draw a 3D guardian character using primitives"""
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(scale, scale, scale)
        
        bob = 3 * math.sin(self.character_bob * 0.02)
        glTranslatef(0, 0, bob)
        
        # Main body
        glColor3f(*color)
        glPushMatrix()
        glScalef(1.5, 1.2, 2.0)
        draw_cube(50)
        glPopMatrix()
        
        # Head
        glPushMatrix()
        glTranslatef(0, 0, 50)
        draw_cube(35)
        glPopMatrix()
        
        # Eyes with glow
        eye_pulse = 0.8 + 0.2 * math.sin(self.character_bob * 0.1)
        glColor3f(1.0 * eye_pulse, 0.2 * eye_pulse, 0.2 * eye_pulse)
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 10, 18, 55)
            draw_cube(10)
            glPopMatrix()
        
        # Energy core
        pulse = 0.6 + 0.3 * math.sin(self.character_bob * 0.06)
        glPushMatrix()
        glTranslatef(0, 20, 25)
        glColor3f(0.8 * pulse, 0.2 * pulse, 0.9 * pulse)
        draw_crystal(12)
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_3d_scene(self):
        """Draw the modern 3D dialogue scene"""
        gluLookAt(0, -200, 100, 0, 0, 30, 0, 0, 1)
        
        # Ground plane
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glColor3f(0.05, 0.05, 0.08)
        glVertex3f(-300, -300, 0)
        glVertex3f(300, -300, 0)
        glColor3f(0.08, 0.08, 0.12)
        glVertex3f(300, 300, 0)
        glVertex3f(-300, 300, 0)
        glEnd()
        
        # Central platform
        glColor3f(0.12, 0.12, 0.18)
        glPushMatrix()
        glTranslatef(0, 50, 1)
        draw_ground(60)
        glPopMatrix()
        
        # Draw character based on who's speaking
        char_data = self.characters.get(self.character_name, self.characters['Hiccup'])
        
        if char_data['model'] == 'viking':
            self.draw_viking_character(0, 50, 0, 1.2, char_data['color'])
        elif char_data['model'] == 'spirit':
            self.draw_spirit_character(0, 50, 20, 1.0, char_data['color'])
        elif char_data['model'] == 'guardian':
            self.draw_guardian_character(0, 50, 0, 0.8, char_data['color'])

    def draw_dialogue_box(self):
        """Draw the modern dialogue box UI"""
        if not self.dialogue_active:
            return
        
        box_margin = 60
        box_height = 180
        box_y = 40
        box_width = self.window_width - (box_margin * 2)
        
        glEnable(GL_BLEND)
        
        # Shadow
        shadow_offset = 8
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(box_margin + shadow_offset, box_y - shadow_offset)
        glVertex2f(box_margin + box_width + shadow_offset, box_y - shadow_offset)
        glVertex2f(box_margin + box_width + shadow_offset, box_y + box_height - shadow_offset)
        glVertex2f(box_margin + shadow_offset, box_y + box_height - shadow_offset)
        glEnd()
        
        # Main background
        glBegin(GL_QUADS)
        glColor4f(0.02, 0.02, 0.06, 0.95)
        glVertex2f(box_margin, box_y)
        glVertex2f(box_margin + box_width, box_y)
        glColor4f(0.04, 0.04, 0.10, 0.95)
        glVertex2f(box_margin + box_width, box_y + box_height)
        glVertex2f(box_margin, box_y + box_height)
        glEnd()
        
        # Top accent bar
        glColor4f(0.6, 0.5, 0.2, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(box_margin, box_y + box_height - 3)
        glVertex2f(box_margin + box_width, box_y + box_height - 3)
        glVertex2f(box_margin + box_width, box_y + box_height)
        glVertex2f(box_margin, box_y + box_height)
        glEnd()
        
        # Border
        glColor4f(0.5, 0.4, 0.3, 0.8)
        glLineWidth(3)
        glBegin(GL_LINE_LOOP)
        glVertex2f(box_margin, box_y)
        glVertex2f(box_margin + box_width, box_y)
        glVertex2f(box_margin + box_width, box_y + box_height)
        glVertex2f(box_margin, box_y + box_height)
        glEnd()
        glLineWidth(1)
        
        glDisable(GL_BLEND)
        
        # Character name
        char_data = self.characters.get(self.character_name, {'accent': (0.5, 0.5, 0.5)})
        name_y = box_y + box_height - 45
        name_width = len(self.character_name) * 12 + 40
        name_x = box_margin + 20
        
        glEnable(GL_BLEND)
        # Name background
        glBegin(GL_QUADS)
        glColor4f(char_data['accent'][0] * 0.6, char_data['accent'][1] * 0.6, char_data['accent'][2] * 0.6, 0.95)
        glVertex2f(name_x, name_y - 10)
        glVertex2f(name_x + name_width, name_y - 10)
        glColor4f(char_data['accent'][0] * 0.4, char_data['accent'][1] * 0.4, char_data['accent'][2] * 0.4, 0.95)
        glVertex2f(name_x + name_width, name_y + 28)
        glVertex2f(name_x, name_y + 28)
        glEnd()
        glDisable(GL_BLEND)
        
        # Character name text
        self.draw_text(self.character_name, name_x + 20, name_y, (1.0, 1.0, 1.0), GLUT_BITMAP_HELVETICA_18)
        
        # Dialogue text with word wrapping
        text_x = box_margin + 30
        text_y = box_y + box_height - 80
        max_width = box_width - 60
        
        words = self.displayed_text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in test_line)
            
            if test_width < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw text lines
        for i, line in enumerate(lines[:4]):
            line_y = text_y - i * 28
            self.draw_text(line, text_x, line_y, (0.95, 0.95, 1.0), GLUT_BITMAP_HELVETICA_18)
        
        # Continue indicator
        if self.text_complete:
            indicator_x = box_margin + box_width - 110
            indicator_y = box_y + 15
            blink_alpha = 0.5 + 0.5 * math.sin(self.particle_time * 0.15)
            
            glEnable(GL_BLEND)
            glColor4f(0.3, 0.4, 0.5, 0.7 * blink_alpha)
            glBegin(GL_QUADS)
            glVertex2f(indicator_x - 8, indicator_y - 5)
            glVertex2f(indicator_x + 85, indicator_y - 5)
            glVertex2f(indicator_x + 85, indicator_y + 22)
            glVertex2f(indicator_x - 8, indicator_y + 22)
            glEnd()
            glDisable(GL_BLEND)
            
            self.draw_text("[SPACE]", indicator_x, indicator_y, (0.95, 0.95, 1.0), GLUT_BITMAP_HELVETICA_12)
    
    def draw_scene(self):
        """Draw the complete dialogue scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw 3D background scene
        self.setup_3d_projection()
        self.draw_3d_scene()
        
        # Draw 2D UI overlay
        self.setup_2d_projection()
        self.draw_dialogue_box()
        
        if not hasattr(self, 'integrated_mode') or not self.integrated_mode:
            glutSwapBuffers()
    
    def update_text_animation(self):
        """Update the text typing animation"""
        if not self.dialogue_active or self.text_complete:
            return
        
        current_time = time.time()
        if current_time - self.last_char_time >= self.text_speed:
            if self.char_index < len(self.current_dialogue):
                self.displayed_text += self.current_dialogue[self.char_index]
                self.char_index += 1
                self.last_char_time = current_time
            else:
                self.text_complete = True
        
        self.scene_rotation += 0.2
        self.character_bob += 0.5
        self.particle_time += 0.5

    def show_next_line(self):
        """Show the next line of dialogue"""
        if self.current_line < len(self.dialogue_lines):
            self.current_dialogue = self.dialogue_lines[self.current_line]
            self.displayed_text = ""
            self.char_index = 0
            self.text_complete = False
            self.last_char_time = time.time()
        else:
            self.end_dialogue()
    
    def advance_dialogue(self):
        """Advance to next dialogue line or complete current text"""
        if not self.dialogue_active:
            return False
        
        if not self.text_complete:
            self.displayed_text = self.current_dialogue
            self.text_complete = True
            return False
        else:
            self.current_line += 1
            self.show_next_line()
            return self.current_line >= len(self.dialogue_lines)
    
    def end_dialogue(self):
        """End the current dialogue"""
        self.dialogue_active = False
        self.current_dialogue = ""
        self.displayed_text = ""

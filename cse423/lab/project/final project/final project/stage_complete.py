import sys
import os
import math

# Add the local OpenGL library path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class StageCompleteScreen:
    """Modern 3D stage completion screen"""
    
    def __init__(self):
        self.window_width = 800
        self.window_height = 600
        self.completion_active = False
        self.stage_number = 1
        self.animation_time = 0.0
        self.auto_advance_time = 10.0
        self.auto_advance_enabled = False
        
        # 3D scene elements
        self.crystal_rotation = 0
        self.platform_glow = 0
        
        # Environment
        self.trees = []
        self.init_trees()
        
        # Stage completion messages
        self.stage_messages = {
            1: {
                'title': 'MEMORY FRAGMENT RECOVERED',
                'subtitle': 'The First Echo Awakens',
                'description': 'A memory of home returns to you.'
            },
            2: {
                'title': 'PATHWAY ILLUMINATED',
                'subtitle': 'Deeper Memories Surface',
                'description': 'Friendship remembered, bonds restored.'
            },
            3: {
                'title': 'GUARDIAN DEFEATED',
                'subtitle': 'The Truth Revealed',
                'description': 'Your true identity is restored.'
            }
        }
        
        # Colors
        self.colors = {
            'gold': (0.95, 0.85, 0.3),
            'silver': (0.8, 0.8, 0.9),
            'purple': (0.5, 0.3, 0.7),
            'green': (0.3, 0.8, 0.4)
        }
    
    def init_trees(self):
        """Initialize scattered fallen trees"""
        import random
        random.seed(123)
        
        # Create scattered fallen trees around the scene
        for i in range(12):
            # Random scattered positions
            angle = random.uniform(0, 360)
            distance = random.uniform(100, 250)
            x = math.cos(math.radians(angle)) * distance
            y = math.sin(math.radians(angle)) * distance
            
            self.trees.append({
                'x': x,
                'y': y,
                'length': random.uniform(40, 70),
                'trunk_width': random.uniform(6, 10),
                'fallen_angle': random.uniform(0, 360),  # Direction it's lying
                'tilt': random.uniform(-15, 15),  # Slight tilt
                'color': (0.15 + random.uniform(0, 0.05), 0.2 + random.uniform(0, 0.05), 0.12)
            })
    
    def draw_tree(self, tree):
        """Draw a fallen/scattered tree lying on the ground using ONLY allowed functions"""
        glPushMatrix()
        glTranslatef(tree['x'], tree['y'], tree['trunk_width'])
        
        # Rotate to make it lie on the ground
        glRotatef(tree['fallen_angle'], 0, 0, 1)
        glRotatef(90 + tree['tilt'], 0, 1, 0)
        
        # Trunk - lying cylinder drawn as box - ALLOWED
        glColor3f(0.25, 0.18, 0.12)
        w = tree['trunk_width']
        l = tree['length']
        
        glBegin(GL_QUADS)
        # Front
        glVertex3f(-w, -w, 0)
        glVertex3f(w, -w, 0)
        glVertex3f(w, -w, l)
        glVertex3f(-w, -w, l)
        # Back
        glVertex3f(-w, w, 0)
        glVertex3f(-w, w, l)
        glVertex3f(w, w, l)
        glVertex3f(w, w, 0)
        # Left
        glVertex3f(-w, -w, 0)
        glVertex3f(-w, -w, l)
        glVertex3f(-w, w, l)
        glVertex3f(-w, w, 0)
        # Right
        glVertex3f(w, -w, 0)
        glVertex3f(w, w, 0)
        glVertex3f(w, w, l)
        glVertex3f(w, -w, l)
        glEnd()
        
        # Some broken branches sticking out - ALLOWED
        glColor3f(0.2, 0.15, 0.1)
        for i in range(3):
            branch_pos = tree['length'] * (0.3 + i * 0.25)
            branch_angle = i * 120
            
            glPushMatrix()
            glTranslatef(0, 0, branch_pos)
            glRotatef(branch_angle, 0, 0, 1)
            glRotatef(45, 0, 1, 0)
            
            # Draw branch as box - ALLOWED
            bw = tree['trunk_width'] * 0.3
            bl = tree['length'] * 0.3
            glBegin(GL_QUADS)
            glVertex3f(-bw, -bw, 0)
            glVertex3f(bw, -bw, 0)
            glVertex3f(bw, -bw, bl)
            glVertex3f(-bw, -bw, bl)
            glVertex3f(-bw, bw, 0)
            glVertex3f(-bw, bw, bl)
            glVertex3f(bw, bw, bl)
            glVertex3f(bw, bw, 0)
            glEnd()
            glPopMatrix()
        
        glPopMatrix()
    
    def init_opengl(self):
        """Initialize OpenGL settings"""
        glClearColor(0.02, 0.02, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def setup_3d_projection(self):
        """Set up 3D perspective projection"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.window_width / self.window_height, 1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Lighting
        light_pos = [0.0, 100.0, 200.0, 1.0]
        light_ambient = [0.3, 0.3, 0.4, 1.0]
        light_diffuse = [1.0, 0.9, 0.8, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    
    def setup_2d_projection(self):
        """Set up 2D orthographic projection"""
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
    
    def draw_3d_crystal(self, size, color):
        """Draw a 3D memory crystal"""
        glColor3f(*color)
        
        # Octahedron shape
        glBegin(GL_TRIANGLES)
        for i in range(4):
            angle1 = i * 90
            angle2 = (i + 1) * 90
            x1 = math.cos(math.radians(angle1)) * size
            y1 = math.sin(math.radians(angle1)) * size
            x2 = math.cos(math.radians(angle2)) * size
            y2 = math.sin(math.radians(angle2)) * size
            
            # Top
            glNormal3f(0, 0, 1)
            glVertex3f(0, 0, size * 2)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y2, 0)
            
            # Bottom
            glNormal3f(0, 0, -1)
            glVertex3f(0, 0, -size * 2)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y1, 0)
        glEnd()
    
    def draw_completion_scene(self):
        """Draw a completely different results-style 3D scene"""
        # Top-down angled camera for results view
        gluLookAt(0, -180, 200, 0, 0, 0, 0, 0, 1)
        
        # Dark atmospheric ground
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glColor3f(0.03, 0.03, 0.06)
        glVertex3f(-500, -500, -5)
        glVertex3f(500, -500, -5)
        glVertex3f(500, 500, -5)
        glVertex3f(-500, 500, -5)
        glEnd()
        
        # Draw distant trees for atmosphere
        for tree in self.trees:
            self.draw_tree(tree)
        
        # Three pedestals for the three stages
        pedestal_positions = [(-80, 0), (0, 0), (80, 0)]
        
        for i, (px, py) in enumerate(pedestal_positions):
            stage_num = i + 1
            is_complete = stage_num <= self.stage_number
            
            # Pedestal base using triangles - ALLOWED
            if is_complete:
                glColor3f(0.15, 0.15, 0.22)
            else:
                glColor3f(0.08, 0.08, 0.12)
            
            glPushMatrix()
            glTranslatef(px, py, 0)
            
            # Base platform - draw circle using triangles - ALLOWED
            glBegin(GL_TRIANGLES)
            for j in range(32):
                angle1 = j * (360 / 32)
                angle2 = (j + 1) * (360 / 32)
                x1 = math.cos(math.radians(angle1)) * 35
                y1 = math.sin(math.radians(angle1)) * 35
                x2 = math.cos(math.radians(angle2)) * 35
                y2 = math.sin(math.radians(angle2)) * 35
                
                glVertex3f(0, 0, 0)
                glVertex3f(x1, y1, 0)
                glVertex3f(x2, y2, 0)
            glEnd()
            
            # Pedestal column - draw cylinder using quads - ALLOWED
            glBegin(GL_QUADS)
            for j in range(16):
                angle1 = j * (360 / 16)
                angle2 = (j + 1) * (360 / 16)
                x1 = math.cos(math.radians(angle1)) * 15
                y1 = math.sin(math.radians(angle1)) * 15
                x2 = math.cos(math.radians(angle2)) * 15
                y2 = math.sin(math.radians(angle2)) * 15
                
                glVertex3f(x1, y1, 0)
                glVertex3f(x2, y2, 0)
                glVertex3f(x2, y2, 40)
                glVertex3f(x1, y1, 40)
            glEnd()
            
            # Top of pedestal - draw circle using triangles - ALLOWED
            glPushMatrix()
            glTranslatef(0, 0, 40)
            glBegin(GL_TRIANGLES)
            for j in range(32):
                angle1 = j * (360 / 32)
                angle2 = (j + 1) * (360 / 32)
                x1 = math.cos(math.radians(angle1)) * 18
                y1 = math.sin(math.radians(angle1)) * 18
                x2 = math.cos(math.radians(angle2)) * 18
                y2 = math.sin(math.radians(angle2)) * 18
                
                glVertex3f(0, 0, 0)
                glVertex3f(x1, y1, 0)
                glVertex3f(x2, y2, 0)
            glEnd()
            glPopMatrix()
            
            if is_complete:
                # Glowing effect for completed stages - draw ring using quads - ALLOWED
                glow_pulse = 0.5 + 0.3 * math.sin(self.animation_time * 0.04 + i)
                glEnable(GL_BLEND)
                glColor4f(self.colors['gold'][0] * glow_pulse,
                         self.colors['gold'][1] * glow_pulse,
                         self.colors['gold'][2] * glow_pulse, 0.4)
                glPushMatrix()
                glTranslatef(0, 0, 1)
                glBegin(GL_QUADS)
                for j in range(32):
                    angle1 = j * (360 / 32)
                    angle2 = (j + 1) * (360 / 32)
                    x1 = math.cos(math.radians(angle1)) * 30
                    y1 = math.sin(math.radians(angle1)) * 30
                    x2 = math.cos(math.radians(angle2)) * 30
                    y2 = math.sin(math.radians(angle2)) * 30
                    x3 = math.cos(math.radians(angle2)) * 38
                    y3 = math.sin(math.radians(angle2)) * 38
                    x4 = math.cos(math.radians(angle1)) * 38
                    y4 = math.sin(math.radians(angle1)) * 38
                    
                    glVertex3f(x1, y1, 0)
                    glVertex3f(x2, y2, 0)
                    glVertex3f(x3, y3, 0)
                    glVertex3f(x4, y4, 0)
                glEnd()
                glPopMatrix()
                glDisable(GL_BLEND)
                
                # Memory fragment on pedestal - draw octahedron using triangles - ALLOWED
                glPushMatrix()
                float_offset = 5 * math.sin(self.animation_time * 0.03 + i * 1.2)
                glTranslatef(0, 0, 60 + float_offset)
                glRotatef(self.crystal_rotation + i * 120, 0, 0, 1)
                glRotatef(30, 1, 0, 0)
                
                # Draw octahedron - ALLOWED
                glColor3f(*self.colors['gold'])
                size = 12
                glBegin(GL_TRIANGLES)
                # Top pyramid
                for j in range(4):
                    angle1 = j * 90
                    angle2 = (j + 1) * 90
                    x1 = math.cos(math.radians(angle1)) * size
                    y1 = math.sin(math.radians(angle1)) * size
                    x2 = math.cos(math.radians(angle2)) * size
                    y2 = math.sin(math.radians(angle2)) * size
                    
                    glVertex3f(0, 0, size * 1.5)
                    glVertex3f(x1, y1, 0)
                    glVertex3f(x2, y2, 0)
                
                # Bottom pyramid
                for j in range(4):
                    angle1 = j * 90
                    angle2 = (j + 1) * 90
                    x1 = math.cos(math.radians(angle1)) * size
                    y1 = math.sin(math.radians(angle1)) * size
                    x2 = math.cos(math.radians(angle2)) * size
                    y2 = math.sin(math.radians(angle2)) * size
                    
                    glVertex3f(0, 0, -size * 1.5)
                    glVertex3f(x2, y2, 0)
                    glVertex3f(x1, y1, 0)
                glEnd()
                
                # Inner glow - larger octahedron - ALLOWED
                glEnable(GL_BLEND)
                glColor4f(1.0, 0.9, 0.5, 0.5 * glow_pulse)
                size = size * 1.3
                glBegin(GL_TRIANGLES)
                # Top pyramid
                for j in range(4):
                    angle1 = j * 90
                    angle2 = (j + 1) * 90
                    x1 = math.cos(math.radians(angle1)) * size
                    y1 = math.sin(math.radians(angle1)) * size
                    x2 = math.cos(math.radians(angle2)) * size
                    y2 = math.sin(math.radians(angle2)) * size
                    
                    glVertex3f(0, 0, size * 1.5)
                    glVertex3f(x1, y1, 0)
                    glVertex3f(x2, y2, 0)
                
                # Bottom pyramid
                for j in range(4):
                    angle1 = j * 90
                    angle2 = (j + 1) * 90
                    x1 = math.cos(math.radians(angle1)) * size
                    y1 = math.sin(math.radians(angle1)) * size
                    x2 = math.cos(math.radians(angle2)) * size
                    y2 = math.sin(math.radians(angle2)) * size
                    
                    glVertex3f(0, 0, -size * 1.5)
                    glVertex3f(x2, y2, 0)
                    glVertex3f(x1, y1, 0)
                glEnd()
                glDisable(GL_BLEND)
                glPopMatrix()
                
                # Light beam from fragment - draw cone using quads - ALLOWED
                glEnable(GL_BLEND)
                glColor4f(self.colors['gold'][0], 
                         self.colors['gold'][1], 
                         self.colors['gold'][2], 0.2)
                glPushMatrix()
                glTranslatef(0, 0, 60)
                glBegin(GL_QUADS)
                for j in range(16):
                    angle1 = j * (360 / 16)
                    angle2 = (j + 1) * (360 / 16)
                    x1 = math.cos(math.radians(angle1)) * 8
                    y1 = math.sin(math.radians(angle1)) * 8
                    x2 = math.cos(math.radians(angle2)) * 8
                    y2 = math.sin(math.radians(angle2)) * 8
                    x3 = math.cos(math.radians(angle2)) * 2
                    y3 = math.sin(math.radians(angle2)) * 2
                    x4 = math.cos(math.radians(angle1)) * 2
                    y4 = math.sin(math.radians(angle1)) * 2
                    
                    glVertex3f(x1, y1, 0)
                    glVertex3f(x2, y2, 0)
                    glVertex3f(x3, y3, 100)
                    glVertex3f(x4, y4, 100)
                glEnd()
                glPopMatrix()
                glDisable(GL_BLEND)
            else:
                # Empty pedestal - show locked state using cube - ALLOWED
                glColor3f(0.15, 0.15, 0.18)
                glPushMatrix()
                glTranslatef(0, 0, 60)
                s = 10
                glBegin(GL_QUADS)
                # Front
                glVertex3f(-s, -s, s)
                glVertex3f(s, -s, s)
                glVertex3f(s, s, s)
                glVertex3f(-s, s, s)
                # Back
                glVertex3f(-s, -s, -s)
                glVertex3f(-s, s, -s)
                glVertex3f(s, s, -s)
                glVertex3f(s, -s, -s)
                # Top
                glVertex3f(-s, s, -s)
                glVertex3f(-s, s, s)
                glVertex3f(s, s, s)
                glVertex3f(s, s, -s)
                # Bottom
                glVertex3f(-s, -s, -s)
                glVertex3f(s, -s, -s)
                glVertex3f(s, -s, s)
                glVertex3f(-s, -s, s)
                # Right
                glVertex3f(s, -s, -s)
                glVertex3f(s, s, -s)
                glVertex3f(s, s, s)
                glVertex3f(s, -s, s)
                # Left
                glVertex3f(-s, -s, -s)
                glVertex3f(-s, -s, s)
                glVertex3f(-s, s, s)
                glVertex3f(-s, s, -s)
                glEnd()
                glPopMatrix()
            
            glPopMatrix()
        
        # Connecting energy lines between completed pedestals
        if self.stage_number >= 2:
            glEnable(GL_BLEND)
            glLineWidth(3)
            energy_pulse = 0.4 + 0.3 * math.sin(self.animation_time * 0.05)
            glColor4f(self.colors['gold'][0], 
                     self.colors['gold'][1], 
                     self.colors['gold'][2], energy_pulse)
            
            glBegin(GL_LINES)
            for i in range(min(self.stage_number - 1, 2)):
                x1, y1 = pedestal_positions[i]
                x2, y2 = pedestal_positions[i + 1]
                glVertex3f(x1, y1, 60)
                glVertex3f(x2, y2, 60)
            glEnd()
            
            glLineWidth(1)
            glDisable(GL_BLEND)

    def display(self):
        """Main display function"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if self.completion_active:
            # Draw 3D scene
            self.setup_3d_projection()
            self.draw_completion_scene()
            
            # Draw 2D UI overlay
            self.setup_2d_projection()
            
            # Get stage message
            msg = self.stage_messages.get(self.stage_number, {
                'title': 'STAGE COMPLETE',
                'subtitle': 'Well Done!',
                'description': 'Continue your journey.'
            })
            
            # Centered title card
            glEnable(GL_BLEND)
            
            # Title with simple glow
            title_y = self.window_height - 100
            
            # Glow effect
            for offset in [4, 2]:
                glow_intensity = 0.3 / offset
                glow_color = (self.colors['gold'][0] * glow_intensity,
                             self.colors['gold'][1] * glow_intensity,
                             self.colors['gold'][2] * glow_intensity)
                self.draw_centered_text(msg['title'], title_y + offset, glow_color, GLUT_BITMAP_TIMES_ROMAN_24)
            
            # Main title
            self.draw_centered_text(msg['title'], title_y, self.colors['gold'], GLUT_BITMAP_TIMES_ROMAN_24)
            
            # Subtitle
            subtitle_y = self.window_height - 150
            self.draw_centered_text(msg['subtitle'], subtitle_y, self.colors['silver'], GLUT_BITMAP_HELVETICA_18)
            
            # Description
            desc_y = self.window_height - 190
            self.draw_centered_text(msg['description'], desc_y, (0.7, 0.7, 0.8), GLUT_BITMAP_HELVETICA_12)
            
            # Simple progress text at bottom
            progress_text = f"Stage {self.stage_number} of 3 Complete"
            text_y = 80
            self.draw_centered_text(progress_text, text_y, self.colors['green'], GLUT_BITMAP_HELVETICA_18)
            
            # Simple progress dots
            dot_y = 50
            dot_spacing = 40
            start_x = (self.window_width - (3 * dot_spacing)) // 2
            
            for i in range(3):
                dot_x = start_x + i * dot_spacing + 20
                
                if i < self.stage_number:
                    # Completed - filled circle
                    glColor3f(*self.colors['gold'])
                else:
                    # Not completed - empty circle
                    glColor3f(0.3, 0.3, 0.4)
                
                # Draw dot as small quad
                dot_size = 12
                glBegin(GL_QUADS)
                glVertex2f(dot_x - dot_size/2, dot_y - dot_size/2)
                glVertex2f(dot_x + dot_size/2, dot_y - dot_size/2)
                glVertex2f(dot_x + dot_size/2, dot_y + dot_size/2)
                glVertex2f(dot_x - dot_size/2, dot_y + dot_size/2)
                glEnd()
                
                # Glow for completed
                if i < self.stage_number:
                    glEnable(GL_BLEND)
                    pulse = 0.3 + 0.2 * math.sin(self.animation_time * 0.05)
                    glColor4f(self.colors['gold'][0], 
                             self.colors['gold'][1], 
                             self.colors['gold'][2], pulse)
                    dot_size = 18
                    glBegin(GL_QUADS)
                    glVertex2f(dot_x - dot_size/2, dot_y - dot_size/2)
                    glVertex2f(dot_x + dot_size/2, dot_y - dot_size/2)
                    glVertex2f(dot_x + dot_size/2, dot_y + dot_size/2)
                    glVertex2f(dot_x - dot_size/2, dot_y + dot_size/2)
                    glEnd()
                    glDisable(GL_BLEND)
            
            # Continue prompt
            if self.animation_time > 30:
                pulse = 0.7 + 0.3 * math.sin(self.animation_time * 0.08)
                prompt_y = 20
                self.draw_centered_text("Press any key to continue...", prompt_y, 
                                      (0.9 * pulse, 0.9 * pulse, 1.0 * pulse), 
                                      GLUT_BITMAP_HELVETICA_12)
            
            glDisable(GL_BLEND)
        
        # Only swap buffers in standalone mode
        if not hasattr(self, 'integrated_mode') or not self.integrated_mode:
            glutSwapBuffers()
    
    def start_completion(self, stage_number, completion_time=0.0, auto_advance=True):
        """Start the stage completion animation"""
        self.stage_number = stage_number
        self.completion_active = True
        self.animation_time = 0.0
        self.crystal_rotation = 0
        self.auto_advance_enabled = auto_advance
        print(f"Stage {stage_number} completed!")
    
    def update(self):
        """Update the completion screen animation"""
        if not self.completion_active:
            return False
        
        self.animation_time += 0.5  # Slower animation
        self.crystal_rotation += 0.8  # Slower rotation
        
        # Auto advance if enabled
        if self.auto_advance_enabled and self.animation_time >= self.auto_advance_time * 60:
            self.end_completion()
            return True
        
        return False
    
    def end_completion(self):
        """End the completion screen"""
        self.completion_active = False
        print("Advancing to next stage...")
    
    def handle_input(self):
        """Handle input to skip completion screen"""
        if self.completion_active and self.animation_time > 30:
            self.end_completion()
            return True
        return False
    
    def is_complete(self):
        """Check if the completion screen has finished"""
        return not self.completion_active
    
    def keyboard(self, key, x, y):
        """Handle keyboard input"""
        if key == b'\x1b':
            glutLeaveMainLoop()
        else:
            if self.handle_input():
                print("Completion screen skipped")
    
    def run(self):
        """Run standalone for testing"""
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_width, self.window_height)
        glutInitWindowPosition(100, 100)
        glutCreateWindow(b"Stage Complete Test")
        
        self.init_opengl()
        self.start_completion(1)
        
        glutDisplayFunc(self.display)
        glutKeyboardFunc(self.keyboard)
        glutIdleFunc(lambda: (self.update(), glutPostRedisplay()))
        
        print("Stage Complete Screen Test")
        print("Press any key to continue, ESC to exit")
        
        glutMainLoop()


if __name__ == "__main__":
    screen = StageCompleteScreen()
    screen.run()

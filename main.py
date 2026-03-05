import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen Dimensions
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
BLOCK_SIZE = 30
PLAY_WIDTH = 300  # 10 blocks * 30
PLAY_HEIGHT = 600 # 20 blocks * 30
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = (SCREEN_HEIGHT - PLAY_HEIGHT) // 2

# Colors
COLOR_BG = (15, 15, 26)
COLOR_GRID = (30, 30, 40)
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (0, 243, 255)

# Tetromino Colors
COLORS = [
    (0, 0, 0),       # Null
    (0, 240, 240),   # I
    (0, 0, 240),     # J
    (240, 160, 0),   # L
    (240, 240, 0),   # O
    (0, 240, 0),     # S
    (160, 0, 240),   # T
    (240, 0, 0)      # Z
]

# Shapes (Same as JS version)
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

SHAPES = [I, J, L, O, S, T, Z]
SHAPE_COLORS = [1, 2, 3, 4, 5, 6, 7]

# Fonts
FONT_MAIN = pygame.font.SysFont('arial', 30, bold=True)
FONT_SMALL = pygame.font.SysFont('arial', 20)
FONT_TITLE = pygame.font.SysFont('arial', 50, bold=True)

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

class Button:
    def __init__(self, text, x, y, w, h, func):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.func = func
        self.hovered = False

    def draw(self, surface):
        color = COLOR_ACCENT if self.hovered else (100, 100, 100)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)
        
        text_surf = FONT_SMALL.render(self.text, True, (255, 255, 255) if not self.hovered else (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.func:
            self.func()

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption('Tetris Unofficial')
        self.clock = pygame.time.Clock()
        self.state = 'START'  # START, PLAYING, GAMEOVER
        self.reset_game()
        
        # UI Buttons
        self.buttons = [
            Button("RESET", 20, SCREEN_HEIGHT - 60, 80, 40, self.go_to_start),
            Button("QUIT", SCREEN_WIDTH - 100, SCREEN_HEIGHT - 60, 80, 40, sys.exit)
        ]

    def draw_start_screen(self, surface):
        surface.fill(COLOR_BG)
        # Title
        font_title = pygame.font.SysFont('arial', 80, bold=True)
        label_title = font_title.render('TETRIS', 1, COLOR_ACCENT)
        label_sub = FONT_MAIN.render('UNOFFICIAL', 1, COLOR_TEXT)
        
        surface.blit(label_title, (SCREEN_WIDTH/2 - label_title.get_width()/2, SCREEN_HEIGHT/2 - 150))
        surface.blit(label_sub, (SCREEN_WIDTH/2 - label_sub.get_width()/2, SCREEN_HEIGHT/2 - 70))
        
        # Start Prompt
        font_msg = pygame.font.SysFont('arial', 40)
        label_msg = font_msg.render('Press Any Key to Start', 1, (255, 255, 255))
        
        # Blinking effect
        if pygame.time.get_ticks() % 1000 < 500:
            surface.blit(label_msg, (SCREEN_WIDTH/2 - label_msg.get_width()/2, SCREEN_HEIGHT/2 + 50))
            
        pygame.display.update()

    def go_to_start(self):
        self.state = 'START'
        self.reset_game()

    def reset_game(self):
        self.grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
        self.locked_positions = {}  # Fixed: Now a class attribute
        self.bag = []
        self.current_piece = self.get_shape()
        self.next_piece = self.get_shape()
        self.hold_piece = None
        self.can_hold = True
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        self.fall_speed = 0.5
        self.t_spin_ready = False
        self.last_move_rotate = False
        self.combo = -1 # Combo counter (starts at -1, first clear makes it 0)
        
        # DAS (Delayed Auto Shift) variables
        self.move_timers = {'left': 0, 'right': 0, 'down': 0}
        self.das_delay = 200 # ms before auto repeat starts
        self.arr_delay = 50  # ms between repeats

    def move(self, dx, dy):
        self.current_piece.x += dx
        self.current_piece.y += dy
        if not self.valid_space(self.current_piece, self.grid):
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            return False
        self.last_move_rotate = False
        return True

    def get_shape(self):
        if not self.bag:
            self.bag = list(range(len(SHAPES)))
            random.shuffle(self.bag)
        
        shape_idx = self.bag.pop()
        return Piece(5, 0, SHAPES[shape_idx])

    def create_grid(self, locked_pos={}):
        grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if (x, y) in locked_pos:
                    c = locked_pos[(x,y)]
                    grid[y][x] = c
        return grid

    def convert_shape_format(self, piece):
        positions = []
        format = piece.shape[piece.rotation % len(piece.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    positions.append((piece.x + j - 2, piece.y + i - 4))

        return positions

    def valid_space(self, piece, grid):
        accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
        accepted_pos = [j for sub in accepted_pos for j in sub]

        formatted = self.convert_shape_format(piece)

        for pos in formatted:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
        return True

    def check_lost(self, positions):
        for pos in positions:
            x, y = pos
            if y < 1:
                return True
        return False

    def check_t_spin(self, piece, grid):
        if piece.shape != T:
            return False
        
    def check_t_spin(self, piece, grid):
        if piece.shape != T or not self.last_move_rotate:
            return False
        
        # Center of T (approximate based on rotation)
        # In our 5x5 matrix, the center is at (2, 2)
        # piece.x, piece.y is the top-left of the 5x5 matrix on the board
        center_x = piece.x + 2
        center_y = piece.y + 2
        
        # Corners relative to center: (-1, -1), (1, -1), (-1, 1), (1, 1)
        corners = [
            (center_x - 1, center_y - 1),
            (center_x + 1, center_y - 1),
            (center_x - 1, center_y + 1),
            (center_x + 1, center_y + 1)
        ]
        
        occupied = 0
        for x, y in corners:
            # Check if out of bounds or occupied
            if x < 0 or x >= 10 or y >= 20: # Wall/Floor counts as occupied
                occupied += 1
            elif y >= 0 and grid[y][x] != (0,0,0): # Block present
                occupied += 1
                
        return occupied >= 3

    def draw_text_middle(self, text, size, color, surface):
        font = pygame.font.SysFont('arial', size, bold=True)
        label = font.render(text, 1, color)
        surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))

    def draw_grid(self, surface, grid):
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        pygame.draw.rect(surface, COLOR_ACCENT, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 2)

        for i in range(len(grid)):
            pygame.draw.line(surface, COLOR_GRID, (TOP_LEFT_X, TOP_LEFT_Y + i*BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i*BLOCK_SIZE))
            for j in range(len(grid[i])):
                pygame.draw.line(surface, COLOR_GRID, (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))

    def clear_rows(self, grid, locked):
        inc = 0
        ind = 19
        for i in range(len(grid)-1, -1, -1):
            row = grid[i]
            if (0,0,0) not in row:
                inc += 1
                ind = i
                for j in range(len(row)):
                    try:
                        del locked[(j,i)]
                    except:
                        continue

        if inc > 0:
            for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
                x, y = key
                if y < ind:
                    newKey = (x, y + inc)
                    locked[newKey] = locked.pop(key)
        
        return inc

    def draw_next_shape(self, shape, surface):
        font = FONT_SMALL
        label = font.render('Next', 1, COLOR_TEXT)

        sx = TOP_LEFT_X + PLAY_WIDTH + 50
        sy = TOP_LEFT_Y + 50
        format = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, COLORS[SHAPE_COLORS[SHAPES.index(shape.shape)]], (sx + j*BLOCK_SIZE, sy + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        surface.blit(label, (sx + 10, sy - 30))

    def draw_hold_shape(self, shape, surface):
        font = FONT_SMALL
        label = font.render('Hold', 1, COLOR_TEXT)
        sx = TOP_LEFT_X - 150
        sy = TOP_LEFT_Y + 50
        
        if shape:
            format = shape.shape[shape.rotation % len(shape.shape)]
            for i, line in enumerate(format):
                row = list(line)
                for j, column in enumerate(row):
                    if column == '0':
                        pygame.draw.rect(surface, COLORS[SHAPE_COLORS[SHAPES.index(shape.shape)]], (sx + j*BLOCK_SIZE, sy + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        surface.blit(label, (sx + 10, sy - 30))

    def draw_window(self, surface, grid, score=0, level=1):
        surface.fill(COLOR_BG)

        # Title
        font = FONT_TITLE
        label = font.render('TETRIS', 1, COLOR_TEXT)
        surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))
        
        # Score
        font = FONT_SMALL
        label = font.render('Score: ' + str(score), 1, COLOR_TEXT)
        sx = TOP_LEFT_X + PLAY_WIDTH + 50
        sy = TOP_LEFT_Y + 200
        surface.blit(label, (sx, sy))
        
        label = font.render('Level: ' + str(level), 1, COLOR_TEXT)
        surface.blit(label, (sx, sy + 30))

        self.draw_grid(surface, grid)
        self.draw_next_shape(self.next_piece, surface)
        self.draw_hold_shape(self.hold_piece, surface)
        
        # Draw Buttons
        for btn in self.buttons:
            btn.draw(surface)

    def run(self):
        # locked_positions removed from here as it's now in self
        change_piece = False
        run = True
        
        while run:
            if self.state == 'START':
                self.draw_start_screen(self.screen)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        self.state = 'PLAYING'
                        self.reset_game()
                continue

            self.grid = self.create_grid(self.locked_positions)
            self.fall_time += self.clock.get_rawtime()
            self.clock.tick()

            # Fall speed control
            if self.fall_time/1000 > self.fall_speed:
                self.fall_time = 0
                self.current_piece.y += 1
                if not self.valid_space(self.current_piece, self.grid) and self.current_piece.y > 0:
                    self.current_piece.y -= 1
                    change_piece = True

            # Input Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEMOTION:
                    for btn in self.buttons:
                        btn.check_hover(event.pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        for btn in self.buttons:
                            btn.check_click(event.pos)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move(-1, 0)
                        self.move_timers['left'] = 0 # Reset timer on fresh press
                    elif event.key == pygame.K_RIGHT:
                        self.move(1, 0)
                        self.move_timers['right'] = 0
                    elif event.key == pygame.K_DOWN:
                        self.move(0, 1)
                        self.move_timers['down'] = 0
                    elif event.key == pygame.K_UP:
                        # Hard Drop
                        while self.valid_space(self.current_piece, self.grid):
                            self.current_piece.y += 1
                        self.current_piece.y -= 1
                        change_piece = True
                        self.last_move_rotate = False
                    elif event.key == pygame.K_z:
                        self.current_piece.rotation += 1
                        if not self.valid_space(self.current_piece, self.grid):
                            self.current_piece.rotation -= 1
                        else:
                            self.last_move_rotate = True
                    elif event.key == pygame.K_x:
                        self.current_piece.rotation -= 1
                        if not self.valid_space(self.current_piece, self.grid):
                            self.current_piece.rotation += 1
                        else:
                            self.last_move_rotate = True
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        if self.can_hold:
                            if self.hold_piece is None:
                                self.hold_piece = self.current_piece
                                self.current_piece = self.next_piece
                                self.next_piece = self.get_shape()
                            else:
                                self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
                                self.current_piece.x = 5
                                self.current_piece.y = 0
                            self.can_hold = False
                    elif event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused

            # Continuous Movement (DAS/ARR)
            keys = pygame.key.get_pressed()
            dt = self.clock.get_rawtime()
            
            # Left
            if keys[pygame.K_LEFT]:
                self.move_timers['left'] += dt
                if self.move_timers['left'] > self.das_delay:
                    if self.move(-1, 0):
                        self.move_timers['left'] -= self.arr_delay
            else:
                self.move_timers['left'] = 0
            
            # Right
            if keys[pygame.K_RIGHT]:
                self.move_timers['right'] += dt
                if self.move_timers['right'] > self.das_delay:
                    if self.move(1, 0):
                        self.move_timers['right'] -= self.arr_delay
            else:
                self.move_timers['right'] = 0
                
            # Down (Soft Drop)
            if keys[pygame.K_DOWN]:
                self.move_timers['down'] += dt
                if self.move_timers['down'] > 50: # Faster soft drop
                    if self.move(0, 1):
                        self.move_timers['down'] = 0
            else:
                self.move_timers['down'] = 0

            if self.paused:
                self.draw_text_middle("PAUSED", 60, COLOR_TEXT, self.screen)
                pygame.display.update()
                continue

            shape_pos = self.convert_shape_format(self.current_piece)

            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                if y > -1:
                    self.grid[y][x] = COLORS[SHAPE_COLORS[SHAPES.index(self.current_piece.shape)]]

            if change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    self.locked_positions[p] = COLORS[SHAPE_COLORS[SHAPES.index(self.current_piece.shape)]]
                
                self.current_piece = self.next_piece
                self.next_piece = self.get_shape()
                change_piece = False
                self.can_hold = True
                
                rows = self.clear_rows(self.grid, self.locked_positions)
                
                # Scoring
                if rows > 0:
                    self.combo += 1
                    base_score = 0
                    if self.check_t_spin(self.current_piece, self.grid): # Use proper check
                        base_score = 400 * rows * 2 # Bonus
                        print("T-SPIN!")
                    else:
                        scores = [0, 100, 300, 500, 800]
                        base_score = scores[rows]
                    
                    # Add Combo Bonus (50 * combo * level)
                    combo_bonus = 50 * self.combo * self.level
                    self.score += (base_score * self.level) + combo_bonus
                    
                    if self.combo > 0:
                        print(f"COMBO {self.combo}!")
                    
                    self.lines_cleared += rows
                    self.level = self.lines_cleared // 10 + 1
                    self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05)
                else:
                    self.combo = -1

            self.draw_window(self.screen, self.grid, self.score, self.level)
            pygame.display.update()

            if self.check_lost(self.locked_positions):
                self.draw_text_middle("GAME OVER", 80, COLOR_TEXT, self.screen)
                pygame.display.update()
                pygame.time.delay(2000)
                self.go_to_start()
                # self.locked_positions is cleared in go_to_start -> reset_game

if __name__ == '__main__':
    game = TetrisGame()
    game.run()

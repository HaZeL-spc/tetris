import pygame
import random

# creating the data structure for pieces
# setting up global vars
# functions
# - create_grid
# - draw_grid
# - draw_window
# - rotating shape in main
# - setting up the main

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

import sys
import os


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


pygame.font.init()

# GLOBALS VARS
dirname = os.path.dirname(__file__)

s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 690  # meaning 600 // 20 = 20 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

screen = pygame.display.set_mode((s_width, s_height))
clock = pygame.time.Clock()
run = True

shape_moved = False
pace_down = 0
pace_barrier = 30
first_round = False
is_dead = False
level = 1

pygame.mixer.init()
music = pygame.mixer.music.load(os.path.join(dirname, 'tetris-gameboy-02.mp3'))
pygame.mixer.music.play(-1)
pygame.display.set_caption("Tetris")


# SHAPE FORMATS

S = [['.....',
      '......',
      '..00..',
      '.00...',
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
      '.....',
      '0000.',
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

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255),
                (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
shapes_on_screen = []
# index 0 - 6 represent shape
grid = [[(0, 0, 0) for x in range(play_width//block_size)]
        for i in range(play_height//block_size)]


class Shape:
    def __init__(self, x, y, shape, color, widthL, widthR):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0
        self.widthL = widthL
        self.widthR = widthR


def get_shape():
    shape = random.choice(shapes)
    return shape


def show_shape_next_to(x, y, shape):
    color = shape_colors[shapes.index(shape)]
    for i in range(len(shape[0])):
        for j in range(len(shape[0][i])):
            if shape[0][i][j] == "0":
                pygame.draw.rect(
                    screen, color, (x + j*block_size, y + i*block_size, block_size, block_size), 0)
                pygame.draw.rect(screen, (100, 100, 100), (x + j*block_size,
                                                           y + i*block_size, block_size, block_size), 1)


def get_width(shape, rotation):
    start_index = 4
    koniec_index = 0
    for i in range(len(shape[rotation])):
        for j in range(len(shape[rotation][i])):
            if shape[rotation][i][j] == "0":
                if j < start_index:
                    start_index = j
                if j > koniec_index:
                    koniec_index = j
    widthL = 2 - start_index
    widthP = koniec_index - 2

    return widthL, widthP


def save_shape(shape):
    color = shape_colors[shapes.index(shape)]
    widthL, widthP = get_width(shape, 0)
    shapes_on_screen.append(Shape(play_width//2, 2*block_size,
                                  shape, color, widthL * block_size, widthP*block_size))


def delete_remaining(shape_object, grid):
    for i in range(len(shape_object.shape[shape_object.rotation])):
        for j in range(len(shape_object.shape[shape_object.rotation][i])):
            if shape_object.shape[shape_object.rotation][i][j] == "0":
                grid[shape_object.y//block_size + i -
                     2][shape_object.x//block_size + j-2] = (0, 0, 0)
    return grid


def convert_shape_to_screen(shape_object, grid):
    for i in range(len(shape_object.shape[shape_object.rotation])):
        for j in range(len(shape_object.shape[shape_object.rotation][i])):
            if shape_object.shape[shape_object.rotation][i][j] == "0":
                #print(shape.y//block_size + i-2,shape.x//block_size + j-2)
                grid[shape_object.y//block_size + i-2][shape_object.x //
                                                       block_size + j-2] = shape_object.color
    return grid


def check_down_collision():
    element = shapes_on_screen[len(shapes_on_screen)-1]
    for i in range(len(element.shape[element.rotation])):
        for j in range(len(element.shape[element.rotation][i])):
            box = element.shape[element.rotation][i][j]
            if box == "0":
                height = (i - 2)*block_size + element.y + block_size
                if height >= play_height:
                    return True
    return False


def check_box_collision():
    element = shapes_on_screen[len(shapes_on_screen)-1]
    for i in range(len(element.shape[element.rotation])):
        for j in range(len(element.shape[element.rotation][i])):
            box = element.shape[element.rotation][i][j]
            if box == "0":
                grid_box = grid[element.y//block_size +
                                i-2][element.x//block_size + j-2]
                if grid_box != (0, 0, 0):
                    return True
    return False


def check_if_died():
    for i in range(4, -1, -1):
        for j in range(len(grid[i])):
            if grid[i][j] != (0, 0, 0):
                return True
    return False


def check_combo(grid):
    i = len(grid)-1
    while i > 0:
        count_in_row = 0
        for j in range(len(grid[i])):
            grid_box = grid[i][j]
            if grid_box != (0, 0, 0):
                count_in_row += 1

        if count_in_row == len(grid[i]):
            grid.pop(i)
            row = [(0, 0, 0) for x in range(play_width//block_size)]
            grid.insert(0, row)
        else:
            i -= 1

    return grid


def draw_alongside_fields():
    pygame.draw.rect(screen, (50, 50, 50),
                     (0, 0, (s_width - play_width) / 2, s_height), 0)
    pygame.draw.rect(screen, (50, 50, 50), (top_left_x +
                                            play_width, 0, (s_width - play_width) / 2, s_height), 0)

    pygame.draw.rect(screen, (130, 130, 130),
                     (top_left_x - 10, 0, 10, s_height), 0)
    pygame.draw.rect(screen, (130, 130, 130),
                     (top_left_x + play_width, 0, 10, s_height), 0)

    arcade_font_level = pygame.font.Font(
        os.path.join(dirname, 'ARCADECLASSIC.TTF'), 30)

    text_level = arcade_font_level.render("Level", 1, (255, 255, 255))
    text_level_number = arcade_font_level.render(
        str(level), 1, (255, 255, 255))
    next_shape_text = arcade_font_level.render("nastepny", 1, (255, 255, 255))

    screen.blit(text_level, (650, 100))
    screen.blit(text_level_number, (650 + text_level.get_width() //
                                    2 - text_level_number.get_width()//2, 140))

    screen.blit(next_shape_text, (630, 250))
    show_shape_next_to(620, 300, next_shape)


def write_end_game():
    arcade_font_main = pygame.font.Font(
        os.path.join(dirname, 'ARCADECLASSIC.TTF'), 100)
    arcade_font_bottom = pygame.font.Font(
        os.path.join(dirname, 'ARCADECLASSIC.TTF'), 30)

    text1 = arcade_font_main.render("Przegrales", 1, (255, 100, 100))
    text2 = arcade_font_bottom.render(
        "kliknij spacje zeby sprobowac ponownie", 1, (255, 100, 100))

    screen.blit(text1, (s_width//2-text1.get_width() //
                        2, s_height//2-text1.get_height()//2))
    screen.blit(text2, (s_width//2-text2.get_width()//2,
                        s_height//2-text2.get_height()//2+70))


def redrawGameWindow():
    #pygame.draw.rect(screen, (0,0,0), (0,0,s_width, s_height), 0)
    #pygame.draw.rect(screen, (255,0,0), (top_left_x, top_left_y, play_width, play_height), 1)

    draw_alongside_fields()

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            pygame.draw.rect(screen, color, (top_left_x + j*block_size,
                                             top_left_y + i*block_size, block_size, block_size), 0)
            if color != (0, 0, 0):
                pygame.draw.rect(screen, (100, 100, 100), (top_left_x + j*block_size,
                                                           top_left_y + i*block_size, block_size, block_size), 1)

    if is_dead:
        write_end_game()

    pygame.draw.rect(screen, (255, 50, 50), (top_left_x,
                                             top_left_y + block_size*5, play_width, 10), 0)
    #pygame.draw.rect(screen, (255,255,255), (top_left_x + shapes_on_screen[len(shapes_on_screen)-1].x, top_left_y + shapes_on_screen[len(shapes_on_screen)-1].y, block_size, block_size), 3)
    pygame.display.update()


next_shape = get_shape()

while run:
    clock.tick(60)
    if not shape_moved and not is_dead:
        shape = next_shape
        save_shape(shape)
        shape_moved = True
        if len(shapes_on_screen) % 15 == 0:
            level += 1
            pace_barrier = 30 - level*2

        next_shape = get_shape()

    element = shapes_on_screen[len(shapes_on_screen)-1]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            # obrot ksztaltu
            if event.key == pygame.K_SPACE:
                if not is_dead:
                    grid = delete_remaining(element, grid)

                    if element.rotation + 1 >= len(element.shape):
                        widthL, widthR = get_width(element.shape, 0)
                        if element.x - widthL*block_size >= 0 and element.x + widthR*block_size + block_size <= play_width:
                            element.rotation = 0
                            if check_box_collision():
                                element.rotation = len(element.shape) - 1
                    else:
                        widthL, widthR = get_width(
                            element.shape, element.rotation + 1)
                        if element.x - widthL*block_size >= 0 and element.x + widthR*block_size + block_size <= play_width:
                            element.rotation += 1
                            if check_box_collision():
                                element.rotation -= 1

                    grid = convert_shape_to_screen(element, grid)
                    widthL, widthR = get_width(element.shape, element.rotation)
                    element.widthL = widthL * block_size
                    element.widthR = widthR * block_size
                else:
                    is_dead = False
                    shape_moved = False
                    grid = [[(0, 0, 0) for x in range(play_width//block_size)]
                            for i in range(play_height//block_size)]

            # skrecanie na boki
            if not is_dead:
                if event.key == pygame.K_LEFT and element.x - element.widthL > 0:
                    grid = delete_remaining(element, grid)
                    element.x -= block_size

                    if check_box_collision():
                        element.x += block_size

                    grid = convert_shape_to_screen(element, grid)
                if event.key == pygame.K_RIGHT and element.x + element.widthR + block_size < play_width:
                    grid = delete_remaining(element, grid)
                    element.x += block_size

                    if check_box_collision():
                        element.x -= block_size

                    grid = convert_shape_to_screen(element, grid)

                if event.key == pygame.K_DOWN:
                    pace_barrier = 4

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pace_barrier = 30 - level*2

    if not is_dead:
        if not check_down_collision():
            pace_down += 1
            if pace_down >= pace_barrier and shape_moved:
                grid = delete_remaining(element, grid)
                element.y += block_size
                if not check_box_collision():
                    grid = convert_shape_to_screen(element, grid)
                    pace_down = 0
                else:
                    element.y -= block_size
                    grid = convert_shape_to_screen(element, grid)
                    if check_if_died():
                        is_dead = True
                        level = 1
                    else:
                        grid = check_combo(grid)
                        shape_moved = False
        else:
            shape_moved = False
            grid = check_combo(grid)

    redrawGameWindow()

pygame.quit()

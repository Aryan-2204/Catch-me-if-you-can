#!/usr/bin/env python3
import pygame
import sys
import os
import random
import math
from entities import Player, Pokemon, Item
from astar import astar
import storage

pygame.init()

# Game Constants
WIDTH, HEIGHT = 900, 900
ROWS, COLS = 15, 15
BLOCK_SIZE = WIDTH // COLS
FPS = 60

# Colors
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (60, 100, 200)
GREEN = (50, 200, 50)
RED = (220, 50, 50)
GRID_COLOR = (200, 200, 200)

# Map Themes
THEMES = [
    {"bg": WHITE, "wall": BLUE, "grid": (200, 200, 200)},
    {"bg": (40, 60, 40), "wall": (120, 80, 20), "grid": (50, 70, 50)},
    {"bg": (200, 220, 250), "wall": (100, 150, 200), "grid": (180, 200, 230)}
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Chase")
clock = pygame.time.Clock()

# Load Images (fallback to colors if missing)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
trainer_img = None
pokemon_img = None
rock_img = None
pokeball_img = None
try:
    trainer_img = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "ash.png")).convert_alpha(), (BLOCK_SIZE, BLOCK_SIZE))
except:
    pass
try:
    pokemon_img = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "pikachu.png")).convert_alpha(), (BLOCK_SIZE, BLOCK_SIZE))
except:
    pass
try:
    rock_img = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "rock.png")).convert_alpha(), (BLOCK_SIZE, BLOCK_SIZE))
except:
    pass
try:
    pokeball_img = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "pokeball.png")).convert_alpha(), (BLOCK_SIZE, BLOCK_SIZE))
except:
    pass

# Fonts
font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 40)

grid = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1,  Ascend
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1,  Ascend
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1 Ascend


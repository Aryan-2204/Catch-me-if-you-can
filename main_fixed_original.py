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
FPS = 60 # Boosted FPS for smooth UI and animations

# Colors
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (60, 100, 200)    # Walls
GREEN = (50, 200, 50)    # Trainer
RED = (220, 50, 50)      # Pokemon
GRID_COLOR = (200, 200, 200)

# Map Themes
THEMES = [
    {"bg": WHITE, "wall": BLUE, "grid": (200, 200, 200)},         # 0: Default
    {"bg": (40, 60, 40), "wall": (120, 80, 20), "grid": (50, 70, 50)}, # 1: Forest/Cave
    {"bg": (200, 220, 250), "wall": (100, 150, 200), "grid": (180, 200, 230)} # 2: City/Ice
]
current_theme_idx = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Trainer vs Pokémon (A* vs Minimax)")
clock = pygame.time.Clock()

# Load Images
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    trainer_img = pygame.image.load(os.path.join(BASE_DIR, "ash.png")).convert_alpha()
    trainer_img = pygame.transform.scale(trainer_img, (BLOCK_SIZE, BLOCK_SIZE))
except Exception as e:
    print("Error loading ash:", e)
    trainer_img = None

try:
    pokemon_img = pygame.image.load(os.path.join(BASE_DIR, "pikachu.png")).convert_alpha()
    pokemon_img = pygame.transform.scale(pokemon_img, (BLOCK_SIZE, BLOCK_SIZE))
except Exception as e:
    print("Error loading pikachu:", e)
    pokemon_img = None

try:
    rock_img = pygame.image.load(os.path.join(BASE_DIR, "rock.png")).convert_alpha()
    rock_img = pygame.transform.scale(rock_img, (BLOCK_SIZE, BLOCK_SIZE))
except Exception as e:
    print("Error loading rock:", e)
    rock_img = None

try:
    pokeball_img = pygame.image.load(os.path.join(BASE_DIR, "pokeball.png")).convert_alpha()
    pokeball_img = pygame.transform.scale(pokeball_img, (BLOCK_SIZE, BLOCK_SIZE))
except Exception as e:
    print("Error loading pokeball:", e)
    pokeball_img = None

# Additional UI characters
ui_chars = []
for name in ["charmander.png", "squirtle.png", "bulbasaur.png", "mewtwo.png"]:
    try:
        img = pygame.image.load(os.path.join(BASE_DIR, name)).convert_alpha()
        ui_chars.append(pygame.transform.scale(img, (120, 120)))
    except Exception as e:
        print(f"Error loading {name}:", e)
        ui_chars.append(None)
char_mander, squir_tle, bulba_saur, mew_two = ui_chars

# Retro font
try:
    font_path = os.path.join(BASE_DIR, "press_start_2p.ttf")
    font = pygame.font.Font(font_path, 16)
    large_font = pygame.font.Font(font_path, 32)
except Exception as e:
    print("Error loading retro font:", e)
    try:
        font = pygame.font.SysFont("Courier", 24, bold=True)
        large_font = pygame.font.SysFont("Courier", 40, bold=True)
    except:
        font = pygame.font.Font(None, 24)
        large_font = pygame.font.Font(None, 40)

# Title font
try:
    title_font_path = os.path.join(BASE_DIR, "Pokemon Solid.ttf")
    title_font = pygame.font.Font(title_font_path, 80)
except Exception as e:
    print("Error loading title font:", e)
    title_font = large_font

# 15x15 map. 1 = wall, 0 = path
grid = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Randomly select valid spawn locations
spawnable = [(r, c) for r in range(ROWS) for c in range(COLS) if grid[r][c] == 0]

# Initialize game entity variables
player = None
pokemon = None
items = []

score = 0
game_over = False

def draw_grid():
    theme = THEMES[current_theme_idx]
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            # Base floor
            pygame.draw.rect(screen, theme["bg"], rect)
            pygame.draw.rect(screen, theme["grid"], rect, 1)
            
            # If it's a wall, draw the rock on top
            if grid[r][c] == 1:
                if rock_img:
                    screen.blit(rock_img, rect.topleft)
                else:
                    pygame.draw.rect(screen, theme["wall"], rect)
                    pygame.draw.rect(screen, BLACK, rect, 2)

def draw_entity(pos, color, label="", is_trainer=False, is_pokemon=False, anim_tick=0):
    x = pos[1] * BLOCK_SIZE
    y = pos[0] * BLOCK_SIZE
    
    # Walking bob animation
    bob_y = math.sin(anim_tick * 0.25) * 4 if (is_trainer or is_pokemon) else 0
    
    if is_trainer and trainer_img:
        screen.blit(trainer_img, (x, y + bob_y))
    elif is_pokemon and pokemon_img:
        screen.blit(pokemon_img, (x, y + bob_y))
    else:
        cx, cy = x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2 + bob_y
        pygame.draw.circle(screen, color, (int(cx), int(cy)), BLOCK_SIZE // 2 - 4)
        pygame.draw.circle(screen, BLACK, (int(cx), int(cy)), BLOCK_SIZE // 2 - 4, 3)
        if label:
            t = font.render(label, True, BLACK)
            t_rect = t.get_rect(center=(cx, cy))
            screen.blit(t, t_rect)

def draw_button(surface, text, font, color, rect_obj, hover=False):
    # Enlarge button purely on logic dimensions for hover
    if hover:
        rect_obj = rect_obj.inflate(8, 8)
    
    # Draw classic RPG thick borders
    # Outer black box
    pygame.draw.rect(surface, BLACK, rect_obj)
    # Inner colored fill
    fill_rect = rect_obj.inflate(-8, -8)
    pygame.draw.rect(surface, color, fill_rect)
    # Thin inner border
    inner_border = fill_rect.inflate(-4, -4)
    pygame.draw.rect(surface, BLACK, inner_border, 2)
    
    lbl = font.render(text, True, BLACK)
    l_rect = lbl.get_rect(center=rect_obj.center)
    surface.blit(lbl, l_rect)

title_surface_cache = None

def get_title_surface():
    global title_surface_cache
    if title_surface_cache is not None:
        return title_surface_cache
        
    title_text = "Pokémon Chase"
    
    # Calculate dimensions
    base_text = title_font.render(title_text, True, (255, 204, 0))
    w, h = base_text.get_size()
    
    # Create a padded surface to hold outline and shadow
    pad = 20
    surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    
    center_x, center_y = surf.get_width() // 2, surf.get_height() // 2
    
    # Shadow
    t_shadow = title_font.render(title_text, True, (20, 60, 160))
    surf.blit(t_shadow, t_shadow.get_rect(center=(center_x + 8, center_y + 8)))
    
    # Outline
    outline_color = (40, 90, 160)
    outline_thickness = 4
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx == 0 and dy == 0: continue
            if dx*dx + dy*dy <= outline_thickness*outline_thickness + 2:
                t_outline = title_font.render(title_text, True, outline_color)
                surf.blit(t_outline, t_outline.get_rect(center=(center_x + dx, center_y + dy)))
                
    # Inner Fill
    surf.blit(base_text, base_text.get_rect(center=(center_x, center_y)))
    
    title_surface_cache = surf
    return surf

def main():
    storage.init_storage()
    settings = storage.get_settings()
    
        global player, pokemon, items, score, game_over
        running = True
    
    # Advanced States: TITLE, DIFFICULTY, TRANSITION_IN, TRANSITION_OUT, PLAYING, PAUSED, GAME_OVER
    state = "TITLE"
    next_state = ""
    difficulty = 3
    start_time = 0
    play_time = 0
    catch_timer = 0
    turn_history = []
    
    # Transition
    transition_progress = 0.0
    transition_speed = 0.02 # Adjusted for 60 FPS
    
    # Animation Ticks
    anim_tick = 0
    
    # UI Constants
    btn_start = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 50, 240, 60)
    btn_easy = pygame.Rect(WIDTH//2 - 190, HEIGHT//2 - 20, 380, 55)
    btn_med = pygame.Rect(WIDTH//2 - 190, HEIGHT//2 + 50, 380, 55)
    btn_hard = pygame.Rect(WIDTH//2 - 190, HEIGHT//2 + 120, 380, 55)
    btn_back = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 200, 300, 55)
    btn_home = pygame.Rect(WIDTH - 150, 20, 130, 50)
    
    def reset_game():
        nonlocal start_time, play_time, turn_history
        global player, pokemons, items, score, game_over
        game_over = False
        score = 0
        play_time = 0
        turn_history = []
        
        available = list(spawnable)
        random.shuffle(available)
        player = Player(available.pop())
        # AI auto-play removed
        
        pokemons = [
            Pokemon(available.pop(), "MINIMAX"),
            Pokemon(available.pop(), "ASTAR"),
            Pokemon(available.pop(), "RANDOM")
        ]
        items = [
            Item(available.pop(), "SPEED"),
            Item(available.pop(), "FREEZE")
        ]
        start_time = pygame.time.get_ticks()

    def process_turn(new_pos, p_str):
        nonlocal catch_timer, transition_progress, state, next_state, turn_history
        global player, pokemons, items, score, game_over
        
        player.prev_pos = player.pos
        player.pos = new_pos
        if player.speed_boost_turns > 0: player.speed_boost_turns -= 1
        
        turn_history.append(p_str)
        if len(turn_history) > 6: turn_history.pop(0)
        
        picked_up = [it for it in items if it.pos == player.pos]
        for it in picked_up:
            turn_history.append(f"Got {it.type_name}!")
            if it.type_name == "SPEED": player.apply_powerup("SPEED")
            elif it.type_name == "FREEZE":
                for p in pokemons: p.freeze_turns = 3
            items.remove(it)
            avail = [(dr, dc) for dr in range(ROWS) for dc in range(COLS) if grid[dr][dc] == 0 and (dr,dc) != player.pos and (dr,dc) != pokemon.pos]
            if avail: items.append(Item(random.choice(avail), random.choice(["SPEED", "FREEZE"])))
        
        caught_any = (pokemon.pos == player.pos)
        if caught_any:
            game_over = True
            state = "CATCH_ANIMATION"
            catch_timer = 0
            return
            
        current_diff = min(6, difficulty + (score // 10))
        new_poke_move = pokemon.get_move(player, grid, current_diff)
            if new_poke_move != pokemon.pos:
                pr, pc = pokemon.pos
                nr, nc = new_poke_move
                poke_str = "Pika: "
                if nr < pr: poke_str += "UP"
                elif nr > pr: poke_str += "DOWN"
                elif nc < pc: poke_str += "LEFT"
                else: poke_str += "RIGHT"
                turn_history.append(poke_str)
                if len(turn_history) > 6: turn_history.pop(0)
                if nr < pr: poke_str += "UP"
                elif nr > pr: poke_str += "DOWN"
                elif nc < pc: poke_str += "LEFT"
                else: poke_str += "RIGHT"
                turn_history.append(poke_str)
                if len(turn_history) > 6: turn_history.pop(0)
            pokemon.pos = new_poke_move
            
        caught_any_after = (pokemon.pos == player.pos)
        if caught_any_after:
            game_over = True
            state = "CATCH_ANIMATION"
            catch_timer = 0
        else:
            score += 1
            if score > 0 and score % 5 == 0:
                paths = [(r, c) for r in range(1, ROWS-1) for c in range(1, COLS-1) if grid[r][c] == 0 and (r,c) != player.pos and (r,c) != pokemon.pos and not any(it.pos ==(r,c) for it in items)]
                walls = [(r, c) for r in range(1, ROWS-1) for c in range(1, COLS-1) if grid[r][c] == 1]
                if paths and walls:
                    p1 = random.choice(paths)
                    w1 = random.choice(walls)
                    grid[p1[0]][p1[1]] = 1
                    grid[w1[0]][w1[1]] = 0
                    turn_history.append("Walls Shifted!")
                    if len(turn_history) > 6: turn_history.pop(0)

    reset_game()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
                
            if event.type == pygame.KEYDOWN:
                if state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        next_state = "TITLE"
                        state = "TRANSITION_IN"
                        transition_progress = 0.0
                elif state == "PAUSED":
                    if event.key == pygame.K_ESCAPE:
                        state = "PLAYING"
                elif state == "PLAYING" and not game_over:
                    if event.key == pygame.K_ESCAPE:
                        state = "PAUSED"
                        continue
                        
                    r, c = player.pos
                    new_pos = None
                    p_str = ""
                    if event.key == pygame.K_UP and r > 0 and grid[r-1][c] == 0:
                        new_pos = (r-1, c); p_str = "Ash: UP"
                    elif event.key == pygame.K_DOWN and r < ROWS-1 and grid[r+1][c] == 0:
                        new_pos = (r+1, c); p_str = "Ash: DOWN"
                    elif event.key == pygame.K_LEFT and c > 0 and grid[r][c-1] == 0:
                        new_pos = (r, c-1); p_str = "Ash: LEFT"
                    elif event.key == pygame.K_RIGHT and c < COLS-1 and grid[r][c+1] == 0:
                        new_pos = (r, c+1); p_str = "Ash: RIGHT"

                    if new_pos:
                        process_turn(new_pos, p_str)

                anim_tick += 1
        
        # AI auto-play removed

        # ---------------- RENDERING BASE LAYER -----------------
        screen.fill(BLACK)
        
        # We need to draw the base layer depending on state
        draw_state = state
        if state in ("TRANSITION_IN", "TRANSITION_OUT"):
            # If transitioning IN, draw current underlying state (e.g., TITLE)
            # If transitioning OUT, draw NEXT underlying state (e.g., PLAYING)
            draw_state = next_state if state == "TRANSITION_OUT" else ("TITLE" if next_state == "DIFFICULTY" else "PLAYING")
            if next_state == "GAME_OVER" and state == "TRANSITION_IN": draw_state = "PLAYING"
            if next_state == "GAME_OVER" and state == "TRANSITION_OUT": draw_state = "GAME_OVER"
            if next_state == "TITLE" and state == "TRANSITION_OUT": draw_state = "TITLE"
            if next_state == "PLAYING" and state == "TRANSITION_IN": draw_state = "DIFFICULTY"

        if draw_state == "TITLE":
            # Stripe scrolling background
            bg_color1 = (135, 206, 235) # Sky blue
            bg_color2 = (176, 226, 255)
            screen.fill(bg_color1)
            offset = (anim_tick * 2) % 40
            for x in range(-100, WIDTH+100, 40):
                pygame.draw.line(screen, bg_color2, (x + offset, 0), (x - HEIGHT + offset, HEIGHT), 20)
                
            # Floating Pokemon & Trainer
            float_ash = math.sin(anim_tick * 0.025) * 10
            float_pika = math.sin(anim_tick * 0.025 + math.pi) * 10
            
            # Additional floating characters
            float_1 = math.sin(anim_tick * 0.02) * 15
            float_2 = math.sin(anim_tick * 0.03 + 2) * 12
            float_3 = math.sin(anim_tick * 0.022 + 4) * 14
            float_4 = math.sin(anim_tick * 0.027 + 1) * 16

            if char_mander: screen.blit(pygame.transform.scale(char_mander, (180, 180)), (60, HEIGHT//2 + 20 + float_1))
            if squir_tle: screen.blit(pygame.transform.scale(squir_tle, (180, 180)), (WIDTH - 220, HEIGHT//2 + 40 + float_2))
            if bulba_saur: screen.blit(pygame.transform.scale(bulba_saur, (150, 150)), (100, HEIGHT//2 - 250 + float_3))
            if mew_two: screen.blit(pygame.transform.scale(mew_two, (220, 220)), (WIDTH - 280, HEIGHT//2 - 300 + float_4))

            if trainer_img:
                scaled_ash = pygame.transform.scale(trainer_img, (180, 180))
                screen.blit(scaled_ash, (WIDTH//2 - 220, HEIGHT//2 - 120 + float_ash))
            if pokemon_img:
                scaled_pika = pygame.transform.scale(pokemon_img, (180, 180))
                screen.blit(scaled_pika, (WIDTH//2 + 40, HEIGHT//2 - 120 + float_pika))
                
            # Bouncing Title logo
            logo_y = HEIGHT//4 + math.sin(anim_tick * 0.05) * 5
            surf = get_title_surface()
            screen.blit(surf, surf.get_rect(center=(WIDTH//2, logo_y)))
            
            # Start Button
            hover_start = btn_start.collidepoint(mouse_pos)
            c_start = (150, 255, 150) if hover_start else GREEN
            draw_button(screen, "START", large_font, c_start, btn_start, hover_start)
            
            if mouse_clicked and hover_start and state == "TITLE":
                next_state = "DIFFICULTY"
                state = "TRANSITION_IN"
                transition_progress = 0.0
                
        elif draw_state == "DIFFICULTY":
            screen.fill((50, 110, 190))
            
            # Decorative UI characters (scaled up)
            float_ui1 = math.sin(anim_tick * 0.02) * 10
            float_ui2 = math.cos(anim_tick * 0.025) * 8
            
            if char_mander: screen.blit(pygame.transform.scale(char_mander, (260, 260)), (10, HEIGHT//2 - 200 + float_ui1))
            if squir_tle: screen.blit(pygame.transform.scale(squir_tle, (260, 260)), (WIDTH - 280, HEIGHT//2 - 190 + float_ui2))
            if bulba_saur: screen.blit(pygame.transform.scale(bulba_saur, (240, 240)), (20, HEIGHT//2 + 120 + float_ui1))
            if mew_two: screen.blit(pygame.transform.scale(mew_two, (280, 280)), (WIDTH - 300, HEIGHT//2 + 90 + float_ui2))

            sub = large_font.render("Select Mode", True, WHITE)
            screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
            
            h_easy = btn_easy.collidepoint(mouse_pos)
            h_med = btn_med.collidepoint(mouse_pos)
            h_hard = btn_hard.collidepoint(mouse_pos)
            h_back = btn_back.collidepoint(mouse_pos)
            
            btn_auto = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 180, 300, 50)
            c_easy = (100, 255, 100) if h_easy else GREEN
            c_med = (255, 200, 50) if h_med else (255, 165, 0)
            c_hard = (255, 100, 100) if h_hard else RED
            c_back = (200, 200, 200) if h_back else (150, 150, 150)
            
            draw_button(screen, "EASY (1-Step AI)", font, c_easy, btn_easy, h_easy)
            draw_button(screen, "NORMAL (3-Step AI)", font, c_med, btn_med, h_med)
            draw_button(screen, "HARD (5-Step AI)", font, c_hard, btn_hard, h_hard)
            draw_button(screen, "EXIT TO HOME", font, c_back, btn_back, h_back)
            
            if mouse_clicked and state == "DIFFICULTY":
                if h_easy: difficulty = 1; next_state = "PLAYING"; state = "TRANSITION_IN"; transition_progress = 0.0
                elif h_med: difficulty = 3; next_state = "PLAYING"; state = "TRANSITION_IN"; transition_progress = 0.0
                elif h_hard: difficulty = 5; next_state = "PLAYING"; state = "TRANSITION_IN"; transition_progress = 0.0
                elif h_back: next_state = "TITLE"; state = "TRANSITION_IN"; transition_progress = 0.0
                    
        elif draw_state in ("PLAYING", "PAUSED", "CATCH_ANIMATION", "GAME_OVER"):
            if draw_state in ("PLAYING", "PAUSED") and state in ("PLAYING", "PAUSED"):
                play_time = (pygame.time.get_ticks() - start_time) // 1000
                
            draw_grid()
            
            # Draw Items
            for item in items:
                cx, cy = item.pos[1]*BLOCK_SIZE + BLOCK_SIZE//2, item.pos[0]*BLOCK_SIZE + BLOCK_SIZE//2
                ic = (100,200,250) if item.type_name == "FREEZE" else (250,200,50)
                # gentle pulse item size
                pulse = math.sin(anim_tick * 0.1) * 2
                r = int(BLOCK_SIZE//3 + pulse)
                pygame.draw.circle(screen, ic, (cx, cy), max(2, r))
                pygame.draw.circle(screen, THEMES[0]["bg"], (cx, cy), max(2, r), 2)
            
            draw_entity(player.pos, GREEN, "T", is_trainer=True, anim_tick=anim_tick)
            
            if draw_state == "CATCH_ANIMATION" or (draw_state in ("PLAYING", "PAUSED", "GAME_OVER") and game_over):
                if draw_state == "CATCH_ANIMATION":
                    catch_timer += 1
                    
                    # Classic Encounter Flash
                    if catch_timer < 20 and (catch_timer // 4) % 2 == 0:
                        screen.fill((220, 220, 230))
                        
                    shake_x = math.sin(catch_timer * 0.8) * 8 if catch_timer < 50 else 0
                    shake_y = -abs(math.sin(catch_timer * 0.2)) * 15 if catch_timer < 30 else 0
                    if catch_timer > 90:
                        storage.save_score(score, play_time, difficulty, is_caught=True)
                        next_state = "GAME_OVER"
                        state = "TRANSITION_IN"
                        transition_progress = 0.0
                else:
                    shake_x, shake_y = 0, 0
                
                # Render Pokemons (highlighting caught ones)
                if pokemon.pos == player.pos:
                    px, py = pokemon.pos[1] * BLOCK_SIZE, pokemon.pos[0] * BLOCK_SIZE
                    if pokeball_img:
                        screen.blit(pokeball_img, (px + shake_x, py + shake_y))
                    else:
                        pygame.draw.circle(screen, RED, (int(px + BLOCK_SIZE//2 + shake_x), int(py + BLOCK_SIZE//2 + shake_y)), BLOCK_SIZE//2)
                else:
                    draw_entity(pokemon.pos, RED, "P", is_pokemon=True, anim_tick=anim_tick)
            else:
                draw_entity(pokemon.pos, RED, "P", is_pokemon=True, anim_tick=anim_tick)
            
            # Fog of War Overlay
            if draw_state in ("PLAYING", "CATCH_ANIMATION"):
                fog_surf = pygame.Surface((WIDTH, HEIGHT))
                fog_surf.fill((10, 10, 15))
                cx = int(player.pos[1] * BLOCK_SIZE + BLOCK_SIZE//2)
                cy = int(player.pos[0] * BLOCK_SIZE + BLOCK_SIZE//2)
                vis_radius = BLOCK_SIZE * 3.5 if player.speed_boost_turns == 0 else BLOCK_SIZE * 4.5
                pygame.draw.circle(fog_surf, (255, 0, 255), (cx, cy), int(vis_radius))
                for it in items:
                    if it.type_name == "SPEED":
                        ix, iy = int(it.pos[1] * BLOCK_SIZE + BLOCK_SIZE//2), int(it.pos[0] * BLOCK_SIZE + BLOCK_SIZE//2)
                        pygame.draw.circle(fog_surf, (255, 0, 255), (ix, iy), int(BLOCK_SIZE * 1.5))
                fog_surf.set_colorkey((255, 0, 255))
                fog_surf.set_alpha(235)
                screen.blit(fog_surf, (0, 0))
            
            # HUD Overlay
            hud_surf = pygame.Surface((250, 200), pygame.SRCALPHA)
            hud_surf.fill((0, 0, 0, 160)) 
            screen.blit(hud_surf, (10, 10))
            
            t_score = font.render(f"Turns: {score}", True, WHITE)
            t_time = font.render(f"Time: {play_time}s", True, WHITE)
            screen.blit(t_score, (20, 15))
            screen.blit(t_time, (20, 45))
            
            for i, log_str in enumerate(turn_history):
                # Light blue for Pika, Green for Ash
                tc = (150, 200, 255) if "Pika" in log_str else (150, 255, 150)
                t_log = font.render(log_str, True, tc)
                screen.blit(t_log, (20, 80 + i * 18))
            
            h_home = btn_home.collidepoint(mouse_pos)
            c_home = (220, 100, 100) if h_home else (180, 50, 50)
            draw_button(screen, "EXIT", font, c_home, btn_home, h_home)
            
            if mouse_clicked and h_home and state in ("PLAYING", "PAUSED") and not game_over:
                storage.save_score(score, play_time, difficulty, is_caught=False)
                next_state = "TITLE"
                state = "TRANSITION_IN"
                transition_progress = 0.0
                
            if state == "PAUSED":
                panel = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 100, 300, 200)
                pygame.draw.rect(screen, (30, 30, 30, 230), panel)
                pygame.draw.rect(screen, WHITE, panel, 3)
                p_text = large_font.render("PAUSED", True, WHITE)
                screen.blit(p_text, p_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
                
                btn_res = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 40)
                btn_qt = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 40)
                hr = btn_res.collidepoint(mouse_pos)
                hq = btn_qt.collidepoint(mouse_pos)
                
                draw_button(screen, "RESUME", font, (100, 200, 100) if hr else GREEN, btn_res, hr)
                draw_button(screen, "QUIT TO MENU", font, (200, 100, 100) if hq else RED, btn_qt, hq)
                
                if mouse_clicked:
                    if hr: state = "PLAYING"
                    elif hq: 
                        storage.save_score(score, play_time, difficulty, is_caught=False)
                        next_state = "TITLE"
                        state = "TRANSITION_IN"
                        transition_progress = 0.0
            
            if draw_state == "GAME_OVER":
                panel = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
                pygame.draw.rect(screen, BLACK, panel)
                pygame.draw.rect(screen, RED, panel, 5)
                
                go_text = large_font.render("Pokémon Caught!", True, RED)
                screen.blit(go_text, go_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 45)))
                
                stars = 3 if score >= 30 else (2 if score >= 15 else 1)
                for i in range(3):
                    color = (255, 215, 0) if i < stars else (100, 100, 100)
                    points = []
                    cx, cy = WIDTH//2 - 40 + i*40, HEIGHT//2
                    for jp in range(5):
                        a = jp * 4 * math.pi / 5 - math.pi / 2
                        points.append((cx + math.cos(a)*12, cy + math.sin(a)*12))
                    pygame.draw.polygon(screen, color, points)
                
                stat_text = font.render(f"Survived {play_time}s in {score} turns", True, WHITE)
                screen.blit(stat_text, stat_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 35)))
                
                sub_text = font.render("Press SPACE to return", True, (200, 200, 200))
                screen.blit(sub_text, sub_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 75)))

        # ---------------- CLOUD TRANSITION LAYER -----------------
        if state in ("TRANSITION_IN", "TRANSITION_OUT"):
            prog = float(transition_progress) if state == "TRANSITION_IN" else (1.0 - float(transition_progress))
            cloud_x = int((WIDTH / 2) * prog)
            
            # Draw Left and Right cloud walls
            pygame.draw.rect(screen, WHITE, (0, 0, cloud_x, HEIGHT))
            pygame.draw.rect(screen, WHITE, (WIDTH - cloud_x, 0, WIDTH, HEIGHT))
            
            # Draw fluffy cloud edges
            for y in range(-20, HEIGHT+50, 40):
                offset = math.sin((y + anim_tick*0.5) * 0.05) * 10
                pygame.draw.circle(screen, WHITE, (int(cloud_x), int(y)), int(35 + offset))
                pygame.draw.circle(screen, WHITE, (int(WIDTH - cloud_x), int(y)), int(35 - offset))
            
            # Progress Logic
            transition_progress += transition_speed
            if transition_progress >= 1.0:
                if state == "TRANSITION_IN":
                    if next_state == "PLAYING": reset_game()
                    state = "TRANSITION_OUT"
                    transition_progress = 0.0
                elif state == "TRANSITION_OUT":
                    state = next_state
                    transition_progress = 0.0

        # ---------------- 90S CRT SCANLINE EFFECT -----------------
        # Draws a semi-transparent horizontal line every few pixels
        scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(scanline_surf, (0, 0, 0, 40), (0, y), (WIDTH, y), 1)
        screen.blit(scanline_surf, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

import pygame
import random
import time
import chess
import pyttsx3
import os

# Initialize pygame and sound
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // 8
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
RED = (255, 0, 0)
TEXT_COLOR = (200, 0, 0)

# Load horror sounds
def load_sound(filename):
    try:
        return pygame.mixer.Sound(filename)
    except pygame.error:
        print(f"WARNING: Sound {filename} not found.")
        return None

scream_sound = load_sound("sounds/scream.mp3")
laugh_sound = load_sound("sounds/laugh.mp3")
error_sound = load_sound("sounds/error.mp3")

# Load chess piece images
piece_images = {}
for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
    piece_images[f'w{piece}'] = pygame.image.load(f"pieces/w{piece}.png")
    piece_images[f'b{piece}'] = pygame.image.load(f"pieces/b{piece}.png")

for key in piece_images:
    piece_images[key] = pygame.transform.scale(piece_images[key], (SQUARE_SIZE, SQUARE_SIZE))

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Haunted Chess")

# Load chessboard
board = chess.Board()

# Voice engine
engine = pyttsx3.init()
engine.setProperty('rate', 100)

# Timer setup
def get_time_limit():
    font = pygame.font.Font(None, 40)
    input_text = ""
    screen.fill((0, 0, 0))
    prompt_text = font.render("Enter game duration (seconds):", True, TEXT_COLOR)
    screen.blit(prompt_text, (50, HEIGHT // 2 - 50))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return int(input_text) if input_text.isdigit() else 180
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isdigit():
                    input_text += event.unicode

        screen.fill((0, 0, 0))
        screen.blit(prompt_text, (50, HEIGHT // 2 - 50))
        user_input = font.render(input_text, True, TEXT_COLOR)
        screen.blit(user_input, (50, HEIGHT // 2))
        pygame.display.flip()

TIME_LIMIT = get_time_limit()
START_TIME = time.time()

player_turn = True
selected_piece = None

def draw_board(time_left=None):
    """Draws the chessboard and pieces."""
    screen.fill((0, 0, 0))
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_str = piece.symbol()
            color_prefix = 'w' if piece.color == chess.WHITE else 'b'
            image = piece_images.get(f"{color_prefix}{piece_str.lower()}", None)
            if image:
                col = square % 8
                row = 7 - (square // 8)
                screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    if time_left is not None:
        font = pygame.font.Font(None, 40)
        timer_text = font.render(f"Time Left: {int(time_left)}s", True, TEXT_COLOR)
        screen.blit(timer_text, (20, 20))

    pygame.display.flip()

def get_square_from_mouse(pos):
    """Converts mouse click position to chess square."""
    x, y = pos
    col = x // SQUARE_SIZE
    row = 7 - (y // SQUARE_SIZE)
    return chess.square(col, row)

def play_sound(sound):
    """Plays a sound if it exists."""
    if sound:
        sound.play()
        time.sleep(0.5)  # Small delay to ensure sound plays


def ai_move():
    """AI makes a move."""
    global player_turn
    if board.is_game_over():
        return  

    move = random.choice(list(board.legal_moves))
    board.push(move)

    if random.randint(1, 5) == 1:
        if laugh_sound: laugh_sound.play()
        engine.say("You can't win.")
        engine.runAndWait()

    player_turn = True  

def jumpscare():
    """Triggers a jumpscare effect."""
    screen.fill(RED)
    pygame.display.flip()
    if scream_sound: scream_sound.play()
    time.sleep(1)
    draw_board()

running = True

while running:
    elapsed_time = time.time() - START_TIME
    time_left = max(TIME_LIMIT - elapsed_time, 0)

    if time_left <= 0:
        engine.say("Your time is up...")
        engine.runAndWait()
        running = False
        break

    draw_board(time_left=time_left)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
            click_square = get_square_from_mouse(event.pos)
            piece = board.piece_at(click_square)

            if selected_piece is None:
                if piece and piece.color == chess.WHITE:
                    selected_piece = click_square
            else:
                move = chess.Move(selected_piece, click_square)
                if move in board.legal_moves:
                    board.push(move)  
                    selected_piece = None
                    player_turn = False  
                    if random.randint(1, 10) == 1:
                        jumpscare()
                else:
                    selected_piece = None  

    if not player_turn:  
        time.sleep(1)  
        ai_move()  

pygame.quit()

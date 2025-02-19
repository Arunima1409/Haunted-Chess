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
whisper_sound = pygame.mixer.Sound("sounds/whisper.mp3")
scream_sound = pygame.mixer.Sound("sounds/scream.mp3")
static_sound = pygame.mixer.Sound("sounds/static.mp3")
laugh_sound = pygame.mixer.Sound("sounds/laugh.mp3")
error_sound = pygame.mixer.Sound("sounds/error.mp3")

# Load chess piece images
piece_images = {}
piece_types = ['p', 'r', 'n', 'b', 'q', 'k']
for piece in piece_types:
    piece_images[f'w{piece}'] = pygame.image.load(os.path.join("pieces", f"w{piece}.png"))
    piece_images[f'b{piece}'] = pygame.image.load(os.path.join("pieces", f"b{piece}.png"))

# Resize images
for key in piece_images:
    piece_images[key] = pygame.transform.scale(piece_images[key], (SQUARE_SIZE, SQUARE_SIZE))

# Set up screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Haunted Chess")

# Load chessboard
board = chess.Board()

# Voice engine for creepy responses
engine = pyttsx3.init()
engine.setProperty('rate', 100)

# Function to get player's desired timer
def get_time_limit():
    """Ask the player to enter a time limit before the game starts."""
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 40)
    input_text = ""
    prompt_text = font.render("Enter game duration (seconds):", True, TEXT_COLOR)
    screen.blit(prompt_text, (50, HEIGHT // 2 - 50))
    pygame.display.flip()

    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return int(input_text) if input_text.isdigit() else 180  # Default 3 min
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isdigit():
                    input_text += event.unicode

        screen.fill((0, 0, 0))
        screen.blit(prompt_text, (50, HEIGHT // 2 - 50))
        user_input = font.render(input_text, True, TEXT_COLOR)
        screen.blit(user_input, (50, HEIGHT // 2))
        pygame.display.flip()

# Get user input for time limit
TIME_LIMIT = get_time_limit()
START_TIME = time.time()

def creepy_voice(text):
    """AI whispers creepy messages."""
    engine.say(text)
    engine.runAndWait()

def draw_board(creepy_message=None, time_left=None):
    """Draws the chessboard, pieces, and optional horror messages."""
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draw pieces
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

    # Display timer
    if time_left is not None:
        font = pygame.font.Font(None, 40)
        timer_text = font.render(f"Time Left: {int(time_left)}s", True, TEXT_COLOR)
        screen.blit(timer_text, (20, 20))

    # Display horror text if any
    if creepy_message:
        font = pygame.font.Font(None, 40)
        text = font.render(creepy_message, True, TEXT_COLOR)
        screen.blit(text, (random.randint(100, 300), random.randint(100, 500)))

    pygame.display.flip()

def ai_move():
    """AI makes a move, sometimes cheating."""
    global board, player_turn

    if random.randint(1, 3) == 1:  # 33% chance of cheating
        if board.legal_moves:
            move = random.choice(list(board.legal_moves))
            board.push(move)
        else:
            if board.move_stack:
                board.pop()  # AI resurrects a piece (cheating)

        laugh_sound.play()
        creepy_message = "I changed the rules..."
        creepy_voice(creepy_message)
        draw_board(creepy_message)
        time.sleep(1)
    else:
        if board.legal_moves:
            board.push(random.choice(list(board.legal_moves)))

    player_turn = True  # Give turn back to player

def glitch_effect():
    """Creates a quick glitch effect."""
    sound_choice = random.choice([whisper_sound, scream_sound, static_sound])
    sound_choice.play()
    
    for _ in range(3):
        screen.fill(RED)
        pygame.display.flip()
        time.sleep(0.1)
        draw_board("ERROR 666")
        pygame.display.flip()
        time.sleep(0.1)

def fake_crash():
    """Fakes a game crash with an error message."""
    error_sound.play()
    
    messages = [
        "System Error: Chess AI has taken over.",
        "Fatal Error: Unknown entity detected.",
        "Game Over? No. It's just beginning...",
        "Your system is compromised.",
        "WARNING: You are being watched..."
    ]
    creepy_voice(random.choice(messages))

    font = pygame.font.Font(None, 50)
    text = font.render("ERROR: SYSTEM OVERRIDE", True, (255, 0, 0))
    screen.blit(text, (WIDTH//4, HEIGHT//2))
    pygame.display.flip()
    time.sleep(3)

    pygame.quit()
    exit()

def time_up():
    """Ends the game when time runs out."""
    glitch_effect()
    creepy_voice("Your time is up... Now it's my turn.")
    fake_crash()

selected_piece = None  
player_turn = True  

def get_square_from_mouse(pos):
    """Convert mouse click position to chess square."""
    x, y = pos
    col = x // SQUARE_SIZE
    row = 7 - (y // SQUARE_SIZE)
    return chess.square(col, row)

running = True

while running:
    screen.fill((0, 0, 0))

    elapsed_time = time.time() - START_TIME
    time_left = max(TIME_LIMIT - elapsed_time, 0)

    if time_left <= 0:
        time_up()  

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

                    if random.randint(1, 3) == 1:
                        glitch_effect()

                    ai_move()

                else:
                    selected_piece = None
                    if random.randint(1, 6) == 1:  
                        fake_crash()

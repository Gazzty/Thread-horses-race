import pygame
import time
import threading
import random
from PIL import Image

# --- Configuración ---
amount_horses = 5
WIDTH, HEIGHT = 1000, 600
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)

top_margin = 20
bottom_margin = 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HORSE RACE")
font = pygame.font.SysFont("Courier", 20)
clock = pygame.time.Clock()

# --- Configuración de la carrera ---
finish_line = 20
step_size = 25
start_x = 100
race_threads = []

# --- Función para cargar frames del GIF ---
def load_gif_frames(filename, scale):
    from PIL import Image
    pil_img = Image.open(filename)
    frames = []
    try:
        while True:
            frame = pil_img.convert("RGBA")
            pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
            pygame_frame = pygame.transform.scale(pygame_frame, scale)
            frames.append(pygame_frame)
            pil_img.seek(pil_img.tell() + 1)
    except EOFError:
        pass
    return frames

# --- Calcular espacio por caballo ---
space_per_horse = (HEIGHT - top_margin - bottom_margin) / amount_horses
horse_height = int(space_per_horse * 0.8)  # 80% del espacio, deja margen
horse_width = int(horse_height * (200/150))  # mantener proporción original (200x150)

# Cargar frames del gif escalados
horse_frames = load_gif_frames("uma-musume-special-week.gif", scale=(horse_width, horse_height))
frame_count = len(horse_frames)
frame_duration = 0.1


class Horse:
    def __init__(self, name, y):
        self.name = name
        self.position = 0
        self.y = y
        self.frame_index = 0
        self.last_frame_time = time.time()

    def inc_position(self):
        self.position += 1

    def race(self):
        while self.position < finish_line:
            self.inc_position()
            if not self.position >= finish_line:
                time.sleep(random.uniform(.1, 1))
        finish_race(self.name)

    def draw(self, surface):
        offset_x = start_x + self.position * step_size

        # Animación por frames
        now = time.time()
        if now - self.last_frame_time > frame_duration:
            self.frame_index = (self.frame_index + 1) % frame_count
            self.last_frame_time = now

        surface.blit(horse_frames[self.frame_index], (offset_x, self.y))


# --- Inicializar caballos ---
horses = []
for i in range(amount_horses):
    horse_y = top_margin + i * space_per_horse
    horses.append(Horse(f"H{i+1}", horse_y))

winner = None
winner_lock = threading.Lock()
running = True
start_time = time.perf_counter()


def finish_race(name):
    finish_time = time.perf_counter()
    global winner
    with winner_lock:
        if winner is None:
            winner = name
            print(f"Winner is: {name}!!!")
            print(f"Time: {round(finish_time - start_time, 2)} seconds")


# --- Arrancar hilos ---
for horse in horses:
    race_thread = threading.Thread(target=horse.race)
    race_thread.start()
    race_threads.append(race_thread)


# --- Loop principal ---
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Líneas de salida y meta
    start_line_x = start_x
    finish_line_x = start_x + (finish_line) * step_size + horse_width - 20

    pygame.draw.line(screen, GREEN, (start_line_x, 0), (start_line_x, HEIGHT), 4)
    pygame.draw.line(screen, RED, (finish_line_x, 0), (finish_line_x, HEIGHT), 4)

    # Dibujar caballos
    for horse in horses:
        horse.draw(screen)

    # Mostrar ganador
    if winner:
        text = font.render(f"Winner: {winner}", True, YELLOW)
        screen.blit(text, (WIDTH // 3, HEIGHT - 40))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
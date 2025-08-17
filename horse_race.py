import pygame
import time
import threading
import random

# How many horses do you want to race?
# NOTE: with more than 10 horses the visuals are not so good
amount_horses = 7

# --- Pygame settings ---
WIDTH, HEIGHT = 1000, 600
FPS = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
top_margin = 20
bottom_margin = 20
available_height = HEIGHT - top_margin - bottom_margin
space_per_horse = available_height / amount_horses

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ASCII HORSE RACE")
font = pygame.font.SysFont("Courier", 20)  # monospace font
clock = pygame.time.Clock()

# --- Race settings ---
finish_line = 20            # number of steps
step_size = 25              # pixels per step
start_x = 100               # where horses start
race_threads = []


# ASCII horse art (multiline)
HORSE_ART = [
    "            .''",
    "  ._.-.___.' (`\\",
    " //(        ( `' ",
    "'/ )\\ ).__. )   ",
    "' <' `\\ ._/'\\   ",
    "   `   \\     \\  ",
]
# get horse width (in pixels)
horse_width = max([font.size(line)[0] for line in HORSE_ART])


class Horse:
    def __init__(self, name, y):
        self.name = name
        self.position = 0
        self.y = y

    def inc_position(self):
        self.position += 1

    def race(self):
        while self.position < finish_line:
            self.inc_position()
            if not self.position >= finish_line:
                time.sleep(random.uniform(.1, 1))
        finish_race(self.name)

    def draw(self, surface):
        # Draw ASCII horse shifted by position
        offset_x = start_x + self.position * step_size
        for i, line in enumerate(HORSE_ART):
            text = font.render(line, True, WHITE)
            surface.blit(text, (offset_x, self.y + i * 20))


# --- Horses setup ---
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


# --- Start race threads ---
for horse in horses:
    race_thread = threading.Thread(target=horse.race)
    race_thread.start()
    race_threads.append(race_thread)


# --- Main loop ---
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Draw start and finish lines ---
    start_line_x = start_x
    finish_line_x = start_x + (finish_line) * step_size + horse_width - 20

    pygame.draw.line(screen, GREEN, (start_line_x, 0), (start_line_x, HEIGHT), 4)
    pygame.draw.line(screen, RED, (finish_line_x, 0), (finish_line_x, HEIGHT), 4)

    # Draw horses
    for horse in horses:
        horse.draw(screen)

    # Show winner
    if winner:
        text = font.render(f"Winner: {winner}", True, YELLOW)
        screen.blit(text, (WIDTH // 3, HEIGHT - 40))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

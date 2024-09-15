import random

import pygame

WALL = "#"
EMPTY = " "
PATH = "."
START = "S"
END = "E"

HEIGHT, WIDTH = 59, 59
CELL_SIZE = 10
WINDOW_HEIGHT = HEIGHT * CELL_SIZE
WINDOW_WIDTH = WIDTH * CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Maze Generator")


def draw_maze(maze):
    for i in range(HEIGHT):
        for j in range(WIDTH):
            color = RED
            if maze[i][j] == WALL:
                color = BLACK
            elif maze[i][j] == EMPTY:
                color = WHITE
            pygame.draw.rect(screen, color, pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def random_directions():
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    random.shuffle(directions)
    return directions


def generate_maze_path(maze, x, y):
    maze[x][y] = EMPTY
    for dx, dy in random_directions():
        if 1 <= x + 2 * dx < HEIGHT - 1 and 1 <= y + 2 * dy < WIDTH - 1 and maze[x + 2 * dx][y + 2 * dy] == WALL:
            maze[x + dx][y + dy] = EMPTY
            generate_maze_path(maze, x + 2 * dx, y + 2 * dy)


def find_path(maze, start_x, start_y):
    clear_path(maze)
    stack = [(start_x, start_y)]
    visited = set()

    while stack:
        x, y = stack.pop()

        if (x, y) in visited:
            continue

        visited.add((x, y))

        if maze[x][y] == END:
            return True

        if maze[x][y] != START:
            maze[x][y] = PATH

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx < HEIGHT - 1 and 1 <= ny < WIDTH - 1 and maze[nx][ny] in [EMPTY, END] and (
                    nx, ny) not in visited:
                stack.append((nx, ny))

    return False


def clear_path(maze):
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if maze[i][j] == PATH:
                maze[i][j] = EMPTY


def create_start_end(maze):
    maze[1][1] = START
    maze[-2][-2] = END


def create_new_maze():
    maze = [[WALL for _ in range(WIDTH)] for _ in range(HEIGHT)]
    generate_maze_path(maze, 1, 1)
    create_start_end(maze)
    return maze


maze = create_new_maze()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                maze = create_new_maze()
            if event.key == pygame.K_SPACE:
                find_path(maze, 1, 1)

    screen.fill(BLACK)
    draw_maze(maze)
    pygame.display.flip()

pygame.quit()

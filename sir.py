import random

import numpy as np
import pygame

# Constants
GRID_SIZE = 200
CELL_SIZE = 3
WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE

# Pygame Colors
EMPTY = (20, 20, 20)
SUSCEPTIBLE = (200, 200, 200)
INFECTED = (200, 10, 10)
RECOVERED = (10, 200, 10)


class Entity:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def tick(self, grid):
        pass


class Empty(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, EMPTY)


class Human(Entity):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)

    def random_move(self, grid):
        if random.random() < 0.5:
            for new_x, new_y in self.adjacent_cells():
                if isinstance(grid[new_x, new_y], Empty):
                    self.move(grid, new_x, new_y)
                    break

    def move(self, grid, new_x, new_y):
        grid[new_x, new_y] = self
        grid[self.x, self.y] = Empty(self.x, self.y)
        self.x, self.y = new_x, new_y

    def adjacent_cells(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            yield (self.x + dx) % GRID_SIZE, (self.y + dy) % GRID_SIZE

    def take_action(self, grid):
        pass

    def tick(self, grid):
        self.random_move(grid)
        self.take_action(grid)


class Susceptible(Human):
    def __init__(self, x, y):
        super().__init__(x, y, SUSCEPTIBLE)


class Infected(Human):
    def __init__(self, x, y):
        super().__init__(x, y, INFECTED)
        self.duration = 100

    def take_action(self, grid):
        self.attempt_die(grid)
        self.infect(grid)
        self.recover(grid)

    def recover(self, grid):
        self.duration -= 1
        if self.duration <= 0:
            grid[self.x, self.y] = Recovered(self.x, self.y)

    def infect(self, grid):
        for new_x, new_y in self.adjacent_cells():
            if isinstance(grid[new_x, new_y], Susceptible):
                grid[new_x, new_y] = Infected(new_x, new_y)

    def attempt_die(self, grid):
        if random.random() <= 0.01:
            grid[self.x, self.y] = Empty(self.x, self.y)


class Recovered(Human):
    def __init__(self, x, y):
        super().__init__(x, y, RECOVERED)
        self.duration = 50

    def take_action(self, grid):
        self.duration -= 1
        if self.duration <= 0:
            grid[self.x, self.y] = Susceptible(self.x, self.y)


class Simulation:
    def __init__(self, params):
        self.params = params
        self.grid = np.array([[Empty(i, j) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)])
        self.populate()

    def populate(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rnd = random.random()
                if rnd < 0.07:
                    self.grid[i, j] = Susceptible(i, j)
                elif rnd < 0.071:
                    self.grid[i, j] = Infected(i, j)
        # self.grid[GRID_SIZE//2][GRID_SIZE//2] = Infected(GRID_SIZE//2, GRID_SIZE//2)

    def tick(self):
        for row in self.grid:
            for entity in row:
                entity.tick(self.grid)


class App:
    def __init__(self, simulation):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SIR Simulation")
        self.simulation = simulation
        self.clock = pygame.time.Clock()
        self.continuous_mode = False

    def render(self):
        self.screen.fill(EMPTY)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                entity = self.simulation.grid[i, j]
                pygame.draw.rect(self.screen, entity.color,
                                 pygame.Rect(i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.simulation.tick()
                    elif event.key == pygame.K_RETURN:
                        self.continuous_mode = not self.continuous_mode

            if self.continuous_mode:
                self.simulation.tick()

            self.render()
            self.clock.tick(10)

        pygame.quit()


if __name__ == "__main__":
    simulation = Simulation({})
    app = App(simulation)
    app.run()

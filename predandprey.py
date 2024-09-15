import random

import matplotlib.pyplot as plt
import numpy as np
import pygame

# Constants
GRID_SIZE = 100
CELL_SIZE = 6
WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE

# Pygame Colors
EMPTY = (65, 25, 0)
GREEN = (100, 170, 0)
SHEEP = (220, 200, 200)
WOLF = (200, 0, 0)


class Entity:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def tick(self, grid, params):
        pass


class Empty(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, EMPTY)

    def tick(self, grid, params):
        if random.random() < params["grass_growth_rate"]:
            grid[self.x, self.y] = Grass(self.x, self.y)


class Grass(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)


class Animal(Entity):
    def __init__(self, x, y, hunger, max_hunger, eats_cls, reproduction_rate, color):
        super().__init__(x, y, color)
        self.hunger = hunger
        self.max_hunger = max_hunger
        self.eats_cls = eats_cls
        self.reproduction_rate = reproduction_rate

    def random_move(self, grid):
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

    def attempt_eat(self, grid):
        for new_x, new_y in self.adjacent_cells():
            if isinstance(grid[new_x, new_y], self.eats_cls):
                self.hunger = 0
                self.move(grid, new_x, new_y)
                return True
        return False

    def reproduce(self, grid):
        if random.random() < self.reproduction_rate:
            for new_x, new_y in self.adjacent_cells():
                if isinstance(grid[new_x, new_y], Empty):
                    grid[new_x, new_y] = self.create_child(new_x, new_y)
                    break

    def create_child(self, x, y):
        raise NotImplementedError()

    def increase_hunger(self, grid):
        self.hunger += 1
        if self.hunger >= self.max_hunger:
            grid[self.x, self.y] = Empty(self.x, self.y)

    def tick(self, grid, params):
        if not self.attempt_eat(grid):
            self.random_move(grid)
        self.reproduce(grid)
        self.increase_hunger(grid)


class Sheep(Animal):
    def __init__(self, x, y, params):
        super().__init__(x, y, 0, params["sheep_max_hunger"], Grass, params["sheep_reproduction_rate"], SHEEP)
        self.params = params

    def create_child(self, x, y):
        return Sheep(x, y, self.params)


class Wolf(Animal):
    def __init__(self, x, y, params):
        super().__init__(x, y, 0, params["wolf_max_hunger"], Sheep, params["wolf_reproduction_rate"], WOLF)
        self.params = params

    def create_child(self, x, y):
        return Wolf(x, y, self.params)


class Simulation:
    def __init__(self, params):
        self.params = params
        self.grid = np.array([[Empty(i, j) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)])
        self.populate()
        self.sheep_population_history = []
        self.wolf_population_history = []

    def populate(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rnd = random.random()
                if rnd < 0.1:
                    self.grid[i, j] = Grass(i, j)
                elif rnd < 0.18:
                    self.grid[i, j] = Sheep(i, j, self.params)
                elif rnd < 0.19:
                    self.grid[i, j] = Wolf(i, j, self.params)

    def tick(self):
        for row in self.grid:
            for entity in row:
                entity.tick(self.grid, self.params)
        self.record_population()

    def record_population(self):
        sheep_count = sum(isinstance(entity, Sheep) for row in self.grid for entity in row)
        wolf_count = sum(isinstance(entity, Wolf) for row in self.grid for entity in row)
        self.sheep_population_history.append(sheep_count)
        self.wolf_population_history.append(wolf_count)

    def has_both_species(self):
        sheep_present = any(isinstance(entity, Sheep) for row in self.grid for entity in row)
        wolf_present = any(isinstance(entity, Wolf) for row in self.grid for entity in row)
        return sheep_present and wolf_present

    def plot_population(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.sheep_population_history, label='Sheep Population', color='grey')
        plt.plot(self.wolf_population_history, label='Wolf Population', color='red')
        plt.xlabel('Time Step')
        plt.ylabel('Population')
        plt.title('Population Over Time')
        plt.legend()
        plt.grid(True)
        plt.show()


class App:
    def __init__(self, simulation):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Animal Simulation")
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
                    elif event.key == pygame.K_p:
                        self.simulation.plot_population()

            if self.continuous_mode:
                self.simulation.tick()

            self.render()
            self.clock.tick(10)

        pygame.quit()


if __name__ == "__main__":
    simulation = Simulation({'sheep_max_hunger': 44,
                             'wolf_max_hunger': 35,
                             'sheep_reproduction_rate': 0.051,
                             'wolf_reproduction_rate': 0.017,
                             'grass_growth_rate': 0.013})
    app = App(simulation)
    app.run()

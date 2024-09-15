import random

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
NUM_BOIDS = 80
MAX_SPEED = 2
NEIGHBOR_RADIUS = 60
ALIGNMENT_FACTOR = 0.05
COHESION_FACTOR = 0.05
SEPARATION_FACTOR = 0.1
SEPARATION_DISTANCE = 20
BOUNDARY_AVOIDANCE_DISTANCE = 10
BOUNDARY_AVOIDANCE_FACTOR = 0.5


class Boid:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.velocity.scale_to_length(MAX_SPEED)

    def update(self):
        self.position += self.velocity

    def apply_behaviors(self, boids):
        alignment = self.align(boids)
        cohesion = self.cohere(boids)
        separation = self.separate(boids)
        boundary_avoidance = self.avoid_boundaries()

        self.velocity += alignment + cohesion + separation + boundary_avoidance
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)

    def align(self, boids):
        steering = pygame.Vector2(0, 0)
        total = 0
        avg_vector = pygame.Vector2(0, 0)
        for other in boids:
            if other != self and self.position.distance_to(other.position) < NEIGHBOR_RADIUS:
                avg_vector += other.velocity
                total += 1
        if total > 0:
            avg_vector /= total
            avg_vector.scale_to_length(MAX_SPEED)
            steering = avg_vector - self.velocity
        return steering * ALIGNMENT_FACTOR

    def cohere(self, boids):
        steering = pygame.Vector2(0, 0)
        total = 0
        center_of_mass = pygame.Vector2(0, 0)
        for other in boids:
            if other != self and self.position.distance_to(other.position) < NEIGHBOR_RADIUS:
                center_of_mass += other.position
                total += 1
        if total > 0:
            center_of_mass /= total
            direction_to_com = center_of_mass - self.position
            direction_to_com.scale_to_length(MAX_SPEED)
            steering = direction_to_com - self.velocity
        return steering * COHESION_FACTOR

    def separate(self, boids):
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            distance = self.position.distance_to(other.position)
            if other != self and distance < SEPARATION_DISTANCE:
                diff = self.position - other.position
                diff /= distance
                steering += diff
                total += 1
        if total > 0:
            steering /= total
        if steering.length() > 0:
            steering.scale_to_length(MAX_SPEED)
            steering = steering - self.velocity
        return steering * SEPARATION_FACTOR

    def avoid_boundaries(self):
        steering = pygame.Vector2(0, 0)

        if self.position.x < BOUNDARY_AVOIDANCE_DISTANCE:
            steering.x = MAX_SPEED
        elif self.position.x > SCREEN_WIDTH - BOUNDARY_AVOIDANCE_DISTANCE:
            steering.x = -MAX_SPEED

        if self.position.y < BOUNDARY_AVOIDANCE_DISTANCE:
            steering.y = MAX_SPEED
        elif self.position.y > SCREEN_HEIGHT - BOUNDARY_AVOIDANCE_DISTANCE:
            steering.y = -MAX_SPEED

        if steering.length() > 0:
            steering.scale_to_length(MAX_SPEED)
            steering -= self.velocity
        return steering * BOUNDARY_AVOIDANCE_FACTOR


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Boids Simulation")
    clock = pygame.time.Clock()

    boids = [Boid(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(NUM_BOIDS)]

    running = True
    while running:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for boid in boids:
            boid.apply_behaviors(boids)
            boid.update()
            pygame.draw.circle(screen, (255, 255, 255), (int(boid.position.x), int(boid.position.y)), 5)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

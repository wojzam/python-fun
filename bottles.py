import colorsys
import random
import sys

import pygame

pygame.init()

WIDTH, HEIGHT = 1200, 600
BACKGROUND = (5, 5, 5)
WHITE = (255, 255, 255)
BOTTLE_COLOR = (100, 100, 100)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)

MAX_CAPACITY = 4
ROW_CAPACITY = 10
BOTTLE_WIDTH = 60
BOTTLE_HEIGHT = 200
BOTTLE_SPACING = 40
BOTTLE_TOP_MARGIN = 50
BOTTLE_LEFT_MARGIN = 100
FLUID_HEIGHT = BOTTLE_HEIGHT // (MAX_CAPACITY + 1)
FLUID_MARGIN = 5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fluid sort")


def generate_colors(n):
    return [tuple(int(c * 255) for c in colorsys.hls_to_rgb(i / n,
                                                            0.4 if i % 2 else 0.8,
                                                            0.8 if i % 2 else 1)) for i in range(n)]


FLUID_COLORS = generate_colors(18)
INITIAL_CONTENT = [[FLUID_COLORS[i] for _ in range(MAX_CAPACITY)] for i in range(len(FLUID_COLORS))] + [[], []]


class Bottle:
    def __init__(self, index, content):
        row = 1 if index < ROW_CAPACITY else 2
        x = BOTTLE_LEFT_MARGIN + (index % ROW_CAPACITY) * (BOTTLE_WIDTH + BOTTLE_SPACING)
        y = HEIGHT - row * (BOTTLE_HEIGHT + BOTTLE_TOP_MARGIN)
        self.rect = pygame.Rect(x, y, BOTTLE_WIDTH, BOTTLE_HEIGHT)
        self.color = BOTTLE_COLOR
        self.selected = False
        self.content = content.copy()

    def pour(self, other):
        if not self.can_pour(other):
            return False

        top = self.content.pop()
        other.content.append(top)
        while self.content and self.content[-1] == top and len(other.content) < MAX_CAPACITY:
            other.content.append(self.content.pop())
        return True

    def can_pour(self, other):
        return self != other and self.content and len(other.content) < MAX_CAPACITY and (
                not other.content or other.content[-1] == self.content[-1])

    def force_pour(self, other):
        if self != other and self.content and len(other.content) < MAX_CAPACITY:
            other.content.append(self.content.pop())

    def reversible_pour(self, other):
        c1, c2 = self.content.copy(), other.content.copy()
        self.pour(other)
        return c1, c2

    def has_different_fluids(self):
        if len(self.content) < 2:
            return False
        for i in range(len(self.content[:-1])):
            if self.content[i] != self.content[i + 1]:
                return True
        return False

    def draw(self):
        raise_height = 20 if self.selected else 0
        bottle_top_y = self.rect.y - raise_height
        top_left = (self.rect.x - 10, bottle_top_y)
        top_right = (self.rect.x + BOTTLE_WIDTH + 10, bottle_top_y)
        pygame.draw.polygon(screen, self.color, [top_left, top_right, (self.rect.x + BOTTLE_WIDTH, bottle_top_y + 30),
                                                 (self.rect.x, bottle_top_y + 30)])
        pygame.draw.rect(screen, self.color, pygame.Rect(self.rect.x, bottle_top_y, BOTTLE_WIDTH, BOTTLE_HEIGHT),
                         border_radius=20)

        for i, fluid in enumerate(self.content):
            fluid_rect = pygame.Rect(self.rect.x + FLUID_MARGIN, self.rect.y + BOTTLE_HEIGHT - (
                    i + 1) * FLUID_HEIGHT - 2 * FLUID_MARGIN - raise_height,
                                     BOTTLE_WIDTH - FLUID_MARGIN * 2, FLUID_HEIGHT)
            pygame.draw.rect(screen, fluid, fluid_rect, border_radius=10)


class Puzzle:
    def __init__(self, initial_content):
        self.bottles = [Bottle(i, content) for i, content in enumerate(initial_content)]
        self.shuffle_bottles()

    def shuffle_bottles(self):
        for _ in range(1000):
            a, b = random.sample(self.bottles, 2)
            a.force_pour(b)

        while self.bottles[-1].content or self.bottles[-2].content:
            for bottle in self.bottles[:-2]:
                self.bottles[-1].force_pour(bottle)
                self.bottles[-2].force_pour(bottle)

    def is_solved(self):
        for bottle in self.bottles:
            if bottle.content and (len(bottle.content) != MAX_CAPACITY or not all(
                    color == bottle.content[0] for color in bottle.content)):
                return False
        return True

    def perform_hint_move(self):
        states = {hash(self)}

        def get_possible_moves(bottles):
            moves = []
            for i, bottle in enumerate(bottles):
                if bottle.content:
                    for j, other_bottle in enumerate(bottles):
                        if bottle.can_pour(other_bottle):
                            moves.append((bottle, other_bottle))
            random.shuffle(moves)
            return moves

        def solve_puzzle(first_move=None, level=0):
            solution_moves = []
            for move in get_possible_moves(self.bottles):
                if level == 0:
                    first_move = move

                c1, c2 = move[0].reversible_pour(move[1])

                if self.is_solved():
                    move[0].content, move[1].content = c1, c2
                    return first_move, level

                state_hash = hash(self)
                if state_hash not in states:
                    states.add(state_hash)
                    result = solve_puzzle(first_move, level + 1)

                    if result:
                        solution_moves.append(result)

                move[0].content, move[1].content = c1, c2
            if not solution_moves:
                return None
            else:
                return min(solution_moves, key=lambda x: x[1])

        result = solve_puzzle()
        if result:
            result[0][0].pour(result[0][1])

    def reset(self):
        self.__init__(INITIAL_CONTENT)

    def save_state(self):
        return [bottle.content.copy() for bottle in self.bottles]

    def load_state(self, saved_state):
        for i, content in enumerate(saved_state):
            self.bottles[i].content = content.copy()

    def __hash__(self):
        bottle_states = [tuple(bottle.content) for bottle in self.bottles]
        sorted_states = tuple(sorted(bottle_states))
        return hash(sorted_states)


def draw_button(button_rect, text, font):
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, button_rect)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (button_rect.x + (button_rect.width - text_surface.get_width()) // 2,
                               button_rect.y + (button_rect.height - text_surface.get_height()) // 2))


def main():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    puzzle = Puzzle(INITIAL_CONTENT)

    move_history = []
    prev_selected = None

    new_game_button_rect = pygame.Rect(340, 20, 150, 50)
    undo_button_rect = pygame.Rect(510, 20, 120, 50)
    hint_button_rect = pygame.Rect(650, 20, 120, 50)

    while True:
        screen.fill(BACKGROUND)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if new_game_button_rect.collidepoint(mouse_pos):
                    puzzle.reset()
                    move_history = []

                if undo_button_rect.collidepoint(mouse_pos) and move_history:
                    last_state = move_history.pop()
                    puzzle.load_state(last_state)
                    if prev_selected:
                        prev_selected.selected = False
                        prev_selected = None

                if hint_button_rect.collidepoint(mouse_pos):
                    move_history.append(puzzle.save_state())
                    puzzle.perform_hint_move()

                for bottle in puzzle.bottles:
                    if bottle.rect.collidepoint(mouse_pos):
                        if prev_selected:
                            if prev_selected == bottle:
                                prev_selected.selected = False
                                prev_selected = None
                            else:
                                move_history.append(puzzle.save_state())
                                if prev_selected.pour(bottle):
                                    prev_selected.selected = False
                                    prev_selected = None
                                else:
                                    move_history.pop()
                        elif bottle.content:
                            prev_selected = bottle
                            bottle.selected = True

        for bottle in puzzle.bottles:
            bottle.draw()

        draw_button(new_game_button_rect, "New Game", font)
        draw_button(undo_button_rect, "Undo", font)
        draw_button(hint_button_rect, "Hint", font)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

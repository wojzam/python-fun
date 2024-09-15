import sys

import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong Game')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

ball_speed_x = 4
ball_speed_y = 4
player_speed = 6

PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_WIDTH, BALL_HEIGHT = 15, 15

player1_x, player1_y = 30, (HEIGHT // 2) - (PADDLE_HEIGHT // 2)
player2_x, player2_y = WIDTH - 30 - PADDLE_WIDTH, (HEIGHT // 2) - (PADDLE_HEIGHT // 2)
ball_x, ball_y = WIDTH // 2 - BALL_WIDTH // 2, HEIGHT // 2 - BALL_HEIGHT // 2

player1_score, player2_score = 0, 0
font = pygame.font.Font(None, 74)


def draw_elements():
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (player1_x, player1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, WHITE, (player2_x, player2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, BALL_WIDTH, BALL_HEIGHT))
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    score1 = font.render(str(player1_score), True, WHITE)
    score2 = font.render(str(player2_score), True, WHITE)
    screen.blit(score1, (WIDTH // 4, 10))
    screen.blit(score2, (WIDTH * 3 // 4 - 30, 10))
    pygame.display.flip()


def game_loop():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, player1_y, player2_y, player1_score, player2_score

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and player1_y > 0:
            player1_y -= player_speed
        if keys[pygame.K_s] and player1_y < HEIGHT - PADDLE_HEIGHT:
            player1_y += player_speed

        if keys[pygame.K_UP] and player2_y > 0:
            player2_y -= player_speed
        if keys[pygame.K_DOWN] and player2_y < HEIGHT - PADDLE_HEIGHT:
            player2_y += player_speed

        ball_x += ball_speed_x
        ball_y += ball_speed_y

        if ball_y <= 0 or ball_y >= HEIGHT - BALL_HEIGHT:
            ball_speed_y *= -1

        if ball_x <= player1_x + PADDLE_WIDTH and player1_y < ball_y < player1_y + PADDLE_HEIGHT:
            ball_speed_x *= -1
        if ball_x >= player2_x - BALL_WIDTH and player2_y < ball_y < player2_y + PADDLE_HEIGHT:
            ball_speed_x *= -1

        if ball_x <= 0:
            player2_score += 1
            ball_x, ball_y = WIDTH // 2 - BALL_WIDTH // 2, HEIGHT // 2 - BALL_HEIGHT // 2
            ball_speed_x *= -1
        if ball_x >= WIDTH:
            player1_score += 1
            ball_x, ball_y = WIDTH // 2 - BALL_WIDTH // 2, HEIGHT // 2 - BALL_HEIGHT // 2
            ball_speed_x *= -1

        draw_elements()

        clock.tick(60)


if __name__ == "__main__":
    game_loop()

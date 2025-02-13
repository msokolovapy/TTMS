import pygame
import sys

pygame.init()

# Screen dimensions
screen_width = 200
screen_height = 150
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

pygame.display.set_caption('Table Tennis Animation')
clock = pygame.time.Clock()

player1_image = pygame.image.load('Minecraft_human_original_transp.png').convert_alpha()
player2_image = pygame.image.load('Minecraft_human_2.png').convert_alpha()

player1_image = pygame.transform.scale(player1_image, (100, 70))

# Player settings
player_width = 20
player_height = 100

# Player positions
player1_x = 5
player1_y = (screen_height // 2) - (player_height // 2)
player2_x = screen_width - 5 - player_width
player2_y = (screen_height // 2) - (player_height // 2)

# Ball settings
ball_radius = 5
ball_x = screen_width // 2
ball_y = screen_height // 2
ball_speed_x = 2
ball_speed_y = 2



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] and player1_y > 0:
        player1_y -= 0.5
    if keys[pygame.K_s] and player1_y < screen_height - player_height:
        player1_y +=0.5
    if keys[pygame.K_UP] and player2_y > 0:
        player2_y -= 0.5
    if keys[pygame.K_DOWN] and player2_y < screen_height - player_height:
        player2_y += 0.5

    # Move the ball
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Ball collision with top and bottom walls
    if ball_y - ball_radius <= 0 or ball_y + ball_radius >= screen_height:
        ball_speed_y = -ball_speed_y

    # Ball collision with paddles
    if (player1_x + player_width >= ball_x - ball_radius and
            player1_y <= ball_y <= player1_y + player_height):
        ball_speed_x = -ball_speed_x

    if (player2_x <= ball_x + ball_radius and
            player2_y <= ball_y <= player2_y + player_height):
        ball_speed_x = -ball_speed_x

    # Fill the screen with white
    screen.fill(white)

    # Draw the players and the ball
    screen.blit(player1_image, (player1_x, player1_y))
    screen.blit(player2_image, (player2_x, player2_y))
    pygame.draw.circle(screen, black, (ball_x, ball_y), ball_radius)

    pygame.display.flip()
    clock.tick(60)


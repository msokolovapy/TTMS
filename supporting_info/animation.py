import pygame
import sys
import random

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

# Player settings
player_width = 10
player_height = 40

# Player positions
player1_x = 10  # Bottom-left corner
player1_y = screen_height - player_height

player2_x = screen_width - player_width - 10  # Top-right corner
player2_y = 0

# Ball settings
ball_radius = 7
ball_x = screen_width // 2
ball_y = screen_height // 2
ball_speed_x = 2  # Slower speed
ball_speed_y = 2

# Movement speeds
player1_speed = 2
player2_speed = 2

# Ball direction flags
ball_towards_player1 = False
ball_towards_player2 = True

# Variables to control random paddle movement behavior
random_move_delay = 30  # Change direction after 30 frames
player1_random_timer = random_move_delay
player2_random_timer = random_move_delay
player1_random_direction = random.choice([-1, 1])
player2_random_direction = random.choice([-1, 1])

def move_paddle_towards_ball(player_y, player_height, ball_y, speed):
    # Move the paddle towards the ball, but with a delay to mimic human reaction
    if player_y + player_height // 2 < ball_y - 5:
        player_y += speed
    elif player_y + player_height // 2 > ball_y + 5:
        player_y -= speed
    return player_y


def smooth_random_paddle_movement(player_y, player_height, screen_height, speed, timer, direction):
    # Change direction only after a certain delay to reduce jittery motion
    if timer <= 0:
        direction = random.choice([-1, 1])  # Pick a new random direction
        timer = random_move_delay  # Reset the timer
    else:
        timer -= 1  # Count down the timer

    # Apply movement in the current direction
    player_y += direction * speed

    # Ensure the paddle stays on screen
    if player_y < 0:
        player_y = 0
    if player_y + player_height > screen_height:
        player_y = screen_height - player_height

    return player_y, timer, direction


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Move the ball
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Ball collision with top and bottom walls
    if ball_y - ball_radius <= 0 or ball_y + ball_radius >= screen_height:
        ball_speed_y = -ball_speed_y

    # Ball collision with paddles
    if ball_towards_player1:
        if (player1_x + player_width >= ball_x - ball_radius and
                player1_y <= ball_y <= player1_y + player_height):
            ball_speed_x = -ball_speed_x
            ball_towards_player1 = False
            ball_towards_player2 = True

    if ball_towards_player2:
        if (player2_x <= ball_x + ball_radius and
                player2_y <= ball_y <= player2_y + player_height):
            ball_speed_x = -ball_speed_x
            ball_towards_player2 = False
            ball_towards_player1 = True

    # Move paddles
    if ball_towards_player1:
        player1_y = move_paddle_towards_ball(player1_y, player_height, ball_y, player1_speed)
        player2_y, player2_random_timer, player2_random_direction = smooth_random_paddle_movement(
            player2_y, player_height, screen_height, player2_speed, player2_random_timer, player2_random_direction)

    if ball_towards_player2:
        player2_y = move_paddle_towards_ball(player2_y, player_height, ball_y, player2_speed)
        player1_y, player1_random_timer, player1_random_direction = smooth_random_paddle_movement(
            player1_y, player_height, screen_height, player1_speed, player1_random_timer, player1_random_direction)

    # Prevent paddles from moving off-screen
    if player1_y < 0:
        player1_y = 0
    if player1_y + player_height > screen_height:
        player1_y = screen_height - player_height

    if player2_y < 0:
        player2_y = 0
    if player2_y + player_height > screen_height:
        player2_y = screen_height - player_height

    # Fill the screen with white
    screen.fill(white)

    # Draw the players and the ball
    pygame.draw.rect(screen, black, (player1_x, player1_y, player_width, player_height))
    pygame.draw.rect(screen, black, (player2_x, player2_y, player_width, player_height))
    pygame.draw.circle(screen, black, (ball_x, ball_y), ball_radius)

    pygame.display.flip()
    clock.tick(60)

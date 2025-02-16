import pygame
import random
from pygame.locals import *
pygame.mixer.init()


pygame.init()


WIDTH, HEIGHT = 980, 660
GRAVITY = 0.5
FLAP_STRENGTH = -10
OBSTACLE_SPEED = 3
GAP_SIZE = 250
fps = 60
obstacle_frequency = 2000
last_obstacle_time = pygame.time.get_ticks()
score = 0
level = 1


def adjust_speed():
    global OBSTACLE_SPEED, obstacle_frequency, level
    if score >= 7:
        level = 2
        OBSTACLE_SPEED = 4
        obstacle_frequency = 1500
    if score >= 14:
        level = 3
        OBSTACLE_SPEED = 5
        obstacle_frequency = 1000
    if score >= 21:
        level = 4
        OBSTACLE_SPEED = 6
        obstacle_frequency = 800
    if score >= 28:
        level = 5
        OBSTACLE_SPEED = 7
        obstacle_frequency = 600
    if score >= 35:
        level = 6
        OBSTACLE_SPEED = 8
        obstacle_frequency = 500



BACKGROUND = pygame.image.load("img/skyHopper2.jpg")
GROUND = pygame.image.load("img/ground.jpg")
DRAGON_IMG = pygame.image.load("img/dragon.png")
OBSTACLE_IMG = pygame.image.load("img/obsticle.png")


pygame.mixer.music.load("music/lady-of-the-80s.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

game_over_sound = pygame.mixer.Sound("music/losng-horn.mp3")
game_over_sound.set_volume(0.7)


BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))
GROUND = pygame.transform.scale(GROUND, (WIDTH, 100))
DRAGON_IMG = pygame.transform.scale(DRAGON_IMG, (90, 80))
OBSTACLE_IMG = pygame.transform.scale(OBSTACLE_IMG, (100, 300))


START_SCREEN = pygame.image.load("img/StartGameBG.png")
RESTART_SCREEN = pygame.image.load("img/youLooseBG.png")

START_SCREEN = pygame.transform.scale(START_SCREEN, (WIDTH, HEIGHT))
RESTART_SCREEN = pygame.transform.scale(RESTART_SCREEN, (WIDTH, HEIGHT))



screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sky Hopper')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)



class Dragon(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = DRAGON_IMG
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.lives = 3

    def update(self, game_started):
        if game_started:
            self.vel += GRAVITY
            if self.vel > 10:
                self.vel = 10
            self.rect.y += int(self.vel)
            if self.rect.bottom > HEIGHT - 100:
                self.rect.bottom = HEIGHT - 100
                self.vel = 0
            if self.rect.top < 0:
                self.rect.top = 0
                self.vel = 0

    def jump(self):
        self.vel = FLAP_STRENGTH


class ObstaclePair(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        min_height = 100
        max_height = HEIGHT - 100 - GAP_SIZE

        top_height = random.randint(min_height, max_height)
        bottom_height = HEIGHT - 100 - (top_height + GAP_SIZE)

        self.top_obstacle = pygame.Rect(
            x,
            0,
            OBSTACLE_IMG.get_width(),
            top_height
        )
        self.bottom_obstacle = pygame.Rect(
            x,
            top_height + GAP_SIZE,
            OBSTACLE_IMG.get_width(),
            bottom_height
        )
        self.passed = False


    def update(self):
        global score
        adjust_speed()
        self.top_obstacle.x -= OBSTACLE_SPEED
        self.bottom_obstacle.x -= OBSTACLE_SPEED
        if self.top_obstacle.right < 0:
            self.kill()
        if not self.passed and self.top_obstacle.right < dragon.rect.left:
            self.passed = True
            score += 1

    def draw(self, screen):
        top_obstacle_image = pygame.transform.scale(OBSTACLE_IMG, (self.top_obstacle.width, self.top_obstacle.height))
        screen.blit(top_obstacle_image, self.top_obstacle.topleft)
        bottom_obstacle_image = pygame.transform.scale(OBSTACLE_IMG, (self.bottom_obstacle.width, self.bottom_obstacle.height))
        screen.blit(pygame.transform.flip(bottom_obstacle_image, False, True), self.bottom_obstacle.topleft)


dragon_g = pygame.sprite.Group()
dragon = Dragon(100, HEIGHT // 2)
dragon_g.add(dragon)
obstacle_group = pygame.sprite.Group()


def should_spawn_obstacle():
    return True


def draw_lives():
    lives_text = font.render(f'Lives: {dragon.lives}', True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))


def draw_score():
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - 120, 10))


def restart_game():
    global game_started, dragon, obstacle_group, score, OBSTACLE_SPEED, level
    game_started = False
    dragon.lives = 3
    dragon.rect.center = [100, HEIGHT // 2]
    obstacle_group.empty()
    score = 0
    level = 1
    OBSTACLE_SPEED = 3
    obstacle_frequency = 2000
    pygame.mixer.music.play(-1)


def check_collision():
    global game_running, show_restart_screen
    for obstacle in obstacle_group:
        if dragon.rect.colliderect(obstacle.top_obstacle) or dragon.rect.colliderect(obstacle.bottom_obstacle):
            dragon.lives -= 1
            if dragon.lives == 0:
                game_running = False
                show_restart_screen = True
                pygame.mixer.music.stop()
                game_over_sound.play()
                return
            obstacle_group.remove(obstacle)


game_started = False
game_running = True
run = True
show_restart_screen = False

while run:
    clock.tick(fps)

    if not game_started and not show_restart_screen:
        screen.blit(START_SCREEN, (0, 0))
        pygame.mixer.music.stop()

    elif show_restart_screen:
        screen.blit(RESTART_SCREEN, (0, 0))
        pygame.mixer.music.stop()

    else:
        screen.blit(BACKGROUND, (0, 0))
        screen.blit(GROUND, (0, HEIGHT - 100))

        dragon_g.draw(screen)

        if game_running:
            dragon_g.update(game_started)

            if game_started:
                obstacle_group.update()
                for obstacle in obstacle_group:
                    obstacle.draw(screen)
                draw_lives()
                draw_score()
                check_collision()

                current_time = pygame.time.get_ticks()
                if should_spawn_obstacle() and current_time - last_obstacle_time > obstacle_frequency:
                    obstacle_x = WIDTH
                    obstacle_pair = ObstaclePair(obstacle_x)
                    obstacle_group.add(obstacle_pair)
                    last_obstacle_time = current_time

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

        if event.type == KEYDOWN:
            if event.key == K_SPACE and not game_started and not show_restart_screen:
                game_started = True
                pygame.mixer.music.play(-1)

            if event.key == K_SPACE and game_started and game_running:
                dragon.jump()

            if event.key == K_r and show_restart_screen:
                show_restart_screen = False
                restart_game()
                game_running = True
                game_started = False

    pygame.display.update()

pygame.quit()
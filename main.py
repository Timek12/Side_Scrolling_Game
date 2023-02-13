import pygame
import math
import os

pygame.init()

WIDTH, HEIGHT = 1500, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Side Scrolling Game")

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "forest_background.png")), (WIDTH * 2 / 3, HEIGHT))
BG2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "desert_background.png")),
                             (WIDTH * 2 / 3, HEIGHT))

# BG = pygame.image.load(os.path.join("assets", "forest_background.png")).convert()
BG_WIDTH = BG.get_width()

titles = 2 * (math.ceil(WIDTH / BG_WIDTH) + 1)
scroll = 0

# define game variavles
GRAVITY = 0.75

# define player action variables
moving_left = False
moving_right = False

# set framerate

clock = pygame.time.Clock()
FPS = 60


def draw_bg(scroll):
    for i in range(0, titles):
        if i % 2:
            WIN.blit(BG, (i * BG_WIDTH + scroll, 0))
        else:
            WIN.blit(BG2, (i * BG_WIDTH + scroll, 0))
        # reset scroll
    if abs(scroll) > BG_WIDTH:
        scroll = 0


class Worrior(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, velocity):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.velocity = velocity
        self.vel_y = 0
        self.direction = 1
        self.jump = False
        self.in_air = True
        self.flip = False

        # creating animation
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump']
        for animation in animation_types:
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0

        if moving_left:
            dx = - self.velocity
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.velocity
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # check collision with floor

        if self.rect.bottom + dy > 470:
            dy = 470 - self.rect.bottom
            self.in_air = False
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 180

        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

            self.update_time = pygame.time.get_ticks()

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation  settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        WIN.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


player = Worrior('player', 300, 470, 2, 5)
# enemy = Worrior('soldier2_transparent.png', 820, 400, 0.8, 5)


running = True

while running:
    clock.tick(FPS)

    draw_bg(scroll)
    player.update_animation()
    player.draw()

    if player.alive:
        if moving_left or moving_right:
            player.update_action(1)  # 1: run
        elif player.in_air:
            player.update_action(2)  # 2: jump
        else:
            player.update_action(0)  # 0: idle
        player.move(moving_left, moving_right)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True

            if event.key == pygame.K_d:
                moving_right = True

            if event.key == pygame.K_w and player.alive:
                player.jump = True

            if event.key == pygame.K_ESCAPE:
                running = False

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        scroll -= 5
    elif keys[pygame.K_a]:
        scroll += 5

    pygame.display.update()

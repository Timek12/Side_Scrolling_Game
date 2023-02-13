import pygame
import math
import os

pygame.init()

WIDTH, HEIGHT = 1500, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Side Scrolling Game")

# load images
BULLET = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bullet2.png")), (25, 35))
GRENADE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "grenade1.png")), (75, 75))
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
shoot = False
grenade = False
grenade_thrown = False

# set framerate

clock = pygame.time.Clock()
FPS = 60


def draw_bg(scroll):
    for i in range(0, titles):
        # if i % 2:
        WIN.blit(BG, (i * BG_WIDTH + scroll, 0))
        # else:
        #    WIN.blit(BG2, (i * BG_WIDTH + scroll, 0))
        # reset scroll
    if abs(scroll) > BG_WIDTH:
        scroll = 0


class Worrior(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
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
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0

        if moving_left:
            dx = - self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
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

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.53 * player.rect.size[0] * self.direction), player.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 180

        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

            self.update_time = pygame.time.get_ticks()

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation  settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        WIN.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.flip = False
        self.direction = direction
        if self.direction == 1:
            self.flip = False
        else:
            self.flip = True
        self.image = pygame.transform.flip(BULLET, self.flip, False)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = GRENADE
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #check collision with the floor
        if self.rect.bottom + dy > 470:
            dy = 470 - self.rect.bottom
            self.speed = 0

        #check collision with edge of the screen
        if self.rect.left + dx < 0 or self.rect.right + dx > WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed
        #update granade position
        self.rect.x += dx
        self.rect.y += dy





# create sprite groups (similar to lists but more functionality)
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()

player = Worrior('player', 300, 470, 2, 4, 30, 5)
enemy = Worrior('enemy', 820, 400, 2, 5, 30, 0)


running = True

while running:
    clock.tick(FPS)

    draw_bg(scroll)
    player.update()
    player.draw()

    enemy.update()
    enemy.draw()

    #update and draw groups
    bullet_group.update()
    grenade_group.update()
    bullet_group.draw(WIN)
    grenade_group.draw(WIN)



    if player.alive:
        #shoot bullets
        if shoot:
            player.shoot()
        #throw granades
        elif grenade and grenade_thrown == False and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + ( 0.1 * player.rect.size[0] * player.direction),
                              player.rect.top * 1.2, player.direction)
            grenade_group.add(grenade)
            player.grenades -= 1
            grenade_thrown = True
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

            if event.key == pygame.K_SPACE:
                shoot = True

            if event.key == pygame.K_q:
                grenade = True

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
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        scroll -= 4
    elif keys[pygame.K_a]:
        scroll += 4

    pygame.display.update()

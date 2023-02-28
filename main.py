import pygame
import os
import random
import csv

pygame.init()

WIDTH, HEIGHT = 800, 640
BG = (144, 201, 120)
ITEM_BOX_SIZE = 80
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Side Scrolling Game")



# define game variavles
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = HEIGHT // ROWS
TILE_TYPES = 21
level = 1

# load images

img_list = []
for x in range(TILE_TYPES):
    img = pygame.transform.scale(pygame.image.load(f'tile/{x}.png'), (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


BULLET = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bullet2.png")), (25, 35))
GRENADE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "grenade2.png")), (25, 25))
# BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "forest_background.png")), (WIDTH * 2 / 3, HEIGHT))
# BG2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "desert_background.png")),
#                             (WIDTH * 2 / 3, HEIGHT))
HEALTH_BOX = pygame.transform.scale(pygame.image.load(os.path.join("assets", "health.png")),
                                    (ITEM_BOX_SIZE, ITEM_BOX_SIZE))
AMMO_BOX = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ammo_box.png")),
                                  (ITEM_BOX_SIZE, ITEM_BOX_SIZE))
GRENADE_BOX = pygame.transform.scale(pygame.image.load(os.path.join("assets", "grenade2.png")),
                                     (ITEM_BOX_SIZE, ITEM_BOX_SIZE))
# BG = pygame.image.load(os.path.join("assets", "forest_background.png")).convert()

item_boxes = {
    'Health': HEALTH_BOX,
    'Ammo': AMMO_BOX,
    'Grenade': GRENADE_BOX
}


# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# set framerate

clock = pygame.time.Clock()
FPS = 60

# define font
font = pygame.font.SysFont('Futura', 40)


def draw_text(x, y, text, font, text_col):
    img = font.render(text, True, text_col)
    WIN.blit(img, (x, y))

def draw_bg():
    WIN.fill(BG)


class Worrior(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.kills = 0
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

        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

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
        self.width = self.image.get_width()
        self.height = self.image.get_height()

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

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom


        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.65 * player.rect.size[0] * self.direction), player.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 100) == 1:
                self.update_action(0)  # 1: run
                self.idling = True
                self.idling_counter = 50
            # check if the ai in near the player
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)  # 0: IDLE
                self.shoot()

            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run

                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 140 * self.direction, self.rect.centery)
                    # pygame.draw.rect(WIN, RED, self.vision)
                    self.move_counter += 1

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

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


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        #iterate through each value in level data file
        global health_bar, player
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile == 9 or tile == 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        #create player
                        player = Worrior('player', x * TILE_SIZE, y * TILE_SIZE, 1, 4, 15, 10)
                        health_bar = HealthBar(150, 13, player.health, player.health)
                    elif tile == 16:
                        enemy = Worrior('enemy', x * TILE_SIZE, y * TILE_SIZE, 1, 3, 30, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            WIN.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    # collision with player
    def update(self):
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            flag = 0
            if self.item_type == 'Health' and player.health + 25 <= player.max_health:
                player.health += 25
            elif self.item_type == 'Ammo':
                player.ammo += 20
            elif self.item_type == 'Grenade':
                player.grenades += 3
            else:
                flag = 1
            if flag == 0:
                self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        ratio = self.health / self.max_health

        pygame.draw.rect(WIN, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(WIN, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(WIN, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 20
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
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

        # check collision with obstacles
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    if enemy.health <= 0:
                        player.kills += 1
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
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #check for collision with level
        for tile in world.obstacle_list:
            #check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    self.direction *= -1
                    dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # update granade position
        self.rect.x += dx
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y)
            explosion_group.add(explosion)

            # checking for distance between grenade and the player
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                        enemy.health -= 50
                        if enemy.health <= 0 and enemy.health >= -50:
                            player.kills += 1



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(8):
            img = pygame.transform.scale(pygame.image.load(os.path.join("explosion", f'{num}.png')), (250, 250))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        # update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1

            # checking end of animation
            if self.frame_index >= len(self.images) - 1:
                self.kill()

            self.image = self.images[self.frame_index]


# create sprite groups (similar to lists but more functionality)
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)


running = True

while running:
    clock.tick(FPS)

    draw_bg()
    world.draw()

    # show health
    draw_text(20, 10, 'HEALTH: ', font, BLACK)
    health_bar.draw(player.health)

    # show ammo
    draw_text(20, 50, 'AMMO: ', font, BLACK)
    for x in range(player.ammo):
        WIN.blit(BULLET, (120 + (x * 30), 45))
    # show grenades
    draw_text(20, 80, 'GRENADES: ', font, BLACK)
    for x in range(player.grenades):
        WIN.blit(pygame.transform.scale(GRENADE, (40, 40)), (180 + (x * 50), 70))
    # show kills
    draw_text(20, 110, f'KILLS: {player.kills}', font, BLACK)

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    # update and draw groups
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()
    decoration_group.update()
    water_group.update()
    exit_group.update()


    bullet_group.draw(WIN)
    grenade_group.draw(WIN)
    explosion_group.draw(WIN)
    item_box_group.draw(WIN)
    decoration_group.draw(WIN)
    water_group.draw(WIN)
    exit_group.draw(WIN)


    if player.alive:
        # shoot bullets
        if shoot:
            player.shoot()
        # throw granades
        elif grenade and grenade_thrown == False and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + (0.1 * player.rect.size[0] * player.direction),
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


    pygame.display.update()

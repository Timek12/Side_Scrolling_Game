import pygame
import math
import os

pygame.init()

WIDTH, HEIGHT = 1500, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Side Scrolling Game")


BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "forest_background.png")), (WIDTH * 2 / 3, HEIGHT))
# BG = pygame.image.load(os.path.join("assets", "forest_background.png")).convert()
BG_WIDTH = BG.get_width()


titles = math.ceil(WIDTH / BG_WIDTH) + 3

scroll = 0
print(titles)

OBSTACLE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "obstacle1.png")), (150, 150))

class Worrior(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(os.path.join("assets", "archer.png"))
        self.image = pygame.transform.scale(img, (img.get_width() * scale , img.get_height() * scale))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    def draw(self):
        WIN.blit(player.image, player.rect)

player = Worrior(200, 200, 0.3)



obstacle_spot = [(0, 460), (150, 460), (300, 460), (450, 460), (600, 460), (750, 460), (900, 460), (1050, 460)]

def draw_obstacle(obstacle, obstacle_coordinates):
    for i in range(len(obstacle_coordinates)):
        WIN.blit(obstacle, obstacle_coordinates[i])


clock = pygame.time.Clock()
FPS = 60

running = True
archer_vel = 5

while running:
    clock.tick(FPS)

    for i in range(0, titles):
        WIN.blit(BG, (i * BG_WIDTH + scroll, 0))


    # reset scroll
    if abs(scroll) > BG_WIDTH:
        scroll = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            print(x, y)




    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        scroll -= 2
        # archer.x += archer_vel

    # elif keys[pygame.K_a]:
        # scroll += 2
        # archer.x -= archer_vel
    # elif keys[pygame.K_w]:
        # archer.jump_amplitude = 50
    # elif keys[pygame.K_s] and archer.y <= 340:
        # archer.y += archer_vel

    # dt = clock.tick(60) / 1000.0
    # archer.update(dt)
    # WIN.blit(archer.image, (archer.x, archer.y))



    player.draw()
    draw_obstacle(OBSTACLE, obstacle_spot)

    pygame.display.update()


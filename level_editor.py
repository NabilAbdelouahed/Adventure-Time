import pygame , numpy as np
import pickle
import os
import re

pygame.mixer.pre_init(44100,-16,2,512)
pygame.mixer.init()
pygame.init()

# addin a clock to keep track of time in the game
clock = pygame.time.Clock()
fps = 60


# window dimentions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('coding weeks : groupe 4')

tile_size = 40

font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
white = (255,255,255)
blue = (0,0,255)
red = (255, 0 , 0)
black = (0,0,0)

sun_img = pygame.image.load('img/sun.png')
sky_img = pygame.image.load('img/sky.png')
sky_img = pygame.transform.scale(sky_img,(SCREEN_WIDTH,SCREEN_HEIGHT))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit.png')
blob_img = pygame.image.load('img/blob.png')
xplat_img = pygame.image.load('img/platform.png')
yplat_img = pygame.image.load('img/platform.png')
coin_img = pygame.image.load('img/coin.png')
lava_img = pygame.image.load('img/lava.png')
player = pygame.image.load('img/guy1.png')
player = pygame.transform.scale(player, (30, 60))
main_menu = True


class World():
    def __init__(self, data):
        self.tile_list = []

        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        for i in range(len(data)):
            for j in range(len(data[i])):
                if data[i][j] == 1 :
                    img = pygame.transform.scale(dirt_img, (tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = tile_size * j
                    img_rect.y = tile_size * i
                    tile = (img,img_rect)
                    self.tile_list.append((tile))
                if data[i][j] == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = tile_size * j
                    img_rect.y = tile_size * i
                    tile = (img, img_rect)
                    self.tile_list.append((tile))
                if data[i][j] == 3:
                    img = pygame.transform.scale(blob_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = tile_size * j
                    img_rect.y = tile_size * i
                    tile = (img, img_rect)
                    self.tile_list.append((tile))
                if data[i][j] == 4:
                    img = pygame.transform.scale(xplat_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = tile_size * j
                    img_rect.y = tile_size * i
                    tile = (img, img_rect)
                    self.tile_list.append((tile))
                if data[i][j] == 5:
                    img = pygame.transform.scale(yplat_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = tile_size * j
                    img_rect.y = tile_size * i
                    tile = (img, img_rect)
                    self.tile_list.append((tile))
                if data[i][j] == 6:
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = tile_size * j
                    img_rect.y = tile_size * i
                    tile = (img, img_rect)
                    self.tile_list.append((tile))
                if data[i][j] == 7 :
                    img = pygame.transform.scale(coin_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = tile_size * j
                    img_rect.y = tile_size * i
                    tile = (img, img_rect)
                    self.tile_list.append((tile))
                if data[i][j] == 8 :
                    img = pygame.transform.scale(exit_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = tile_size * j
                    img_rect.y = tile_size * i
                    tile = (img, img_rect)
                    self.tile_list.append((tile))



    def draw(self):
        for tile in self.tile_list :
            screen.blit(tile[0],tile[1])


def split_screen(screen, tile_size):
    for x in range(0, SCREEN_WIDTH, tile_size):
        for y in range(0, SCREEN_HEIGHT, tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            pygame.draw.rect(screen, white, rect, 1)


run = True
clicked = False
action = False
level_data = [[0 for i in range(20)] for j in range(20)]
world = World(level_data)
while run :
    clock.tick(fps)
    screen.blit(sky_img, (0, 0))
    screen.blit(sun_img, (60, 60))
    screen.blit(player,(2*tile_size,SCREEN_HEIGHT-3*tile_size+20))
    split_screen(screen, tile_size)
    world.draw()
    x , y = pygame.mouse.get_pos()
    i , j = x//tile_size , y//tile_size

    if pygame.mouse.get_pressed()[0] and clicked == False:
        action = True
        clicked = True
    if  pygame.mouse.get_pressed()[0] == 0 :
        clicked = False
    if action :
        level_data[j][i] += 1
        action = False
        if level_data[j][i] >= 9 :
            level_data[j][i] = 0
    world = World(level_data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()

# save the level data to a file using pickle
def pickle_level(mat,i):
    with open(f'./levels/level_{i}.bin', 'wb') as fichier:
        pickle.dump(mat, fichier, pickle.HIGHEST_PROTOCOL)
    return()

# Get latest level number
def get_latest_level(directory_path):
    pattern = re.compile(r'^level_(\d+)\.bin$')
    max_level = None

    for filename in os.listdir(directory_path):
        match = pattern.match(filename)
        if match:
            level = int(match.group(1))
            if max_level is None or level > max_level:
                max_level = level
    if max_level is None:
        max_level = 0
    return max_level

level_number = get_latest_level('levels') + 1

pickle_level(level_data, level_number)
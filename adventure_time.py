import pygame
import pickle, os


pygame.mixer.pre_init(44100,-16,2,512)
pygame.mixer.init()
pygame.init()

#addin a clock to keep track of time in the game
clock = pygame.time.Clock()
fps = 60

# window dimentions
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
WINDOW_SIZE = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 100 * 100 - 100

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('coding weeks : groupe 4')

# create a 20*20 grid : 800/20 = 40 cell
tile_size = WINDOW_SIZE / 20

# display variables
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
white = (255,255,255)
blue = (0,0,255)
red = (255, 0 , 0)
black = (0,0,0)

#global variable for game status
game_over = 0

#to know when to display the main menu
main_menu = True

#levels
level = 1
max_level = len(os.listdir('./levels'))-1

score = 0

#import images
sun_img = pygame.image.load('img/sun.png')
sky_img = pygame.image.load('img/sky.png')
sky_img = pygame.transform.scale(sky_img,(WINDOW_SIZE,WINDOW_SIZE))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

#import sounds
pygame.mixer.music.load('sound_effect/music.wav')
pygame.mixer.music.play(-1,0.0,5000)
coin_sound = pygame.mixer.Sound('sound_effect/coin.wav')
coin_sound.set_volume(0.5)
jump_sound = pygame.mixer.Sound('sound_effect/jump.wav')
jump_sound.set_volume(0.5)
game_over_sound = pygame.mixer.Sound('sound_effect/game_over.wav')
game_over_sound.set_volume(0.5)


def depickle(i):
    with open(f'levels/level_{i}.bin', 'rb') as fichier:
        level = pickle.load(fichier)
    return(level)


# there is no built in function in pygame tp show a text in the screen so we need to build one
# for that we will convert text to image and use pygame.blit

def draw_text(text, font, text_col, x, y) :
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

# function to update levels
def reset_level(level, level_data):
    player.reset(tile_size * 2, WINDOW_SIZE - (tile_size * 2.5))
    blob_group.empty()
    platform_group.empty()
    lava_group.empty()
    coin_group.empty()
    exit_group.empty()
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)

    if level <= max_level :
        level_data = depickle(level)
        world = World(level_data)
    return(world)

# a class to generate all buttons
class Button():
    def __init__(self, x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        #check if the mouse is on the button and clicked
        if self.rect.collidepoint(pos) :
            if pygame.mouse.get_pressed()[0] and self.clicked == False: #list with 0 et 1 for the 3 buttons of the mouse
                action = True
                self.clicked = True
        if  pygame.mouse.get_pressed()[0] == 0 :
            self.clicked = False
        #draw the button
        screen.blit(self.image, self.rect)
        return(action)

#player class to define his position, movements...
class player():
    def __init__(self,x,y) :
        self.reset(x,y)

    def update(self, game_over):
        #we add dx and dy instead of self.rect.x += 5 so we can calculate the new position before applying it
        # this helps with collision detection 
        dx = 0
        dy = 0
        # adding a speed limit for the walking animation
        walk_cooldown = 5
        col_thresh = 20
        if game_over == 0 :
            # detect movement keys
            key = pygame.key.get_pressed()
            # if player is mid-air he can't jump
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -(tile_size * 0.36)
                self.jumped = True
                jump_sound.play()
            if key[pygame.K_SPACE] == False :
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False :
                self.counter = 0
                self.index = 0
                if self.direction == 1 :
                    self.image = self.images_right[self.index]
                if self.direction == -1 :
                    self.image = self.images_left[self.index]

            #add animation
            if self.counter > walk_cooldown :
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right) :
                    self.index = 0
                if self.direction == 1 :
                    self.image = self.images_right[self.index]
                if self.direction == -1 :
                    self.image = self.images_left[self.index]

            #add gravity
            self.vel_y += 1
            if self.vel_y > (tile_size * 0.25) :
                self.vel_y = tile_size * 0.25
            dy += self.vel_y

            #detect collision
            self.in_air = True
            for tile in world.tile_list :
                # check collision on x axis
                #given a position n we calculate the n+1 position using x+dx (same for y axis)
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #check collision ow yaxis
                if tile[1].colliderect(self.rect.x,self.rect.y + dy, self.width, self.height ) :
                    # check is player is under or ovec a block
                    #if vel < 0 player is jumping
                    if self.vel_y < 0:
                        #we move the player by the distance between him and the bloc
                        dy = tile[1].bottom - self.rect.top
                        # velocity needs to be reset to 0 to avoid getting a flying effect before the player falls
                        self.vel_y = 0
                    #if vel > 0 player is falling
                    elif self.vel_y >= 0:
                        #we move the player by the distance between him and the bloc
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            # check collision with blobs
            # spritecollide works the same as sprite rect but with sprite groups
            # if we don't add the False parameter, when colliding the function will make the colliding elements disappear but we just need to detect the collision
            if pygame.sprite.spritecollide(self, blob_group, False) :
                game_over = -1
                game_over_sound.play()

            # check collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False) :
                game_over = -1
                game_over_sound.play()
            # check collision with the exit
            if pygame.sprite.spritecollide(self, exit_group, False) :
                game_over = 1

            # check collision with flyingblocks
            for platform in platform_group:
                # on the x axis
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) :
                    dx = 0
                # on the y axis
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if player is under a bloc
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh :
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # check if player is standing on a bloc
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh :
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
                    #move the player with the moving bloc
                    if platform.move_x != 0 :
                        self.rect.x += platform.move_direction

            # update player's position
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1 :
            self.image = self.dead_image
            draw_text('GAME OVER !', font, red, (WINDOW_SIZE // 2) - (tile_size * 5), (WINDOW_SIZE // 2) - (tile_size * 2.5))
            draw_text('SCORE : ' + str(score), font_score, black, (WINDOW_SIZE // 2) - (tile_size * 2), (WINDOW_SIZE // 2) + (tile_size * 1.5))
            if self.rect.y > 160 :
                self.rect.y -= 5
        # draw player
        screen.blit(self.image,self.rect)

        return ( game_over )
        
    # Function to restart the player's position when starting or restarting a level
    def reset(self, x, y):
        # adding lists containing the player's images so for each movement we run through the list for an animation
        self.images_right = []
        self.images_left = []
             # track the index/position in the list
        self.index = 0
              # a variable to control the speed of the animation
        self.counter = 0
        # load the images in the lists
        for num in range(1,5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (tile_size * 0.75, tile_size * 1.5))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        # add a varible to adjust jumping speed depending on the space key press duration
        self.vel_y = 0
        # add a variable to control juming occurence
        self.jumped = False
        # control the movement direction to know which list to load for the animation
        self.direction = 0
        # prohibit multiple jumps 
        self.in_air = True

# class world to define levels structure 
class World():
    def __init__(self, data):
        # a simpler level list with just obstacles and their position
        self.tile_list = []
        
        # data represents the level's matrix
        # import images to create the world
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        # read the list and add corresponding blocs
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
                    # we add a +5 on the y axis to rest the blob on the dirt bloc
                    blob = Blob(tile_size * j, tile_size * i + 5)
                    # add the blob to an enemy group
                    blob_group.add(blob)
                if data[i][j] == 4:
                    platform = Plateform(tile_size * j, tile_size * i, 1,0)
                    platform_group.add(platform)
                if data[i][j] == 5:
                    platform = Plateform(tile_size * j, tile_size * i , 0 , 1)
                    platform_group.add(platform)
                if data[i][j] == 6:
                    lava = Lava(tile_size * j, tile_size * i + (tile_size // 2))
                    lava_group.add(lava)
                if data[i][j] == 7 :
                    coin = Coin(tile_size * j + tile_size // 2 , tile_size * i + tile_size // 2)
                    coin_group.add(coin)
                if data[i][j] == 8 :
                    exit = Exit(tile_size * j , tile_size * i - (tile_size // 2))
                    exit_group.add(exit)


    # display obstacles on the screen
    def draw(self):
        for tile in self.tile_list :
            screen.blit(tile[0],tile[1])

# create a blob class for enemies
# we will use a class included in the pygame "pygame.sprite.Sprite". the blob class will be a child class of it
# pygame.sprite.Sprite is a class for visible game objects so we will use some of its functions for the blob class
class Blob(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/blob.png")
        self.image = pygame.transform.scale(img, (tile_size , tile_size) )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # blob movement left and right
        self.move_direction = 1
        # limit blob movement to not fall from mobing blocs
        self.move_counter = 0
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > tile_size :
            # change direction
            self.move_direction *= -1
            # multiply by -1 instead of resetting to 0 to have the same movement to the left instead of going back to initianl position
            self.move_counter *= -1

class Plateform(pygame.sprite.Sprite) :
    def __init__(self,x,y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/platform.png")
        self.image = pygame.transform.scale(img, (tile_size , tile_size // 2) )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # for the blocs movement we will do the same as for the blob movement
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        if self.move_x == 1 :
            self.rect.x += self.move_direction
            self.move_counter += 1
            if abs(self.move_counter) > tile_size:
                # change direction
                self.move_direction *= -1
                # multiply by -1 instead of resetting to 0 to have the same movement to the left instead of going back to initianl position
                self.move_counter *= -1
        if self.move_y == 1 :
            self.rect.y += self.move_direction
            self.move_counter += 1
            if abs(self.move_counter) > tile_size:
                # change direction
                self.move_direction *= -1
                # multiply by -1 instead of resetting to 0 to have the same movement to the left instead of going back to initianl position
                self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(img, (tile_size , tile_size // 2 + 1) )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/coin.png")
        self.image = pygame.transform.scale(img, (tile_size // 2 , tile_size // 2) )
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

class Exit(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/exit.png")
        self.image = pygame.transform.scale(img, (tile_size , int(tile_size *1.5)) )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# create a list 20*20 to discribe the world
# 0 : nothing
# 1 : dirt
# 2 : grass
# 3 : blob
# 4 : plateforme horizontale
# 5 : plateforme varticale
# 6 : lava
# 7 : coin
# 8 : exit
level_data = depickle(level)
#import images
player = player(tile_size * 2 , WINDOW_SIZE - (tile_size * 2.5))
# pygame.sprite.Sprite class works the same as a list : needs to be initialised before append
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create coins for score
score_coin = Coin(tile_size //2 , tile_size // 2 )
coin_group.add(score_coin)
world = World(level_data)

# create buttons
restart_button = Button(WINDOW_SIZE // 2 - (tile_size * 2), WINDOW_SIZE // 2 , restart_img)
start_button = Button(WINDOW_SIZE // 2 - (tile_size * 7.5), WINDOW_SIZE // 2, start_img)
exit_button = Button(WINDOW_SIZE // 2 + (tile_size * 2.5), WINDOW_SIZE // 2, exit_img)

# game loop
run = True
while run :
    # fix the frame rate
    clock.tick(fps)
    # display images on the window
    screen.blit(sky_img, (0, 0))
    screen.blit(sun_img, (60, 60))

    # display menu
    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else :
        world.draw()

        if game_over == 0 :
            blob_group.update()
            platform_group.update()
            # manage coins
            if pygame.sprite.spritecollide(player, coin_group, True):
                score +=1
                coin_sound.play()
            draw_text('X '+ str(score), font_score, white, tile_size - (tile_size * 0.125), (tile_size * 0.125))

        # we didn't add a draw function for the blob because it's included in pygame.sprite.Sprite
        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)
        game_over = player.update(game_over)

        # the player lost
        if game_over == -1 :
             if restart_button.draw():
                world = reset_level(level,level_data)
                game_over = 0
                score = 0


        # player finished the level
        if game_over == 1 :
            level += 1
            if level <= max_level :
                # go to next level
                world = reset_level(level,level_data)
                game_over = 0
            else :
                draw_text('YOU WIN ! ', font, blue, (WINDOW_SIZE // 2) - (tile_size * 3.75), (WINDOW_SIZE // 2) - (tile_size * 2.5))
                draw_text('SCORE : '+ str(score),font_score,black,(WINDOW_SIZE // 2) - (tile_size * 2), (WINDOW_SIZE // 2) + (tile_size * 1.75))
                # restart game
                if restart_button.draw():
                    level = 1
                    world = reset_level(level, level_data)
                    game_over = 0
                    score = 0

        # condition to close the game window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()


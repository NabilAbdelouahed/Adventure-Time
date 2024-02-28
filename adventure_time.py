import pygame
import pickle, os


pygame.mixer.pre_init(44100,-16,2,512)
pygame.mixer.init()
pygame.init()

#addin a clock to keep track of time in the game
clock = pygame.time.Clock()
fps = 60

# window dimentions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('coding weeks : groupe 4')

# créer une grille 20*20 : 800/20 = 40 par case
tile_size = 40

# variables pour les affichages
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
white = (255,255,255)
blue = (0,0,255)
red = (255, 0 , 0)
black = (0,0,0)

#creer une variable globale qui indique quand est-ce que le jeu est fini
game_over = 0

#créer une varible pour savoir quand afficher le menu principal
main_menu = True

#levels
level = 1
max_level = len(os.listdir('D:/projects python pycharm/adventure_time/levels'))-1

score = 0

#importer les images
sun_img = pygame.image.load('img/sun.png')
sky_img = pygame.image.load('img/sky.png')
sky_img = pygame.transform.scale(sky_img,(SCREEN_WIDTH,SCREEN_HEIGHT))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

#importer les sons
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
#pour cela on va convertir le texte en image et utiliser pygame.blit

def draw_text(text, font, text_col, x, y) :
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

# creer une fonction pour charger les niveaux
def reset_level(level, level_data):
    player.reset(80, SCREEN_HEIGHT - 100)
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

#on crée une classe pour gérer tout les boutons du jeu restart par exemple
class Button():
    def __init__(self, x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #on veut appuier une seule fois sur le souris donc on peut utiliser self.clicked pour cela
        self.clicked = False
    def draw(self):
        # une variable qui représente la fonction du bouton
        action = False
        #position de la souris ( un point )
        pos = pygame.mouse.get_pos()
        #verifier si la souris est sur le bouton et si on appui sur le bouton
        if self.rect.collidepoint(pos) :
            if pygame.mouse.get_pressed()[0] and self.clicked == False: #liste avec des 0 et 1 pour les 3 boutons de la souris
                action = True
                self.clicked = True
        if  pygame.mouse.get_pressed()[0] == 0 :
            self.clicked = False
        #dessiner le bouton
        screen.blit(self.image, self.rect)
        return(action)

#creer une classe player pour definir le joueur, ses deplacements ...
class player():
    def __init__(self,x,y) :
        self.reset(x,y)

    def update(self, game_over):
        # on ajoute dx et dy au lieu de faire self.rect.x += 5 pour pouvoir calculer la nouvelle position avant de l'appliquer
        # pour faciliter la detection des collisions par la suite
        dx = 0
        dy = 0
        # adding a speed limit for the walking animation
        walk_cooldown = 5
        col_thresh = 20
        if game_over == 0 :
            # detecter les touches pour les deplacements
            key = pygame.key.get_pressed()
            # si le joueur est dans l'air il ne peux pas sauter
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
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

            #ajouter l'animation
            if self.counter > walk_cooldown :
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right) :
                    self.index = 0
                if self.direction == 1 :
                    self.image = self.images_right[self.index]
                if self.direction == -1 :
                    self.image = self.images_left[self.index]

            #ajouter la gravité
            self.vel_y += 1
            if self.vel_y > 10 :
                self.vel_y = 10
            dy += self.vel_y

            #vérifier la collision
            self.in_air = True
            for tile in world.tile_list :
                # vérifier la collision sur la direction x
                #étant en position n on utilise la position n+1 calculée a l'aide de x + dx ( pareil pour la direction y)
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #vérifier la collision sur la direction y
                if tile[1].colliderect(self.rect.x,self.rect.y + dy, self.width, self.height ) :
                    # verifier si le joueur est dessous ou dessus un bloc
                    #si vel < 0 le joueur est en train de sauter
                    if self.vel_y < 0:
                        #on bouge le joueur de la distance entre le block et sa position
                        dy = tile[1].bottom - self.rect.top
                        # la vitesse doit etre reset a 0 lorsqu'il touche le bloc avec sa tete pour eviter d'avoir un effet que le joueur plane pour
                        # un moment avant de retomber
                        self.vel_y = 0
                    #si vel > 0 le joueur est en train de tomber
                    elif self.vel_y >= 0:
                        #on bouge le joueur de la distance entre le block et sa position
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            # vérifier la collision avec les blobs
            # spritecollide foctionne comme sprite rect mais avec les groupes sprite
            #si on ne met pas le False lors de la collision la fonction va faire disparaitre ces elements or on veux juste detecter la collision
            if pygame.sprite.spritecollide(self, blob_group, False) :
                game_over = -1
                game_over_sound.play()

            # vérifier la collision avec la lave
            if pygame.sprite.spritecollide(self, lava_group, False) :
                game_over = -1
                game_over_sound.play()
            # vérifier la collision avec la sortie
            if pygame.sprite.spritecollide(self, exit_group, False) :
                game_over = 1

            # vérifier les collision avec les plateformes
            for platform in platform_group:
                #sur la direction x
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) :
                    dx = 0
                # sur la direction y
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #verifier si le joueur est sous une plateforme
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh :
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # verifier si le joueur est sur une plateforme
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh :
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
                    #deplacer le joueur avec la plateforme
                    if platform.move_x != 0 :
                        self.rect.x += platform.move_direction

            # mise a jour des coordonnées du joueur
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1 :
            self.image = self.dead_image
            draw_text('GAME OVER !', font, red, (SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) - 100)
            draw_text('SCORE : ' + str(score), font_score, black, (SCREEN_WIDTH // 2) - 80, (SCREEN_HEIGHT // 2) + 70)
            if self.rect.y > 160 :
                self.rect.y -= 5
        #dessiner le player
        screen.blit(self.image,self.rect)

        return ( game_over )
    # on crée une fonction restart qui réinitialise le joueur lorsque le bouton restart est presse
    def reset(self, x, y):
        # adding lists containing the player's images so for each movement we run through the list for an animation
        self.images_right = []
        self.images_left = []
             #track the index/position in the list
        self.index = 0
              # a variable to control the speed of the animation
        self.counter = 0
        #load the images in the lists
        for num in range(1,5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (30, 60))
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
        # ajouter une variable qui traduit la vitesse lors du saut pour gérer l'amplitude du saut selon l'appui sur le space key
        self.vel_y = 0
        # ajouter une variable pour controler les sauts
        self.jumped = False
        #control the movement direction to know which list to load for the animation
        self.direction = 0
        # pour fixer le bug de pouvoir sauter plusieurs fois on ajoute une variable qui nous indique quand est ce que le joueur est dans l'air
        self.in_air = True

#creer une classe world pour definir les niveaux
class World():
    def __init__(self, data):
        #creer une liste plus simplifiee pour le world avec que les obstacles et leurs positions
        self.tile_list = []
        # data représente la matrice world

        # importer les images pour créer le niveau
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        # lire la liste world_data et interpreter les entiers
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
                    # on met un +5 sur la direction y pour poser le blob sur le bloque dirt
                    blob = Blob(tile_size * j, tile_size * i + 5)
                    #ajouter le blob au groupe des ennemis
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


    #afficher les obstacles sur la fenetre
    def draw(self):
        for tile in self.tile_list :
            screen.blit(tile[0],tile[1])

# creer une classe blob pour les ennemis
# on va utiliser la classe incluse dans le module pygame "pygame.sprite.Sprite". la classe blob sera une classe enfant de cette classe
# pygame.sprite.Sprite is a class for visible game objects donc on utilisera qq fonctions de cette classe dans la classe blob
class Blob(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # une variable pour le mouvement des blobs vers la gauche ou la droite
        self.move_direction = 1
        #une variable qui nous aidera a limiter le mouvement des blobs pour ne pas depasser la plateforme par exemple
        self.move_counter = 0
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > tile_size :
            #changer la direction
            self.move_direction *= -1
            # multiplier par -1 au lieu de reset a zero pour avoir le meme mouvement a gauche au lieu de revenir a la position initiale
            self.move_counter *= -1

class Plateform(pygame.sprite.Sprite) :
    def __init__(self,x,y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/platform.png")
        self.image = pygame.transform.scale(img, (tile_size , tile_size // 2) )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #pour le mouvement des plateformes on va faire comme pour le mouvement des blobs
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        if self.move_x == 1 :
            self.rect.x += self.move_direction
            self.move_counter += 1
            if abs(self.move_counter) > tile_size:
                # changer la direction
                self.move_direction *= -1
                # multiplier par -1 au lieu de reset a zero pour avoir le meme mouvement a gauche au lieu de revenir a la position initiale
                self.move_counter *= -1
        if self.move_y == 1 :
            self.rect.y += self.move_direction
            self.move_counter += 1
            if abs(self.move_counter) > tile_size:
                # changer la direction
                self.move_direction *= -1
                # multiplier par -1 au lieu de reset a zero pour avoir le meme mouvement a gauche au lieu de revenir a la position initiale
                self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(img, (tile_size , tile_size // 2) )
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
#importer les images
player = player(80 , SCREEN_HEIGHT - 100)
# la classe pygame.sprite.Sprite fonctionne comme les listes avant de faire un append il faut creer une liste vide ou on pourra ajouter
# les ennemis par la suite. ceci sera le role de la variable ci dessous (blob_group) :
#pareil pour la lave, plateforme et exit
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# creer un coin pour l'affichage du score
score_coin = Coin(tile_size //2 , tile_size // 2 )
coin_group.add(score_coin)
world = World(level_data)

#créer les boutons
restart_button = Button(SCREEN_WIDTH // 2 -80, SCREEN_HEIGHT // 2 , restart_img)
start_button = Button(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2, start_img)
exit_button = Button(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, exit_img)

# boucle du jeu
run = True
while run :
    #fix the frame rate
    clock.tick(fps)
    #afficher les images dans la fenetre
    screen.blit(sky_img, (0, 0))
    screen.blit(sun_img, (60, 60))

    # afficher le menu ou jouer
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
            #gerer les coins
            if pygame.sprite.spritecollide(player, coin_group, True):
                score +=1
                coin_sound.play()
            draw_text('X '+ str(score), font_score, white, tile_size -5, 5)

        #on n'a pas codé la fonction draw pour les blob parce que celle ci est deja codée dans la classe pygame.sprite.Sprite
        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)
        game_over = player.update(game_over)

        #le joueur a perdu
        if game_over == -1 :
             if restart_button.draw():
                world = reset_level(level,level_data)
                game_over = 0
                score = 0


        #le joueur a fini le niveau
        if game_over == 1 :
            level += 1
            if level <= max_level :
                #passer au niveau suivant
                world = reset_level(level,level_data)
                game_over = 0
            else :
                draw_text('YOU WIN ! ', font, blue, (SCREEN_WIDTH // 2) - 150, (SCREEN_HEIGHT // 2) - 100)
                draw_text('SCORE : '+ str(score),font_score,black,(SCREEN_WIDTH // 2) - 80, (SCREEN_HEIGHT // 2) + 70)
                #restart le jeu
                if restart_button.draw():
                    level = 1
                    world = reset_level(level, level_data)
                    game_over = 0
                    score = 0

        # condition pour fermer la fenetre du jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()


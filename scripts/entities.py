import pygame, os, random
from .question import Question
from .effects import Stun
from .utils import load_img, load_images, BASE_IMG_PATH

class Entity:
    def __init__(self,game):
        self.game = game
        self.load_assets()
        self.position_x, self.position_y = 200,200  #initial position
        self.current_frame, self.last_frame_update = 0,0

    def update(self,delta_time, actions):
        # Get the direction from inputs
        direction_x = actions["right"] - actions["left"]
        direction_y = actions["down"] - actions["up"]
        # Update the position
        self.position_x += 100 * delta_time * direction_x
        self.position_y += 100 * delta_time * direction_y
        # Animate the sprite
        self.animate(delta_time,direction_x,direction_y)

    def render(self, display):
        display.blit(self.curr_image, (self.position_x,self.position_y))

    def animate(self):
        pass

    def load_assets(self):
        # Get the diretory with the player sprites
        self.sprite_dir = os.path.join(self.game.sprite_dir, "player")
        self.front_sprites, self.back_sprites, self.right_sprites, self.left_sprites = [],[],[],[]
        # Load in the frames for each direction
        for i in range(1,5):
            self.front_sprites.append(pygame.image.load(os.path.join(self.sprite_dir, "player_front" + str(i) +".png")))
            self.back_sprites.append(pygame.image.load(os.path.join(self.sprite_dir, "player_back" + str(i) +".png")))
            self.right_sprites.append(pygame.image.load(os.path.join(self.sprite_dir, "player_right" + str(i) +".png")))
            self.left_sprites.append(pygame.image.load(os.path.join(self.sprite_dir, "player_left" + str(i) +".png")))
        # Set the default frames to facing front
        self.curr_image = self.front_sprites[0]
        self.curr_anim_list = self.front_sprites

class Player():
    def __init__(self,game, game_world):
        self.game = game        #game class in main
        self.game_world = game_world        #containing the in-game objects
        self.position_x, self.position_y = 200,200
        self.speed = 100
        self.current_frame, self.last_frame_update = 0,0
        
        self.size = (16,16)

        self.question_queue = []
        self.applied_fx = []
        self.stunned = False
        self.point = 0

        self.load_assets()

    def update(self,delta_time, actions):
        # Get the direction from inputs
        direction_x = actions["right"] - actions["left"]
        direction_y = actions["down"] - actions["up"]

        # Update the position
        self.position_x += self.speed * delta_time * direction_x  # (100*direction_x) is x velocity, 100 is the speed along the x axis
        self.position_y += self.speed * delta_time * direction_y
        
        # Handle collision with coins
        player_rect = self.rect()
        collected_coins = []
        for coin in self.game_world.coins:
            if player_rect.colliderect(coin):
                collected_coins.append(coin)
                self.point += 1
        for coin in collected_coins:
            self.game_world.coins.remove(coin)

        # "Handle collision with spells"
        collected_spells = []
        for spell in self.game_world.spells:
            if player_rect.colliderect(spell):
                self.question_queue.append(Question(self.game))
                collected_spells.append(spell)
                self.point += 1
        for spell in collected_spells:
            self.game_world.spells.remove(spell)
        
        # Animate the sprite
        self.animate(delta_time,direction_x,direction_y)

        # Update question queue
        if actions['answered']:
            if self.question_queue.pop(0).correct(actions):
                # self.applied_fx.append()
                ...
            else:
                self.applied_fx.append(Stun(self, 3))

        # update effects - this need to go after updating Player.applied_fx
        for effect in self.applied_fx:
            effect.update(delta_time, actions)

    def render(self, display, actions):
        # draw the player
        display.blit(self.curr_image, (self.position_x,self.position_y))

        #overlay
        # update effects
        for effect in self.applied_fx:
            effect.render_overlay(display)

        # render question for this player
        if len(self.question_queue) >= 1:
            self.question_queue[0].render(display, actions)

    def animate(self, delta_time, direction_x, direction_y):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time
        # If no direction is pressed, set image to idle and return
        if not (direction_x or direction_y): 
            if not self.stunned:
                self.curr_image = self.curr_anim_list[0]
            return
        # If an image was pressed, use the appropriate list of frames according to direction
        if direction_x:
            if direction_x > 0: self.curr_anim_list = self.right_sprites
            else: self.curr_anim_list = self.left_sprites
        if direction_y:
            if direction_y > 0: self.curr_anim_list = self.front_sprites
            else: self.curr_anim_list = self.back_sprites
        # Advance the animation if enough time has elapsed
        if self.last_frame_update > .15:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame +1) % len(self.curr_anim_list)
            if not self.stunned:
                self.curr_image = self.curr_anim_list[self.current_frame]

    def rect(self):
        return pygame.Rect(self.position_x, self.position_y, *self.size)

    def load_assets(self):
        # Get the diretory with the player sprites
        self.sprite_dir = os.path.join(self.game.sprite_dir, "player")
        # Load in the frames for each direction
        self.front_sprites = load_images('player/front')
        self.back_sprites = load_images('player/back')
        self.right_sprites = load_images('player/right')
        self.left_sprites = load_images('player/left')
        # Load img for Stun effect
        self.stunned_img = {'front':None, 'back':None, 'right':None, 'left':None}
        for stun_direction in self.stunned_img:
            self.stunned_img[stun_direction] = load_img('player/stunned/'+ stun_direction + '.png')
        # Set the default frames to facing front
        self.curr_image = self.front_sprites[0]
        self.curr_anim_list = self.front_sprites

        #Load overlays for effects
        self.overlays = {}
        for effect_name in os.listdir(BASE_IMG_PATH + 'overlay'):
            self.overlays[effect_name] = load_images('overlay/' + effect_name)        

class Bot(Entity):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)

class Coin(Entity):
    def __init__(self, game):
        super().__init__(game)
        self.position_x = random.choice(range((self.game.GAME_W - self.game.GAME_H)//2 + 25, (self.game.GAME_W + self.game.GAME_H)//2 - 25))
        self.position_y = random.choice(range(25 ,self.game.GAME_H - 25))

        self.rect = pygame.Rect(self.position_x, self.position_y, 9, 9)

    def update(self,delta_time, actions):

        # Handle collision with players
        ... # TODO

        # Animate the sprite
        self.animate(delta_time)

    def animate(self, delta_time):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time
        # intro sequence (rename files)
        '''if not (direction_x or direction_y): 
            self.curr_image = self.sprites[0]
            return'''
        
        # handles if 'counterintuitive' is played
        ...# TODO

        # Advance the animation if enough time has elapsed
        if self.last_frame_update > .15:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame +1) % len(self.sprites)
            self.curr_image = self.sprites[self.current_frame]

    def load_assets(self):
        # Get the diretory with the player sprites
        self.sprite_dir = os.path.join(self.game.sprite_dir, "coin")
        self.sprites = []
        # Load in the frames for each direction
        for i in range(1,5):
            self.sprites.append(pygame.image.load(os.path.join(self.sprite_dir, "coin" + str(i) +".png")))
        # Set the default frames to facing front
        self.curr_image = self.sprites[0]

class Spell(Entity):
    def __init__(self, game):
        super().__init__(game)
        self.position_x = random.choice(range((self.game.GAME_W - self.game.GAME_H)//2 + 25, (self.game.GAME_W + self.game.GAME_H)//2 - 25))
        self.position_y = random.choice(range(25 ,self.game.GAME_H - 25))

        self.rect = pygame.Rect(self.position_x, self.position_y, 12, 12)

        # self.effect = random.choice()

    def update(self,delta_time, actions):

        # Handle collision with players
        ... # TODO

        # Animate the sprite
        self.animate(delta_time)

    def animate(self, delta_time):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time
        # intro sequence (rename files)
        '''if not (direction_x or direction_y): 
            self.curr_image = self.sprites[0]
            return'''
        
        # handles if 'counterintuitive' is played
        ...# TODO

        # Advance the animation if enough time has elapsed
        if self.last_frame_update > .15:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame +1) % len(self.sprites)
            self.curr_image = self.sprites[self.current_frame]

    def load_assets(self):
        # Get the diretory with the player sprites
        self.sprite_dir = os.path.join(self.game.sprite_dir, "spell")
        self.sprites = []
        # Load in the frames for each direction
        for i in range(1,3):
            self.sprites.append(pygame.image.load(os.path.join(self.sprite_dir, "spell" + str(i) +".png")))
        # Set the default frames to facing front
        self.curr_image = self.sprites[0]
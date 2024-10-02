import pygame, os, random, sys
from .question import Question
from .effects import Stunned, Delayed_coin_burst, Extra_coin_value, Drop_coin_around_self, Accumulation, Immunity
from .utils import load_img, load_images, BASE_IMG_PATH, PLAYER_SPEED

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

    def render(self, display, offset):
        display.blit(self.curr_image, (self.position_x - offset[0], self.position_y - offset[1]))

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
        self.size = (16,16)
        self.position_x, self.position_y = self.game.GAME_W/2 - self.size[0]/2, self.game.GAME_H/2 - self.size[1]/2
        self.speed = 100
        self.current_frame, self.last_frame_update = 0,0
        
        self.question_queue = []
        self.applied_fx = []
        self.effects_to_remove = []
        self.stunned = False
        self.immuned = False

        self.score = 0
        self.score_font = pygame.font.SysFont('Consolas', 28, False, False)

        self.load_assets()

    def update(self,delta_time, actions):
        # Get the direction from inputs
        direction_x = actions["right"] - actions["left"]
        direction_y = actions["down"] - actions["up"]

        if self.stunned: self.speed = 0
        else: self.speed = PLAYER_SPEED
        # Update the position
        self.position_x += self.speed * delta_time * direction_x  # (100*direction_x) is x velocity, 100 is the speed along the x axis
        # prevent player going out of border
        if self.position_x < self.game_world.game_area['left']:
            self.position_x = self.game_world.game_area['left']
        elif self.position_x > self.game_world.game_area['right']:
            self.position_x = self.game_world.game_area['right']
        self.position_y += self.speed * delta_time * direction_y
        # prevent player going out of border
        if self.position_y < self.game_world.game_area['top']:
            self.position_y = self.game_world.game_area['top']
        elif self.position_y > self.game_world.game_area['bottom']:
            self.position_y = self.game_world.game_area['bottom']

        # Handle collision with coins
        player_rect = self.rect()
        collected_coins = []
        for coin in self.game_world.coins:
            if player_rect.colliderect(coin):
                collected_coins.append(coin)
                self.score += 1
        for coin in collected_coins:
            self.game_world.coins.remove(coin)

        # "Handle collision with spells"
        collected_spells = []
        for spell in self.game_world.spells:
            if player_rect.colliderect(spell):
                self.question_queue.append(Question(self.game))
                collected_spells.append(spell)
        for spell in collected_spells:
            self.game_world.spells.remove(spell)

        # Update question queue
        if actions['answered']:
            if self.question_queue.pop(0).correct(actions):
                self.applied_fx.append(Immunity(self))
            else:
                self.applied_fx.append(Stunned(self, 3))

        # update effects - this need to go after updating Player.applied_fx
        for effect in self.applied_fx:
            effect.update()
        for effect in self.effects_to_remove:
            self.applied_fx.remove(effect)
        self.effects_to_remove = []
                
        # Animate the sprite
        self.animate(delta_time,direction_x,direction_y)

    def render(self, display, actions, offset, rendered_by_others = False):
        # draw the player
        display.blit(self.curr_image, (self.position_x - offset[0], self.position_y - offset[1]))

        #overlay
        # update effects
        for effect in self.applied_fx:
            effect.render_overlay(display, offset)

        # render question and score for this player only
        if not rendered_by_others:
            if len(self.question_queue) >= 1:
                self.question_queue[0].render(display, actions)

            display.blit(self.score_font.render(str(self.score), True, (0,0,0)), (25,25))

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

class Bot(Entity):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)

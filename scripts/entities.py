import pygame, os, random, math
from .question import Question
from .effects import Stunned
from .utils import load_img, load_images, BASE_IMG_PATH, PLAYER_SPEED


class Player():
    def __init__(self,game, game_world):
        self.game = game        #game class in main
        self.game_world = game_world        #containing the in-game objects
        self.size = (16,16)
        self.position_x, self.position_y = self.game.GAME_W/2 - self.size[0]/2, self.game.GAME_H/2 - self.size[1]/2
        self.speed = 100
        self.current_frame, self.last_frame_update = 0,0
        
        self.question_queue = []
        self.answered_q = None
        self.applied_fx = []
        self.effects_to_remove = []
        self.stunned = False
        self.immuned = False

        self.score = 0
        self.score_font = pygame.font.SysFont('Consolas', 28, False, False)

        self.load_assets()

    def update(self,delta_time, actions):
        if self.game_world.end_game:
            return
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

        if not self.game_world.end_game:
            # Handle collision with coins
            player_rect = self.rect()
            collected_coins = []
            for coin in self.game_world.coins:
                if player_rect.colliderect(coin):
                    collected_coins.append(coin)
                    self.question_queue.append(Question(self.game, self))
            for coin in collected_coins:
                self.game_world.coins.remove(coin)

            # Update question queue
            if actions['answered']:
                self.answered_q = self.question_queue.pop(0)
                if self.answered_q.correct():
                    self.score += 50
                else:
                    self.applied_fx.append(Stunned(self, 3))

        # Animate the sprite
        self.animate(delta_time,direction_x,direction_y)

        # update effects - this need to go after updating Player.applied_fx
        for effect in self.applied_fx:
            effect.update()
        for effect in self.effects_to_remove:
            self.applied_fx.remove(effect)
        self.effects_to_remove = []

    def render(self, display, actions, offset, rendered_by_others = False):
        # draw the player
        display.blit(self.curr_image, (self.position_x - offset[0], self.position_y - offset[1]))

        #overlay
        # update effects
        for effect in self.applied_fx:
            effect.render_overlay(display, offset)

        # render question and score for this player only
        if not rendered_by_others:
            if self.answered_q and self.stunned:
                self.answered_q.render(display)
            elif len(self.question_queue) >= 1:
                self.question_queue[0].render(display)

    def animate(self, delta_time, direction_x, direction_y):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time
        # If no direction is pressed, set image to idle and return
        if not (direction_x or direction_y): 
            if not self.stunned:
                self.current_frame = 0
                self.curr_image = self.curr_anim_list[self.current_frame]
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
        # Icon for leader board
        self.icon = load_img('player/icon.png')

class Bot(Player):
    def __init__(self,game, game_world, difficulty:str):
        super().__init__(game, game_world)
        if difficulty == 'startup':
            self.accuracy = [.5,.5]
            self.answering_time = 8
        if difficulty == 'enterprise':
            self.accuracy = [.3,.7]
            self.answering_time = 5
        if difficulty == 'corporation':
            self.accuracy = [.1,.9]
            self.answering_time = 3
        del self.question_queue
        self.wait = 0
        self.add_point = 0
        self.wrong = False

    def update(self, delta_time):
        if self.game_world.end_game:
            return
        # animate is in the move_toward func
        # if self.difficulty == 'corporation':
        if self.wait <= 0:
            prev_nearest_dist = math.inf
            if not self.stunned and len(self.game_world.coins) > 0:
                for coin in self.game_world.coins:
                    if self.distance_from_player(coin) < prev_nearest_dist:
                        nearest_coin_loc = (coin.position_x, coin.position_y)
                self.move_toward(nearest_coin_loc, delta_time)
            
            if self.add_point > 0:
                self.score += self.add_point*50
                self.add_point = 0

            if self.wrong:
                self.applied_fx.append(Stunned(self, 3))
                self.wrong = False

        else:
            self.wait -= delta_time

        bot_rect = self.rect()
        # "Handle collision with coins"
        collected_coins = []
        for coin in self.game_world.coins:
            if bot_rect.colliderect(coin):
                self.wait = self.answering_time
                if random.choices([0,1], self.accuracy)[0]:
                    self.add_point += 1
                else:
                    self.wrong = True
                collected_coins.append(coin)
        for coin in collected_coins:
            self.game_world.coins.remove(coin)

        # update effects - this need to go after updating Player.applied_fx
        for effect in self.applied_fx:
            effect.update()
        for effect in self.effects_to_remove:
            self.applied_fx.remove(effect)
        self.effects_to_remove = []

    def load_assets(self):
        # Load in the frames for each direction
        self.front_sprites = load_images('bot/front')
        self.back_sprites = load_images('bot/back')
        self.right_sprites = load_images('bot/right')
        self.left_sprites = load_images('bot/left')
        # Load img for Stun effect
        self.stunned_img = {'front':None, 'back':None, 'right':None, 'left':None}
        for stun_direction in self.stunned_img:
            self.stunned_img[stun_direction] = load_img('bot/stunned/'+ stun_direction + '.png')
        # Set the default frames to facing front
        self.curr_image = self.front_sprites[0]
        self.curr_anim_list = self.front_sprites       
        # Icon for leader board
        self.icon = load_img('bot/icon.png')

    def move_toward(self, loc, dt):
        if self.stunned: self.speed = 0
        else: self.speed = PLAYER_SPEED

        if self.position_x - loc[0] > 6: direction_x = -1
        elif self.position_x - loc[0] < -6: direction_x = 1
        else: direction_x = 0
        if not self.stunned:
            self.position_x += self.speed * dt * direction_x

        if self.position_y - loc[1] > 6: direction_y = -1
        elif self.position_y - loc[1] < -6: direction_y = 1
        else: direction_y = 0
        if not self.stunned:
            self.position_y += self.speed * dt * direction_y

        self.animate(dt,direction_x,direction_y)
        
    def distance_from_player(self, obj):
        diagonal_path_dist = min(abs(self.position_x - obj.position_x), abs(self.position_y - obj.position_y))
        remaining_straight_dist = abs(abs(self.position_x - obj.position_x) - abs(self.position_y - obj.position_y))
        return diagonal_path_dist + remaining_straight_dist
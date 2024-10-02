import pygame, time, random, math, os
from .utils import PLAYER_SPEED, BASE_IMG_PATH, load_images
from .collectibles import Coin
NEGATIVE_FX = ['stunned', 'steal', 'lose_coins_every_sec', 'stolen', 'teleport_random', 'coins_avoid_player']

class Effect():
    '''
    Base class for timed effects on player, except for Exploit
    '''

    def __init__(self, player, fx_name:str, duration = -1, frame_interval = .15) -> None:
        '''
        player: player to receive the effect
        fx_name: specifies the overlay set to use and the level of the current fx(if any)
        '''
        self.fx_name = fx_name
        self.player = player
        self.timer = duration       #-1 imply untimed
        # current frame of overlay
        self.current_frame, self.last_frame_update = 0,0

        self.curr_sprite_set = load_images('overlay/' + self.fx_name)
        self.curr_overlay_img = self.curr_sprite_set[0]

        self.frame_interval = .08

    def update(self):
        # update time elapsed since last frame and remove effect after finishing the last frame (if the animation does not loop)
        self.last_frame_update += self.player.game.dt
        if self.curr_overlay_img == self.curr_sprite_set[-1] and self.last_frame_update > self.frame_interval:
            self.player.effects_to_remove.append(self)

    def animate_overlay(self, sprite_set, loop = True):
        # Advance the animation if enough time has elapsed
        if self.last_frame_update > self.frame_interval:
            self.last_frame_update = 0
            if loop:
                self.current_frame = (self.current_frame +1) % len(sprite_set)
            else:
                self.current_frame = min(self.current_frame +1, len(sprite_set)-1)
            self.curr_overlay_img = sprite_set[self.current_frame]

    def render_overlay(self, display, offset):
        player_rect = self.player.rect()
        overlay_rect = self.curr_overlay_img.get_rect(center = player_rect.center)
        overlay_rect.x -= offset[0]
        overlay_rect.y -= offset[1]
        display.blit(self.curr_overlay_img, overlay_rect)

    def load_assets(self):
        self.curr_sprite_set = load_images('overlay/' + self.fx_name)       


# ------------------------------- Possitive fx -------------------------------------

class Stunned(Effect):
    def __init__(self, player, duration) -> None:
        super().__init__(player, self.__class__.__name__.lower(), duration)
        self.sliding_timer = .75

        # if player is already stunned, stop taking prev direction
        if self.player.stunned:
            self.already_stunned = True                 # If there is an existing Stun obj in Player's fx queue
            self.got_prev_directions = True
        else:
            self.already_stunned = False
            self.got_prev_directions = False
        self.prev_directions = [0,0]

        # intercept the player's animation sprites
        match self.player.curr_anim_list:
            case self.player.front_sprites:
                self.player.curr_image = self.player.stunned_img['front']
            case self.player.back_sprites:
                self.player.curr_image = self.player.stunned_img['back']
            case self.player.right_sprites:
                self.player.curr_image = self.player.stunned_img['right']
            case self.player.left_sprites:
                self.player.curr_image = self.player.stunned_img['left']

    def update(self):
        self.timer -= self.player.game.dt
        self.sliding_timer -= self.player.game.dt
        self.last_frame_update += self.player.game.dt

        if self.timer <= 0:
            self.player.stunned = False
            # return the sprite collection based on direction
            if self.player.curr_image == self.player.stunned_img['front']: self.player.curr_anim_list = self.player.front_sprites
            elif self.player.curr_image == self.player.stunned_img['back']: self.player.curr_anim_list = self.player.back_sprites
            elif self.player.curr_image == self.player.stunned_img['right']: self.player.curr_anim_list = self.player.right_sprites
            elif self.player.curr_image == self.player.stunned_img['left']: self.player.curr_anim_list = self.player.left_sprites
            # delete fx
            self.player.effects_to_remove.append(self)
            return

        if not self.got_prev_directions:
            self.prev_directions[0] = (self.player.game.actions['right'] - self.player.game.actions['left'])
            self.prev_directions[1] = (self.player.game.actions['down'] - self.player.game.actions['up'])
            self.got_prev_directions = True

        # if player is not already stunned and was moving when stunned, add sliding
        if not self.already_stunned:
            #                         <---------------------------add sliding distance----------------------------->  
            self.player.position_x += PLAYER_SPEED * self.player.game.dt * max(0, self.sliding_timer)*self.prev_directions[0]
            self.player.position_y += PLAYER_SPEED * self.player.game.dt * max(0, self.sliding_timer)*self.prev_directions[1]
        
        self.player.stunned = True

        self.animate_overlay(self.curr_sprite_set)

class Extra_coin_value(Effect):
    'One-time effect with no looping animation'
    def __init__(self, player, level:int) -> None:
        super().__init__(player, self.__class__.__name__.lower() + '_lvl' + str(level))
        self.level = level
        self.last_coin_counting_frame = 10
        self.player_prev_score = self.player.score
        self.enough_coin = False
        self.frame_interval = .08

    def update(self):
        self.animate_overlay()

        if self.curr_overlay_img == self.curr_sprite_set[self.last_coin_counting_frame]:
            if not self.enough_coin:
                self.last_frame_update = -.2       #allow the last frame to be displayed for another (.2+fx_end_frame_interval) second
                self.player.score += self.level
            self.enough_coin = True
        if self.curr_overlay_img == self.curr_sprite_set[-1]:
            self.player.effects_to_remove.append(self)

    def animate_overlay(self):
        if not self.enough_coin:
            if self.player.score - self.player_prev_score > 0:
                self.current_frame = min(self.current_frame + (self.player.score - self.player_prev_score), self.last_coin_counting_frame)
                self.curr_overlay_img = self.curr_sprite_set[self.current_frame]
                self.player_prev_score = self.player.score
        else:
            self.last_frame_update += self.player.game.dt
            super().animate_overlay(self.curr_sprite_set)
    
class Delayed_coin_burst(Effect):
    def __init__(self, player) -> None:
        super().__init__(player, self.__class__.__name__.lower())
        self.player_prev_score = self.player.score
        self.end_fx = False
    
    def update(self):
        if self.curr_overlay_img == self.curr_sprite_set[-1]:
            if not self.end_fx:
                self.player.score += 30
                self.timer = 1
                self.end_fx = True
        else: 
            self.animate_overlay()

        if self.end_fx:
            self.timer -= self.player.game.dt
            if self.timer < 0:
                self.player.effects_to_remove.append(self)

    def animate_overlay(self):
        if self.player.score - self.player_prev_score > 0:
            self.current_frame = (self.current_frame + (self.player.score - self.player_prev_score)) % len(self.curr_sprite_set)
            self.curr_overlay_img = self.curr_sprite_set[self.current_frame]

            # take away the point scored during the fx
            self.player.score -= 1
            self.player_prev_score = self.player.score

class Drop_coin_around_self():
    def __init__(self, player, duration, radius=50) -> None:
        self.player = player
        self.timer = duration
        # current frame of overlay
        self.last_frame_update = 0
        self.coin_spawn_interval = random.choice(range(60, 150))/1000
        self.radius = radius

    def update(self):
        self.timer -= self.player.game.dt
        self.last_frame_update += self.player.game.dt
        if self.timer < 0:
            self.player.effects_to_remove.append(self)
        elif self.last_frame_update > self.coin_spawn_interval:
            x = random.choice(range(
                max(int(-self.radius + self.player.position_x), self.player.game_world.game_area['left']),
                min(int(self.radius + self.player.position_x), self.player.game_world.game_area['right'])
            ))
            y = random.choice(range(
                max(int(-math.sqrt(self.radius**2 - (x+1 - self.player.position_x)**2) + self.player.position_y), self.player.game_world.game_area['top']), 
                min(int(math.sqrt(self.radius**2 - (x+1 - self.player.position_x)**2) + 1 + self.player.position_y), self.player.game_world.game_area['bottom'])
            ))      # the 1 in (x+1 - self.player.position_x)**2 is for adjusting the truncation by calling int() to choose random x
            self.player.game_world.coins.append(Coin(self.player.game, pos=(x,y)))
            self.last_frame_update = 0
            self.coin_spawn_interval = random.choice(range(60, 150))/1000

    def render_overlay(self, *args):
        pass        # no rendering needed

class Accumulation(Effect):
    def __init__(self, player, max_stack = 3) -> None:
        super().__init__(player, self.__class__.__name__.lower(), frame_interval=.07)
        self.max_stack = max_stack
        self.remaining = max_stack - 1
        for fx in self.player.applied_fx:
            if isinstance(fx, Accumulation):
                self.player.effects_to_remove.append(fx)
                self.remaining = fx.remaining - 1
        self.current_frame = 2 - self.remaining
        self.curr_overlay_img = self.curr_sprite_set[self.current_frame]  # 2 is the level-3 piggy bank img

    def update(self):
        self.last_frame_update += self.player.game.dt

        if self.curr_overlay_img == self.curr_sprite_set[-1] and self.last_frame_update > self.frame_interval:
            self.player.effects_to_remove.append(self)
        self.animate_overlay()

    def animate_overlay(self):
        if self.remaining == 0:
            super().animate_overlay(self.curr_sprite_set, loop=False)

class Immunity(Effect):
    def __init__(self, player) -> None:
        super().__init__(player, self.__class__.__name__.lower())
        self.used = False
        self.intro_sprites = self.curr_sprite_set[:4]
        self.iron_body_sprites = self.curr_sprite_set[4:10]
        self.fx_used_sprites = self.curr_sprite_set[10:]
        self.curr_sprite_set = self.intro_sprites

    def update(self):   
        self.last_frame_update += self.player.game.dt

        # check if the newly appended fx is negative
        if self.player.applied_fx[-1].fx_name in NEGATIVE_FX:
            self.player.applied_fx.pop()
            self.used = True
            self.curr_sprite_set = self.fx_used_sprites
            self.curr_overlay_img = self.fx_used_sprites[0]
            self.current_frame = 0
        if self.curr_overlay_img == self.fx_used_sprites[-1] and self.last_frame_update > self.frame_interval:
            self.player.effects_to_remove.append(self)
            return
        self.animate_overlay()

    def animate_overlay(self):
        # if the fx is still stored, loop the iron body fx
        if self.curr_sprite_set == self.intro_sprites:
            super().animate_overlay(self.curr_sprite_set, loop = False)
            if self.curr_overlay_img == self.curr_sprite_set[-1]:
                self.curr_sprite_set = self.iron_body_sprites
                self.curr_overlay_img = self.iron_body_sprites[0]
                self.current_frame = 0
        elif not self.used:
            super().animate_overlay(self.curr_sprite_set, loop = True)
        # if used, render the remaining sprites once
        else:
            super().animate_overlay(self.curr_sprite_set, loop = False)

class Enhance_reward():
    def __init__(self, player) -> None:
        super().__init__(player, self.__class__.__name__.lower())

    def effect_logic(self, delta_time, remove_list ):   
        ...

class Gain_coin_every_sec():
    def __init__(self, player, duration) -> None:
        super().__init__(player, self.__class__.__name__.lower())

    def effect_logic(self, delta_time, remove_list ):   
        ...

# -------------------------- Negative fx -------------------------------

class Example_Neg_FX():
    def __init__(self, player, duration) -> None:
        super().__init__(player, duration, self.__class__.__name__.lower())

    def effect_logic(self, delta_time, remove_list, ):   
        if self.player.immunity:
            remove_list.append(self)
            return
        ...
  
class Stolen():
    def __init__(self, player) -> None:
        super().__init__(player, self.__class__.__name__.lower())

    def effect_logic(self, delta_time, remove_list):
        ...

class Lose_coins_every_sec():
    def __init__(self, player, duration) -> None:
        super().__init__(player, self.__class__.__name__.lower())

    def effect_logic(self, delta_time, remove_list ):   
        ...

class Teleport_random():
    def __init__(self, player, duration) -> None:
        super().__init__(player, self.__class__.__name__.lower())

    def effect_logic(self, delta_time, remove_list ):   
        ...

class Stop_coin_drop():
    def __init__(self, player, duration) -> None:
        super().__init__(player, self.__class__.__name__.lower())

    def effect_logic(self, delta_time, remove_list ):   
        ...

class Coins_avoid_player():
    def __init__(self, player, duration) -> None:
        super().__init__(player, self.__class__.__name__.lower())

    def effect_logic(self, delta_time, remove_list ):   
        ...
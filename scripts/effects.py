import pygame, time

class Stun():
    def __init__(self, player, duration) -> None:
        self.player = player
        self.timer = duration
        self.sliding_timer = .75
        self.prev_directions = [0,0]
        self.got_prev_directions = False

        # current frame of overlay
        self.current_frame, self.last_frame_update = 0,0
        self.curr_overlay_img = None

    def update(self, delta_time, actions):
        self.timer -= delta_time
        self.sliding_timer -= delta_time
        if self.timer <= 0:
            self.player.stunned = False
            self.player.applied_fx.remove(self)
            return
        else:
            if self.got_prev_directions == False:
                self.prev_directions[0] = (actions['right'] - actions['left'])
                self.prev_directions[1] = (actions['down'] - actions['up'])
                self.got_prev_directions = True

            #                         <--------------------negate distance travelled -------------------->    <---------------------------add sliding distance---------------------------------->  
            self.player.position_x -= self.player.speed * delta_time * (actions['right'] - actions['left']) - self.player.speed * delta_time * max(0, self.sliding_timer)*self.prev_directions[0]
            self.player.position_y -= self.player.speed * delta_time * (actions['down'] - actions['up']) - self.player.speed * delta_time * max(0, self.sliding_timer)*self.prev_directions[1]
        
        # intercept the animation
        self.player.stunned = True
        if not (self.prev_directions[0] or self.prev_directions[1]):
            match self.player.current_anim_list:
                case self.player.front_sprites:
                    self.player.curr_image = self.player.stunned_img['front']
                case self.player.back_sprites:
                    self.player.curr_image = self.player.stunned_img['back']
                case self.player.right_sprites:
                    self.player.curr_image = self.player.stunned_img['right']
                case self.player.left_sprites:
                    self.player.curr_image = self.player.stunned_img['left']
        if self.prev_directions[0]:
            if self.prev_directions[0] > 0: self.player.curr_image = self.player.stunned_img['right']
            else: self.player.curr_image = self.player.stunned_img['left']
        if self.prev_directions[1]:
            if self.prev_directions[1] > 0: self.player.curr_image = self.player.stunned_img['front']
            else: self.player.curr_image = self.player.stunned_img['back']
        
        # update overlay
        self.curr_overlay_img = self.player.overlays['stunned'][self.current_frame]
        self.animate_overlay(delta_time)

    def animate_overlay(self, delta_time):
        self.last_frame_update += delta_time
        # Advance the animation if enough time has elapsed
        if self.last_frame_update > .15:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame +1) % len(self.player.overlays['stunned'])
            self.curr_overlay_img = self.player.overlays['stunned'][self.current_frame]

    def render_overlay(self, display):
        player_rect = self.player.rect()
        overlay_rect = self.curr_overlay_img.get_rect(midbottom = player_rect.midbottom)
        display.blit(self.curr_overlay_img, overlay_rect)
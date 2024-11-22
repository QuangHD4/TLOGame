import pygame, os, random

class Collectible:
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

class Coin(Collectible):
    def __init__(self, game, spawn_area=None, pos=None):
        super().__init__(game)
        if spawn_area:
            self.position_x = random.choice(range(spawn_area['left'], spawn_area['right']))
            self.position_y = random.choice(range(spawn_area['top'], spawn_area['bottom']))
        if pos:
            self.position_x = pos[0]
            self.position_y = pos[1]
        self.rect = pygame.Rect(self.position_x, self.position_y, 9, 9)

    def update(self,delta_time, actions):
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

class Spell(Collectible):
    def __init__(self, game, spawn_area):
        super().__init__(game)
        self.position_x = random.choice(range(spawn_area['left'], spawn_area['right']))
        self.position_y = random.choice(range(spawn_area['top'], spawn_area['bottom']))

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
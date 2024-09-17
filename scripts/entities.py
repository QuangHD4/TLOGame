import pygame, os

class Entity:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)  # Entity's rectangle (for collision and rendering)
        self.color = color
        self.speed = 5  # Movement speed

    def update(self, entities):
        keys = pygame.key.get_pressed()

        # Move entity based on input (WASD or Arrow keys)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Collision detection with other entities
        for entity in entities:
            if entity != self and self.rect.colliderect(entity.rect):
                print(f"Collision detected between entities at {self.rect} and {entity.rect}")

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Player():
    def __init__(self,game):
        self.game = game
        self.load_sprites()
        self.position_x, self.position_y = 200,200
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

    def animate(self, delta_time, direction_x, direction_y):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time
        # If no direction is pressed, set image to idle and return
        if not (direction_x or direction_y): 
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
            self.curr_image = self.curr_anim_list[self.current_frame]

    def load_sprites(self):
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

class Bot(Entity):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)

class Coin(Entity):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)

class Spell(Entity):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
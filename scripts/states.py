import pygame, os
from .entities import Player
from .collectibles import Coin, Spell

class State():
    def __init__(self, game):
        self.game = game
        self.prev_state = None

    def update(self, delta_time, actions):
        pass
    def render(self, surface):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()

class Title(State):
    def __init__(self, game):
        State.__init__(self, game)
        

    def update(self, delta_time, actions):
        if actions["start"]:
            new_state = Game_World(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render(self, display, actions):
        display.fill((255,255,255))
        self.game.draw_text(display, "Game States Demo", (0,0,0), self.game.GAME_W/2, self.game.GAME_H/2 )

class PauseMenu(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)
        # Set the menu
        self.menu_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "menu.png"))
        self.menu_rect = self.menu_img.get_rect()
        self.menu_rect.center = (self.game.GAME_W*.85, self.game.GAME_H*.4)
        # Set the cursor and menu states
        self.menu_options = {0 :"Party", 1 : "Items", 2 :"Magic", 3 : "Exit"}
        self.index = 0
        self.cursor_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "cursor.png"))
        self.cursor_rect = self.cursor_img.get_rect()
        self.cursor_pos_y = self.menu_rect.y + 38
        self.cursor_rect.x, self.cursor_rect.y = self.menu_rect.x + 10, self.cursor_pos_y

    def update(self, delta_time, actions):  
        self.update_cursor(actions)      
        if actions["action1"]:
            self.transition_state()
        if actions["action2"]:
            self.exit_state()
        self.game.reset_keys()

    def render(self, display):
        # render the gameworld behind the menu, which is right before the pause menu on the stack
        #self.game.state_stack[-2].render(display)
        self.prev_state.render(display)
        display.blit(self.menu_img, self.menu_rect)
        display.blit(self.cursor_img, self.cursor_rect)

    def transition_state(self):
        if self.menu_options[self.index] == "Party": 
            new_state = PartyMenu(self.game)
            new_state.enter_state()
        elif self.menu_options[self.index] == "Items": 
            pass # TO-DO
        elif self.menu_options[self.index] == "Magic": 
            pass # TO-DO
        elif self.menu_options[self.index] == "Exit": 
            while len(self.game.state_stack) > 1:
                self.game.state_stack.pop()


    def update_cursor(self, actions):
        if actions['down']:
            self.index = (self.index + 1) % len(self.menu_options)
        elif actions['up']:
            self.index = (self.index - 1) % len(self.menu_options)
        self.cursor_rect.y = self.cursor_pos_y + (self.index * 32)

class PartyMenu(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)

    def update(self, delta_time, actions):
        if actions["action2"]:
            self.exit_state()
        self.game.reset_keys()

    def render(self, display):
        display.fill((255,255,255))
        self.game.draw_text(display, "PARTY MENU GOES HERE", (0,0,0), self.game.GAME_W/2, self.game.GAME_H/2 )

class Game_World(State):
    def __init__(self, game):
        State.__init__(self,game)
        self.camera_scroll = [0,0]
        self.game_area = {'top': 25, 'bottom': self.game.GAME_H - 25, 'left': 100, 'right': self.game.GAME_W-100}
        self.scroll_area = {'top': 100, 'bottom': self.game.GAME_H - 100, 'left': 250, 'right': self.game.GAME_W - 250}
        self.scroll_time = 8

        self.player = Player(self.game, self)
        self.coins = [Coin(self.game, self.game_area)]
        self.spells = [Spell(self.game, self.game_area)]
        self.new_coin_interval = 0
        self.new_spell_interval = 0

        self.grass_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "grass.png"))

    def update(self,delta_time, actions):
        # apply scrolling, stop scrolling when player is near the border
        if self.player.position_x < self.scroll_area['left']:
            self.camera_scroll[0] += (self.scroll_area['left'] - self.game.GAME_W/2 - self.camera_scroll[0])/self.scroll_time
        elif self.player.position_x > self.scroll_area['right']:
            self.camera_scroll[0] += (self.scroll_area['right'] - self.game.GAME_W/2 - self.camera_scroll[0])/self.scroll_time
        else:
            self.camera_scroll[0] += (self.player.rect().centerx - self.game.GAME_W/2 - self.camera_scroll[0])/self.scroll_time

        if self.player.position_y < self.scroll_area['top']:
            self.camera_scroll[1] += (self.scroll_area['top'] - self.game.GAME_H/2 - self.camera_scroll[1])/self.scroll_time
        elif self.player.position_y > self.scroll_area['bottom']:
            self.camera_scroll[1] += (self.scroll_area['bottom'] - self.game.GAME_H/2 - self.camera_scroll[1])/self.scroll_time
        else:
            self.camera_scroll[1] += (self.player.rect().centery - self.game.GAME_H/2 - self.camera_scroll[1])/self.scroll_time

        # Check if the game was paused 
        if actions["start"]:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        self.player.update(delta_time, actions)

        # many coins
        self.new_coin_interval += delta_time
        if self.new_coin_interval > .75:
            new_coin = Coin(self.game, self.game_area)
            self.coins.append(new_coin)
            self.new_coin_interval = 0
        for coin in self.coins:
            coin.update(delta_time, actions)

        #spells
        self.new_spell_interval += delta_time
        if self.new_spell_interval > 1.5:
            new_spell = Spell(self.game, self.game_area)
            self.spells.append(new_spell)
            self.new_spell_interval = 0
        for spell in self.spells:
            spell.update(delta_time, actions)

    def render(self, display, actions):
        bg_window = (
            self.grass_img.get_rect().centerx - self.game.GAME_W/2 + self.camera_scroll[0], 
            self.grass_img.get_rect().centery - self.game.GAME_H/2 + self.camera_scroll[1],
            self.game.GAME_W,
            self.game.GAME_H
        )
        display.blit(self.grass_img, (0,0), bg_window)
        
        for coin in self.coins:
            coin.render(display, self.camera_scroll)

        for spell in self.spells:
            spell.render(display, self.camera_scroll)

        self.player.render(display, actions, self.camera_scroll)
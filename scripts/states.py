import pygame, os, pickle
from .entities import Player
from .collectibles import Coin, Spell
from .utils import load_img
from network import Network

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
        self.buttons = [
            {'name': 'rules','rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2, self.game.GAME_H*3/5 - 30/2, 160, 30), 'active_rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2 - 15, self.game.GAME_H*3/5 - 30/2 - 5, 160+30, 30+10), 'is_chosen':False},
            {'name': 'single_player','rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2, self.game.GAME_H*3/5 - 30/2 + 30*3/2, 160,30), 'active_rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2 - 15, self.game.GAME_H*3/5 - 30/2 + 30*3/2 - 5, 160+30, 30+10), 'is_chosen':False},
            {'name': 'multiplayer', 'rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2, self.game.GAME_H*3/5 - 30/2 + 30*3, 160,30), 'active_rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2 - 15, self.game.GAME_H*3/5 - 30/2 + 30*3 - 5, 160+30, 30+10), 'is_chosen':False}
        ]
        self.btn_font = pygame.font.SysFont('Consolas', 15, True)
        self.btn_index = 0

    def update(self, dt, actions):
        prev_btn_index = self.btn_index
        if actions['down']:
            self.btn_index = (self.btn_index + 1) % len(self.buttons)
        elif actions['up']:
            self.btn_index = (self.btn_index - 1) % len(self.buttons)
        self.buttons[prev_btn_index]['is_chosen'] = False
        self.buttons[self.btn_index]['is_chosen'] = True

        if actions['choose']:
            if self.btn_index == 0:
                pass
            elif self.btn_index == 1:
                new_state = Game_World(self.game)
                new_state.enter_state()
            elif self.btn_index == 2:
                Multiplayer_Game(self.game).enter_state()
                self.game.state_stack[-1].update(self.game.dt,self.game.actions)
        self.game.reset_keys()


    def render(self, display, actions):
        display.fill((255,255,255))
        self.game.draw_text(display, "Game States Demo", (0,0,0), self.game.GAME_W/2, self.game.GAME_H/3)

        for button in self.buttons:
            if button['is_chosen']:
                pygame.draw.rect(display, (181,230,29), button['active_rect'], width = 5, border_radius = 5)
                text = self.btn_font.render(button['name'], False, (181,230,29))
                display.blit(text, text.get_rect(center = button['rect'].center))
            else:
                pygame.draw.rect(display, (0,0,0), button['rect'], width = 5, border_radius = 5)
                text = self.btn_font.render(button['name'], False, (0,0,0))
                display.blit(text, text.get_rect(center = button['rect'].center))


    '''def handle_button_click(self):
        if event.type == pygame.MOUSEBUTTONDOWN: 
            if input_rect.collidepoint(event.pos): 
                active = True
            else: 
                active = False
  
        if event.type == pygame.KEYDOWN: 
  
            # Check for backspace 
            if event.key == pygame.K_BACKSPACE: 
  
                # get text input from 0 to -1 i.e. end. 
                user_text = user_text[:-1] 
  
            # Unicode standard is used for string 
            # formation 
            else: 
                user_text += event.unicode'''

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
        State.__init__(self, game)
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

    def update(self, delta_time, actions):
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
        '''if actions["start"]:
            new_state = PauseMenu(self.game)
            new_state.enter_state()'''
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

class Multiplayer_Game(Game_World):
    def __init__(self, game):
        super().__init__(game)

        # NOTE: make new sprites so players can tell themselves apart
        # NOTE: coins and spell spawn may be better handled by server

        self.n = Network()
        self.player_id = int(self.n.getP())

    def update(self, delta_time, actions):
        super().update(delta_time, actions)
        # try:
            # send player data and get a list of other players' data (Player obj)
        
        self.other_players = self.n.send(self.encode_player_data())
        # self.other_players = self.n.send(pickle.dumps(self.player))
        '''except:
            print('Shit! Something went terribly wrong.')'''

    def render(self, display, actions):
        super().render(display, actions)
        for player_id in self.other_players:
            player_img = load_img(self.other_players[player_id]['curr_player_img_addr'])
            x = self.other_players[player_id]['pos'][0] - self.camera_scroll[0]
            y = self.other_players[player_id]['pos'][1] - self.camera_scroll[1]
            player_rect = display.blit(player_img, (x,y))

            for fx in self.other_players[player_id]['curr_overlay_img_addr']:
                overlay_img = load_img(fx)
                overlay_rect = overlay_img.get_rect(center = player_rect.center)
                display.blit(overlay_img, overlay_rect)

    def encode_player_data(self):
        player_data = {
            'pos':(self.player.position_x, self.player.position_y),
        }

        curr_player_img_addr = 'player/'
        if self.player.curr_anim_list == self.player.front_sprites:
            curr_player_img_addr += 'front/' + str(self.player.current_frame) + '.png'
        elif self.player.curr_anim_list == self.player.back_sprites:
            curr_player_img_addr += 'back/' + str(self.player.current_frame) + '.png'
        elif self.player.curr_anim_list == self.player.left_sprites:
            curr_player_img_addr += 'left/' + str(self.player.current_frame) + '.png'
        elif self.player.curr_anim_list == self.player.right_sprites:
            curr_player_img_addr += 'right/' + str(self.player.current_frame) + '.png'
        elif self.player.curr_image in self.player.stunned_img.values():
            curr_player_img_addr += 'stunned' + list(self.player.stunned_img.keys())[list(self.player.stunned_img.values()).index(self.player.curr_image)] + '.png'
        player_data['curr_player_img_addr'] = curr_player_img_addr

        curr_overlay_img_addr = ['overlays/']*len(self.player.applied_fx)
        for order, effect in enumerate(self.player.applied_fx):
            curr_overlay_img_addr[order] += effect.fx_name + '/' + str(effect.curr_sprite_set.index(effect.curr_overlay_img)) + '.png'
        player_data['curr_overlay_img_addr'] = curr_overlay_img_addr

        return player_data
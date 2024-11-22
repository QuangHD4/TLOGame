import pygame, os, pickle
from .entities import Player, Bot
from .collectibles import Coin, Spell
from .utils import load_img

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
            {'name': 'play','rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2, self.game.GAME_H*3/5 - 30/2 + 30*3/2, 160,30), 'active_rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2 - 15, self.game.GAME_H*3/5 - 30/2 + 30*3/2 - 5, 160+30, 30+10), 'is_chosen':False},
        ]
        self.btn_font = pygame.font.SysFont('Consolas', 15, True)
        self.instruction_font = pygame.font.SysFont('Consolas', 9, False)
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
                Rules(self.game).enter_state()
            elif self.btn_index == 1:
                Choose_Diff(self.game).enter_state()
        self.game.reset_keys()


    def render(self, display, actions):
        display.fill((255,255,255))
        self.game.draw_text(display, "TLO Game", (0,0,0), self.game.GAME_W/2, self.game.GAME_H/3)
        instruction_1 = self.instruction_font.render('press UP or DOWN to change option, ENTER to choose',True,(100,100,100))
        r = instruction_1.get_rect(center = (self.game.GAME_W/2, self.game.GAME_H-15))
        display.blit(instruction_1,r)

        for button in self.buttons:
            if button['is_chosen']:
                pygame.draw.rect(display, (181,230,29), button['active_rect'], width = 5, border_radius = 5)
                text = self.btn_font.render(button['name'], True, (181,230,29))
                display.blit(text, text.get_rect(center = button['rect'].center))
            else:
                pygame.draw.rect(display, (0,0,0), button['rect'], width = 5, border_radius = 5)
                text = self.btn_font.render(button['name'], True, (0,0,0))
                display.blit(text, text.get_rect(center = button['rect'].center))

class Rules(State):
    def __init__(self, game):
        super().__init__(game)
        self.rules_img = pygame.image.load('assets/rules.png')

    def update(self, dt, actions):
        if actions['choose']:
            self.exit_state()
        self.game.reset_keys()

    def render(self, display, actions):
        display.fill((255,233,194))
        r = self.rules_img.get_rect(center = (self.game.GAME_W/2, self.game.GAME_H/2))
        display.blit(self.rules_img, r)

class Choose_Diff(Title):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [
            {'name': 'startup (I)','rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2, self.game.GAME_H*3/5 - 30/2, 160, 30), 'active_rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2 - 15, self.game.GAME_H*3/5 - 30/2 - 5, 160+30, 30+10), 'is_chosen':False},
            {'name': 'enterprise (II)','rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2, self.game.GAME_H*3/5 - 30/2 + 30*3/2, 160,30), 'active_rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2 - 15, self.game.GAME_H*3/5 - 30/2 + 30*3/2 - 5, 160+30, 30+10), 'is_chosen':False},
            {'name': 'corporation (III)','rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2, self.game.GAME_H*3/5 - 30/2 + 30*3, 160,30), 'active_rect': pygame.rect.Rect(self.game.GAME_W/2 - 160/2 - 15, self.game.GAME_H*3/5 - 30/2 + 30*3 - 5, 160+30, 30+10), 'is_chosen':False}
        ]
        self.instruction_font_2 = pygame.font.SysFont('Consolas', 12, True)

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
                Game_World(self.game, difficulty='startup').enter_state()
            elif self.btn_index == 1:
                Game_World(self.game, difficulty='enterprise').enter_state()
            elif self.btn_index == 2:
                Game_World(self.game, difficulty='corporation').enter_state()
        self.game.reset_keys()

    def render(self, display, actions):
        super().render(display, actions)
        instruction_2 = self.instruction_font_2.render('CHOOSE DIFFICULTY',True,(100,100,100))
        r = instruction_2.get_rect(center = (self.game.GAME_W/2, self.game.GAME_H/2))
        display.blit(instruction_2,r)

class Game_World(State):
    def __init__(self, game, difficulty = 'corporation'):
        State.__init__(self, game)
        self.camera_scroll = [0,0]
        self.game_area = {'top': 25, 'bottom': self.game.GAME_H - 25, 'left': 100, 'right': self.game.GAME_W-100}
        self.scroll_area = {'top': 100, 'bottom': self.game.GAME_H - 100, 'left': 250, 'right': self.game.GAME_W - 250}
        self.scroll_time = 8

        self.difficulty = difficulty
        self.player = Player(self.game, self)
        self.bot = Bot(self.game, self, difficulty)
        self.coins = [Coin(self.game, self.game_area), Coin(self.game, self.game_area), Coin(self.game, self.game_area), Coin(self.game, self.game_area)]
        self.new_coin_interval = 0
        if difficulty == 'startup':
            self.new_coin_wait = 3
        if difficulty == 'enterprise':
            self.new_coin_wait = 2.5
        if difficulty == 'corporation':
            self.new_coin_wait = 2

        self.grass_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "grass.png"))

        self.leaderboard_font = pygame.font.SysFont('consolas', 9)
        self.curr_leaderboard = ['player', 'bot']
        self.end_game = False
        self.btn_font = pygame.font.SysFont('Consolas', 15, True)
        self.restart_options = [
            {'name': 'play again','rect': pygame.rect.Rect(self.game.GAME_W/3 - 160/2, self.game.GAME_H*2/3 - 30/2, 160, 30), 'active_rect': pygame.rect.Rect(self.game.GAME_W/3 - 160/2 - 5, self.game.GAME_H*2/3 - 30/2 - 5, 160+10, 30+10), 'is_chosen':True},
            {'name': 'return to menu','rect': pygame.rect.Rect(self.game.GAME_W*2/3 - 160/2, self.game.GAME_H*2/3 - 30/2, 160,30), 'active_rect': pygame.rect.Rect(self.game.GAME_W*2/3 - 160/2 - 5, self.game.GAME_H*2/3 - 30/2 - 5, 160+10, 30+10), 'is_chosen':False}
        ]
        self.btn_index = 0
        self.end_btn_wait = 1

    def update(self, delta_time, actions):
        if not self.end_game:
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

            # many coins
            self.new_coin_interval += delta_time
            if self.new_coin_interval > self.new_coin_wait:
                new_coin = Coin(self.game, self.game_area)
                self.coins.append(new_coin)
                self.new_coin_interval = 0
            for coin in self.coins:
                coin.update(delta_time, actions)
            
            # Reminder: implement end_game into each
            self.player.update(delta_time, actions)
            self.bot.update(delta_time)

            if self.player.score >= self.bot.score:
                self.curr_leaderboard = ['player','bot']
            else:
                self.curr_leaderboard = ['bot','player']

            self.check_end_game(end_goal = 1000)
        
        else:
            self.end_btn_wait -= self.game.dt
            if self.end_btn_wait >= 0:
                return
            
            prev_btn_index = self.btn_index
            if actions['left']:
                self.btn_index = (self.btn_index + 1) % len(self.restart_options)
            elif actions['right']:
                self.btn_index = (self.btn_index - 1) % len(self.restart_options)
            self.restart_options[prev_btn_index]['is_chosen'] = False
            self.restart_options[self.btn_index]['is_chosen'] = True

            if actions['choose']:
                if self.btn_index == 0:
                    self.exit_state()
                    Game_World(self.game, difficulty=self.difficulty).enter_state()
                elif self.btn_index == 1:
                    self.exit_state()
            #note: always reset_keys after handling events
            self.game.reset_keys()

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

        self.bot.render(display, actions, self.camera_scroll, rendered_by_others=True)
        self.player.render(display, actions, self.camera_scroll)

        self.print_leaderboard(display)

        if self.end_game:
            if self.winner == 'player':
                self.game.draw_text(display, 'You Win', (255,255,0), self.game.GAME_W/2, self.game.GAME_H/2)
            else:
                self.game.draw_text(display, 'You Lose :(', (0,0,0), self.game.GAME_W/2, self.game.GAME_H/2)

            if self.end_btn_wait <= 0:
                for button in self.restart_options:
                    if button['is_chosen']:
                        pygame.draw.rect(display, (255,255,255), button['active_rect'], border_radius = 5)
                        pygame.draw.rect(display, (181,230,29), button['active_rect'], width = 5, border_radius = 5)
                        text = self.btn_font.render(button['name'], False, (181,230,29))
                        display.blit(text, text.get_rect(center = button['rect'].center))
                    else:
                        pygame.draw.rect(display, (255,255,255), button['rect'], border_radius = 5)
                        pygame.draw.rect(display, (0,0,0), button['rect'], width = 5, border_radius = 5)
                        text = self.btn_font.render(button['name'], False, (0,0,0))
                        display.blit(text, text.get_rect(center = button['rect'].center))

    def check_end_game(self, end_goal = 1000):
        if self.player.score >= end_goal:
            self.end_game = True
            self.winner = 'player'
        elif self.bot.score >= end_goal:
            self.end_game = True
            self.winner = 'bot'

    def print_leaderboard(self, display):
        '''for i in range(2):
            display.blit(self.leaderboard_font.render(f'{i+1}', False, (0,0,0)), (self.game.GAME_W - 100, 21+i*16))
        if prev_leaderboard != self.curr_leaderboard:
            pass
        prev_leaderboard = self.curr_leaderboard'''
        for i, entity_id in enumerate(self.curr_leaderboard):
            if entity_id == 'player':
                temp_surf = pygame.Surface((90, 15), pygame.SRCALPHA)
                pygame.draw.rect(
                    temp_surf, 
                    (255,255,175), 
                    (0, 0, 90, 15),
                    border_radius = 5,
                )
                temp_surf.set_alpha(160)
                display.blit(temp_surf, (self.game.GAME_W - 105, 17+i*16))
                name = display.blit(self.leaderboard_font.render('You', True, (0,0,0)), (self.game.GAME_W - 75, 21+i*16))
                icon_rect = self.player.icon.get_rect(centery = name.centery, centerx = self.game.GAME_W - 85)
                display.blit(self.player.icon, icon_rect)
                score = self.leaderboard_font.render(str(self.player.score), True, (0,0,0))
                score_rect = score.get_rect(right = self.game.GAME_W - 20, top = 21+i*16)
                display.blit(score, score_rect)
            else:
                name = display.blit(self.leaderboard_font.render('Bot', True, (0,0,0)), (self.game.GAME_W - 75, 21+i*16))
                icon_rect = self.bot.icon.get_rect(centery = name.centery, centerx = self.game.GAME_W - 85)
                display.blit(self.bot.icon, icon_rect)
                score = self.leaderboard_font.render(str(self.bot.score), True, (0,0,0))
                score_rect = score.get_rect(right = self.game.GAME_W - 20, top = 21+i*16)
                display.blit(score, score_rect)

            display.blit(self.leaderboard_font.render(f'{i+1}', False, (0,0,0)), (self.game.GAME_W - 100, 21+i*16))

import os, time, pygame
from scripts.states import Title

class Game():
    def __init__(self):
        pygame.init()
        self.GAME_W,self.GAME_H = 540, 360
        self.SCREEN_WIDTH,self.SCREEN_HEIGHT = 1080, 720
        self.game_canvas = pygame.Surface((self.GAME_W,self.GAME_H))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,self.SCREEN_HEIGHT))
        self.running, self.playing = True, True
        self.actions = {
            "left": False, "right": False, "up" : False, "down" : False,
            "action1" : False, "action2" : False, "choose" : False,
            'a':0, 'b':0, 'c':0, 'd':0, 'answered': False
        }
        self.dt, self.prev_time = 0, 0
        self.state_stack = []
        self.load_assets()
        self.load_states()

        self.clock = pygame.time.Clock()

    def game_loop(self):
        while self.playing:
            self.get_dt()
            self.get_events()
            self.update()
            self.render()

            self.clock.tick(60)

    def get_events(self):
        if self.actions['answered']:
            self.actions['a'], self.actions['b'], self.actions['c'], self.actions['d'] = 0,0,0,0
            self.actions['answered'] = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False
                if event.key == pygame.K_LEFT:
                    self.actions['left'] = True
                if event.key == pygame.K_RIGHT:
                    self.actions['right'] = True
                if event.key == pygame.K_UP:
                    self.actions['up'] = True
                if event.key == pygame.K_DOWN:
                    self.actions['down'] = True
                if event.key == pygame.K_p:
                    self.actions['action1'] = True
                if event.key == pygame.K_o:
                    self.actions['action2'] = True
                if event.key in (options := [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d]):
                    try:
                        if len(self.state_stack[-1].player.question_queue) > 0:
                            options.remove(event.key)
                            for option in options:
                                self.actions[pygame.key.name(option)] = 0
                            self.actions[pygame.key.name(event.key)] += 1
                            if self.actions[pygame.key.name(event.key)] == 2:
                                self.actions['answered'] = True
                    except AttributeError:
                        pass
                if event.key == pygame.K_RETURN:
                    self.actions['choose'] = True
                if event.key == pygame.K_TAB:
                    self.actions['multiplayer'] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.actions['left'] = False
                if event.key == pygame.K_RIGHT:
                    self.actions['right'] = False
                if event.key == pygame.K_UP:
                    self.actions['up'] = False
                if event.key == pygame.K_DOWN:
                    self.actions['down'] = False
                if event.key == pygame.K_p:
                    self.actions['action1'] = False
                if event.key == pygame.K_o:
                    self.actions['action2'] = False
                if event.key == pygame.K_RETURN:
                    self.actions['choose'] = False  
                if event.key == pygame.K_TAB:
                    self.actions['multiplayer'] = False

    def update(self):
        self.state_stack[-1].update(self.dt,self.actions)

    def render(self):
        self.state_stack[-1].render(self.game_canvas, self.actions)
        # Render current state to the screen
        self.screen.blit(pygame.transform.scale(self.game_canvas,(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0,0))
        pygame.display.flip()

    def get_dt(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now

    def draw_text(self, surface, text, color, x, y):
        text_surface = self.font.render(text, True, color)
        #text_surface.set_colorkey((0,0,0))
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)

    def load_assets(self):
        # Create pointers to directories 
        self.assets_dir = os.path.join("assets")
        self.sprite_dir = os.path.join(self.assets_dir, "sprites")
        self.font_dir = os.path.join(self.assets_dir, "font")
        self.font= pygame.font.Font(os.path.join(self.font_dir, "PressStart2P-vaV7.ttf"), 20)

    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False


if __name__ == "__main__":
    g = Game()
    while g.running:
        g.game_loop()
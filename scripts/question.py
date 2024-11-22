import pygame, random, os, csv

class Question:
    def __init__(self, game, player) -> None:
        self.game = game
        self.player = player
        # self.key_word = random.choices(ALL_EFFECTS, weight)
        self.question = random.choice(self.questions())
        self.font = pygame.font.SysFont('Consolas', 10, bold=True, italic=False)
        self.options = [self.question['a'], self.question['b'], self.question['c'], self.question['d']]
        random.shuffle(self.options)
        for i in range(len(self.options)):
            if self.question['correct'] == self.options[i]:
                self.correct_option = i
        self.end_display_timer = 3

    def correct(self):
        if self.game.actions['a'] == 2:
            self.correct = self.question['correct'] == self.options[0]
            self.player_chose = 0
            return self.correct
        elif self.game.actions['b'] == 2:
            self.correct = self.question['correct'] == self.options[1]
            self.player_chose = 1
            return self.correct
        elif self.game.actions['c'] == 2:
            self.correct = self.question['correct'] == self.options[2]
            self.player_chose = 2
            return self.correct
        elif self.game.actions['d'] == 2:
            self.correct = self.question['correct'] == self.options[3]
            self.player_chose = 3
            return self.correct            

    def render(self, display):
        words = self.question['question'].split()

        # now, construct lines out of these words
        lines = []

        while len(words) > 0:
            # get as many words as will fit within allowed_width
            line_words = []
            while len(words) > 0:
                line_words.append(words.pop(0))
                fw, fh = self.font.size(' '.join(line_words + words[:1]))
                if fw > self.game.GAME_W-160:
                    break
            # add a line consisting of those words
            line = ' '.join(line_words)
            lines.append(line)

        #bg
        bg_rect = pygame.rect.Rect(20, 15, self.game.GAME_W-140, 65 + 10*(len(lines)-1))
        pygame.draw.rect(display, (255,235,185), bg_rect, border_radius=10)

        y_offset = 0
        for i, line in enumerate(lines):
            fw, fh = self.font.size(line)
            line_spacing = 5

            # (tx, ty) is the top-left of the font surface
            tx = 30 + 10*(i == 0)
            ty = 25 + y_offset + i*line_spacing

            font_surface = self.font.render(line, True, (0,0,0))
            display.blit(font_surface, (tx, ty))

            y_offset += fh
                

        #handle spacing
        option_rect_width = 85
        margin = 10
        spacing = (bg_rect.width - 2*margin - 4*option_rect_width)/3
        # draw options rect + txt
        for i in range(4):  #num of options
            option_bg_rect = pygame.draw.rect(display, (255,200,50), (bg_rect.x + margin + int(option_rect_width+spacing)*i, bg_rect.y + 30 + 10*(len(lines)-1), option_rect_width, 25), border_radius=7)
            if self.options[i] == 'stand above the crowd':
                rendered_option_txt_1 = self.font.render('stand above',True, (55,55,55))
                rendered_option_txt_2 = self.font.render('the crowd', True, (55,55,55))
                option_txt_rect_1 = rendered_option_txt_1.get_rect(centerx = option_bg_rect.centerx, centery = option_bg_rect.centery - 5)
                option_txt_rect_2 = rendered_option_txt_2.get_rect(centerx = option_bg_rect.centerx, centery = option_bg_rect.centery + 5)
                display.blit(rendered_option_txt_1, option_txt_rect_1)
                display.blit(rendered_option_txt_2, option_txt_rect_2)
            elif self.options[i] == 'counterintuitive':
                rendered_option_txt_1 = self.font.render('counter-',True, (55,55,55))
                rendered_option_txt_2 = self.font.render('intuitive', True, (55,55,55))
                option_txt_rect_1 = rendered_option_txt_1.get_rect(centerx = option_bg_rect.centerx, centery = option_bg_rect.centery - 5)
                option_txt_rect_2 = rendered_option_txt_2.get_rect(centerx = option_bg_rect.centerx, centery = option_bg_rect.centery + 5)
                display.blit(rendered_option_txt_1, option_txt_rect_1)
                display.blit(rendered_option_txt_2, option_txt_rect_2)
            else:
                rendered_option_txt = self.font.render(self.options[i],True, (55,55,55))
                option_txt_rect = rendered_option_txt.get_rect(center = option_bg_rect.center)
                display.blit(rendered_option_txt, option_txt_rect)

        #render correct option when answered
        if self not in self.player.question_queue:
            self.end_display_timer -= self.game.dt
            if self.end_display_timer <= 0:
                self.player.answered_q = None
            if not self.correct:
                pygame.draw.rect(display, (255,0,0), (bg_rect.x + margin + int(option_rect_width+spacing)*self.player_chose-4, bg_rect.y + 30+2 + 10*(len(lines)-1) - 4, option_rect_width+2*4, 20+2*4), width = 4, border_radius=10)
                pygame.draw.rect(display, (181,230,29), (bg_rect.x + margin + int(option_rect_width+spacing)*self.correct_option-4, bg_rect.y + 30+2 + 10*(len(lines)-1) -4, option_rect_width+2*4, 20+2*4), width = 4, border_radius=10)
                self.game.actions['a'] = 0
                self.game.actions['b'] = 0
                self.game.actions['c'] = 0
                self.game.actions['d'] = 0
        else:
            # draw hover overlay
            if self.game.actions['a'] == 1:
                pygame.draw.rect(display, (70,70,200), (bg_rect.x + margin + int(option_rect_width+spacing)*0 - 4, bg_rect.y + 2 + 30 + 10*(len(lines)-1) - 4, option_rect_width+2*4, 20+2*4), width = 4, border_radius=10)
            elif self.game.actions['b'] == 1:
                pygame.draw.rect(display, (70,70,200), (bg_rect.x + margin + int(option_rect_width+spacing)*1 - 4, bg_rect.y + 2+30 + 10*(len(lines)-1) - 4, option_rect_width+2*4, 20+2*4), width = 4, border_radius=10)
            elif self.game.actions['c'] == 1:
                pygame.draw.rect(display, (70,70,200), (bg_rect.x + margin + int(option_rect_width+spacing)*2 - 4, bg_rect.y + 2+30 + 10*(len(lines)-1) - 4, option_rect_width+2*4, 20+2*4), width = 4, border_radius=10)
            elif self.game.actions['d'] == 1:
                pygame.draw.rect(display, (70,70,200), (bg_rect.x + margin + int(option_rect_width+spacing)*3 - 4, bg_rect.y + 2+ 30 + 10*(len(lines)-1) - 4, option_rect_width+2*4, 20+2*4), width = 4, border_radius=10)   

    def questions(self):
        questions = []
        with open(os.path.join(self.game.assets_dir, 'questions/questions.csv'), encoding='utf-8') as file:
            for line in csv.DictReader(file):
                questions.append(line)
        print(questions)
        return questions
    

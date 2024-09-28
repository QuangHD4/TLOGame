import pygame, random, os, csv

class Question:
    def __init__(self, game) -> None:
        self.game = game
        # self.key_word = random.choices(ALL_EFFECTS, weight)      
        self.key_word = 'counterintuitive'
        self.question = random.choice(self.questions(self.key_word))
        self.font = pygame.font.SysFont('Consolas', 9, bold=False, italic=False)
        self.options = [self.question['a'], self.question['b'], self.question['c'], self.question['d']]
        random.shuffle(self.options)


    def correct(self, actions):
        if actions['a'] == 2:
            return self.question['correct'] == self.options[0]
        elif actions['b'] == 2:
            return self.question['correct'] == self.options[1]
        elif actions['c'] == 2:
            return self.question['correct'] == self.options[2]
        elif actions['d'] == 2:
            return self.question['correct'] == self.options[3]
            

    def render(self, display, actions):
        #bg
        bg_rect = pygame.rect.Rect(75, 15, self.game.GAME_W-150, 60)
        pygame.draw.rect(display, (127,127,50), bg_rect)
        #question
        display.blit(self.font.render(self.question['question'], False, (55,55,55)), (bg_rect.x+10, bg_rect.y+10))

        #handle spacing
        option_rect_width = 60
        margin = 30
        spacing = (bg_rect.width - 2*margin - 4*option_rect_width)/3
        # draw options rect + txt
        for i in range(4):  #num of options
            option_bg_rect = pygame.draw.rect(display, (50,200,50), (bg_rect.x + margin + int(option_rect_width+spacing)*i, bg_rect.y + 30, option_rect_width, 20))
            rendered_option_txt = self.font.render(self.options[i],False, (55,55,55))
            option_txt_rect = rendered_option_txt.get_rect(center = option_bg_rect.center)
            display.blit(rendered_option_txt, option_txt_rect)
        # draw hover overlay
        if actions['a'] == 1:
            pygame.draw.rect(display, (70,70,200), (bg_rect.x + margin + int(option_rect_width+spacing)*0, bg_rect.y + 30, option_rect_width, 20), width = 5)
        elif actions['b'] == 1:
            pygame.draw.rect(display, (70,70,200), (bg_rect.x + margin + int(option_rect_width+spacing)*1, bg_rect.y + 30, option_rect_width, 20), width = 5)
        elif actions['c'] == 1:
            pygame.draw.rect(display, (70,70,200), (bg_rect.x + margin + int(option_rect_width+spacing)*2, bg_rect.y + 30, option_rect_width, 20), width = 5)
        elif actions['d'] == 1:
            pygame.draw.rect(display, (70,70,200), (bg_rect.x + margin + int(option_rect_width+spacing)*3, bg_rect.y + 30, option_rect_width, 20), width = 5)
        

    def load_images(self):
        sprite_dir = os.path.join(self.game.sprite_dir, "question")
        """self.images = {
            'background':pygame.image.load(os.path.join(sprite_dir, "bg.png")),
            'option_static':pygame.image.load(os.path.join(sprite_dir, "option_static.png")),
            'option_hover':pygame.image.load(os.path.join(sprite_dir, "option_hover.png"))
        }"""

    def questions(self,key_word:str):
        questions = []
        with open(os.path.join(self.game.assets_dir, 'questions', key_word + '.csv')) as file:
            for line in csv.DictReader(file):
                questions.append(line)
        return questions
    

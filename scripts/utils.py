import os, pygame

BASE_IMG_PATH = 'assets/sprites/'
PLAYER_SPEED = 100

def load_img(path):
    return pygame.image.load(BASE_IMG_PATH + path).convert_alpha()

def load_images(path):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(load_img(path + '/' + img_name))
    return images

class Button():
    def __init__(self, location, size:list, text:str='', is_chosen:bool=False) -> None:
        self.location = location
        self.size = size
        self.text = text
        self.is_chosen = is_chosen

    def render(self, display):
        pygame.draw.rect(display, (255,255,255), )
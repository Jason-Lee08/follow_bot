import pygame

class Display:
    def __init__(self):
        self.BLACK = (0, 0, 0)
        self.WHITE = (200, 200, 200)
        pygame.init()
        self.screen = pygame.display.set_mode((640, 240))
        self.font = pygame.font.SysFont('ubuntumono', 20)
        self.running = True
        self.x = 20
        self.y = 20
    
    def writeLine(self, text):
        rendered = self.font.render(text, True, self.BLACK)
        self.screen.blit(rendered, (self.x, self.y))
        self.y += 20
    
    def reset(self):
        self.x = 20
        self.y = 20
        self.screen.fill(self.WHITE)

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                self.running = False
    
    def update(self):
        pygame.display.update()
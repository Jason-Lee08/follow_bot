import sys
import pygame as pg
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255, 255, 255) 
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Visualization:
    def __init__(self):
        self.screenWidth = 2160 // 1.5
        self.screenLength = 2160 // 1.5
        self.midX = self.screenWidth // 2
        self.midY = self.screenLength // 2
        self.length = 45
        self.width = 60
        self.FPS = 60

        self.circleBorderThickness = 3
        self.lineThickness = 3

        self.p1 = [self.midX - self.length, self.midY - self.width]
        self.p2 = [self.midX + self.length, self.midY - self.width]
        self.p3 = [self.midX - self.length, self.midY + self.width]
        self.p4 = [self.midX + self.length, self.midY + self.width]

        pg.init()

        self.fps_clock = pg.time.Clock()
        self.screen = pg.display.set_mode((self.screenWidth, self.screenLength))

        self.font = pg.font.SysFont('ubuntumono', 20)
        self.x = 20
        self.y = 20

    def drawLines(self):
        pg.draw.line(self.screen, WHITE, self.p1, self.p2, self.lineThickness)
        pg.draw.line(self.screen, WHITE, self.p1, self.p3, self.lineThickness)
        pg.draw.line(self.screen, WHITE, self.p3, self.p4, self.lineThickness)
        pg.draw.line(self.screen, WHITE, self.p2, self.p4, self.lineThickness)

    def drawCircles(self, radii):
        pg.draw.circle(self.screen, RED, self.p1, radii[0], self.circleBorderThickness)
        pg.draw.circle(self.screen, RED, self.p2, radii[1], self.circleBorderThickness)
        pg.draw.circle(self.screen, RED, self.p3, radii[2], self.circleBorderThickness)
        pg.draw.circle(self.screen, RED, self.p4, radii[3], self.circleBorderThickness)

    def drawPhoneGuess(self, guess):
        pg.draw.circle(self.screen, GREEN, (guess[0] + self.midX, self.midY - guess[1]), 20)

    def updateScreen(self, sensorInput, guess, texts):
        self.x = 20
        self.y = 20
        self.screen.fill(WHITE)

        self.screen.fill(BLACK)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        
        any(self.writeLine(text) for text in texts)
        self.drawLines()
        self.drawCircles(sensorInput)
        self.drawPhoneGuess(guess)
        pg.display.flip()
        self.fps_clock.tick(self.FPS)
    
    def writeLine(self, text):
        rendered = self.font.render(text, True, WHITE)
        self.screen.blit(rendered, (self.x, self.y))
        self.y += 20

def generateRandomTestingRadii():
    return (np.random.rand(5) * 40   + 80).tolist()


if __name__ == "__main__":
    v = Visualization()
    v.__init__()

    sensorUpdate = [100, 90, 85, 130]

    while True:
        v.updateScreen(generateRandomTestingRadii())
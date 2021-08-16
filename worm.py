#!/usr/bin/env python

"""
worm.py
The classic game, written in python using pygame.
Written by Quinn Neufeld.
Oct. 5th, 2019
"""

import time
import random
import math

import pygame

SIZE = (640, 640)
BOARD_SIZE = (40, 40)
BLK_WIDTH = SIZE[0] // BOARD_SIZE[0]
BLK_HEIGHT = SIZE[1] // BOARD_SIZE[1]
WRM_SPD = 1
TPS = 15

pygame.display.init()

COLORS = {
    "white": pygame.color.Color(255, 255, 255),
    "black": pygame.color.Color(0, 0, 0),
    "red": pygame.color.Color(255, 0, 0)
}

class Segment:
    """Class for a single segment of a worm.
    x, y - starting coordinates of the segment on the screen
    screen - The screen to draw the segment on
    ahead - the segment ahead of this one (or None if there isn't one)"""
    def __init__(self, x, y, screen, ahead=None):
        self.x = x
        self.y = y
        self.ahead = ahead
        self.rect = pygame.Rect(math.floor(self.x * BLK_WIDTH), math.floor(self.y * BLK_HEIGHT), BLK_WIDTH, BLK_HEIGHT)
        self.get_next_move()

    def draw(self):
        """Draws the segment on the screen"""
        pygame.draw.rect(screen, COLORS["white"], (math.floor(self.x * BLK_WIDTH), math.floor(self.y * BLK_HEIGHT), BLK_WIDTH, BLK_HEIGHT))
    
    def move(self, x=None, y=None, draw=True):
        """Offset the segment's position by the internal mov values
        Or by positions if they're given
        Draws the segment if draw is true"""
        #Get x and y move values, either from args or from the object's memory
        if x == None:
            mov_x = self.mov_x
        else:
            mov_x = x
        if y == None:
            mov_y = self.mov_y
        else:
            mov_y = y
        
        self.x += mov_x
        self.y += mov_y
        if draw:
            self.draw()
    
    def get_next_move(self):
        """Returns the next move (or two Nones if there is no leading segment)
        Also updates the internal movement vals."""
        #Check that ahead exists
        if self.ahead == None:
            self.mov_x = None
            self.mov_y = None
            return None, None

        #Get difference in x and y values
        self.mov_x = self.ahead.x - self.x
        self.mov_y = self.ahead.y - self.y

        return self.mov_x, self.mov_y

class Worm:
    """Class for an entire worm."""
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.segs = []
    
    def spawn(self, n_segments=4):
        """Spawn the worm segments.
        A worm must spawn with at least two segments, otherwise issues could occur."""
        #Add the first segment
        self.segs.append(Segment(self.x, self.y, screen))
        self.lead_seg = self.segs[0]
        for _ in range(1, n_segments):
            self.add_segment()
        #Set first segment's follower segment
    
    def add_segment(self):
        """Add a segment to an existing worm."""
        last_seg = self.segs[-1]
        seg_movx, seg_movy = last_seg.get_next_move()
        #Check for a lead segment
        if seg_movx == None:
            seg_movx = -1
            seg_movy = 0
        else:
            seg_movx *= -1
            seg_movy *= -1

        seg_x = last_seg.x + seg_movx
        seg_y = last_seg.y + seg_movy

        #Add segment to segment list
        self.segs.append(Segment(seg_x, seg_y, screen, ahead=self.segs[-1]))
    
    def draw(self):
        """Draw the worm on the screen"""
        for seg in self.segs:
            seg.draw()

    def move(self, x: int, y: int, draw=False):
        """Move the worm a given x or y."""
        #Calculate updated positions
        for seg in self.segs[1:]:
            seg.get_next_move()
        #Move the first segment in a given direction
        self.lead_seg.move(x, y, draw=draw)
        #Move each segment
        for seg in self.segs[1:]:
            seg.move()
        
        if draw:
            self.draw()
    
    def eat_food(self):
        """Checks if the head of the snake is over food, and if it is, moves the food and increases the snake's length"""
        if self.lead_seg.x == food.x and self.lead_seg.y == food.y:
            food.move()
            self.add_segment()
            score.increase()
    
    def check_walls(self):
        """Checks to see if the snake has hit a wall"""
        #Check the walls
        if self.lead_seg.x < 0 or self.lead_seg.x >= BOARD_SIZE[0] or self.lead_seg.y < 0 or self.lead_seg.y >= BOARD_SIZE[1]:
            lose()

    def check_snake_collision(self):
        """Checks to see if the snake has run into itself"""
        #Check each snake segment that isn't the first one
        for seg in self.segs[1:]:
            if self.lead_seg.x == seg.x and self.lead_seg.y == seg.y:
                lose()

class Food:
    """Simple class to store information on the food."""
    def __init__(self):
        self.move()
    
    def draw(self):
        """Draws the food on the board"""
        pygame.draw.rect(screen, COLORS["red"], (self.x * BLK_WIDTH, self.y * BLK_HEIGHT, BLK_WIDTH, BLK_HEIGHT))

    def move(self):
        """Moves the food to a random position"""
        self.x = random.randint(0, BOARD_SIZE[0] - 1)
        self.y = random.randint(0, BOARD_SIZE[1] - 1)

class ScoreKeeper:
    """Class to store scoring information and drawing."""
    def __init__(self):
        self.score = 0
    
    def increase(self, redraw=True):
        """Increases the score by 1."""
        self.score += 1
        if redraw:
            self.draw()
    
    def draw(self):
        print("Score: " + str(self.score), end="\r", flush=False)

def lose():
    """Lose function. Quits the game and prints you lose and your final score."""
    #TODO: Make the window say you lose instead of the terminal.
    print("You lose.")
    pygame.quit()
    print("Your final score: " + str(score.score))
    exit()

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Worm")

worm = Worm(BOARD_SIZE[0] / 2, BOARD_SIZE[1] / 2, screen)
worm.spawn()

food = Food()

#Enable keyboard events only
pygame.event.set_allowed(None)
pygame.event.set_allowed(pygame.KEYDOWN)

#Snake direction
direction = (1, 0)
kbd_directon = pygame.K_RIGHT
cur_direction = kbd_directon

#Score object
score = ScoreKeeper()
score.draw()

while True:
    #Store loop start time
    start_time = time.time()
    #Process events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            exit()
        #Filter out non-keyboard events
        if e.type != pygame.KEYDOWN:
            continue
        #Change worm direction based on keypresses, and prevent the snake from doing a 180
        if e.key == pygame.K_UP and cur_direction != pygame.K_DOWN:
            direction = (0, -1)
            kbd_directon = e.key
        elif e.key == pygame.K_DOWN and cur_direction != pygame.K_UP:
            direction = (0, 1)
            kbd_directon = e.key
        elif e.key == pygame.K_LEFT and cur_direction != pygame.K_RIGHT:
            direction = (-1, 0)
            kbd_directon = e.key
        elif e.key == pygame.K_RIGHT and cur_direction != pygame.K_LEFT:
            direction = (1, 0)
            kbd_directon = e.key
        #Exit on escape press
        elif e.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()

    #Update current direction
    cur_direction = kbd_directon
    #Check loss conditions
    worm.check_snake_collision()
    worm.check_walls()
    #Move worm
    worm.move(direction[0], direction[1])
    #Clear screen
    screen.fill(COLORS["black"])
    #Check food
    worm.eat_food()
    #Draw worm and food
    worm.draw()
    food.draw()
    #Update display
    pygame.display.flip()
    #Sleep, subtracting the time it took to run the game loop
    time.sleep((1 / TPS) - (time.time() - start_time))
    

# Required Modules
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450 
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)

# Screen and Clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Code Escape!")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)

GAME_SCREEN = pygame.image.load("game_screen.jpg").convert()
GAME_SCREEN = pygame.transform.scale(GAME_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Player Class
class Student(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() # Inherit the parent class properties 

        # Player Image
        self.image = pygame.image.load("coding_boy.png")
        self.image = pygame.transform.scale(self.image, (40, 80))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 8
        self.rect.y = SCREEN_HEIGHT - 130

        # Jumping Variables
        self.is_jumping = False
        self.velocity = 0

    def update(self):
        keys = pygame.key.get_pressed()

        # Jump
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.is_jumping = True
            self.velocity = -22  # Influences jump height

        # Fast downward motion when ducking mid-air
        if keys[pygame.K_DOWN]:
            if self.is_jumping:
                self.velocity += 5

        # Apply gravity
        if self.is_jumping:
            self.velocity += 1
            self.rect.y += self.velocity
            if self.rect.y >= SCREEN_HEIGHT - 130:
                self.rect.y = SCREEN_HEIGHT - 130
                self.is_jumping = False
                self.velocity = 0

# Obstacle Class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type
        if type == "homework":
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT - 100
        elif type == "locker":
            self.image = pygame.Surface((30, 75))
            self.image.fill(RED)
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT - 250
        elif type == "backpack":
            self.image = pygame.Surface((40, 40))
            self.image.fill(RED)
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT - 100
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= (SCREEN_WIDTH // 2 + score) // 100  # Speed increases as score increases
        if self.rect.x < -self.rect.width:
            self.kill()
        
def text_to_screen(txt, colour, x, y, font_size):
    font = pygame.font.SysFont("arial", font_size)
    screen.blit(font.render(txt,True,colour),[x,y])

def start_screen(high_score, last_score):
    while True:
        # Displaying the Background Image of the Start Screen
        bg = pygame.image.load("start_screen.jpg")
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(bg, (0,0))
        
        #Displaying the High Score and Previous Score
        text_to_screen(f"{high_score}", WHITE, 330, 335, 30)
        text_to_screen(f"{last_score}", WHITE, 590, 335, 30)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
    
                # Check if user pressed play_button
                if 330 <= x and x <= 470 and 250 <= y and y <= 310:
                    return

# Main Game Loop
def main():
    global score
    score = 0
    high_score = 0
    last_score = 0

    while True:
        start_screen(high_score, last_score)

        # Sprite Groups
        all_sprites = pygame.sprite.Group()
        obstacles = pygame.sprite.Group()

        # Player Instance
        player = Student()
        all_sprites.add(player)

        # Obstacle Timer
        obstacle_timer = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.fill(WHITE)
            
            screen.blit(GAME_SCREEN, (0,0))
            # Update
            all_sprites.update()
            obstacles.update()

            # Spawn Obstacles
            obstacle_timer += 1
            if len(obstacles.sprites()) <= 2 and random.randint(0, 100) < 10 and obstacle_timer > 30:
                obstacle_type = random.choice(["homework", "locker", "backpack"])
                obstacle = Obstacle(obstacle_type)
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
                obstacle_timer = 0

            # Collision Detection
            if pygame.sprite.spritecollide(player, obstacles, False):
                running = False

            # Scoring
            score += 1
            high_score = max(high_score, score)

            # Draw Everything
            
            all_sprites.draw(screen)
            text_to_screen(f"Score {score}", BLACK, 10, 10, 36)
            text_to_screen(f"High Score: {high_score}", BLACK, 550, 10, 36)
            
            pygame.display.flip()
            clock.tick(FPS)

        last_score = score
        score = 0

if __name__ == "__main__":
    main()

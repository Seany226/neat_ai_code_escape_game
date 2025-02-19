# Required Modules
import pygame
import random
import sys
import neat
import os
import pickle

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

GAME_SCREEN = pygame.image.load(os.path.join("assets","game_screen.jpg")).convert()
GAME_SCREEN = pygame.transform.scale(GAME_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Player Class
class Student(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() # Inherit the parent class properties 

        # Player Image
        self.image = pygame.image.load(os.path.join("assets","coding_boy.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 80))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 8
        self.rect.y = SCREEN_HEIGHT - 127

        # Jumping Variables
        self.is_jumping = False
        self.velocity = 0

    def update(self):
        keys = pygame.key.get_pressed()

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and not self.is_jumping:
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
            if self.rect.y >= SCREEN_HEIGHT - 127:
                self.rect.y = SCREEN_HEIGHT - 127
                self.is_jumping = False
                self.velocity = 0

# Obstacle Class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type, player_type):
        super().__init__()
        self.type = type
        self.player_type = player_type
        if type == "smallvirus":
            self.image = pygame.image.load(os.path.join("assets","virus.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (55, 45))
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT - random.randint(100,125)
        elif type == "bigvirus":
            self.image = pygame.image.load(os.path.join("assets","virus.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (70, 60))
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT - random.randint(110,150)
        elif type == "cloud_error":
            self.image = pygame.image.load((os.path.join("assets","cloud_error.png"))).convert_alpha()
            self.image = pygame.transform.scale(self.image, (100, 50))
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT - random.randint(275,350)
        self.rect.x = SCREEN_WIDTH

    def update(self):
        if self.player_type == "ai":
            self.rect.x -= 3
        else:
            self.rect.x -= min(3 + score // 300, 9)  # Speed increases as score increases
        
        if self.rect.x < -self.rect.width:
            self.kill() # Remove the obstacle if it goes off screen

# Function to display text on the screen        
def text_to_screen(txt, colour, x, y, font_size):
    font = pygame.font.SysFont("arial", font_size)
    screen.blit(font.render(txt,True,colour),[x,y])

def start_screen(high_score, last_score):
    while True:
        # Displaying the Background Image of the Start Screen
        bg = pygame.image.load((os.path.join("assets","start_screen.jpg")))
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(bg, (0,0))
        
        #Displaying the High Score and Previous Score
        text_to_screen(f"{last_score}", WHITE, 330, 335, 30)
        text_to_screen(f"{high_score}", WHITE, 590, 335, 30)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
    
                # Check if user pressed play_button
                if 330 <= x and x <= 470 and 250 <= y and y <= 310:
                    return "game"
                
                if 495 <= x and x <= 650 and 250 <= y and y <= 310:
                    return "ai"

def game(high_score):
    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    # Player Instance
    player = Student()
    all_sprites.add(player)

    global score
    score = 0
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
        
        if len(obstacles.sprites()) == 0 or (random.randint(0, 100) < 5 and obstacles.sprites()[-1].rect.x < 0.7 * SCREEN_WIDTH):
            obstacle_type = random.choice(["smallvirus", "bigvirus", "cloud_error"])
            obstacle = Obstacle(obstacle_type, "human")
            all_sprites.add(obstacle)
            obstacles.add(obstacle)

        # Collision Detection
        if pygame.sprite.spritecollide(player, obstacles, False):
            running = False

        # Scoring
        score += 1
        high_score = max(high_score, score)

        # Draw Everything
        
        all_sprites.draw(screen)
        text_to_screen(f"Score: {score}", WHITE, 10, 10, 36)
        text_to_screen(f"High Score: {high_score}", WHITE, 550, 10, 36)
        
        pygame.display.flip()
        clock.tick(FPS)

    return score


def eval_genomes(genomes, config):
    screen.fill(WHITE)
    screen.blit(GAME_SCREEN, (0,0))
    
    nets = []
    students = []
    ge = []

    global score
    score = 0

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    # Obstacle Timer
    obstacle_timer = 0
    running = True
        

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        students.append(Student())
        ge.append(genome)
        all_sprites.add(students[-1])



    while running and len(students) > 0:
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        
        screen.fill(WHITE)
        screen.blit(GAME_SCREEN, (0,0))

        fitness_type = "cloud_error"

        # Spawn Obstacles
        obstacle_timer += 1
        if len(obstacles.sprites()) < 2 and random.randint(0, 100) < 5 and obstacle_timer > 50:
            obstacle_type = random.choice(["smallvirus", "cloud_error"]) # Remove bigvirus to simplify game for AI
            obstacle = Obstacle(obstacle_type, "ai")
            all_sprites.add(obstacle)
            obstacles.add(obstacle)
            obstacle_timer = 0
            for genome in ge:
                if obstacle_type != fitness_type:
                    genome.fitness += 2
                    fitness_type = obstacle_type
                else:
                    genome.fitness += 0.5

        # Scoring
        score += 1
       
        for x, player in enumerate(students):  # Give each student a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            
            if obstacles:
                obstacle = obstacles.sprites()[0]
                # inputs = (player.rect.y, player.velocity, obstacle.rect.y - player.rect.y, obstacle.rect.x - player.rect.x) # without normalization
            
                # Normalize inputs
                norm_player_y = player.rect.y / SCREEN_HEIGHT
                if player.velocity == 0:
                    norm_velocity = 0
                else:
                    norm_velocity = player.velocity / abs(player.velocity)
                norm_obstacle_y = obstacle.rect.y / SCREEN_HEIGHT
                norm_obstacle_x = (obstacle.rect.x - player.rect.x) / SCREEN_WIDTH
                inputs = (norm_player_y, norm_velocity, norm_obstacle_y, norm_obstacle_x)
            else:
                # inputs = (player.rect.y, player.velocity, SCREEN_HEIGHT, SCREEN_WIDTH) # without normalization
                norm_player_y = player.rect.y / SCREEN_HEIGHT
                if player.velocity == 0:
                    norm_velocity = 0
                else:
                    norm_velocity = player.velocity / abs(player.velocity)
                inputs = (norm_player_y, norm_velocity, 1, 1)  # Normalized values for no obstacle
                
            output = nets[students.index(player)].activate(inputs)

            # tanh activation is used function so result will be between -1 and 1            
            if output[0] > 0.75 and player.is_jumping == False:
                player.is_jumping = True
                player.velocity = -22
            
            if output[1] > 0.75 and player.is_jumping == True:
                player.velocity += 5
               

        # check for collision
        for player in students:
            # Collision Detection
            if pygame.sprite.spritecollide(player, obstacles, False):
                
                ge[students.index(player)].fitness -= 5
                nets.pop(students.index(player))
                ge.pop(students.index(player))
                students.pop(students.index(player))
                all_sprites.remove(player)
         # Update
        all_sprites.update()
        obstacles.update()

        all_sprites.draw(screen)
        text_to_screen(f"Score: {score}", WHITE, 10, 10, 36)
        text_to_screen(f"Alive: {len(nets)}", WHITE, 650, 10, 36)

        pygame.display.flip()
        clock.tick(FPS)
        if score > 10000:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            running = False
            break


def run_game(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 100 generations.
    winner = p.run(eval_genomes, 100)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

    return

# Main Game Loop
def main(config_path):
    high_score = 0
    last_score = 0

    while True:
        game_state = start_screen(high_score, last_score)
        
        if game_state == "game":
            last_score = game(high_score)
            high_score = max(high_score, last_score)
        elif game_state == "ai":
            run_game(config_path)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.txt')
    main(config_path)
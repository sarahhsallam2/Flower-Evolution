import pygame
from pygame import mixer
import random
import time
import math

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 100, 0)
LEAF_GREEN = (0, 200, 0)
GRAY = (200, 200, 200)
BUTTON_COLOR = (100, 200, 100)
BUTTON_HOVER_COLOR = (120, 220, 120)
SHADOW_COLOR = (50, 100, 50)

screen_width = 1450
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flower Evolution")

button_width = 350
button_height = 70
rect_width = 150
rect_height = 300

flower_count = 8  
spacing = screen_width // (flower_count + 0.3)  
fixed_y = screen_height // 2 + 100

mutation_rate=0.05

flower_positions = [(spacing * (i + 0.5), fixed_y + 50) for i in range(flower_count)] 
rect_positions = [(spacing * (i + 0.5) - rect_width // 2, fixed_y) for i in range(flower_count)]  

#1)we will be creating a Population for Flowers:
class Flower:
    def __init__(self, x, y):
        self.size_center = random.randint(10, 45)
        self.color_center = [random.randint(0, 255) for _ in range(3)]
        self.color_petals = [random.randint(0, 255) for _ in range(3)]
        self.num_petals = random.randint(0, 7)
        # this is a Position for center
        self.x = x  
        self.y = y  

        self.hover_time = 0  
        self.is_hovered = False  

    def display(self, screen):
        # this is the rectangle drawing
        rect_top_left = (self.x - rect_width // 2, self.y - rect_height // 2)
        pygame.draw.rect(screen, GRAY, (rect_top_left[0], rect_top_left[1], rect_width, rect_height), 2)

        # below is the drawing of stem inside the rectangle 
        stem_top = (self.x, self.y + self.size_center)
        stem_bottom = (self.x, self.y + 100)
        pygame.draw.line(screen, DARK_GREEN, stem_top, stem_bottom, 5)

        # Drawing petals inside the rectangle
        for i in range(self.num_petals):
            angle = (i / self.num_petals) * 2 * math.pi
            radius = self.size_center * 1.2
            petal_x = self.x + int(radius * math.cos(angle))
            petal_y = self.y - int(radius * math.sin(angle))
            pygame.draw.circle(screen, self.color_petals, (petal_x, petal_y), self.size_center // 2)

        # this is the center of the flower
        pygame.draw.circle(screen, self.color_center, (self.x, self.y), self.size_center)
        
  
    def __len__(self):
            return self.num_petals
        
    def check_hover(self, mouse_pos):
            distance = ((mouse_pos[0] - self.x) ** 2 + (mouse_pos[1] - self.y) ** 2) ** 0.5
            return distance < self.size_center


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = BUTTON_COLOR
        self.hovered = False

    def display(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        shadow_rect = self.rect.move(5, 5)
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=15)

        # The color on hover is changed in here
        current_color = BUTTON_HOVER_COLOR if self.hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=15)

        # Drawing the button text
        font = pygame.font.Font(None, 42)
        text_surface = font.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 20, self.rect.y + 20))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


# Selection: according to hovering 
def selection(population):
    population.sort(key=lambda x: x.hover_time, reverse=True)
    chosedParents= population[:4]
    return chosedParents
            

# Crossover which now considers all attributes (0 to 7)
def crossover(parent1, parent2):
    # Create child flowers at random positions
    child1 = Flower(random.randint(50, screen_width - 50), random.randint(50, screen_height - 50))
    child2 = Flower(random.randint(50, screen_width - 50), random.randint(50, screen_height - 50))

    # Choose a crossover point between 0 and 7
    crossover_point = random.randint(0, 7)
   

    # Perform crossover on 'size_center'
    if crossover_point == 0:
        child1.size_center = parent2.size_center
        child2.size_center = parent1.size_center
    else:
        child1.size_center = parent1.size_center
        child2.size_center = parent2.size_center

    # Perform crossover on 'color_center' if the crossover point affects this attribute (1-3)
    if 1 <= crossover_point <= 3:
        child1.color_center[:crossover_point] = parent1.color_center[:crossover_point]
        child1.color_center[crossover_point:] = parent2.color_center[crossover_point:]
        
        
        child2.color_center[:crossover_point] = parent2.color_center[:crossover_point]
        child2.color_center[crossover_point:] = parent1.color_center[crossover_point:]
    else:
        # If crossover point does not affect 'color_center', just inherit from the first parent
        child1.color_center = parent1.color_center[:]
        child2.color_center = parent2.color_center[:]

    # Perform crossover on 'color_petals' if the crossover point affects this attribute (4-6)
    if 4 <= crossover_point <= 6:
        petal_crossover_index = crossover_point - 3  # Map to 0-2
        child1.color_petals[:petal_crossover_index] = parent1.color_petals[:petal_crossover_index]
        child1.color_petals[petal_crossover_index:] = parent2.color_petals[petal_crossover_index:]
        #print('child1.color_petals[:petal_crossover_index]',child1.color_petals[:petal_crossover_index])
        
        
        child2.color_petals[:petal_crossover_index] = parent2.color_petals[:petal_crossover_index]
        child2.color_petals[petal_crossover_index:] = parent1.color_petals[petal_crossover_index:]
    else:
        # If crossover point does not affect 'color_petals', just inherit from the first parent
        child1.color_petals = parent1.color_petals[:]
        child2.color_petals = parent2.color_petals[:]

    # Perform crossover on 'num_petals' if crossover_point == 7
    if crossover_point == 7:
        child1.num_petals = parent2.num_petals
        child2.num_petals = parent1.num_petals
    else:
        # If crossover point does not affect 'num_petals', just inherit from the first parent
        child1.num_petals = parent1.num_petals
        child2.num_petals = parent2.num_petals

    return child1, child2


def mutate(new_population):
    for i in range(3):

        numberOfFlowerToMutate = random.randint(0, 7)
        geneToMutate = random.randint(0, 7)

        if geneToMutate == 0:
            new_population[numberOfFlowerToMutate].size_center = random.randint(10, 45)

        if geneToMutate in [1,2,3] :
            # Randomly creating colors for the center 
            new_population[numberOfFlowerToMutate].color_center[geneToMutate-1] = random.randint(0, 255)
        
        if geneToMutate in [4, 5, 6]:
            # Randomly creating colors for the petals
            new_population[numberOfFlowerToMutate].color_petals[geneToMutate-4] = random.randint(0, 255) 
        
        if geneToMutate == 7:
            new_population[numberOfFlowerToMutate].num_petals = random.randint(0, 7)    

    return new_population 
 
def evolve_population(population, positions):
    """Evolve the population through selection, crossover, and mutation while maintaining positions."""
    new_population = []

    selectedParents = selection(population)
    
    
    # keeping same positionsss
    for i in range(len(positions)):
        newFlower = Flower(positions[i][0], positions[i][1])
        
        # Copy genes from first flower
        newFlower.size_center = population[i].size_center
        newFlower.color_center = population[i].color_center[:]
        newFlower.color_petals = population[i].color_petals[:]
        newFlower.num_petals = population[i].num_petals
        newFlower.hover_time = 0  # Reset hover time

        new_population.append(newFlower)
        
#[0,1,2,3,4,5,6,7]
#[0,1,2,3,0,1,2,3] #population based on fitness
    # crossover 
    for i in range(0, len(new_population), 2):
        parent1 = selectedParents[i % 4] #population:8 because we take 4 from populations 
        parent2 = selectedParents[(i + 1) % 4]
        
        #We just want to crossover first 4 
        if i<4:
            child1, child2 = crossover(parent1, parent2)
        else:    
            child1, child2 = parent1, parent2
            child1.hover_time=0
            child1.is_hovered=False
            child2.hover_time=0
            child2.is_hovered=False
            
            
        # Assign the fixed positions to the new children
        child1.x, child1.y = new_population[i].x, new_population[i].y #put them in same positions as their parents 
        child2.x, child2.y = new_population[i + 1].x, new_population[i + 1].y

        new_population[i] = child1
        new_population[i + 1] = child2

    # mutation
    mutate(new_population)

    return new_population

population = [Flower(x, y) for x, y in flower_positions]
generation = 0
running = True
button = Button(screen_width // 2 - button_width // 2, 50, button_width, button_height, "Evolve New Generation")

# Main loop
while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button.is_clicked(mouse_pos):
                print(f"Evolving to Generation {generation + 1}")
                population = evolve_population(population, flower_positions)
                generation += 1

    for flower in population:
        flower.display(screen)
        if flower.check_hover(mouse_pos):
            if not flower.is_hovered:
                flower.start_hover_time = time.time()
                flower.is_hovered = True
            else:
                # Increment hover time while still hovering
                flower.hover_time += time.time() - flower.start_hover_time
                flower.start_hover_time = time.time()  # Reset for next frame
                
        else:
            if flower.is_hovered:
                flower.hover_time += time.time() - flower.start_hover_time
                flower.is_hovered = False

    font = pygame.font.Font(None, 35)
    for i, flower in enumerate(population):
        text = font.render(f"Flower {i + 1} Fitness: {round(flower.hover_time, 2)}s", True, BLACK)
        screen.blit(text, (10, 30 + i * 40))
    
    
    button.display(screen)
    generation_text = font.render(f"Generation: {generation}", True, BLACK)
    screen.blit(generation_text, (screen_width - 200, 20))

    pygame.display.flip()

pygame.quit()
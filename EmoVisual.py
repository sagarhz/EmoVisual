import pygame
import sys
import random
import numpy as np
from scipy.ndimage import gaussian_filter

pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EmoVisual")

EMOTIONS = {
    'anger': (255, 0, 0),    # Red
    'sadness': (0, 0, 255),  # Blue
    'joy': (255, 255, 0),    # Yellow
    'fear': (0, 255, 0),     # Green
    'love': (255, 105, 180)  # Pink
}

def create_fluid_surface(emotions_data, previous_surface):
    new_surface = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
    total = sum(emotions_data.values())
    
    if total == 0:
        return previous_surface if previous_surface is not None else new_surface

    for emotion, value in emotions_data.items():
        weight = value / total
        color = np.array(EMOTIONS[emotion]) / 255.0
        
        for _ in range(int(value * 20)):  
            x, y = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
            size = random.randint(20, 80) 
            
            y_start, y_end = max(0, y-size), min(HEIGHT, y+size+1)
            x_start, x_end = max(0, x-size), min(WIDTH, x+size+1)
            
            y_indices, x_indices = np.ogrid[y_start-y:y_end-y, x_start-x:x_end-x]
            mask = x_indices**2 + y_indices**2 <= size**2
            
            for i in range(3):  # Color channel
                new_surface[y_start:y_end, x_start:x_end, i] += mask * color[i] * weight * 0.5  # Increased intensity

    #Gaussian blur
    for i in range(3):
        new_surface[:,:,i] = gaussian_filter(new_surface[:,:,i], sigma=12)

    # Blend
    if previous_surface is not None:
        new_surface = previous_surface * 0.7 + new_surface * 0.1 

    #Convert
    new_surface = np.clip(new_surface, 0, 1)
    return new_surface

def main():
    emotions_data = {emotion: 0 for emotion in EMOTIONS}
    clock = pygame.time.Clock()
    previous_surface = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.unicode in '12345':
                    emotion = list(EMOTIONS.keys())[int(event.unicode) - 1]
                    emotions_data[emotion] += 1
                    print(f"Added {emotion}. Current values: {emotions_data}")

        fluid_surface = create_fluid_surface(emotions_data, previous_surface)
        previous_surface = fluid_surface.copy()

        pygame_surface = pygame.surfarray.make_surface((fluid_surface * 255).astype(np.uint8).swapaxes(0, 1))
        screen.blit(pygame_surface, (0, 0))

        font = pygame.font.Font(None, 24)
        for i, (emotion, value) in enumerate(emotions_data.items()):
            text = font.render(f"{emotion}: {value}", True, (255, 255, 255))
            screen.blit(text, (10, 10 + i * 30))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
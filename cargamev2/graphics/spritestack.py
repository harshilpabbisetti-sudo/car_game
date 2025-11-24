import sys
import os

import pygame

pygame.init()

screen = pygame.display.set_mode((500, 500), 0, 32)

# file = input()
images = [pygame.image.load(f'fuel/sprite_{i}.png') for i in range(0, 17)]

clock = pygame.time.Clock()


def render_stack(surf, image, pos, rotation, spread=1):
    for i, img in enumerate(image):
        rotated_img = pygame.transform.rotozoom(img, rotation, 2)
        surf.blit(rotated_img, (pos[0] - rotated_img.get_width() // 2, pos[1] - rotated_img.get_height() // 2 - i * spread))
        

frame = 0

while True:
    screen.fill((0, 0, 0))
    
    frame += 1
    
    render_stack(screen, images, (250, 250), frame, 3)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    screen.blit(pygame.transform.scale(screen, screen.get_size()), (0, 0))
    pygame.display.update()
    clock.tick(60)
    

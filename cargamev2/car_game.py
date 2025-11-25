import random
import math
import pygame
from sys import exit
import os

vector = pygame.math.Vector2


def linear_movement(keys, center, speed, acceleration):
    center.y += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        speed += acceleration
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        speed -= acceleration
    else:
        speed *= 0.75
    speed = max(min(speed, 20), -20)

    return center, speed


class Background(pygame.sprite.Sprite):
    def __init__(self, x_offset, y_offset):
        super().__init__()
        self.image = pygame.image.load('graphics/background.jpg').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.75)
        self.rect = self.image.get_rect(center=(540 + x_offset, 270 + y_offset))
        self.speed = 10

    def player_input(self, keys):
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y += self.speed
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y -= self.speed

    def generate(self):
        if self.rect.y + self.image.get_height() < 0:
            self.rect.y += self.image.get_height() * 2
        elif self.rect.y > screen.get_height():
            self.rect.y -= self.image.get_height() * 2
        elif self.rect.x + self.image.get_width() < 0:
            self.rect.x += self.image.get_width() * 2
        elif self.rect.x > screen.get_width():
            self.rect.x -= self.image.get_width() * 2

    def update(self, keys):
        self.player_input(keys)
        self.generate()


class Road(pygame.sprite.Sprite):
    def __init__(self, real_images, center, speed, acceleration, angular_velocity, start_dirn=vector(0, -1)):
        super().__init__()
        self.angle = round(start_dirn.angle_to(vector(0, -1)))
        self.angular_velocity = angular_velocity
        self.speed = speed
        self.acceleration = acceleration

        self.center = center
        self.screen_center = vector(screen.get_width()/2, screen.get_height()/2)

        self.real_images = real_images
        self.image = self.real_images[self.angle]
        self.rect = self.image.get_rect(center=self.center)

        self.screen_rect = screen.get_rect()

    def player_input(self, keys):
        (self.center, self.speed) = linear_movement(keys, self.center, self.speed, self.acceleration)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.angular_velocity
            self._rotation(-1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.angular_velocity
            self._rotation(1)

    def _rotation(self, sign):
        self.angle %= 360
        self.image = self.real_images[self.angle]
        pivot_center = self.center - self.screen_center
        pivot_center = pivot_center.rotate(-sign * self.angular_velocity)
        self.center = pivot_center + self.screen_center
        self.rect = self.image.get_rect(center=self.center)

    def drawing(self):
        if self.screen_rect.colliderect(self.rect):
            screen.blit(self.image, self.rect)
    def update(self, keys):
        self.player_input(keys)
        self.rect.center = self.center
        self.drawing()


class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.layer_images = [pygame.transform.rotozoom(pygame.image.load('graphics/car/' + img), 0, 2) for img in
                             os.listdir(f'graphics/car')]
        self.offset = 1
        self.center = (screen.get_width() / 2, screen.get_height() / 2)

        self.angle = 0
        self.angular_vel = 1
        self.image = self.layer_images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=self.center)

        self.left_wheel_offset = vector(-14, 20)
        self.right_wheel_offset = vector(14, 20)

    def drawing(self):
        self.image = pygame.transform.rotate(self.layer_images[0], self.angle)
        for i, img in enumerate(self.layer_images):
            img = pygame.transform.rotate(img, self.angle)
            screen.blit(img, img.get_rect(center=(self.center[0], self.center[1] - i * self.offset)))

    def player_input(self, keys):
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= self.angular_vel
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += self.angular_vel
        else:
            self.angle *= 0.75
        self.angle = max(min(self.angle, 30), -30)

    def update(self, keys):
        self.player_input(keys)
        self.drawing()
        if abs(self.angle) > 20:
            drift.add(DriftParticle(vector(self.center) + self.left_wheel_offset.rotate(-self.angle), speed, acceleration, angular_velocity))
            drift.add(DriftParticle(vector(self.center) + self.right_wheel_offset.rotate(-self.angle), speed, acceleration, angular_velocity))


class Fuel(pygame.sprite.Sprite):
    def __init__(self, images, pos, speed, acceleration, angular_velocity):
        super().__init__()
        self.images = images

        self.center = vector(pos[0]+random.randint(-50, 50), pos[1]+random.randint(-50, 50))
        self.screen_center = vector(screen.get_width()/2, screen.get_height()/2)

        self.speed = speed
        self.acceleration = acceleration
        self.angular_velocity = angular_velocity
        self.sprite_rotation = 0
        self.offset = 2
        self.rect = self.images[0][0].get_rect(center=self.center)

        self.screen_rect = screen.get_rect()

    def player_input(self, keys):
        (self.center, self.speed) = linear_movement(keys, self.center, self.speed, self.acceleration)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._rotation(1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._rotation(-1)

    def _rotation(self, sign):
        pivot_center = self.center - self.screen_center
        pivot_center = pivot_center.rotate(sign * self.angular_velocity)
        self.center = pivot_center + self.screen_center

    def drawing(self):
        self.sprite_rotation += 1
        self.sprite_rotation %= 360
        if self.screen_rect.colliderect(self.rect):
            for i in range(len(self.images)):
                screen.blit(self.images[i][self.sprite_rotation],
                            self.images[i][self.sprite_rotation].get_rect(center=(self.center[0],
                                                                                  self.center[1] - i * self.offset)))

    def update(self, keys):
        self.player_input(keys)
        self.drawing()
        self.rect.center = self.center


class DriftParticle(pygame.sprite.Sprite):
    def __init__(self, pos, speed, acceleration, angular_velocity):
        super().__init__()
        self.center = pos
        self.angle = 0
        self.angular_velocity = angular_velocity
        self.speed = speed
        self.acceleration = acceleration
        self.screen_center = vector(screen.get_width() / 2, screen.get_height() / 2)

        self.screen_rect = screen.get_rect()

    def player_input(self, keys):
        (self.center, self.speed) = linear_movement(keys, self.center, self.speed, self.acceleration)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.angular_velocity
            self._rotation(1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.angular_velocity
            self._rotation(-1)

    def _rotation(self, sign):
        pivot_center = self.center - self.screen_center
        pivot_center = pivot_center.rotate(sign * self.angular_velocity)
        self.center = pivot_center + self.screen_center

    def drawing(self):
        if self.screen_rect.collidepoint(self.center):
            pygame.draw.rect(screen, (0, 0, 0), (self.center.x, self.center.y, 3, 3))

    def destroy(self):
        if len(drift.sprites()) > 50:
            drift.sprites()[0].kill()

    def update(self, keys):
        self.player_input(keys)
        self.drawing()
        self.destroy()


class Hole(pygame.sprite.Sprite):
    def __init__(self, images, pos, speed, acceleration, angular_velocity):
        super().__init__()
        self.angle = 0
        self.angular_velocity = angular_velocity
        self.speed = speed
        self.acceleration = acceleration

        self.center = vector(pos[0]+random.randint(-50, 50), pos[1]+random.randint(-50, 50))
        self.screen_center = vector(screen.get_width() / 2, screen.get_height() / 2)

        self.real_images = images
        self.image = self.real_images[self.angle]
        self.rect = self.image.get_rect(center=self.center)

        self.screen_rect = screen.get_rect()

    def player_input(self, keys):
        (self.center, self.speed) = linear_movement(keys, self.center, self.speed, self.acceleration)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.angular_velocity
            self._rotation(-1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.angular_velocity
            self._rotation(1)

    def _rotation(self, sign):
        self.angle %= 360
        self.image = self.real_images[self.angle]
        pivot_center = self.center - self.screen_center
        pivot_center = pivot_center.rotate(-sign * self.angular_velocity)
        self.center = pivot_center + self.screen_center
        self.rect = self.image.get_rect(center=self.center)

    def drawing(self):
        if self.screen_rect.colliderect(self.rect):
            screen.blit(self.image, self.rect)

    def update(self, keys):
        self.player_input(keys)
        self.rect.center = self.center


class Cone(pygame.sprite.Sprite):
    def __init__(self, images, pos, speed, acceleration, angular_velocity):
        super().__init__()
        self.angle = 0
        self.angular_velocity = angular_velocity
        self.speed = speed
        self.acceleration = acceleration

        self.center = vector(pos[0]+random.randint(-50, 50), pos[1]+random.randint(-50, 50))
        self.screen_center = vector(screen.get_width() / 2, screen.get_height() / 2)

        self.images = images
        self.image = self.images[0][self.angle]
        self.rect = self.image.get_rect(center=self.center)
        self.offset = 3

        self.screen_rect = screen.get_rect()

    def player_input(self, keys):
        (self.center, self.speed) = linear_movement(keys, self.center, self.speed, self.acceleration)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.angular_velocity
            self._rotation(-1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.angular_velocity
            self._rotation(1)

    def _rotation(self, sign):
        self.angle %= 360
        pivot_center = self.center - self.screen_center
        pivot_center = pivot_center.rotate(-sign * self.angular_velocity)
        self.center = pivot_center + self.screen_center

    def drawing(self):
        if self.screen_rect.colliderect(self.rect):
            for i in range(len(self.images)):
                screen.blit(self.images[i][self.angle],
                            self.images[i][self.angle].get_rect(center=(self.center[0],
                                                                        self.center[1] - i * self.offset)))

    def update(self, keys):
        self.player_input(keys)
        self.drawing()
        self.rect.center = self.center


def fuel_collision(fuel_amt):
    if pygame.sprite.spritecollide(car.sprite, fuel, True):
        fuel_amt += 5
    return fuel_amt


def fuel_bar(fuel_amt, empty_bar, boxes):
    if fuel_amt > 9:
        fuel_amt = 9
    fuel_amt -= fuel_per_sec/fps
    screen.blit(empty_bar, (10, 10))
    for i in range(math.floor(fuel_amt)):
        screen.blit(boxes[i], (22 + 24 * i, 22))
    return fuel_amt


def car_boundaries():
    if not pygame.sprite.spritecollide(car.sprite, road, False, pygame.sprite.collide_mask):
        stop_on_collision([road, fuel, hole, cone, drift])
    if pygame.sprite.spritecollide(car.sprite, hole, False):
        if pygame.sprite.spritecollide(car.sprite, hole, False, pygame.sprite.collide_mask):
            stop_on_collision([road, fuel, hole, cone, drift])
    if pygame.sprite.spritecollide(car.sprite, cone, False):
        stop_on_collision([road, fuel, hole, cone, drift])


def stop_on_collision(groups):
    for group in groups:
        for sprite in group:
            if sprite.speed != 0:
                sprite.center.y -= 25 * (sprite.speed / abs(sprite.speed))
                sprite.speed = 0
                if hasattr(sprite, "rect"):
                    sprite.rect.center = sprite.center


def positioning_adding(speed, acceleration, angular_velocity):

    # image loading
    straight_road = pygame.image.load('graphics/road/straight_road.png').convert_alpha()
    straight_road_list = []
    for i in range(360):
        straight_road_list.append(pygame.transform.rotate(straight_road, i))

    right_road = pygame.image.load('graphics/road/right_turn.png').convert_alpha()
    right_road = pygame.transform.scale(right_road, (256, 256))
    right_road_list = []
    for i in range(360):
        right_road_list.append(pygame.transform.rotate(right_road, i))

    left_road = pygame.image.load('graphics/road/left_turn.png').convert_alpha()
    left_road = pygame.transform.scale(left_road, (256, 256))
    left_road_list = []
    for i in range(360):
        left_road_list.append(pygame.transform.rotate(left_road, i))

    fuel_list = []
    for i in range(0, 17):
        fuel_list.append(
            [pygame.transform.rotate(pygame.image.load(f'graphics/fuel/sprite_{i}.png').convert_alpha(), j) for j in
             range(360)])

    hole_image = pygame.image.load('graphics/hole.png').convert_alpha()
    hole_list = []
    for i in range(360):
        hole_list.append(pygame.transform.rotate(
            pygame.transform.rotozoom(hole_image, 0, 2), i))

    cone_list = []
    for i in range(0, 5):
        cone_list.append([pygame.transform.rotate(pygame.image.load(f'graphics/cones/sprite_{i}.png').convert_alpha(), j) for j in range(360)])

    # positioning
    track = [[2, 1, 2, 0, 0],
             [1, 0, 1, 0, 0],
             [1, 0, 3, 1, 2],
             [2, 1, 3, 0, 1],
             [0, 0, 1, 0, 1],
             [0, 0, 2, 1, 2]]
    track_key = {
        1: straight_road_list,
        2: right_road_list,
        3: left_road_list
    }

    dirn = [[0, 90, 90, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 180, 90, 90],
            [-90, 90, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, -90, 90, 180]]

    fuel_position = [[1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1]]

    hole_position = [[0, 0, 1, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 1, 0, 0]]

    cone_position = [[0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0]]

    # adding to classes
    background.add(Background(0, 0))
    background.add(Background(0 + screen.get_width(), 0))
    background.add(Background(0 + screen.get_width(), 0 + screen.get_height()))
    background.add(Background(0, 0 + screen.get_height()))

    for i in range(len(track)):
        for j in range(len(track[i])):
            if track[i][j]:
                road.add(Road(track_key[track[i][j]],
                              vector(540 + 256 * j,
                                     14 + 256 * i),
                              speed,
                              acceleration,
                              angular_velocity,
                              vector(0, -1).rotate(dirn[i][j])))
            if fuel_position[i][j]:
                fuel.add(Fuel(fuel_list, (540 + 256 * j, 14 + 256 * i), speed, acceleration, angular_velocity))
            if hole_position[i][j]:
                hole.add(Hole(hole_list, (540 + 256 * j, 14 + 256 * i), speed, acceleration, angular_velocity))
            if cone_position[i][j]:
                cone.add(Cone(cone_list, (540 + 256 * j, 14 + 256 * i), speed, acceleration, angular_velocity))


fuel_amt = 9
fps = 60
fuel_per_sec = 0.1

speed = 0
acceleration = 1
angular_velocity = 4

pygame.init()

screen = pygame.display.set_mode((1080, 540))
clock = pygame.time.Clock()
pygame.display.set_caption('Car Game')

font = pygame.font.Font('graphics/font/Pixeltype.ttf', 50)

background = pygame.sprite.Group()
road = pygame.sprite.Group()
fuel = pygame.sprite.Group()
hole = pygame.sprite.Group()
cone = pygame.sprite.Group()
car = pygame.sprite.GroupSingle()
car.add(Car())
drift = pygame.sprite.Group()

positioning_adding(speed, acceleration, angular_velocity)

empty_bar = pygame.transform.rotozoom(pygame.image.load('graphics/fuel_bar/empty_fuel_bar.png'), 0, 4)
boxes = []
for i in range(8):
    boxes.append(pygame.transform.rotozoom(pygame.image.load(f'graphics/fuel_bar/boxes/sprite_{i}.png').convert_alpha(), 0, 4))

game_msg = font.render('Game Over', False, (255, 255, 255))
game_msg_rect = game_msg.get_rect(center = (screen.get_width()/2, screen.get_height()/2))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    keys = pygame.key.get_pressed()

    car_boundaries()

    background.draw(screen)
    background.update(keys)

    road.update(keys)

    car.update(keys)

    fuel.update(keys)

    fuel_amt = fuel_collision(fuel_amt)
    fuel_amt = fuel_bar(fuel_amt, empty_bar, boxes)

    drift.update(keys)
    
    hole.update(keys)

    cone.update(keys)

    if fuel_amt < 1:
        screen.blit(game_msg, game_msg_rect)

    pygame.display.update()
    clock.tick(fps)

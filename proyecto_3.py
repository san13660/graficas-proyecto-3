# Christopher Sandoval 13660
# Proyecto 3

import pygame
from math import pi, cos, sin, atan2

show_map = False

window_width = 530
window_height = 400
window_largest_dimension = 530

input_1 = input('Mostrar mapa? (s/n): ')
input_2 = input('Resolucion default? (530x400) (s/n): ')

if input_1 == 's':
  show_map = True

if input_2 == 'n':
  input_3 = input('Ingrese el ancho: ')
  input_4 = input('Ingrese el alto: ')

  try:
    input_3 = int(input_3)
    input_4 = int(input_4)
    window_width = input_3
    window_height = input_4
    window_largest_dimension = input_4

  except:
    print('Resolucion invalida. Ejecutando con resolucion default (530x400).')


floor_color = (60, 40, 15)
ceiling_color = (60, 60, 60)



hand_width = 132
hand_height = 132

wall_width = 32
wall_height = 32

player_speed = 10

offset = 0

if show_map:
  offset = 500


pygame.init()
screen = pygame.display.set_mode((window_width + offset, window_height), pygame.DOUBLEBUF|pygame.HWACCEL|pygame.HWSURFACE)
screen.set_alpha(None)

#pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])


wall1 = pygame.image.load('./wall_1.png').convert()
wall2 = pygame.image.load('./wall_2.png').convert()
wall3 = pygame.image.load('./wall_3.png').convert()

textures = {
  "1": wall1,
  "2": wall2,
  "3": wall3
}

hand = pygame.image.load('./handaxe.png').convert()

enemies = [
  {
    "x": 100,
    "y": 200,
    "texture": pygame.image.load('./sprite_2.png').convert()
  },
  {
    "x": 280,
    "y": 190,
    "texture": pygame.image.load('./sprite_3.png').convert()
  },
  {
    "x": 320,
    "y": 360,
    "texture": pygame.image.load('./sprite_1.png').convert()
  }
]

class Raycaster(object):
  def __init__(self, screen):
    _, _, self.width, self.height = screen.get_rect()
    self.screen = screen
    self.blocksize = 50
    self.player = {
      "x": self.blocksize + 20,
      "y": self.blocksize + 20,
      "a": pi/3,
      "fov": pi/3
    }
    self.map = []
    self.zbuffer = [-float('inf') for z in range(0, window_width)]
    # self.clear()

  def clear(self):
    for x in range(self.width):
      for y in range(self.height):
        if y > self.height/2 or (show_map and x < 500):
          color = floor_color
        else:
          color = ceiling_color
        self.point(x, y, color)

  def point(self, x, y, c = None):
    screen.set_at((x, y), c)

  def draw_rectangle(self, x, y, texture):
    for cx in range(x, x + 50):
      for cy in range(y, y + 50):
        tx = int((cx - x)*wall_width / 50)
        ty = int((cy - y)*wall_height / 50)
        c = texture.get_at((tx, ty))
        self.point(cx, cy, c)

  def load_map(self, filename):
    with open(filename) as f:
      for line in f.readlines():
        self.map.append(list(line))

  def cast_ray(self, a):
    d = 0
    while True:
      x = self.player["x"] + d*cos(a)
      y = self.player["y"] + d*sin(a)

      i = int(x/50)
      j = int(y/50)

      if self.map[j][i] != ' ':
        hitx = x - i*50
        hity = y - j*50

        if 1 < hitx < 49:
          maxhit = hitx
        else:
          maxhit = hity

        tx = int(maxhit * wall_width / 50)

        return d, self.map[j][i], tx

      #self.point(int(x), int(y), (255, 255, 255))

      d += 1

  def draw_stake(self, x, h, texture, tx):
    start = int((window_height/2) - h/2)
    end = int((window_height/2) + h/2)
    for y in range(start, end):
      ty = int(((y - start)*wall_height)/(end - start))
      c = texture.get_at((tx, ty))
      self.point(x, y, c)

  def draw_sprite(self, sprite, sprite_height=160, sprite_width=160):
    sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])

    sprite_d = ((self.player["x"] - sprite["x"])**2 + (self.player["y"] - sprite["y"])**2)**0.5
    #print(sprite_d)
    if sprite_d > 20:
      sprite_size = (window_height/sprite_d) * 70

      sprite_x = offset + (sprite_a - self.player["a"])*window_width/self.player["fov"] + (window_width/2) - sprite_size/2
      sprite_y = (window_height/2) - sprite_size/2

      sprite_x = int(sprite_x)
      sprite_y = int(sprite_y)
      sprite_size = int(sprite_size)

      for x in range(sprite_x, sprite_x + sprite_size):
        for y in range(sprite_y, sprite_y + sprite_size):
          if offset < x < offset + window_width and self.zbuffer[x - offset] >= sprite_d:
            tx = int((x - sprite_x) * sprite_width/sprite_size)
            ty = int((y - sprite_y) * sprite_height/sprite_size)
            c = sprite["texture"].get_at((tx, ty))
            if c != (18, 249, 155, 255):
              self.point(x, y, c)
              self.zbuffer[x - window_width] = sprite_d

  def draw_player(self, xi, yi, w = hand_width, h = hand_height):
    for x in range(xi, xi + w):
      for y in range(yi, yi + h):
        tx = int((x - xi) * hand_width/w)
        ty = int((y - yi) * hand_height/h)
        c = hand.get_at((tx, ty))
        if c != (18, 249, 155, 255):
          self.point(x, y, c)

  def render(self, draw_map):
    if show_map:
      for x in range(0, 500, 50):
        for y in range(0, 500, 50):
          i = int(x/50)
          j = int(y/50)
          if self.map[j][i] != ' ':
            self.draw_rectangle(x, y, textures[self.map[j][i]])

      self.point(int(self.player["x"]), int(self.player["y"]), (255, 255, 255))

      for i in range(0, 500):
        self.point(500, i, (0, 0, 0))
        self.point(501, i, (0, 0, 0))
        self.point(499, i, (0, 0, 0))

    for i in range(0, window_width):
      a =  self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/window_width
      d, c, tx = self.cast_ray(a)
      x = offset + i
      if(d >= 10):
        factor = (d*cos(a-self.player["a"]))
        h = window_height/factor * 70
        self.draw_stake(x, h, textures[c], tx)
        self.zbuffer[i] = d
      else:
        break

    for enemy in enemies:
      if show_map:
        self.point(enemy["x"], enemy["y"], (250, 0, 0))
      self.draw_sprite(enemy)

    player_draw_width = int(window_width/3)
    player_draw_height = int(window_width/3)

    self.draw_player(int(offset + (window_width/2) - (player_draw_width/2.5)), window_height - player_draw_height, player_draw_width, player_draw_height)

r = Raycaster(screen)
r.load_map('./map.txt')

c = 0
while True:

  player_x_movement = 0
  player_y_movement = 0

  for e in pygame.event.get():
    if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
      exit(0)
    if e.type == pygame.KEYDOWN:
      if e.key == pygame.K_LEFT:
        r.player["a"] -= pi/10
      elif e.key == pygame.K_RIGHT:
        r.player["a"] += pi/10

      elif e.key == pygame.K_d:
        player_y_movement = sin(r.player["a"]+pi/2) * player_speed
        player_x_movement = cos(r.player["a"]+pi/2) * player_speed
      elif e.key == pygame.K_a:
        player_y_movement = sin(r.player["a"]-pi/2) * player_speed
        player_x_movement = cos(r.player["a"]-pi/2) * player_speed
      elif e.key == pygame.K_w:
        player_y_movement = sin(r.player["a"]) * player_speed
        player_x_movement = cos(r.player["a"]) * player_speed
      elif e.key == pygame.K_s:
        player_y_movement = -sin(r.player["a"]) * player_speed
        player_x_movement = -cos(r.player["a"]) * player_speed

  distance_check = r.cast_ray(r.player["a"])[0]

  if distance_check > 40:
    r.player["x"] += player_x_movement
    r.player["y"] += player_y_movement
  else:
    r.player["x"] -= player_x_movement
    r.player["y"] -= player_y_movement

  r.clear()
  r.render(show_map)

  pygame.display.flip()

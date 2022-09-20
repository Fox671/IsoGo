import pygame
from random import choice, randint
import os
from math import sqrt

class Player(pygame.sprite.Sprite):
	"""
	Base class every player sprite.

	Player(): return Player
	"""

	player_group = pygame.sprite.GroupSingle()
	x, y = 0, 0

	step = 0.04
	half_step = step/2

	def __init__(self):
		super().__init__()

		self.image = pygame.image.load("assets/test/character.png").convert_alpha()
		self.rect = self.image.get_rect(center = (screen.get_width()/2, screen.get_height()/2))
		Player.player_group.add(self)

	# every-frame function
	def update(self) -> None:
		keys = pygame.key.get_pressed()
		if keys[pygame.K_d]:
			Player.x += self.half_step
			Player.y += self.half_step
		if keys[pygame.K_a]:
			Player.x -= self.half_step
			Player.y -= self.half_step
		if keys[pygame.K_w]:
			Player.x -= self.step
			Player.y += self.step
		if keys[pygame.K_s]:
			Player.x += self.step
			Player.y -= self.step

class Object(pygame.sprite.Sprite):
	"""
	Base class for every game sprite except player sprite.

	Object((x, y)): return or create Object instance with x, y attributes
	"""

	tile_width = 237
	tile_height = 119

	def __init__(self, image: str, sound: str, coords: tuple) -> None:
		self.x, self.y = coords[0], coords[1]

		super().__init__()

		self.image = pygame.image.load(image)
		self.sound = pygame.mixer.Sound(sound)
		self.rect = self.image.get_rect(midbottom = (self.get_position(coords)))

		World.all_sprites[(self.x, self.y)] = self
		self.position_update()

	# return object position
	def get_position(self, coords: tuple) -> tuple:
		x = +coords[0]*Object.tile_width + coords[1]*Object.tile_width - Player.x*Object.tile_width - Player.y*Object.tile_width + 960
		y = -coords[1]*Object.tile_height + coords[0]*Object.tile_height + Player.y*Object.tile_height - Player.x*Object.tile_height + 540
		return x, y
	
	def visible_update(self) -> None:
		distance = sqrt((self.x - Player.x)**2 + (self.y - Player.y)**2)
		if distance > view_distance:
			World.object_group.remove(World.all_sprites[(self.x, self.y)])
		elif not World.all_sprites[(self.x, self.y)] in World.object_group.sprites():
			World.object_group.add(World.all_sprites[(self.x, self.y)])
	
	def position_update(self) -> None:
		if hasattr(self, "rect"):
			object_offset = self.get_position((self.x, self.y))
			self.rect.x = object_offset[0]
			self.rect.y = object_offset[1]
	
	def destroy(self) -> None:
		mouse = pygame.mouse.get_pressed()
		if mouse[0]:
			if self.rect.collidepoint(pygame.mouse.get_pos()):
				World.all_sprites[(self.x, self.y)] = "grass"
				self.sound.play()
				self.kill()

	# every-frame function
	def update(self) -> None:
		self.visible_update()
		self.position_update()
		self.destroy()

class World():
	"""
	Class for infity world generation. Every-frame class

	World()): return or create World instance
	"""

	object_group = pygame.sprite.Group()
	all_sprites = {}

	filenames = []
	for dirpath, dirnames, filenames in os.walk("assets/grass"):
		filenames.extend(filenames)
		break

	def __init__(self):
		for x in range(int(-view_distance*1.2+Player.x), int(view_distance*1.2+Player.x)):
			for y in range(int(-view_distance*1.2+Player.y), int(view_distance*1.2+Player.y)):
				if not (x, y) in World.all_sprites.keys():
					if randint(0, 4) != 0:
						type = choice(["assets/grass", "assets/flower"])
						image = os.path.join(type, choice(World.filenames)[:-4]+".png")
						sound = os.path.join(type, choice(World.filenames)[:-4]+".mp3")
						Object(image, sound, (x, y))
					else:
						World.all_sprites[(x, y)] = "grass"
				elif World.all_sprites[(x, y)] != "grass":
					World.all_sprites[(x, y)].visible_update()

# pygame init
pygame.init()
pygame.display.set_caption("IsoGo")
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN, vsync=1)
clock = pygame.time.Clock()	
player = Player()
view_distance = 5

# main loop
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			# exit event
			pygame.quit()
			exit()
	
	# generate terrain
	World()
	screen.fill(("#5faf2b"))

	# update and draw terrain
	World.object_group.update()
	World.object_group.draw(screen)

	# update and draw player
	player.player_group.update()
	player.player_group.draw(screen)

	# pygame update
	pygame.display.update()
	clock.tick(75)
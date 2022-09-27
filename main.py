import pygame
from random import choice, randint
from configparser import ConfigParser
from math import sqrt

# player class
class Player(pygame.sprite.Sprite):
	"""
	Base class every player sprite.

	Player(): return Player
	"""

	# static variables
	player_group = pygame.sprite.GroupSingle()
	x, y = 0, 0

	step = 4
	half_step = step/2

	inventory = []

	# init function
	def __init__(self):
		super().__init__()

		# image, rect attributes
		self.image = pygame.image.load("assets/ui/character.png").convert_alpha()
		self.rect = self.image.get_rect(center = (screen.get_width()/2, screen.get_height()/2))
		Player.player_group.add(self)

	# every-frame function
	def update(self) -> None:
		keys = pygame.key.get_pressed()
		fps = clock.get_fps()
		if fps != 0:
			# right, left, up, down keys
			if keys[pygame.K_d]:
				Player.x += self.half_step/fps
				Player.y += self.half_step/fps
			if keys[pygame.K_a]:
				Player.x -= self.half_step/fps
				Player.y -= self.half_step/fps
			if keys[pygame.K_w]:
				Player.x -= self.step/fps
				Player.y += self.step/fps
			if keys[pygame.K_s]:
				Player.x += self.step/fps
				Player.y -= self.step/fps

# object class
class Object(pygame.sprite.Sprite):
	"""
	Base class for every game sprite except player sprite.

	Object((x, y)): return or create Object instance with x, y attributes
	"""

	# static variables
	tile_width = 254
	tile_height = 146

	configparser = ConfigParser()
	file_dict = {}

	# init function
	def __init__(self, image: str, sound: str, coords: tuple, config: str) -> None:
		self.x, self.y = coords[0], coords[1]
		super().__init__()

		# first-time files importing
		if not image in Object.file_dict.keys():
			Object.file_dict[image] = pygame.image.load(image).convert_alpha()
		if not sound in Object.file_dict.keys():
			Object.file_dict[sound] = pygame.mixer.Sound(sound)
		if not config in Object.file_dict.keys():
			Object.configparser.read(config)
			Object.file_dict[config] = {}
			Object.file_dict[config]["object", "item"] = Object.configparser.get("object", "item")
			Object.file_dict[config]["object", "durability"] = Object.configparser.getfloat("object", "durability")

		# image, rect attributes
		self.image = Object.file_dict[image]
		self.rect = self.image.get_rect(midbottom = (self.position_update()))

		# other attributes
		self.index = 0.0
		self.item = Object.file_dict[config]["object", "item"]
		self.durability = Object.file_dict[config]["object", "durability"]
		self.sound = Object.file_dict[sound]
		World.all_sprites[(self.x, self.y)] = self

	# return and set object position
	def position_update(self) -> tuple:
		x = +self.x*Object.tile_width + self.y*Object.tile_width - Player.x*Object.tile_width - Player.y*Object.tile_width + 960
		y = -self.y*Object.tile_height + self.x*Object.tile_height + Player.y*Object.tile_height - Player.x*Object.tile_height + 540

		if hasattr(self, "rect"):
			self.rect.x = x
			self.rect.y = y
		return x, y

	# return and set object visibility
	def visible_update(self) -> bool:
		distance = sqrt((self.x - Player.x)**2 + (self.y - Player.y)**2)
		if distance > view_distance:
			World.object_group.remove(World.all_sprites[(self.x, self.y)])
			return False
		elif not World.all_sprites[(self.x, self.y)] in World.object_group.sprites():
			World.object_group.add(World.all_sprites[(self.x, self.y)])
			return True

	# destroy object by mouse clicking
	def destroy(self) -> None:
		mouse = pygame.mouse.get_pressed()
		# detecting mouse clicking
		if mouse[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
			fps = clock.get_fps()
			if fps != 0:
				# detecting object destroying
				self.index += 81/fps
				if self.index >= self.durability:
					World.all_sprites[(self.x, self.y)] = "empty"
					self.sound.play()
					self.kill()
					if self.item != "empty":
						Player.inventory.append(self.item)
		else:
			self.index = 0.0

	# every-frame function
	def update(self) -> None:
		self.visible_update()
		self.position_update()
		self.destroy()

# every-frame world class
class World():
	"""
	Class for infity world generation. Every-frame class

	World()): return or create World instance
	"""

	# static variables
	object_group = pygame.sprite.Group()
	all_sprites = {}

	filenames = ["object1", "object2", "object3", "object4"]
	dirnames = ["assets/grass/", "assets/grass/", "assets/grass/", "assets/flower/", "assets/flower/", "assets/stone/"]

	# init function
	def __init__(self):
		# x, y matrix
		for x in range(int(-view_distance*1.2+Player.x), int(view_distance*1.2+Player.x)):
			for y in range(int(-view_distance*1.2+Player.y), int(view_distance*1.2+Player.y)):
				if not (x, y) in World.all_sprites.keys():
					# randint chance to appear
					if randint(0, 4) != 0:
						type = choice(World.dirnames)
						image = type + choice(World.filenames) + ".png"
						sound = type + choice(World.filenames) + ".mp3"
						config = type + "object" + ".cfg"
						Object(image, sound, (x, y), config)
					else:
						World.all_sprites[(x, y)] = "empty"
				elif World.all_sprites[(x, y)] != "empty":
					World.all_sprites[(x, y)].visible_update()

# pygame init
pygame.init()
pygame.display.set_caption("IsoGo")
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN, vsync=1)
clock = pygame.time.Clock()
player = Player()
view_distance = 6

# main loop
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			# exit event
			pygame.quit()
			exit()
	
	# generate terrain
	screen.fill(("#5faf2b"))
	World()

	# update and draw terrain
	World.object_group.draw(screen)
	World.object_group.update()

	# update and draw player
	player.player_group.draw(screen)
	player.player_group.update()

	# pygame update
	pygame.display.update()
	clock.tick(144)
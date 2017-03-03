import os, pygame
from pygame.locals import *
from random import randint
from math import sin, cos, radians



def load_image(name, colorkey = None):
	"""loads an image and converts it to pixels. raises an exception if image not found"""
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', name
		raise SystemExit, message
	image = image.convert()
	# set the colorkey to be the color of the top left pixel
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

def load_sound(name):
	"""loads a sound. raises an exception if not found"""
	class NoneSound:
		def play(self): pass
	if not pygame.mixer:
		return NoneSound()
	fullname = os.path.join('data', name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'Cannot load sound:', wav
		raise SystemExit, message
	return sound

def manageball(xmove, ymove):
	"""Handles all of the collisions with walls, paddles, and portals"""
	global current_misses
	global current_score

	#check if ball is in portal
	if (portal_top.rect.contains(ball.rect) == 1 or
		portal_bottom.rect.contains(ball.rect) == 1 or
		portal_left.rect.contains(ball.rect) == 1 or
		portal_right.rect.contains(ball.rect) == 1):
	
		score_sound.play()
		xmove = 0
		ymove = 0
		ball.set_serve()
		current_score += 1

	#check if ball hit the sides
	if (ball.rect.top < 0 or
		ball.rect.bottom > 480 or
		ball.rect.left < 0 or 
		ball.rect.right > 640):

		crash_sound.play()
		xmove = 0
		ymove = 0
		ball.set_serve()
		current_misses += 1

	#paddle collisions
	paddles = [paddle_right, paddle_left, paddle_top, paddle_bottom]
	cos_mults = [-1, 1, 1, -1]
	sin_mults = [-1, -1, -1, -1]
	collision = False
	
	for i in range(0, len(paddles)):
		if ball.rect.colliderect(paddles[i]):
			collision = True
			if i < 2:
				intersection = ((paddles[i].rect.y + (paddles[i].rect.height/2)) - ball.rect.y)
			else:
				intersection = ((paddles[i].rect.x + (paddles[i].rect.width/2)) - ball.rect.x)
			angle = (float(intersection) / (paddle_left.rect.height/2)) * 75
			rads = (radians(angle))
			xmove = cos_mults[i] * 3 * cos(rads)
			ymove = sin_mults[i] * 3 * sin(rads)
			if i >= 2:
				xmove, ymove = ymove, xmove
	if collision:
		paddle_sound.play()
		
	return (xmove, ymove)

def disp_instructions():
	"""call to write instructions"""
	instructions_font = pygame.font.Font(None, 20)
	instructions_font.set_italic(1)
	color = Color('white')
	msg = "Click to Serve, ESC to Quit"
	instructions_image = instructions_font.render(msg, 0, color)
	instructions_pos = instructions_image.get_rect().move(10, 10)
	background.blit(instructions_image, instructions_pos)


class Ball(pygame.sprite.Sprite):
	"""move the ball"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call the sprite init inside the class init
		self.image, self.rect = load_image('ballsmall.png', -1) #creates our image and associated rect
		self.posx = 320 
		self.posy = 240
		self.pos = self.posx, self.posy
		self.rect.center = self.pos
		
	def update(self, xmove, ymove):
		"""move the ball"""
		self.posx = self.posx + xmove
		self.posy = self.posy + ymove
		self.pos = self.posx, self.posy
		self.rect.center = self.pos
		
	def set_serve(self):
		"""resets the ball to the center for next serve"""
		self.posx = 320 
		self.posy = 240
		self.pos = self.posx, self.posy
		self.rect.center = self.pos
	
class PaddleTop(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call the sprite init inside the class init
		self.image, self.rect = load_image('paddle.png', -1) #creates our image and associated rect
		self.original = self.image
		self.image = pygame.transform.rotate(self.original, 90)
		self.rect = self.image.get_rect(center = self.rect.center)
		
	def update(self):
		"move the paddle"
		posx, posy = pygame.mouse.get_pos()
		pos = (posx, 40)
		self.rect.center = pos

class PaddleBottom(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call the sprite init inside the class init
		self.image, self.rect = load_image('paddle.png', -1) #creates our image and associated rect
		self.original = self.image
		self.image = pygame.transform.rotate(self.original, -90)
		self.rect = self.image.get_rect(center = self.rect.center)

	def update(self):
		"move the paddle"
		posx, posy = pygame.mouse.get_pos()
		pos = (posx, 440)
		self.rect.center = pos

class PaddleRight(pygame.sprite.Sprite):
	"""Controls movement of the paddle"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call the sprite init inside the class init
		self.image, self.rect = load_image('paddle.png', -1) #creates our image and associated rect
		
	def update(self):
		"move the paddle"
		posx, posy = pygame.mouse.get_pos()
		pos = (600, posy)
		self.rect.center = pos
		
class PaddleLeft(pygame.sprite.Sprite):
	"""Controls movement of the paddle"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call the sprite init inside the class init
		self.image, self.rect = load_image('paddle.png', -1) #creates our image and associated rect
		
	def update(self):
		"move the paddle"
		posx, posy = pygame.mouse.get_pos()
		pos = (40, posy)
		self.rect.center = pos

class Portal(pygame.sprite.Sprite):
	"""contains functions to orient each portal"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call the sprite init inside the class init
		
		self.image, self.rect = load_image('portal.png', -1) #creates our image and associated rect

	def portal_top(self):
		pos = (320, 0)
		self.rect.center = pos
	
	def portal_bottom(self):
		pos = (320, 480)
		self.rect.center = pos
		
	def portal_left(self):
		self.original = self.image
		self.image = pygame.transform.rotate(self.original, 90)
		self.rect = self.image.get_rect(center = self.rect.center)
		
		pos = (0, 240)
		self.rect.center = pos
		
	def portal_right(self):
		self.original = self.image
		self.image = pygame.transform.rotate(self.original, 90)
		self.rect = self.image.get_rect(center = self.rect.center)
		
		pos = (640, 240)
		self.rect.center = pos
		
	def update(self):
		pass

class Score(pygame.sprite.Sprite):
	"""score contained in sprite to prevent text overwriting"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.font = pygame.font.Font(None, 20)
		self.font.set_italic(1)
		self.color = Color('white')
		self.lastscore = -1
		self.lastmisses = -1
		self.update()
		self.rect = self.image.get_rect().move(10, 450)
	def update(self):
		global current_score
		global current_misses
		
		if current_score != self.lastscore or current_misses != self.lastmisses:
			self.font = pygame.font.Font(None, 20)
			self.font.set_italic(1)
			self.color = Color('white')
			self.lastscore = current_score
			msg = "Score: %d  Misses: %d" % (current_score, current_misses)
			self.image = self.font.render(msg, 0, self.color)
			self.rect = self.image.get_rect().move(10, 450)
			

pygame.init()

#globals
clock = pygame.time.Clock()
xmove = 0
ymove = 0
xpos = 320
ypos = 240
current_score = 0
current_misses = 0
done = False

#create display
pygame.event.set_grab(1)
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('PYNG')
pygame.mouse.set_visible(0)

#load sounds
paddle_sound = load_sound('ping.wav')
crash_sound = load_sound('crash.wav')
score_sound = load_sound('score.wav')

#load background
background = pygame.Surface(screen.get_size())
background, _ = load_image('background.jpg')

#create paddles
paddle_right = PaddleRight()
paddle_left = PaddleLeft()
paddle_top = PaddleTop()
paddle_bottom = PaddleBottom()

#create portals
portal_top = Portal()
portal_bottom = Portal()
portal_left = Portal()
portal_right = Portal()

#orient the portals
portal_top.portal_top()
portal_bottom.portal_bottom()
portal_left.portal_left()
portal_right.portal_right()

#make a ball
ball = Ball()

#score sprite
score = Score()

#draw the instructions
disp_instructions()

#create sprite groups
paddlesprites = pygame.sprite.RenderPlain((paddle_right,paddle_left, paddle_top, paddle_bottom))
portalsprites = pygame.sprite.RenderPlain((portal_top, portal_bottom, portal_left, portal_right))
ballsprite = pygame.sprite.RenderPlain((ball))
scoresprite = pygame.sprite.RenderPlain((score))


#GAME LOOP
while done == False:
	clock.tick(30) # set our max framerate
	for e in pygame.event.get():
		if e.type == KEYUP:
			if e.key == K_ESCAPE:
				done = True
		if e.type == MOUSEBUTTONUP:
			while xmove == 0 or ymove == 0:
				start_vectors = [-3, 3]
				xmove = start_vectors[randint(0, 1)]
				ymove = start_vectors[randint(0, 1)]	

	#get ball movements
	xmove, ymove = manageball(xmove, ymove)

	#update sprites
	ball.update(xmove, ymove)
	paddlesprites.update()
	scoresprite.update()

	#blit the background and draw sprites
	screen.blit(background, (0,0))
	scoresprite.draw(screen)
	paddlesprites.draw(screen)
	portalsprites.draw(screen)
	ballsprite.draw(screen)

	#update the display
	pygame.display.update()

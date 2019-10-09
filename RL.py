import random
import numpy as np
import keyboard as kb 
from PIL import Image
import cv2
import time
import h5py



class car():

	def __init__(self, size):
		self.size = size
		self.car_size = 3
		#self.x = random.randint(int(1.5*self.car_size), self.size-int(1.5*self.car_size))
		#self.y = random.randint(int(1.5*self.car_size), self.size-int(1.5*self.car_size))
		self.x = .15*self.size
		self.y = .2*self.size
		self.orientation = 90
		self.power = 0
		self.t = []
		self.l = []
		self.b = []
		self.r = []
		# Generate car color
		def mycolor():
			c1 = random.uniform(0, 255)
			c2 = random.uniform(0, 255)
			c3 = random.uniform(0, 255)
			return (c1, c2, c3)
		
		self.barva1 = mycolor()
		self.barva2 = mycolor()
		self.barva3 = mycolor()

	def __sub__(self, other):
		return (self.x-other.x, self.y-other.y)

	def __str__(self):
		return f"Avto-x:{self.x}-y:{self.y}-o:{self.orientation}-p{self.power}"

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def action(self, orientation_increment, power_increment):
		self.orientation += orientation_increment
		self.power += power_increment
		if self.orientation >= 360 or self.orientation <= -360:
			self.orientation = 0
		if self.power >= 1.2:
			self.power = 1.2
		if self.power <= -.2:
			self.power = -.2
		if power_increment == 0:
			self.power -= .02
			if self.power <= 0:
				self.power = 0
		self.move(self.orientation, self.power)

	def move(self, orientation, power):
		self.x += power * np.cos(orientation*np.pi/180)
		self.y += power * np.sin(orientation*np.pi/180)
		self.kvadratek(orientation)

		# Preveri, če smo še znotraj igrišča
		if self.x <= 2*self.car_size:
			self.x = 2*self.car_size
		elif self.x >= self.size-2*self.car_size:
			self.x = self.size-2*self.car_size
		if self.y <= 2*self.car_size:
			self.y = 2*self.car_size
		elif self.y >= self.size-2*self.car_size:
			self.y = self.size-2*self.car_size

	def kvadratek(self, o, a=False, b=15):
		if not a:
			a = self.car_size
		self.t = np.array([self.x+a*np.cos((o+3*180/4+b)*2*np.pi/360), self.y+a*np.sin((o+3*180/4+b)*2*np.pi/360)])
		self.l = np.array([self.x+a*np.cos((o+5*180/4-b)*2*np.pi/360), self.y+a*np.sin((o+5*180/4-b)*2*np.pi/360)])
		self.b = np.array([self.x+a*np.cos((o+7*180/4+b)*2*np.pi/360), self.y+a*np.sin((o+7*180/4+b)*2*np.pi/360)])
		self.r = np.array([self.x+a*np.cos((o+180/4-b)*2*np.pi/360), self.y+a*np.sin((o+180/4-b)*2*np.pi/360)])

		self.p1 = np.array([self.x+a*np.cos((o+2*180/4+b)*2*np.pi/360), self.y+a*np.sin((o+2*180/4+b)*2*np.pi/360)])
		self.p2 = np.array([self.x+a*np.cos((o+6*180/4-b)*2*np.pi/360), self.y+a*np.sin((o+6*180/4-b)*2*np.pi/360)])

	def trk(self, pot):
		for u in range(len(pot[0,:])):
			tb_x = round(self.b[0],0)
			tb_y = round(self.b[1],0)
			tr_x = round(self.r[0],0)
			tr_y = round(self.r[1],0)
			pot1_x = round(pot[0,u],0)
			pot1_y = round(pot[1,u],0)
			pot2_x = round(pot[2,u],0)
			pot2_y = round(pot[3,u],0)

			if tb_x == pot1_x and tb_y == pot1_y:
				self.konec = True
				print('Zabil si se v notranjo ograjo!')
				break
			elif tr_x == pot2_x and tr_y == pot2_y:
				self.konec = True
				print('Zabil si se v zunanjo ograjo!')
				break
			elif tb_x == pot2_x and tb_y == pot2_y:
				self.konec = True
				print('Zabil si se v zunanjo ograjo!')
				break
			elif tr_x == pot1_x and tr_y == pot1_y:
				self.konec = True
				print('Zabil si se v notranjo ograjo!')
				break


class Env():
	def __init__(self):
		self.SIZE = 200
		self.MOVE_PENALTY = 1
		self.CRASH_PENALTY = -200
		self.reset()

	def reset(self):
		self.avto = car(self.SIZE)
		self.episode_step = 0

	def step(self, action):
		self.episode_step += 1
		self.avto.action(action[0], action[1])

	def get_image(self):
		img = np.zeros((self.SIZE, self.SIZE, 3), dtype=np.uint8)
		print(int(self.avto.x), int(self.avto.y))
		img[int(self.avto.x)][int(self.avto.y)] = self.avto.barva1
		img[int(self.avto.t[0])][int(self.avto.t[1])] = self.avto.barva2
		img[int(self.avto.l[0])][int(self.avto.l[1])] = self.avto.barva2
		img[int(self.avto.b[0])][int(self.avto.b[1])] = self.avto.barva3
		img[int(self.avto.r[0])][int(self.avto.r[1])] = self.avto.barva3
		img = Image.fromarray(img, 'RGB')
		return img

	def render(self):
		img = self.get_image()
		img = img.resize((400, 400))
		cv2.imshow('image', np.array(img))
		cv2.waitKey(10)

class player():

	def __init__(self):
		self.o = 0
		self.p = 0

	def move_o(self):
		if kb.is_pressed('left'):
			self.o = 5
		elif kb.is_pressed('right'):
			self.o = -5
		else:
			self.o = 0
		return self.o

	def move_p(self):
		if kb.is_pressed('up'):
			self.p = .05
		elif kb.is_pressed('down'):
			self.p = -.2
		else:
			self.p = 0
		return self.p


env = Env()
jernej = player()

for i in range(2000):
	action = [jernej.move_o(), jernej.move_p()]
	env.step(action)
	env.render()
	











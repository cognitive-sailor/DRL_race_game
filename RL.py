import random
import numpy as np
import keyboard as kb
from PIL import Image
import cv2
import time
import h5py
import reward_gates as rg



class Car:

	def __init__(self, size, track):
		self.size = size  # Playground size, inhereted from Environment
		self.car_size = 3
		self.create_track = track
		self.x = .15*self.size  # Set fixed car position
		self.y = .2*self.size
		self.orientation = 90  # Set fixed car orientation
		self.power = 0  # Initial car thrust is zero
		self.t = []  # Top-left corner of a car
		self.l = []  # Bottom-left corner of a car
		self.b = []  # Bottom-right corner of a car
		self.r = []  # Top-right corner of a car
		# Generate car color
		def my_color():
			c1 = random.uniform(50, 255)
			c2 = random.uniform(50, 255)
			c3 = random.uniform(50, 255)
			return c1, c2, c3

		self.barva1 = my_color()
		self.barva2 = my_color()
		self.barva3 = my_color()

	def __sub__(self, other):
		return (self.x-other.x, self.y-other.y)

	def __str__(self):
		return f"Avto-x:{self.x}-y:{self.y}-o:{self.orientation}-p{self.power}"

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def action(self, orientation_increment, power_increment):
		if self.create_track:
			self.orientation += orientation_increment*.25
		else:
			self.orientation += orientation_increment
		self.power += power_increment

		if self.create_track:
			upower_limit = .2  # Creating a track, we want a car to go slower
			lpower_limit = -.2
		else:
			upower_limit = 1.2
			lpower_limit = -.2
		if self.orientation >= 360 or self.orientation <= -360:
			self.orientation = 0  # Orientation of a car is always [-360, 360]
		if self.power >= upower_limit:
			self.power = upower_limit  # Max power limit
		if self.power <= lpower_limit:
			self.power = lpower_limit  # Min power limit
		if power_increment == 0:
			self.power -= .02  # If no power input, slow deceleration
			if self.power <= 0:
				self.power = 0  # ..until car stops.
		self.move(self.orientation, self.power)  # Move a car!

	def move(self, orientation, power):
		self.x += power * np.cos(orientation*np.pi/180)  # Set coordinates to a new position
		self.y += power * np.sin(orientation*np.pi/180)
		if self.create_track:
			self.kvadratek(orientation, 2.5*self.car_size)  # Orient car's corners (creating a track, "car" should be wider)
		else:
			self.kvadratek(orientation)  # Orient car's corners

		# Is car still inside our environment? If not, correct.
		if self.x <= 2*self.car_size:
			self.x = 2*self.car_size
		elif self.x >= self.size-2*self.car_size:
			self.x = self.size-2*self.car_size
		if self.y <= 2*self.car_size:
			self.y = 2*self.car_size
		elif self.y >= self.size-2*self.car_size:
			self.y = self.size-2*self.car_size

	def kvadratek(self, o, a=False, b=15):
		# Calculate car's correct corner points orientation
		if not a:
			a = self.car_size
		self.t = np.array([self.x+a*np.cos((o+3*180/4+b)*2*np.pi/360), self.y+a*np.sin((o+3*180/4+b)*2*np.pi/360)])
		self.l = np.array([self.x+a*np.cos((o+5*180/4-b)*2*np.pi/360), self.y+a*np.sin((o+5*180/4-b)*2*np.pi/360)])
		self.b = np.array([self.x+a*np.cos((o+7*180/4+b)*2*np.pi/360), self.y+a*np.sin((o+7*180/4+b)*2*np.pi/360)])
		self.r = np.array([self.x+a*np.cos((o+180/4-b)*2*np.pi/360), self.y+a*np.sin((o+180/4-b)*2*np.pi/360)])

		if self.create_track:
			self.p1 = np.array([self.x+a*np.cos((o+2*180/4+b)*2*np.pi/360), self.y+a*np.sin((o+2*180/4+b)*2*np.pi/360)])
			self.p2 = np.array([self.x+a*np.cos((o+6*180/4-b)*2*np.pi/360), self.y+a*np.sin((o+6*180/4-b)*2*np.pi/360)])


class Env:
	def __init__(self):
		self.SIZE = 200
		self.MOVE_PENALTY = -1
		self.CRASH_PENALTY = -200
		self.create_track = True
		self.STEPS = 2_000
		self.GATE_REWARD = 50
		self.done = False
		self.crashed = False
		self.through_gate = False
		self.episode_step = 0


		try:
			# If track exist, load it. If not, create it!
			with h5py.File('Track-size_200-width_7-t_1571223844.2934508.h5','r') as f:
				pot = f['/pot']
				self.proga = pot[...]
				print('Proga uspesno uvozena!')
			line1 = self.proga[:2, :]
			line2 = self.proga[-2:, :]

			# Draw the track
			img = np.zeros((self.SIZE, self.SIZE, 3), dtype=np.uint8)
			for i in range(len(line1[0])):
				img[int(line1[0, i]), int(line1[1, i])] = (30, 30, 50)
			for i in range(len(line2[0])):
				img[int(line2[0, i]), int(line2[1, i])] = (30, 50, 30)

			# Make reward_gates
			self.gates = rg.Gate(self.proga)
			self.gate_index = 0

			self.create_track = False

		except Exception as e:
			pass

		if self.create_track:
			img = np.zeros((self.SIZE, self.SIZE, 3), dtype=np.uint8)
			self.STEPS = 5_000
			self.track = np.zeros((4, self.STEPS))
			print(f'Ustvarjam novo progo...')

		self.image = img
		self.reset()


	def reset(self):
		self.avto = Car(self.SIZE, self.create_track)
		self.episode_step = 0
		self.crashed = False
		self.done = False
		# Erase the unreached gate
		for j in range(self.gates.POINTS):
			self.image[int(self.gates.LINES[self.gate_index][j][0]),
				int(self.gates.LINES[self.gate_index][j][1])] = (0, 0, 0)
		# Draw the first gate
		for j in range(self.gates.POINTS):
			self.image[int(self.gates.LINES[0][j][0]),
				int(self.gates.LINES[0][j][1])] = (255, 0, 0)

		self.gate_index = 0

	def step(self, action):
		self.episode_step += 1
		self.avto.action(action[0], action[1])  # Tell a car which action to take
		if not self.create_track:
			self.collision()  # Check if car crashed
			ga_reward = self.gate_check() # Check if car passed a gate
		reward = 0
		# Get the reward
		if self.crashed or self.episode_step >= self.STEPS:
			reward = self.CRASH_PENALTY
			self.done = True
		elif self.through_gate:
			reward = ga_reward + self.MOVE_PENALTY
		else:
			reward = self.MOVE_PENALTY

		# Reset the "through_gate" flag
		self.through_gate = False

		# Get new observation
		new_observation = np.array(self.get_image())

		if self.create_track:
			self.track[0, self.episode_step-1] = self.avto.p1[0]  # Record the track
			self.track[1, self.episode_step-1] = self.avto.p1[1]
			self.track[2, self.episode_step-1] = self.avto.p2[0]
			self.track[3, self.episode_step-1] = self.avto.p2[1]

			if self.episode_step >= self.STEPS:
				with h5py.File(f'Track-size_{self.SIZE}-width_{int(2.5*self.avto.car_size)}-t_{time.time()}.h5','w') as f:
					data = f.create_dataset('pot', self.track.shape)
					data[...] = self.track
				print(f'Track saved!')

		return new_observation, reward

	def get_image(self):
		img = np.zeros((self.SIZE, self.SIZE, 3), dtype=np.uint8)
		img = img + self.image  # Adds a track to an image
		if not self.create_track:
			img[int(self.avto.x)][int(self.avto.y)] = self.avto.barva1  # Draw the car at current position
			img[int(self.avto.t[0])][int(self.avto.t[1])] = self.avto.barva2
			img[int(self.avto.l[0])][int(self.avto.l[1])] = self.avto.barva2
			img[int(self.avto.b[0])][int(self.avto.b[1])] = self.avto.barva3
			img[int(self.avto.r[0])][int(self.avto.r[1])] = self.avto.barva3
		else:
			self.image[int(self.avto.p1[0])][int(self.avto.p1[1])] = (255, 255, 255)
			self.image[int(self.avto.p2[0])][int(self.avto.p2[1])] = (255, 255, 255)
		img = Image.fromarray(img, 'RGB')
		return img

	def render(self):
		img = self.get_image()  # Display current image
		img = img.resize((400, 400))
		cv2.imshow('image', np.array(img))
		cv2.waitKey(10)

	def collision(self):
		# Check if car has crashed into inner or outer wall
		if not self.image[int(self.avto.b[0]), int(self.avto.b[1]), 1] == 0:
			self.crashed = True
		if not self.image[int(self.avto.r[0]), int(self.avto.r[1]), 1] == 0:
			self.crashed = True

	def gate_check(self):
		# Check if car has passed a gate
		if self.image[int(self.avto.x), int(self.avto.y), 0] == 255:
			self.through_gate = True
			g_reward = self.GATE_REWARD
			print('Just drove through the gate!')
			# Erase current gate
			for j in range(self.gates.POINTS):
				self.image[int(self.gates.LINES[self.gate_index][j][0]),
					int(self.gates.LINES[self.gate_index][j][1])] = (0, 0, 0)
			# Draw the next gate
			if self.gate_index == self.gates.NUMBER_OF_GATES:
				self.gate_index = 0  # Draw the first gate again, if agent made a whole lap
			else:
				self.gate_index += 1
			for j in range(self.gates.POINTS):
				self.image[int(self.gates.LINES[self.gate_index][j][0]),
					int(self.gates.LINES[self.gate_index][j][1])] = (255, 0, 0)

		else:
			g_reward = 0
		return g_reward

class Player:

	def __init__(self):
		self.o = 0
		self.p = 0
		self.power_max = .05
		self.power_min = -.2
		self.orient_size = 5

	def move_o(self):
		# Change a car's orientation
		if kb.is_pressed('left'):
			self.o = self.orient_size
		elif kb.is_pressed('right'):
			self.o = -self.orient_size
		else:
			self.o = 0
		return self.o

	def move_p(self):
		# Change a car's thrust (power)
		if kb.is_pressed('up'):
			self.p = self.power_max
		elif kb.is_pressed('down'):
			self.p = self.power_min
		else:
			self.p = 0
		return self.p


'''
env = Env()
jernej = Player()

for i in range(env.STEPS):
	action = [jernej.move_o(), jernej.move_p()]
	env.step(action)
	env.render()
	if env.done:
		print(f'Crashed in episode step: {env.episode_step}')
		env.reset()
'''

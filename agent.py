import RL
import random

env = RL.Env()
jernej = RL.Player()

for i in range(env.STEPS):
	action = [jernej.move_o(), jernej.move_p()]
	#action = [random.choice([-5, 5]), random.choice([-.05, .05])]
	env.step(action)
	env.render()
	if env.done:
		print(f'Crashed in episode step: {env.episode_step}');
		env.reset()

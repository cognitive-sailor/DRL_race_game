import RL

env = Env()
jernej = Player()

for i in range(env.STEPS):
	action = [jernej.move_o(), jernej.move_p()]
	env.step(action)
	env.render()
	if env.done:
		print(f'Crashed in episode step: {env.episode_step}')
		env.reset()
		env.done = False

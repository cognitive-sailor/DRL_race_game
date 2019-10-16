import h5py
import numpy as np

class Gate:
    def __init__(self, path):
        self.NUMBER_OF_GATES = 30
        self.POINTS = 50  # Everi gate is made with this many points
        self.LINES = np.zeros((self.NUMBER_OF_GATES, self.POINTS, 2))
        path_length = len(path[0])
        make_gate_every = np.floor(path_length/self.NUMBER_OF_GATES)
        self.point_pairs = []
        # At every "make_gate_every" gate, find x and y coordinates for points on both walls
        for i in range(path_length):
            if not i % make_gate_every and i != 0:
                self.point_pairs.append([path[0, i], path[1, i], path[2, i], path[3, i]])
        # Generate series of points for each gate
        for j in range(len(self.point_pairs)):
            a = Line(self.point_pairs[j], self.POINTS)
            self.LINES[j, :] = np.array(a.line)


class Line:
    def __init__(self, pairs, points):
        self.Ax = pairs[0]
        self.Ay = pairs[1]
        self.Bx = pairs[2]
        self.By = pairs[3]
        self.line = self.make_line(points)

    def make_line(self, poin):
        points = poin
        x = np.linspace(self.Ax, self.Bx, points, endpoint=True)
        y = np.linspace(self.Ay, self.By, points, endpoint=True)
        line = []
        for i in range(len(x)):
            line.append([x[i], y[i]])
        return line


'''
# If track exist, load it. If not, create it!
with h5py.File('Track-size_200-width_7-t_1570654659.9921403.h5','r') as f:
    pot = f['/pot']
    proga = pot[...]
    print('Proga uspesno uvozena!')

neki = Gate(proga)
'''

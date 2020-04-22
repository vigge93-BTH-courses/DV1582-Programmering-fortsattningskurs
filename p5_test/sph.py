import p5
import random
import numpy as np

class Particle:
    def __init__(self, x, y, m, p, d):
        self._pos = p5.Vector(x, y)
        self._vel = p5.Vector(0, 0)
        self._acc = p5.Vector(0, 0)
        self._mass = m
        self._pressure = p
        self._density = d
        self._volume = m/d

    def calc_pressure(self):
        pass

    @staticmethod
    def kernel():
        pass
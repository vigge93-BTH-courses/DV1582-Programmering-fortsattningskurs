from random import randint


class Die:
    def __init__(self, sides=6):
        self._value = 1
        self._sides = sides
        self.roll()

    def roll(self):
        self._value = randint(1, self._sides)

    @property
    def get_value(self):
        return self._value

    def __str__(self):
        return str(self._value)

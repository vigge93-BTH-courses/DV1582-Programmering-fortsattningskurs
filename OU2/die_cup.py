from die import Die


class DieCup:
    def __init__(self, number_of_dice=5):
        self._dice = [Die(6) for n in range(number_of_dice)]
        self._banked = [False for n in range(number_of_dice)]

    def roll(self):
        for index, die in enumerate(self._dice):
            if not self._banked[index]:
                die.roll()

    def die_value(self, index):
        return self._dice[index].get_value

    def bank(self, index):
        self._banked[index] = True

    def is_banked(self, index):
        return self._banked[index]

    def release(self, index):
        self._banked[index] = False

    def release_all(self):
        self._banked = [False for n in range(len(self._banked))]

    def find_value_unbanked(self, value):
        for index, die in enumerate(self._dice):
            if die.get_value == value and not self._banked[index]:
                return index

        return - 1
    
    def get_total_value(self):
        s = 0
        for die in self._dice:
            s += die.get_value
        
        return s


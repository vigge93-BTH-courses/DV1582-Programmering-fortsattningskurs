class Player():

    def __init__(self, name):
        self._name = name
        self._score = 0

    def set_name(self, namestring):
        self._name = namestring

    @property
    def current_score(self):
        return self._score

    def reset_score(self):
        self._score = 0

    def play_round(self, game):
        self._score += game.round()

    def __str__(self):
        return f"{self._name}: {self._score} points"

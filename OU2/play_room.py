class PlayRoom:
    def __init__(self):
        self._game = None
        self._players = []

    def set_game(self, game):
        self._game = game

    def add_player(self, player):
        self._players.append(player)

    def reset_scores(self):
        list(map(lambda player: player.reset_score(), self._players))

    def play_round(self):
        for player in self._players:
            player.play_round(self._game)

    def game_finished(self):
        return len(list(filter(lambda player: player.current_score >= self._game.winning_score, self._players))) > 0

    def print_scores(self):
        print(*[str(player) for player in self._players], sep='\n', end='\n\n')

    def print_winner(self):
        print("Winner:\n" + str(sorted(self._players, key=lambda player: player.current_score, reverse=True)[0]))

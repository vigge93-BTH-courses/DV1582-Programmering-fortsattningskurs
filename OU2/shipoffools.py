from play_room import PlayRoom
from ship_of_fools_game import ShipOfFoolsGame
from player import Player

if __name__ == "__main__":
    room = PlayRoom()
    room.set_game(ShipOfFoolsGame(21))
    room.add_player(Player("Jåker"))
    room.add_player(Player("Viral"))
    room.add_player(Player("Jerry"))
    room.add_player(Player("Kruise"))
    room.add_player(Player("Onyxia"))
    room.reset_scores()
    while not room.game_finished():
        room.play_round()
        room.print_scores()
    room.print_winner()

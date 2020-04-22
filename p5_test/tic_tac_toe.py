import p5

class Player():
    def __init__(self, name, piece_factory):
        self._name = name
        self._score = 0
        self._pieces = []
        for _ in range(9):
            self._pieces.append(piece_factory())

    def make_move(self, x, y, game_board):
        valid_move = True
        try:
            game_board.add_piece(self._pieces[0], x, y)
            self._pieces = self._pieces[1:]
        except ValueError as e:
            print(str(e))
            valid_move = False
        return valid_move

class TicTacToeGame():
    def __init__(self, game_board):
        self._game_board = game_board
        self._players = []
        self._active_player_index = 0

    def add_player(self, player):
        self._players.append(player)
    
    def get_active_player(self):
        return self._players[self._active_player_index]

    def next_turn(self):
        self._active_player_index = (self._active_player_index + 1) % len(self._players)
    
    def make_move(self, x, y):
        valid = self.get_active_player().make_move(x, y, self._game_board)
        if valid:
            self.next_turn()
    
    def draw(self):
        self._game_board.draw()

    def game_over(self):
        return self._game_board.board_is_full() or self._game_board.someone_has_won()

class GameBoard():
    def __init__(self):
        self._pieces = {}
        for row in range(3):
            for col in range(3):
                self._pieces[(row, col)] = None
        self._margin = 40
    
    def add_piece(self, piece, x, y):
        row =  y // (height / 3)
        col = x // (height / 3)
        if self._pieces[(row, col)] is None:
            self._pieces[(row, col)] = piece
        else:
            raise ValueError('Space already occupied!')

    def draw(self):
        p5.push_style()
        p5.no_fill()
        p5.stroke_weight(10)
        self._draw_grid()
        for piece in self._pieces:
            if self._pieces[piece] is not None:
                x = piece[1]*width/3 + self._margin/2
                y = piece[0]*height/3 + self._margin/2
                w = width/3 - self._margin
                h = height/3 - self._margin
                self._pieces[piece].draw(x, y, w, h)

        p5.pop_style()

    def _draw_grid(self):
        for horizontal in range(1, 3):
            h = horizontal*height/3
            p5.line((0, h), (width, h))

        for vertical in range(1, 3):
            w = vertical*width/3
            p5.line((w, 0), (w, height))

    def board_is_full(self):
        for piece in self._pieces:
            if self._pieces[piece] is None:
                return False
        return True

    def someone_has_won(self):
        # Rows        
        for row in range(3):
            if self._pieces[(row, 0)] is not None and type(self._pieces[(row, 0)]) == type(self._pieces[(row, 1)]) == type(self._pieces[(row, 2)]):
                return True
        # Columns
        for col in range(3):
            if self._pieces[(0, col)] is not None and type(self._pieces[(0, col)]) == type(self._pieces[(1, col)]) == type(self._pieces[(2, col)]):
                return True
        
        # Diagonals
        if self._pieces[(0, 0)] is not None and type(self._pieces[(0, 0)]) == type(self._pieces[(1, 1)]) == type(self._pieces[(2, 2)]):
            return True
        if self._pieces[(0, 2)] is not None and type(self._pieces[(0, 2)]) == type(self._pieces[(1, 1)]) == type(self._pieces[(2, 0)]):
            return True
        return False
            

class GamePiece():

    def draw(self, x, y, w, h):
        raise NotImplementedError
    
    @staticmethod
    def piece_factory():
        raise NotImplementedError

class PieceX(GamePiece):
    def __init__(self):
        GamePiece.__init__(self)
    
    def draw(self, x, y, w, h):
        p5.push_style()
        p5.no_fill()
        p5.stroke_weight(5)
        p5.line((x,y), (x+w, y+h))
        p5.line((x+w, y), (x, y + h))
        p5.pop_style()
    
    @staticmethod
    def piece_factory():
        return PieceX()

class PieceO(GamePiece):
    def __init__(self):
        GamePiece.__init__(self)

    def draw(self, x, y, w, h):
        p5.push_style
        p5.no_fill()
        p5.stroke_weight(5)
        p5.ellipse((x, y), (x+w, y+h), mode='CORNERS')
        p5.pop_style()

    @staticmethod
    def piece_factory():
        return PieceO()

tic_tac_toe_game = None


def setup():
    global tic_tac_toe_game

    p5.size(700, 700)
    game_board = GameBoard()
    tic_tac_toe_game = TicTacToeGame(game_board)
    tic_tac_toe_game.add_player(Player('Jåker', PieceX.piece_factory))
    tic_tac_toe_game.add_player(Player('Viral', PieceO.piece_factory))

def draw():
    global tic_tac_toe_game
    p5.background(200)
    tic_tac_toe_game.draw()
    if tic_tac_toe_game.game_over():
        setup()
def mouse_pressed():
    global tic_tac_toe_game
    tic_tac_toe_game.make_move(mouse_x, mouse_y)

if __name__ == '__main__':
    p5.run()
import time
import sys
import random
import copy

from base_client import LiacBot

WHITE = 1
BLACK = -1
NONE = 0

PAWN = 1
ROOK = 2
KNIGHT = 3

# BOT =========================================================================
class TestBot(LiacBot):
    name = 'test Bot'

    def __init__(self):
        super(TestBot, self).__init__()
        self.last_move = None

    def on_move(self, state):
        print 'Generating a move...',
        board = Board(state)

        if state['bad_move']:
            print state['board']
            raw_input()

        t1 = time.time()
        eval = self.alpha_beta(board, 2, -100000, +100000, True)
        t2 = time.time()
        print eval, t2-t1
        move = [(6,2),(5,2)]

        self.last_move = move
        print move
        self.send_move(move[0], move[1])

    def on_game_over(self, state):
        print 'Game Over.'
        sys.exit()

#Alpha Beta ============================================================



    def alpha_beta(self, board, depth, alpha, beta, maximizingPlayer):

        # terminalNode ?
        for col in range(0, 8):
            if (not board.is_empty((7,col)) and board[(7,col)].type == PAWN):
                return board.my_pieces[0].team * 10000
            if (not board.is_empty((0,col)) and board[(0,col)].type == PAWN):
                return board.my_pieces[0].team * -10000

        # depth = 0 ?
        if depth == 0:
            return board.evaluationBoard()

        if maximizingPlayer:
            for p in range(len(board.my_pieces)):
                piece = board.my_pieces[p]
                moves = piece.generate()
                for move in moves:
                    # Board copy
                    sonBoard = copy.copy(board)
                    # Piece mouvement
                    pieceA = sonBoard[piece.position]
                    pieceB = sonBoard[move]
                    sonBoard[move] = pieceA
                    sonBoard[piece.position] = None
                    if pieceA.is_opponent(pieceB):
                        for i,pc in enumerate(sonBoard.op_pieces):
                            if pc.position == move :
                                sonBoard.op_pieces.pop(i)
                                break
                    sonBoard.my_pieces[p].position = move

                    alpha = max(alpha, self.alpha_beta(sonBoard, (depth - 1), alpha, beta, False))

                    if beta <= alpha: break
                if beta <= alpha: break
            return alpha
        else:
            for p in range(len(board.op_pieces)):
                piece = board.op_pieces[p]
                moves = piece.generate()
                for move in moves:
                    # Board copy
                    sonBoard = copy.copy(board)
                    # Piece mouvement
                    pieceA = sonBoard[piece.position]
                    pieceB = sonBoard[move]
                    sonBoard[move] = pieceA
                    sonBoard[piece.position] = None
                    if pieceA.is_opponent(pieceB):
                        for i,pc in enumerate(sonBoard.my_pieces):
                            if pc.position == move :
                                sonBoard.my_pieces.pop(i)
                                break
                    sonBoard.op_pieces[p].position = move

                    beta = min(beta, self.alpha_beta(sonBoard, (depth - 1), alpha, beta, True))
                    if beta <= alpha: break
                if beta <= alpha: break
            return beta


# MODELS ======================================================================
class Board(object):
    def __init__(self, state):
        self.cells = [[None for j in xrange(8)] for i in xrange(8)]
        self.my_pieces = []
        self.op_pieces = []
        
        PIECES = {
            'r': Rook,
            'p': Pawn,
            'b': Bishop,
            'q': Queen,
            'n': Knight,
        }

        my_team = state['who_moves']
        c = state['board']
        i = 0

        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                if c[i] != '.':
                    cls = PIECES[c[i].lower()]
                    team = BLACK if c[i].lower() == c[i] else WHITE

                    piece = cls(self, team, (row, col))
                    self.cells[row][col] = piece

                    if team == my_team:
                        self.my_pieces.append(piece)
                    else:
                        self.op_pieces.append(piece)

                i += 1

    def __getitem__(self, pos):
        if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7:
            return None

        return self.cells[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self.cells[pos[0]][pos[1]] = value

    def is_empty(self, pos):
        return self[pos] is None

    def generate(self):
        moves = []
        for piece in self.my_pieces:
            ms = piece.generate()
            ms = [(piece.position, m) for m in ms]
            moves.extend(ms)

        return moves

    def evaluationBoard(self):

       # myScore
        myScore = 0
        if self.my_pieces[0].team == WHITE:
            for piece in self.my_pieces:
                if piece.type == PAWN:
                    row = piece.position[0]
                    myScore = myScore + 3*2^(row-1)
                if piece.type == ROOK:
                    nbsMov = len(piece.generate())
                    myScore = myScore + 10+nbsMov
                if piece.type == KNIGHT:
                    nbsMov = len(piece.generate())
                    myScore = myScore + 10+nbsMov*2
        else:
            for piece in self.my_pieces:
                if piece.type == PAWN:
                    row = piece.position[0]
                    myScore = myScore + 3*2^(6-row)
                if piece.type == ROOK:
                    nbsMov = len(piece.generate())
                    myScore = myScore + 10+nbsMov
                if piece.type == KNIGHT:
                    nbsMov = len(piece.generate())
                    myScore = myScore + 10+nbsMov*2

        # opScore
        opScore = 0
        if self.op_pieces[0].team == WHITE:
            for piece in self.op_pieces:
                if piece.type == PAWN:
                    row = piece.position[0]
                    opScore = opScore + 3*2^(row-1)
                if piece.type == ROOK:
                    nbsMov = len(piece.generate())
                    opScore = opScore + 10+nbsMov
                if piece.type == KNIGHT:
                    nbsMov = len(piece.generate())
                    opScore = opScore + 10+nbsMov*2
        else:
            for piece in self.op_pieces:
                if piece.type == PAWN:
                    row = piece.position[0]
                    opScore = opScore + 3*2^(6-row)
                if piece.type == ROOK:
                    nbsMov = len(piece.generate())
                    opScore = opScore + 10+nbsMov
                if piece.type == KNIGHT:
                    nbsMov = len(piece.generate())
                    opScore = opScore + 10+nbsMov*2

        return myScore-opScore


class Piece(object):
    def __init__(self):
        self.board = None
        self.team = None
        self.position = None
        self.type = NONE

    def generate(self):
        pass

    def is_opponent(self, piece):
        return piece is not None and piece.team != self.team

class Pawn(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position
        self.type = PAWN

    def generate(self):
        moves = []
        my_row, my_col = self.position

        d = self.team

        # Movement to 1 forward
        pos = (my_row + d*1, my_col)
        if self.board.is_empty(pos):
            moves.append(pos)

        # Normal capture to right
        pos = (my_row + d*1, my_col+1)
        piece = self.board[pos]
        if self.is_opponent(piece):
            moves.append(pos)

        # Normal capture to left
        pos = (my_row + d*1, my_col-1)
        piece = self.board[pos]
        if self.is_opponent(piece):
            moves.append(pos)

        return moves

class Rook(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position
        self.type = ROOK
        
    def _col(self, dir_):
        my_row, my_col = self.position
        d = -1 if dir_ < 0 else 1
        for col in xrange(1, abs(dir_)):
            yield (my_row, my_col + d*col)

    def _row(self, dir_):
        my_row, my_col = self.position

        d = -1 if dir_ < 0 else 1
        for row in xrange(1, abs(dir_)):
            yield (my_row + d*row, my_col)

    def _gen(self, moves, gen, idx):
        for pos in gen(idx):
            piece = self.board[pos]
            
            if piece is None: 
                moves.append(pos)
                continue
            
            elif piece.team != self.team:
                moves.append(pos)

            break

    def generate(self):
        moves = []

        my_row, my_col = self.position
        self._gen(moves, self._col, 8-my_col) # RIGHT
        self._gen(moves, self._col, -my_col-1) # LEFT
        self._gen(moves, self._row, 8-my_row) # TOP
        self._gen(moves, self._row, -my_row-1) # BOTTOM

        return moves

class Bishop(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _gen(self, moves, row_dir, col_dir):
        my_row, my_col = self.position

        for i in xrange(1, 8):
            row = row_dir*i
            col = col_dir*i
            q_row, q_col = my_row+row, my_col+col

            if not 0 <= q_row <= 7 or not 0 <= q_col <= 7:
                break

            piece = self.board[q_row, q_col]
            if piece is not None:
                if piece.team != self.team:
                    moves.append((q_row, q_col))
                break

            moves.append((q_row, q_col))

    def generate(self):
        moves = []

        self._gen(moves, row_dir=1, col_dir=1) # TOPRIGHT
        self._gen(moves, row_dir=1, col_dir=-1) # TOPLEFT
        self._gen(moves, row_dir=-1, col_dir=-1) # BOTTOMLEFT
        self._gen(moves, row_dir=-1, col_dir=1) # BOTTOMRIGHT

        return moves

class Queen(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _col(self, dir_):
        my_row, my_col = self.position
        
        d = -1 if dir_ < 0 else 1
        for col in xrange(1, abs(dir_)):
            yield (my_row, my_col + d*col)

    def _row(self, dir_):
        my_row, my_col = self.position

        d = -1 if dir_ < 0 else 1
        for row in xrange(1, abs(dir_)):
            yield (my_row + d*row, my_col)

    def _gen_rook(self, moves, gen, idx):
        for pos in gen(idx):
            piece = self.board[pos]
            
            if piece is None: 
                moves.append(pos)
                continue
            
            elif piece.team != self.team:
                moves.append(pos)

            break

    def _gen_bishop(self, moves, row_dir, col_dir):
        my_row, my_col = self.position

        for i in xrange(1, 8):
            row = row_dir*i
            col = col_dir*i
            q_row, q_col = my_row+row, my_col+col

            if not 0 <= q_row <= 7 or not 0 <= q_col <= 7:
                break

            piece = self.board[q_row, q_col]
            if piece is not None:
                if piece.team != self.team:
                    moves.append((q_row, q_col))
                break

            moves.append((q_row, q_col))

    def generate(self):
        moves = []

        my_row, my_col = self.position
        self._gen_rook(moves, self._col, 8-my_col) # RIGHT
        self._gen_rook(moves, self._col, -my_col-1) # LEFT
        self._gen_rook(moves, self._row, 8-my_row) # TOP
        self._gen_rook(moves, self._row, -my_row-1) # BOTTOM
        self._gen_bishop(moves, row_dir=1, col_dir=1) # TOPRIGHT
        self._gen_bishop(moves, row_dir=1, col_dir=-1) # TOPLEFT
        self._gen_bishop(moves, row_dir=-1, col_dir=-1) # BOTTOMLEFT
        self._gen_bishop(moves, row_dir=-1, col_dir=1) # BOTTOMRIGHT

        return moves

class Knight(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position
        self.type = KNIGHT

    def _gen(self, moves, row, col):
        if not 0 <= row <= 7 or not 0 <= col <= 7:
            return

        piece = self.board[(row, col)]
        if piece is None or self.is_opponent(piece):
            moves.append((row, col))

    def generate(self):
        moves = []
        my_row, my_col = self.position

        self._gen(moves, my_row+1, my_col+2)
        self._gen(moves, my_row+1, my_col-2)
        self._gen(moves, my_row-1, my_col+2)
        self._gen(moves, my_row-1, my_col-2)
        self._gen(moves, my_row+2, my_col+1)
        self._gen(moves, my_row+2, my_col-1)
        self._gen(moves, my_row-2, my_col+1)
        self._gen(moves, my_row-2, my_col-1)

        return moves
# =============================================================================

if __name__ == '__main__':
    color = 0
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = 1
            port = 50200

    bot = TestBot()
    bot.port = port

    bot.start()




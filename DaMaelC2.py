import time
import sys

from base_client import LiacBot

# Parameters

DEPTH = 3

V_PAWN = 5
V_OTHER = 10
M_PAWN = 2
COEF = 100


# ================================================================

WHITE = 1
BLACK = -1

EMPTY = 0
PAWN = 1
ROOK = 2
KNIGHT = 3

INFINITY = float('inf')

# BOT =========================================================================
class AlphaBetaBot(LiacBot):
    name = 'DaMael'

    def __init__(self):
        super(AlphaBetaBot, self).__init__()
        self.last_move = None

    def on_move(self, state):
        print 'Generating a move...',
        representation = Representation()
        representation.initialization(state)

        if state['bad_move']:
            print state['board']
            raw_input()

        t1 = time.time()
        eval,move = self.selectMove(representation, DEPTH)
        t2 = time.time()
        print eval, t2-t1

        self.last_move = move
        print move
        self.send_move(move[0], move[1])

    def on_game_over(self, state):
        print 'Game Over.'
        sys.exit()

#Alpha Beta ============================================================

    def remove(self,list,p):
        for i,pc in enumerate(list):
            if pc.position == p:
                piece = list.pop(i)
                return piece

    def selectMove(self, representation, depth):

        bestEval = -INFINITY
        bestMove = None

        for p in xrange(len(representation.my_pieces)):
            piece = representation.my_pieces[p]
            moves = representation.generateMov(piece)
            p1 = piece.position
            for p2 in moves:

                #Piece mouvement
                    #  board
                piece1 = representation.getP(p1)
                piece2 = representation.getP(p2)
                representation.setP(p1, EMPTY)
                representation.setP(p2, piece1)
                    # op_pieces list
                if representation.is_opponent(piece1,piece2):
                    pieceOp = self.remove(representation.op_pieces,p2)

                    # my_pieces list
                piece.position = p2

                eval = self.alpha_beta(representation, (depth - 1), -INFINITY, INFINITY, False)

                #Piece mouvement back
                    # board
                representation.setP(p1, piece1)
                representation.setP(p2, piece2)
                    # op_pieces list
                if representation.is_opponent(piece1,piece2):
                    representation.op_pieces.append(pieceOp)

                    # my_pieces list
                piece.position = p1

                if eval > bestEval:
                    bestEval=eval
                    bestMove=[p1,p2]

        return bestEval, bestMove




    def alpha_beta(self, representation, depth, alpha, beta, maximizingPlayer):

        # terminalNode ?
        for col in range(8):
            # White victory
            if representation.getP((7,col)) == PAWN:
                return representation.my_color * 10000 * (depth+1)
            # Black victory
            if representation.getP((0,col)) == PAWN:
                return representation.my_color * -10000 * (depth+1)

        leastPawnO = False
        for piece in representation.op_pieces:
            if piece.type == PAWN:
                leastPawnO = True
                break
        if leastPawnO == False:
            return 10000 * (depth+1)

        leastPawnM = False
        for piece in representation.my_pieces:
            if piece.type == PAWN:
                leastPawnM = True
                break
        if leastPawnM == False:
            return -10000 * (depth+1)

        # depth = 0 ?
        if depth == 0:
            return representation.evaluation()

        if maximizingPlayer:
            for p in xrange(len(representation.my_pieces)):

                piece = representation.my_pieces[p]
                moves = representation.generateMov(piece)
                p1 = piece.position
                for p2 in moves:

                    #Piece mouvement
                        #  board
                    piece1 = representation.getP(p1)
                    piece2 = representation.getP(p2)
                    representation.setP(p1, EMPTY)
                    representation.setP(p2, piece1)
                        # op_pieces list
                    if representation.is_opponent(piece1,piece2):
                        pieceOp = self.remove(representation.op_pieces,p2)

                        # my_pieces list
                    piece.position = p2

                    alpha = max(alpha, self.alpha_beta(representation, (depth - 1), alpha, beta, False))

                    #Piece mouvement back
                        # board
                    representation.setP(p1, piece1)
                    representation.setP(p2, piece2)
                        # op_pieces list
                    if representation.is_opponent(piece1,piece2):
                        representation.op_pieces.append(pieceOp)
                        # my_pieces list
                    piece.position = p1

                    if beta <= alpha: break
                if beta <= alpha: break
            return alpha
        else:
            for p in xrange(len(representation.op_pieces)):

                piece = representation.op_pieces[p]
                moves = representation.generateMov(piece)
                p1 = piece.position

                for p2 in moves:

                    #Piece mouvement
                        #  board
                    piece1 = representation.getP(p1)
                    piece2 = representation.getP(p2)
                    representation.setP(p1, EMPTY)
                    representation.setP(p2, piece1)
                        # op_pieces list

                    if representation.is_opponent(piece1,piece2):
                        pieceOp = self.remove(representation.my_pieces,p2)

                        # my_pieces list
                    piece.position = p2

                    beta = min(beta, self.alpha_beta(representation, (depth - 1), alpha, beta, True))

                    #Piece mouvement back
                        # board
                    representation.setP(p1, piece1)
                    representation.setP(p2, piece2)
                        # op_pieces list
                    if representation.is_opponent(piece1,piece2):
                        representation.my_pieces.append(pieceOp)
                        # my_pieces list
                    piece.position = p1

                    if beta <= alpha: break
                if beta <= alpha: break
            return beta


# MODELS ======================================================================
class Representation(object):
    def __init__(self):
        self.board = [[EMPTY for j in xrange(8)] for i in xrange(8)]
        self.my_pieces = []
        self.op_pieces = []
        self.my_color = None

    def initialization(self, state):
        self.my_color = state['who_moves']

        PIECES = {
            'r': Rook,
            'p': Pawn,
            'n': Knight,
        }

        PiecesBord = {
            'r': ROOK,
            'p': PAWN,
            'n': KNIGHT,
        }

        c = state['board']
        i = 0
        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                if c[i] != '.':

                    cls = PIECES[c[i].lower()]
                    clsB = PiecesBord[c[i].lower()]
                    color = BLACK if c[i].lower() == c[i] else WHITE

                    self.board[row][col] = color*clsB

                    piece = cls((row, col), color)
                    if color == self.my_color:
                        self.my_pieces.append(piece)
                    else:
                        self.op_pieces.append(piece)

                i += 1

    def getP(self, pos):
        if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7:
            return None
        return self.board[pos[0]][pos[1]]

    def setP(self, pos, value):
        self.board[pos[0]][pos[1]] = value




    # functions to generate movement

    def is_empty(self, pos):
        return self.getP(pos) == EMPTY

    def is_opponent(self,p1,p2):
        return p2 is not None and p1*p2 < 0

    def _col(self, piece, dir_):
        my_row, my_col = piece.position

        d = -1 if dir_ < 0 else 1
        for col in xrange(1, abs(dir_)):
            yield (my_row, my_col + d*col)

    def _row(self, piece, dir_):
        my_row, my_col = piece.position

        d = -1 if dir_ < 0 else 1
        for row in xrange(1, abs(dir_)):
            yield (my_row + d*row, my_col)

    def _genRook(self, piece, moves, gen, idx):

        for pos in gen(piece, idx):
            if self.is_empty(pos):
                moves.append(pos)
                continue
            elif self.is_opponent(self.getP(piece.position),self.getP(pos)):
                moves.append(pos)
            break

    def _genKnight(self, piece, moves, row, col):
        if not 0 <= row <= 7 or not 0 <= col <= 7:
            return

        if self.is_empty((row, col)) or self.is_opponent(self.getP(piece.position), self.getP((row, col))):
            moves.append((row, col))

    def generateMov(self, piece):

        moves = []
        my_row, my_col = piece.position
        d = piece.color

        #Pawn
        if piece.type == PAWN:
            # Movement to 1 forward
            pos = (my_row + d*1, my_col)
            if self.is_empty(pos):
                moves.append(pos)

            # Normal capture to right
            pos = (my_row + d*1, my_col+1)
            if self.is_opponent(self.getP(piece.position),self.getP(pos)):
                moves.append(pos)

            # Normal capture to left
            pos = (my_row + d*1, my_col-1)
            if self.is_opponent(self.getP(piece.position),self.getP(pos)):
                moves.append(pos)

        #Rook
        if piece.type == ROOK:
            self._genRook(piece, moves, self._col, 8-my_col) # RIGHT
            self._genRook(piece, moves, self._col, -my_col-1) # LEFT
            self._genRook(piece, moves, self._row, 8-my_row) # TOP
            self._genRook(piece, moves, self._row, -my_row-1) # BOTTOM

        #Knight
        if piece.type == KNIGHT:
            self._genKnight(piece, moves, my_row+1, my_col+2)
            self._genKnight(piece, moves, my_row+1, my_col-2)
            self._genKnight(piece, moves, my_row-1, my_col+2)
            self._genKnight(piece, moves, my_row-1, my_col-2)
            self._genKnight(piece, moves, my_row+2, my_col+1)
            self._genKnight(piece, moves, my_row+2, my_col-1)
            self._genKnight(piece, moves, my_row-2, my_col+1)
            self._genKnight(piece, moves, my_row-2, my_col-1)

        return moves


    def evaluation(self):

       # myScore
        myScore = 0
        nbsPawn = 0
        if self.my_color == WHITE:
             for piece in self.my_pieces:
                if piece.type == PAWN:
                    nbsPawn = nbsPawn + 1
                    row = piece.position[0]
                    myScore = myScore + V_PAWN*M_PAWN^(row-1)
                if piece.type == ROOK:
                    nbsMov = len(self.generateMov(piece))
                    myScore = myScore + V_OTHER+nbsMov
                if piece.type == KNIGHT:
                    nbsMov = len(self.generateMov(piece))
                    myScore = myScore + V_OTHER+nbsMov*2
        else:
            for piece in self.my_pieces:
                if piece.type == PAWN:
                    nbsPawn = nbsPawn + 1
                    row = piece.position[0]
                    myScore = myScore + V_PAWN*M_PAWN^(6-row)
                if piece.type == ROOK:
                    nbsMov = len(self.generateMov(piece))
                    myScore = myScore + V_OTHER+nbsMov
                if piece.type == KNIGHT:
                    nbsMov = len(self.generateMov(piece))
                    myScore = myScore + V_OTHER+nbsMov*2

        myScore = myScore + COEF * nbsPawn/len(self.my_pieces)

        # opScore
        opScore = 0
        nbsPawnO = 0
        if self.my_color != WHITE:
            for piece in self.op_pieces:
                if piece.type == PAWN:
                    nbsPawnO = nbsPawnO + 1
                    row = piece.position[0]
                    opScore = opScore + V_PAWN*M_PAWN^(row-1)
                if piece.type == ROOK:
                    nbsMov = len(self.generateMov(piece))
                    opScore = opScore + V_OTHER+nbsMov
                if piece.type == KNIGHT:
                    nbsMov = len(self.generateMov(piece))
                    opScore = opScore + V_OTHER+nbsMov*2
        else:
            for piece in self.op_pieces:
                if piece.type == PAWN:
                    nbsPawnO = nbsPawnO + 1
                    row = piece.position[0]
                    opScore = opScore + V_PAWN*M_PAWN^(6-row)
                if piece.type == ROOK:
                    nbsMov = len(self.generateMov(piece))
                    opScore = opScore + V_OTHER+nbsMov
                if piece.type == KNIGHT:
                    nbsMov = len(self.generateMov(piece))
                    opScore = opScore + V_OTHER+nbsMov*2

        opScore = opScore + COEF * nbsPawnO/len(self.op_pieces)

        return myScore-opScore


class Piece(object):
    def __init__(self):
        self.position = None
        self.type = EMPTY
        self.color = None

class Pawn(Piece):
    def __init__(self, position, color):
        self.position = position
        self.type = PAWN
        self.color = color


class Rook(Piece):
    def __init__(self, position, color):
        self.position = position
        self.color = color
        self.type = ROOK


class Knight(Piece):
    def __init__(self, position, color):
        self.position = position
        self.color = color
        self.type = KNIGHT



# =============================================================================

if __name__ == '__main__':
    color = 0
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = 1
            port = 50200

    bot = AlphaBetaBot()
    bot.port = port

    bot.start()

#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

class InputException( Exception ): pass
class TaskTypeError( InputException ): pass
class PlayerTypeError( InputException ): pass

next_line = lambda f: f.readline().rstrip()

class Reversi( object ):

    GREEDY      = '1'
    MINIMAX     = '2'
    ALPHA_BETA  = '3'
    COMPETITION = '4'

    BOARD_SIZE = 8

    base_weight = [ [ 99,  -8,  8,  6 ],
                    [ -8, -24, -4, -3 ],
                    [  8,  -4,  7,  4 ],
                    [  6,  -3,  4,  0 ] ]

    opponent_coord = []
    max_weight = -999
    best_move = None
    pre_coord = None

    def __init__( self ):
        with open( "input.txt", "U" ) as f:

            self.task_num = next_line( f )
            if self.task_num not in ( self.GREEDY, self.MINIMAX,
                                      self.ALPHA_BETA, self.COMPETITION ):
                raise TaskTypeError( task_num )

            self.player = next_line( f )
            if self.player not in ( 'X', 'O' ):
                raise PlayerTypeError( self.player )
            if self.player == 'X':
                self.opponent = 'O'
            else:
                self.opponent = 'X'

            self.cutoff_depth = int( next_line( f ) )
            self.read_states( f )
            self.init_weight()

    def init_weight( self ):
        self.init_weight = []
        for i in range(self.BOARD_SIZE):
            self.init_weight.append( [0]*8 )
        for i in range(4):
            for j in range(4):
                self.init_weight[i][j] = self.base_weight[i][j]
                self.init_weight[i][7-j] = self.base_weight[i][j]
                self.init_weight[7-i][j] = self.base_weight[i][j]
                self.init_weight[7-i][7-j] = self.base_weight[i][j]

    def read_states( self, fd ):
        self.init_states = []
        i = 0
        for line in fd:
            states = []
            j = 0
            for s in line.rstrip():
                states.append( s )
                if s == self.opponent:
                    self.opponent_coord.append( (i,j) )
                j = j + 1
            states = [ s for s in line.rstrip() ]
            self.init_states.append( states )
            i = i + 1
        assert( i == j == self.BOARD_SIZE )

    def find_best_move( self, ):
        pass
    def greedy( self, ):

        moves = []
        for op in self.opponent_coord:
            for x_move in ( -1, 0, 1 ):
                for y_move in ( -1, 0, 1 ):
                    if x_move | y_move == 0:
                        continue
                    val = self.calculate_val( op, [y_move, x_move] )
                    if val is not None:
                        #new_coord = ( op[0]+y_move, op[1]+x_move )
                        moves.append( ( val, ( op[0]+y_move, op[1]+x_move ) ) )

        if not moves:
            exit(0)

        # TODO equal
        self.best_move = max( moves, key=lambda x:x[0] )[1]

        self.convert_opponents( self.best_move )
        self.init_states[self.best_move[0]][self.best_move[1]] = self.player

        for i in self.init_states:
            print(i)

    def convert_opponents( self, new_move ):

        for i in ( -1, 0, 1 ):
            for j in ( -1, 0, 1 ):
                if i | j == 0:
                    continue
                x = new_move[0] + i
                y = new_move[1] + j
                if self.cross_edge( ( x, y ) ):
                    continue
                while self.init_states[x][y] == self.opponent:
                    self.init_states[x][y] = self.player
                    x = x + i
                    y = y + j
                    if self.cross_edge( ( x, y ) ):
                       break


    def minimax( self, ):
        pass

    def alphabeta( self, ):
        pass

    def cross_edge( self, coord ):

        if coord[0] < 0 or coord[1] < 0 or coord[0] >= self.BOARD_SIZE or coord[1] >= self.BOARD_SIZE:
            return True
        return False

    def calculate_val( self, orig_coord, move ):
        valid_move = False
        new_coord = (orig_coord[0]+move[0], orig_coord[1]+move[1])
        if self.init_states[ new_coord[0] ][ new_coord[1] ] != "*":
            return
        if self.cross_edge( new_coord ):
            return
        for i in range(self.BOARD_SIZE-1):
            tmp_coord = ( orig_coord[0]-move[0]*i, orig_coord[1]-move[1]*i )
            if self.cross_edge( tmp_coord ):
                return
            if self.init_states[ tmp_coord[0] ][ tmp_coord[1] ] == self.player:
                valid_move = True
                break

        if not valid_move:
            return

        return self.init_weight[ new_coord[0] ][ new_coord[1]]

        """
        if self.init_weight[ new_coord[0] ][ new_coord[1]] > self.max_weight:
            self.pre_coord = orig_coord
            self.best_move = new_coord
            self.max_weight = self.init_weight[ new_coord[0] ][ new_coord[1]]

        if self.init_weight[ new_coord[0] ][ new_coord[1]] == self.max_weight:
            if self.best_move[0] > new_coord[0]:
                self.pre_coord = orig_coord
                self.best_move = new_coord
                self.max_weight = self.init_weight[ new_coord[0] ][ new_coord[1]]
        """

if __name__ == "__main__":
    reversi = Reversi()
    reversi.greedy()

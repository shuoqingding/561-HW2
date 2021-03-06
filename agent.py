#!/usr/bin/env python2.6

from __future__ import absolute_import, division, print_function
import copy

class InputException( Exception ): pass
class TaskTypeError( InputException ): pass
class PlayerTypeError( InputException ): pass

next_line = lambda f: f.readline().rstrip()

def readable_value( val ):
    if val == -float("Inf"):
        return "-Infinity"
    elif val == float("Inf"):
        return "Infinity"
    return val

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
        self.log = []

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

    def print_node( self, node, alpha_beta=False ):
        coord = [ "a","b","c","d","e","f","g","h" ]
        if node['move'] in ( "root", "pass" ):
            move = node['move']
        else:
            move = coord[node['move'][1]]+str(node['move'][0]+1)

        value = readable_value( node['value'] )

        if alpha_beta:
            alpha = readable_value( node['alpha'] )
            beta = readable_value( node['beta'] )
            self.log.append( "{0},{1},{2},{3},{4}\n".format(
                move, node['depth'], value, alpha, beta ) )
        else:
            self.log.append( "{0},{1},{2}\n".format( move, node['depth'], value ) )

    def find_best_move( self, parent, max_depth=1, log=False, alpha_beta=False ):
        depth = parent['depth'] + 1
        if  depth > max_depth:
            return

        if depth % 2 == 1:
            value = float('Inf')
            player = self.player
            opponent = self.opponent
        else:
            value = -float('Inf')
            player = self.opponent
            opponent = self.player

        if self.is_end( parent['states'] ):
            parent['value'] = self.get_value( parent['states'] )
            return

        nodes = parent['children']

        has_move = False
        for x_move in range( self.BOARD_SIZE ):
            for y_move in range( self.BOARD_SIZE ):

                new_states = self.get_valid_states( (x_move, y_move), parent['states'], player, opponent )
                if new_states is None:
                    continue

                new_move = ( x_move, y_move )
                if depth == max_depth:
                    value = self.get_value( new_states )

                node = { "move"    : new_move,
                         "depth"   : depth,
                         "states"  : new_states,
                         "value"   : value,
                         "alpha"   : parent['alpha'],
                         "beta"    : parent['beta'],
                         "children": [] }
                has_move = True

                if self.is_end( new_states ):
                    return

                self.print_node( node, alpha_beta=alpha_beta )
                self.find_best_move( node, max_depth, log=log, alpha_beta=alpha_beta )
                if alpha_beta and ( ( depth % 2 == 1 and node['value'] >= parent['beta'] )\
                   or ( depth % 2 == 0 and node['value'] <= parent['alpha'] ) ):
                    if depth % 2 == 1:
                        parent['value'] = max( parent['value'], node['value'] )
                    else:
                        parent['value'] = min( parent['value'], node['value'] )
                    nodes.append( node )
                    self.print_node( parent, alpha_beta=alpha_beta )
                    return
                else:
                    if depth % 2 == 1:
                        parent['value'] = max( parent['value'], node['value'] )
                        parent['alpha'] = max( parent['alpha'], min( node['value'], node['beta'] ) )
                    else:
                        parent['value'] = min( parent['value'], node['value'] )
                        parent['beta'] = min( parent['beta'], max( node['value'], node['alpha'] ) )
                    nodes.append( node )
                    self.print_node( parent, alpha_beta=alpha_beta )

        if not has_move:
            if parent['move'] == 'pass':
                value = self.get_value( parent['states'] )

            node = { "move"    : "pass",
                     "depth"   : depth,
                     "states"  : parent['states'],
                     "value"   : value,
                     "alpha"   : parent['alpha'],
                     "beta"    : parent['beta'],
                     "children": [] }

            self.print_node( node, alpha_beta=alpha_beta )
            if parent['move'] != 'pass':
                self.find_best_move( node, max_depth,log=log, alpha_beta=alpha_beta )

            if alpha_beta and ( ( depth % 2 == 1 and node['value'] >= parent['beta'] )\
               or ( depth % 2 == 0 and node['value'] <= parent['alpha'] ) ):
                if depth % 2 == 1:
                    parent['value'] = max( parent['value'], node['value'] )
                else:
                    parent['value'] = min( parent['value'], node['value'] )
                nodes.append( node )
                self.print_node( parent, alpha_beta=alpha_beta )
                return
            else:
                if depth % 2 == 1:
                    parent['value'] = max( parent['value'], node['value'] )
                    parent['alpha'] = max( parent['alpha'], min( node['value'], node['beta'] ) )
                else:
                    parent['value'] = min( parent['value'], node['value'] )
                    parent['beta'] = min( parent['beta'], max( node['value'], node['alpha'] ) )
                nodes.append( node )
                self.print_node( parent, alpha_beta=alpha_beta )

    def is_end( self, states ):

        player_num = 0
        opponent_num = 0
        for i in range( self.BOARD_SIZE ):
            for j in range( self.BOARD_SIZE ):
                if states[i][j] == self.player:
                    player_num = player_num + 1
                if states[i][j] == self.opponent:
                    opponent_num = opponent_num + 1

        if opponent_num == 0 or player_num == 0 or\
           opponent_num + player_num == self.BOARD_SIZE*self.BOARD_SIZE:
            return True

        return False


    def get_valid_states( self, new_coord, states, player, opponent ):
        if states[ new_coord[0] ][ new_coord[1] ] != "*":
            return

        for x in ( 1,0,-1 ):
            for y in ( 1,0,-1 ):
                if x | y == 0 or self.cross_edge( (new_coord[0]+x,new_coord[1]+y) ):
                    continue
                updated_states = copy.deepcopy( states )
                updated_states[ new_coord[0] ][ new_coord[1] ] = player
                if states[ new_coord[0]+x ][ new_coord[1]+y ] == opponent:
                    updated_states[ new_coord[0]+x ][ new_coord[1]+y ] = player
                    for i in range(2,self.BOARD_SIZE):
                        tmp_coord = ( new_coord[0]+x*i, new_coord[1]+y*i )
                        if self.cross_edge( tmp_coord ) or\
                           states[ tmp_coord[0] ][ tmp_coord[1] ] == "*":
                            break
                        if states[ tmp_coord[0] ][ tmp_coord[1] ] == player:
                            return updated_states
                        updated_states[ tmp_coord[0] ][ tmp_coord[1] ] = player

        return

    def get_value( self, states ):
        value = 0
        for x in range( self.BOARD_SIZE ):
            for y in range( self.BOARD_SIZE ):
                if states[x][y] == self.player:
                    value = value + self.init_weight[x][y]
                elif states[x][y] == self.opponent:
                    value = value - self.init_weight[x][y]
        return value

    def greedy( self, ):
        self.minimax( 1, log=False )

    def cutoff_minimax( self ):
        self.minimax( self.cutoff_depth )

    def minimax( self, depth, log=True, alpha_beta=False ):

        root = { "value"   : -float('Inf'),
                 "states"  : copy.deepcopy( self.init_states ),
                 "depth"   : 0,
                 "alpha"   : -float('Inf'),
                 "beta"    : float('Inf'),
                 "move"    : 'root',
                 "children": [] }
        if log:
            if alpha_beta:
                self.log.append( "Node,Depth,Value,Alpha,Beta\n" )
            else:
                self.log.append( "Node,Depth,Value\n" )

            if self.is_end( self.init_states ):
                root['value'] = self.get_value( self.init_states )
            self.print_node( root, alpha_beta=alpha_beta )

        self.find_best_move( root, depth, log=log, alpha_beta=alpha_beta )

        if not root['children']:
            best_node = root
        else:
            max_node = max( root['children'], key=lambda x:x['value'] )
            max_value = max_node['value']
            best_node = None
            for node in root['children']:
                if node['value'] == max_value:
                    if best_node is None or\
                       node['move'][0]*10 + node['move'][1] < best_node['move'][0]*10 + best_node['move'][1]:
                        best_node = node

        with open( "output.txt", "w" ) as fout:
            for i in best_node['states']:
                fout.write( "".join(i) + '\n' )
            for log in self.log:
                fout.write( log )

    def alphabeta( self, ):
        self.minimax( self.cutoff_depth, log=True, alpha_beta=True )

    def cross_edge( self, coord ):
        if coord[0] < 0 or coord[1] < 0 or\
           coord[0] >= self.BOARD_SIZE or\
           coord[1] >= self.BOARD_SIZE:
            return True

        return False

    def run( self, ):
        if self.task_num == "1":
            self.greedy()
        if self.task_num == "2":
            self.cutoff_minimax()
        if self.task_num == "3":
            self.alphabeta()

if __name__ == "__main__":
    reversi = Reversi()
    reversi.run()

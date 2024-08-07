"""
Randomly generate templates for the private/shared game.

Creates files in ./instances and ./requests
"""
from tqdm import tqdm

import re
import string
import random
import chess
import sys
import clemgame
from clemgame.clemgame import GameInstanceGenerator
from games.chess_withvariants.utils.board_functions import  piece_values,board_to_text,matrix_to_fen,fen_to_matrix,generateBoard


GAME_NAME = "chess_withvariants"
N_INSTANCES= 2 #Let's start small
SEED = 123



class ChessGameInstanceGenerator(GameInstanceGenerator):
    """
        FEN stands for Forsyth-Edwards Notation. These are the general rules that define a board:
        Default board is:
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        Where: 
            "w" ->  White's turn
            "KQkq" ->   Castling available  on white(KQ) on  King (K) and Queen(Q) side.
                        Castling available  on black(kq) on  King (q) and Queen(q) side.
            "-" ->  No enpassant
            "0" ->  Number of half-moves
            "1" ->  Number of full-moves (begins at 1).
        
        We want to generate the following combinations of games:
            - Normal game (baseline for an easy test)
            - Chess puzzles
            - Randomized (with fairness) starting position of figures.
            - Randomized (with fairness) starting figures.
            - Combination of last 2 methods (which opens exponentially different generations).

    """
    

    ##TODO: TEST
    def __init__(self):
        super().__init__(GAME_NAME)



    ##TODO: TEST
    def on_generate(self):
        #Dont need this one; we will generate each Board in a different manner
        #self.experiment_config = self.load_json("resources/config.json")
        #self.instance_utils = InstanceUtils(self.experiment_config, self.game_name)


        ### GENERATE BASELINE
        
        #self.baseline_template = self.load_template('resources/terse_prompt_baseline.template')
        experiments = {
            'baseline' : (lambda :generateBoard()),
            #'random_8_figures' : (lambda :self.randomBoard(piece_amount=8)),
            'random_16_figures' : (lambda :self.randomBoard()),
            #'random_24_figures' : (lambda :self.randomBoard(piece_amount=24)),
            'chess960_1' : (lambda :(chess.Board.from_chess960_pos(random.randint(0,959)).fen().split()[0])),
            #'chess960_2' : (lambda :(chess.Board.from_chess960_pos(random.randint(0,959)).fen().split()[0])),
            #'chess960_2' : (lambda :(chess.Board.from_chess960_pos(random.randint(0,959)).fen().split()[0]))
        }
        #experiments = {  'baseline' : (lambda :generateBoard())}
        n_turns = [6,30]
        n_turns = [10]
        #n_turns = [400]
        
        for exp_name in experiments:
            for  i in ['verbose','brief']:
                for j in ['','no']:
                    exp_ending = f'_{i}_{j}preamble' 
                    filename= f'resources/{exp_ending}_prompt.template'
                    template = self.load_template(filename)
                    for board_reminder in [True,False] :
                        exp_ending += '' if  not board_reminder else f'_reminder'
                        experiment = self.add_experiment(exp_name+ exp_ending)
                        for idx,num in enumerate(n_turns):
                            instance = self.add_game_instance(experiment,idx)
                            instance['board']=  (experiments[exp_name])()
                            instance['n_turns']= num
                            instance['board_reminder'] = board_reminder
                            board= str(chess.Board(fen=instance['board']))
                            variant = ""
                            pieces = ""
                            if exp_name.split('_')[0] == 'random':
                                pieces = exp_name.split('_')[1]
                                variant = "You are playing a variant of chess where each player plays with " +pieces+ "randomised pieces."
                            elif exp_name.split('_')[0] == 'chess960':
                                variant = "You are playing a game of Fischer random chess (Chess960)."
                            prompt = string.Template(template) \
                                    .substitute(skill='expert',board=board,variant=variant)
                            
                            instance['initial_prompt'] = prompt

        

    ##TODO: TEST
   
    ###UNTESTED FUNCTION
    def evaluateBoardFair(self,board):
        """
        Check if the values of pieces on either side is fair or not
        """
        error_quotient=0.1
        w_value = 0
        b_value = 0
        for row in board:
            for piece in row:
                if piece is None or piece.lower()== 'k':
                    continue
                elif piece.isupper():
                    w_value += piece_values[piece.lower()]
                elif piece.islower():
                    b_value += piece_values[piece]
        allowed_error= max(b_value,w_value)*error_quotient
        if  b_value < w_value:
            return b_value+allowed_error >= w_value
        else:
            return  w_value +allowed_error >= b_value

    ##TODO: TEST
    ###UNTESTED FUNCTION
    def randomPiece(self):
        """ Returns a random piece """
        piece_options= list(piece_values.keys())
        return piece_options[random.randint(0,len(piece_options)-1)]
    
    ##TODO: TEST
    ###UNTESTED FUNCTION
    def randomBoard(self,piece_amount=16):
        """
        Generates a random board with pieceAmount pieces per player. Follows a set of rules for  avoiding unfair configurations: 
        - The king must always be in the farthest row from the center.
        - The amount of pieces per side must be equal. 
        - Pieces in the board will be filled from the farthest row to the center, putting pieces as far from the center rows as possible.
        """
        boardL = 8
        board =  [['Q']*boardL for _ in range(boardL)]
        if piece_amount > 24:
            raise 'Too many pieces!!'
        n_turns = [4,7,10,10]
        for exp_name in experiments:
            experiment = self.add_experiment(exp_name)
            for idx,num in enumerate(n_turns):
                instance = self.add_game_instance(experiment,idx)
                instance['board']=  (experiments[exp_name])()
                instance['n_turns']= num
                #print(instance['board'])
                #assert(False)
                board= str(chess.Board(fen=instance['board']))
                prompt = string.Template(self.baseline_template) \
                        .substitute(skill='expert',board=board)
                instance['initial_prompt'] = prompt

        

    ##TODO: TEST
   
    ###UNTESTED FUNCTION
    def evaluateBoardFair(self,board):
        """
        Check if the values of pieces on either side is fair or not
        """
        error_quotient=0.1
        w_value = 0
        b_value = 0
        for row in board:
            for piece in row:
                if piece is None or piece.lower()== 'k':
                    continue
                elif piece.isupper():
                    w_value += piece_values[piece.lower()]
                elif piece.islower():
                    b_value += piece_values[piece]
        allowed_error= max(b_value,w_value)*error_quotient
        if  b_value < w_value:
            return b_value+allowed_error >= w_value
        else:
            return  w_value +allowed_error >= b_value

    ##TODO: TEST
    ###UNTESTED FUNCTION
    def randomPiece(self):
        """ Returns a random piece """
        piece_options= list(piece_values.keys())
        return piece_options[random.randint(0,len(piece_options)-1)]
    
    ##TODO: TEST
    ###UNTESTED FUNCTION
    def randomBoard(self,piece_amount=16):
        """
        Generates a random board with pieceAmount pieces per player. Follows a set of rules for  avoiding unfair configurations: 
        - The king must always be in the farthest row from the center.
        - The amount of pieces per side must be equal. 
        - Pieces in the board will be filled from the farthest row to the center, putting pieces as far from the center rows as possible.
        """
        boardL = 8
        board =  [['Q']*boardL for _ in range(boardL)]
        if piece_amount > 24:
            raise 'Too many pieces!!'
        i = 0
        while not self.evaluateBoardFair(board): 
            #print(f"attempt #{i} to generate a random board")
            #print(chess.Board(matrix_to_fen(board)))
            i+=1
            board =  [[None]*boardL for _ in range(boardL)]
            board[0][random.randint(0,boardL-1)]='k' 
            board[-1][random.randint(0,boardL-1)]='K' 
            # PENDING TO TEST THIS
            pieces_added = 0
            row = 0 
            col = 0
            while pieces_added < piece_amount:
                if board[row][col] is None :
                    board[row][col] = self.randomPiece() 
                col+=1
                if col == boardL: 
                    col =0
                    row +=1
                pieces_added+=1
            pieces_added = 0
            row = -1 
            col = -1
            while pieces_added < piece_amount:
                if board[row][col] is None :
                    board[row][col] = self.randomPiece().upper()
                col += -1
                if -col == boardL+1 : 
                    col = -1
                    row += -1
                pieces_added+=1
        print('-----FINAL BOARD-------')
        print(chess.Board(matrix_to_fen(board)))
        return matrix_to_fen(board)


   

if __name__ == "__main__":
    random.seed(SEED)
    ChessGameInstanceGenerator().generate()

"""Student agent: edit ONLY this file."""
from agents.agent import Agent
from store import register_agent
from helpers import (Move, get_valid_moves, execute_move, check_winner,
                     check_endgame, random_move, copy_state, top_view, LINES)
from constants import *
import numpy as np
import time


# weight of material in total_score
W_MATERIAL = 1
# weights per piece, [S, M, L]
WEIGHTS = [1, 2, 3]
# factor to prefer moving a piece on the board instead of taking out of reserve
PREF = 0.5


def material(board, reserves, player, owners, sizes):
    m_score = 0
    # for each piece size, subtract opponent's available pieces from player's, then multiply by weight
    for size in range(NUM_SIZES):
        m_score = m_score + (WEIGHTS[size]) * (reserves[player, size] - reserves[3 - player, size])

    # for each cell, add weight of piece for player, subtract weight of piece of opponent
    # a piece on the board weighs less than a piece in reserve, because we prefer moving a piece on the board than wasting a reserve piece for a similar gain, since reserve pieces are guaranteed flexibility
    for row in range(board.shape[0]):
        for col in range(board.shape[1]):
            if owners[row, col] == player:
                m_score = m_score + PREF*WEIGHTS[sizes[row, col]]

            if owners[row, col] == (3 - player):
                m_score = m_score - PREF*WEIGHTS[sizes[row, col]]        

    return m_score


#helper function to count the pieces on the board
def pieces_on_board (owners, sizes,player):
    # 2 arrays for the 2 players, where indices are piece size
    player_1=[0,0,0]
    player_2=[0,0,0]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            #looping over each column and rows, you check who is the owner, and add 1 in the array according to the size of the piece on the board
    
            if owners[r,c]==player:
                player_1[sizes[r,c]]+=1

            elif owners[r,c] == 3-player:
                player_2[sizes[r,c]]+=1

    return player_1, player_2


#helper function to pool together the reserve and the pieces on the board
def pool (player, reserves, player_1, player_2, line, owners,sizes):
     pool_1=[0,0,0]
     pool_2=[0,0,0]
     # you just add up the pieces on the board and the reserve
     for i in range (3):
         pool_1[i]=reserves[player,i] + player_1[i]
         pool_2[i]=reserves[3-player,i] + player_2[i]
    #for each couple in the line we are in, you delete the pieces on the line since they cant be moved
     for couple in line:
        if owners[couple]==player:
            pool_1[sizes[couple]]-=1
        elif owners[couple]==3-player:
            pool_2[sizes[couple]]-=1

     return pool_1, pool_2
         
    
def evaluate (board, reserves, player):
        total_score=0
        threats=0 
        his_threats=0

        
        #get the owner and size of each block on each square
        owners, sizes= top_view(board)
        player_1, player_2=pieces_on_board(owners, sizes, player)
        # for every line of size 4, so 4 columns, 4 rows, 2 diagonlas
        for line in LINES[WIN_LENGTH]:
            
            obstacle=False #set a variable to false so we dont give an accidental score to a line with a obstacle
            score_1=0
            score_2=0
            for couple in line: #each couple is one sqaure in the line, there is 4
                if owners[couple]==3: #when the owner is 3, that mean there is an obstacle
                    obstacle=True
                     
                
                if owners[couple]==player:
                    score_1+=1

                elif owners[couple]==3-player:
                    score_2+=1


            #this is so we skip the scoring
            if(obstacle!=False):
                continue
            #we only score lines occupied by 1 player only, and we scale the score by a 10 factor
            if score_1>0 and score_2==0:
                    if score_1==3:
                        threats+=1
                    total_score+= 10 ** score_1

            elif score_2>0 and score_1==0:
                    #if opponent has 3 pieces, worsen the score since he can win
                    if score_2==3:
                    
                        total_score-=10 ** score_2 *100
                        his_threats+=1

                    else:
                        total_score-=10 ** score_2
            #now we score lines that are mixed, so both players occupy
            elif score_1>0 and score_2>0:

                 pool_1,pool_2=pool(player,reserves,player_1,player_2,line,owners,sizes)
                 can_cover=True
                 #we recheck each couple in line
                 for couple in line:
                      bigger=False
                     #here we check the owner is the other player
                      if owners[couple]==3-player:
                           #then we check indices of blocks only bigger then the other players block
                           for i in range (sizes[couple]+1, 3):
                                if (not bigger):
                                    #if we have at least 1 bigger, we remove it from the copy reserve and set bigger to true to not double count bigger blocks
                                    if pool_1[i]>0 :
                                        pool_1[i]-=1
                                        bigger=True 

                           if not bigger: # if bigger stayed false through that line, we had no block in the reserve to cover it
                                can_cover=False
                
                # if we are able to cover each block in the line, we give it a good score, but less good then open line
                 if  can_cover:
                      if score_1==3:
                          threats+=1
                      total_score+= 10** score_1 //2


                # Here we do the exact same thing but for the other players view
                
                 he_can_cover=True
                 for couple in line:
                    bigger=False
                    if owners[couple]==player:
                        for i in range (sizes[couple]+1, 3):
                            if (not bigger):
                                if pool_2[i]>0:
                                    pool_2[i]-=1
                                    bigger=True
                
                        if not bigger: 
                            he_can_cover=False
                                
                
                 if  he_can_cover:
                    #added the same evalutaion for when the other player has 3 in one line
                    if score_2==3:
                        total_score-=10** score_2 //2 *100
                        his_threats+=1
                    else:
                        total_score-= 10** score_2 //2                
                        total_score-= 10** score_2 //2
        if threats>=2 and his_threats==0:
            total_score+=100000


        total_score += W_MATERIAL * material(board, reserves, player, owners, sizes)
        return total_score

            


def search (board, reserves, player, ply, deadline):

    #get all valid moves from present board
    valid_moves_list =get_valid_moves(board, reserves, player)
    #this will be the variable that keeps track of the best move
    best_move=None
    #best score starts at worst value
    best_score=-float("inf")


    #for each move, copy current state, execute the move and gets its score
    for move in valid_moves_list:
        b, r=copy_state(board, reserves)
        execute_move(b, r, player, move)
        done, winner, why=check_endgame(b,r, 3-player, ply + 1)
        #if move is winner, do that move 
        if winner==player:
            return move
        #here all other moves are 0 since eval is 0 for all moves
        score =evaluate(b,r, player)
        #except if move makes other player win, then give bad score so it never picks it
        if winner==3-player:
            score=-10000000000
        
        #keep updating best move
        if(score>best_score): 
            best_score=score
            best_move=move

    return best_move
    

        


@register_agent("student_agent")          # do not change this string
class StudentAgent(Agent):
    def __init__(self):
        """Set up your agent. This runs once per game, before the first move, and must finish
        within INIT_TIME_LIMIT seconds."""
        super().__init__()
        self.name = "StudentAgent"
        self.counter=0

    def step(self, board, reserves, player, opponent):
        """Return the Move you want to play.

        Takes: board, reserves - your own copies of the current position.
               player, opponent - your player number (1 or 2) and the other one.
        Agent.step in agents/agent.py explains each argument and the time limit.
        """
        
        start = time.perf_counter()
        deadline=start+2
        ply= 2*self.counter + player -1
        self.counter +=1
        
    

        # ALLOW_MOVES and WIN_LENGTH (from constants) are the rule flags of this game.
        # helpers.get_valid_moves / check_winner already respect them; your own
        # move generator and evaluation function must too.
        # TODO: replace with your search. Keep (time.perf_counter() - start) < STEP_TIME_LIMIT - margin.
        return search (board, reserves, player, ply, deadline)

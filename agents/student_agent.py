"""Student agent: edit ONLY this file."""
from agents.agent import Agent
from store import register_agent
from helpers import (Move, get_valid_moves, execute_move, check_winner,
                     check_endgame, random_move, copy_state, top_view, LINES)
from constants import *
import numpy as np
import time


def evaluate (board, reserves, player):
        total_score=0

        
    
        owners, sizes= top_view(board)
        for line in LINES[WIN_LENGTH]:
        
            obstacle=False
            score_1=0
            score_2=0
            for couple in line:
                if owners[couple]==3:
                    obstacle=True
                     
                
                if owners[couple]==player:
                    score_1+=1

                elif owners[couple]==3-player:
                    score_2+=1

            if(obstacle!=False):
                continue

            if score_1>0 and score_2==0:
                    total_score+= 10 ** score_1

            elif score_2>0 and score_1==0:
                    total_score-=10 ** score_2


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

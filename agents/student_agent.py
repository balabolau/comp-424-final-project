"""Student agent: edit ONLY this file."""
from agents.agent import Agent
from store import register_agent
from helpers import (Move, get_valid_moves, execute_move, check_winner,
                     check_endgame, random_move, copy_state, top_view)
from constants import *
import numpy as np
import time

def evaluate (board, reserves, player):
    return 0




def make_move(board, reserves, player, move):
    # Make the move on the board so we can search the next state.
    if move.src is None:
        reserves[player, move.size] -= 1
    else:
        row, col = move.src
        board[row, col, move.size] = 0

    row, col = move.dest
    board[row, col, move.size] = player


def undo_move(board, reserves, player, move):
    # Put the piece back so the next move uses the original state.
    row, col = move.dest
    board[row, col, move.size] = 0

    if move.src is None:
        reserves[player, move.size] += 1
    else:
        row, col = move.src
        board[row, col, move.size] = player


def order_moves(board, reserves, turn, moves, player, end_time):
    # Try better moves first so alpha-beta can skip more branches.
    scores = []

    for i in range(len(moves)):
        if time.perf_counter() >= end_time:
            raise TimeoutError

        move = moves[i]
        make_move(board, reserves, turn, move)

        try:
            winner = check_winner(board, turn)

            if winner == player:
                score = 1000000
            elif winner == 3 - player:
                score = -1000000
            else:
                # The evaluation function is provided by the other teammate.
                score = evaluate(board, reserves, player)
        finally:
            undo_move(board, reserves, turn, move)

        scores.append((score, i, move))

    scores.sort(key=lambda x: x[0], reverse=(turn == player))
    return [item[2] for item in scores]


def minimax(board, reserves, turn, player, depth, alpha, beta, ply, end_time):
    # Stop the search if we are getting close to the time limit.
    if time.perf_counter() >= end_time:
        raise TimeoutError

    if ply >= MAX_PLIES:
        return 0

    if depth == 0:
        return evaluate(board, reserves, player)

    moves = get_valid_moves(board, reserves, turn)

    if not moves:
        # With movement on, a player with no legal moves loses.
        if constants.ALLOW_MOVES:
            return -1000000 if turn == player else 1000000

        # With movement off, a player may have to skip a turn.
        other_moves = get_valid_moves(board, reserves, 3 - turn)
        if not other_moves:
            return 0
        return minimax(board, reserves, 3 - turn, player, depth - 1,
                       alpha, beta, ply + 1, end_time)

    if depth > 1:
        moves = order_moves(board, reserves, turn, moves, player, end_time)

    if turn == player:
        best = -float('inf')
    else:
        best = float('inf')

    for move in moves:
        if time.perf_counter() >= end_time:
            raise TimeoutError

        make_move(board, reserves, turn, move)

        try:
            winner = check_winner(board, turn)

            if winner == player:
                score = 1000000 + depth
            elif winner == 3 - player:
                score = -1000000 - depth
            elif ply + 1 >= MAX_PLIES:
                score = 0
            else:
                score = minimax(board, reserves, 3 - turn, player,
                                depth - 1, alpha, beta, ply + 1, end_time)
        finally:
            undo_move(board, reserves, turn, move)

        if turn == player:
            # MAX keeps the highest score.
            if score > best:
                best = score
            if best > alpha:
                alpha = best
        else:
            # MIN keeps the lowest score.
            if score < best:
                best = score
            if best < beta:
                beta = best

        if alpha >= beta:
            break

    return best


def search (board, reserves, player, ply, deadline):
     # Start with a legal move in case we run out of time.
    moves = get_valid_moves(board, reserves, player)
    if not moves:
        return None

    best_move = moves[0]
    depth = 1

    # Search one level deeper each time we finish a full search.
    while time.perf_counter() < end_time:
        alpha = -float('inf')
        beta = float('inf')
        best = -float('inf')
        next_move = best_move

        ordered = [best_move] + [move for move in moves if move != best_move]

        try:
            if depth > 1:
                ordered = order_moves(board, reserves, player, ordered,
                                      player, end_time)
                ordered.remove(best_move)
                ordered.insert(0, best_move)

            for move in ordered:
                if time.perf_counter() >= end_time:
                    raise TimeoutError

                make_move(board, reserves, player, move)

                try:
                    winner = check_winner(board, player)

                    if winner == player:
                        score = 1000000 + depth
                    elif winner == 3 - player:
                        score = -1000000 - depth
                    elif ply + 1 >= MAX_PLIES:
                        score = 0
                    else:
                        score = minimax(board, reserves, 3 - player, player,
                                        depth - 1, alpha, beta, ply + 1, end_time)
                finally:
                    undo_move(board, reserves, player, move)

                if score > best:
                    best = score
                    next_move = move

                if best > alpha:
                    alpha = best

            # Only save the new move after the whole depth is finished.
            best_move = next_move

            if best >= 1000000:
                break

            depth += 1
        except TimeoutError:
            # Keep the last completed result instead of the unfinished one.
            break

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

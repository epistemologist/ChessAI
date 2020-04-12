from game import *
from score import *

import cProfile

BOARD = "rqkr\npppp\nPPPP\nRQKR"
WINNING_FUNCTION = checkmate
DEPTH = 4

def get_next_boards(board):
	out = []
	for move in board.get_all_moves():
		temp_board = EmptyBoard()
		temp_board.deep_copy(board)
		if move[0] == 'move':
			try:
				temp_board.move(temp_board.get_piece(move[1].position), move[2])
				out.append(temp_board)
			except Exception as e: pass
		if move[0] == 'capture':
			try:
				temp_board.capture(temp_board.get_piece(move[1].position),temp_board.get_piece(move[2]))
				out.append(temp_board)
			except Exception as e: pass
	return out
def main():
	board = process_board(BOARD, True)
	game_tree = [[board]]
	visited_boards = [board]
	for i in range(DEPTH):
		current_level = []
		for b in game_tree[-1]:
			for potential_board in get_next_boards(b):
				if WINNING_FUNCTION(potential_board) == 0 and potential_board not in visited_boards:
					current_level.append(potential_board)
					visited_boards.append(potential_board)
		game_tree.append(current_level)
		print(i,len(current_level),len(visited_boards))

cProfile.run("main()")

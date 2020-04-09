from game import *
from score import *
from ai import *

BOARD = "ppp\n...\nPPP"
SCORE_FUNCTION = hexapawn
WINNING_FUNCTION = hexapawn
DEPTH = 15

def gen_next_move(board):
	new_board = Board(0,0,[],False)
	new_board.deep_copy(board)
	new_board.history = []
	board_node = BoardNode(new_board, scoring_function = SCORE_FUNCTION)
	winning_position = alpha_beta(board_node, DEPTH, float("-inf"), float("inf"), True)
	next_move = winning_position.board.history[0]
	piece_from, piece_to = next_move.positions
	print(next_move)
	if next_move.type == 'move':
		board.move(board.get_piece(piece_from), piece_to)
	if next_move.type == 'capture':
		board.capture(board.get_piece(piece_from), board.get_piece(piece_to))
	return board


board = process_board(BOARD, True)
print(board)
while True:
	x1,y1,x2,y2 = [int(i) for i in input().split()]
	next_board = make_move(board, (x1,y1), (x2,y2))
	if next_board == None:
		print("Invalid move!")
		continue
	else:
		board = next_board
		print("Your Move")
		print(board, WINNING_FUNCTION(board))
		if WINNING_FUNCTION(board) == 1:
			print("You win!")
			break
		print("AI Move")
		board = gen_next_move(board)
		print(board, WINNING_FUNCTION(board))
		if WINNING_FUNCTION(board) == -1:
			print("You lose!")
			break

		

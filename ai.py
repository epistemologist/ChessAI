from game import *
from score import *

import traceback
# Node that stores a chess board in a tree
class BoardNode:
	def __init__(self, board, scoring_function = lambda x: None):
		self.board = board
		self.scoring_function = scoring_function
		self.score = scoring_function(board)
		self.children = []
		self.possible_moves = []
	def update_children(self):
		if len(self.children) != 0: return
		for move in self.board.get_all_moves():
			temp_board = EmptyBoard()
			temp_board.deep_copy(self.board)
			if move[0] == "move":
				try:
					temp_board.move(temp_board.get_piece(move[1].position), move[2])
					self.children.append(BoardNode(temp_board, self.scoring_function))
					self.possible_moves.append((move[1].position, move[2]))
				except Exception as e: pass
			if move[0] == "capture":
				try:
					temp_board.capture(temp_board.get_piece(move[1].position),
						               temp_board.get_piece(move[2]))
					self.children.append(BoardNode(temp_board, self.scoring_function))
					self.possible_moves.append((move[1], move[2]))
				except Exception as e: pass
	def __repr__(self):
		return self.board.__repr__()
# Implementation of alpha-beta pruning
@lru_cache(maxsize=None)
def alpha_beta(node,depth,a,b,maximizing_player):
    if depth == 0:
        return node
    node.update_children()
    if len(node.children) == 0:
        return node
    if maximizing_player:
        temp_score = float("-inf")
        temp_node = None
        for child in node.children:
            temp = alpha_beta(child, depth-1, a, b, False)
            if temp.score > temp_score:
                temp_score = temp.score
                temp_node = temp
            a = max(a, temp_score)
            if a >= b:
                break
        return temp_node
    else:
        temp_score = float("inf")
        temp_node = None
        for child in node.children:
            temp = alpha_beta(child, depth-1, a, b, True)
            if temp.score < temp_score:
                temp_score = temp.score
                temp_node = temp
            b = min(b,temp_score)
            if a >= b:
                break
        return temp_node


board = process_board("ppp\n...\nPPP",True)
board.move(board.get_piece((1,2)), (1,1))
board_node = BoardNode(board, scoring_function = hexapawn)


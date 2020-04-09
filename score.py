def naive_scoring_function(board_in):
	score = 0
	for piece in board_in.pieces:
		score += piece.score * (1 if piece.direction else -1)
	return score * (1 if board_in.turn else -1)

def winning_scoring_function(board_in):
	if len(board_in.get_all_moves()) != 0: return 0
	score_player, score_ai = board_in.scores
	return 1 if score_player > score_ai else -1
	
def hexapawn(board_in):
	if len(board_in.get_all_moves()) == 0:
		score_player, score_ai = board_in.scores
		return 1 if score_player > score_ai else -1
	else:
		for piece in board_in.pieces:
			if piece.position[1] == 0 and piece.direction: return 1
			if piece.position[1] == 2 and not piece.direction: return -1
	return 0
	
def checkmate(board_in):
	kings = []
	for piece in board_in.pieces:
		if piece.piece_type == 'king': kings.append(piece)
	if len(kings)==1:
		return 1 if kings[0].direction else -1
	return 0

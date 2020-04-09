import copy
from functools import lru_cache
from collections import namedtuple
# Utility functions
dist = lambda p1, p2: (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

# Class to store the current state of a board (used to store the history of the board)
class BoardState(namedtuple("BoardState", "type positions board")):
	def __eq__(self, other):
		return self.type == other.type and self.positions == other.positions and self.board == other.board
# Gets all squares on the chess board between pos1 and pos2
def chess_path(pos1, pos2):
	path = [pos2]
	if pos1[1] > pos2[1]:
		pos1, pos2 = pos2, pos1
	x1, y1 = pos1
	x2, y2 = pos2
	if x1 == x2:
		path.extend([(x1, i) for i in range(min(y1, y2), max(y1, y2)+1)])
	if y1 == y2:
		path.extend([(i, y1) for i in range(min(x1, x2), max(x1, x2)+1)])
	if (y2 - y1) == (x2 - x1):
		path.extend([(x1+i, y1+i) for i in range(y2-y1+1)])
	if (x2 - x1) == -(y2 - y1):
		path.extend([(x1-i, y1+i) for i in range(y2-y1+1)])
	return sorted(list(set(path)))


# Python class for a game piece
class Piece:
	def __init__(self, position, direction, piece_type, char, icon, get_moves, get_captures, board_size, score):
		# position of piece on the board
		self.position = position
		# direction of piece - True if piece goes from bottom to top and False if piece goes from top to bottom
		# i.e. True if piece is black, False if piece is white
		self.direction = direction
		# boolean flag determining whether or not this piece has moved yet (used to deal with pawn logic)
		self.has_moved = False
		# string determining piece type
		self.piece_type = piece_type
		# char that represents piece when printing board
		self.char = char
		# string to store image file to represent piece
		# for future use if we want to make a web interface
		self.icon = icon
		# function that given position of piece, gives all valid positions that the piece can move to
		self.get_moves = get_moves
		# function that given position of piece, gives all valid positions that piece can capture
		self.get_captures = get_captures
		# get board size to help with the two above functions
		self.board_size = board_size
		# score of the piece, used in scoring current board
		self.score = score

	# representation of the piece object
	
	def __repr__(self):
		return ("black " if self.direction else "white ") + self.piece_type + " at " + str(self.position)

	# equals method
	def __eq__(self, other):
		return self.position == other.position and \
			self.direction == other.direction and \
			self.has_moved == other.has_moved and \
			self.piece_type == other.piece_type and \
			self.char == other.char and \
			self.icon == other.icon and \
			self.get_moves == other.get_moves and \
			self.get_captures == other.get_captures and \
			self.board_size == other.board_size and \
			self.score == other.score
	def __hash__(self):
		# return hash((self.position, self.direction, self.has_moved)) # too slow!!!
		"""
		self.char -> 8 bits
		self.position -> (4 bits, 4 bits)
		self.has_moved -> 1 bit
		
		total = 17 bits
		"""
		out = 1<<8
		out += ord(self.char)
		out <<= 4
		out += self.position[0]
		out <<= 4
		out += self.position[1]
		out <<= 1
		out += int(self.has_moved)
		return out
	def get_valid_moves(self):
		return self.get_moves(self.position, self.board_size, self.direction, self.has_moved)

	def get_valid_captures(self):
		return self.get_captures(self.position, self.board_size, self.direction, self.has_moved)

# Python class for implementing a board


class Board:
	def __init__(self, length, width, pieces, turn):
		# check to make sure all pieces have valid positions
		for piece in pieces:
			x, y = piece.position
			if not(0 <= x < length and 0 <= y <= width):
				raise ValueError("One of the pieces has an invalid position!")
		# length of the board
		self.length = length
		# width of the board
		self.width = width
		# pieces on the board (stored as an array)
		self.pieces = pieces
		# move history
		self.history = []
		# which piece's turn it is to move next
		self.turn = turn
		# scores of the two players
		self.scores = [0,0]

	def get_piece(self, pos):
		# returns the piece at given position if any
		for piece in self.pieces:
			if piece.position == pos:
				return piece
		return None

	def move(self, piece, position):
		# keep track of old position to add to history
		old_position = piece.position
		# make sure the piece is on the board
		if piece not in self.pieces:
			raise ValueError("The given piece is not on the board!")
		# make sure given path is not obstructed
		occupied_positions = [p.position for p in self.pieces]
		path = chess_path(piece.position, position)
		#print("occupied positions", occupied_positions)
		#print("path", path)
		for p in occupied_positions:
			if p in path and p != piece.position:
				raise ValueError("Given path is obstructed!")
		# make sure that it is this piece's turn to move
		if self.turn != piece.direction:
			raise ValueError("Not this piece's turn!")
		# check to make sure that this is a valid move
		# get all valid positions that this piece can go to
		valid_positions = piece.get_valid_moves()
		#print("valid_positions", valid_positions)
		if position not in valid_positions:
			raise ValueError("The given position is not valid!")
		# we then move the given piece
		piece.position = position
		piece.has_moved = True
		self.turn = not(self.turn)
		#self.history.append(["move",(old_position, position)])
		self.history.append(BoardState("move", (old_position,position), self))

	def capture(self, capturer, captured):
		#print("capturer", capturer)
		#print("captured", captured)
		# keep track of old position
		old_position = capturer.position
		# make sure that the capturer and the captured pieces are actually on the board
		if capturer not in self.pieces:
			raise ValueError("Capturer piece not on board!")
		if captured not in self.pieces:
			raise ValueError("Captured piece not on board!")
		# make sure path is not obstructed
		occupied_positions = [p.position for p in self.pieces]
		#print("occupied positions",occupied_positions)
		path = chess_path(capturer.position, captured.position)
		#print("path",path)
		flag = (len(path) == 2) and capturer.position in path and captured.position in path
		for p in occupied_positions:
			if p in path and not flag and p != captured.position and p != capturer.position:
				#print(p)
				raise ValueError("Given path is obstructed!")
		# make sure that it is this piece's turn
		if self.turn != capturer.direction:
			raise ValueError("Not this piece's turn!")
		# make sure pieces are on opposing teams
		if capturer.direction == captured.direction:
			raise ValueError("Cannot capture a piece on the same team!")
		# check to make sure capturer can actually capture the captured piece
		captured_position = captured.position
		valid_capture_positions = capturer.get_valid_captures()
		#print("valid capture positions", valid_capture_positions)
		if captured_position not in valid_capture_positions:
			raise ValueError("Capturer piece cannot capture this piece!")
		capturer.position = captured_position
		capturer.has_moved = True
		self.turn = not(self.turn)
		self.pieces.remove(captured)
		self.scores[capturer.direction] += capturer.score
		#self.history.append(["capture", (old_position, captured.position)])
		self.history.append(BoardState("capture", (old_position, captured.position), self))
	def __repr__(self):
		# temp array to store characters
		chars = [["." for j in range(self.length)] for i in range(self.width)]
		# put corresponding characters into array
		for piece in self.pieces:
			i, j = piece.position
			chars[j][i] = piece.char
		return "\n".join(["".join(i) for i in chars])

	def get_all_moves(self):
		moves = []
		for piece in self.pieces:
			if self.turn == piece.direction:
				for move in piece.get_valid_moves():
					moves.append(("move", piece, move))
				for capture in piece.get_valid_captures():
					moves.append(("capture", piece, capture))
		return moves

	def deep_copy(self,board):
		self.length = board.length
		self.width = board.width
		self.turn = board.turn
		self.pieces = []
		for piece in board.pieces:
			self.pieces.append(copy.copy(piece))
		self.history = []
		for move in board.history:
			#print(move)
			self.history.append(move)
		self.scores = board.scores
		
	def __eq__(self, other):
		return isinstance(other, Board) and self.turn == other.turn and sorted([hash(i) for i in self.pieces]) == sorted([hash(i) for i in other.pieces])
		
# Function to create an empty board
def EmptyBoard():
	return Board(0,0,[],None)

# Valid move and valid capture functions for various chess pieces

# Kings


def king_valid_moves(position, board_size, direction, has_moved):
	x, y = position
	w, h = board_size
	return [(i, j) for i in range(w) for j in range(h) if 1<=dist((i,j),position)<=2]


def king_valid_captures(position, board_size, direction, has_moved):
	return king_valid_moves(position, board_size, direction, has_moved)

# Rooks (horizontal + vertical motion)


def rook_valid_moves(position, board_size, direction, has_moved):
	x, y = position
	w, h = board_size
	return [(i, j) for i in range(w) for j in range(h) if (i == x or j == y) and (i, j) != (x, y)]


def rook_valid_captures(position, board_size, direction, has_moved):
	return rook_valid_moves(position, board_size, direction, has_moved)

# Bishops (diagonal motion)


def bishop_valid_moves(position, board_size, direction, has_moved):
	x, y = position
	w, h = board_size
	return [(i, j) for i in range(w) for j in range(h) if ((i-x) == (j-y) or (i-x) == (y-j)) and (i, j) != (x, y)]


def bishop_valid_captures(position, board_size, direction, has_moved):
	return bishop_valid_moves(position, board_size, direction, has_moved)

# Queens (horizontal + vertical + diagonal motion)


def queen_valid_moves(position, board_size, direction, has_moved):
	x, y = position
	w, h = board_size
	return [(i, j) for i in range(w) for j in range(h) if ((i-x) == (j-y) or (i-x) == (y-j) or i == x or j == y) and (i, j) != (x, y)]


def queen_valid_captures(position, board_size, direction, has_moved):
	return queen_valid_moves(position, board_size, direction, has_moved)

# Knight (L shapes)


def knight_valid_moves(position, board_size, direction, has_moved):
	x, y = position
	w, h = board_size
	return [(i, j) for i in range(w) for j in range(h) if dist(position, (i,j)) == 5]


def knight_valid_captures(position, board_size, direction, has_moved):
	return knight_valid_moves(position, board_size, direction, has_moved)

# Limited pawns (pawns that cannot move 2 places forwad on their first move)


def limited_pawn_valid_moves(position, board_size, direction, has_moved):
	x, y = position
	w, h = board_size
	possible_moves = []
	if direction:
		possible_moves.append((x, y+1))
	else:
		possible_moves.append((x, y-1))
	return [(i, j) for (i, j) in possible_moves if 0 <= i < w and 0 <= j < h]


def limited_pawn_valid_captures(position, board_size, direction, has_moved):
	x, y = position
	w, h = board_size
	possible_moves = []
	if direction:
		possible_moves.extend([(x-1, y-1), (x+1, y-1)])
	else:
		possible_moves.extend([(x-1, y+1), (x+1, y+1)])
	return [(i, j) for (i, j) in possible_moves if 0 <= i < w and 0 <= j < h]

# Pawns


def pawn_valid_moves(position, board_size, direction, has_moved):
	x, y = position
	w, h = board_size
	possible_moves = []
	if not direction:
		possible_moves.append((x, y+1))
		if not has_moved:
			possible_moves.append((x, y+2))
	else:
		possible_moves.append((x, y-1))
		if not has_moved:
			possible_moves.append((x, y-2))
	return [(i, j) for (i, j) in possible_moves if 0 <= i < w and 0 <= j < h]


def pawn_valid_captures(position, board_size, direction, has_moved):
	return limited_pawn_valid_captures(position, board_size, direction, has_moved)

# Constructors for various pieces


def King(position, direction, board_size):
	return Piece(position, direction, "king", "K" if direction else "k", None, king_valid_moves, king_valid_captures, board_size, 0)

def Rook(position, direction, board_size):
	return Piece(position, direction, "rook", "R" if direction else "r", None, rook_valid_moves, rook_valid_captures, board_size, 5)

def Bishop(position, direction, board_size):
	return Piece(position, direction, "bishop", "B" if direction else "b", None, bishop_valid_moves, bishop_valid_captures, board_size, 3)


def Queen(position, direction, board_size):
	return Piece(position, direction, "queen", "Q" if direction else "q", None, queen_valid_moves, queen_valid_captures, board_size, 9)


def Knight(position, direction, board_size):
	return Piece(position, direction, "knight", "N" if direction else "n", None, knight_valid_moves, knight_valid_captures, board_size, 3)


def Pawn(position, direction, board_size):
	return Piece(position, direction, "pawn", "P" if direction else "p", None, pawn_valid_moves, pawn_valid_captures, board_size, 1)

# Function that takes a string and returns the board it represents
# NOTE: the first player should have pieces denoted by a capital letter
def process_board(board, turn):
	board = [list(i) for i in board.split("\n")]
	l,w = len(board), len(board[0])
	piece_types = {
		'k':King,
		'r':Rook,
		'b':Bishop,
		'q':Queen,
		'n':Knight,
		'p':Pawn
	}
	pieces = []
	for i in range(l):
		for j in range(w):
			char = board[j][i]
			if char.lower() in piece_types: pieces.append(piece_types[char.lower()]((i,j), char.isupper(), (l,w)))
	return Board(l,w,pieces,turn)
	
# function that attempts to make a move on a board
def make_move(board, pos1, pos2):
	try:
		board.move(board.get_piece(pos1),pos2)
		return board
	except Exception as e:
		try:
			board.capture(board.get_piece(pos1),board.get_piece(pos2))
			return board
		except Exception as e:
			pass
	return None
# TEST CODE
"""
board = process_board("PPP\n...\nppp", False)
print(board)
"""
"""
make_move(board,(0,2),(0,1))
print(board.get_all_moves())
print(get_best_move(board,10))
"""

'''
This file is responsible for finding best moves for the chess engine
'''


import random

pieceScore = {"K" : 0, "Q" : 9, "R" : 5, "B" : 3, "N" : 3, "P" : 1} #used to score position of a gamestate

#providing positional tables for each piece used when calculated score of a position

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
			    [1, 2, 2, 2, 2, 2, 2, 1],
			    [1, 2, 3, 3, 3, 3, 2, 1],
			    [1, 2, 3, 4, 4, 3, 2, 1],
			    [1, 2, 3, 4, 4, 3, 2, 1],
			    [1, 2, 3, 3, 3, 3, 2, 1],
			    [1, 2, 2, 2, 2, 2, 2, 1],
			    [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
			    [3, 4, 3, 2, 2, 3, 4, 3],
			    [2, 3, 4, 3, 3, 4, 3, 2],
			    [1, 2, 3, 4, 4, 3, 2, 1],
			    [1, 2, 3, 4, 4, 3, 2, 1],
			    [2, 3, 4, 3, 3, 4, 3, 2],
			    [3, 4, 3, 2, 2, 3, 4, 3],
			    [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores =  [[1, 1, 1, 3, 3, 1, 1, 1],
			    [1, 2, 3, 3, 3, 3, 2, 1],
			    [1, 3, 3, 3, 3, 3, 3, 1],
			    [3, 3, 3, 3, 3, 3, 3, 3],
			    [3, 3, 3, 3, 3, 3, 3, 3],
			    [1, 4, 3, 3, 3, 3, 4, 1],
			    [1, 2, 3, 3, 3, 3, 2, 1],
			    [1, 1, 1, 1, 1, 1, 1, 1]]

rookScores =   [[4, 4, 4, 4, 4, 4, 4, 4],
			    [4, 4, 4, 4, 4, 4, 4, 4],
			    [1, 1, 2, 3, 3, 2, 1, 1],
			    [1, 2, 3, 3, 3, 3, 2, 1],
			    [1, 2, 3, 3, 3, 3, 2, 1],
			    [1, 1, 2, 3, 3, 2, 1, 1],
			    [4, 4, 4, 4, 4, 4, 4, 4],
			    [4, 4, 4, 4, 4, 4, 4, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
				   [4, 4, 4, 4, 4, 4, 4, 4],
				   [3, 3, 3, 3, 3, 3, 3, 3],
				   [3, 3, 3, 4, 4, 3, 3, 3],
				   [1, 1, 3, 4, 4, 3, 1, 1],
				   [1, 2, 2, 3, 3, 2, 2, 1],
				   [0, 0, 0, 0, 0, 0, 0, 0],
				   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
				   [0, 0, 0, 0, 0, 0, 0, 0],
				   [1, 2, 2, 3, 3, 2, 2, 1],
				   [1, 1, 3, 4, 4, 3, 1, 1],
				   [3, 3, 3, 4, 4, 3, 3, 3],
				   [3, 3, 3, 3, 3, 3, 3, 3],
				   [4, 4, 4, 4, 4, 4, 4, 4],
				   [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores, 
					   "R":rookScores, "bP": blackPawnScores, "wP": whitePawnScores}						

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


'''
Generate a random move
'''
def findRandomMove(validMoves):
	return validMoves[random.randint(0, len(validMoves) - 1)] #inclusive

'''
Helper method to make the first recursive call when findind the best move
'''
def findBestMove(gs, validMoves, returnQueue):
	global nextMove
	nextMove = None
	random.shuffle(validMoves)
	findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
	returnQueue.put(nextMove)

'''
Negamax search approach using Alpha Beta pruning to improve runtime
'''
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
	global nextMove
	if depth == 0:
		return turnMultiplier * scoreBoard(gs)

	maxScore = -CHECKMATE
	for move in validMoves:
		gs.makeMove(move)
		nextMoves = gs.getValidMoves()
		score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier) #recursive call
		if score > maxScore:
			maxScore = score
			if depth == DEPTH:
				nextMove = move
		gs.undoMove()
		if maxScore > alpha: #pruning
			alpha = maxScore
		if alpha >= beta:
			break
	return maxScore

'''
Positive score is good for white, negative score is good for black and means black is winning
'''
def scoreBoard(gs):
	if gs.checkmate:
		if gs.whiteToMove:
			return -CHECKMATE #black wins
		else:
			return CHECKMATE #white wins
	elif gs.stalemate:
		return STALEMATE


	score = 0
	for row in range(len(gs.board)):
		for col in range(len(gs.board[row])):
			square = gs.board[row][col]
			if square != '--':
				#score it positionally
				piecePositionScore = 0
				if square[1] != 'K': #no position table for king
					if square[1] == 'P': #pawns
						piecePositionScore = piecePositionScores[square][row][col]
					else : #other pieces
						piecePositionScore = piecePositionScores[square[1]][row][col]

				if square[0] == 'w':
					score += pieceScore[square[1]] + piecePositionScore * .1
				elif square[0] == 'b':
					score -= pieceScore[square[1]] + piecePositionScore * .1

	return score










'''
This file is responsible for handling user input and displaying the current Game State info
Optimizations: Bit board, zoberish hashing (transposition tables), connect to a data base of openings, end game theory
'''

import pygame as pygame
import ChessEngine, SmartMoveFinder
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 512 
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #used in animations
IMAGES = {}

'''
Initialize a global dictionary of images of chess pieces
'''
def loadImages():
	pieces = ["bP", "bR", "bN", "bB", "bQ", "bK", "wP", "wR", "wN", "wB", "wQ", "wK"]
	for piece in pieces:
		IMAGES[piece] = pygame.transform.scale(pygame.image.load("Chess_Images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

'''
Handle user input and updating the graphics 
'''
def main():
	#Set up pygame environment 
	pygame.init()
	screen = pygame.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
	clock = pygame.time.Clock()
	screen.fill(pygame.Color("white"))
	moveLogFont = pygame.font.SysFont('Arial', 14, False, False)

	gs = ChessEngine.GameState()
	validMoves = gs.getValidMoves()
	moveMade = False #flag variable for when a move is made 
	animate = False #flag variable to determine whether to animate 

	loadImages()
	running = True
	sqSelected = () #no square is selected, keep track of the last click of the user (row, col)
	playerClicks = [] #keep track of the player clicks (two tuples: [(6, 4), (4, 4)])
	gameOver = False
	playerOne = True #if a human is playing white, then this will be true, if AI playing then false
	playerTwo = False 
	AIThinking = False 
	moveFinderProcess = None #necessary for threading/multi processing
	moveUndone = False

	while running: 
		humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				running = False
				pygame.quit()
				pygame.display.quit()
			elif e.type == pygame.MOUSEBUTTONDOWN:
				if not gameOver:
					location = pygame.mouse.get_pos() #(x, y) location of mouse 
					col = location[0] // SQ_SIZE
					row = location[1] // SQ_SIZE
					if sqSelected == (row, col)or col >= 8: #the user clicked the same square twice or user clicked mouse log
						sqSelected = () #deselect
						playerClicks = [] #clear player clicks 
					else:
						sqSelected = (row, col)
						playerClicks.append(sqSelected) #append for both 1st and 2nd click
					if len(playerClicks) == 2 and humanTurn: #after 2nd click
						move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
						for i in range(len(validMoves)):
							if move == validMoves[i]:
								gs.clicked = True
								gs.makeMove(validMoves[i])
								moveMade = True 
								animate = True
								sqSelected = () #reset user clicks
								playerClicks = []
						if not moveMade:
							playerClicks = [sqSelected]
			# key handlers
			elif e.type == pygame.KEYDOWN:
				if e.key == pygame.K_z: #undo when 'z' is pressed
					gs.undoMove()
					moveMade = True
					animate = False
					gameOver = False
					if AIThinking:
						moveFinderProcess.terminate()
						AIThinking = False
					moveUndone = True

				if e.key == pygame.K_r: #reset the board when 'r' is pressed
					gameOver = False
					gs = ChessEngine.GameState()
					validMoves = gs.getValidMoves()
					sqSelected = ()
					playerClicks = []
					moveMade = False
					animate = False
					gameOver = False
					if AIThinking:
						moveFinderProcess.terminate()
						AIThinking = False
					moveUndone = True

		#AI move finder logic
		if not gameOver and not humanTurn and not moveUndone:
			if not AIThinking:
				AIThinking = True
				returnQueue = Queue() #used to pass dat between threads
				moveFinderProcess = Process(target = SmartMoveFinder.findBestMove, args = (gs, validMoves, returnQueue))
				moveFinderProcess.start() #call findBestMove(...)
			if not moveFinderProcess.is_alive(): #do this once the thread is dead
				AIMove = returnQueue.get()
				if AIMove is None:
					AIMove = SmartMoveFinder.findRandomMove(validMoves)
				gs.makeMove(AIMove)
				moveMade = True
				animate = True
				AIThinking = False


		if moveMade:
			if animate:
				animateMove(gs.moveLog[-1], screen, gs.board, clock)
			validMoves = gs.getValidMoves()
			moveMade = False
			animate = False
			moveUndone = False

		drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

		if gs.checkmate or gs.stalemate:
			gameOver = True
			text = 'Stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
			drawEndGameText(screen, text)
			
		clock.tick(MAX_FPS)
		pygame.display.flip()
	

'''
Draw board
'''
def drawBoard(screen):
	global colors
	colors = [pygame.Color("light gray"), pygame.Color("gray")]
	for r in range(DIMENSION):
		for c in range(DIMENSION):
			color = colors[(r+c)%2]
			pygame.draw.rect(screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw current game state 
'''
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
	drawBoard(screen) #draw squares on the board
	highlightSquares(screen, gs, validMoves, sqSelected)
	drawPieces(screen, gs.board) #draw pieces on top of those squares
	drawMoveLog(screen, gs, moveLogFont)

'''
Draw highlights for legal moves
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
	if sqSelected != ():
		r, c = sqSelected
		if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved 
			#highlight selected square  
			s = pygame.Surface((SQ_SIZE, SQ_SIZE))
			s.set_alpha(100) #transparency -> 0 is transparent; 255 is opaque
			s.fill(pygame.Color('blue'))
			screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
			#highlight moves from that square
			s.fill(pygame.Color('yellow'))
			for move in validMoves:
				if move.startRow == r and move.startCol == c:
					screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))


'''
Draw pieces on the board 
'''
def drawPieces(screen, board): 
	for r in range(DIMENSION):
		for c in range(DIMENSION):
			piece = board[r][c]
			if piece != "--": #not empty square
				screen.blit(IMAGES[piece], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the move log
'''
def drawMoveLog(screen, gs, font):
	moveLogRect = pygame.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
	pygame.draw.rect(screen, pygame.Color('black'), moveLogRect)

	#add move log header
	headerFont = pygame.font.SysFont('Arial', 20, False, False)
	textObject = headerFont.render("Move Log", True, pygame.Color('white'))
	textLocation = textObject.get_rect(center=(MOVE_LOG_PANEL_WIDTH/2 + WIDTH, 15))
	screen.blit(textObject, textLocation)

	moveLog = gs.moveLog
	moveTexts =  [] #modify this later
	for i in range(0 , len(moveLog), 2):
		moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
		if i + 1 < len(moveLog): # make sure black made a move
			moveString += str(moveLog[i+1]) + "  "
		moveTexts.append(moveString)
	movesPerRow = 3
	padding = 5
	textY = padding
	lineSpacing = 2
	headerHeight = 40
	for i in range(0, len(moveTexts), movesPerRow):
		text = ""
		for j in range(movesPerRow):
			if i + j < len(moveTexts):
				text += moveTexts[i+j]
		textObject = font.render(text, True, pygame.Color('white'))
		textLocation = moveLogRect.move(padding, textY + headerHeight)
		screen.blit(textObject, textLocation)
		textY += textObject.get_height() + lineSpacing
	

'''
Draw an animation for each move
'''
def animateMove(move, screen, board, clock):
	global colors
	dR = move.endRow - move.startRow
	dC = move.endCol - move.startCol
	framesPerSquare = 10 #frames to move one square
	frameCount = (abs(dR) + abs(dC)) * framesPerSquare
	for frame in range(frameCount + 1):
		r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
		drawBoard(screen)
		drawPieces(screen, board)
		#erase piece moved from its ending square
		color = colors[(move.endRow + move.endCol) % 2]
		endSquare = pygame.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
		pygame.draw.rect(screen, color, endSquare)
		#draw the captured piece onto rectangle
		if move.pieceCaptured != '--':
			if move.isEnpassantMove:
				enpassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
				endSquare = pygame.Rect(move.endCol*SQ_SIZE, enpassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
			screen.blit(IMAGES[move.pieceCaptured], endSquare)
		#draw moving piece
		screen.blit(IMAGES[move.pieceMoved], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
		pygame.display.flip()
		clock.tick(90)



'''
Draw text at the end of the game describing the outcome
'''
def drawEndGameText(screen, text):
	font = pygame.font.SysFont('Helvitca', 32, True, False)
	textObject = font.render(text, 0, pygame.Color('Gray'))
	textLocation = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
	screen.blit(textObject, textLocation)
	textObject = font.render(text, 0, pygame.Color('Black'))
	screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
	main()
	





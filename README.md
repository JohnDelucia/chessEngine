# chessEngine

For this project, I coded the game of Chess and implemented a Chess Engine which has the ability to play around a 1000 ELO rating.
Each player is constrained to only legal chess moves. All special moves such as enpassant, castling, and pawn promotions have been implemented.

**Engine:**
For the chess engine, I have implemented a Negamax search which relies on a zero sum property: white is always trying to maximize its score while black is trying to minimize its score. I introduced Alpha Beta pruning to improve the runtime of the engine. This approach allows theh engine to disregard "bad" moves that will not be chosen by a player thus greatly reducing the number a moves the engine must consider.

**Two Player Game:** 
Allows two players to play chess against eachother.


**Player vs Engine:** 
Allows one player to play chess against a chess engine. 

**Engine vs Engine:** 
Watch as chess engine plays against itself. 

# Chess Engine

For this project, I coded the game of Chess and implemented a Chess Engine which has the ability to play around a 1000 ELO rating.

**Engine:**
For the chess engine, I have implemented a Negamax search which relies on a zero sum property: white is always trying to maximize its score while black is trying to minimize its score. I introduced Alpha Beta pruning to improve the runtime of the engine. This approach allows the engine to disregard "bad" moves that will not be chosen by a player, thus greatly reducing the number a moves the engine must consider.

**Chess Game:**
Each player is constrained to only legal chess moves. All special moves such as enpassant, castling, and pawn promotions have been implemented.
The program allows for Player vs Player, Player vs Engine, and Engine vs Engine game play. A demonstration of Player vs Engine is shown directly below. 

https://user-images.githubusercontent.com/96018567/186703858-347e3d68-e34c-425c-8215-0006b55df1e0.mov


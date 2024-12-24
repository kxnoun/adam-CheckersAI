# adam-checkersAI

this repo contains a python program designed to solve checkers endgame puzzles using minimax and alpha-beta pruning. the objective is to ensure the red player wins in the fewest moves possible while the black player attempts to prolong the game.

here, checkers is two-player played on an 8x8 grid (we use english draughts rules).

key features
- **alpha-beta pruning**: to reduce number of nodes explored
- **depth-limited search**: to balance performance and computation time (greater the depth, the more states we search, but takes longer)
- -**node ordering**: ordered my successors by eval function to try and speed up alpha-beta pruning.
- **evaluation function**: estimates utility of non-terminal states.

## running
use command line inputs like the following:
```bash
python3 checkers.py --inputfile <input file> --outputfile <output file>

under Scripts/, there are two scripts, use checkers.py.
there are two examples under Examples/, you can make your own examples too!

that's 

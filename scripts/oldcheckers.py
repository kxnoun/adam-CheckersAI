import sys
import time
import argparse

class CState:
    def __init__(self, board) -> None:
        self.board = board

    def __repr__(self) -> str:
        return '\n'.join(self.board)
    
    def get_p(self, row, col):
        return self.board[row][col]
    
    def set_p(self, row, col, piece):
        self.board[row] = self.board[row][:col] + piece + self.board[row][(col + 1):]
    
    def gen_successor(self, player):
        successors = []
        mandatory_jumps = []

        for i in range(8):
            for j in range(8):
                if self.get_p(i, j).lower() == player:
                    jumps = gen_jump(self, i, j, player)
                    if jumps:
                        mandatory_jumps.extend(jumps)
                    else:
                        successors.extend(gen_move(self, i, j, player))
        if mandatory_jumps:
            return mandatory_jumps
        return successors

def gen_move(state: CState, row: int, col: int, player: str):
    if state.get_p(row, col).isupper():
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    elif player == 'r':
        directions = [(-1, -1), (-1, 1)]
    elif player == 'b':
        directions = [(1, -1), (1, 1)]
    
    moves = []
    for d_row, d_col in directions:
        new_row, new_col = row + d_row, col + d_col
        if is_valid_bounds(new_row, new_col) and state.get_p(new_row, new_col) == '.':
            new_state = CState([r[:] for r in state.board])
            new_state.set_p(row, col, '.')
            piece = state.get_p(row, col)
            if (player == 'r' and new_row == 0) or (player == 'b' and new_row == 7):
                piece = piece.upper()
            new_state.set_p(new_row, new_col, piece)
            moves.append(new_state)
    return moves

def gen_jump(state: CState, row: int, col: int, player: str):
    if state.get_p(row, col).isupper():
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    elif player == 'r':
        directions = [(-1, -1), (-1, 1)]
    elif player == 'b':
        directions = [(1, -1), (1, 1)]
    
    jumps = []
    for d_row, d_col in directions:
        new_row, new_col = row + d_row, col + d_col
        jump_row, jump_col = row + (2 * d_row), col + (2 * d_col)
        if (is_valid_bounds(new_row, new_col) and is_valid_bounds(jump_row, jump_col) and
            state.get_p(new_row, new_col).lower() == get_opponent(player) and
            state.get_p(jump_row, jump_col) == '.'):
            new_state = CState([r[:] for r in state.board])
            new_state.set_p(row, col, '.')
            new_state.set_p(new_row, new_col, '.')
            piece = state.get_p(row, col)
            if (player == 'r' and jump_row == 0) or (player == 'b' and jump_row == 7):
                piece = piece.upper()
            new_state.set_p(jump_row, jump_col, piece)
            jumps.append(new_state)
            subsequent_jumps = gen_jump(new_state, jump_row, jump_col, player)
            
            if subsequent_jumps:
                for jump in subsequent_jumps:
                    jumps.append(jump)
            else:
                jumps.append(new_state)

    return jumps

def is_valid_bounds(row, col):
    return 0 <= row < 8 and 0 <= col < 8
    
def get_opponent(player):
    if player == 'b':
        opp = 'r'
    else:
        opp = 'b'
    return opp

def player_win(state, player):
    opp = get_opponent(player)
    for row in state.board:
        if opp in row or opp.upper() in row:
            return False
    return True
    
def evaluate(state, player):
    score = 0

    # weights
    piece_w = 1
    king_w= 3
    center_w = 0.5
    advance_w = 0.5
    safety_w = 1
    kingpot_w = 2

    opp = get_opponent(player)
    for i, row in enumerate(state.board):
        for j, piece in enumerate(row):
            if piece.lower() == player:
                score += piece_w

                if piece.isupper():
                    score += king_w

                if 2 <= i <= 5 and 2 <= j <= 5:
                    score += center_w
                
                if (player == 'r' and i < 3) or (player == 'b' and i > 4):
                    score += advance_w
                
                if j == 0 or j == 7:
                    score += safety_w

                if (player == 'r' and i == 1) or (player == 'b' and i == 6):
                    score += kingpot_w
            
            elif piece.lower() == opp:
                score -= piece_w
                
                if piece.isupper():
                    score -= king_w
                
                if 2 <= i <= 5 and 2 <= j <= 5:
                    score -= center_w
                
                if (opp == 'r' and i < 3) or (opp == 'b' and i > 4):
                    score -= advance_w
                
                if j == 0 or j == 7:
                    score -= safety_w

                if (opp == 'r' and i == 1) or (opp == 'b' and i == 6):
                    score -= kingpot_w
    
    if player == 'r':
        return score
    return -score

def cutoff_test(state: CState, depth, max_depth):
    return depth >= max_depth or is_terminal(state)

def max_value(state: CState, alpha, beta, depth, max_depth):
    if cutoff_test(state, depth, max_depth):
        return evaluate(state, 'r')
    v = -float('inf')
    for successor in state.gen_successor('r'):
        v = max(v, min_value(successor, alpha, beta, depth + 1, max_depth))
        if v >= beta:
            return v
        alpha = max(alpha, v)
    return v

def min_value(state: CState, alpha, beta, depth, max_depth):
    if cutoff_test(state, depth, max_depth):
        return evaluate(state, 'b')
    v = float('inf')
    for successor in state.gen_successor('b'):
        v = min(v, max_value(successor, alpha, beta, depth + 1, max_depth))
        if v <= alpha:
            return v
        beta = min(beta, v)
    return v

def alpha_beta_search(state: CState, depth, max_depth, maximizing_player):
    best_value = -float('inf') if maximizing_player else float('inf')
    best_state = None

    for successor in state.gen_successor('r' if maximizing_player else 'b'):
        if maximizing_player:
            value = min_value(successor, -float('inf'), float('inf'), depth + 1, max_depth)
            if value > best_value:
                best_value = value
                best_state = successor
        else:
            value = max_value(successor, -float('inf'), float('inf'), depth + 1, max_depth)
            if value < best_value:
                best_value = value
                best_state = successor

    return best_state, best_value

def is_terminal(state):
    return player_win(state, 'r') or player_win(state, 'b')

def play(init_state, max_depth):
    curr_state = init_state
    states = [curr_state]
    turn = 'r'
    depth = 0

    while not is_terminal(curr_state):
        if turn == 'r':
            best_move, _ = alpha_beta_search(curr_state, depth, max_depth, True)
            turn = 'b'
        else:
            best_move, _ = alpha_beta_search(curr_state, depth, max_depth, False)
            turn = 'r'
        curr_state = best_move
        states.append(curr_state)

    return states

def read_from_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    board = [line.strip() for line in lines]
    return board

def write_output(file, states):
    with open(file, 'w') as f:
        for state in states:
            for row in state.board:
                f.write(row + '\n')
            f.write('\n')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="input."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="solution"
    )
    args = parser.parse_args()

    initial_board = read_from_file(args.inputfile)
    init_state = CState(initial_board)
    x = time.time()
    final_states = play(init_state, 10)
    print(f"Time: {time.time() - x} seconds")
    write_output(args.outputfile, final_states)
    print(f"{len(final_states) - 1} moves")
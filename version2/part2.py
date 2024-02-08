import copy
import sys
import cProfile
import pstats


class Agent:
    def __init__(self, tiles, maximizing, path, forbidden, prev, moves):
        self.tiles = tiles
        self.maximizing = maximizing
        self.path = path
        self.prev_move = prev
        self.forbidden = forbidden
        self.lose = False
        self.moves = moves

    def is_prev(self, move):
        tile, direction = move
        val, (row, col) = tile
        if direction == 'u':
            row -= 1
        elif direction == 'r':
            col += 1
        elif direction == 'd':
            row += 1
        elif direction == 'l':
            col -= 1
        return (val, (row, col)) == self.prev_move

    def check_forbidden(self):
        for tile in self.forbidden.keys():
            if tile in self.tiles:
                self.forbidden[tile] += 1
                if self.forbidden[tile] > 2:
                    self.lose = True
            else:
                self.forbidden[tile] = 0

    def get_copy(self):
        return Agent(set(self.tiles), self.maximizing, self.path,
                     dict(self.forbidden), copy.copy(self.prev_move), self.moves)


num_expanded = 0
agent1_max_moves = 0
agent2_max_moves = 0


class State:
    def __init__(self, board, agent1, agent2, cost, turn):
        self.board = board
        self.agent1 = agent1
        self.agent2 = agent2
        self.cost = cost
        self.turn = turn

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))

    def copy_board(self):
        return [list(row) for row in self.board]

    def is_over(self):
        if self.agent1.lose:
            return -1
        if self.agent2.lose:
            return 1

        board = self.board

        if (board[0][0] == "1" and board[0][1] == "2") or (board[0][1] == "1" and board[0][0] == "2"):
            return 1
        if (board[2][1] == "8" and board[2][2] == "9") or (board[2][2] == "8" and board[2][1] == "9"):
            return -1

        return 0

    def move(self, move):
        tile, direction = move
        val, (row, col) = tile

        if self.turn:
            agent = self.agent1
        else:
            agent = self.agent2

        n_row, n_col = row, col
        if direction == 'u':
            n_row += -1
            agent.path += f"{tile}->U, "
        elif direction == 'r':
            n_col += 1
            agent.path += f"{tile}->R, "
        elif direction == 'd':
            n_row += 1
            agent.path += f"{tile}->D, "
        elif direction == 'l':
            n_col += -1
            agent.path += f"{tile}->L, "

        agent.prev_move = tile
        agent.tiles.remove(tile)
        agent.tiles.add((val, (n_row, n_col)))
        agent.check_forbidden()
        agent.moves += 1

        self.turn = not self.turn
        self.board[row][col] = '0'
        self.board[n_row][n_col] = str(val)

    def available_moves(self, agent):
        moves = []
        sorted_list = sorted(agent.tiles, key=lambda t: t[0])
        for tile in sorted_list:
            val, (row, col) = tile
            if row != 0 and self.board[row - 1][col] == '0':
                moves.append((tile, 'u'))
            if col != 2 and self.board[row][col + 1] == '0':
                moves.append((tile, 'r'))
            if row != 2 and self.board[row + 1][col] == '0':
                moves.append((tile, 'd'))
            if col != 0 and self.board[row][col - 1] == '0':
                moves.append((tile, 'l'))
        return moves

    def copy_agent(self, num):
        if num == 1:
            return self.agent1.get_copy()
        else:
            return self.agent2.get_copy()

    def expand(self):
        global num_expanded
        if self.turn:
            agent = self.agent1
        else:
            agent = self.agent2

        next_states = []
        for move in self.available_moves(agent):
            if agent.is_prev(move):
                num_expanded += 1
                continue

            agent1 = self.copy_agent(1)
            agent2 = self.copy_agent(2)
            state = State(self.copy_board(), agent1, agent2, self.cost + 1, self.turn)
            state.move(move)
            next_states.append(state)
        num_expanded += len(next_states)
        return next_states


def setup(turn, file_path):
    board = []

    with open(file_path, 'r') as file:
        read_file_array = file.read().splitlines()
        for i in range(len(read_file_array)):
            row_array = read_file_array[i].split()
            board.append(row_array)

    tiles1_2 = set()
    tiles8_9 = set()
    forbidden1 = {(1, (2, 1)): 0, (1, (2, 2)): 0, (2, (2, 1)): 0, (2, (2, 2)): 0}
    forbidden2 = {(8, (0, 0)): 0, (8, (0, 1)): 0, (9, (0, 0)): 0, (9, (0, 1)): 0}

    for i in range(3):
        for j in range(3):
            if board[i][j] == '1':
                tiles1_2.add((1, (i, j)))
            elif board[i][j] == '2':
                tiles1_2.add((2, (i, j)))
            elif board[i][j] == '8':
                tiles8_9.add((8, (i, j)))
            elif board[i][j] == '9':
                tiles8_9.add((9, (i, j)))

    agent1 = Agent(tiles1_2, True, "", forbidden1, (0, (0, 0)), 0)
    agent2 = Agent(tiles8_9, False, "", forbidden2, (0, (0, 0)), 0)

    return State(board, agent1, agent2, 0, turn)


def minimax(state, depth, alpha, beta):
    global agent1_max_moves
    global agent2_max_moves
    is_over = state.is_over()

    total_moves = state.agent1.moves + state.agent2.moves

    if depth == 0 or is_over != 0:
        return is_over

    next_st = state.expand()

    if state.turn:
        max_eval = float('-inf')
        for st in next_st:
            evaluation = minimax(st, depth - 1, alpha, beta)
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        if max_eval == -1:
            agent2_max_moves = max(total_moves, agent2_max_moves)
        return max_eval

    else:
        min_eval = float('inf')
        for st in next_st:
            evaluation = minimax(st, depth - 1, alpha, beta)
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        if min_eval == 1:
            agent1_max_moves = max(total_moves, agent1_max_moves)
        return min_eval


def write_output(utility, expanded_nodes, max_moves, output_path):
    with open(output_path, "w") as output_file:
        output_file.write(f"{utility}\n")
        output_file.write(f"{expanded_nodes}\n")


def main():
    start_agent = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]

    turn = True
    if start_agent == "2":
        turn = False

    initial_state = setup(turn, input_path)
    utility = minimax(initial_state, 10, float('-inf'), float('inf'))

    if utility == 1:
        max_moves = agent1_max_moves
    elif utility == -1:
        max_moves = agent2_max_moves
    else:
        max_moves = 0

    if not turn:
        utility *= -1

    write_output(utility, num_expanded, max_moves, output_path)


if __name__ == "__main__":
    with cProfile.Profile() as profile:
        main()
    results = pstats.Stats(profile)
    results.sort_stats(pstats.SortKey.TIME)
    results.print_stats()

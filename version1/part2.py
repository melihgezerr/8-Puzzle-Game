import cProfile
import pstats
import sys
from heapq import *



class State:
    def __init__(self, board, tiles, cost, path, manhattan):
        self.board = board
        self.tiles = tiles
        self.cost = cost
        self.path = path
        self.manhattan = manhattan

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))

    def available_moves(self):
        moves = []
        for tile in self.tiles:
            row, col = tile
            if row != 0 and (row - 1, col) not in self.tiles:
                moves.append((tile, 'u'))
            if col != 2 and (row, col + 1) not in self.tiles:
                moves.append((tile, 'r'))
            if row != 2 and (row + 1, col) not in self.tiles:
                moves.append((tile, 'd'))
            if col != 0 and (row, col - 1) not in self.tiles:
                moves.append((tile, 'l'))
        return moves

    def move(self, move):
        tile, direction = move
        shift_x, shift_y = 0, 0
        if direction == 'u':
            shift_x = -1
            self.path += f"{tile}->U, "
        elif direction == 'r':
            shift_y = 1
            self.path += f"{tile}->R, "
        elif direction == 'd':
            shift_x = 1
            self.path += f"{tile}->D, "
        elif direction == 'l':
            shift_y = -1
            self.path += f"{tile}->L, "

        self.tiles.remove(tile)
        tile_x, tile_y = tile[0], tile[1]
        new_x, new_y = tile_x + shift_x, tile_y + shift_y

        goal_row, goal_col = divmod(int(self.board[new_x][new_y]) - 1, 3)

        if abs(goal_row - tile_x) > abs(goal_row - new_x):
            self.manhattan += 1
        elif abs(goal_row - tile_x) < abs(goal_row - new_x):
            self.manhattan -= 1
        elif abs(goal_col - tile_y) > abs(goal_col - new_y):
            self.manhattan += 1
        elif abs(goal_col - tile_y) < abs(goal_col - new_y):
            self.manhattan -= 1

        self.board[tile_x][tile_y], self.board[new_x][new_y] = (
            self.board[new_x][new_y],
            '0',
        )
        self.tiles.add((new_x, new_y))

    def is_goal(self):
        return self.board == [['1', '2', '3'], ['4', '5', '6'], ['0', '0', '0']]

    def copy_board(self):
        return [list(row) for row in self.board]

    def expand(self):
        next_states = []
        for move in self.available_moves():
            new_state = State(self.copy_board(), self.tiles.copy(), self.cost + 1, self.path, self.manhattan)
            new_state.move(move)
            next_states.append(new_state)
        return next_states

def setup(file_path):
    board = []
    tiles = set()
    with open(file_path, 'r') as file:
        read_file_array = file.read().splitlines()
        board.clear()

        for i in range(len(read_file_array)):
            row_array = read_file_array[i].split()
            board.append(row_array)

    for i in range(3):
        for j in range(3):
            if board[i][j] == '0':
                tiles.add((i, j))

    return State(board, tiles, 0, "", calc_manhattan(board))


class astar_queue:
    def __init__(self):
        self.ucs_counter = 0
        self.heap = []

    def put(self, state):
        self.ucs_counter += 1
        heappush(self.heap, (state.manhattan + state.cost + (linear_conflicts(state.board) * 2), self.ucs_counter, state))

    def pop(self):
        return heappop(self.heap)[2]

def astar(initial_state, output_path):
    visited = set()
    queue = astar_queue()
    queue.put(initial_state)
    expanded_nodes = 0

    while len(queue.heap) > 0:

        state = queue.pop()

        if state in visited:
            continue
        visited.add(state)

        if state.is_goal():
            write_output(state, expanded_nodes, output_path)
            break

        next_states = state.expand()
        expanded_nodes += 1
        for state in next_states:
            queue.put(state)


def calc_manhattan(board):
    distance = 0
    for row in range(3):
        for col in range(3):
            if board[row][col] != '0':
                goal_row, goal_col = divmod(int(board[row][col]) - 1, 3)
                distance += abs(goal_row - row) + abs(goal_col - col)
    return distance

def linear_conflicts(board):
    conflicts = 0
    for row in range(3):
        for col in range(3):
            number = int(board[row][col])
            if number != 0:
                goal_row, goal_col = divmod(number - 1, 3)
                if row == goal_row:
                    for c in range(col + 1, 3):
                        other = int(board[row][c])
                        if other != 0 and (other - 1) // 3 == row and other < number:
                            conflicts += 1
                if col == goal_col:
                    for r in range(row + 1, 3):
                        other = int(board[r][col])
                        if other != 0 and (other - 1) % 3 == col and other < number:
                            conflicts += 1

    return conflicts

def write_output(state, expanded_nodes, output_path):
    with open(output_path, "a") as output_file:
        output_file.write(f"Expanded Nodes: {expanded_nodes}\n")
        output_file.write(f"Cost: {state.cost}\n")
        output_file.write("Here paths are written as '<index>->direction'. The <index> element gives the row and column of which empty tile is moving.\n")
        output_file.write(f"Path: {state.path}\n\n")
def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    initial_state = setup(input_path)
    open(output_path, "w").close()

    astar(initial_state, output_path)


if __name__ == "__main__":
    with cProfile.Profile() as profile:
        main()
    results = pstats.Stats(profile)
    results.sort_stats(pstats.SortKey.TIME)
    results.print_stats()

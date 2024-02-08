import cProfile
import pstats
import sys
from collections import deque
from heapq import *


class State:
    def __init__(self, board, tile, cost, path, manhattan):
        self.board = board
        self.tile = tile
        self.cost = cost
        self.path = path
        self.direction = 1
        self.manhattan = manhattan

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))

    def available_moves(self):
        tile = self.tile
        moves = []
        if tile[0] != 0:
            moves.append('u')
        if tile[1] != 2:
            moves.append('r')
        if tile[0] != 2:
            moves.append('d')
        if tile[1] != 0:
            moves.append('l')
        return moves

    def move(self, direction):
        shift_x, shift_y = 0, 0
        if direction == 'u':
            shift_x = -1
            self.path += "U "
            self.direction = 1
        elif direction == 'r':
            shift_y = 1
            self.path += "R "
            self.direction = 2
        elif direction == 'd':
            shift_x = 1
            self.path += "D "
            self.direction = 3
        elif direction == 'l':
            shift_y = -1
            self.path += "L "
            self.direction = 4

        tile_x, tile_y = self.tile[0], self.tile[1]
        new_x, new_y = tile_x + shift_x, tile_y + shift_y

        if self.manhattan != None:
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
        self.tile = (new_x, new_y)

    def is_goal(self):
        return self.board == [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '0']]

    def copy_board(self):
        return [list(row) for row in self.board]

    def expand(self):
        next_states = []
        for direction in self.available_moves():
            new_state = State(self.copy_board(), self.tile, self.cost + 1, self.path, self.manhattan)
            new_state.move(direction)
            next_states.append(new_state)
        return next_states


class ucs_queue:
    def __init__(self):
        self.ucs_counter = 0
        self.heap = []

    def put(self, state):
        self.ucs_counter += 1
        heappush(self.heap, (state.cost, state.direction, self.ucs_counter, state))

    def pop(self):
        return heappop(self.heap)[3]
class greedy_queue:
    def __init__(self):
        self.ucs_counter = 0
        self.heap = []

    def put(self, state):
        self.ucs_counter += 1
        heappush(self.heap, (state.manhattan, state.direction, self.ucs_counter, state))


    def pop(self):
        return heappop(self.heap)[3]
class astar_queue:
    def __init__(self):
        self.ucs_counter = 0
        self.heap = []

    def put(self, state):
        self.ucs_counter += 1
        heappush(self.heap, (state.manhattan + state.cost, state.direction, self.ucs_counter, state))


    def pop(self):
        return heappop(self.heap)[3]


def bfs(initial_state, output_path):
    visited = set()
    queue = deque()
    queue.append(initial_state)
    expanded_nodes = 0

    while len(queue) > 0:

        state = queue.popleft()

        if state in visited:
            continue
        visited.add(state)

        if state.is_goal():
            write_output(state, expanded_nodes, output_path)
            break

        next_states = state.expand()
        expanded_nodes += 1
        for state in next_states:
            queue.append(state)
def dfs(initial_state, output_path):
    visited = set()
    stack = deque()
    stack.append(initial_state)
    expanded_nodes = 0

    while True:
        state = stack.pop()
        if state in visited:
            continue
        visited.add(state)

        if state.is_goal():
            write_output(state, expanded_nodes, output_path)
            break

        next_states = state.expand()
        expanded_nodes += 1
        for state in next_states[::-1]:
            stack.append(state)
def ucs(initial_state, output_path):
    visited = set()
    queue = ucs_queue()
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
def greedy(initial_state, output_path):
    visited = set()
    queue = greedy_queue()
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
def write_output(state, expanded_nodes, output_path):
    with open(output_path, "a") as output_file:
        output_file.write(f"{expanded_nodes}\n")
        output_file.write(f"{state.cost}\n")
        output_file.write(f"{state.path}\n")
def setup(file_path):
    board = []
    tile = tuple()
    with open(file_path, 'r') as file:
        read_file_array = file.read().splitlines()
        board.clear()

        for i in range(len(read_file_array)):
            row_array = read_file_array[i].split()
            board.append(row_array)

    for i in range(3):
        for j in range(3):
            if board[i][j] == '0':
                tile = (i, j)

    return State(board, tile, 0, "", calc_manhattan(board))

def main():

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    initial_state = setup(input_path)
    open(output_path, "w").close()

    bfs(initial_state, output_path)
    dfs(initial_state, output_path)
    ucs(initial_state, output_path)
    greedy(initial_state, output_path)
    astar(initial_state, output_path)

if __name__ == "__main__":
    with cProfile.Profile() as profile:
        main()
    results = pstats.Stats(profile)
    results.sort_stats(pstats.SortKey.TIME)
    results.print_stats()

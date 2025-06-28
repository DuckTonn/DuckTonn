import heapq
from copy import deepcopy

class RushHourGame:
    def __init__(self, board, vehicles, unit_cost=1):
        """
        Initialize the Rush Hour game with unit cost.
        
        Args:
            board: 2D list representing the initial board state
            vehicles: Dictionary of vehicles with their positions and orientations
            unit_cost: Cost per unit length of vehicle (default: 1)
        """
        self.board = board
        self.vehicles = vehicles
        self.size = len(board)
        self.exit_row = self.size // 2  # Typically the middle row for Rush Hour
        self.exit_col = self.size - 1   # Rightmost column
        self.unit_cost = unit_cost
    
    def is_goal(self, state):
        """Check if the red car (usually 'X') is at the exit position."""
        for vehicle, info in state['vehicles'].items():
            if vehicle == 'X':
                for row, col in info['positions']:
                    if info['orientation'] == 'horizontal' and col == self.exit_col:
                        return True
        return False
    
    def get_successors(self, state):
        """Generate all possible successor states with cost = length * unit_cost."""
        successors = []
        board = state['board']
        vehicles = state['vehicles']
        
        for vehicle, info in vehicles.items():
            positions = info['positions']
            orientation = info['orientation']
            length = len(positions)
            move_cost = length * self.unit_cost  # Cost = length × unit_cost
            
            if orientation == 'horizontal':
                # Try moving left
                left_pos = positions[0]
                new_col = left_pos[1] - 1
                if new_col >= 0 and board[left_pos[0]][new_col] == '.':
                    new_positions = [(pos[0], pos[1]-1) for pos in positions]
                    if self.is_valid_move(board, positions, new_positions):
                        new_state = self.create_new_state(state, vehicle, new_positions)
                        successors.append((new_state, move_cost))
                
                # Try moving right
                right_pos = positions[-1]
                new_col = right_pos[1] + 1
                if new_col < self.size and board[right_pos[0]][new_col] == '.':
                    new_positions = [(pos[0], pos[1]+1) for pos in positions]
                    if self.is_valid_move(board, positions, new_positions):
                        new_state = self.create_new_state(state, vehicle, new_positions)
                        successors.append((new_state, move_cost))
            
            elif orientation == 'vertical':
                # Try moving up
                top_pos = positions[0]
                new_row = top_pos[0] - 1
                if new_row >= 0 and board[new_row][top_pos[1]] == '.':
                    new_positions = [(pos[0]-1, pos[1]) for pos in positions]
                    if self.is_valid_move(board, positions, new_positions):
                        new_state = self.create_new_state(state, vehicle, new_positions)
                        successors.append((new_state, move_cost))
                
                # Try moving down
                bottom_pos = positions[-1]
                new_row = bottom_pos[0] + 1
                if new_row < self.size and board[new_row][bottom_pos[1]] == '.':
                    new_positions = [(pos[0]+1, pos[1]) for pos in positions]
                    if self.is_valid_move(board, positions, new_positions):
                        new_state = self.create_new_state(state, vehicle, new_positions)
                        successors.append((new_state, move_cost))
        
        return successors
    
    def is_valid_move(self, board, old_positions, new_positions):
        """Check if all new positions are empty or part of the moving vehicle."""
        for (r, c) in new_positions:
            if board[r][c] != '.' and (r, c) not in old_positions:
                return False
        return True
    
    def create_new_state(self, old_state, moved_vehicle, new_positions):
        """Create a new game state after moving a vehicle."""
        new_state = deepcopy(old_state)
        new_board = new_state['board']
        vehicles = new_state['vehicles']
        
        # Clear old positions
        for r, c in vehicles[moved_vehicle]['positions']:
            new_board[r][c] = '.'
        
        # Set new positions
        vehicle_char = moved_vehicle
        for r, c in new_positions:
            new_board[r][c] = vehicle_char
        
        # Update vehicle info
        vehicles[moved_vehicle]['positions'] = new_positions
        
        return new_state

def uniform_cost_search(game):
    initial_state = {
        'board': deepcopy(game.board),
        'vehicles': deepcopy(game.vehicles)
    }
    
    def get_state_hash(state):
        vehicles_tuple = tuple(
            (v, tuple(info['positions']), info['orientation'])
            for v, info in sorted(state['vehicles'].items())
        )
        board_tuple = tuple(tuple(row) for row in state['board'])
        return (board_tuple, vehicles_tuple)
    state_hash = get_state_hash(initial_state)
    
    state_repository = {state_hash: initial_state}
    
    frontier = []
    heapq.heappush(frontier, (0, state_hash, []))
    
    explored = set()

    while frontier:
        total_cost, current_hash, path = heapq.heappop(frontier)
        current_state = state_repository[current_hash]

        if current_hash in explored:
            continue
        explored.add(current_hash)

        if game.is_goal(current_state):
            return path, total_cost

        for successor, cost in game.get_successors(current_state):
            successor_hash = get_state_hash(successor)
            
            if successor_hash not in explored:
                new_cost = total_cost + cost
                
                # Tìm xe di chuyển
                moved_vehicle = None
                for vehicle in current_state['vehicles']:
                    if current_state['vehicles'][vehicle]['positions'] != successor['vehicles'][vehicle]['positions']:
                        moved_vehicle = vehicle
                        break
                
                # Xác định hướng di chuyển
                direction = ""
                if moved_vehicle:
                    old_pos = current_state['vehicles'][moved_vehicle]['positions'][0]
                    new_pos = successor['vehicles'][moved_vehicle]['positions'][0]
                    if current_state['vehicles'][moved_vehicle]['orientation'] == 'horizontal':
                        direction = "right" if new_pos[1] > old_pos[1] else "left"
                    else:
                        direction = "down" if new_pos[0] > old_pos[0] else "up"
                
                # Lưu state mới vào repository
                state_repository[successor_hash] = successor
                
                # Thêm vào frontier
                new_path = path + [(moved_vehicle, direction, new_cost)]
                heapq.heappush(frontier, (new_cost, successor_hash, new_path))
    
    return None, float('inf')
# Example usage
if __name__ == "__main__":
    # Example Rush Hour board (6x6)
    board = [
        ['.', '.', '.', '.', '.', '.'],
        ['.', '.', 'B', '.', 'C', '.'],
        ['A', 'A', 'X', 'X', 'C', '.'],
        ['.', '.', 'B', '.', 'C', '.'],
        ['.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.']
    ]

    vehicles = {
        'X': {'positions': [(2, 2), (2, 3)], 'orientation': 'horizontal'},
        'A': {'positions': [(2, 0), (2, 1)], 'orientation': 'horizontal'},
        'B': {'positions': [(1, 2), (3, 2)], 'orientation': 'vertical'},
        'C': {'positions': [(2, 4), (3, 4), (4, 4)], 'orientation': 'vertical'}
    }
    unit_cost = 1
    game = RushHourGame(board, vehicles, unit_cost)
    solution_path, total_cost = uniform_cost_search(game)
    
    if solution_path:
        print(f"Solution found with total cost {total_cost}!")
        for i, (vehicle, direction, cost) in enumerate(solution_path, 1):
            print(f"Step {i}: Move {vehicle} {direction} (cost: {cost})")
    else:
        print("No solution found.")

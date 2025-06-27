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
                row, col = info['positions'][0]
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
    """Perform Uniform Cost Search with cost = length × unit_cost."""
    initial_state = {
        'board': deepcopy(game.board),
        'vehicles': deepcopy(game.vehicles)
    }
    
    # Priority queue: (total_cost, state, path)
    frontier = []
    heapq.heappush(frontier, (0, initial_state, []))
    
    explored = set()
    
    while frontier:
        total_cost, current_state, path = heapq.heappop(frontier)
        
        # Check if current state is the goal
        if game.is_goal(current_state):
            return path, total_cost
        
        # Skip if already explored
        state_hash = str(current_state['board'])
        if state_hash in explored:
            continue
            
        explored.add(state_hash)
        
        # Generate successors
        for successor, cost in game.get_successors(current_state):
            successor_hash = str(successor['board'])
            if successor_hash not in explored:
                new_cost = total_cost + cost
                new_path = path + [(successor['vehicles']['X']['positions'], new_cost)]
                heapq.heappush(frontier, (new_cost, successor, new_path))
    
    return None, float('inf')  # No solution found

# Example usage
if __name__ == "__main__":
    # Example Rush Hour board (6x6)
    board = [
        ['.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.'],
        ['A', 'A', 'X', 'X', 'B', '.'],
        ['.', '.', 'C', 'D', 'B', '.'],
        ['.', '.', 'C', 'D', 'E', 'E'],
        ['.', '.', 'F', 'F', 'F', '.']
    ]
    
    vehicles = {
        'X': {'positions': [(2, 2), (2, 3)], 'orientation': 'horizontal'},  # length=2
        'A': {'positions': [(2, 0), (2, 1)], 'orientation': 'horizontal'},  # length=2
        'B': {'positions': [(2, 4), (3, 4)], 'orientation': 'vertical'},    # length=2
        'C': {'positions': [(3, 2), (4, 2)], 'orientation': 'vertical'},    # length=2
        'D': {'positions': [(3, 3), (4, 3)], 'orientation': 'vertical'},    # length=2
        'E': {'positions': [(4, 4), (4, 5)], 'orientation': 'horizontal'},  # length=2
        'F': {'positions': [(5, 2), (5, 3), (5, 4)], 'orientation': 'horizontal'}  # length=3
    }
    
    unit_cost = 1  # Cost per unit length
    game = RushHourGame(board, vehicles, unit_cost)
    solution_path, total_cost = uniform_cost_search(game)
    
    if solution_path:
        print(f"Solution found with total cost {total_cost}!")
        for i, (positions, cost) in enumerate(solution_path, 1):
            # Find which vehicle moved by comparing with previous state
            if i == 1:
                moved_vehicle = 'X'  # Assuming first move is by the red car
            else:
                # Compare positions to find which vehicle moved
                prev_positions = solution_path[i-2][0]
                for vehicle, info in game.vehicles.items():
                    if info['positions'] != positions and len(info['positions']) == len(positions):
                        moved_vehicle = vehicle
                        break
            
            print(f"Move {i}: {moved_vehicle} to {positions} (cost: {cost})")
    else:
        print("No solution found.")
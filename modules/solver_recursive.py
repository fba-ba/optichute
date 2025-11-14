import logging
from modules.pattern_generator import PatternGenerator


class RecursiveSolver:
    """Solves the cutting stock problem using recursive backtracking."""
    
    def __init__(self, stock, required, config):
        """
        Initialize the solver.
        
        Args:
            stock: List of available stock pieces
            required: List of required pieces to cut
            config: Configuration dictionary
        """
        self.stock = stock
        self.required = required
        self.config = config
        self.kerf_mm = config.get('kerf_mm', 0)
        self.kerf_m = self.kerf_mm / 1000.0
        self.top_n = config.get('top_n_solutions', 10)
        self.logger = logging.getLogger(__name__)
        
        # Expand stock and required based on quantities
        self.stock_expanded = self._expand_stock()
        self.required_expanded = self._expand_required()
        
        # Solution storage
        self.solutions = []
    
    def _expand_stock(self):
        """Expand stock list based on quantities."""
        expanded = []
        for piece in self.stock:
            for i in range(piece.get('quantity', 1)):
                expanded.append({
                    'id': f"{piece.get('id', 'S')}-{i+1}",
                    'original_id': piece.get('id', 'S'),
                    'length_m': piece['length_m']
                })
        return expanded
    
    def _expand_required(self):
        """Expand required list based on quantities."""
        expanded = []
        for piece in self.required:
            for i in range(piece.get('quantity', 1)):
                expanded.append({
                    'id': f"{piece.get('id', 'P')}-{i+1}",
                    'original_id': piece.get('id', 'P'),
                    'length_m': piece['length_m']
                })
        return expanded
    
    def solve(self):
        """
        Solve the cutting optimization problem.
        
        Returns:
            List of top N solutions
        """
        self.logger.info(f"Stock pieces: {len(self.stock_expanded)}")
        self.logger.info(f"Required pieces: {len(self.required_expanded)}")
        
        # Start recursive search
        current_solution = []
        remaining_required = list(range(len(self.required_expanded)))
        
        self._recursive_search(current_solution, remaining_required, 0)
        
        # Sort solutions by score
        self.solutions.sort(key=self._solution_score, reverse=True)
        
        # Return top N
        return self.solutions[:self.top_n]
    
    def _recursive_search(self, current_solution, remaining_required, stock_idx):
        """
        Recursive search for solutions.
        
        Args:
            current_solution: Current cutting plan (list of cuts per stock)
            remaining_required: Indices of remaining required pieces
            stock_idx: Current stock piece index
        """
        # Base case: no more required pieces
        if not remaining_required:
            self._add_solution(current_solution)
            return
        
        # Base case: no more stock
        if stock_idx >= len(self.stock_expanded):
            self._add_solution(current_solution)
            return
        
        # Get current stock piece
        stock_piece = self.stock_expanded[stock_idx]
        
        # Generate all valid patterns for this stock
        patterns = self._generate_patterns_for_stock(stock_piece, remaining_required)
        
        # Try each pattern
        for pattern in patterns:
            # Create new solution with this pattern
            new_solution = current_solution + [{
                'stock_id': stock_piece['id'],
                'stock_length_m': stock_piece['length_m'],
                'cuts': [self.required_expanded[i] for i in pattern]
            }]
            
            # Update remaining required pieces
            new_remaining = [i for i in remaining_required if i not in pattern]
            
            # Recurse with next stock piece
            self._recursive_search(new_solution, new_remaining, stock_idx + 1)
        
        # Also try not using this stock piece
        self._recursive_search(current_solution, remaining_required, stock_idx + 1)
    
    def _generate_patterns_for_stock(self, stock_piece, remaining_indices):
        """Generate valid cutting patterns for a stock piece."""
        # Filter required pieces to only remaining ones
        remaining_pieces = [self.required_expanded[i] for i in remaining_indices]
        
        if not remaining_pieces:
            return []
        
        patterns = []
        
        # Try all combinations of remaining pieces
        self._find_combinations(
            stock_piece['length_m'],
            remaining_pieces,
            remaining_indices,
            [],
            0,
            patterns
        )
        
        return patterns
    
    def _find_combinations(self, stock_length, pieces, indices, current, start, results):
        """Find all valid combinations that fit in stock."""
        # Calculate current usage
        if current:
            total_length = sum(pieces[indices.index(i)]['length_m'] for i in current)
            kerf_loss = (len(current) - 1) * self.kerf_m if len(current) > 0 else 0
            used = total_length + kerf_loss
            
            if used <= stock_length:
                results.append(current[:])
            else:
                return  # This combination is too long
        
        # Try adding more pieces
        for i in range(start, len(indices)):
            idx = indices[i]
            if idx not in current:  # Each piece can only be used once
                current.append(idx)
                self._find_combinations(stock_length, pieces, indices, current, i + 1, results)
                current.pop()
    
    def _add_solution(self, solution):
        """Add a solution to the list if it's valid."""
        if solution:  # Only add non-empty solutions
            self.solutions.append(solution)
            
            # Limit solution count to save memory
            if len(self.solutions) > self.top_n * 100:
                self.solutions.sort(key=self._solution_score, reverse=True)
                self.solutions = self.solutions[:self.top_n * 10]
    
    def _solution_score(self, solution):
        """
        Calculate score for a solution.
        Higher is better.
        
        Score tuple: (pieces_cut, -waste, -stock_used)
        """
        pieces_cut = sum(len(cut['cuts']) for cut in solution)
        total_waste = sum(self._calculate_cut_waste(cut) for cut in solution)
        stock_used = len(solution)
        
        return (pieces_cut, -total_waste, -stock_used)
    
    def _calculate_cut_waste(self, cut):
        """Calculate waste for a single cut."""
        stock_length = cut['stock_length_m']
        cuts_length = sum(piece['length_m'] for piece in cut['cuts'])
        num_cuts = len(cut['cuts']) - 1 if len(cut['cuts']) > 0 else 0
        kerf_loss = num_cuts * self.kerf_m
        
        return stock_length - cuts_length - kerf_loss

from itertools import combinations_with_replacement


class PatternGenerator:
    """Generates all valid cutting patterns for a stock piece."""
    
    def __init__(self, stock_length_m, required_pieces, kerf_mm):
        """
        Initialize pattern generator.
        
        Args:
            stock_length_m: Length of stock piece in meters
            required_pieces: List of required pieces with lengths and quantities
            kerf_mm: Kerf loss per cut in millimeters
        """
        self.stock_length_m = stock_length_m
        self.required_pieces = required_pieces
        self.kerf_m = kerf_mm / 1000.0  # Convert mm to meters
    
    def generate_patterns(self):
        """
        Generate all valid cutting patterns.
        
        Returns:
            List of patterns, where each pattern is a list of piece indices
        """
        patterns = []
        
        # Create expanded list of pieces (accounting for quantities)
        piece_pool = []
        for i, piece in enumerate(self.required_pieces):
            piece_pool.extend([i] * piece['quantity'])
        
        # Generate all possible combinations
        max_pieces = len(piece_pool)
        
        for num_pieces in range(1, max_pieces + 1):
            for combo in combinations_with_replacement(range(len(self.required_pieces)), num_pieces):
                if self._is_valid_pattern(combo):
                    patterns.append(list(combo))
        
        return patterns
    
    def _is_valid_pattern(self, pattern):
        """
        Check if a pattern fits within the stock length.
        
        Args:
            pattern: List of piece indices
        
        Returns:
            True if pattern is valid, False otherwise
        """
        if not pattern:
            return False
        
        # Calculate total length needed
        total_length = 0
        for piece_idx in pattern:
            total_length += self.required_pieces[piece_idx]['length_m']
        
        # Calculate kerf loss: (n - 1) cuts
        num_cuts = len(pattern) - 1
        kerf_loss = num_cuts * self.kerf_m
        
        # Check if it fits
        return (total_length + kerf_loss) <= self.stock_length_m
    
    def calculate_waste(self, pattern):
        """Calculate waste for a given pattern."""
        if not pattern:
            return self.stock_length_m
        
        total_length = sum(self.required_pieces[i]['length_m'] for i in pattern)
        num_cuts = len(pattern) - 1
        kerf_loss = num_cuts * self.kerf_m
        
        return self.stock_length_m - total_length - kerf_loss

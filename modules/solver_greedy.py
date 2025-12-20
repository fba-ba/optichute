import logging
from operator import itemgetter


class GreedySolver:
    """Solves the cutting stock problem using greedy heuristics."""
    
    def __init__(self, stock, required, config):
        """
        Initialize the greedy solver.
        
        Args:
            stock: List of available stock pieces
            required: List of required pieces to cut
            config: Configuration dictionary
        """
        self.stock = stock
        self.required = required
        self.config = config
        self.kerf = config.get('kerf', 0)
        self.top_n = config.get('top_n_solutions', 10)
        self.logger = logging.getLogger(__name__)

        # Solution storage
        self.solutions = []

    def solve(self):
        """
        Solve using multiple greedy strategies and return top N solutions.
        
        Returns:
            List of top N solutions
        """
        self.logger.info(f"Stock pieces: {len(self.stock)}")
        self.logger.info(f"Required pieces: {len(self.required)}")
        
        # Define sorting variations
        sort_variations = [
            ('desc_req_desc_stock', True, True),   # Both descending (original)
            ('desc_req_asc_stock', True, False),   # Desc req, asc stock
            ('asc_req_desc_stock', False, True),   # Asc req, desc stock
            ('asc_req_asc_stock', False, False),   # Both ascending
        ]
        
        # Try each base strategy with different sorting variations
        for sort_name, req_desc, stock_desc in sort_variations:
            # First Fit
            self.logger.info(f"Trying First Fit with {sort_name}")
            solution = self._first_fit(req_desc, stock_desc)
            if solution:
                self.solutions.append(solution)
            
            # Best Fit
            self.logger.info(f"Trying Best Fit with {sort_name}")
            solution = self._best_fit(req_desc, stock_desc)
            if solution:
                self.solutions.append(solution)
            
            # Worst Fit  
            self.logger.info(f"Trying Worst Fit with {sort_name}")
            solution = self._worst_fit(req_desc, stock_desc)
            if solution:
                self.solutions.append(solution)
        
        # Sort solutions by score
        self.solutions.sort(key=self._solution_score, reverse=True)
        
        # Return top N unique solutions
        unique_solutions = self._get_unique_solutions(self.solutions)
        return unique_solutions[:self.top_n]
    
    def _first_fit(self, req_descending=True, stock_descending=True):
        """First Fit strategy with configurable sorting."""
        # Sort required pieces by length
        required_sorted = sorted(self.required, 
                                key=lambda x: x['length'], 
                                reverse=req_descending)
        
        # Sort stock pieces by length
        stock_sorted = sorted(self.stock, 
                             key=lambda x: x['length'], 
                             reverse=stock_descending)
        
        solution = []
        remaining_required = required_sorted[:]
        
        for stock_piece in stock_sorted:
            if not remaining_required:
                break
            
            cuts = []
            remaining_length = stock_piece['length']
            
            i = 0
            while i < len(remaining_required):
                piece = remaining_required[i]
                
                # Calculate space needed including kerf
                kerf_needed = self.kerf if cuts else 0
                space_needed = piece['length'] + kerf_needed
                
                if space_needed <= remaining_length:
                    cuts.append(piece)
                    remaining_length -= space_needed
                    remaining_required.pop(i)
                else:
                    i += 1
            
            if cuts:
                solution.append({
                    'stock_id': stock_piece['id'],
                    'stock_length': stock_piece['length'],
                    'cuts': cuts
                })
        
        return solution if solution else None
    
    def _best_fit(self, req_descending=True, stock_descending=True):
        """Best Fit strategy - minimizes waste per stock piece."""
        # Sort required pieces by length
        required_sorted = sorted(self.required, 
                                key=lambda x: x['length'], 
                                reverse=req_descending)
        
        solution = []
        remaining_required = required_sorted[:]
        available_stock = sorted(self.stock, 
                                key=lambda x: x['length'], 
                                reverse=stock_descending)
        
        while remaining_required and available_stock:
            best_fit = None
            best_waste = float('inf')
            best_stock_idx = -1
            best_cuts = []
            
            # Try each stock piece
            for stock_idx, stock_piece in enumerate(available_stock):
                cuts = []
                remaining_length = stock_piece['length']
                temp_required = remaining_required[:]
                
                # Greedily fill this stock
                i = 0
                while i < len(temp_required):
                    piece = temp_required[i]
                    kerf_needed = self.kerf if cuts else 0
                    space_needed = piece['length'] + kerf_needed
                    
                    if space_needed <= remaining_length:
                        cuts.append(piece)
                        remaining_length -= space_needed
                        temp_required.pop(i)
                    else:
                        i += 1
                
                # Calculate waste
                if cuts:
                    waste = remaining_length
                    if waste < best_waste:
                        best_waste = waste
                        best_stock_idx = stock_idx
                        best_cuts = cuts
            
            # Apply best fit
            if best_stock_idx >= 0:
                stock_piece = available_stock[best_stock_idx]
                solution.append({
                    'stock_id': stock_piece['id'],
                    'stock_length': stock_piece['length'],
                    'cuts': best_cuts
                })
                
                # Remove used stock and pieces
                available_stock.pop(best_stock_idx)
                for cut in best_cuts:
                    remaining_required.remove(cut)
            else:
                break
        
        return solution if solution else None
    
    def _worst_fit(self, req_descending=True, stock_descending=True):
        """Worst Fit strategy - spreads pieces across stock."""
        # Sort required pieces by length
        required_sorted = sorted(self.required, 
                                key=lambda x: x['length'], 
                                reverse=req_descending)
        
        # Initialize bins (stock pieces) - sorted for consistency
        stock_sorted = sorted(self.stock, 
                             key=lambda x: x['length'], 
                             reverse=stock_descending)
        bins = []
        for stock_piece in stock_sorted:
            bins.append({
                'stock_id': stock_piece['id'],
                'stock_length': stock_piece['length'],
                'cuts': [],
                'remaining': stock_piece['length']
            })
        
        # Assign each piece to bin with most remaining space
        for piece in required_sorted:
            # Find bin with most remaining space that can fit this piece
            best_bin = None
            max_remaining = -1
            
            for bin_data in bins:
                kerf_needed = self.kerf if bin_data['cuts'] else 0
                space_needed = piece['length'] + kerf_needed
                
                if space_needed <= bin_data['remaining']:
                    if bin_data['remaining'] > max_remaining:
                        max_remaining = bin_data['remaining']
                        best_bin = bin_data
            
            # Add piece to best bin
            if best_bin:
                kerf_needed = self.kerf if best_bin['cuts'] else 0
                best_bin['cuts'].append(piece)
                best_bin['remaining'] -= (piece['length'] + kerf_needed)
        
        # Convert to solution format
        solution = []
        for bin_data in bins:
            if bin_data['cuts']:
                solution.append({
                    'stock_id': bin_data['stock_id'],
                    'stock_length': bin_data['stock_length'],
                    'cuts': bin_data['cuts']
                })
        
        return solution if solution else None
    
    def _get_unique_solutions(self, solutions):
        """Filter out duplicate solutions."""
        unique = []
        seen_signatures = set()
        
        for solution in solutions:
            signature = self._solution_signature(solution)
            if signature not in seen_signatures:
                unique.append(solution)
                seen_signatures.add(signature)
        
        return unique
    
    def _solution_signature(self, solution):
        """Create a unique signature for a solution."""
        # Include both pieces AND their stock arrangement for true uniqueness
        arrangement = tuple(
            (cut['stock_id'], tuple(sorted([p['id'] for p in cut['cuts']])))
            for cut in sorted(solution, key=lambda x: x['stock_id'])
        )
        return arrangement
    
    def _solution_score(self, solution):
        """Calculate score for a solution."""
        pieces_cut = sum(len(cut['cuts']) for cut in solution)
        total_waste = sum(self._calculate_waste(cut) for cut in solution)
        stock_used = len(solution)
        
        return (pieces_cut, -total_waste, -stock_used)
    
    def _calculate_waste(self, cut):
        """Calculate waste for a single cut."""
        stock_length = cut['stock_length']
        cuts_length = sum(piece['length'] for piece in cut['cuts'])
        num_cuts = len(cut['cuts']) - 1 if len(cut['cuts']) > 0 else 0
        kerf_loss = num_cuts * self.kerf
        
        return stock_length - cuts_length - kerf_loss

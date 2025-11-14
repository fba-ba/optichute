import json
import logging
from datetime import datetime


class OutputFormatter:
    """Formats and outputs optimization results."""
    
    def __init__(self, config, stock, required, solutions, computation_time):
        """Initialize formatter with results."""
        self.config = config
        self.stock = stock
        self.required = required
        self.solutions = solutions
        self.computation_time = computation_time
        self.kerf_mm = config.get('kerf_mm', 0)
        self.kerf_m = self.kerf_mm / 1000.0
        self.logger = logging.getLogger(__name__)
    
    def print_console(self):
        """Print results to console."""
        print("\n" + "=" * 80)
        print("WOOD CUTTING OPTIMIZATION RESULTS")
        print("=" * 80)
        
        # Input summary
        total_stock = sum(s['length_m'] * s.get('quantity', 1) for s in self.stock)
        total_required = sum(r['length_m'] * r.get('quantity', 1) for r in self.required)
        
        print(f"\nINPUT SUMMARY:")
        print(f"  Total stock available: {total_stock:.3f}m")
        print(f"  Total required: {total_required:.3f}m")
        print(f"  Kerf per cut: {self.kerf_mm}mm ({self.kerf_m:.4f}m)")
        print(f"  Computation time: {self.computation_time:.3f}s")
        print(f"  Solutions found: {len(self.solutions)}")
        
        # Print top solutions
        for rank, solution in enumerate(self.solutions, 1):
            self._print_solution(rank, solution)
            
            if rank >= self.config.get('top_n_solutions', 10):
                break
    
    def _print_solution(self, rank, solution):
        """Print a single solution."""
        pieces_cut = sum(len(cut['cuts']) for cut in solution)
        total_required_pieces = sum(r.get('quantity', 1) for r in self.required)
        completion = (pieces_cut / total_required_pieces * 100) if total_required_pieces > 0 else 0
        total_waste = sum(self._calculate_waste(cut) for cut in solution)
        stock_used = len(solution)
        
        print(f"\n{'─' * 80}")
        print(f"SOLUTION #{rank} - {pieces_cut}/{total_required_pieces} pieces ({completion:.1f}% complete)")
        print(f"{'─' * 80}")
        
        for i, cut in enumerate(solution, 1):
            stock_id = cut['stock_id']
            stock_length = cut['stock_length_m']
            cuts = cut['cuts']
            
            print(f"\nSTOCK #{i} ({stock_id}) - {stock_length}m:")
            
            # List cuts
            cut_list = ", ".join([f"{c['id']}({c['length_m']}m)" for c in cuts])
            print(f"  CUT: {cut_list}")
            
            # Calculate kerf and waste
            num_cuts = len(cuts) - 1 if len(cuts) > 0 else 0
            kerf_loss = num_cuts * self.kerf_m
            waste = self._calculate_waste(cut)
            
            print(f"  KERF LOSS: {num_cuts} cuts × {self.kerf_mm}mm = {kerf_loss:.4f}m")
            print(f"  UNUSED: {waste:.4f}m")
        
        print(f"\n{'─' * 80}")
        print(f"TOTAL: {pieces_cut}/{total_required_pieces} pieces | " +
              f"Waste: {total_waste:.4f}m | Stock used: {stock_used}/{len(self.stock)}")
    
    def _calculate_waste(self, cut):
        """Calculate waste for a cut."""
        stock_length = cut['stock_length_m']
        cuts_length = sum(c['length_m'] for c in cut['cuts'])
        num_cuts = len(cut['cuts']) - 1 if len(cut['cuts']) > 0 else 0
        kerf_loss = num_cuts * self.kerf_m
        
        return stock_length - cuts_length - kerf_loss
    
    def save_json(self, output_file):
        """Save results to JSON file."""
        # Build JSON structure
        total_stock = sum(s['length_m'] * s.get('quantity', 1) for s in self.stock)
        total_required = sum(r['length_m'] * r.get('quantity', 1) for r in self.required)
        
        output_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "input_summary": {
                "total_stock_length_m": round(total_stock, 4),
                "total_required_length_m": round(total_required, 4),
                "kerf_mm": self.kerf_mm,
                "algo_type": self.config.get('algo_type', 'recursive'),
                "computation_time_s": round(self.computation_time, 4)
            },
            "solutions": []
        }
        
        # Add solutions
        for rank, solution in enumerate(self.solutions, 1):
            solution_data = self._format_solution_json(rank, solution)
            output_data["solutions"].append(solution_data)
            
            if rank >= self.config.get('top_n_solutions', 10):
                break
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        self.logger.info(f"Results saved to {output_file}")
    
    def _format_solution_json(self, rank, solution):
        """Format a solution for JSON output."""
        pieces_cut = sum(len(cut['cuts']) for cut in solution)
        total_required_pieces = sum(r.get('quantity', 1) for r in self.required)
        completion = (pieces_cut / total_required_pieces * 100) if total_required_pieces > 0 else 0
        total_waste = sum(self._calculate_waste(cut) for cut in solution)
        stock_used = len(solution)
        
        cutting_plan = []
        for cut in solution:
            num_cuts = len(cut['cuts']) - 1 if len(cut['cuts']) > 0 else 0
            kerf_loss = num_cuts * self.kerf_m
            waste = self._calculate_waste(cut)
            
            cutting_plan.append({
                "stock_id": cut['stock_id'],
                "stock_length_m": round(cut['stock_length_m'], 4),
                "cuts": [
                    {
                        "id": c['id'],
                        "length_m": round(c['length_m'], 4)
                    } for c in cut['cuts']
                ],
                "kerf_loss_m": round(kerf_loss, 4),
                "unused_m": round(waste, 4)
            })
        
        # Determine unfulfilled pieces
        cut_pieces = set()
        for cut in solution:
            for piece in cut['cuts']:
                cut_pieces.add(piece['id'])
        
        all_required = set()
        for piece in self.required:
            for i in range(piece.get('quantity', 1)):
                all_required.add(f"{piece.get('id', 'P')}-{i+1}")
        
        unfulfilled = list(all_required - cut_pieces)
        
        return {
            "rank": rank,
            "score": {
                "pieces_cut": pieces_cut,
                "pieces_required": total_required_pieces,
                "completion_percentage": round(completion, 2),
                "total_waste_m": round(total_waste, 4),
                "stock_pieces_used": stock_used
            },
            "cutting_plan": cutting_plan,
            "unfulfilled_pieces": unfulfilled
        }

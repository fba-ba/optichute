class CuttingVisualizer:
    """Creates ASCII art visualizations of cutting patterns."""
    
    def __init__(self, kerf=0):
        """Initialize visualizer."""
        self.kerf = kerf
    
    def visualize_solution(self, solution, width=70):
        """
        Create ASCII visualization of a complete solution.
        
        Args:
            solution: List of cuts
            width: Character width for visualization
        
        Returns:
            String containing ASCII art
        """
        output = []
        
        for i, cut in enumerate(solution, 1):
            output.append(f"\nStock #{i}: {cut['stock_id']} ({cut['stock_length']}mm)")
            output.append(self._visualize_single_cut(cut, width))
        
        return "\n".join(output)
    
    def _visualize_single_cut(self, cut, width=70):
        """
        Create ASCII visualization of a single stock piece cut.
        
        Args:
            cut: Dictionary with stock_length and cuts
            width: Character width for the bar
        
        Returns:
            String containing ASCII art
        """
        stock_length = cut['stock_length']
        cuts = cut['cuts']
        
        # Calculate total used length
        cuts_length = sum(c['length'] for c in cuts)
        num_cuts = len(cuts) - 1 if cuts else 0
        kerf_loss = num_cuts * self.kerf
        waste = stock_length - cuts_length - kerf_loss
        
        # Build visualization
        lines = []
        
        # Top border
        lines.append("┌" + "─" * width + "┐")
        
        # Calculate character widths for each section
        char_per_meter = width / stock_length
        
        # Build the bar
        bar = "│"
        legend = " "
        
        for i, piece in enumerate(cuts):
            piece_chars = int(piece['length'] * char_per_meter)
            piece_chars = max(1, piece_chars)  # At least 1 character
            
            # Add piece
            piece_label = piece['id']
            if len(piece_label) <= piece_chars:
                padding = (piece_chars - len(piece_label)) // 2
                bar += " " * padding + piece_label + " " * (piece_chars - padding - len(piece_label))
            else:
                bar += piece_label[:piece_chars]
            
            legend += f"{piece['id']}({piece['length']}mm) "
            
            # Add kerf if not last piece
            if i < len(cuts) - 1:
                kerf_chars = max(1, int(self.kerf * char_per_meter))
                bar += "█" * kerf_chars
                legend += "| "
        
        # Add waste
        waste_chars = width - len(bar) + 1  # +1 for the opening │
        if waste_chars > 0:
            bar += "░" * waste_chars
        
        bar += "│"
        lines.append(bar)
        
        # Bottom border
        lines.append("└" + "─" * width + "┘")
        
        # Add legend
        lines.append(f"  Pieces: {legend.strip()}")
        lines.append(f"  Kerf (█): {kerf_loss}mm | Waste (░): {waste}mm")
        
        return "\n".join(lines)
    
    def create_compact_view(self, solution):
        """
        Create a compact text representation.
        
        Args:
            solution: List of cuts
        
        Returns:
            String with compact view
        """
        lines = []
        
        for i, cut in enumerate(solution, 1):
            pieces = " + ".join([f"{c['id']}" for c in cut['cuts']])
            
            cuts_length = sum(c['length'] for c in cut['cuts'])
            num_cuts = len(cut['cuts']) - 1 if cut['cuts'] else 0
            kerf_loss = num_cuts * self.kerf
            waste = cut['stock_length'] - cuts_length - kerf_loss
            
            lines.append(
                f"[{cut['stock_id']}] {pieces} = {cuts_length}mm + "
                f"kerf:{kerf_loss}mm + waste:{waste}mm = {cut['stock_length']}mm"
            )
        
        return "\n".join(lines)

import json
from pathlib import Path


class InputParser:
    """Parses and validates JSON input files."""
    
    def __init__(self, filepath):
        """Initialize parser with input file path."""
        self.filepath = filepath
        self.data = None
    
    def parse(self):
        """Parse and validate the input JSON file."""
        # Read JSON file
        with open(self.filepath, 'r') as f:
            self.data = json.load(f)
        
        # Validate structure
        self._validate()
        
        # Extract components
        config = self.data.get('config', {})
        stock = self.data.get('stock', [])
        required = self.data.get('required', [])
        
        return config, stock, required
    
    def _validate(self):
        """Validate the input data structure."""
        if 'stock' not in self.data:
            raise ValueError("Missing 'stock' field in input JSON")
        
        if 'required' not in self.data:
            raise ValueError("Missing 'required' field in input JSON")
        
        # Validate stock pieces
        for i, piece in enumerate(self.data['stock']):
            if 'length_m' not in piece:
                raise ValueError(f"Stock piece {i} missing 'length_m'")
            if piece['length_m'] <= 0:
                raise ValueError(f"Stock piece {i} has invalid length")
            if 'quantity' not in piece:
                piece['quantity'] = 1  # Default quantity
        
        # Validate required pieces
        for i, piece in enumerate(self.data['required']):
            if 'length_m' not in piece:
                raise ValueError(f"Required piece {i} missing 'length_m'")
            if piece['length_m'] <= 0:
                raise ValueError(f"Required piece {i} has invalid length")
            if 'quantity' not in piece:
                piece['quantity'] = 1  # Default quantity
        
        # Validate config
        config = self.data.get('config', {})
        if 'kerf_mm' not in config:
            config['kerf_mm'] = 0  # Default: no kerf
        if 'top_n_solutions' not in config:
            config['top_n_solutions'] = 10  # Default: top 10
        if 'algo_type' not in config:
            config['algo_type'] = 'recursive'  # Default algorithm
        if 'log_level' not in config:
            config['log_level'] = 'INFO'  # Default log level

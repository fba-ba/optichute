#!/usr/bin/env python3
"""
Wood Cutting Optimizer
Optimizes the cutting of wood offcuts to minimize waste and maximize piece count.
"""

import sys
import json
import time
from pathlib import Path
from modules.solver_recursive import RecursiveSolver
from modules.solver_greedy import GreedySolver


# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.input_parser import InputParser
from modules.solver_recursive import RecursiveSolver
from modules.output_formatter import OutputFormatter
from modules.logger import setup_logger


def main():
    """Main entry point for the wood optimizer."""
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python wood_optimizer.py <input_file.json>")
        print("Example: python wood_optimizer.py tests/test_basic.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if file exists
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found!")
        sys.exit(1)
    
    try:
        # Parse input
        parser = InputParser(input_file)
        config, stock, required = parser.parse()
        
        # Setup logger
        logger = setup_logger(config.get('log_level', 'INFO'))
        logger.info(f"Starting wood cutting optimization...")
        logger.info(f"Algorithm: {config.get('algo_type', 'recursive')}")
        
        # Start timing
        start_time = time.time()
        
        # Select algorithm
        algo_type = config.get('algo_type', 'recursive').lower()

        if algo_type == 'recursive':
            solver = RecursiveSolver(stock, required, config)
            solutions = solver.solve()
        elif algo_type == 'greedy':
            solver = GreedySolver(stock, required, config)
            solutions = solver.solve()
        else:
            raise ValueError(f"Unknown algorithm type: {algo_type}")    
        
        # Calculate computation time
        computation_time = time.time() - start_time
        logger.info(f"Computation completed in {computation_time:.3f}s")
        
        # Format and display output
        formatter = OutputFormatter(config, stock, required, solutions, computation_time)


        # Console output
        visualize = config.get('visualize', True)
        formatter.print_console(visualize=visualize)
        
        # JSON output (if requested)
        output_file = config.get('output_file')
        if output_file:
            formatter.save_json(output_file)
            logger.info(f"Results saved to {output_file}")
        
        logger.info("Optimization complete!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

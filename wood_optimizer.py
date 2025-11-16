#!/usr/bin/env python3
"""
Wood Cutting Optimizer
Optimizes the cutting of wood offcuts to minimize waste and maximize piece count.
"""

import sys
import json
import time
import multiprocessing
from pathlib import Path


# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.input_parser import InputParser
from modules.solver_recursive import RecursiveSolver
from modules.solver_greedy import GreedySolver
from modules.output_formatter import OutputFormatter
from modules.logger import setup_logger


def run_solver_process(solver, result_list):
    """Wrapper function to run solver in a separate process and store results."""
    solutions = solver.solve()
    if solutions:
        result_list.extend(solutions)


def main():
    """Main entry point for the wood optimizer."""
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python wood_optimizer.py <input_file.json>")
        print("Example: python wood_optimizer.py tests/test_basic.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    input_path = Path(input_file)
    
    # Check if file exists
    if not input_path.exists():
        print(f"Error: File '{input_file}' not found!")
        sys.exit(1)
    
    config = {}  # Initialize config here to ensure it's available in 'finally'
    output_file_success = None
    output_file_error = None

    try:
        # Parse input
        parser = InputParser(input_file)
        config, stock, required = parser.parse()
        
        # Setup logger
        logger = setup_logger(config.get('log_level', 'INFO'))
        logger.info(f"Starting wood cutting optimization...")
        logger.info(f"Algorithm: {config.get('algo_type', 'recursive')}")
        
        # Determine output file paths
        output_file_base = config.get('output_file')
        if output_file_base:
            output_path = Path(output_file_base)
            output_file_success = output_path
            output_file_error = output_path.with_suffix('.err')
        else:
            output_file_success = input_path.with_suffix('.cut')
            output_file_error = input_path.with_suffix('.err')

        # Start timing
        start_time = time.time()
        
        # Select algorithm
        algo_type = config.get('algo_type', 'recursive').lower()

        solver = None
        if algo_type == 'recursive':
            solver = RecursiveSolver(stock, required, config)
        elif algo_type == 'greedy':
            solver = GreedySolver(stock, required, config)
        else:
            raise ValueError(f"Unknown algorithm type: {algo_type}")    
        
        # Run solver with timeout
        timeout = config.get('timeout', 0)
        solutions = []
        if timeout > 0:
            with multiprocessing.Manager() as manager:
                # Using a list proxy to get results back from the process
                result_list = manager.list()
                p = multiprocessing.Process(target=run_solver_process, args=(solver, result_list))
                p.start()
                p.join(timeout)
                if p.is_alive():
                    p.terminate()
                    p.join()
                    logger.warning(f"Solver timed out after {timeout} seconds.")
                else:
                    solutions = list(result_list)
        else:
            solutions = solver.solve()

        # Calculate computation time
        computation_time = time.time() - start_time
        logger.info(f"Computation completed in {computation_time:.3f}s")
        
        # Format and display output
        formatter = OutputFormatter(config, stock, required, solutions, computation_time)

        # Console output
        visualize = config.get('visualize', True)
        formatter.print_console(visualize=visualize)
        
        # JSON output (if requested)
        formatter.save_json(output_file_success)
        
        logger.info("Optimization complete!")
        
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        if output_file_error:
            with open(output_file_error, 'w') as f:
                f.write(json.dumps({"error": error_message, "traceback": traceback.format_exc()}, indent=2))
        sys.exit(1)
    finally:
        if config.get('delete_me', False):
            input_path.unlink()
            print(f"Input file '{input_file}' deleted.")


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Add this line for executable compatibility
    main()

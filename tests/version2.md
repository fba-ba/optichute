# Wood Optimizer - Implementation Status

This document tracks the status of the new requirements and outlines the impact on the existing codebase.

**Last Updated:** 2024-10-27

---

### Requirement Breakdown & Impact Analysis

| # | Requirement | Status | Impacted Files | Notes |
|---|---|---|---|---|
| 1 | **Units to `mm`**: All length measures will be in `mm`. `kerf_mm` becomes `kerf`. `length_m` becomes `length`. | **Done** | `input_parser.py`, `solver_*.py`, `output_formatter.py`, `visualizer.py`, `tests/*.json` | This is a core change affecting most of the logic and I/O. The `kerf_m` conversion will be removed. |
| 2 | **`log_level` optional**: Default to `INFO`. | **Done** | `input_parser.py` | The default is already in place, but I will verify it. |
| 3 | **`output_file` optional**: Default to `input_file.cut` on success, `input_file.err` on failure. | **Done** | `wood_optimizer.py` | The main script will handle this logic at the end of execution. |
| 4 | **`length_m` to `length`**: Rename parameter in input. | **Done** | `input_parser.py`, `solver_*.py`, `output_formatter.py`, `visualizer.py`, `tests/*.json` | Handled as part of Requirement #1. |
| 5 | **`timeout` parameter**: New optional `config` parameter to stop long-running jobs. | **Done** | `wood_optimizer.py` | Implemented in the main script to wrap the solver execution. |
| 6 | **`delete_me` parameter**: New optional `config` parameter to delete the input file after processing. | **Done** | `wood_optimizer.py` | A `finally` block will be used to ensure deletion happens on success or failure. |
| 7 | **Remove `quantity`**: Each stock/required piece is a unique entry with a unique `id`. | **Done** | `input_parser.py`, `solver_*.py`, `output_formatter.py`, `tests/*.json` | The `_expand_stock` and `_expand_required` methods will be removed from solvers. |
| 8 | **`length_m` to `length`**: Rename parameter in output. | **Done** | `output_formatter.py`, `visualizer.py` | Handled as part of Requirement #1. |
| 9 | **`total_*_m` to `total_*_length`**: Rename output summary fields. | **Done** | `output_formatter.py` | Handled as part of Requirement #1. |
| 10 | **`kerf_mm` to `kerf`**: Rename output summary field. | **Done** | `output_formatter.py` | Handled as part of Requirement #1. |
| 11 | **No ID suffix**: Use the `id` from the input file directly, without adding `-1`, `-2`, etc. | **Done** | `solver_*.py`, `output_formatter.py` | This is a direct consequence of removing the `quantity` parameter. |

---

### Implementation Steps

1.  **Modify `input_parser.py`**:
    -   Update validation to look for `length` instead of `length_m`.
    -   Remove default `quantity` logic.
    -   Add default for `timeout`.

2.  **Modify Solver Modules (`solver_recursive.py`, `solver_greedy.py`)**:
    -   Remove `_expand_stock` and `_expand_required` methods.
    -   Update all `length_m` references to `length`.
    -   Remove `kerf_m` conversion and use `kerf` directly.
    -   Ensure algorithms correctly handle lists with duplicate lengths but unique IDs.

3.  **Modify `visualizer.py`**:
    -   Update all `length_m` references to `length`.
    -   Remove `kerf_m` conversion.
    -   Adjust calculations to work with `mm`.

4.  **Modify `output_formatter.py`**:
    -   Update all `length_m` references to `length`.
    -   Update JSON output fields (`total_stock_length`, `kerf`, etc.).
    -   Update console output to reflect `mm`.
    -   Remove logic that relies on expanded IDs.

5.  **Modify `wood_optimizer.py`**:
    -   Implement `timeout` logic around the `solver.solve()` call.
    -   Implement the new `output_file` naming logic (`.cut`/`.err`).
    -   Implement the `delete_me` logic to remove the input file.

6.  **Update Test Files (`tests/*.json`)**:
    -   Update all test files to the new format (remove `quantity`, use `length` and `kerf`, add `timeout` and `delete_me` where appropriate).

This structured approach will ensure all requirements are met and the script remains robust.


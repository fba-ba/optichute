# 🪵 Wood Optimizer - User Guide

This guide provides instructions on how to set up, use, and distribute the Wood Cutting Optimizer script.

---

## 1. Scope of the Script

The Wood Optimizer is a command-line tool designed to solve the "cutting stock problem" for woodworking projects. Its primary purpose is to determine the most efficient way to cut a list of required wood pieces from a given inventory of available stock pieces (offcuts).

The script aims to:
-   **Maximize Material Usage**: It finds cutting plans that produce the highest possible number of required pieces.
-   **Minimize Waste**: Among solutions that produce the same number of pieces, it prioritizes those with the least amount of leftover material.
-   **Provide Flexibility**: It can generate multiple high-quality solutions, allowing you to choose the one that best fits your needs.
-   **Ensure Accuracy**: It accounts for material lost during each cut, known as "kerf," which you can specify in millimeters.

The optimizer supports two different algorithms: a precise `recursive` method for optimal results on smaller projects, and a fast `greedy` method for good, quick solutions on larger, more complex jobs.

---

## 2. Setting Up the Python Environment

To ensure the script runs in a clean and isolated environment, it's highly recommended to use a Python virtual environment (`venv`). This prevents conflicts with other Python projects on your system.

### Creating the Virtual Environment

1.  Open a terminal or command prompt in the project's main folder (the one containing `wood_optimizer.py`).
2.  Run the command to create a new virtual environment. A common convention is to name the environment folder `venv`. The command is `python -m venv venv`.
3.  A new folder named `venv` will be created in your project directory.

### Activating the Virtual Environment

Before running the script, you must activate the environment. The command differs based on your operating system.

-   **On Windows**: Run `venv\Scripts\activate`.
-   **On macOS and Linux**: Run `source venv/bin/activate`.

Once activated, your command prompt will usually show the environment's name (e.g., `(venv)`) to indicate that it's active. The script does not require any external packages, so no installation with `pip` is necessary.

---

## 3. How to Use the Optimizer

The script is run from the command line and takes a single argument: the path to a JSON file that defines your project.

### Running the Script

With your virtual environment activated, run the script by typing `python`, the script name `wood_optimizer.py`, and finally the path to your input file.

Example: `python wood_optimizer.py tests/test_basic.json`

### The Input JSON File

This file contains all the information the optimizer needs. All length measurements must be provided in **millimeters (mm)**. It is structured into three main sections:

-   **`config`**: This section holds general settings.
    -   `kerf`: The saw blade width in millimeters (e.g., `3`).
    -   `algo_type`: The algorithm to use (`recursive` or `greedy`).
    -   `top_n_solutions`: The number of top-ranked solutions to display.
    -   `timeout` (optional): The maximum time in seconds the script is allowed to run before stopping.
    -   `delete_me` (optional): Set to `true` to automatically delete the input file after processing.

-   **`stock`**: A list of all the available wood pieces you have in your inventory. Each item in the list is an object representing a **single, unique piece** of stock with its own `id` and `length` in millimeters.

-   **`required`**: A list of all the pieces you need to cut for your project. Like the stock, each item is an object for a **single, unique piece** with its own `id` and `length` in millimeters.

### Understanding the Output

After running, the script will print the results directly to the console. The output includes:
-   An **Input Summary** showing total material available versus total material needed, all in millimeters.
-   A ranked list of the **Top Solutions**.
-   For each solution, a detailed **Cutting Plan** shows which required pieces to cut from each stock piece, along with the calculated waste and kerf loss for that stock.
-   A final summary for each solution, showing the total number of pieces cut, total waste, and the number of stock pieces used.

The script will also generate an output file with a `.cut` extension (e.g., `test_basic.cut`) containing the results in a structured JSON format. If an error occurs, a `.err` file will be created instead.

---

## 4. Usage Examples

### Example 1: A Small DIY Project

Imagine you are building a small bookshelf and have a few leftover wood planks.

You would create a JSON file listing your three stock planks and the ten different-sized pieces you need. Since this is a small job, you would set the `algo_type` to `recursive` to find the absolute best cutting plan.

**`bookshelf.json`:**
```json
{
  "config": {
    "kerf": 3,
    "algo_type": "recursive",
    "top_n_solutions": 5
  },
  "stock": [
    {"id": "plank-01", "length": 2500},
    {"id": "plank-02", "length": 1600}
  ],
  "required": [
    {"id": "shelf-1", "length": 800},
    {"id": "shelf-2", "length": 800},
    {"id": "support-1", "length": 500},
    {"id": "support-2", "length": 500}
  ]
}
```

After running `python wood_optimizer.py bookshelf.json`, the console output would show you the best solution. For instance, it might tell you to cut two 800mm pieces and one 500mm piece from your 2500mm stock plank, leaving only a small amount of waste.

### Example 2: A Large Production Run

Consider a workshop that needs to cut hundreds of pieces for a large batch of cabinets.

In this case, finding the perfect solution could take too long. You would set the `algo_type` to `greedy` and might add a `timeout` for safety.

**`cabinets.json`:**
```json
{
  "config": {
    "kerf": 3,
    "algo_type": "greedy",
    "timeout": 60
  },
  "stock": [
    {"id": "board-001", "length": 3000},
    {"id": "board-002", "length": 3000},
    ...
  ],
  "required": [
    {"id": "door-001", "length": 1200},
    {"id": "panel-001", "length": 750},
    ...
  ]
}
```

When you run the script, it will produce several very good (but not guaranteed to be perfect) cutting plans in just a few seconds. This allows you to quickly generate an efficient cutting list for the shop floor.

---

## 5. Building the Executable (.exe)

To share the script with others who may not have Python installed, you can compile it into a single standalone executable file (`.exe` on Windows). The recommended tool for this is `PyInstaller`.

### How to Build

1.  First, install `PyInstaller` into your activated virtual environment using `pip install pyinstaller`.
2.  Once installed, navigate to your project folder in the terminal.

### Interactive Version (with Console Window)

This version is for standard use, where you can see the console output.

`pyinstaller --onefile --name WoodOptimizer wood_optimizer.py`

### Non-Interactive Version (No Console Window)

This version is ideal for when the script is called by another program or a batch process. It runs silently in the background without opening a console window.

`pyinstaller --onefile --noconsole --name WoodOptimizer_ni wood_optimizer.py`

The `--noconsole` flag is the key here. It creates a "windowless" application. The script is robustly designed to handle this mode, writing its output to `.cut` or `.err` files instead of trying to print to a non-existent console.

### Finding the Executable

After running either command, `PyInstaller` will package your script into a single `.exe` file. You will find the final executable (`WoodOptimizer.exe` or `WoodOptimizer_ni.exe`) inside a new folder named `dist`. This file can be run on any compatible computer without needing Python or any other dependencies.
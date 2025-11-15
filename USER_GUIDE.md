# 🪵 Wood Optimizer - User Guide

This guide provides instructions on how to set up, use, and distribute the Wood Cutting Optimizer script.

---

## 1. Scope of the Script

The Wood Optimizer is a command-line tool designed to solve the "cutting stock problem" for woodworking projects. Its primary purpose is to determine the most efficient way to cut a list of required wood pieces from a given inventory of available stock pieces (offcuts).

The script aims to:
-   **Maximize Material Usage**: It finds cutting plans that produce the highest possible number of required pieces.
-   **Minimize Waste**: Among solutions that produce the same number of pieces, it prioritizes those with the least amount of leftover material.
-   **Provide Flexibility**: It can generate multiple high-quality solutions, allowing you to choose the one that best fits your needs.
-   **Ensure Accuracy**: It accounts for material lost during each cut, known as "kerf," which you can specify.

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

This file contains all the information the optimizer needs. It is structured into three main sections:

-   **`config`**: This section holds general settings. You can define the saw blade `kerf_mm` (in millimeters), the `algo_type` (`recursive` or `greedy`), and the number of `top_n_solutions` you wish to see.
-   **`stock`**: Here, you list all the available wood pieces you have in your inventory. For each type of stock, you specify its length and quantity.
-   **`required`**: This section lists all the pieces you need to cut for your project, including their desired length and quantity.

### Understanding the Output

After running, the script will print the results directly to the console. The output includes:
-   An **Input Summary** showing total material available versus total material needed.
-   A ranked list of the **Top Solutions**.
-   For each solution, a detailed **Cutting Plan** shows which required pieces to cut from each stock piece, along with the calculated waste and kerf loss for that stock.
-   A final summary for each solution, showing the total number of pieces cut, total waste, and the number of stock pieces used.

If specified in the config, the script can also save these results in a structured JSON file for your records.

---

## 4. Usage Examples

### Example 1: A Small DIY Project

Imagine you are building a small bookshelf and have a few leftover wood planks.

You would create a JSON file listing your three stock planks and the ten different-sized pieces you need for the shelves and supports. In the `config` section, you would set the `algo_type` to `recursive` to find the absolute best cutting plan.

After running the script with your JSON file, the console output would show you the best solution. For instance, it might tell you to cut two 0.8m pieces and one 0.5m piece from your 2.5m stock plank, leaving only a small amount of waste. It would provide a similar plan for your other stock pieces, helping you complete the project with minimal material cost.

### Example 2: A Large Production Run

Consider a workshop that needs to cut hundreds of pieces for a large batch of cabinets.

In this case, finding the perfect solution could take too long. You would set the `algo_type` to `greedy` in the JSON file. This tells the optimizer to use a faster heuristic approach.

When you run the script, it will produce several very good (but not guaranteed to be perfect) cutting plans in just a few seconds. This allows you to quickly generate an efficient cutting list for the shop floor, saving significant time and material compared to manual planning, even on a very large scale.

---

## 5. Building the Executable (.exe)

To share the script with others who may not have Python installed, you can compile it into a single standalone executable file (`.exe` on Windows). The recommended tool for this is `PyInstaller`.

### How to Build

1.  First, install `PyInstaller` into your activated virtual environment using `pip install pyinstaller`.
2.  Once installed, navigate to your project folder in the terminal.
3.  Run the `pyinstaller` command with a few options. Specify that you want a `--onefile` executable and give it a `--name`, for example, `WoodOptimizer`. The final argument is the name of your Python script.

    Example: `pyinstaller --onefile --name WoodOptimizer wood_optimizer.py`

4.  `PyInstaller` will analyze your script and package it, along with a Python interpreter, into a single `.exe` file.
5.  You will find the final `WoodOptimizer.exe` file inside a new folder named `dist`. This file can be run on any compatible computer without needing Python or any other dependencies.

This makes distributing and running the tool incredibly simple for any user.
import multiprocessing as mp
import tkinter as tk
from tkinter import filedialog


def file_explorer():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    filepath = filedialog.askdirectory() or ""
    return filepath.strip()


if __name__ == "__main__":
    print(file_explorer())

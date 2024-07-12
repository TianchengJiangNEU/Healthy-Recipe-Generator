import tkinter as tk
from gui import RecipeGeneratorGUI

def main():
    root = tk.Tk()
    app = RecipeGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
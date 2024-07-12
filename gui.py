import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from config import EXAMPLE_CUISINE, EXAMPLE_DIET
from recipe_api import get_recipes, get_shopping_list, save_shopping_list
import re

class RecipeGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Recipe Generator")
        master.geometry("800x600")

        self.create_widgets()
        self.pack_widgets()

    def create_widgets(self):
        # Cuisine
        self.cuisine_label = ttk.Label(self.master, text="Cuisine:")
        self.cuisine_combobox = ttk.Combobox(self.master, values=["None"] + EXAMPLE_CUISINE)
        self.cuisine_combobox.set("None")

        # Diet
        self.diet_label = ttk.Label(self.master, text="Diet:")
        self.diet_combobox = ttk.Combobox(self.master, values=["None"] + EXAMPLE_DIET)
        self.diet_combobox.set("None")

        # Ingredients
        self.ingredients_label = ttk.Label(self.master, text="Ingredients (separate multiple ingredients with commas):")
        self.ingredients_entry = ttk.Entry(self.master, width=50)

        # Max Calories
        self.calories_label = ttk.Label(self.master, text="Max Calories:")
        self.calories_entry = ttk.Entry(self.master)

        # Max Fat
        self.fat_label = ttk.Label(self.master, text="Max Fat (g):")
        self.fat_entry = ttk.Entry(self.master)

        # Number of Recipes
        self.number_label = ttk.Label(self.master, text="Number of Recipes:")
        self.number_entry = ttk.Entry(self.master)

        # Generate Button
        self.generate_button = ttk.Button(self.master, text="Generate Recipes", command=self.generate_recipes)

        # Results
        self.results_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=80, height=20)
        self.results_text.config(state=tk.DISABLED)

    def pack_widgets(self):
        # Pack all widgets
        self.cuisine_label.pack()
        self.cuisine_combobox.pack()
        self.diet_label.pack()
        self.diet_combobox.pack()
        self.ingredients_label.pack()
        self.ingredients_entry.pack()
        self.calories_label.pack()
        self.calories_entry.pack()
        self.fat_label.pack()
        self.fat_entry.pack()
        self.number_label.pack()
        self.number_entry.pack()
        self.generate_button.pack(pady=10)
        self.results_text.pack(pady=10)

    def validate_ingredients(self, ingredients):
        # Split the ingredients string into a list
        ingredient_list = [i.strip() for i in ingredients.split(',')]
        
        # Check if each ingredient is valid (not just numbers)
        for ingredient in ingredient_list:
            if ingredient.isdigit() or not re.search('[a-zA-Z]', ingredient):
                return False
        return True

    def generate_recipes(self):
        # Get input values
        cuisine = self.cuisine_combobox.get()
        cuisine = None if cuisine == "None" else cuisine
        diet = self.diet_combobox.get()
        diet = None if diet == "None" else diet
        ingredients = self.ingredients_entry.get()
        max_calories = self.calories_entry.get()
        max_fat = self.fat_entry.get()
        number = self.number_entry.get()

        # Validate inputs
        if not ingredients:
            messagebox.showerror("Error", "Please enter at least one ingredient.", parent=self.master)
            return
        if not self.validate_ingredients(ingredients):
            messagebox.showerror("Error", "Please enter valid ingredients.", parent=self.master)
            return
        if not max_calories.isdigit() or not max_fat.isdigit() or not number.isdigit():
            messagebox.showerror("Error", "Please enter valid numbers for calories, fat, and number of recipes.", parent=self.master)
            return

        try:
            # Get recipes
            recipes, total_results = get_recipes(cuisine, diet, ingredients, max_calories, max_fat, number)

            # Debug information
            print("API Response:")
            for recipe in recipes:
                print(f"Recipe ID: {recipe.get('id')}")
                print(f"Instructions type: {type(recipe.get('instructions'))}")
                print(f"Analyzed Instructions: {recipe.get('analyzedInstructions')}")
                print(f"Summary: {recipe.get('summary')}")
                print("---")

            # Display results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            
            if total_results == 0:
                self.results_text.insert(tk.END, "Sorry, no recipes found.")
            else:
                for recipe in recipes:
                    self.results_text.insert(tk.END, f"Recipe ID: {recipe.get('id', 'N/A')}\n")
                    self.results_text.insert(tk.END, f"Recipe Title: {recipe.get('title', 'N/A')}\n")
                    self.results_text.insert(tk.END, f"Time Required: {recipe.get('readyInMinutes', 'N/A')} minutes\n")
                    self.results_text.insert(tk.END, f"Recipe URL: {recipe.get('spoonacularSourceUrl', 'N/A')}\n")
                    
                    self.results_text.insert(tk.END, "Calorie & Fat Content:\n")
                    nutrition = recipe.get('nutrition', {}).get('nutrients', [])
                    for item in nutrition:
                        self.results_text.insert(tk.END, f"{item.get('name', 'N/A')}: {item.get('amount', 'N/A')} {item.get('unit', 'N/A')}\n")
                    
                    self.results_text.insert(tk.END, "Ingredients Needed:\n")
                    ingredients = recipe.get('extendedIngredients', [])
                    for item in ingredients:
                        self.results_text.insert(tk.END, f"{item.get('name', 'N/A')}: {item.get('amount', 'N/A')} {item.get('unit', 'N/A')}\n")
                    
                    self.results_text.insert(tk.END, "Instructions:\n")
                    instructions = recipe.get('analyzedInstructions', [])
                    if instructions and isinstance(instructions[0], dict):
                        steps = instructions[0].get('steps', [])
                        if steps:
                            for step in steps:
                                self.results_text.insert(tk.END, f"{step.get('number', 'N/A')}. {step.get('step', 'N/A')}\n")
                        else:
                            self.results_text.insert(tk.END, "No detailed instructions available.\n")
                    elif 'instructions' in recipe and recipe['instructions']:
                        self.results_text.insert(tk.END, recipe['instructions'] + "\n")
                    elif 'summary' in recipe and recipe['summary']:
                        self.results_text.insert(tk.END, "Recipe summary:\n" + recipe['summary'] + "\n")
                    else:
                        self.results_text.insert(tk.END, "No instructions available. Please check the recipe URL for more details.\n")
                    
                    self.results_text.insert(tk.END, "\n")

            self.results_text.config(state=tk.DISABLED)

            # Ask user if they want to save shopping list
            self.ask_save_shopping_list(recipes)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while fetching recipes: {str(e)}", parent=self.master)

    def ask_save_shopping_list(self, recipes):
        save_window = tk.Toplevel(self.master)
        save_window.title("Save Shopping List")
        save_window.geometry("400x300")

        question_label = ttk.Label(save_window, text="Select recipes to save shopping lists:")
        question_label.pack(pady=10)

        recipe_listbox = tk.Listbox(save_window, selectmode=tk.MULTIPLE, width=50, height=10)
        for recipe in recipes:
            recipe_listbox.insert(tk.END, f"{recipe['id']} - {recipe['title']}")
        recipe_listbox.pack(pady=10)

        def save_lists():
            selected_indices = recipe_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Error", "Please select at least one recipe.", parent=save_window)
                return

            saved_count = 0
            for index in selected_indices:
                recipe_id = recipes[index]['id']
                try:
                    ingredients = get_shopping_list(recipe_id)
                    if ingredients:
                        save_shopping_list(recipe_id, ingredients)
                        saved_count += 1
                    else:
                        messagebox.showwarning("Warning", f"Unable to get ingredients for recipe {recipe_id}.", parent=save_window)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Error saving shopping list for recipe {recipe_id}: {str(e)}", parent=save_window)

            if saved_count > 0:
                messagebox.showinfo("Success", f"{saved_count} shopping list(s) have been saved to 'Shopping list.txt'.", parent=save_window)
            save_window.destroy()

        save_button = ttk.Button(save_window, text="Save Selected", command=save_lists)
        save_button.pack(pady=10)


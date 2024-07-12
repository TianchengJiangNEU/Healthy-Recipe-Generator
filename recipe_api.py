import requests
from config import API_KEY

def get_recipes(cuisine, diet, include_ingredients, max_calories, max_fat, number):
    url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}'
    
    params = {
        'includeIngredients': include_ingredients,
        'maxCalories': max_calories,
        'maxFat': max_fat,
        'addRecipeInformation': True,
        'fillIngredients': True,
        'instructionsRequired': True,
        'addRecipeNutrition': True,
        'number': number
    }
    
    if cuisine:
        params['cuisine'] = cuisine
    if diet:
        params['diet'] = diet

    response = requests.get(url, params=params)
    data = response.json()
    return data['results'], data['totalResults']

def get_shopping_list(recipe_id):
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/ingredientWidget.json?apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data.get('ingredients', [])

def save_shopping_list(recipe_id, ingredients):
    with open('Shopping list.txt', 'a') as file:
        file.write(f'*******Shopping list for recipe {recipe_id}*******\n')
        for item in ingredients:
            file.write(f"{item['name']}: {item['amount']['metric']['value']} {item['amount']['metric']['unit']}\n")
        file.write('\n')
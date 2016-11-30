import requests
import json, os
from dotenv import load_dotenv

class RecipeClient:
  def __init__(self, api_key):
    self. endpoint = \
      'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/'
    self.api_key = api_key

  def find_by_ingredients(self, ingredients):
    url = self.endpoint + 'recipes/findByIngredients'

    params = {
      'fillIngredients': False,
      'ingredients': ingredients, #string
      'limitLicense': False,
      'number': 5,
      'ranking': 1
    }

    headers={
      "X-Mashape-Key": self.api_key,
      "Accept": "application/json"
    }

    return requests.get(url, params=params, headers=headers).json()

  def find_by_cuisine(self, cuisine):
    url = self.endpoint + "recipes/search"

    payload = {
      'number': 5,
      'query': ' ',
      'cuisine': cuisine
    }
    headers={ 'X-Mashape-Key': self.api_key }

    return requests.get(url, 
                        params=payload, 
                        headers=headers).json()['results']

  def get_info_by_id(self, id):
    url = self.endpoint + "recipes/" + str(id) + "/information"
    params = {'includeNutrition': False }
    headers = {'X-Mashape-Key': self.api_key}

    return requests.get(url, params=params, headers=headers).json()

  def get_steps_by_id(self, id):
    url = self.endpoint + "recipes/" + str(id) + "/analyzedInstructions"
    params = {'stepBreakdown': True}
    headers={'X-Mashape-Key': self.api_key}

    return requests.get(url, params=params, headers=headers).json()

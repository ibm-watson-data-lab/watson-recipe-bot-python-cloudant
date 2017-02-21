import time

from cloudant.query import Query


class CloudantRecipeStore(object):

    def __init__(self, client, db_name):
        """
        Creates a new instance of CloudantRecipeStore.
        Parameters
        ----------
        client - The instance of cloudant client to connect to
        db_name - The name of the database to use
        """
        self.client = client
        self.db_name = db_name

    def init(self):
        """
        Creates and initializes the database.
        """
        try:
            self.client.connect()
            print('Getting database...')
            if self.db_name not in self.client.all_dbs():
                print('Creating database {}...'.format(self.db_name))
                self.client.create_database(self.db_name)
            else:
                print('Database {} exists.'.format(self.db_name))
            # see if the by_popularity design doc exists, if not then create it
            db = self.client[self.db_name]
            query = Query(db, selector={ '_id': '_design/by_popularity' })
            result = query()['docs']
            if result is None or len(result) <= 0:
                design_doc = {
                    '_id': '_design/by_popularity',
                    'views': {
                        'ingredients': {
                            'map': 'function (doc) {\n  if (doc.type && doc.type==\'userIngredientRequest\') {\n    emit(doc.ingredient_name, 1);\n  }\n}',
                            'reduce': '_sum'
                        },
                        'cuisines': {
                            'map': 'function (doc) {\n  if (doc.type && doc.type==\'userCuisineRequest\') {\n    emit(doc.cuisine_name, 1);\n  }\n}',
                            'reduce': '_sum'
                        },
                        'recipes': {
                            'map': 'function (doc) {\n  if (doc.type && doc.type==\'userRecipeRequest\') {\n    emit(doc.recipe_title, 1);\n  }\n}',
                            'reduce': '_sum'
                        }
                    },
                    'language': 'javascript'
                }
                db.create_document(design_doc)
            # see if the by_day_of_week design doc exists, if not then create it
            query = Query(db, selector={ '_id': '_design/by_day_of_week' })
            result = query()['docs']
            if result is None or len(result) <= 0:
                design_doc = {
                    '_id': '_design/by_day_of_week',
                    'views': {
                        'ingredients': {
                            'map': 'function (doc) {\n  if (doc.type && doc.type==\'userIngredientRequest\') {\n    var weekdays = [\'Sunday\',\'Monday\',\'Tuesday\',\'Wednesday\',\'Thursday\',\'Friday\',\'Saturday\'];\n    emit(weekdays[new Date(doc.date).getDay()], 1);\n  }\n}',
                            'reduce': '_sum'
                        },
                        'cuisines': {
                            'map': 'function (doc) {\n  if (doc.type && doc.type==\'userCuisineRequest\') {\n    var weekdays = [\'Sunday\',\'Monday\',\'Tuesday\',\'Wednesday\',\'Thursday\',\'Friday\',\'Saturday\'];\n    emit(weekdays[new Date(doc.date).getDay()], 1);\n  }\n}',
                            'reduce': '_sum'
                        },
                        'recipes': {
                            'map': 'function (doc) {\n  if (doc.type && doc.type==\'userRecipeRequest\') {\n    var weekdays = [\'Sunday\',\'Monday\',\'Tuesday\',\'Wednesday\',\'Thursday\',\'Friday\',\'Saturday\'];\n    emit(weekdays[new Date(doc.date).getDay()], 1);\n  }\n}',
                            'reduce': '_sum'
                        }
                    },
                    'language': 'javascript'
                }
                db.create_document(design_doc)
        finally:
            self.client.disconnect()

    # User

    def add_user(self, user_id):
        """
        Adds a new user to Cloudant if a user with the specified ID does not already exist.
        Parameters
        ----------
        user_id - The ID of the user (typically the ID returned from Slack)
        """
        user_doc = {
            'type': 'user',
            'name': user_id
        }
        return self.add_doc_if_not_exists(user_doc, 'name')

    # Ingredients

    @staticmethod
    def get_unique_ingredients_name(ingredient_str):
        """
        Gets the unique name for the ingredient to be stored in Cloudant.
        Parameters
        ----------
        ingredient_str - The ingredient or comma-separated list of ingredients specified by the user
        """
        ingredients = [x.strip() for x in ingredient_str.lower().strip().split(',')]
        ingredients.sort()
        return ','.join([x for x in ingredients])

    def find_ingredient(self, ingredient_str):
        """
        Finds the ingredient based on the specified ingredientsStr in Cloudant.
        Parameters
        ----------
        ingredient_str - The ingredient or comma-separated list of ingredients specified by the user
        """
        return self.find_doc('ingredient', 'name', self.get_unique_ingredients_name(ingredient_str))

    def add_ingredient(self, ingredient_str, matching_recipes, user_doc):
        """
        Adds a new ingredient to Cloudant if an ingredient based on the specified ingredientsStr does not already exist.
        Parameters
        ----------
        ingredient_str - The ingredient or comma-separated list of ingredients specified by the user
        matching_recipes - The recipes that match the specified ingredientsStr
        user_doc - The existing Cloudant doc for the user
        """
        ingredient_doc = {
            'type': 'ingredient',
            'name': self.get_unique_ingredients_name(ingredient_str),
            'recipes': matching_recipes
        }
        ingredient_doc = self.add_doc_if_not_exists(ingredient_doc, 'name')
        self.record_ingredient_request_for_user(ingredient_doc, user_doc)
        return ingredient_doc

    def record_ingredient_request_for_user(self, ingredient_doc, user_doc):
        """
        Records the request by the user for the specified ingredient.
        Stores the ingredient and the number of times it has been accessed in the user doc.
        Parameters
        ----------
        ingredient_doc - The existing Cloudant doc for the ingredient
        user_doc - The existing Cloudant doc for the user
        """
        try:
            self.client.connect()
            # get latest user
            latest_user_doc = self.client[self.db_name][user_doc['_id']]
            # see if user has an array of ingredients, if not create it
            if 'ingredients' not in latest_user_doc.keys():
                latest_user_doc['ingredients'] = []
            # find the ingredient that matches the name of the passed in ingredient
            # if it doesn't exist create it
            user_ingredients = filter(lambda x: x['name'] == ingredient_doc['name'], latest_user_doc['ingredients'])
            if len(user_ingredients) > 0:
                user_ingredient = user_ingredients[0]
            else:
                user_ingredient = {'name': ingredient_doc['name']}
                latest_user_doc['ingredients'].append(user_ingredient)
            # see if the user_ingredient exists, if not create it
            if 'count' not in user_ingredient.keys():
                user_ingredient['count'] = 0
            # increment the count on the user_ingredient
            user_ingredient['count'] += 1
            # save the user doc
            latest_user_doc.save()
            # add a new doc with the user/ingredient details
            user_ingredient_doc = {
                'type': 'userIngredientRequest',
                'user_id': user_doc['_id'],
                'user_name': user_doc['name'],
                'ingredient_id': ingredient_doc['_id'],
                'ingredient_name': ingredient_doc['name'],
                'date': int(time.time()*1000)
            }
            db = self.client[self.db_name]
            db.create_document(user_ingredient_doc)
        finally:
            self.client.disconnect()

    # Cuisine

    @staticmethod
    def get_unique_cuisine_name(cuisine):
        """
        Gets the unique name for the cuisine to be stored in Cloudant.
        Parameters
        ----------
        cuisine - The cuisine specified by the user
        """
        return cuisine.strip().lower()

    def find_cuisine(self, cuisine):
        """
        Finds the cuisine with the specified name in Cloudant.
        Parameters
        ----------
        cuisine - The cuisine specified by the user
        """
        return self.find_doc('cuisine', 'name', self.get_unique_cuisine_name(cuisine))

    def add_cuisine(self, cuisine_str, matching_recipes, user_doc):
        """
        Adds a new cuisine to Cloudant if a cuisine with the specified name does not already exist.
        Parameters
        ----------
        cuisine - The cuisine specified by the user
        matching_recipes - The recipes that match the specified cuisine
        user_doc - The existing Cloudant doc for the user
        """
        cuisine_doc = {
            'type': 'cuisine',
            'name': self.get_unique_cuisine_name(cuisine_str),
            'recipes': matching_recipes
        }
        cuisine_doc = self.add_doc_if_not_exists(cuisine_doc, 'name')
        self.record_cuisine_request_for_user(cuisine_doc, user_doc)
        return cuisine_doc

    def record_cuisine_request_for_user(self, cuisine_doc, user_doc):
        """
        Records the request by the user for the specified cuisine.
        Stores the cuisine and the number of times it has been accessed in the user doc.
        Parameters
        ----------
        cuisine_doc - The existing Cloudant doc for the cuisine
        user_doc - The existing Cloudant doc for the user
        """
        try:
            self.client.connect()
            # get latest user
            latest_user_doc = self.client[self.db_name][user_doc['_id']]
            # see if user has an array of cuisines, if not create it
            if 'cuisines' not in latest_user_doc.keys():
                latest_user_doc['cuisines'] = []
            # find the cuisine that matches the name of the passed in cuisine
            # if it doesn't exist create it
            user_cuisines = filter(lambda x: x['name'] == cuisine_doc['name'], latest_user_doc['cuisines'])
            if len(user_cuisines) > 0:
                user_cuisine = user_cuisines[0]
            else:
                user_cuisine = {'name': cuisine_doc['name']}
                latest_user_doc['cuisines'].append(user_cuisine)
            # see if the user_cuisine exists, if not create it
            if 'count' not in user_cuisine.keys():
                user_cuisine['count'] = 0
            # increment the count on the user_cuisine
            user_cuisine['count'] += 1
            # save the user doc
            latest_user_doc.save()
            # add a new doc with the user/cuisine details
            user_cuisine_doc = {
                'type': 'userCuisineRequest',
                'user_id': user_doc['_id'],
                'user_name': user_doc['name'],
                'cuisine_id': cuisine_doc['_id'],
                'cuisine_name': cuisine_doc['name'],
                'date': int(time.time()*1000)
            }
            db = self.client[self.db_name]
            db.create_document(user_cuisine_doc)
        finally:
            self.client.disconnect()

    # Recipe

    @staticmethod
    def get_unique_recipe_name(recipe_id):
        """
        Gets the unique name for the recipe to be stored in Cloudant.
        Parameters
        ----------
        recipe_id - The ID of the recipe (typically the ID of the recipe returned from Spoonacular)
        """
        return str(recipe_id).strip().lower()

    def find_recipe(self, recipe_id):
        """
        Finds the recipe with the specified ID in Cloudant.
        Parameters
        ----------
        recipe_id - The ID of the recipe (typically the ID of the recipe returned from Spoonacular)
        """
        return self.find_doc('recipe', 'name', self.get_unique_recipe_name(recipe_id))

    def find_favorite_recipes_for_user(self, user_doc, count):
        """
        Finds the user's favorite recipes in Cloudant.
        Parameters
        ----------
        user_doc - The existing Cloudant doc for the user
        count - The max number of recipes to return
        """
        try:
            self.client.connect()
            db = self.client[self.db_name]
            latest_user_doc = db[user_doc['_id']]
            if 'recipes' in latest_user_doc.keys():
                user_recipes = latest_user_doc['recipes']
                user_recipes.sort(key=lambda x: x['count'], reverse=True)
                recipes = []
                for i, recipe in enumerate(user_recipes):
                    if i >= count:
                        break
                    recipes.append(recipe)
                return recipes
            else:
                return []
        finally:
            self.client.disconnect()

    def add_recipe(self, recipe_id, recipe_title, recipe_detail, ingredient_cuisine_doc, user_doc):
        """
        Adds a new recipe to Cloudant if a recipe with the specified name does not already exist.
        Parameters
        ----------
        recipe_id - The ID of the recipe (typically the ID of the recipe returned from Spoonacular)
        recipe_title - The title of the recipe
        recipe_detail - The detailed instructions for making the recipe
        ingredient_cuisine_doc - The existing Cloudant doc for either the ingredient or cuisine selected before the recipe
        user_doc - The existing Cloudant doc for the user
        """
        recipe = {
            'type': 'recipe',
            'name': self.get_unique_recipe_name(recipe_id),
            'title': recipe_title.strip(),
            'instructions': recipe_detail
        }
        recipe = self.add_doc_if_not_exists(recipe, 'name')
        self.record_recipe_request_for_user(recipe, ingredient_cuisine_doc, user_doc)
        return recipe

    def record_recipe_request_for_user(self, recipe_doc, ingredient_cuisine_doc, user_doc):
        """
        Records the request by the user for the specified recipe.
        Stores the recipe and the number of times it has been accessed in the user doc.
        Parameters
        ----------
        recipe_doc - The existing Cloudant doc for the recipe
        ingredient_cuisine_doc - The existing Cloudant doc for either the ingredient or cuisine selected before the recipe
        user_doc - The existing Cloudant doc for the user
        """
        try:
            self.client.connect()
            # get latest user
            latest_user_doc = self.client[self.db_name][user_doc['_id']]
            # see if user has an array of recipes, if not create it
            if 'recipes' not in latest_user_doc.keys():
                latest_user_doc['recipes'] = []
            # find the recipe that matches the name of the passed in recipe
            # if it doesn't exist create it
            user_recipes = filter(lambda x: x['id'] == recipe_doc['name'], latest_user_doc['recipes'])
            if len(user_recipes) > 0:
                user_recipe = user_recipes[0]
            else:
                user_recipe = {
                    'id': recipe_doc['name'],
                    'title': recipe_doc['title']
                }
                latest_user_doc['recipes'].append(user_recipe)
            # see if the user_recipe exists, if not create it
            if 'count' not in user_recipe.keys():
                user_recipe['count'] = 0
            # increment the count on the user_recipe
            user_recipe['count'] += 1
            # save the user doc
            latest_user_doc.save()
            # add a new doc with the user/recipe details
            user_recipe_doc = {
                'type': 'userRecipeRequest',
                'user_id': user_doc['_id'],
                'user_name': user_doc['name'],
                'recipe_id': recipe_doc['_id'],
                'recipe_title': recipe_doc['title'],
                'date': int(time.time()*1000)
            }
            db = self.client[self.db_name]
            db.create_document(user_recipe_doc)
        finally:
            self.client.disconnect()

    # Cloudant Helper Methods

    def find_doc(self, doc_type, property_name, property_value):
        """
        Finds a doc based on the specified doc_type, property_name, and property_value.
        Parameters
        ----------
        doc_type - The type value of the document stored in Cloudant
        property_name - The property name to search for
        property_value - The value that should match for the specified property name
        """
        try:
            self.client.connect()
            db = self.client[self.db_name]
            selector = {
                '_id': {'$gt': 0},
                'type': doc_type,
                property_name: property_value
            }
            query = Query(db, selector=selector)
            for doc in query()['docs']:
                return doc
            return None
        finally:
            self.client.disconnect()

    def add_doc_if_not_exists(self, doc, unique_property_name):
        """
        Adds a new doc to Cloudant if a doc with the same value for unique_property_name does not exist.
        Parameters
        ----------
        doc - The document to add
        unique_property_name - The name of the property used to search for an existing document (the value will be extracted from the doc provided)
        """
        doc_type = doc['type']
        property_value = doc[unique_property_name]
        existing_doc = self.find_doc(doc_type, unique_property_name, property_value)
        if existing_doc is not None:
            print('Returning {} doc where {}={}'.format(doc_type, unique_property_name, property_value))
            return existing_doc
        else:
            print('Creating {} doc where {}={}'.format(doc_type, unique_property_name, property_value))
            try:
                self.client.connect()
                db = self.client[self.db_name]
                return db.create_document(doc)
            finally:
                self.client.disconnect()

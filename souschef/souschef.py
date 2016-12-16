import pprint
import time
import threading
from user_state import UserState


class SousChef(threading.Thread):

    def __init__(self, slack_bot_id, slack_client, conversation_client, conversation_workspace_id, recipe_client, recipe_store):
        threading.Thread.__init__(self)
        self.running = True
        self.slack_bot_id = slack_bot_id
        self.slack_client = slack_client
        self.conversation_client = conversation_client
        self.conversation_workspace_id = conversation_workspace_id
        self.recipe_client = recipe_client
        self.recipe_store = recipe_store
        #
        self.at_bot = "<@" + slack_bot_id + ">:"
        self.delay = 0.5  # second
        self.user_state_map = {}
        self.pp = pprint.PrettyPrinter(indent=4)

    def parse_slack_output(self, slack_rtm_output):
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and 'user_profile' not in output and self.at_bot in output['text']:
                    return output['text'].split(self.at_bot)[1].strip().lower(), output['user'], output['channel']
                elif output and 'text' in output and 'user_profile' not in output:
                    return output['text'].lower(), output['user'], output['channel']
        return None, None, None

    def post_to_slack(self, response, channel):
        self.slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

    def handle_message(self, message, message_sender, channel):
        try:
            # get or create state for the user
            if message_sender in self.user_state_map.keys():
                state = self.user_state_map[message_sender]
            else:
                state = UserState(message_sender)
                self.user_state_map[message_sender] = state
            # send message to watson conversation
            watson_response = self.conversation_client.message(
                workspace_id=self.conversation_workspace_id,
                message_input={'text': message},
                context=state.conversation_context)
            # update conversation context
            state.conversation_context = watson_response['context']
            # route response
            if 'is_favorites' in state.conversation_context.keys() and state.conversation_context['is_favorites']:
                response = self.handle_favorites_message(state)
            elif 'is_ingredients' in state.conversation_context.keys() and state.conversation_context['is_ingredients']:
                response = self.handle_ingredients_message(state, message)
            elif 'is_selection' in state.conversation_context.keys() and state.conversation_context['is_selection']:
                response = self.handle_selection_message(state)
            elif watson_response['entities'] and watson_response['entities'][0]['entity'] == 'cuisine':
                cuisine = watson_response['entities'][0]['value']
                response = self.handle_cuisine_message(state, cuisine)
            else:
                response = self.handle_start_message(state, watson_response)
        except Exception:
            # clear state and set response
            self.clear_user_state(state)
            response = "Sorry, something went wrong! Say anything to me to start over..."
        # post response to slack
        self.post_to_slack(response, channel)

    def handle_start_message(self, state, watson_response):
        if state.user is None:
            user = self.recipe_store.add_user(state.user_id)
            state.user = user
        response = ''
        for text in watson_response['output']['text']:
            response += text + "\n"
        return response

    def handle_favorites_message(self, state):
        recipes = self.recipe_store.find_favorite_recipes_for_user(state.user, 5)
        # update state
        state.conversation_context['recipes'] = recipes
        state.ingredient_cuisine = None
        # build and return response
        response = self.get_recipe_list_response(state)
        return response

    def handle_ingredients_message(self, state, message):
        # we want to get a list of recipes based on the ingredients (message)
        # first we see if we already have the ingredients in our datastore
        ingredients_str = message
        ingredient = self.recipe_store.find_ingredient(ingredients_str)
        if ingredient is not None:
            print "Ingredient exists for {}. Returning recipes from datastore.".format(ingredients_str)
            matching_recipes = ingredient['recipes']
            # increment the count on the user-ingredient
            self.recipe_store.record_ingredient_request_for_user(ingredient, state.user)
        else:
            # we don't have the ingredients in our datastore yet, so get list of recipes from Spoonacular
            print "Ingredient does not exist for {}. Querying Spoonacular for recipes.".format(ingredients_str)
            matching_recipes = self.recipe_client.find_by_ingredients(ingredients_str)
            # add ingredient to datastore
            ingredient = self.recipe_store.add_ingredient(ingredients_str, matching_recipes, state.user)
        # update state
        state.conversation_context['recipes'] = matching_recipes
        state.ingredient_cuisine = ingredient
        # build and return response
        response = self.get_recipe_list_response(state)
        return response

    def handle_cuisine_message(self, state, message):
        # we want to get a list of recipes based on the cuisine
        # first we see if we already have the cuisine in our datastore
        cuisine_str = message
        cuisine = self.recipe_store.find_cuisine(cuisine_str)
        if cuisine is not None:
            print "Cuisine exists for {}. Returning recipes from datastore.".format(cuisine_str)
            matching_recipes = cuisine['recipes']
            # increment the count on the user-cuisine
            self.recipe_store.record_cuisine_request_for_user(cuisine, state.user)
        else:
            # we don't have the cuisine in our datastore yet, so get list of recipes from Spoonacular
            print "Cuisine does not exist for {}. Querying Spoonacular for recipes.".format(cuisine_str)
            matching_recipes = self.recipe_client.find_by_cuisine(cuisine_str)
            # add cuisine to datastore
            cuisine = self.recipe_store.add_cuisine(cuisine_str, matching_recipes, state.user)
        # update state
        state.conversation_context['recipes'] = matching_recipes
        state.ingredient_cuisine = cuisine
        # build and return response
        response = self.get_recipe_list_response(state)
        return response

    def handle_selection_message(self, state):
        selection = -1
        if state.conversation_context['selection'].isdigit():
            selection = int(state.conversation_context['selection'])
        if 1 <= selection <= 5:
            # we want to get a the recipe based on the selection
            # first we see if we already have the recipe in our datastore
            recipes = state.conversation_context['recipes']
            recipe_id = recipes[selection-1]['id']
            recipe = self.recipe_store.find_recipe(recipe_id)
            if recipe is not None:
                print "Recipe exists for {}. Returning recipe steps from datastore.".format(recipe_id)
                recipe_detail = recipe['instructions']
                recipe_title = recipe['title']
                # increment the count on the ingredient/cuisine-recipe and the user-recipe
                self.recipe_store.record_recipe_request_for_user(recipe, state.ingredient_cuisine, state.user)
            else:
                print "Recipe does not exist for {}. Querying Spoonacular for details.".format(recipe_id)
                recipe_info = self.recipe_client.get_info_by_id(recipe_id)
                recipe_steps = self.recipe_client.get_steps_by_id(recipe_id)
                recipe_detail = self.get_recipe_instructions_response(recipe_info, recipe_steps)
                recipe_title = recipe_info['title']
                # add recipe to datastore
                self.recipe_store.add_recipe(recipe_id, recipe_title, recipe_detail, state.ingredient_cuisine, state.user)
            # clear state and return response
            self.clear_user_state(state)
            return recipe_detail
        else:
            # clear state and return response
            self.clear_user_state(state)
            return "Invalid selection! Say anything to start over..."

    @staticmethod
    def clear_user_state(state):
        state.ingredient_cuisine = None
        state.conversation_context = None
        state.conversation_started = False

    @staticmethod
    def get_recipe_list_response(state):
        response = "Lets see here...\nI've found these recipes:\n"
        for i, recipe in enumerate(state.conversation_context['recipes']):
            response += str(i + 1) + ". " + recipe['title'] + "\n"
        response += "\nPlease enter the corresponding number of your choice."
        return response

    @staticmethod
    def get_recipe_instructions_response(recipe_info, recipe_steps):
        response = "Ok, it takes *" + \
                   str(recipe_info['readyInMinutes']) + \
                   "* minutes to make *" + \
                   str(recipe_info['servings']) + \
                   "* servings of *" + \
                   recipe_info['title'] + "*. Here are the steps:\n\n"

        if recipe_steps and recipe_steps[0]['steps']:
            for i, r_step in enumerate(recipe_steps[0]['steps']):
                equip_str = ""
                for e in r_step['equipment']:
                    equip_str += e['name'] + ", "
                if not equip_str:
                    equip_str = "None"
                else:
                    equip_str = equip_str[:-2]
                response += "*Step " + str(i + 1) + "*:\n" + \
                            "_Equipment_: " + equip_str + "\n" + \
                            "_Action_: " + r_step['step'] + "\n\n"
        else:
            response += "_No instructions available for this recipe._\n\n"

        response += "*Say anything to me to start over...*"
        return response

    def run(self):
        self.recipe_store.init()
        while self.running:
            if self.slack_client.rtm_connect():
                print("sous-chef is connected and running!")
                while self.running:
                    slack_output = self.slack_client.rtm_read()
                    message, message_sender, channel = self.parse_slack_output(slack_output)
                    if message and channel:
                        self.handle_message(message, message_sender, channel)
                    time.sleep(self.delay)
            else:
                print("Connection failed. Invalid Slack token or bot ID?")
        print("sous-chef shutting down...")

    def stop(self):
        self.running = False

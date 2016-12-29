import os
import sys

from cloudant.client import Cloudant
from dotenv import load_dotenv
from slackclient import SlackClient
from watson_developer_cloud import ConversationV1

from souschef.recipe import RecipeClient
from souschef.cloudant_recipe_store import CloudantRecipeStore
from souschef.souschef import SousChef

if __name__ == "__main__":
    try:
        # load environment variables
        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
        slack_bot_id = os.environ.get("SLACK_BOT_ID")
        slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
        conversation_workspace_id = os.environ.get("CONVERSATION_WORKSPACE_ID")
        conversation_client = ConversationV1(
            username=os.environ.get("CONVERSATION_USERNAME"),
            password=os.environ.get("CONVERSATION_PASSWORD"),
            version='2016-07-11'
        )
        recipe_client = RecipeClient(os.environ.get("SPOONACULAR_KEY"))
        recipe_store_url = os.environ.get("CLOUDANT_URL")
        if recipe_store_url.find('@') > 0:
            prefix = recipe_store_url[0:recipe_store_url.find('://')+3]
            suffix = recipe_store_url[recipe_store_url.find('@')+1:]
            recipe_store_url = '{}{}'.format(prefix, suffix)
        recipe_store = CloudantRecipeStore(
            Cloudant(
                os.environ.get("CLOUDANT_USERNAME"),
                os.environ.get("CLOUDANT_PASSWORD"),
                url=recipe_store_url
            ),
            os.environ.get("CLOUDANT_DB_NAME")
        )
        # start the souschef bot
        souschef = SousChef(slack_bot_id,
                            slack_client,
                            conversation_client,
                            conversation_workspace_id,
                            recipe_client,
                            recipe_store)
        souschef.start()
        sys.stdin.readline()
    except (KeyboardInterrupt, SystemExit):
        pass
    souschef.stop()
    souschef.join()

import os
from cloudant.client import Cloudant
from dotenv import load_dotenv
from slackclient import SlackClient
from watson_developer_cloud import ConversationV1

from souschef.recipe import RecipeClient
from souschef.cloudant_recipe_store import CloudantRecipeStore
from souschef.souschef import SousChef

if __name__ == "__main__":
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

    bot_id = os.environ.get("SLACK_BOT_ID")
    conversation_workspace_id = os.environ.get("CONVERSATION_WORKSPACE_ID")

    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

    conversation_client = ConversationV1(
        username=os.environ.get("CONVERSATION_USERNAME"),
        password=os.environ.get("CONVERSATION_PASSWORD"),
        version='2016-07-11'
    )

    recipe_client = RecipeClient(os.environ.get("SPOONACULAR_KEY"))

    cloudant_client = Cloudant(
        os.environ.get("CLOUDANT_USERNAME"),
        os.environ.get("CLOUDANT_PASSWORD"),
        url=os.environ.get("CLOUDANT_URL")
    )
    recipe_store = CloudantRecipeStore(cloudant_client, os.environ.get("CLOUDANT_DB_NAME"))

    souschef = SousChef(recipe_store,
                        bot_id,
                        slack_client,
                        conversation_client,
                        conversation_workspace_id,
                        recipe_client)
    souschef.run()

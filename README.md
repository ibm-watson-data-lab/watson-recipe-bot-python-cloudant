# Watson Recipe Bot + Cloudant

*NOTE: This README is a work in progress* 

This project is based on the [Watson Recipe Bot example](https://medium.com/ibm-watson-developer-cloud/how-to-build-a-recipe-slack-bot-using-watson-conversation-and-spoonacular-api-487eacaf01d4#.i0q8fnhuu).
The Watson Recipe Bot is Slack bot that recommends recipes based on ingredients or cuisines.
This project is essentially a fork of the Watson Recipe Bot with some additional features, including:

1. Multi-user support - the original application supported only a single user interacting with the bot at a time. This application support multiple users interacting with the bot at the same time.
2. Deploy to Bluemix - the original application was designed to be run locally. This application can be run locally, or deployed as a web application to Bluemix.
2. Cloudant integration - this application adds Cloudant integration for caching 3rd party API calls and storing each user's chat history (the ingredients, cuisines, and recipes they have selected).
3. Additional Watson Conversation intent - this application adds a "favorites" intent which allows a user to request their favorite recipes based on the history stored in Cloudant.

## Getting Started

Before you get started [read the original blog post](https://medium.com/ibm-watson-developer-cloud/how-to-build-a-recipe-slack-bot-using-watson-conversation-and-spoonacular-api-487eacaf01d4#.i0q8fnhuu)
to understand how the Watson Recipe Bot works. You __do not__ need to follow the instructions in the blog post. All the instructions required to run the bot are below.
After cloning this repo follow the steps below.

### Quick Reference

The following environment variables are required to run the application:

```
SLACK_BOT_TOKEN=xxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
SLACK_BOT_ID=UXXXXXXXX
SPOONACULAR_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CONVERSATION_USERNAME=xxxxxxx-xxxx-xxxx-xxxxx-xxxxxxxxxxxxx
CONVERSATION_PASSWORD=xxxxxxxxxxxx
CONVERSATION_WORKSPACE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLOUDANT_USERNAME=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-bluemix
CLOUDANT_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLOUDANT_URL=https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-bluemix.cloudant.com
CLOUDANT_DB_NAME=watson_recipe_bot
```

We will show you how configure the necessary services and retrieve these values in the instructions below:

### Prerequisites

The following prerequisites are required to run the application. We will walk you through configuring each one below:

1. A [Bluemix](https://www.ibm.com/cloud-computing/bluemix/) account.
2. A [Watson Conversation](https://www.ibm.com/watson/developercloud/conversation.html) service provisioned in your Bluemix account.
3. A [Cloudant](http://cloudant.com/) service provisioned in your Bluemix account.
4. A [Spoonacular](https://spoonacular.com/food-api) API key. A free tier is available, however a credit card is required.
5. A [Slack](https://slack.com) account and permission in your Slack team to register a Slack bot. 

To run locally you will need Python 2 or 3, [pip](https://pip.pypa.io/en/stable/) and [virtualenv](https://virtualenv.pypa.io/en/stable/).

To push your application to Bluemix from your local development environment you will need the [Bluemix CLI and Dev Tools](https://console.ng.bluemix.net/docs/starters/install_cli.html).

### Local Development Environment

We'll start by getting your local development environment set up. If you haven't already install Python, pip, and virtualenv.

You can install Python by following the instructions [here](https://www.python.org/downloads/).

You can install pip by following the instructions [here](https://pip.pypa.io/en/stable/).

You can install virtualenv by following the instructions [here](https://virtualenv.pypa.io/en/stable/).

From the command-line cd into the watson-recipe-bot-python-cloudant directory:

```
git clone https://github.com/ibm-cds-labs/watson-recipe-bot-python-cloudant
cd watson-recipe-bot-python-cloudant
```
 
Create and activate a new virtual environment:

```
virtualenv venv
source ./venv/bin/activate
```

Install the application requirements:

```
pip install -r requirements.txt
```

Copy the .env.template file included in the project to .env. This file will contain the environment variable definitions:

```
cp .env.template .env
```

### Slack

In this next step we'll create a new Slack bot in your Slack team.
 
In your web browser go to [https://my.slack.com/services/new/bot](https://my.slack.com/services/new/bot). Make sure you sign into the appropriate Slack team.
You can also change the Slack team from the pulldown in the top right.

1. You'll start by choosing a username for your bot. In the field provided enter **sous-chef**.
2. Click the **Add bot integration** button.
3. On the following screen you will find the API Token. Copy this value to your clipboard.
4. Open the .env file in a text editor.
5. Paste the copied token from your clipboard as the SLACK_BOT_TOKEN value:

    ```
    SLACK_BOT_TOKEN=xxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
    ```

6. Save the .env file

Next, we need to get the Slack ID of the bot. The application includes a Python script for doing just that.

1. From the command-line run the following command:

    ```
    python scripts/get_bot_id.py
    ```

2. The script should print out the bot ID. The output should be similar to the following:

    ```
    Bot ID for 'sous-chef' is U3XXXXXXX
    ```

3. Copy and paste the bot ID into your .env file:

    ```
    SLACK_BOT_ID=U3XXXXXXX
    ```

### Spoonacular

In this next step we'll set up your Spoonacular account. Spoonacular is a Food and Recipe API.
The application uses Spoonacular to find recipes based on ingredient or cuisines requested by the user.
  
1. In your web browser go to [https://spoonacular.com/food-api](https://spoonacular.com/food-api).
2. Find and click the **Get Access** button.
3. Click the appropriate button to gain access (i.e. **Get Regular Access**)
4. Choose the appropriate Pricing plan (i.e. **Basic**) and click the **Subscribe** button.
5. Follow the instructions to sign into or sign up for a Mashape account.
6. After you have subscribed to Spoonacular in the Documentation tab find a curl example on the right. It may look something like this:

    ```
    curl -X POST --include 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/food/products/classify' \
      -H 'X-Mashape-Key: Znxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
      -H 'Content-Type: application/json' \
      -H 'Accept: application/json' \
      --data-binary '{"title":"Kroger Vitamin A & D Reduced Fat 2% Milk","upc":"","plu_code":""}'
    ```

7. Copy the value of the X-Mashape-Key and paste it into your .env file:

    ```
    SPOONACULAR_KEY=Znxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

### Bluemix

If you do not already have a Bluemix account [click here](https://console.ng.bluemix.net/registration/) to sign up.

Login to your Bluemix account.

#### Watson Conversation

First, we'll walk you through provisioning a Watson Conversation service in your Bluemix account:

1. From your Bluemix Applications or Services Dashboard click the **Create Service** button.
2. In the IBM Bluemix Catalog search for **Watson Conversation**.
3. Select the **Conversation** service.
4. Click the **Create** button on the Conversation detail page.
5. On your newly created Conversation service page click the **Service Credentials** tab.
6. Find your newly created Credentials and click **View Credentials**
7. Copy the username and password into your .env file:

    ```
    CONVERSATION_USERNAME=xxxxxxx-xxxx-xxxx-xxxxx-xxxxxxxxxxxxx
    CONVERSATION_PASSWORD=xxxxxxxxxxxx
    ```

Next, let's launch the Watson Conversation tool and import our conversation workspace.

1. Go back to the **Manage** tab.
2. Click the **Launch tool** button.
3. Log in to Watson Conversation with your Bluemix credentials if prompted to do so.
4. On the **Create workspace** page click the **Import** button.
5. Choose the workspace.json file in the application directory (watson-recipe-bot-python-cloudant).
6. Click the **Import** button.
7. Under Workspaces you should now see the Recipe Bot.
8. Click the menu button (3 vertical dots) and click **View Details**
9. Copy the Workspace ID and paste it into your .env file:

    ```
    CONVERSATION_WORKSPACE_ID=40xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    ```

### Cloudant

We're almost there! Next, we'll provision an instance of Cloudant in our Bluemix account. After this step we will be able to run our bot locally.

1. From your Bluemix Applications or Services Dashboard click the **Create Service** button.
2. In the IBM Bluemix Catalog search for **Cloudant**.
3. Select the **Cloudant NoSQL DB** service.
4. Click the **Create** button on the Cloudant detail page.
5. On your newly created Cloudant service page click the **Service Credentials** tab.
6. Find your newly created Credentials and click **View Credentials**
7. Copy the username, password, and the url into your .env file:

    ```
    CLOUDANT_USERNAME=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-bluemix
    CLOUDANT_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    CLOUDANT_URL=https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-bluemix.cloudant.com
    ```

### Run Locally

We're now ready to test our bot. From the command-line run the following command:

```
python run.py
```

If all is well you should see output similar to the following:

```
Getting database...
Creating database watson_recipe_bot...
sous-chef is connected and running!
```

To interact with the bot open Slack, go to the Slack team where you installed the bot, start a direct conversation with
sous-chef, and say "hi".

_More details coming soon!_
 
### Deploy to Bluemix

**Coming soon!**
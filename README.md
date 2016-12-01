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

We will show you how configure the necessary services and retrieve these follows in the instructions below:

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

We'll start by getting your local development environment set up.

From the command-line cd into the watson-bot-recipe-python-cloudant directory:


### Bluemix

If you do not already have a Bluemix account [click here](https://console.ng.bluemix.net/registration/) to sign up.

Login to your Bluemix account.

#### Watson Conversation

From your Bluemix Dashboard 



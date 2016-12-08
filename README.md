# Watson Recipe Bot + Cloudant

This project is based on the [Watson Recipe Bot example](https://medium.com/ibm-watson-developer-cloud/how-to-build-a-recipe-slack-bot-using-watson-conversation-and-spoonacular-api-487eacaf01d4#.i0q8fnhuu).
The Watson Recipe Bot is a Slack bot that recommends recipes based on ingredients or cuisines.
This project is essentially a fork of the Watson Recipe Bot with some additional features, including:

1. Multi-user support - the original application supported only a single user interacting with the bot at a time. This application supports multiple users interacting with the bot at the same time.
2. Deploy to Bluemix - the original application was designed to be run locally. This application can be run locally, or deployed as a web application to Bluemix.
2. Cloudant integration - this application adds Cloudant integration for caching 3rd party API calls and storing each user's chat history (the ingredients, cuisines, and recipes they have selected).
3. Additional Watson Conversation intent - this application adds a "favorites" intent which allows a user to request their favorite recipes based on the history stored in Cloudant.

####Prefer Node.js?

There is a Node.js version of this project [here](https://github.com/ibm-cds-labs/watson-recipe-bot-nodejs-cloudant).

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

We will show you how to configure the necessary services and retrieve these values in the instructions below:

### Prerequisites

The following prerequisites are required to run the application.

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

    ![Slack](screenshots/slack1.png?rev=2&raw=true)

2. Click the **Add bot integration** button.
3. On the following screen you will find the API Token. Copy this value to your clipboard.

    ![Slack](screenshots/slack2.png?rev=2&raw=true)
    
4. Open the .env file in a text editor.
5. Paste the copied token from your clipboard as the SLACK_BOT_TOKEN value:

    ```
    SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
    ```

6. Save the .env file

Next, we need to get the Slack ID of the bot.

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
2. Click the **Get Access** button.

    ![Spoonacular](screenshots/spoonacular1.png?rev=1&raw=true)

3. Click the appropriate button to gain access (i.e. **Get Regular Access**)

    ![Spoonacular](screenshots/spoonacular2.png?rev=2&raw=true)

4. Choose the appropriate Pricing plan (i.e. **Basic**) and click the **Subscribe** button.
5. Follow the instructions to sign into or sign up for a Mashape account.
6. After you have subscribed to Spoonacular in the Documentation tab find a curl example on the right. It should look similar to this:

    ![Spoonacular](screenshots/spoonacular3.png?rev=2&raw=true)

7. Copy the value of the X-Mashape-Key and paste it into your .env file:

    ```
    SPOONACULAR_KEY=vxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

### Bluemix

If you do not already have a Bluemix account [click here](https://console.ng.bluemix.net/registration/) to sign up.

Login to your Bluemix account.

### Watson Conversation

First, we'll walk you through provisioning a Watson Conversation service in your Bluemix account:

1. From your Bluemix Applications or Services Dashboard click the **Create Service** button.

    ![Bluemix](screenshots/bluemix1.png?rev=3&raw=true)

2. In the IBM Bluemix Catalog search for **Watson Conversation**.
3. Select the **Conversation** service.

    ![Watson Conversation](screenshots/conversation1.png?rev=1&raw=true)
    
4. Click the **Create** button on the Conversation detail page.
5. On your newly created Conversation service page click the **Service Credentials** tab.

    ![Watson Conversation](screenshots/conversation2.png?rev=1&raw=true)

6. Find your newly created Credentials and click **View Credentials**

    ![Watson Conversation](screenshots/conversation3.png?rev=1&raw=true)

7. Copy the username and password into your .env file:

    ```
    CONVERSATION_USERNAME=xxxxxxx-xxxx-xxxx-xxxxx-xxxxxxxxxxxxx
    CONVERSATION_PASSWORD=xxxxxxxxxxxx
    ```

Next, let's launch the Watson Conversation tool and import our conversation workspace.

1. Go back to the **Manage** tab.
2. Click the **Launch tool** button.

    ![Watson Conversation](screenshots/conversation4.png?rev=1&raw=true)

3. Log in to Watson Conversation with your Bluemix credentials if prompted to do so.
4. On the **Create workspace** page click the **Import** button.

    ![Watson Conversation](screenshots/conversation5.png?rev=1&raw=true)
    
5. Choose the workspace.json file in the application directory (*watson-recipe-bot-python-cloudant/workspace.json*).
6. Click the **Import** button.

    ![Watson Conversation](screenshots/conversation6.png?rev=1&raw=true)

7. Under Workspaces you should now see the Recipe Bot.
8. Click the menu button (3 vertical dots) and click **View Details**

    ![Watson Conversation](screenshots/conversation7.png?rev=1&raw=true)
    
9. Copy the Workspace ID and paste it into your .env file:

    ```
    CONVERSATION_WORKSPACE_ID=40xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    ```

### Cloudant

We're almost there! Next, we'll provision an instance of Cloudant in our Bluemix account. After this step we will be able to run our bot locally.

1. From your Bluemix Applications or Services Dashboard click the **Create Service** button.
2. In the IBM Bluemix Catalog search for **Cloudant**.
3. Select the **Cloudant NoSQL DB** service.

    ![Watson Conversation](screenshots/cloudant1.png?rev=1&raw=true)
    
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

![sous-chef](screenshots/local1.png?rev=2&raw=true)

### Deploy to Bluemix

You can deploy the application to Bluemix by following a few simple steps.

We will be using the `cf push` command to deploy the application to Bluemix from our local environment. 
If you have not yet installed the Bluemix CLI and Dev Tools [click here](https://console.ng.bluemix.net/docs/starters/install_cli.html)
for instructions on how to download and configure the CLI tools.  

Once you have the CLI tools run the following command (make sure you are in the watson-recipe-bot-python-cloudant directory):

```
cf push
```

It will take a few minutes for the application to be uploaded and created in Bluemix.
The first time you deploy the application it will fail to start.
This is because we need to add our environment variables to the application in Bluemix.

1. After a few minutes has passed and your `cf push` command has completed log in to Bluemix.
2. Find and click the **watson-recipe-bot-cloudant** application under **Cloud Foundry Applications** in your Apps Dashboard.
3. On the application page click **Runtime** in the menu on the left then click **Environment Variables**:

    ![Cloud Foundry Application](screenshots/cfapp1.png?rev=1&raw=true)

4. Add each environment variable from your .env file and click the **Save** button:

    ![Cloud Foundry Application](screenshots/cfapp2.png?rev=1&raw=true)
    
5. Your app will automatically restart, but it may fail again. Wait for a minute or two and restart your app again.

To verify that your bot is running open Slack and start a direct conversation with sous-chef. Slack should show that sous-chef is active:

![sous-chef](screenshots/sous-chef1.png?rev=1&raw=true)

Here are some sample conversations you can have with sous-chef:

![sous-chef](screenshots/sous-chef-convo1.png?rev=4&raw=true)

![sous-chef](screenshots/sous-chef-convo2.png?rev=4&raw=true)

![sous-chef](screenshots/sous-chef-convo3.png?rev=4&raw=true)

## Next Steps

For more information on how the sous-chef bot works [read the original blog post](https://medium.com/ibm-watson-developer-cloud/how-to-build-a-recipe-slack-bot-using-watson-conversation-and-spoonacular-api-487eacaf01d4#.i0q8fnhuu).

We will be publishing a new blog post soon that will discuss the enhancements we have made to the original application, including
how we are using Cloudant to store chat history and enable the new "favorites" intent.

## Privacy Notice

This application includes code to track deployments to [IBM Bluemix](https://www.bluemix.net/) and other Cloud Foundry platforms. The following information is sent to a [Deployment Tracker](https://github.com/cloudant-labs/deployment-tracker) service on each deployment:

* Application Name (`application_name`)
* Space ID (`space_id`)
* Application Version (`application_version`)
* Application URIs (`application_uris`)

This data is collected from the `VCAP_APPLICATION` environment variable in IBM Bluemix and other Cloud Foundry platforms. This data is used by IBM to track metrics around deployments of sample applications to IBM Bluemix to measure the usefulness of our examples, so that we can continuously improve the content we offer to you. Only deployments of sample applications that include code to ping the Deployment Tracker service will be tracked.

### Disabling Deployment Tracking

Deployment tracking can be disabled by removing or commenting out the following line in `server.py`:

`deployment_tracker.track()`

## License

Licensed under the [Apache License, Version 2.0](LICENSE.txt).

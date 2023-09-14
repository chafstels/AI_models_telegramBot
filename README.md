
# ChatGPT: Telegram Bot powered by OpenAI GPT-3.5
ChatGPT is a Telegram bot that utilizes OpenAI's GPT-4 language model to generate human-like responses to user messages. The bot can be used for casual conversations, brainstorming ideas, or even for educational purposes.


# Installation
To use the ChatGPT bot, you will need to have a Telegram account and an OpenAI API key. You can obtain an API key by signing up for OpenAI's GPT-3.5 program.

Once you have your API key, you can download the source code for the bot and install the required dependencies using the following commands:
```sh
git clone https://github.com/Tr3bleee/ChatGPT.git

cd ChatGPT

pip install -r requirements.txt
```
# Configuration
Before running the bot, you will need to update the bot_token and api_key variables in the main.py file with your own Telegram bot token and OpenAI API key, respectively.

# Usage
To start the ChatGPT bot, run the following command:
```sh
python main.py
```
Once the bot is running, you can interact with it by sending messages to its Telegram account. The bot will respond to your messages with human-like responses generated by the GPT-4 model.

The bot currently supports the following commands:

/start: Initializes the bot and starts a new conversation thread.

/newtopic: Starts a new topic of conversation in the current conversation thread.

/image: Generate image with support DALL-E

/about: About bot

/help: Show commands


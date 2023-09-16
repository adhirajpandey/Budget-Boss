import json
from telethon.sync import TelegramClient
import datetime
import re
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime as dt


load_dotenv()

# Telegram API credentials
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')


# Connect to MongoDB
def connectMongo() -> object:
    try:
        # loading env variables
        cluster = os.getenv("MONGO_CLUSTER")
        user = os.getenv("MONGO_USER")
        password = os.getenv("MONGO_PASSWORD")

        # connecting with mongo db
        connection_string = "mongodb+srv://" + user + ":" + password + "@" + cluster + ".mongodb.net/test?retryWrites=true&w=majority"

        client = MongoClient(connection_string)

        # connecting with database
        db = client["BudgetBossDB"]

        return db

    except:
        print("Error while connecting with mongo db")


def cleanPrice(msgtext):
    price_regex = r"Price: \u20b9(\d+)"

    matches = re.findall(price_regex, msgtext)
    if matches:
        price = matches[0]
        return int(price)
    else:
        return -1


def extractFromMsgText(msgtext):
    product_name = msgtext[0:msgtext.index('\n')]
    product_price = cleanPrice(msgtext)
    product_link = msgtext[msgtext.index('https://'):]
    product_website = ""

    if "amzn" in product_link:
        product_website = "AMAZON INDIA"
    elif "bit" in product_link:
        product_website = "FLIPKART INDIA"

    return product_name, product_price, product_link, product_website


def getDeals():
    db = connectMongo()

    deals_collection = db["Deals"]

    # Channel username or ID to extract messages from
    channel_username = 'lootersindia'

    # Path to the session file
    session_file = 'session_file.session'

    # Number of recent messages to extract
    num_messages = 10

    # Create a Telegram client using the session file
    client = TelegramClient(session_file, api_id, api_hash)

    # Start the client
    client.start()

    # Get the channel entity
    channel = client.get_entity(channel_username)

    # Retrieve the recent messages from the channel
    recent_messages = client.get_messages(channel, limit=num_messages)

    # List to store extracted messages
    messages = []

    # Iterate over the recent messages in reverse order
    for message in reversed(recent_messages):
        # Extract desired message data
        product_name, product_price, product_link, product_website = extractFromMsgText(message.text)

        message_data = {
            'id': message.id,
            'message_time_unix': message.date.timestamp(),
            'message_time': datetime.datetime.fromtimestamp(message.date.timestamp()).strftime('%Y-%m-%d %H:%M:%S'),
            'product_link': product_link,
            'product_name': product_name,
            'product_price': product_price,
            'product_website': product_website
        }

        # Append the message data to the list
        messages.append(message_data)

    # Save messages to a JSON file
    with open('mostrecent_dump.json', 'w') as json_file:
        json.dump(messages, json_file, indent=4)

    # check id for redundancy
    list_of_ids = deals_collection.find({}, {"id": 1, "_id": 0})

    list_of_ids = [x['id'] for x in list_of_ids]

    new_messages = [message for message in messages if message['id'] not in list_of_ids]

    # Insert new messages into MongoDB
    if new_messages:
        deals_collection.insert_many(new_messages)

    if new_messages:
        print(
            f"{len(new_messages)} new messages from the channel saved to channel_messages.json file and inserted into MongoDB")
    else:
        print("No new messages from the channel")


if __name__ == "__main__":
    print(dt.now())
    getDeals()
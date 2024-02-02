import os
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup
import json
import requests


load_dotenv()


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


def getImageFromAmazonLink(link):
    try:
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
        # getting page using requests module
        page = requests.get(link, headers=header)

        soup = BeautifulSoup(page.content, 'html.parser')

        # defining title and price
        # title = soup.find(id='productTitle').get_text()

        img_div = soup.find(id="imgTagWrapperId")
        imgs_str = img_div.img.get('data-a-dynamic-image')  # a string in Json format

        # convert to a dictionary
        imgs_dict = json.loads(imgs_str)

        # each key in the dictionary is a link of an image, and the value shows the size (print all the dictionay to inspect)
        num_element = 0

        first_link = list(imgs_dict.keys())[num_element]

        return first_link

    except Exception as e:
        # print("Error in extracting image :", e)
        return None


def getImageFromFlipkartLink(URL):
    try:
        response = requests.get(URL)

        final_url = response.url

        URL = final_url

        response = requests.get(URL)

        # Extracting the source code of the page and passing it to bs4
        page = BeautifulSoup(response.text, 'html.parser')

        # fetch data of all img tags only src attribute and get link with highest dim(landing img)
        links = [img.get('src') for img in page.find_all('img') if img.get('src') and img.get('src').startswith('http') and "image" in img.get('src')]
        dimensions = list(set(link.split('/')[4] for link in links))
        highest_dim = max(dimensions)

        image = [link for link in links if highest_dim in link][0]

        return image

    except:
        return None


def fetchAmazonImg(link):
    # retrying multiple times due to unpredictable amazon response
    count = 0
    imglink = None
    while count < 15 and imglink == None:
        imglink = getImageFromAmazonLink(link)
        count += 1
    return imglink

def fetchFlipkartImg(link):
    # retrying multiple times due to unpredictable flipkart response
    count = 0
    imglink = None
    while count < 15 and imglink == None:
        imglink = getImageFromFlipkartLink(link)
        count += 1
    return imglink


def getImages():
    db = connectMongo()
    deals_collection = db["Deals"]

    query_result = (deals_collection.find({"product_image": {"$exists": False}},
                                          {"product_website": 1,
                                           "product_link": 1,
                                           "id": 1,
                                           "_id": 0}).sort("message_time_unix", -1))

    # Iterate through the results and update the product_image field
    for deal in query_result:
        # print(i["id"])
        if deal["product_website"] == "AMAZON INDIA":
            image_link = fetchAmazonImg(deal["product_link"])
            if image_link is not None:
                deals_collection.update_one({'id': deal["id"]}, {"$set": {'product_image': image_link}}, upsert=True)
            else:
                amazon_logo_link = "https://s3-symbol-logo.tradingview.com/amazon--600.png"
                image_link = amazon_logo_link
                deals_collection.update_one({'id': deal["id"]}, {"$set": {'product_image': image_link}}, upsert=True)
            print("Amazon Deal Image updated : ", image_link)

        elif deal["product_website"] == "FLIPKART INDIA":
            image_link = fetchFlipkartImg(deal["product_link"])
            if image_link is not None:
                deals_collection.update_one({'id': deal["id"]}, {"$set": {'product_image': image_link}}, upsert=True)
            else:
                flipkart_logo_link = "https://pbs.twimg.com/profile_images/1267713887165485061/WUR4QXtd_400x400.jpg"
                image_link = flipkart_logo_link
                deals_collection.update_one({'id': deal["id"]}, {"$set": {'product_image': image_link}}, upsert=True)
            print("Flipkart Deal Image updated : ", image_link)


    print("All images fetched")

if __name__ == '__main__':
    print(datetime.now())
    getImages()
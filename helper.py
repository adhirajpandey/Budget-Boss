import os
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient

# load environment variables
load_dotenv()


def connectMongo() -> object:
    try:
        # loading env variables
        cluster = os.getenv("MONGO_CLUSTER")
        user = os.getenv("MONGO_USER")
        password = os.getenv("MONGO_PASSWORD")

        # connecting with mongo db
        connectionstring = "mongodb+srv://" + user + ":" + password + "@" + cluster + ".mongodb.net/test?retryWrites=true&w=majority"

        client = MongoClient(connectionstring)

        # connecting with database
        db = client["BUDGETBOSS"]

        return db

    except:
        print("Error while connecting with mongo db")


def scrapeProductInfo_amzn(URL):
    try:
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}

        # getting page using requests module
        page = requests.get(URL, headers=header)

        # getting html content with proper formatting
        soup1 = BeautifulSoup(page.content, "html.parser")

        # defining title and price
        title = soup1.find(id='productTitle').get_text()
        price = soup1.find('span', attrs={'class': 'a-price-whole'}).get_text().replace(",", "")

        # cleaning title and price
        title = title.strip()
        price = price.strip()[:-1]
        # price = price[:-1]

        return [title, int(price)]

    except:
        return [-1, -1]


def scrapeProductInfo_flkt(URL):
    try:
        FLIPKART_API_URL = "https://flipkart.dvishal485.workers.dev/product/min/"

        # cleaning URL in required API format
        if "http" in URL:
            URL = URL.replace("https://www.flipkart.com/", "")

        elif "http" not in URL and "www" in URL:
            URL = URL.replace("www.flipkart.com/", "")

        # getting page using requests module
        page = requests.get(FLIPKART_API_URL + URL)

        # getting results in json
        product_data = page.json()

        title = product_data["name"]

        price = product_data["current_price"]

        return [title, int(price)]

    except:
        return [-1, -1]


def scrapeProductInfo_mntr(URL):
    try:
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

        page = requests.get(URL, headers=header)

        soup = BeautifulSoup(page.text, "html.parser")

        # Extract all the scripts where the data is stored
        scripts = soup.findAll("script")

        data = scripts[1].string

        # convert script data to json
        product_data = json.loads(data)

        title = product_data['name']

        price = product_data['offers']['price']

        return [title, int(price)]

    except:
        return [-1, -1]


def scrapeProductInfo_boat(URL):
    try:
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}

        page = requests.get(URL, headers=header)
        soup = BeautifulSoup(page.text, "html.parser")

        # get price and cleaned title
        price = soup.find('span', attrs={'class': 'price price--highlight price--large'}).get_text().replace(",", "")
        title = soup.find('h1', attrs={'class': 'product-meta__title heading h3'}).get_text().strip().replace("\n",
                                                                                                              "").replace(
            "\xa0", "").replace("  ", "")

        # clean price
        price = price[price.index('₹') + 1:]

        return [title, int(price)]

    except:
        return [-1, -1]

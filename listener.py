import requests
import os
import json
from bs4 import BeautifulSoup
import smtplib
import ssl
from dotenv import load_dotenv
from pymongo import MongoClient
from email.mime.text import MIMEText
from datetime import datetime

# load environment variables
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


# function to get collection from mongo db
def fetchData(col):
    return list(col.find({}, {"_id": 0}))


# function to scrape product details from amazon
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


# function to scrape product details from flipkart
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


# function to scrape product details from myntra
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


# function to scrape product details from boat
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


# funtion to mail the link
def sendMail(user_email, product_title, product_price, product_link):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv("SENDER_EMAIL_ID")
    receiver_email = [user_email]
    password = os.getenv("SENDER_EMAIL_PASSWORD")

    FROM = "Budget Boss Bot"
    SUBJECT = "ALERT!! Price Drop for your Product"

    # Read the email content from the file
    with open("email_template.txt", "r") as file:
        TEXT = file.read()

    # Replace placeholders in the email content with actual values
    TEXT = TEXT.format(product_title=product_title,
                       product_price=product_price,
                       product_link=product_link)

    # Create a MIMEText object with the email body and set the character encoding to UTF-8
    message = MIMEText(TEXT, 'html', 'utf-8')

    # Set the email headers
    message['From'] = FROM
    message['Subject'] = SUBJECT

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


# OPERATOR CODE
def main():
    # make connection with sheet db
    product_title, current_price = -1, -1
    db = connectMongo()

    # connecting with collection
    col = db["UserInfo"]

    # fetch all user data from mongo db
    data = fetchData(col)

    # iterate for every product info and send mail if price drops (0th index are column headers)
    for document in data:
        # since amazon does not always gives result in first time, we check at max 15 times
        if "amazon" in document["link"]:
            current_price = -1
            counter = 0
            while current_price == -1 and counter < 15:
                product_title, current_price = scrapeProductInfo_amzn(document["link"])
                counter = counter + 1
                # print(c)

        elif "flipkart" in document["link"]:
            product_title, current_price = scrapeProductInfo_flkt(document["link"])

        elif "myntra" in document["link"]:
            product_title, current_price = scrapeProductInfo_mntr(document["link"])

        elif "boat-lifestyle" in document["link"]:
            product_title, current_price = scrapeProductInfo_boat(document["link"])

        if (current_price < int(document["product_price"])) and (current_price != -1):
            print("Price dropped for product: ", product_title)
            sendMail(user_email=document["email"],
                     product_title=product_title,
                     product_price=current_price,
                     product_link=document["link"]
                     )
            print("Mail Sent")
        else:
            print("Price is still same for product: ", product_title, ",", current_price)


if __name__ == "__main__":
    print(datetime.now())
    main()

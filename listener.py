import requests
import os
import json
from bs4 import BeautifulSoup
import smtplib
import ssl
from dotenv import load_dotenv
from pymongo import MongoClient

#load environment variables
load_dotenv()

def connectMongo() -> object:
    try:
        #loading env variables
        cluster = os.getenv("MONGO_CLUSTER")
        user = os.getenv("MONGO_USER")
        password = os.getenv("MONGO_PASSWORD")

        #connecting with mongo db
        connectionstring = "mongodb+srv://" + user + ":" + password + "@" + cluster + ".mongodb.net/test?retryWrites=true&w=majority"

        client = MongoClient(connectionstring)

        #connecting with database
        db = client["BudgetBossDB"]

        #connecting with collection
        col = db["BudgetBoss"]

        return col
    
    except:
        print("Error while connecting with mongo db")

#function to get collection from mongo db
def fetchData(col):
    return list(col.find({}, {"_id": 0}))

#function to scrape product details from amazon
def scrapeProductInfo_amzn(URL):
    try:
        header ={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}

        #getting page using requests module
        page = requests.get(URL, headers=header)

        #getting html content with proper formatting 
        soup1 = BeautifulSoup(page.content, "html.parser")

        #defining title and price
        title = soup1.find(id='productTitle').get_text()
        price = soup1.find('span', attrs={'class':'a-price-whole'}).get_text().replace(",","")

        #cleaning title and price
        title = title.strip()
        price = price.strip()[:-1]
        # price = price[:-1]

        return [title, int(price)]
    
    except:
        return [-1, -1]

##function to scrape product details from flipkart
def scrapeProductInfo_flkt(URL):
    try:
        API_URL = "https://flipkart.dvishal485.workers.dev/product/min/"

        #cleaning URL in required API format
        if "http" in URL:
            URL = URL.replace("https://www.flipkart.com/", "")
        
        elif "http" not in URL and "www" in URL:
            URL = URL.replace("www.flipkart.com/", "")

        #getting page using requests module
        page = requests.get(API_URL+URL)

        #getting results in json
        product_data = page.json()

        title = product_data["name"]

        price = product_data["current_price"]

        return [title, int(price)]
    
    except:
        return [-1, -1]
    
#function to scrape product details from myntra
def scrapeProductInfo_mntr(URL):
    try:
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

        page = requests.get(URL, headers=header)

        soup = BeautifulSoup(page.text, "html.parser")

        #Extract all the scripts where the data is stored
        scripts = soup.findAll("script")

        data = scripts[1].string

        #convert script data to json
        product_data = json.loads(data)

        title = product_data['name']

        price = product_data['offers']['price']

        return [title, int(price)]
    
    except:
        return [-1, -1]

#funtion to mail the link
def sendMail(user_email, product_title, product_price, product_link):
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "ankitmrt1113@gmail.com"
        receiver_email = [user_email] 
        password = "jupuuefhytsxnxho"       
        FROM = f"Price Tracker Bot"
        SUBJECT = f"ALERT!! Price Drop for your Product"
        TEXT = f"""Hey User,

Price of your product which you asked us to track has dropped.

Please check the below details for the same: 

Product - {product_title}
Price - {product_price}
Link - {product_link}

Happy Shopping!!

Regards,
Price Tracker Bot"""
        
        message = 'From: {}\nSubject: {}\n\n{}'.format(FROM,SUBJECT, TEXT)
        

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


#OPERATOR CODE
def main():
    
    #make connection with sheet db
    col = connectMongo()

    #fetch data from sheet db
    data = fetchData(col)

    #iterate for every product info and send mail if price drops (0th index are column headers)
    for document in data:
        
        if "amazon" in document["link"]: 
            product_title, current_price = scrapeProductInfo_amzn(document["link"])
        
        elif "flipkart" in document["link"]:
            product_title, current_price = scrapeProductInfo_flkt(document["link"])
        
        elif "myntra" in document["link"]:
            product_title, current_price = scrapeProductInfo_mntr(document["link"])

        if (current_price < int(document["product_price"])) and (current_price != -1):
            sendMail(user_email = document["email"], product_title = product_title, product_price = current_price, product_link = document["link"])
            print("Mail Sent, Price dropped for product: ", product_title)
        else:
            print("Price is still same for product: ", product_title)
        
if __name__ == "__main__":
    main()

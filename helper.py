import os
import gspread
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

#load environment variables
load_dotenv()

def connectSheet():
    
    #google api service account key json path
    SERVICE_KEY_FILE = os.getenv("SERVICE_KEY_FILE")

    try:
        #connecting with google sheet
        gc = gspread.service_account(SERVICE_KEY_FILE)
        spreadsheet = os.getenv("SPREADSHEET")
    
        wks = gc.open(spreadsheet).sheet1

        return wks

    except:
        print("Error while connecting with google sheet")

def addData(wks, link, email, title, price):
    wks.append_row([link, email, title, price])

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

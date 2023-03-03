from helper import connectSheet
import requests
from bs4 import BeautifulSoup
import smtplib
import ssl

#function to get worksheet data form google sheet db
def fetchData(wks):
    return wks.get_all_values()

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
    wks = connectSheet()

    #fetch data from sheet db
    data = fetchData(wks)

    #iterate for every product info and send mail if price drops (0th index are column headers)
    for entity in data[1:]:
        
        if "amazon" in entity[0]: 
            product_title, current_price = scrapeProductInfo_amzn(entity[0])
        
        elif "flipkart" in entity[0]:
            product_title, current_price = scrapeProductInfo_flkt(entity[0])

        if (current_price < int(entity[3])) and (current_price != -1):
            sendMail(user_email = entity[1], product_title = product_title, product_price = current_price, product_link = entity[0])

        else:
            print("Price is still same for product: ", product_title)
        
if __name__ == "__main__":
    main()

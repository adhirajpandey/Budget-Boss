from flask import Flask, render_template, request, redirect
from helper import connectSheet, addData, scrapeProductInfo

#make connection with sheet db
wks = connectSheet()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/tracker', methods = ['GET', 'POST'])
def tracker():
    if request.method == "POST":
        
        #get data from html form
        product_link = request.form.get("plink")
        user_email = request.form.get("uemail")

        #scrape product info using multiple requests
        for i in range(3):
            product_title, product_price = scrapeProductInfo(product_link)  
            if product_price != -1:
                break
        
        #add data to sheets db
        if product_price == -1:
            #redirect to status failure
            return render_template('statusF.html')
        
        else:
            #add data and redirect to status success
            addData(wks, product_link, user_email, product_title, product_price)
            return render_template('statusS.html')


    return render_template('tracker.html')   


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
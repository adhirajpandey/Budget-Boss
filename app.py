from flask import Flask, render_template, request
from helper import connectMongo, scrapeProductInfo_amzn, scrapeProductInfo_flkt, scrapeProductInfo_mntr, scrapeProductInfo_boat
import datetime

# make connection with mongo db
db = connectMongo()

user_collection = db["UserInfo"]
deals_collection = db["Deals"]

app = Flask(__name__)


@app.route('/health')
def health():
    """Report process readiness without contacting shops or MongoDB."""
    return {"status": "ok"}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    product_title, product_price = -1, -1

    if request.method == "POST":

        # get data from html form
        product_link = request.form.get("plink")
        user_email = request.form.get("uemail")

        # Make one bounded attempt; reuse the existing failure page if it fails.
        if "amazon" in product_link:
            product_title, product_price = scrapeProductInfo_amzn(product_link)
        elif "flipkart" in product_link:
            product_title, product_price = scrapeProductInfo_flkt(product_link)
        elif "myntra" in product_link:
            product_title, product_price = scrapeProductInfo_mntr(product_link)
        elif "boat-lifestyle" in product_link:
            product_title, product_price = scrapeProductInfo_boat(product_link)
        else:
            return render_template('statusF.html')

        if product_price == -1:
            # redirect to status failure
            return render_template('statusF.html')

        else:
            user_collection.insert_one({"link": product_link,
                                        "email": user_email,
                                        "product_title": product_title,
                                        "product_price": product_price,
                                        "timestamp": datetime.datetime.now().timestamp()
                                        })

            return render_template('statusS.html')

    return render_template('tracker.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/deals')
def deals():
    query_result = deals_collection.find({"product_price": {"$not": {"$lt": 1}}}).sort("message_time_unix", -1).limit(20)
    products = [x for x in query_result]

    return render_template('deals.html', products=products)


if __name__ == '__main__':
    app.run()

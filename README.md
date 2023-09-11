# Budget-Boss

## Description
Price tracking web application that helps you save money on online e-commerce purchases. It allows you to monitor product prices and receive notifications via email when the price drops.

Currently supported E-commerce websites : Amazon, Flipkart, Myntra, Boat.

Check it out - https://budgetbossapp.azurewebsites.net//

## Working
User inputs the desired product link and email. This data along with Product Title and it's Current Price is added in the database.

The background listener.py file runs every hour and compares the current price of the product with the saved price. If the current price is less than the saved price, the bot sends a mail to the user with the required details as shown in the sample below. This listener script is scheduled using cronjob.

It is built using Python, HTML, CSS, Flask, Jinja, Bootstrap and Beautiful Soup and deployed using Microsoft Azure App Service.

Edit: To bypass 15 mins sleep timeout by Azure, `wakewebsite.sh` script is also scheduled using cron to ping webapp at regular intervals.

## Installation and Usage

1. Clone the project on your local system using: `git clone https://github.com/adhirajpandey/Budget-Boss`

2. Install the dependencies: `pip install -r requirements.txt`

3. Setup environment variables in `.env` file.

   Note : Add 'MONGO_CLUSTER', 'MONGO_USER', 'MONGO_PASSWORD' after setting up MongoDB Atlas and configure it's db to be accessed from anywhere.

4. Run the web app using `python app.py`

5. Schedule the `listener.py` file using cron or github actions.

## Utilities

- [x] Functionality for Flipkart
- [x] Functionality for Myntra
- [x] Functionality for Boat
- [ ] Notification via Whatsapp
- [x] Best Deals Section


## Samples

  ![BB_Index](https://user-images.githubusercontent.com/87516052/228626015-cbca61d9-e5b4-4303-ac5d-fa73572561c6.png)

  ![BB_Tracker](https://user-images.githubusercontent.com/87516052/228626121-6284ec09-7c40-4236-aef3-5becb6f6c307.png)

  ![BB_Email](https://user-images.githubusercontent.com/87516052/218429725-1cf1d527-71ee-442c-bdaf-7ac3bf808698.jpeg)
  
  


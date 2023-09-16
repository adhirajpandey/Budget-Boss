# Budget-Boss

## Description
Price tracking web application that helps you save money on online e-commerce purchases. It allows you to monitor product prices and receive notifications via email when the price drops. It also provides a simple web interface to stay updated with trending deals.

Currently supported E-commerce websites : Amazon, Flipkart, Myntra, Boat.

It is built using Python, HTML, CSS, Flask, Jinja, Telethon and Beautiful Soup. Currently using MongoDB as primary Database and deployed using Microsoft Azure App Service.

Apache Airflow and cronjobs are setup on personal linux machine.

Check it out - https://budgetbossapp.azurewebsites.net/

## Working
User inputs the desired product link and email. This data along with Product Title and it's Current Price is added in the database.

The background listener.py file runs every hour and compares the current price of the product with the saved price. If the current price is less than the saved price, the bot sends a mail to the user with the required details as shown in the sample below. This listener script is scheduled using cronjob.

To facilitate Deals Functionality, extract_deals.py gets most recent deals messages from telegram channel and saves them in MongoDB collection and fetch_images.py extracts images from saved deals links. Both of these scripts are scheduled using Airflow in form of DAG.

Edit: To bypass 15 mins sleep timeout by Azure, `wakewebsite.sh` script is also scheduled using cron to ping webapp at regular intervals.

## Installation and Usage

1. Clone the project on your local system using: `git clone https://github.com/adhirajpandey/Budget-Boss`

2. Install the dependencies: `pip install -r requirements.txt`

3. Setup environment variables in `.env` file.

   Notes : 
   1. Add 'MONGO_CLUSTER', 'MONGO_USER', 'MONGO_PASSWORD' after setting up MongoDB Atlas and configure it's db to be accessed from anywhere.
   2. Add 'SENDER_EMAIL_ID', 'SENDER_EMAIL_PASSWORD' after setting up app password from google 2 factor authentication settings.
   3. Add 'TG_API_ID', 'TG_API_HASH' after setting up Telegram API.

4. Run the web app using `python app.py`

5. Schedule the `listener.py` file using cron or github actions.

6. Schedule `extract_deals.py` and `fetch_images.py` using cron to populate the deals DB.

## Notes

1. You would need to authenticate your telethon client using OTP and telgram password by following on-screen instruction after running `extract_deals.py` for first time usage.

   ![tg_config](https://github.com/adhirajpandey/Budget-Boss/assets/87516052/99a62f35-159e-4af4-8f70-6e334420be67)

2. You can use `deals_dag.py` to setup schedule Airflow pipeline for latest deals and its images.
   
   ![airflow](https://github.com/adhirajpandey/Budget-Boss/assets/87516052/a9ccc1c9-65d5-40a2-9431-34d8570240dc)


## Utilities

- [x] Functionality for Flipkart
- [x] Functionality for Myntra
- [x] Functionality for Boat
- [ ] Notification via Whatsapp
- [x] Best Deals Section


## Samples

  ![index](https://github.com/adhirajpandey/Budget-Boss/assets/87516052/126b9a5e-75ed-4671-9b88-d2f09fc3e57b)

  ![tracker](https://github.com/adhirajpandey/Budget-Boss/assets/87516052/4001cead-0918-4acc-8173-7c9d0c8a4a15)

  ![deals](https://github.com/adhirajpandey/Budget-Boss/assets/87516052/625ca642-9a58-44dd-8f41-ef8e6c5b0caf)

  ![about](https://github.com/adhirajpandey/Budget-Boss/assets/87516052/aba5a01f-f862-4666-9982-99de339be7ce)

  ![email](https://github.com/adhirajpandey/Budget-Boss/assets/87516052/d1763d6b-a3d4-4562-9301-0675ee72ab73)



  
  


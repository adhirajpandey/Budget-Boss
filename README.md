# Budget-Boss

## Description
Price tracking web application that helps you save money on online e-commerce purchases. It allows you to monitor product prices and receive notifications via email when the price drops.

Currently supported E-commerce websites : Amazon, Flipkart.

Check it out - https://budgetbossapp.azurewebsites.net//

## Working
User inputs the desired product link and email. This data along with Product Title and it's Current Price is appended in the database.

The background listener.py file runs every hour and compares the current price of the product with the saved price. If the current price is less than the saved price, the bot sends a mail to the user with the required details as shown in the sample below. This listener script is scheduled using cronjob.

It is built using Python, HTML, CSS, Flask, Jinja, Bootstrap and Beautiful Soup and deployed using Microsoft Azure App Service.

Edit: To bypass 15 mins sleep timeout by Azure, `wakewebsite.sh` script is also scheduled using cron to ping webapp at regular intervals.

## Installation and Usage

1. Clone the project on your local system using: `git clone https://github.com/adhirajpandey/Budget-Boss`

2. Install the dependencies: `pip install -r requirements.txt`

3. Setup environment variables in `.env` file.

   Note : You would need to enable Google Drive API and link a google spreadsheet after sharing it with your service 
          account. Check this out for reference - [here](https://mljar.com/blog/authenticate-python-google-sheets-service-account-json-credentials/)

4. Run the web app using `python app.py`

5. Schedule the `listener.py` file using cron or github actions.

## Utilities

- [x] Functionality for Flipkart
- [ ] Functionality for Myntra
- [ ] Notification via Discord
- [ ] Best Deals Section


## Samples

  ![BB_Index](https://user-images.githubusercontent.com/87516052/218428378-b80293b3-06a4-4e16-8ec7-99bf754f405f.png)

  ![BB_Tracker](https://user-images.githubusercontent.com/87516052/218429345-b13965c3-13d1-4ee5-b17a-66d78c3dbdeb.png)

  ![BB_Email](https://user-images.githubusercontent.com/87516052/218429725-1cf1d527-71ee-442c-bdaf-7ac3bf808698.jpeg)

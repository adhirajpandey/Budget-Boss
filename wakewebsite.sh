#!/bin/bash

#To keep the website accessible and bypass 15 min sleep time of azure app service
#Scheduled using Github Actions Cron job

curl -s -v https://budgetboss.azurewebsites.net

echo "DONE"

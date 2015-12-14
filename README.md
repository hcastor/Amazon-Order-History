# Amazon-Order-History
This script is used to pull Amazon order histories from multiple accounts, and store them locally. Since I have many Amazon Prime accounts, I created this script instead of having to remember which account I used when ordering a specific item. This way I can easily retrieve information about an item, without having to rememeber which account I used.

#Usage
On the first run of getOrderHistory.py an accounts.csv file will be created. Fill this out with all your Amazon accounts. Run the script again and the created history.html will contain all of your orders. Open it up in a browser and it should look a lot like an amazon.com order history page.

#Disclaimer
amazonUI.css, and orderHistory.css are pulled from amazon.com, and are not my code. They are used by history.html to make the page look exactly like it does on amazon.com
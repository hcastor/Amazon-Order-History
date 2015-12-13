import re
import os
import json
import csv
import cStringIO
import requests
from robobrowser import RoboBrowser
from datetime import datetime

def makeHistoryFile():
	"""Creates a blank history.html file. This is the file where all the pulled order history will be stored"""
	with open(r'./history.html', 'w') as historyFile:
		header = ['<head>', 
							'    <link rel="stylesheet" type="text/css" href="./orderHistory.css">',
							'    <link rel="stylesheet" type="text/css" href="./amazonUI.css">',
							'    <base href="https://www.amazon.com/" target="_blank">',
							'</head>',
							]
		header = '\n'.join(header)
		historyFile.writelines(header)

def makeAccountFile():
	"""Makes the accounts.csv file, where you put all your amazon emails and passwords"""
	with open(r'./accounts.csv', 'w') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(['Email', 'Password', 'update(True/False)'])

def getOrderId(html):
	"""This returns the orderId line from the order html.
	I need the orderId so that I dont store an order twice.
	There isn't a straight forward way of extracting an order id from the html.
	I tried to just compare each order html to one another, but found request ids prevented that. Request ids change each time a page loads.
	I found that out by doing diff on the same order html requested twice. 
	So the only reliable way to find a order id is bellow
	"""
	storeLine = False
	linesToSkip = None
	for line in html:
		if linesToSkip:
			linesToSkip -= 1
			continue
		if storeLine:
				return line
		if 'Order #' in line:
			storeLine = True
			linesToSkip = 4

def getAccountHtml(accountEmail):
	"""This creates an account html header that is added above each order.
	This is the only thing I change/add from the html extracted from amazon.
	It is just so you can easily tell which account ordered what.
	"""

	accountHtml = ['<div class="a-box a-color-offset-background order-info"><div class="a-box-inner">',
									'<div class="a-row a-size-mini">',
								  '<span class="a-color-secondary label">',
								  '  Account ordered from',
								  '</span>',
								  '</div>',
								  '<div class="a-row a-size-base">',
								  '<span class="a-color-secondary value">',
								  accountEmail,
									'</span>',
									'</div>',
									'</div>',
									'',
								]

	return '\n'.join(accountHtml)

def main():
	"""This loops through every account in accounts.csv. Appending all their orders into 1 local html. 
	That html file uses css pulled from amazon.com so it looks the excat same, and all of the links work, except the ones that requre login.
	"""
	
	if not os.path.isfile('history.html'):
		makeHistoryFile()
	if not os.path.isfile('accounts.csv'):
		makeAccountFile()
		print 'accounts.csv file made. Fill in email/passwords and run again.'
		return 1

	with open('accounts.csv', 'rU') as csvFile:
		reader = csv.reader(csvFile)

		for row in reader:
			email = str(row[0])
			password = str(row[1])
			update = str(row[2])
			
			if update.lower() == 'true':
				#html5lib parser required for broken html on gameSplits
				s = requests.Session()
				s.headers['User-Agent'] = 'Mozilla (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7'
				browser = RoboBrowser(history=True, parser='html5lib', session=s)

				browser.open("https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin")


				form_signIn = browser.get_forms()[0]
				form_signIn['email'] = email
				form_signIn['password'] = password

				browser.submit_form(form_signIn)

				browser.open("https://www.amazon.com/gp/css/history/orders/view.html?orderFilter=year-%s&startAtIndex=1000")

				orders = browser.find_all(class_='a-box-group a-spacing-base order')

				with open(r'./history.html', 'a+') as historyFile:
					historyFile.seek(0)
					storedOrderIds = []
					tempOrder = ''
					storeLine = False
					print 'Collected orders from history.html'
					for line in historyFile:
						if line == '<!-- Start Order -->\n':
							storeLine = True
							continue
						if line == '<!-- End Order -->\n':
							storedOrderIds.append(getOrderId(cStringIO.StringIO(tempOrder)))
							tempOrder = ''
							storeLine = False
						if storeLine:
							tempOrder += line

					print 'Orders stored', len(storedOrderIds)
					print 'Find/Adding new orders for', email
					for order in orders:
						orderId = getOrderId(cStringIO.StringIO(order.__str__()))
						if not orderId in storedOrderIds:
							print 'adding order', orderId
							historyFile.write('\n<!-- Start Order -->\n')
							historyFile.write(getAccountHtml(email))
							historyFile.write(order.__str__())
							historyFile.write('\n<!-- End Order -->\n')

	print 'Done'
	
if __name__ == '__main__':
	main()
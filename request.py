import requests
import json
import csv
import time
import datetime
from pprint import pprint
from ast import literal_eval

with open("config.txt", "r") as file:
    USER = file.readline()[:-1]
    PASS = file.readline()

url = 'https://api.intrinio.com/historical_data?identifier=MSFT&sort_order=asc&item=dividend'
#url = 'https://api.intrinio.com/prices?identifier=AAPL&sort_order=asc&page_number=1'
s = requests.Session()
s.auth = (USER, PASS)
dividends = json.loads(s.get(url).text)

url = 'https://api.intrinio.com/prices?identifier=AAPL&sort_order=asc&page_number=1'
s = requests.Session()
s.auth = (USER, PASS)
r = json.loads(s.get(url).text)

#Reformat to proper dates
for entry in dividends["data"]:
    year, month, day = entry["date"].split("-")
    entry["date"] = datetime.date(int(year), int(month), int(day))


start = dividends["data"][0]["date"]
print(start)

print(start)
pprint(dividends["data"])
def dates_next(bottom_bound):
    start = dividends["data"][bottom_bound]["date"]
    window = datetime.date(start.year + 5, start.month, start.day)
    dates_ahead = []

    #Storing differences in all the dates since dividend pay outs aren't the same
    for entry in dividends["data"]:
        if entry["date"] != window:
            dates_ahead.append(str(window - entry["date"]).split(" ")[0])
    dates_ahead = list(map(lambda x: abs(int(x)), dates_ahead))
    upper_bound = dates_ahead.index(min(dates_ahead))
    return upper_bound

    #dividends["data"].append(entry)

#dividends["data"] = []
#dividends["data"] = sorted(dividends["data"], key = lambda x: x["date"])
#print(dividends["data"])
bottom_bound = 0
upper_bound = dates_next(bottom_bound)
print(upper_bound)

#Key is start, value is end
runs = {}

#All values are in months
NO_GROWTH_CUTOFF_LENGTH = 36
NEGATIVE_GROWTH_CUTOFF_LENGTH = 13

#Note: This means that when we reach the end with our bound of sliding window we will never get another run
#Also, 1825 days is 5 years
while bottom_bound < len(dividends["data"]):
    upper_bound = dates_next(bottom_bound)
    increase = dividends["data"][upper_bound]["value"] / dividends["data"][bottom_bound]["value"]
    days_off = abs(datetime.timedelta(1825) - (dividends["data"][upper_bound]["date"] - dividends["data"][bottom_bound]["date"]))
    print(days_off.days)
    #This is super arbitrary for days off, we can change this
    if increase >= 1.5 and days_off.days < 50:
        run_start = bottom_bound
        #Add whichever one is lower (should always be negative growth)
        cutoff_upper_bound = run_start + NEGATIVE_GROWTH_CUTOFF_LENGTH
        difference = NO_GROWTH_CUTOFF_LENGTH - NEGATIVE_GROWTH_CUTOFF_LENGTH
        cut = -1
        print(increase, dividends["data"][upper_bound]["date"] - dividends["data"][bottom_bound]["date"], dividends["data"][bottom_bound]["date"], dividends["data"][upper_bound]["date"])
        while run_start < len(dividends["data"]):
            #Problem here: Where do we end with either of these cutoffs? What do we do when we run out of data?
            #Check negative growth
            if cutoff_upper_bound < len(dividends["data"]):
                growth = dividends["data"][cutoff_upper_bound]["value"] / dividends["data"][run_start]["value"]
                if growth < 1:
                    #For now we start at bottom
                    cut = run_start
            #Check plateau growth
            if cutoff_upper_bound + difference < len(dividends["data"]):
                growth = dividends["data"][cutoff_upper_bound + difference]["value"] / dividends["data"][run_start]["value"]
                if growth <= 1:
                    cut = run_start
            if cut == run_start or run_start == len(dividends["data"]) - 1:
                #If we are making it to the end of the data then we put it in there too
                runs[dividends["data"][bottom_bound]["date"]] = dividends["data"][run_start]["date"]
                break
            run_start += 1
            cutoff_upper_bound += 1

    bottom_bound += 1
print(runs)
print("Pages of dividend", dividends["total_pages"])


total_pages = int(r["total_pages"])
print(total_pages)
pages_stored = []
'''
for page in range(1, total_pages + 1):
    url = 'https://api.intrinio.com/prices?identifier=AAPL&sort_order=asc&page_number={}'.format(page)
    s = requests.Session()
    s.auth = (USER, PASS)

    pages_stored.append(json.loads(s.get(url).text))
    print("Done Page")

with open("testing", "w") as file:
    for page in pages_stored:
        file.write(str(page) + "\n")
'''
with open("testing", "r") as file:
    for line in file:
        pages_stored.append(literal_eval(line))


#Simple Total return index calculation, $100 to start
tri = 100
num_stocks = None

with open('output.csv', 'w') as csvfile:
    fieldnames = ['Stock Price', 'Date', 'Split Ratio', 'Dividend Value', 'Total Return Index', 'Shares Owned']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for r in pages_stored:
        for i in r["data"]:
            #Change to proper dates
            year, month, day = i["date"].split("-")
            i["date"] = datetime.date(int(year), int(month), int(day))
            dividend = None
            if num_stocks == None:
                num_stocks = tri / i["adj_close"]
            for k in dividends['data']:
                if i['date'] == k['date']:
                    dividend = k["value"]
                    #Use the dividend received for all owned shares to buy more shares
                    num_stocks += (num_stocks * dividend) / i["adj_close"]
            #Our TRI is equal to the number of stocks we own times the stock price
            tri = num_stocks * i["adj_close"]
            writer.writerow({'Date': i["date"], 'Stock Price': i["adj_close"],
                             'Split Ratio': i["split_ratio"], 'Dividend Value': dividend,
                             'Total Return Index': tri, "Shares Owned": num_stocks})
import requests
import json
import csv
import time
import datetime
from ast import literal_eval

with open("config.txt", "r") as file:
    USER = file.readline()[:-1]
    PASS = file.readline()

url = 'https://api.intrinio.com/historical_data?identifier=AAPL&&sort_order=asc&item=dividend'
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
window = datetime.date(start.year + 5, start.month, start.day)

dates_ahead = []

#Storing differences in all the dates since dividend pay outs aren't the same
for entry in dividends["data"]:
    dates_ahead.append(str(window - entry["date"]).split(" ")[0])
    print(str(window - entry["date"]))


dates_ahead = list(map(lambda x: abs(int(x)), dates_ahead))
curr_pos = dates_ahead.index(min(dates_ahead))
print(curr_pos)

bottom_bound = 0

#Note: This means that when we reach the end with our bound of sliding window we will never get another run


'''
while curr_pos < len(dividends["data"]):
    increase = dividends["data"][curr_pos]["value"] / dividends["data"][bottom_bound]["value"]
    print(increase)
    if increase > 50:
        tri_start = bottom_bound

    bottom_bound += 1
    curr_pos += 1

'''

print("Pages of dividend", dividends["total_pages"])


total_pages = int(r["total_pages"])
print(total_pages)
pages_stored = []

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
'''

print(len(pages_stored))
#Simple Total return index calculation
tri = 100
num_stocks = None

with open('output.csv', 'w') as csvfile:
    fieldnames = ['Stock Price', 'Date', 'Split Ratio', 'Dividend Value', 'Total Return Index', 'Stocks Owned']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for r in pages_stored:
        for i in r["data"]:
            year, month, day = i["date"].split("-")
            i["date"] = datetime.date(int(year), int(month), int(day))
            dividend = None
            if num_stocks == None:
                num_stocks = tri / i["adj_close"]
            for k in dividends['data']:
                if i['date'] == k['date']:
                    dividend = k["value"]
                    print(dividend)
                    num_stocks += (num_stocks * dividend) / i["adj_close"]
            tri = num_stocks * i["adj_close"]
            writer.writerow({'Date': i["date"], 'Stock Price': i["adj_close"],
                             'Split Ratio': i["split_ratio"], 'Dividend Value': dividend,
                             'Total Return Index': tri, "Stocks Owned": num_stocks})
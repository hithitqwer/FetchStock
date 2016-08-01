# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import requests
import json
from lxml import html
from pymongo import MongoClient
import schedule
import time



def fetchcmkey():
	stockNun = '0050' #寫死一個股號
	url = 'http://www.cmoney.tw/finance/technicalanalysis.aspx?s='+stockNun
	r = requests.get(url,headers=headers,timeout=3)
	content = html.fromstring(r.text)
	result = content.xpath('//*[@class="primary-navi-now"]/a/@cmkey')
	return result[0]

def fetchHistoryData(stockNun,count):
	url = 'http://www.cmoney.tw/finance/ashx/MainPage.ashx?action=GetTechnicalData&stockId='+stockNun+'&time=d&range='+str(count)+'&cmkey='+cmkey
	headers['Referer'] = 'http://www.cmoney.tw/finance/technicalanalysis.aspx?s='+stockNun
	r = requests.get(url,headers=headers,timeout=5)
	doc = json.loads(r.text)

	for node in doc:
		node['StockNum'] = stockNun;

	return doc

def fetchDayData(stockNun):
	stockData = []
	for item in fetchHistoryData(stockNun,1):
		stockData.append(item)	
	return stockData[len(stockData)-1]

def fetchRealTime(stockNuns):
	if len(stockNuns) != 0:

		session = requests.Session()
		session.get('http://mis.twse.com.tw/stock/fibest.jsp?stock='+stockNuns[0],headers=headers,timeout=3) # get web session

		queryList = map(lambda x:'tse_'+x+'.tw',stockNuns)
		jsonURL = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch='+('|'.join(queryList))
		content = session.get(jsonURL,headers=headers,timeout=3)
		doc = json.loads(content.text)

		stockResult = []
		for realTimedata in doc['msgArray']:
			stockResult.append(realTimedata)
		return stockResult
	else:
		return []

# for x in fetchRealTime(['2330']):
# 	print 'Name:',x['n']

# stockNum:parseBodyData['msgArray'][i]['c'],
# stockDealPrice:parseBodyData['msgArray'][i]['pz'],
# stockHigh:parseBodyData['msgArray'][i]['h'],
# stockLow:parseBodyData['msgArray'][i]['l'],
# stockOpen:parseBodyData['msgArray'][i]['o'],
# stockName:parseBodyData['msgArray'][i]['n'],
# stockDate:parseBodyData['msgArray'][i]['d']


def insertToBDHistoryData(stockNun,count):
	ExistCount = collect.find({'StockNum':stockNun}).count()
	if ExistCount == 0:
		collect.insert_many(fetchHistoryData(stockNun,count))
		print 'Stock %s is inserted. count=%d' % (stockNun,count)
	else:
		print 'Stock %s has been insert to BD.' % (stockNun)

def insertToBDSingleData(stockNun):
	StockItem = fetchDayData(stockNun)

	Date = StockItem['Date']
	Num = StockItem['StockNum']
	ExistCount = collect.find({'Date':Date,'StockNum':Num}).count()
	if ExistCount == 0:
		collect.insert_one(fetchDayData(stockNun))
		print 'Stock %s is inserted.' % (stockNun)
	else:
		print 'Stock %s has been insert to BD.' % (stockNun)

def init():
	global headers
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'}
	
	global cmkey
	cmkey = fetchcmkey()

	
	

init()
print fetchDayData('0050')

# re範例
# content.xpath("//td[re:match(text(),'^[0-9]+')]", namespaces={"re": "http://exslt.org/regular-expressions"}) 

# for x in collect.find({'StockNum':'2330','ClosePr':{'$gt':156}}):
# 	print '%s %s %f' % (x['StockNum'],x['Date'],x['ClosePr'])

# print collect.find({'ClosePr':{'$gt':50}}).distinct('StockNum')

# insertToBDHistoryData('2330',10)
# insertToBDSingleData('2356')
# stocklist = ['2313','0050']
# print fetchRealTime(stocklist)

# stockNum:parseBodyData['msgArray'][i]['c'],
# stockDealPrice:parseBodyData['msgArray'][i]['pz'],
# stockHigh:parseBodyData['msgArray'][i]['h'],
# stockLow:parseBodyData['msgArray'][i]['l'],
# stockOpen:parseBodyData['msgArray'][i]['o'],
# stockName:parseBodyData['msgArray'][i]['n'],
# stockDate:parseBodyData['msgArray'][i]['d']


# Schedule Control example
# schedule.every().day.at("16:05").do(function)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
import scrapy
import pandas as pd
import os
import shutil
from datetime import datetime
import pandas as pd
from pandas.core.indexes.base import Index
from tabulate import tabulate
import datetime
from xlsxwriter import Workbook

print('It is working. Please wait...')

class KalimatiSpider(scrapy.Spider):
    name = 'kalimati'

    def start_requests(self):
        yield scrapy.Request(url='https://kalimatimarket.gov.np/lang/en', dont_filter = True)

        # yield scrapy.Request(url='https://kalimatimarket.gov.np/lang/{0}'.format(self.language))

    def parse(self, response):
        for item in response.xpath('//tbody/tr'):
            name = item.xpath('.//td[1]/text()').get()
            unit = item.xpath('.//td[2]/text()').get()
            min_price = item.xpath('.//td[3]/text()').get()
            max_price = item.xpath('.//td[4]/text()').get()
            avg_price = item.xpath('.//td[5]/text()').get()

            if min_price[-1] in ['0','1','2','3','4','5','6','7','8','9']:
                yield {"English Name": name,
                "Nepali Name": '',
                "Unit": unit,
                "Minimum Price": min_price,
                "Maximum Price": max_price,
                "Average Price": avg_price,
                "Language": 'kalimatiE'}
            else:
                yield {"Nepali Name": name,
                "Unit": unit,
                "Minimum Price": min_price,
                "Maximum Price": max_price,
                "Average Price": avg_price,
                "Language": 'kalimatiN'}
        
        yield scrapy.Request(url='https://kalimatimarket.gov.np/lang/ne')


# this block makes it possible to do cleaning and analysing on this python file itself. This block makes sure that the code below this block are executed normally.
# This block makes it possible to run this python file from within the terminal like usual unlike something like 'scrapy crawl xxxx'
from scrapy.crawler import CrawlerProcess
c = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    'FEED_FORMAT': 'csv',
    'FEED_URI': 'kalimati.csv',})
c.crawl(KalimatiSpider)
c.start()

os.chdir('/Users/birajaryal/virtual_workspace/vegetables/')

#running the cleaning file
clean = os.path.join(os.getcwd(), 'cleaning.py')
os.system('{} {}'.format('python', clean))
print('Cleaning process executed')

#running the analysis file
analyze = os.path.join(os.getcwd(), 'data_analysis.py')
os.system('{} {}'.format('python', analyze))
print('Analyzing process executed')

input("Press Enter to exit: ")
                # 3 Steps
# Run in the terminal this way: python /Users/birajaryal/virtual_workspace/vegetables/vegetables/spiders/kalimati.py
# Below was previously needed but now, all the below are run automatically in this file. 

# Run the cleaning.py file.
# Obtain the cleaned data inside daily folder
# Analyse the data using the data_analysis.py file, and obtain the daily analysis in its own folder 
    






            




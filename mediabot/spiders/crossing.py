# -*- coding: utf-8 -*-
import scrapy
import json
import urlparse
import subprocess
import os.path
from time import gmtime, strftime

class CrossingSpider(scrapy.Spider):
    name = "crossing"
    start_urls = [
        'https://crossing.cw.com.tw/blogIndividual.action?id=678',
    ]

    def __init__(self):
        self.directory = 'crossing'
        if not os.path.exists(self.directory):
           os.mkdir(self.directory)

    def parseArticle(self, response):
        articleTitle = response.css('h1.article-page-title.serif::text').extract_first().strip().replace('/', '-')
        viewNumber = response.css('span.browse').extract_first().split('\n')[2].strip()
        articleDate = response.css('span.date::text').extract_first().strip().replace('/', '-')
        now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        # to process it in the pipeline may be better, but I want to just deal with it here

        filePath = self.directory + '/' + articleDate + '_' + articleTitle + '.csv'
        if not os.path.isfile(filePath):
            with open(filePath, 'wb') as w:
                w.write('date, view_number\n')

        with open(filePath, 'a') as w:
            w.write(now)
            w.write(', ')
            w.write(viewNumber)
            w.write('\n')

    def parse(self, response):
        haveCard = False
        # print(response.body)
        for card in response.css('div.card'):
            haveCard = True

            articleLink = card.css('a::attr("href")').extract_first()

            yield scrapy.Request(url=articleLink, callback=self.parseArticle)


        if haveCard:
            if 'pageNumber' not in response.meta:
                pageNumber = 1
            else:
                pageNumber = response.meta['pageNumber']

            nextPage = self.start_urls[0] + '&page=' + str(pageNumber + 1)
            yield scrapy.Request(nextPage, callback=self.parse, meta={'pageNumber' : pageNumber + 1})

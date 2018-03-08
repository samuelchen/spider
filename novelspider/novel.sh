#!/usr/bin/env sh

nohup scrapy crawl novel -s JOBDIR=./.scrapy-stat/novel-1 >novel.log &
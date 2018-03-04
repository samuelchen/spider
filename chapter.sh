#!/usr/bin/env sh

nohup scrapy crawl chapter -s JOBDIR=./.scrapy-stat/chapter-1 > chapter.log &

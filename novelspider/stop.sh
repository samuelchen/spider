#!/usr/bin/env sh

ps -ef|grep scrapy|grep -v grep|awk '{print $2}'|xargs kill -s SIGINT
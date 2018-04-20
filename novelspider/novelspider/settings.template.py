# -*- coding: utf-8 -*-

# Scrapy settings for novelspider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html


##########################################
#
#  copy to setting.py for local use.
#
##########################################

import os
import socket
import logging
LOG_LEVEL = logging.INFO

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# BOT_NAME = 'GoDuckDuck'

SPIDER_MODULES = ['novelspider.spiders']
NEWSPIDER_MODULE = 'novelspider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'novelspider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    # "User-Agent": random.choice(USER_AGENTS),
    "Accept-Encoding": "gzip,deflate,sdch",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2",
    }
# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'novelspider.middlewares.NovelspiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'novelspider.middlewares.NovelspiderDownloaderMiddleware': 543,
    'novelspider.middlewares.RotateUserAgentMiddleware': 300,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'novelspider.pipelines.NovelspiderAlbumPipeline': 30,
    'novelspider.pipelines.NovelspiderDBPipeline': 300,
}
IMAGES_STORE = os.path.join(BASE_DIR, 'albums')
IMAGES_URLS_FIELD = 'album'
IMAGES_RESULT_FIELD = 'album_down'
IMAGES_EXPIRES = 365 * 10


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_GZIP = True


# --------- customized settings ----------

# DB connection string
# http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
# format: driver://user:pass@host:port/database
# e.g.
# SQLITE3: sqlite:///path/to/database.db
# SQLITE3 in memory: sqlite://  (with nothing) or sqlite:///memory:
# MYSQL: mysql://scott:tiger@localhost/test
# MYSQL with driver and charset: mysql+pymysql://scott:tiger@localhost/test?charset=utf8mb4
# MYSQL with driver and charset: mysql+mysqldb://scott:tiger@localhost/test?charset=utf8&use_unicode=0
# POSTGRESQL: postgresql://scott:tiger@localhost/test
# POSTGRESQL with driver and domain: postgresql+psycopg2://user:password@/dbname
# POSTGRESQL with driver and domain: postgresql+psycopg2://user:password@/dbname?host=/var/lib/postgresql
# DB_CONNECTION_STRING='postgresql://scott:tiger@localhost/test'
DB_CONNECTION_STRING = 'sqlite:///' + os.path.join(BASE_DIR, 'novel.sqlite3')
# DB_CONNECTION_STRING='postgresql://localhost/'

# host name & IP. for distributed spiders
HOSTNAME = socket.gethostname()
SPIDER_ID = HOSTNAME

# how many index pages will be crawled for obtain novels (novel spider)
LIMIT_INDEX_PAGES = 1
# how many novels will be crawled for obtain chapters (novel chapters)
LIMIT_NOVELS = 1
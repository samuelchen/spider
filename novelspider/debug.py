from scrapy.cmdline import execute
import sys
# import os

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

name = sys.argv[1]
execute(['scrapy', 'crawl', name])
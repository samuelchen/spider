novelspider
===========

spider for piaotian[dot]com

* for home links
`scrapy crawl home`

* for all novel links
`scrapy crawl novel`

* for novel chapters
`scrapy crawl chapter`

* use states for remember downloaded
`scrapy crawl chapter -s JOBDIR=./path/to/state/novel-1

* to read novels
run `python readnovel.py 8080`
then browse http://localhost:8080
if port is not specified, 8080 will be default.

* to debug in IDE
  * add file `debug.py` with content
  ```python
      from scrapy.cmdline import execute
      import sys
  
      execute(['scrapy', 'crawl', *sys.argv[1:]])
  ```
  * In IDE, set start script as `debug.py`
  
* scrapy crawl run with arguments
    
    run `spider crawl` as `spider crawl -a arg1 -a arg2=345 -a arg3=abc spider_name`
    
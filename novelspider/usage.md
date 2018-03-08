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
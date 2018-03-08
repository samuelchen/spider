#!/usr/bin/env sh

BASE_PATH=$(cd `dirname $0`; pwd)
echo "BASE_PATH is ${BASE_PATH}."

cd ${BASE_PATH}
#echo ">> ${PWD}"
mkdir -p log
nohup scrapy crawl novel -s JOBDIR=./.scrapy-stat/novel-1 > log/novel.log &
cd -
#echo "<< ${PWD}"

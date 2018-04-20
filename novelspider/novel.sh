#!/usr/bin/env sh

BASE_PATH=$(cd `dirname $0`; pwd)
echo "BASE_PATH is ${BASE_PATH}."

DT=`date +'%y%m%d%H'`
cd ${BASE_PATH}
#echo ">> ${PWD}"
mkdir -p log
nohup scrapy crawl novel > log/novel${DT}.log &
cd -
#echo "<< ${PWD}"

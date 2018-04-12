#!/user/bin/env sh

CWD=$PWD
cd ~/spider/novelspider
git pull
cd log
mv chapter.log `cat chapter_novels.log`
tail `cat chapter_novels.log`
cd ..
source ~/venv/py3/bin/activate
export DJANGO_SETTINGS_MODULE=settings.dev
sh chapter.sh
ps -ef|grep scrapy|grep -v grep
cd $CWD
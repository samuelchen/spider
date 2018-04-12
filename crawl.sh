#!/user/bin/env sh

CWD=$PWD
cd ~/spider/novelspider
git pull
cd log
if [ -e chapter.log ]; then
  mv chapter.log `cat chapter_novels.log`
  tail `cat chapter_novels.log`
fi
cd ..
source ~/venv/py3/bin/activate
# export DJANGO_SETTINGS_MODULE=settings.dev
sh chapter.sh
ps -ef|grep scrapy|grep -v grep
cd $CWD
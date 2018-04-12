#!/user/bin/env sh

CWD=$PWD
cd ~/spider/novelreader
git pull
source ~/venv/py3/bin/activate
export DJANGO_SETTINGS_MODULE=settings.dev
python manage.py runserver 0.0.0.0:9999
cd $CWD
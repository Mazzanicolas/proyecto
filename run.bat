@echo off
start redis-latest/redis-server
start elcelery.bat
git pull origin prod -f
python manage.py makemigrations app
python manage.py migrate
python manage.py runserver

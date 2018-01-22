@echo off
git pull origin prod
python manage.py runserver

@echo off
python manage.py makemigrations app
python manage.py migrate
python manage.py runserver

set FORKED_BY_MULTIPROCESSING=1
start redis-latest/redis-server
start Celery -A proyecto worker -Q CalculationQueue --max-memory-per-child=150000 -E 
start Celery -A proyecto worker -Q delegate --max-tasks-per-child=1 -E -n Worker2 
python manage.py runserver --insecure

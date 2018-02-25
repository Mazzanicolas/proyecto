celery -A proyecto worker -Q delegate --concurrency 2 --max-tasks-per-child=1 -E -n july

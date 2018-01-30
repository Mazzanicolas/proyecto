@echo off
set FORKED_BY_MULTIPROCESSING=1
Celery -A proyecto worker -l info

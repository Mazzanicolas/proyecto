@echo off
prompt $t$g
set FORKED_BY_MULTIPROCESSING=1
Celery -A proyecto worker -Q delegate --max-tasks-per-child=1 -E -n Worker2

@echo off
prompt $t$g
set FORKED_BY_MULTIPROCESSING=1
Celery -A proyecto worker -Q CalculationQueue --max-memory-per-child=150000 -E

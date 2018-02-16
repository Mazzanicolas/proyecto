@echo off
set FORKED_BY_MULTIPROCESSING=1
Celery -A proyecto worker -Q CalculationQueue,delegate

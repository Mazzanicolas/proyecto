set FORKED_BY_MULTIPROCESSING=1
celery -A proyecto worker -Q CalculationQueue,delegate

celery -A proyecto worker -Q CalculationQueue,delegate --concurrency 2

from datetime import datetime, timedelta
def horaMilToDateTime(hora):
    return datetime(2013,3,10,hour = int(hora[:2]),minute = int(hora[-2:]))

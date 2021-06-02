from datetime import datetime

def epoch_to_date(epoch_date: str):
    return datetime.fromtimestamp(float(epoch_date) / 1000)
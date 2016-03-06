import datetime

#
def get_date_span(date, before, after, format_str='%Y%m%d'):
    the_date = datetime.datetime.strptime(date, format_str)
    start = (the_date-datetime.timedelta(days = before)).strftime(format_str)
    end = (the_date+datetime.timedelta(days = after)).strftime(format_str)
    return start, end

#to get all dates between begin and end
def get_date_range(begin, end):
    bd = datetime.datetime.strptime(begin, "%Y%m%d")
    ed = datetime.datetime.strptime(end, "%Y%m%d")
    if bd > ed:
        raise ValueError("Begin date older than end date")
    delta = datetime.timedelta(days=1)
    dates = []
    while bd <= ed:
        if bd.weekday() < 5:
            dates.append(bd.strftime("%Y%m%d"))
        bd += delta
    return dates

def get_previous_dates(date, days):
    dates = []
    i = 1
    today = date
    while i <= days:
        today = today - datetime.timedelta(1)
        if today.weekday() < 5:
            dates.append(today)
            i+= 1
    return dates

def get_following_dates(date, days, inclusive = True):
    if inclusive:
        dates = [date]
    else:
        dates = []
    today = date
    i = 1
    while i <= days:
        today = today + datetime.timedelta(1)
        if today.weekday() < 5:
            dates.append(today)
            i+= 1
    return dates

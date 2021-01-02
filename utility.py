from dateutil.parser import parse
from dateutil import tz

#example: '2020-10-28T06:14:11.2469379+00:00'
def tolocalTimeString(dateString):
    dt = parse(dateString)
    new_ts = dt.astimezone(tz.tzlocal())
    #print(new_ts.tzname()) #Show time zone
    return str(new_ts.date()) + ' ' + str(new_ts.time().strftime('%H:%M'))

#print(tolocalTimeString('2020-10-28T06:14:11.2469379+00:00'))
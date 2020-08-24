import datetime
from math import ceil

print(datetime.date.today().timetuple())

print(datetime.date.today().isoweekday())

def first_monday():
    for i in range(0, 366):
        start_date = datetime.date(year=datetime.datetime.today().year, month=1, day=1)
        end_date = start_date + datetime.timedelta(days=i)
        if end_date.timetuple().tm_wday == 0:
            return i
fm = first_monday()
for i in range(0+fm, 365-fm):
    end_date = datetime.date(year=datetime.datetime.today().year, month=1, day=1) + datetime.timedelta(days=i)
    print(end_date)
    print(f"this {(ceil((end_date.timetuple().tm_yday - first_monday())/7))%2}")


print(datetime.date.today().timetuple().tm_yday)

def AB(date):
    d = datetime.date.strftime(date)
    print('A' if (ceil((end_date.timetuple().tm_yday - first_monday())/7))%2 else 'B')
    
print(f"A OR B : {AB('24/08/2020')}")
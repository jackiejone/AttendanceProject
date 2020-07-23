import datetime

# Script for figuring out if a day is on Week A or Week B ()
weeks = {'A':[], 'B':[]}
AB = 'A'
week_num = 1
for i in range(1, 356):
    date = datetime.timedelta(days=i)
    start_date = datetime.date(2019, 12, 31)
    end_date = start_date + date
    if end_date.isoweekday() in [1, 2, 3, 4, 5]:
        weeks[AB].append((week_num, end_date))
        if end_date.isoweekday() == 5 and AB == 'A':
            AB = 'B'
            week_num += 1
        elif end_date.isoweekday() == 5 and AB == 'B':
            AB = 'A'
            week_num += 1

print(weeks)
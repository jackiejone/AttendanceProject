import datetime

print((datetime.date.today() + datetime.timedelta(days=3)).isoweekday())
print((datetime.date.today() + datetime.timedelta(days=3)))
print((datetime.date.today()).isoweekday())
import datetime

dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(8)]
dates = [date.strftime("%d-%m-%Y") for date in dates]

# From 23-07 to 30-07
hours = ["10:00", "11:30", "13:00"]

DB = {}
for date in dates:
    DB[date] = {}
    for hour in hours:
        DB[date][hour] = {
            "available": True,
            "owner": None,
            "confirmed": False
        }

DB['24-07-2023']['10:00'] = {'available': False, 'owner': 'OWNER1', 'confirmed': True}
DB['24-07-2023']['11:30'] = {'available': False, 'owner': 'OWNER2', 'confirmed': True}
DB['24-07-2023']['13:00'] = {'available': False, 'owner': 'OWNER3', 'confirmed': True}

print(DB)
import datefinder

def extract_dates(text):
    dates = []
    matches = datefinder.find_dates(text)
    for match in matches:
        formatted_date = match.strftime("%d-%m-%Y")
        dates.append(formatted_date)
    return dates

# Example usage
text = "The deadline for submission is the 17 friday"
dates = extract_dates(text)
print(dates)

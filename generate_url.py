import requests
import urllib.parse

task = "The file ./data/dates.txt contains a list of dates, one per line. Count the number of Wednesdays in the list, and write just the number to ./data/dates-wednesdays.txt"
encoded_task = urllib.parse.quote(task)

url = f"http://localhost:8000/run?task={encoded_task}"
# response = requests.post(url)

print(url)

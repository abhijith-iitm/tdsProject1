import requests
import urllib.parse
', and write just the number to ./data/dates-wednesdays.txt'
task = "The file ./data/dates.txt contains a list of dates, one per line. Count the number of Wednesdays in the list"
path = "./data/comments-similar.txt"
encoded_task = urllib.parse.quote(task)

url = f"http://localhost:8000/run?task={encoded_task}"
# url = f"http://localhost:8000/read?path={path}"
# response = requests.post(url)

print(url)

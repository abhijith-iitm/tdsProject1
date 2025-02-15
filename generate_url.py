import requests
import urllib.parse
', and write just the number to ./data/dates-wednesdays.txt'
# task = "List the files in ./data and write them down in ./data/files.txt"
# task = "List all files in the ./data directory and write them into a file called ./data/temp.txt"
# task = "Sort the array of contacts in ./data/contacts.json by last_name, then first_name, and write the result to ./data/contacts-sorted1.json"
# task = "Count the no. of Wednesdays in the file dates.txt inside the ./data folder and write the count into ./data/date-wednesdays1.txt"
task = """Find all Markdown (.md) files in ./data/docs/. For each file, extract the first occurrance of each H1 (i.e. a line starting with # ). Create an index file ./data/docs/index.json that maps each filename (without the ./data/docs/ prefix) to its title (e.g. {"README.md": "Home", "path/to/large-language-models.md": "Large Language Models", ...})"""
# task = "./data/credit-card.png contains a credit card number. Pass the image to an LLM, have it extract the card number, and write it without spaces to ./data/credit-card1.txt"

path = "./data/comments-similar.txt"
encoded_task = urllib.parse.quote(task)

url = f"http://localhost:8000/run?task={encoded_task}"
# url = f"http://localhost:8000/read?path={path}"
# response = requests.post(url)

print(url)

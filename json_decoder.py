import json

# Load the JSON file
with open('json/sample.json', 'r') as file:
    data = json.load(file)

# Convert the depth_data string to a dictionary
for item in data['book_pages']:
    if 'page_content' in item:
        item['page_content'] = json.loads(item['page_content'])

# Optionally, save the modified data back to the JSON file
with open('json/json.json', 'w') as file:
    json.dump(data, file, indent=4)
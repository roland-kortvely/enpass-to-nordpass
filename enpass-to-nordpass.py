import json
import csv
import sys
import os
import re

def is_valid_url_or_domain(url):
    # Regular expression to check if the string is a domain or URL format
    regex = re.compile(
        r'^(https?://)?'  # http:// or https:// (optional)
        r'([\da-z\.-]+)\.'  # domain part (e.g., spotify)
        r'([a-z\.]{2,6})'  # extension part (e.g., .com)
        r'([/\w \.-]*)*$', re.IGNORECASE)  # path (optional)
    return re.match(regex, url) is not None

def convert_enpass_to_nordpass(enpass_file, nordpass_file):
    # Check if Enpass file exists
    if not os.path.exists(enpass_file):
        print(f"Error: '{enpass_file}' does not exist.")
        sys.exit(1)

    with open(enpass_file, 'r') as file:
        enpass_data = json.load(file)

    nordpass_data = []

    for item in enpass_data['items']:
        title = item.get('title', '')
        # Initialize fields with default values
        nordpass_entry = {
            'name': title,
            'url': '',
            'username': '',
            'password': '',
            'note': item.get('note', ''),
            'folder': 'imported_from_enpass',
            'cardholdername': '',
            'cardnumber': '',
            'cvc': '',
            'expirydate': '',
            'zipcode': '',
        }

        # Mapping Enpass fields to NordPass
        for field in item.get('fields', []):
            label = field.get('label', '').lower()
            value = field.get('value', '')
            if label in ['username', 'používateľské meno']:
                nordpass_entry['username'] = value
            elif label in ['password', 'prihlasovacie heslo']:
                nordpass_entry['password'] = value
            elif label in ['url', 'webová stránka']:
                nordpass_entry['url'] = value if value else (title if is_valid_url_or_domain(title) else '')
            elif label in ['držiteľ karty', 'cardholder name']:
                nordpass_entry['cardholdername'] = value
            elif label in ['číslo', 'card number', 'cardnumber']:
                nordpass_entry['cardnumber'] = value
            elif label in ['cvc', 'ccCvc']:
                nordpass_entry['cvc'] = value
            elif label in ['dátum platnosti', 'expiry date', 'expirydate']:
                nordpass_entry['expirydate'] = value

        if not nordpass_entry['url']:
            nordpass_entry['url'] = title if is_valid_url_or_domain(title) else ''

        nordpass_data.append(nordpass_entry)

    # Overwrite or create NordPass CSV
    with open(nordpass_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=nordpass_data[0].keys())
        writer.writeheader()
        writer.writerows(nordpass_data)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <enpass_json_file> <nordpass_csv_file>")
        sys.exit(1)

    enpass_file = sys.argv[1]
    nordpass_file = sys.argv[2]

    convert_enpass_to_nordpass(enpass_file, nordpass_file)
    print("Conversion complete.")


import requests
from bs4 import BeautifulSoup #this script is not using BeautifulSoup to scrape data, but only to parse it. The data is fetched using the requests library.
import csv
import os
import re
import unicodedata

def fetch_html(url):
    response = requests.get(url)
    try:
        response.raise_for_status()  # Raise HTTPError for bad request
        print(f"HTTP request successful")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP request failed. Status code: {response.status_code}. Error: {e}")
    return response.text

def parse_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'wikitable sortable'})
    if table:
        print("Table found in the HTML")
    else:
        print("No table found with that class, check the HTML")
    return table


# using several unfamiliar functions, thus extensive comments
def clean_text(text): 
    # Normalize Unicode characters to remove accents and similar crap
    text = unicodedata.normalize('NFKD', text)
    # Remove all text within square brackets to remove citations/references
    text = re.sub(r'\[.*?\]', '', text)
    # Replac non-standard characters
    text = re.sub(r'\xa0', ' ', text)  # non-breaking spaces
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  #non-ASCII characters
    # Encode and decode to handle/remove non-UTF8 characters
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    return text.strip()  # Strip leading/trailing whitespace juuuust in case


def process_table(table):
    print("Starting to process table...")
    headers = [clean_text(th.get_text(strip=True)) for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr'):
        cols = [clean_text(td.get_text(strip=True)) for td in tr.find_all('td')]
        if cols:  # Ensure the row has data
            rows.append(cols)
    print("Table processing complete!!!")
    return [headers] + rows  # Include headers as the first row

def save_to_csv(data, file_path):
    print(f"File path: {file_path}")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    print(f"Data successfully saved to CSV at {file_path}")

def main():
    # separate the URL stem from the query to allow for use in other ways (LLM search)
    site_url_stem = "https://en.wikipedia.org/wiki/"
    query = "transistor count"

    formatted_query = query.replace(" ", "_")  # Replace spaces with underscores for URL
    url = site_url_stem + formatted_query
    output_path = os.path.join(os.getcwd(), f"{formatted_query}.csv")

    print(f"Constructed URL: {url}")
    html = fetch_html(url)
    table = parse_table(html)
    
    if table is not None:
        table_data = process_table(table)
        save_to_csv(table_data, output_path)
        print("All operations completed successfully.")
    else:
        print("No data to save. Exiting program.")

if __name__ == "__main__":
    main()

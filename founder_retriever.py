import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse

# Function to fetch data from Crunchbase API
def fetch_from_crunchbase_api(company_name, api_key):
    company_name_encoded = urllib.parse.quote(company_name.lower().replace(" ", "-"))
    url = f"https://api.crunchbase.com/v3.1/organizations/{company_name_encoded}"
    headers = {'Authorization': f'Bearer {api_key}'}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Fetching data for {company_name} from Crunchbase API...")  # Debugging print
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")  # Debugging print to see raw JSON
            founders = data.get('data', {}).get('relationships', {}).get('founders', {}).get('items', [])
            founder_names = [f"{founder['properties']['first_name']} {founder['properties']['last_name']}" for founder in founders]
            return ', '.join(founder_names) if founder_names else None
        else:
            print(f"Failed to fetch data for {company_name}, status code: {response.status_code}")  # Debugging print
    except Exception as e:
        print(f"Error fetching data from Crunchbase for {company_name}: {e}")
    
    return None

# Function to scrape data from websites if API fails
def scrape_founder(company_name):
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(company_name)}+founder"
    
    try:
        response = requests.get(search_url)
        print(f"Scraping data for {company_name}...")  # Debugging print
        soup = BeautifulSoup(response.text, 'html.parser')
        snippet = soup.find('div', class_='BNeawe s3v9rd AP7Wnd')
        print(f"Scraped snippet: {snippet.text if snippet else 'No data found'}")  # Debugging print
        return snippet.text if snippet else None
    except Exception as e:
        print(f"Error scraping data for {company_name}: {e}")
    
    return None

# Main function to handle the process
def main(input_csv, output_csv, api_key):
    print(f"Reading input CSV: {input_csv}")  # Debugging print
    df = pd.read_csv(input_csv)
    results = []
    
    for company in df['CompanyName']:
        print(f"Processing {company}...")  # Debugging print
        founder = fetch_from_crunchbase_api(company, api_key)
        
        if not founder:  # Fallback to scraping
            print(f"Fallback to scraping for {company}...")  # Debugging print
            founder = scrape_founder(company)
        
        results.append({'CompanyName': company, 'FounderName': founder or 'Not Found'})
        print(f"Result: {company} - {founder or 'Not Found'}")  # Debugging print

    print(f"Writing results to output CSV: {output_csv}")  # Debugging print
    with open(output_csv, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['CompanyName', 'FounderName'])
        writer.writeheader()
        writer.writerows(results)

    print("Script execution completed.")  # Final print to confirm completion

# Execute the script
if __name__ == "__main__":
    main("input.csv", "output.csv", "your_api_key_here")

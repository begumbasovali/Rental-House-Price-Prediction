import requests 
from bs4 import BeautifulSoup
import csv
import time
import random

# Create the CSV file
csv_file = 'emlakjet_bursa_kiralik_daire_linkleri.csv'
headers = ['Link']

with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

# Total number of pages to scrape
total_pages = 50
base_url = 'https://www.emlakjet.com/kiralik-daire/bursa'

# User-Agent information
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

total_links = 0

# Loop through each page
for page in range(1, total_pages + 1):
    try:
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page}"
        
        print(f"Processing page {page}: {url}")
        
        # Fetch the page
        response = requests.get(url, headers=headers)
        
        # Check if HTTP request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing cards
            listing_cards = soup.select('div._3qnt9._36SwK a')
            
            if not listing_cards:
                # Try alternative HTML structures
                listing_cards = soup.select('a[href*="/ilan/"]')
                
            if not listing_cards:
                print(f"No listings found on page {page}. Trying a different selector.")
                listing_cards = soup.find_all('a', href=lambda href: href and '/ilan/' in href)
            
            # If page is empty or no links found
            if not listing_cards:
                print(f"No listings found on page {page} or the page structure may have changed.")
                continue
                
            page_link_count = 0
            
            # Loop through each listing
            with open(csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                for listing in listing_cards:
                    # Create full URL
                    link = listing.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = 'https://www.emlakjet.com' + link
                        
                        # Write to CSV
                        writer.writerow([link])
                        page_link_count += 1
            
            total_links += page_link_count
            print(f"Extracted {page_link_count} links from page {page}. Total: {total_links}")
            
            # Wait to avoid overloading the server
            time.sleep(random.uniform(1.0, 3.0))
            
        else:
            print(f"Could not fetch page {page}. Error code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred while processing page {page}: {str(e)}")
        # Wait a bit in case of error and continue
        time.sleep(5)
        continue

print(f"Process completed! Total of {total_links} links saved to the CSV file.")

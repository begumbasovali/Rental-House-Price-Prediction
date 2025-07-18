import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import os
from datetime import datetime

# Headers for browser emulation
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
}

def read_listing_urls(csv_file):
    """
    Read listing URLs from the CSV file.
    """
    urls = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row and row[0]:  # Make sure there's a URL
                    urls.append(row[0])
        print(f"Read {len(urls)} URLs from {csv_file}")
        return urls
    except Exception as e:
        print(f"Error reading URLs from {csv_file}: {e}")
        return []

def extract_price(soup):
    """Extract the price from the listing"""
    try:
        price_element = soup.select_one('.price-container .price-share')
        if price_element:
            price_text = price_element.get_text(strip=True).replace('₺', '').strip()
            return price_text
    except Exception as e:
        print(f"Error extracting price: {e}")
    return None

def extract_location(soup):
    """Extract the location from the listing"""
    try:
        location_element = soup.select_one('.breadcrumbs')
        if location_element:
            return location_element.get_text(strip=True)
    except Exception as e:
        print(f"Error extracting location: {e}")
    return None

def extract_property_features(soup):
    """Extract all property features from the listing"""
    features = {}
    
    try:
        # Extract data from the first slide (main details)
        property_lists = soup.select('.spotlight-props .swiper-slide ul')
        
        for property_list in property_lists:
            list_items = property_list.select('li')
            
            for item in list_items:
                key_element = item.select_one('strong')
                value_element = item.select_one('span')
                
                if key_element and value_element:
                    key = key_element.get_text(strip=True)
                    value = value_element.get_text(strip=True)
                    features[key] = value
        
        # Extract coordinates if available
        map_div = soup.select_one('div#map')
        if map_div:
            lat = map_div.get('data-lat')
            lng = map_div.get('data-lng')
            if lat and lng:
                features['Latitude'] = lat
                features['Longitude'] = lng
                
    except Exception as e:
        print(f"Error extracting property features: {e}")
    
    return features

def scrape_listing_details(url):
    """
    Scrape details from a single listing.
    """
    print(f"Scraping details from: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data points
        listing_data = {
            'listing_url': url,
            'scrape_date': datetime.now().strftime('%Y-%m-%d'),
            'price': extract_price(soup),
            'location': extract_location(soup),
        }
        
        # Extract all property features
        property_features = extract_property_features(soup)
        listing_data.update(property_features)
        
        return listing_data
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {'listing_url': url, 'error': str(e)}

def get_all_listings_details(urls, output_file='remax_bursa_ilan_detaylari.csv'):
    """
    Scrape details from all listings and save to CSV.
    """
    all_data = []
    
    # Process each URL
    for i, url in enumerate(urls):
        print(f"Processing listing {i+1}/{len(urls)}")
        
        # Scrape the listing details
        listing_data = scrape_listing_details(url)
        all_data.append(listing_data)
        
        # Add a random delay between requests to be polite
        if i < len(urls) - 1:  # Skip delay for the last URL
            delay = random.uniform(2.0, 5.0)
            print(f"Waiting {delay:.2f} seconds before next request...")
            time.sleep(delay)
    
    # If we have data, save to CSV
    if all_data:
        # Get all possible field names from all dictionaries
        fieldnames = set()
        for data in all_data:
            fieldnames.update(data.keys())
        
        # Sort field names for consistent output (with key fields first)
        priority_fields = ['listing_url', 'scrape_date', 'price', 'location', 'Emlak Tipi', 
                         'm² (Brüt)', 'm² (Net)', 'Oda Sayısı', 'Bulunduğu Kat', 'Isıtma']
        
        # Create a sorted list of field names with priority fields first
        sorted_fields = []
        for field in priority_fields:
            if field in fieldnames:
                sorted_fields.append(field)
                fieldnames.remove(field)
        
        # Add remaining fields alphabetically
        sorted_fields.extend(sorted(fieldnames))
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted_fields)
            writer.writeheader()
            writer.writerows(all_data)
            
        print(f"Successfully saved {len(all_data)} property listings to {output_file}")
    else:
        print("No data collected!")
        
if _name_ == "_main_":
    # CSV file with listing URLs
    input_csv = "remax_bursa_ilan_linkleri.csv"
    
    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"Error: Input file {input_csv} not found!")
    else:
        # Read listing URLs
        listing_urls = read_listing_urls(input_csv)
        
        if listing_urls:
            # Scrape details from all listings
            get_all_listings_details(listing_urls)
        else:
            print("No URLs to process!")
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import os

# Location of the links file
links_file = 'emlakjet_bursa_kiralik_daire_linkleri.csv'

# Location of the output file
output_file = 'emlakjet_bursa_kiralik_daire_detaylari_new.csv'

# CSV headers - Extended
headers = [
    'Link', 
    'Fiyat', 
    'Oda Sayısı', 
    'Bulunduğu Kat', 
    'Metrekare', 
    'Konum',
    'İlan Numarası',
    'İlan Oluşturma Tarihi',
    'İlan Güncelleme Tarihi',
    'Türü',
    'Kategorisi',
    'Tipi',
    'Net Metrekare',
    'Brüt Metrekare',
    'Binanın Yaşı',
    'Binanın Kat Sayısı',
    'Isıtma Tipi',
    'Kullanım Durumu',
    'Yapı Durumu',
    'Eşya Durumu',
    'Aidat',
    'Tapu Durumu',
    'Site İçerisinde',
    'Depozito',
    'Banyo Sayısı',
    'Banyo Metrekare',
    'Balkon Durumu',
    'Salon Metrekare',
    'WC Sayısı',
    'Fiyat Durumu',
    'Görüntülü Gezilebilir mi?',
    'Ada',
    'Parsel'
]

print("Emlakjet Bursa Rental Apartment Details Scraper - New Version")
print("-------------------------------------------------------------")

# User-Agent information - More modern browser information
headers_req = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Referer': 'https://www.emlakjet.com/'
}

# Check previously processed links
processed_links = set()
if os.path.exists(output_file):
    try:
        with open(output_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                if row and len(row) > 0:  # Skip empty rows
                    processed_links.add(row[0])
        print(f"Found {len(processed_links)} already processed links. These links will be skipped.")
    except Exception as e:
        print(f"Error checking existing output file: {str(e)}")
        # Continue empty if there is a problem
        pass

# Create CSV output file (if it doesn't exist)
if not os.path.exists(output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
    print(f"New output file created: {output_file}")
else:
    print(f"Output file already exists, will continue by adding unprocessed links.")

# Read links
links = []
try:
    with open(links_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            if row:  # Skip empty rows
                links.append(row[0])
except Exception as e:
    print(f"Error reading links file: {str(e)}")
    exit()

print(f"Total {len(links)} links found.")

# Filter unprocessed links
links_to_process = [link for link in links if link not in processed_links]
print(f"{len(links_to_process)} links remaining to be processed.")

# Total number of links to be scraped
toplam_link = len(links_to_process)
basarili_scrape = 0
basarisiz_scrape = 0

# Text cleaning function
def clean_text(text):
    if not text:
        return ""
    # Remove unnecessary spaces and line breaks
    text = re.sub(r'\s+', ' ', text.strip())
    return text

# Scraping process for each link
for index, link in enumerate(links_to_process):
    try:
        print(f"Processing: {index+1}/{toplam_link} - {link}")
          # Send request to the page
        response = requests.get(link, headers=headers_req)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Create data dictionary
            data = {header: '' for header in headers}
            data['Link'] = link
            
            # 1. Get price and location information
            try:
                # Price
                price_element = soup.select_one('.styles_price__6zH_9')
                if price_element:
                    price_text = price_element.get_text().strip()
                    # Keep the TL sign
                    data['Fiyat'] = clean_text(price_text)
                
                # Quick info list (Number of Rooms, Floor, Square Meters)
                quick_info_list = soup.select('.styles_quickInfoList__uYRNl li')
                for item in quick_info_list:
                    value_attr = item.get('value', '')
                    text = item.get_text().strip()
                    
                    if 'Oda Sayısı' in value_attr:
                        data['Oda Sayısı'] = clean_text(text)
                    elif 'Bulunduğu Kat' in value_attr:
                        data['Bulunduğu Kat'] = clean_text(text)
                    elif 'Alan' in value_attr or 'Metrekare' in value_attr:
                        data['Metrekare'] = clean_text(text)
                  # Location
                location_element = soup.select_one('.styles_location__Y01SC')
                if location_element:
                    data['Konum'] = clean_text(location_element.get_text())
            except Exception as e:                print(f"Error while fetching price and location information: {str(e)}")
              # 2. Listing details
            try:
                # Find listing information section
                ilan_bilgileri = soup.select('#ilan-hakkinda .styles_inner__sV8Bk li')
                for item in ilan_bilgileri:
                    key_element = item.select_one('.styles_key__VqMhC')
                    value_element = item.select_one('.styles_value__3QmL3')
                    
                    if key_element and value_element:
                        key = clean_text(key_element.get_text())
                        value = clean_text(value_element.get_text())
                        
                        # Matching listing fields - For all fields
                        if key == 'İlan Numarası':
                            data['İlan Numarası'] = value
                        elif key == 'İlan Oluşturma Tarihi':
                            data['İlan Oluşturma Tarihi'] = value
                        elif key == 'İlan Güncelleme Tarihi':
                            data['İlan Güncelleme Tarihi'] = value
                        elif key == 'Türü':
                            data['Türü'] = value
                        elif key == 'Kategorisi':
                            data['Kategorisi'] = value
                        elif key == 'Tipi':
                            data['Tipi'] = value
                        elif key == 'Net Metrekare':
                            data['Net Metrekare'] = value
                        elif key == 'Brüt Metrekare':
                            data['Brüt Metrekare'] = value
                        elif key == 'Oda Sayısı' and not data['Oda Sayısı']:
                            data['Oda Sayısı'] = value
                        elif key == 'Binanın Yaşı':
                            data['Binanın Yaşı'] = value
                        elif key == 'Bulunduğu Kat' and not data['Bulunduğu Kat']:
                            data['Bulunduğu Kat'] = value
                        elif key == 'Binanın Kat Sayısı':
                            data['Binanın Kat Sayısı'] = value
                        elif key == 'Isıtma Tipi':
                            data['Isıtma Tipi'] = value
                        elif key == 'Kullanım Durumu':
                            data['Kullanım Durumu'] = value
                        elif key == 'Yapı Durumu':
                            data['Yapı Durumu'] = value
                        elif key == 'Eşya Durumu':
                            data['Eşya Durumu'] = value
                        elif key == 'Aidat':
                            data['Aidat'] = value
                        elif key == 'Tapu Durumu':
                            data['Tapu Durumu'] = value
                        elif key == 'Site İçerisinde':
                            data['Site İçerisinde'] = value
                        elif key == 'Depozito':
                            data['Depozito'] = value
                        elif key == 'Banyo Sayısı':
                            data['Banyo Sayısı'] = value
                        elif key == 'Banyo Metrekare':
                            data['Banyo Metrekare'] = value
                        elif key == 'Balkon Durumu':
                            data['Balkon Durumu'] = value
                        elif key == 'Salon Metrekare':
                            data['Salon Metrekare'] = value
                        elif key == 'WC Sayısı':
                            data['WC Sayısı'] = value
                        elif key == 'Fiyat Durumu':
                            data['Fiyat Durumu'] = value
                        elif key == 'Görüntülü Gezilebilir mi?':
                            data['Görüntülü Gezilebilir mi?'] = value
                        elif key == 'Ada':
                            data['Ada'] = value
                        elif key == 'Parsel':
                            data['Parsel'] = value
            except Exception as e:
                print(f"İlan detaylarını çekerken hata: {str(e)}")
            
            # CSV'ye kaydet
            with open(output_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([data[header] for header in headers])
            
            basarili_scrape += 1
              # Print progress report after every 10 links
            if (index + 1) % 10 == 0 or index == toplam_link - 1:
                print(f"Progress: {index+1}/{toplam_link} links completed. Successful: {basarili_scrape}, Failed: {basarisiz_scrape}")
            
            # Random delay to reduce server load            time.sleep(random.uniform(1.5, 3.0))
            
        else:
            print(f"Link inaccessible: {link} - Status Code: {response.status_code}")
            basarisiz_scrape += 1            # Wait a bit longer in case of status code error
            time.sleep(5)
            
    except Exception as e:
        print(f"Error processing link: {link} - Error: {str(e)}")
        basarisiz_scrape += 1
        # Wait even longer in case of error
        time.sleep(5)

print(f"\nCompleted! Out of {toplam_link} total links, {basarili_scrape} were successfully scraped, {basarisiz_scrape} failed.")
print(f"Results saved to {output_file} file.")

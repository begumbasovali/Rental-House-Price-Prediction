import csv
import time
import pandas as pd
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

# Function to extract text content safely
def get_text_safely(driver, xpath, wait_time=5):
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text.strip()
    except (TimeoutException, NoSuchElementException):
        return "N/A"
    except Exception as e:
        print(f"Error extracting {xpath}: {e}")
        return "N/A"

# Function to parse brut and net m2 values
def parse_m2_values(m2_text):
    if m2_text == "N/A":
        return "N/A", "N/A"
    
    # Try to find both brut and net values with the exact format from the website
    match = re.search(r'(\d+(?:\.\d+)?)\s*m2\s*\/\s*(\d+(?:\.\d+)?)\s*m2', m2_text)
    if match:
        return f"{match.group(1)} m2", f"{match.group(2)} m2"
    
    # Check for a different format where values might be separated
    brut_match = re.search(r'(\d+(?:\.\d+)?)\s*m2', m2_text)
    net_match = re.search(r'\/\s*(\d+(?:\.\d+)?)\s*m2', m2_text)
    
    if brut_match and net_match:
        return f"{brut_match.group(1)} m2", f"{net_match.group(1)} m2"
    
    # If only one value is found, return it as brut
    if brut_match:
        return f"{brut_match.group(1)} m2", "N/A"
    
    return m2_text, "N/A"

# Function to scrape property details from a URL
def scrape_property_details(driver, url):
    try:
        driver.get(url)
        # Wait for the main content to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.detail-info-wrap"))
        )
        
        # Allow some time for any lazy-loaded content
        time.sleep(2)
        
        # Extract all the property details
        property_data = {
            "İlan Linki": url,
            "Fiyat": get_text_safely(driver, "//p[@class='fz24-text price']"),
            "İl": get_text_safely(driver, "//ul[@class='detail-info-location']/li[1]"),
            "İlçe": get_text_safely(driver, "//ul[@class='detail-info-location']/li[2]"),
            "Mahalle": get_text_safely(driver, "//ul[@class='detail-info-location']/li[3]"),
        }
        
        # Get all specification items
        try:
            spec_items = driver.find_elements(By.CSS_SELECTOR, "li.spec-item")
        except Exception as e:
            print(f"Error finding spec items: {e}")
            spec_items = []
        
        for item in spec_items:
            try:
                label = item.find_element(By.CSS_SELECTOR, "span.txt").text.strip()
                
                # For values, first try value-txt class, if not found use the direct text
                try:
                    value = item.find_element(By.CSS_SELECTOR, "span.value-txt").text.strip()
                except NoSuchElementException:
                    # If value-txt is not found, get the text from the second div/span/a
                    try:
                        value_elements = item.find_elements(By.XPATH, ".//div[@class='tooltip-wrapper spec-item__tooltip'][2]//span | .//a | .//span[not(contains(@class, 'txt'))]")
                        if value_elements:
                            value = " ".join([elem.text.strip() for elem in value_elements if elem.text.strip()])
                        else:
                            value = "N/A"
                    except Exception:
                        value = "N/A"
                
                # Handle empty values
                if not value:
                    value = "N/A"
                  # Handle special case for Brüt / Net M2
                if label == "Brüt / Net M2":
                    # Special handling for Brüt / Net M2
                    try:
                        # Try to get both span elements
                        brut_span = item.find_element(By.XPATH, ".//span[not(contains(@class, 'txt'))][1]")
                        net_span = item.find_element(By.XPATH, ".//span[not(contains(@class, 'txt'))][2]")
                        
                        brut_value = brut_span.text.strip()
                        net_value = net_span.text.strip()
                        
                        # Combine for parsing
                        combined_value = f"{brut_value}{net_value}"
                        brut_m2, net_m2 = parse_m2_values(combined_value)
                        
                        property_data["Brüt M2"] = brut_m2
                        property_data["Net M2"] = net_m2
                    except NoSuchElementException:
                        # Fall back to previous parsing if the spans aren't found
                        brut_m2, net_m2 = parse_m2_values(value)
                        property_data["Brüt M2"] = brut_m2
                        property_data["Net M2"] = net_m2
                else:
                    property_data[label] = value
            
            except NoSuchElementException:
                continue
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
        
        return property_data
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"İlan Linki": url, "Error": str(e)}

# Main function to process all URLs
def process_all_properties():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-webgl")  # Disable WebGL to prevent rendering issues
    chrome_options.add_argument("--disable-software-rasterizer")  # Disable software rasterization
    chrome_options.add_argument("--enable-unsafe-swiftshader")  # Allow SwiftShader as suggested in the error
    chrome_options.add_argument("--log-level=3")  # Suppress most console messages
    chrome_options.add_argument("--silent")  # Enable silent mode
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Disable logging
    
    # Redirect stderr to suppress WebDriver messages
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    
    # Initialize the Chrome driver
    driver = None
    
    try:
        # Read property URLs from CSV
        links_df = pd.read_csv('hepsiemlak_bursa_ilan_linkleri.csv')
        
        # Check if the column name is correct
        url_column = 'İlan Linki' if 'İlan Linki' in links_df.columns else links_df.columns[0]
        
        # List to store all property details
        all_properties = []
        
        # Process each URL
        total_urls = len(links_df)
        
        # Initialize error counter and the last URL that caused an error
        consecutive_errors = 0
        last_error_url = None
        
        for index, row in links_df.iterrows():
            # Reset driver if we have consecutive errors
            if consecutive_errors >= 3:
                print("Too many consecutive errors. Resetting the WebDriver...")
                if driver:
                    driver.quit()
                time.sleep(5)  # Wait a bit before restarting
                driver = webdriver.Chrome(options=chrome_options)
                consecutive_errors = 0
            
            # Initialize driver if not already
            if driver is None:
                driver = webdriver.Chrome(options=chrome_options)
            
            url = row[url_column]
            print(f"Processing {index+1}/{total_urls}: {url}")
            
            try:
                property_data = scrape_property_details(driver, url)
                all_properties.append(property_data)
                consecutive_errors = 0  # Reset error counter on success
                last_error_url = None   # Reset last error URL
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                # Add a basic error entry to not lose track of this URL
                all_properties.append({"İlan Linki": url, "Error": str(e)})
                consecutive_errors += 1
                last_error_url = url
                
                # If driver crashed, reset it
                if "chrome not reachable" in str(e).lower():
                    print("WebDriver connection lost. Restarting...")
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = None
            
            # Add a small delay between requests
            time.sleep(2)
              # Save incremental results every 50 items
            if index > 0 and index % 50 == 0:
                print(f"Saving intermediate results after processing {index+1} properties...")
                temp_df = pd.DataFrame(all_properties)
                temp_file = f'hepsiemlak_bursa_ilan_detaylari_part_{index+1}.csv'
                temp_df.to_csv(temp_file, index=False, encoding='utf-8-sig')
                print(f"Intermediate data saved to {temp_file}")
        
        # Create DataFrame from all properties
        result_df = pd.DataFrame(all_properties)
        
        # Save to CSV
        output_file = 'hepsiemlak_bursa_ilan_detaylari.csv'
        result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Data successfully saved to {output_file}")
      except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the driver
        driver.quit()
        
        # Restore stderr
        sys.stderr = original_stderr

# Run the main function
if __name__ == "__main__":
    process_all_properties()
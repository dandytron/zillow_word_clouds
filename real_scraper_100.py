#!/usr/bin/env python3
"""
Zillow scraper get 100 listings with pagination that's basically broken right now
"""

import os
import time
import random
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
from playwright.sync_api import sync_playwright
from datetime import datetime

# Download NLTK resources if needed
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Create data directory
os.makedirs('data', exist_ok=True)

# Custom real estate stopwords
real_estate_stopwords = set([
    'home', 'property', 'house', 'listing', 'features', 'includes',
    'located', 'offers', 'contact', 'information', 'price', 'sale',
    'bedroom', 'bathroom', 'bath', 'bed', 'sq', 'ft', 'square', 'feet',
    'year', 'built', 'call', 'today', 'agent', 'new', 'view', 'tour',
    'zillow', 'apartment', 'unit', 'rental', 'rent', 'available', 'lease',
    'monthly', 'deposit', 'utilities', 'included', 'pets', 'parking', 'laundry',
    'apt', 'blvd', 'dr', 'st', 'ave', 'street', 'drive', 'boulevard', 'avenue',
    'road', 'lane', 'place', 'court', 'way', 'circle', 'terrace', 'plaza',
    'floor', 'suite', 'building', 'complex', 'community', 'residence', 'residential',
    'luxury', 'premium', 'exclusive', 'modern', 'contemporary', 'traditional',
    'spacious', 'cozy', 'charming', 'beautiful', 'stunning', 'gorgeous', 'amazing',
    'perfect', 'ideal', 'wonderful', 'fantastic', 'excellent', 'outstanding',
    'convenient', 'close', 'near', 'walking', 'distance', 'minutes', 'blocks',
    'downtown', 'uptown', 'midtown', 'suburban', 'urban', 'residential', 'commercial'
])

def create_browser():
    """Create a browser with stealth settings"""
    playwright = sync_playwright().start()
    
    browser = playwright.chromium.launch(
        headless=False,  # Keep visible for CAPTCHA handling
        args=[
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-extensions',
            '--disable-plugins',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-field-trial-config',
            '--disable-ipc-flooding-protection'
        ]
    )
    
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080},
        screen={'width': 1920, 'height': 1080},
        device_scale_factor=1,
        has_touch=False,
        java_script_enabled=True,
        locale='en-US',
        timezone_id='America/Los_Angeles'
    )
    
    page = context.new_page()
    page.set_default_timeout(120000)
    
    return browser, page, playwright

def check_for_captcha(page):
    """Check if a CAPTCHA is present on the page"""
    captcha_selectors = [
        '#px-captcha-wrapper', '.px-captcha-container', '[id*="captcha"]',
        '[class*="captcha"]', 'iframe[title*="verification"]', 'iframe[title*="challenge"]'
    ]
    
    for selector in captcha_selectors:
        try:
            captcha_elem = page.locator(selector)
            if captcha_elem.count() > 0:
                print(f"⚠️  CAPTCHA detected using selector: {selector}")
                return True
        except:
            continue
    
    try:
        page_content = page.content().lower()
        captcha_indicators = [
            'press & hold to confirm you are', 'human verification challenge',
            'confirm you are a human', 'not a bot', 'reference id', 'px-captcha', 'recaptcha'
        ]
        for indicator in captcha_indicators:
            if indicator in page_content:
                print(f"⚠️  CAPTCHA detected in page content: '{indicator}'")
                return True
    except:
        pass
    
    return False

def handle_captcha_interactive(page):
    """Handle CAPTCHA with interactive approach"""
    print("🤖 CAPTCHA detected! Please solve manually...")
    print("Waiting for manual CAPTCHA resolution...")
    
    # Wait longer for manual intervention
    time.sleep(30)
    
    # Check if CAPTCHA is still present
    if check_for_captcha(page):
        print("⚠️  CAPTCHA still present after 30 seconds")
        return False
    else:
        print("✅ CAPTCHA appears to have been resolved")
        return True

def get_listings_with_pagination(neighborhood, target_listings=100):
    """Get listings with proper pagination handling"""
    print(f"\n=== Getting {target_listings} real listings for {neighborhood} ===")
    
    # Load existing data (but we'll ignore it to get fresh data)
    existing_df = load_existing_data(neighborhood)
    print(f"Found {len(existing_df)} existing listings (will get fresh data)")
    # Clear existing data to force fresh scraping
    existing_df = pd.DataFrame()
    
    try:
        browser, page, playwright = create_browser()
        
        # Construct proper URL with full search parameters
        if neighborhood.lower() == "echo park":
            # Use the full URL with search parameters to get all 166 listings
            url = 'https://www.zillow.com/echo-park-los-angeles-ca/rentals/?category=SEMANTIC&searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-118.28746629125978%2C%22east%22%3A-118.21983170874024%2C%22south%22%3A34.05384446981765%2C%22north%22%3A34.10957772807901%7D%2C%22usersSearchTerm%22%3A%22Echo%20Park%20Los%20Angeles%20CA%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A268134%7D%5D%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A14%7D'
        else:
            url = f'https://www.zillow.com/{neighborhood.lower().replace(" ", "-")}-ca/rentals/'
        
        print(f"Starting with URL: {url}")
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        # Longer random delay to avoid detection
        time.sleep(random.uniform(15, 25))
        
        # Check for CAPTCHA
        if check_for_captcha(page):
            if not handle_captcha_interactive(page):
                print("CAPTCHA not resolved, stopping...")
                browser.close()
                playwright.stop()
                return []
        
        all_listings = []
        page_num = 1
        max_pages = 20  # Safety limit
        
        while len(all_listings) < target_listings and page_num <= max_pages:
            print(f"\n--- Page {page_num} ---")
            print(f"Current listings: {len(all_listings)}")
            
            # Scroll to load more content on current page
            print("Scrolling to load more listings...")
            for i in range(25):  # Much more aggressive scrolling to load all listings
                page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {random.uniform(0.8, 1.0)})")
                time.sleep(random.uniform(2, 4))  # Faster scrolling to load more content
            
            # Wait longer for content to load
            time.sleep(random.uniform(8, 12))
            
            # Try clicking "Show more" or "Load more" buttons if they exist
            try:
                load_more_selectors = [
                    'button:has-text("Show more")', 'button:has-text("Load more")',
                    'button:has-text("View more")', '[data-test="load-more"]',
                    '.load-more-button', '.show-more-button'
                ]
                for selector in load_more_selectors:
                    try:
                        load_btn = page.locator(selector)
                        if load_btn.count() > 0:
                            print(f"Found load more button: {selector}")
                            load_btn.first.click()
                            time.sleep(3)
                            break
                    except:
                        continue
            except:
                pass
            
            # Check total available listings on page
            try:
                result_count_elem = page.locator('.result-count, .search-subtitle h2, [data-test="result-count"]')
                if result_count_elem.count() > 0:
                    result_text = result_count_elem.first.text_content()
                    print(f"Page shows: {result_text}")
            except:
                pass
            
            # Extract listings from current page
            page_listings = extract_listings_from_current_page(page, target_listings - len(all_listings))
            
            if page_listings:
                for listing in page_listings:
                    listing['page_number'] = page_num
                all_listings.extend(page_listings)
                print(f"Found {len(page_listings)} listings on page {page_num}")
                print(f"Total listings so far: {len(all_listings)}")
            else:
                print(f"No listings found on page {page_num}")
            
            # Try to go to next page using the specific selector you provided
            if len(all_listings) < target_listings:
                next_page_success = go_to_next_page_proper(page)
                if not next_page_success:
                    print("No more pages available or pagination failed")
                    break
                
                page_num += 1
                time.sleep(random.uniform(3, 6))
            else:
                print(f"Reached target of {target_listings} listings")
                break
        
        print(f"\nTotal listings collected: {len(all_listings)}")
        
        if all_listings:
            # Get detailed descriptions for all listings
            detailed_listings = get_detailed_descriptions(page, all_listings, existing_df)
            
            # Save results
            save_results(detailed_listings, neighborhood)
            
            browser.close()
            playwright.stop()
            return detailed_listings
        
        browser.close()
        playwright.stop()
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        try:
            browser.close()
            playwright.stop()
        except:
            pass
    
    return []

def go_to_next_page_proper(page):
    """Go to next page using the specific pagination element"""
    print("Looking for next page button...")
    
    # Try the specific selector you provided
    next_page_selectors = [
        'a[aria-disabled="false"][rel="next"][title="Next page"]',
        'a[rel="next"][title="Next page"]',
        'a[aria-disabled="false"][rel="next"]',
        'a[rel="next"]',
        'a[title="Next page"]',
        'button[aria-label="Next page"]',
        'a[aria-label="Next page"]',
        'button:has-text("Next")',
        'a:has-text("Next")',
        '[data-test="pagination-next"]',
        '.pagination-next'
    ]
    
    for selector in next_page_selectors:
        try:
            next_btn = page.locator(selector)
            if next_btn.count() > 0:
                # Check if button is disabled
                is_disabled = next_btn.first.get_attribute('aria-disabled')
                if is_disabled == 'true':
                    print("Next page button is disabled")
                    return False
                
                print(f"Found next page button using selector: {selector}")
                next_btn.first.click()
                time.sleep(5)  # Wait longer for page to load
                return True
        except Exception as e:
            print(f"Error with next page selector {selector}: {e}")
            continue
    
    print("No next page button found")
    return False

def extract_listings_from_current_page(page, max_listings_on_page):
    """Extract listings from the current page"""
    listings = []
    
    # Multiple selectors for property cards
    card_selectors = [
        '[data-test="property-card"]',
        '.property-card',
        '[data-testid="property-card"]',
        '.list-card',
        '.property-card-container',
        '.list-card-container'
    ]
    
    cards = None
    for selector in card_selectors:
        try:
            cards = page.locator(selector)
            if cards.count() > 0:
                print(f"Found {cards.count()} cards using selector: {selector}")
                break
        except:
            continue
    
    if not cards or cards.count() == 0:
        print("No property cards found on this page")
        return []
    
    # Extract data from each card
    for i in range(min(cards.count(), max_listings_on_page)):
        try:
            card = cards.nth(i)
            
            # Extract data with multiple selectors
            address = extract_text_with_selectors(card, [
                'address', '[data-test="property-card-addr"]', '.property-address',
                '.list-card-addr', '.property-address-text'
            ])
            
            price = extract_text_with_selectors(card, [
                '[data-test="property-card-price"]', '.property-price', '.price',
                '.list-card-price', '.property-price-text'
            ])
            
            beds = extract_text_with_selectors(card, [
                '[data-test="property-card-beds"]', '.beds', '.bedrooms',
                '.list-card-beds', '.property-beds'
            ])
            
            baths = extract_text_with_selectors(card, [
                '[data-test="property-card-baths"]', '.baths', '.bathrooms',
                '.list-card-baths', '.property-baths'
            ])
            
            sqft = extract_text_with_selectors(card, [
                '[data-test="property-card-sqft"]', '.sqft', '.square-feet',
                '.list-card-sqft', '.property-sqft'
            ])
            
            url = extract_url_with_selectors(card, [
                '[data-test="property-card-link"]', 'a', '.property-link',
                '.list-card-link', '.property-card-link'
            ])
            
            if address and address != "N/A":
                listings.append({
                    'address': address,
                    'price': price,
                    'beds': beds,
                    'baths': baths,
                    'sqft': sqft,
                    'url': url,
                    'description': "N/A",
                    'type': 'Rental'
                })
        
        except Exception as e:
            print(f"Error extracting card {i}: {e}")
            continue
    
    return listings

def extract_text_with_selectors(element, selectors):
    """Extract text using multiple selectors"""
    for selector in selectors:
        try:
            elem = element.locator(selector)
            if elem.count() > 0:
                text = elem.first.text_content().strip()
                if text:
                    return text
        except:
            continue
    return "N/A"

def extract_url_with_selectors(element, selectors):
    """Extract URL using multiple selectors"""
    for selector in selectors:
        try:
            elem = element.locator(selector)
            if elem.count() > 0:
                url = elem.first.get_attribute('href')
                if url:
                    if not url.startswith('http'):
                        url = 'https://www.zillow.com' + url
                    return url
        except:
            continue
    return None

def get_detailed_descriptions(page, listings, existing_df):
    """Get detailed descriptions for all listings"""
    detailed_listings = []
    successful_descriptions = 0
    
    for i, listing in enumerate(listings):
        if not listing['url']:
            print(f"Listing {i+1}: No URL available")
            detailed_listings.append(listing)
            continue
        
        # Check if already exists
        if is_listing_already_scraped(listing, existing_df):
            print(f"Listing {i+1}: Already exists, skipping")
            existing_row = existing_df[existing_df['url'] == listing['url']]
            if not existing_row.empty:
                detailed_listings.append(existing_row.iloc[0].to_dict())
            else:
                detailed_listings.append(listing)
            continue
        
        print(f"Getting details for listing {i+1}/{len(listings)}: {listing['address'][:50]}...")
        print(f"URL: {listing['url']}")
        
        try:
            # Navigate to listing
            time.sleep(random.uniform(5, 10))  # Longer delay before visiting each listing
            page.goto(listing['url'], wait_until='domcontentloaded', timeout=30000)
            
            # Check for CAPTCHA
            if check_for_captcha(page):
                if not handle_captcha_interactive(page):
                    print(f"CAPTCHA blocked listing {i+1}")
                    listing['description'] = "CAPTCHA_BLOCKED"
                    detailed_listings.append(listing)
                    continue
            
            time.sleep(random.uniform(6, 12))  # Longer delay after page load
            
            # Click "Show more" if available
            show_more_selectors = [
                'button:has-text("Show more")', '[data-testid="show-more-button"]',
                '.show-more-button', 'button:has-text("Read more")'
            ]
            
            for selector in show_more_selectors:
                try:
                    show_more_btn = page.locator(selector)
                    if show_more_btn.count() > 0:
                        print("Found 'Show more' button, clicking...")
                        time.sleep(random.uniform(1, 2))
                        show_more_btn.first.click()
                        time.sleep(2)
                        break
                except:
                    continue
            
            # Extract description
            description = extract_description_proper(page)
            
            if description:
                listing['description'] = description
                successful_descriptions += 1
                print(f"✓ Successfully extracted description ({len(description)} chars)")
            else:
                listing['description'] = "N/A"
                print(f"✗ No description found")
            
            detailed_listings.append(listing)
            
            # Progress update
            if (i + 1) % 10 == 0:
                print(f"Progress: {i+1}/{len(listings)} listings processed")
            
        except Exception as e:
            print(f"Error getting details for listing {i+1}: {e}")
            listing['description'] = "ERROR"
            detailed_listings.append(listing)
    
    print(f"\nSummary: {successful_descriptions} successful descriptions out of {len(detailed_listings)} listings")
    return detailed_listings

def extract_description_proper(page):
    """Extract description with proper selectors"""
    description_selectors = [
        '[data-testid="description"]',
        '.ds-overview-section .Text-c11n-8-109-3__sc-aiai24-0',
        '.sc-uhnfH .Text-c11n-8-109-3__sc-aiai24-0',
        '.RTNKi .Text-c11n-8-109-3__sc-aiai24-0',
        '.gycwvU', '.cEHZrB',
        '.property-description', '.description', '.summary',
        '.property-details', '[data-test="property-description"]',
        '.overview-section', '.property-overview',
        'article .Text-c11n-8-109-3__sc-aiai24-0',
        '.Spacer-c11n-8-109-3__sc-17suqs2-0 article',
        '.bgKNvw article', '.property-content',
        '.listing-description', 'p', '.content', '.text'
    ]
    
    for selector in description_selectors:
        try:
            desc_elem = page.locator(selector)
            if desc_elem.count() > 0:
                for j in range(desc_elem.count()):
                    text = desc_elem.nth(j).text_content().strip()
                    if len(text) > 50:
                        return text
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
            continue
    
    return None

def load_existing_data(neighborhood):
    """Load existing data from CSV"""
    filename = f'data/{neighborhood.replace(" ", "_")}_rentals.csv'
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            print(f"Found existing data: {len(df)} listings in {filename}")
            return df
        except Exception as e:
            print(f"Error loading existing data: {e}")
            return pd.DataFrame()
    else:
        print(f"No existing data found for {neighborhood}")
        return pd.DataFrame()

def is_listing_already_scraped(listing, existing_df):
    """Check if listing already exists"""
    if existing_df.empty:
        return False
    
    if listing.get('url') and not existing_df.empty:
        url_match = existing_df['url'] == listing['url']
        if url_match.any():
            return True
    
    if listing.get('address') and not existing_df.empty:
        address_match = existing_df['address'] == listing['address']
        if address_match.any():
            return True
    
    return False

def save_results(listings, neighborhood):
    """Save results to CSV"""
    if not listings:
        print("No listings to save")
        return
    
    df = pd.DataFrame(listings)
    df['neighborhood'] = neighborhood
    df['scraped_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Ensure data directory exists
    csv_filename = f'data/{neighborhood.replace(" ", "_")}_rentals.csv'
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    
    df.to_csv(csv_filename, index=False)
    print(f"Saved {len(df)} listings to {csv_filename}")

def generate_word_cloud_from_descriptions(df, neighborhood):
    """Generate word cloud from descriptions"""
    if df.empty or 'description' not in df.columns:
        print(f"No description data for word cloud in {neighborhood}")
        return
    
    # Combine all descriptions
    descriptions = df['description'].dropna().astype(str)
    if len(descriptions) == 0:
        print(f"No descriptions available for {neighborhood}")
        return
    
    all_text = ' '.join(descriptions)
    
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(all_text.lower())
    
    # Filter tokens
    filtered_tokens = []
    for word in tokens:
        if (word.isalpha() and 
            len(word) > 2 and 
            word not in stop_words and 
            word not in real_estate_stopwords):
            filtered_tokens.append(word)
    
    if not filtered_tokens:
        print(f"No meaningful words found for {neighborhood}")
        return
    
    # Create frequency distribution
    word_freq = Counter(filtered_tokens)
    
    # Generate word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        max_words=100, 
        contour_width=3, 
        contour_color='steelblue',
        colormap='viridis'
    )
    wordcloud.generate_from_frequencies(word_freq)
    
    # Display word cloud
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Most Common Words in {neighborhood} Rental Listings\n(Total: {len(df)} listings)', 
              fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save word cloud
    filename = f'data/{neighborhood.replace(" ", "_")}_description_wordcloud.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Word cloud saved to {filename}")
    
    plt.show()
    
    # Print top words
    print(f"\nTop 10 words in {neighborhood}:")
    for word, count in word_freq.most_common(10):
        print(f"  {word}: {count}")

def main():
    """Main function to scrape 100 real listings"""
    print("=" * 60)
    print("REAL ZILLOW SCRAPER - 100 REAL LISTINGS")
    print("=" * 60)
    
    neighborhoods = ["Echo Park"]
    
    for i, neighborhood in enumerate(neighborhoods, 1):
        print(f"\n{'='*20} NEIGHBORHOOD {i}/{len(neighborhoods)}: {neighborhood} {'='*20}")
        
        try:
            # Scrape data
            listings = get_listings_with_pagination(neighborhood, target_listings=100)
            
            if listings:
                print(f"\n✓ Successfully scraped {len(listings)} listings from {neighborhood}")
                
                # Create dataframe
                df = pd.DataFrame(listings)
                
                # Generate word cloud
                generate_word_cloud_from_descriptions(df, neighborhood)
                
                # Show statistics
                successful_descriptions = sum(1 for desc in df['description'] if desc and desc != "N/A" and desc != "CAPTCHA_BLOCKED")
                print(f"\nStatistics:")
                print(f"  - Total listings: {len(df)}")
                print(f"  - Successful descriptions: {successful_descriptions}")
                print(f"  - Description success rate: {successful_descriptions/len(df)*100:.1f}%")
                
                # Show sample URLs to prove they're real
                print(f"\nSample URLs (first 5):")
                for j, url in enumerate(df['url'].head(5)):
                    print(f"  {j+1}. {url}")
                
            else:
                print(f"\n✗ No data was scraped for {neighborhood}")
                
        except Exception as e:
            print(f"\n✗ Error processing {neighborhood}: {e}")
        
        # Delay between neighborhoods
        if i < len(neighborhoods):
            delay = random.uniform(60, 120)  # Longer delay between neighborhoods
            print(f"\nWaiting {delay:.1f} seconds before next neighborhood...")
            time.sleep(delay)
    
    print(f"\n{'='*60}")
    print("SCRAPING COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 

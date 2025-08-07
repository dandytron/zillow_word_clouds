#!/usr/bin/env python3
"""
Generate word clouds from scraped Zillow data
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import re

# Download NLTK resources if needed
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Custom real estate stopwords - including neighborhood names and common abbreviations
real_estate_stopwords = set([
    # Generic real estate terms
    'home', 'property', 'house', 'listing', 'features', 'includes',
    'located', 'offers', 'contact', 'information', 'price', 'sale',
    'bedroom', 'bathroom', 'bath', 'bed', 'sq', 'ft', 'square', 'feet',
    'year', 'built', 'call', 'today', 'agent', 'new', 'view', 'tour',
    'zillow', 'apartment', 'unit', 'rental', 'rent', 'available', 'lease',
    'monthly', 'deposit', 'utilities', 'included', 'pets', 'parking', 'laundry',
    
    # Common abbreviations
    'apt', 'blvd', 'dr', 'st', 'ave', 'street', 'drive', 'boulevard', 'avenue',
    'road', 'lane', 'place', 'court', 'way', 'circle', 'terrace', 'plaza',
    'floor', 'suite', 'building', 'complex', 'community', 'residence', 'residential',
    
    # Descriptive words
    'luxury', 'premium', 'exclusive', 'modern', 'contemporary', 'traditional',
    'spacious', 'cozy', 'charming', 'beautiful', 'stunning', 'gorgeous', 'amazing',
    'perfect', 'ideal', 'wonderful', 'fantastic', 'excellent', 'outstanding',
    'convenient', 'close', 'near', 'walking', 'distance', 'minutes', 'blocks',
    'downtown', 'uptown', 'midtown', 'suburban', 'urban', 'residential', 'commercial',
    
    # Los Angeles neighborhood names
    'beverly', 'hills', 'beverly hills', 'hollywood', 'downtown', 'venice', 'santa monica',
    'westwood', 'brentwood', 'bel air', 'holmby hills', 'encino', 'tarzana', 'woodland hills',
    'calabasas', 'malibu', 'manhattan beach', 'hermosa beach', 'redondo beach', 'torrance',
    'culver city', 'marina del rey', 'playa del rey', 'el segundo', 'hawthorne', 'gardena',
    'inglewood', 'compton', 'carson', 'long beach', 'san pedro', 'wilmington', 'harbor city',
    'lomita', 'rancho palos verdes', 'palos verdes estates', 'rolling hills estates',
    'rolling hills', 'manhattan beach', 'hermosa beach', 'redondo beach', 'torrance',
    'culver city', 'marina del rey', 'playa del rey', 'el segundo', 'hawthorne', 'gardena',
    'inglewood', 'compton', 'carson', 'long beach', 'san pedro', 'wilmington', 'harbor city',
    'lomita', 'rancho palos verdes', 'palos verdes estates', 'rolling hills estates',
    'rolling hills', 'san fernando valley', 'northridge', 'reseda', 'canoga park',
    'chatsworth', 'porter ranch', 'granada hills', 'sherman oaks', 'studio city',
    'north hollywood', 'valley village', 'tujunga', 'sunland', 'la crescenta',
    'glendale', 'burbank', 'pasadena', 'altadena', 'sierra madre', 'arcadia',
    'monrovia', 'duarte', 'azusa', 'covina', 'west covina', 'diamond bar',
    'walnut', 'rowland heights', 'hacienda heights', 'la puente', 'industry',
    'baldwin park', 'west puente valley', 'avocado heights', 'bassett', 'irwindale',
    'el monte', 'south el monte', 'temple city', 'rosemead', 'san gabriel',
    'alhambra', 'monterey park', 'east los angeles', 'montebello', 'commerce',
    'bell gardens', 'cudahy', 'bell', 'maywood', 'huntington park', 'vernon',
    'south gate', 'lynwood', 'paramount', 'downey', 'norwalk', 'santa fe springs',
    'whittier', 'la habra', 'la mirada', 'cerritos', 'artesia', 'lakewood',
    'cypress', 'los alamitos', 'seal beach', 'sunset beach', 'huntington beach',
    'fountain valley', 'westminster', 'garden grove', 'anaheim', 'fullerton',
    'buena park', 'la palma', 'yorba linda', 'placentia', 'brea', 'la habra heights',
    'rowland heights', 'hacienda heights', 'la puente', 'industry', 'baldwin park',
    'west puente valley', 'avocado heights', 'bassett', 'irwindale', 'el monte',
    'south el monte', 'temple city', 'rosemead', 'san gabriel', 'alhambra',
    'monterey park', 'east los angeles', 'montebello', 'commerce', 'bell gardens',
    'cudahy', 'bell', 'maywood', 'huntington park', 'vernon', 'south gate',
    'lynwood', 'paramount', 'downey', 'norwalk', 'santa fe springs', 'whittier',
    'la habra', 'la mirada', 'cerritos', 'artesia', 'lakewood', 'cypress',
    'los alamitos', 'seal beach', 'sunset beach', 'huntington beach', 'fountain valley',
    'westminster', 'garden grove', 'anaheim', 'fullerton', 'buena park', 'la palma',
    'yorba linda', 'placentia', 'brea', 'la habra heights'
])

def load_and_analyze_data(neighborhood):
    """Load scraped data and analyze it"""
    csv_filename = f'data/{neighborhood.replace(" ", "_")}_rentals.csv'
    
    if not os.path.exists(csv_filename):
        print(f"No data file found for {neighborhood}")
        return None
    
    df = pd.read_csv(csv_filename)
    print(f"Loaded {len(df)} listings for {neighborhood}")
    
    # Show sample data
    print("\nSample data:")
    print(df[['address', 'price', 'beds', 'baths', 'sqft']].head())
    
    # Analyze prices
    print(f"\nPrice Analysis for {neighborhood}:")
    prices = df['price'].dropna()
    print(f"Number of listings with prices: {len(prices)}")
    
    # Extract numeric prices
    numeric_prices = []
    for price in prices:
        # Extract numbers from price strings
        price_digits = re.sub(r'[^\d]', '', str(price))
        if price_digits:
            numeric_prices.append(int(price_digits))
    
    if numeric_prices:
        print(f"Average price: ${sum(numeric_prices)/len(numeric_prices):,.0f}")
        print(f"Price range: ${min(numeric_prices):,} - ${max(numeric_prices):,}")
    
    return df

def generate_word_cloud_from_descriptions(df, neighborhood):
    """Generate word cloud from property descriptions"""
    if df.empty:
        print(f"No data for {neighborhood}")
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
    plt.title(f'Most Common Words in {neighborhood} Rental Descriptions\n(Total: {len(df)} listings)', 
              fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save word cloud
    filename = f'data/{neighborhood.replace(" ", "_")}_description_wordcloud.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Description word cloud saved to {filename}")
    
    plt.show()
    
    # Print top words
    print(f"\nTop 10 words in {neighborhood} descriptions:")
    for word, count in word_freq.most_common(10):
        print(f"  {word}: {count}")

def create_price_analysis(df, neighborhood):
    """Create price analysis visualization"""
    if df.empty:
        return
    
    # Extract numeric prices
    numeric_prices = []
    price_labels = []
    
    for price in df['price'].dropna():
        # Extract numbers from price strings
        price_digits = re.sub(r'[^\d]', '', str(price))
        if price_digits:
            numeric_prices.append(int(price_digits))
            price_labels.append(price)
    
    if not numeric_prices:
        print("No valid prices found for analysis")
        return
    
    # Create price analysis plot
    plt.figure(figsize=(12, 8))
    
    # Price distribution
    plt.subplot(2, 2, 1)
    plt.hist(numeric_prices, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title(f'Price Distribution in {neighborhood}')
    plt.xlabel('Price ($)')
    plt.ylabel('Number of Listings')
    
    # Price vs listing number
    plt.subplot(2, 2, 2)
    plt.scatter(range(len(numeric_prices)), numeric_prices, alpha=0.7, color='red')
    plt.title(f'Price by Listing Order in {neighborhood}')
    plt.xlabel('Listing Number')
    plt.ylabel('Price ($)')
    
    # Price statistics
    plt.subplot(2, 2, 3)
    stats = ['Min', 'Mean', 'Median', 'Max']
    values = [min(numeric_prices), sum(numeric_prices)/len(numeric_prices), 
              sorted(numeric_prices)[len(numeric_prices)//2], max(numeric_prices)]
    plt.bar(stats, values, color=['lightgreen', 'lightblue', 'lightcoral', 'gold'])
    plt.title(f'Price Statistics in {neighborhood}')
    plt.ylabel('Price ($)')
    
    # Price range
    plt.subplot(2, 2, 4)
    plt.boxplot(numeric_prices)
    plt.title(f'Price Range in {neighborhood}')
    plt.ylabel('Price ($)')
    
    plt.tight_layout()
    
    # Save plot
    filename = f'data/{neighborhood.replace(" ", "_")}_price_analysis.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Price analysis saved to {filename}")
    
    plt.show()
    
    # Print statistics
    print(f"\nPrice Statistics for {neighborhood}:")
    print(f"  Minimum: ${min(numeric_prices):,}")
    print(f"  Maximum: ${max(numeric_prices):,}")
    print(f"  Average: ${sum(numeric_prices)/len(numeric_prices):,.0f}")
    print(f"  Median: ${sorted(numeric_prices)[len(numeric_prices)//2]:,}")

def create_neighborhood_comparison():
    """Create comparison across multiple neighborhoods"""
    neighborhoods = ["Beverly_Hills"]  # Add more as data becomes available
    
    all_data = {}
    
    for neighborhood in neighborhoods:
        csv_filename = f'data/{neighborhood}_rentals.csv'
        if os.path.exists(csv_filename):
            df = pd.read_csv(csv_filename)
            all_data[neighborhood] = df
            print(f"Loaded {len(df)} listings for {neighborhood}")
    
    if len(all_data) < 2:
        print("Need data from at least 2 neighborhoods for comparison")
        return
    
    # Create comparison visualization
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Neighborhood Comparison', fontsize=16, fontweight='bold')
    
    # Price comparison
    price_data = []
    labels = []
    
    for neighborhood, df in all_data.items():
        prices = []
        for price in df['price'].dropna():
            price_digits = re.sub(r'[^\d]', '', str(price))
            if price_digits:
                prices.append(int(price_digits))
        
        if prices:
            price_data.append(prices)
            labels.append(neighborhood.replace('_', ' '))
    
    if price_data:
        axes[0, 0].boxplot(price_data, labels=labels)
        axes[0, 0].set_title('Price Comparison')
        axes[0, 0].set_ylabel('Price ($)')
    
    # Number of listings
    listing_counts = [len(df) for df in all_data.values()]
    neighborhood_names = [name.replace('_', ' ') for name in all_data.keys()]
    
    axes[0, 1].bar(neighborhood_names, listing_counts, color='lightblue')
    axes[0, 1].set_title('Number of Listings')
    axes[0, 1].set_ylabel('Count')
    
    # Price ranges
    price_ranges = []
    for neighborhood, df in all_data.items():
        prices = []
        for price in df['price'].dropna():
            price_digits = re.sub(r'[^\d]', '', str(price))
            if price_digits:
                prices.append(int(price_digits))
        
        if prices:
            price_ranges.append(max(prices) - min(prices))
        else:
            price_ranges.append(0)
    
    axes[1, 0].bar(neighborhood_names, price_ranges, color='lightcoral')
    axes[1, 0].set_title('Price Range')
    axes[1, 0].set_ylabel('Price Range ($)')
    
    # Average prices
    avg_prices = []
    for neighborhood, df in all_data.items():
        prices = []
        for price in df['price'].dropna():
            price_digits = re.sub(r'[^\d]', '', str(price))
            if price_digits:
                prices.append(int(price_digits))
        
        if prices:
            avg_prices.append(sum(prices)/len(prices))
        else:
            avg_prices.append(0)
    
    axes[1, 1].bar(neighborhood_names, avg_prices, color='lightgreen')
    axes[1, 1].set_title('Average Price')
    axes[1, 1].set_ylabel('Average Price ($)')
    
    plt.tight_layout()
    
    # Save comparison
    filename = 'data/neighborhood_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Neighborhood comparison saved to {filename}")
    
    plt.show()

def main():
    """Main function"""
    print("=" * 60)
    print("ZILLOW DATA ANALYSIS")
    print("=" * 60)
    
    # Analyze Beverly Hills data
    neighborhood = "Beverly Hills"
    df = load_and_analyze_data(neighborhood)
    
    if df is not None:
        # Generate word cloud from descriptions
        generate_word_cloud_from_descriptions(df, neighborhood)
        
        # Create price analysis
        create_price_analysis(df, neighborhood)
        
        # Create neighborhood comparison (when more data is available)
        create_neighborhood_comparison()
        
        print(f"\nAnalysis completed for {neighborhood}!")
        print("Check the data/ directory for generated visualizations.")
    else:
        print("No data available for analysis.")

if __name__ == "__main__":
    main() 
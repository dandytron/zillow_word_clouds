# Zillow Rental Word Cloud Analyzer

This project scrapes Zillow rental listings from different Los Angeles neighborhoods and creates word clouds to analyze the descriptive language used in each area. The goal WAS to compare socioeconomic differences across neighborhoods through the language used in rental listings. That didn't go so well, mostly because Playwright scrapers are HARD.

Still - I had fun trying and learning, and I built a fun scrollytelling webpage you can find here:

## Features

- **Web Scraping**: Uses Playwright to scrape Zillow rental listings
- **Data Analysis**: Extracts and analyzes rental prices, features, and descriptions
- **Word Cloud Generation**: Creates word clouds from listing descriptions
- **Neighborhood Comparison**: Compares word frequencies across different LA neighborhoods
- **Reproducible**: Runs in Jupyter notebooks for easy reproduction

## Target Neighborhoods

The tool analyzes these Los Angeles neighborhoods:
- Beverly Hills
- Boyle Heights
- Leimert Park
- Sherman Oaks
- Koreatown
- Venice
- Silver Lake
- Echo Park

## Setup Instructions

### 1. Install Python and Jupyter

First, ensure you have Python 3.8+ installed. Then install Jupyter:

```bash
pip install jupyter
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
python -m playwright install chromium
```

### 4. Download NLTK Data (if needed)

The notebook will automatically download required NLTK data, but you can also run:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### 5. Running the Jupyter Notebook

To start working with the project:

1. **Open Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```
   This will open Jupyter in your web browser.

2. **Open the main notebook:**
   - Navigate to `making_clouds.ipynb` for word cloud generation
   - Or open `making_clouds_2.ipynb` for the enhanced version with cohesive colors
   - Or try `playwright_gathering.ipynb` for the web scraping functionality

3. **Run cells step by step:**
   - Click on a cell and press `Shift + Enter` to run it
   - Or use the "Run" button in the toolbar
   - Run cells in order from top to bottom

### 6. Alternative: Run Python Scripts Directly

If you prefer not to use Jupyter, you can run the standalone Python scripts:

```bash
# Generate word clouds from existing data
python generate_wordcloud.py

# Run the main scraper (if you have data to scrape)
python real_scraper_100.py
```

## Project Structure

```
zillow_word_clouds/
├── data/                           # Generated data and word cloud images
├── making_clouds.ipynb             # Main Jupyter notebook for reproducible word cloud generation
├── playwright_gathering.ipynb      # Web scraping notebook
├── generate_wordcloud.py          # Standalone word cloud generator script
├── scraper.py                     # Main scraping script
├── index.html                      # Scrollytelling webpage 
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### 7. Viewing the Scrollytelling Page

To view the interactive web story:

1. **Rename the HTML file:**
   ```bash
   # Rename index.html.html to index.html
   mv index.html.html index.html
   ```

2. **Open in web browser:**
   - Double-click `index.html` to open in your default browser
   - Or serve it locally:
     ```bash
     python -m http.server 8000
     ```
   - Then visit `http://localhost:8000` in your browser

## Usage

### Quick Start with Jupyter

1. **Start Jupyter and open the main notebook:**
   ```bash
   jupyter notebook making_clouds.ipynb
   ```

2. **Generate word clouds from existing data:**
   - Run all cells in `making_clouds.ipynb` or `making_clouds_2.ipynb`
   - The notebook will create word clouds from any CSV files in the `data/` folder

3. **Web scraping (experimental):**
   - Open `playwright_gathering.ipynb` for scraping functionality
   - Note: Scraping success varies due to anti-bot measures

### Quick Start with Python Scripts

```python
# Generate word clouds from existing data
python generate_wordcloud.py

# Run web scraping (if needed)
python real_scraper_100.py
```

### Working with Data

The notebooks include functions for:
- Loading existing CSV data from the `data/` folder
- Generating word clouds with custom color schemes
- Analyzing neighborhood language patterns
- Exporting high-quality PNG and SVG files

## Output Files

The tool generates several types of output:

### Data Files
- `data/{neighborhood}_rentals.csv` - Raw scraped data for each neighborhood

### Visualizations
- `data/{neighborhood}_wordcloud.png` - Word cloud for each neighborhood
- `data/neighborhood_comparison.png` - Comparison charts across neighborhoods

### Data Structure

Each CSV file contains (but wasn't always able to scrape!):
- `address`: Property address
- `price`: Rental price
- `beds`: Number of bedrooms
- `baths`: Number of bathrooms
- `sqft`: Square footage
- `url`: Zillow listing URL
- `description`: Detailed listing description
- `neighborhood`: Neighborhood name
- `scraped_date`: Date and time of scraping

## Anti-Detection Features

The scraper includes several features to avoid bot detection:

- Realistic user agent strings
- Random delays between requests
- Proper browser context settings
- CAPTCHA detection and handling
- Cookie consent handling

## Troubleshooting

### Common Issues

1. **CAPTCHA Detection**: If you encounter CAPTCHA, the browser will open and wait for manual completion
2. **Rate Limiting**: The tool includes random delays, but you may need to increase delays for heavy usage
3. **Browser Issues**: Ensure you have the latest version of Playwright and Chromium installed
4. **Pagination**: Couldn't quite crack this, will hope to improve in a future version.

### Error Handling

The tool DOES have some decent error handling for:
- Network timeouts
- Missing elements
- Invalid data
- Browser crashes

## Ethical Considerations

- Respect Zillow's robots.txt and terms of service
- Use reasonable delays between requests
- Don't overload their servers - just, don't be a jerk and use this tool for evil

## Dependencies

- **Playwright**: Browser automation
- **Pandas**: Data manipulation
- **Matplotlib/Seaborn**: Visualization
- **NLTK**: Natural language processing
- **WordCloud**: Word cloud generation
- **BeautifulSoup**: HTML parsing (backup) - but is a little bit crude by comparison

## License

This project is for educational and research purposes, originally developed for a project to put what I had learned in Columbia Journalism School's Lede Program into (imperfect) practice. Please respect website terms of service and use responsibly.

## Contributing

Feel free to reach out and contribute or suggest improvements!

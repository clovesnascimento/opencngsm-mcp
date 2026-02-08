---
name: webscraping
description: Web scraping with BeautifulSoup and Selenium for dynamic content. Extract data from HTML, handle JavaScript-rendered pages, and parse structured data. Use when user mentions web scraping, data extraction, or crawling websites.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: beautifulsoup4==4.12.2, selenium==4.15.2, requests==2.31.0
compatibility: Requires Chrome/Chromium for Selenium
---

# Web Scraping Skill

## When to use this skill

Use this skill when the user wants to:
- Extract data from websites
- Scrape HTML content
- Handle JavaScript-rendered pages (SPA)
- Parse structured data (tables, lists)
- Crawl multiple pages
- Extract specific elements (text, links, images)

## Setup

1. **Install dependencies:**
   ```bash
   pip install beautifulsoup4==4.12.2 selenium==4.15.2 requests==2.31.0
   ```

2. **Install Chrome/Chromium** (for Selenium):
   - Download from: https://www.google.com/chrome/
   - Or install Chromium: `apt install chromium-browser`

3. **ChromeDriver** (auto-managed by Selenium 4.15+):
   - No manual installation needed
   - Selenium will download compatible driver

## How to use

### Basic scraping (static HTML)

```python
from skills.webscraping.webscraping_skill import WebScrapingSkill

scraper = WebScrapingSkill()

# Scrape static page
data = await scraper.scrape_url(
    url='https://example.com',
    selectors={
        'title': 'h1',
        'description': 'p.description',
        'links': 'a[href]'
    }
)

print(data)
# {'title': 'Example', 'description': '...', 'links': [...]}
```

### Dynamic content (JavaScript)

```python
# Scrape JavaScript-rendered page
data = await scraper.scrape_dynamic(
    url='https://spa-example.com',
    wait_for='div.content',  # Wait for element
    selectors={
        'items': 'div.item',
        'prices': 'span.price'
    }
)
```

### Extract tables

```python
# Extract HTML table
tables = await scraper.extract_tables(
    url='https://example.com/data',
    table_index=0  # First table
)

# Returns list of dicts
for row in tables:
    print(row)
```

### Crawl multiple pages

```python
# Crawl paginated content
results = await scraper.crawl_pages(
    base_url='https://example.com/page/',
    pages=range(1, 11),  # Pages 1-10
    selectors={'title': 'h2', 'content': 'p'}
)
```

## Features

### Static Scraping (BeautifulSoup)
- ✅ Fast HTML parsing
- ✅ CSS selectors
- ✅ XPath support
- ✅ Extract text, attributes, links
- ✅ Parse tables
- ✅ Low resource usage

### Dynamic Scraping (Selenium)
- ✅ JavaScript execution
- ✅ Wait for elements
- ✅ Handle SPAs (Single Page Apps)
- ✅ Scroll pages
- ✅ Click buttons
- ✅ Fill forms

### Data Extraction
- ✅ Custom selectors
- ✅ Multiple elements
- ✅ Nested data
- ✅ Table parsing
- ✅ JSON extraction

## Selectors

### CSS Selectors
```python
selectors = {
    'title': 'h1',                    # Tag
    'subtitle': '.subtitle',          # Class
    'link': '#main-link',             # ID
    'items': 'div.item > p',          # Child
    'prices': 'span[data-price]'      # Attribute
}
```

### XPath (advanced)
```python
xpath = {
    'title': '//h1[@class="main"]',
    'links': '//a[contains(@href, "product")]'
}
```

## Implementation

See [webscraping_skill.py](webscraping_skill.py) for the complete implementation.

## Examples

```python
# Example 1: News scraping
news = await scraper.scrape_url(
    'https://news-site.com',
    selectors={
        'headline': 'h1.headline',
        'author': 'span.author',
        'date': 'time',
        'content': 'div.article-body'
    }
)

# Example 2: E-commerce
products = await scraper.scrape_dynamic(
    'https://shop.com/products',
    wait_for='div.product-card',
    selectors={
        'name': 'h3.product-name',
        'price': 'span.price',
        'image': 'img[src]'
    }
)

# Example 3: Table extraction
data = await scraper.extract_tables(
    'https://stats-site.com',
    table_index=0
)
```

## Troubleshooting

### "ChromeDriver not found"
- Update Selenium: `pip install --upgrade selenium`
- Selenium 4.15+ auto-downloads driver
- Or manually install ChromeDriver

### "Element not found"
- Verify selector is correct
- Use browser DevTools to inspect
- Try waiting longer for dynamic content

### "JavaScript not executing"
- Use `scrape_dynamic()` instead of `scrape_url()`
- Increase wait time
- Check if site blocks headless browsers

### "Rate limiting / blocked"
- Add delays between requests
- Use rotating user agents
- Respect robots.txt
- Consider using proxies

## Best Practices

- ✅ Respect robots.txt
- ✅ Add delays between requests
- ✅ Use appropriate user agent
- ✅ Handle errors gracefully
- ✅ Cache results when possible
- ⚠️ Check website terms of service
- ⚠️ Don't overload servers

## Security

- ⚠️ Validate URLs before scraping
- ⚠️ Sanitize extracted data
- ⚠️ Be careful with dynamic code execution
- ✅ Use HTTPS when possible

## References

- [BeautifulSoup docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium docs](https://www.selenium.dev/documentation/)
- [CSS Selectors reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)

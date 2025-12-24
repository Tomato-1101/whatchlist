# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraping tool that fetches Japanese stock rankings from multiple financial websites and outputs TradingView-compatible watchlists in `TSE:XXXX,TSE:YYYY,...` format.

## Architecture

### Scraper Design Pattern

All scrapers inherit from an abstract base class (`src/scrapers/base.py`) with three core methods:
- `fetch()`: Page retrieval
- `parse()`: Stock code extraction
- `get_ranking()`: Main orchestration method

This design allows easy addition of new data sources by creating a new scraper class that implements the same interface.

### Data Sources

The project integrates multiple financial websites, each requiring different approaches:

1. **Kabutan** (requests + BeautifulSoup): 5 ranking types
   - Price increase/decrease rate
   - Volume, trading value
   - Active stocks

2. **StockWeather** (requests + BeautifulSoup): 2 ranking types
   - Price change from opening

3. **Kabumap** (requests + BeautifulSoup): 1 ranking type
   - Intraday volatility

4. **Matsui Securities** (Playwright required): 1 ranking type
   - Tick count (requires headless browser due to 403 protection)

### Output Format

All rankings output to `output/watchlist_[ranking_type]_[date].txt` in TradingView format:
```
TSE:7203,TSE:6758,TSE:9984,...
```

## Development Commands

### Environment Setup
```bash
# Create and activate venv
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# For Playwright (Matsui scraper)
playwright install
```

### Running the Tool

#### Interactive Mode (Recommended)
```bash
# Windows
run.bat

# Linux/Mac
./run.sh

# Or directly
python -m src.main
```

Interactive mode provides a menu-driven interface where users can:
1. Select rankings by number (e.g., `1,2,3` for multiple selections)
2. Choose `0` to fetch all rankings
3. Specify the number of stocks to fetch
4. Confirm before execution

#### Command-Line Mode
```bash
# Single ranking
python -m src.main --ranking up --count 50

# Multiple rankings
python -m src.main --ranking up --ranking down --ranking volume

# All rankings
python -m src.main --all
```

## Critical Implementation Constraints

### Website Fragility
Web scraping selectors WILL break when websites update their HTML structure. When fixing a broken scraper:
1. Inspect the target website's current HTML structure
2. Update only the CSS selectors or XPath in the affected scraper
3. Do not change the scraper's interface (keep base class methods intact)

### Anti-Scraping Considerations
- Matsui Securities requires Playwright (headless browser) due to 403 protection
- Implement rate limiting to avoid overwhelming target servers
- Some sites may require login in the future - architecture supports both login and no-login routes

### Module Structure
When implementing scrapers, maintain this structure:
- `src/scrapers/`: One file per data source
- `src/exporters/`: Output format handlers (currently only TradingView)
- `src/config.py`: Centralized configuration (URLs, selectors, rate limits)

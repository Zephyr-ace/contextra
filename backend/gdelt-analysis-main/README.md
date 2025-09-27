# GDELT Analysis Pipeline

A reliable quickstart pipeline for analyzing GDELT data focused on Apple and Google/Alphabet. Fetches data from BigQuery, processes it, and generates insightful visualizations.

## Features

- 🌍 **GDELT Data Access**: Direct connection to BigQuery GDELT public dataset
- 🏢 **Company Focus**: Pre-configured for Apple and Google/Alphabet analysis  
- 📊 **Smart Analytics**: Volume spikes, tone analysis, Goldstein-weighted events
- 📈 **Visualizations**: Time-series, scatter plots, bar charts, and dashboards
- 💾 **Caching**: Efficient data caching to minimize BigQuery usage
- 📤 **Export**: CSV, Excel, and JSON export options

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

### 2. Test the Pipeline

```bash
python main.py --test
```

### 3. Run Analysis

```bash
# Quick analysis with basic plots
python main.py --quick --visualize

# Full analysis with all data sources
python main.py --full --export csv --visualize

# Just get a summary
python main.py --summary
```

## CLI Usage

```bash
python main.py [OPTIONS]

Options:
  --test              Test pipeline connectivity and basic functionality
  --quick             Run quick analysis (events only, basic plots)
  --full              Run full analysis (events + mentions + gkg)
  --refresh           Force refresh cached data
  --export {csv,excel,json}  Export processed data
  --visualize         Generate visualization plots
  --summary           Show analysis summary only
```

## Project Structure

```
gdelt-analysis/
├── src/                    # Core modules
│   ├── config.py          # Configuration and company mappings
│   ├── bigquery_client.py # BigQuery connection and queries
│   ├── data_processor.py  # Data processing and analysis
│   ├── data_fetcher.py    # Data orchestration and caching
│   └── visualizer.py      # Chart and plot generation
├── data/                  # Data storage
│   ├── cache/            # Cached query results
│   └── exports/          # Exported data files
├── vizuals/              # Generated visualizations
│   ├── plots/           # Chart files
│   └── graphs/          # Network graphs (future)
├── tests/               # Test files
├── main.py             # CLI entry point
└── requirements.txt    # Dependencies
```

## Data Sources

- **Events**: Core GDELT events with actors, locations, tone, and Goldstein scale
- **Mentions**: Media mentions and source analysis
- **GKG**: Global Knowledge Graph with themes, entities, and relationships

## Analytics Features

### Volume Analysis
- Daily event counts and trends
- Volume spikes vs 30-day baseline
- Company comparison metrics

### Sentiment Analysis  
- Average tone tracking over time
- Tone extremes identification
- Tone vs volume correlation

### Geopolitical Analysis
- Goldstein scale weighted events
- Top countries and sources
- Event type distribution

## Visualizations

The pipeline generates several types of charts:

1. **Time Series**: Event volumes, tone trends, Goldstein-weighted events
2. **Bar Charts**: Top countries, source domains, company comparisons
3. **Scatter Plots**: Tone vs volume analysis with quadrant identification
4. **Dashboard**: Comprehensive multi-plot overview

## Configuration

### Company Mappings
Edit `src/config.py` to add more companies or modify search patterns:

```python
COMPANY_MAPPINGS = {
    "apple": ["Apple Inc", "AAPL", "iPhone", "iPad", ...],
    "google": ["Google", "Alphabet Inc", "GOOGL", "YouTube", ...]
}
```

### Date Range
Default: Last 90 days. Modify `DAYS_LOOKBACK` in config.py.

## Requirements

- Python 3.8+
- Google Cloud BigQuery access
- Service account credentials with BigQuery permissions

## Caching

- Data is cached for 24 hours to minimize BigQuery usage
- Use `--refresh` to force fresh data fetch
- Cache files stored in `data/cache/`

## Testing

```bash
# Run tests
python -m pytest tests/ -v

# Or run specific test
python tests/test_basic.py
```

## Troubleshooting

1. **Authentication Error**: Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to a valid service account key
2. **No Data Found**: Normal if limited activity for companies in recent period
3. **Query Limits**: GDELT queries are limited to prevent excessive BigQuery usage

## Future Extensions

- Network analysis and connection graphs
- More companies and sectors
- Real-time data streaming
- Advanced NLP sentiment analysis
- Interactive dashboards
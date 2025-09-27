"""Main data fetching and caching orchestration."""

import os
import pandas as pd
import pickle
from datetime import datetime
from typing import Dict, Optional, List
from .bigquery_client import GDELTBigQueryClient
from .data_processor import GDELTDataProcessor
from .config import CACHE_DIR, EXPORT_DIR, COMPANY_MAPPINGS, get_date_range, ensure_directories


class GDELTDataFetcher:
    """Main orchestrator for fetching and processing GDELT data."""
    
    def __init__(self):
        """Initialize fetcher with client and processor."""
        self.bq_client = GDELTBigQueryClient()
        self.processor = GDELTDataProcessor()
        ensure_directories()
        
    def get_cache_path(self, data_type: str, start_date: str, end_date: str) -> str:
        """Generate cache file path for data type and date range."""
        return os.path.join(CACHE_DIR, f"{data_type}_{start_date}_{end_date}.pkl")
        
    def load_from_cache(self, cache_path: str) -> Optional[pd.DataFrame]:
        """Load data from cache if it exists and is recent."""
        if not os.path.exists(cache_path):
            return None
            
        # Check if cache is less than 1 day old
        cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
        if cache_age.days >= 1:
            print(f"Cache expired: {cache_path}")
            return None
            
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            print(f"Loaded from cache: {cache_path}")
            return data
        except Exception as e:
            print(f"Failed to load cache {cache_path}: {e}")
            return None
            
    def save_to_cache(self, data: pd.DataFrame, cache_path: str):
        """Save data to cache."""
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"Saved to cache: {cache_path}")
        except Exception as e:
            print(f"Failed to save cache {cache_path}: {e}")
            
    def fetch_events_data(self, force_refresh: bool = False) -> pd.DataFrame:
        """Fetch and process GDELT events data."""
        start_date, end_date = get_date_range()
        cache_path = self.get_cache_path("events_processed", start_date, end_date)
        
        # Try loading from cache first
        if not force_refresh:
            cached_data = self.load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data
                
        print("Fetching events data from BigQuery...")
        
        # Get all company patterns for query
        all_patterns = []
        for patterns in COMPANY_MAPPINGS.values():
            all_patterns.extend(patterns)
            
        # Fetch raw data
        raw_events = self.bq_client.query_events(all_patterns, start_date, end_date)
        
        if raw_events.empty:
            print("No events data found for the specified period")
            return pd.DataFrame()
            
        print(f"Fetched {len(raw_events)} raw events")
        
        # Process and enrich data
        enriched_events = self.processor.enrich_events_data(raw_events)
        print(f"Processed to {len(enriched_events)} relevant events")
        
        # Aggregate to daily metrics
        daily_metrics = self.processor.aggregate_daily_metrics(enriched_events)
        
        # Calculate volume spikes
        final_data = self.processor.calculate_volume_spikes(daily_metrics)
        
        # Save to cache
        self.save_to_cache(final_data, cache_path)
        
        return final_data
        
    def fetch_mentions_data(self, force_refresh: bool = False) -> pd.DataFrame:
        """Fetch GDELT mentions data (lighter version for prototype)."""
        start_date, end_date = get_date_range()
        cache_path = self.get_cache_path("mentions", start_date, end_date)
        
        if not force_refresh:
            cached_data = self.load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data
                
        print("Fetching mentions data from BigQuery...")
        
        all_patterns = []
        for patterns in COMPANY_MAPPINGS.values():
            all_patterns.extend(patterns)
            
        raw_mentions = self.bq_client.query_mentions(all_patterns, start_date, end_date)
        
        self.save_to_cache(raw_mentions, cache_path)
        return raw_mentions
        
    def fetch_gkg_data(self, force_refresh: bool = False) -> pd.DataFrame:
        """Fetch GDELT GKG data (Global Knowledge Graph)."""
        start_date, end_date = get_date_range()
        cache_path = self.get_cache_path("gkg", start_date, end_date)
        
        if not force_refresh:
            cached_data = self.load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data
                
        print("Fetching GKG data from BigQuery...")
        
        all_patterns = []
        for patterns in COMPANY_MAPPINGS.values():
            all_patterns.extend(patterns)
            
        raw_gkg = self.bq_client.query_gkg(all_patterns, start_date, end_date)
        
        self.save_to_cache(raw_gkg, cache_path)
        return raw_gkg
        
    def get_analysis_summary(self, events_data: pd.DataFrame) -> Dict:
        """Generate analysis summary with key metrics."""
        if events_data.empty:
            return {"error": "No data available for analysis"}
            
        summary = {
            "date_range": f"{events_data['date'].min().strftime('%Y-%m-%d')} to {events_data['date'].max().strftime('%Y-%m-%d')}",
            "total_days": events_data['date'].nunique(),
            "companies": list(events_data['primary_company'].unique()),
            "total_events": events_data['event_count'].sum(),
            "avg_daily_events": events_data['event_count'].mean(),
        }
        
        # Company-specific metrics
        company_stats = {}
        for company in events_data['primary_company'].unique():
            company_data = events_data[events_data['primary_company'] == company]
            
            company_stats[company] = {
                "total_events": company_data['event_count'].sum(),
                "avg_tone": company_data['AvgTone_mean'].mean(),
                "avg_goldstein": company_data['GoldsteinScale_mean'].mean(),
                "max_spike": company_data['spike_ratio'].max() if 'spike_ratio' in company_data else 0,
                "days_with_data": len(company_data)
            }
            
        summary["company_stats"] = company_stats
        
        return summary
        
    def export_data(self, events_data: pd.DataFrame, format: str = "csv"):
        """Export processed data to specified format."""
        if events_data.empty:
            print("No data to export")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "csv":
            export_path = os.path.join(EXPORT_DIR, f"gdelt_analysis_{timestamp}.csv")
            events_data.to_csv(export_path, index=False)
            print(f"Data exported to: {export_path}")
            
        elif format == "excel":
            export_path = os.path.join(EXPORT_DIR, f"gdelt_analysis_{timestamp}.xlsx")
            events_data.to_excel(export_path, index=False)
            print(f"Data exported to: {export_path}")
            
        elif format == "json":
            export_path = os.path.join(EXPORT_DIR, f"gdelt_analysis_{timestamp}.json")
            events_data.to_json(export_path, orient='records', date_format='iso')
            print(f"Data exported to: {export_path}")
            
    def test_pipeline(self) -> bool:
        """Test the entire pipeline with minimal data."""
        print("Testing GDELT pipeline...")
        
        try:
            # Test BigQuery connection
            if not self.bq_client.test_connection():
                print("❌ BigQuery connection failed")
                return False
            print("✅ BigQuery connection successful")
            
            # Test data fetching (small sample)
            print("Testing data fetch...")
            events_data = self.fetch_events_data()
            
            if events_data.empty:
                print("⚠️  No events data found (this may be normal)")
            else:
                print(f"✅ Fetched and processed {len(events_data)} records")
                
            print("✅ Pipeline test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Pipeline test failed: {e}")
            return False
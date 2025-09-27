"""Data processing and company matching functionality."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
from .config import COMPANY_MAPPINGS


class GDELTDataProcessor:
    """Process and analyze GDELT data with company matching."""
    
    def __init__(self):
        """Initialize processor with company mappings."""
        self.company_mappings = COMPANY_MAPPINGS
        
    def match_company(self, text: str) -> str:
        """Match text to company based on name patterns."""
        if pd.isna(text):
            return "unknown"
            
        text_upper = str(text).upper()
        
        for company, patterns in self.company_mappings.items():
            for pattern in patterns:
                if pattern.upper() in text_upper:
                    return company
                    
        return "unknown"
        
    def enrich_events_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich events data with company matching and aggregations."""
        if df.empty:
            return df
            
        # Convert SQLDATE to datetime
        df['date'] = pd.to_datetime(df['SQLDATE'], format='%Y%m%d', errors='coerce')
        
        # Match companies in Actor1Name and Actor2Name
        df['company_actor1'] = df['Actor1Name'].apply(self.match_company)
        df['company_actor2'] = df['Actor2Name'].apply(self.match_company)
        
        # Create primary company field (prefer actor1, fallback to actor2)
        df['primary_company'] = df.apply(
            lambda row: row['company_actor1'] if row['company_actor1'] != 'unknown' 
            else row['company_actor2'], axis=1
        )
        
        # Filter to only rows with known companies
        df = df[df['primary_company'] != 'unknown'].copy()
        
        # Convert numeric columns
        numeric_cols = ['GoldsteinScale', 'NumMentions', 'AvgTone']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
        
    def aggregate_daily_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate events data to daily company metrics."""
        if df.empty:
            return pd.DataFrame()
            
        daily_agg = df.groupby(['date', 'primary_company']).agg({
            'GoldsteinScale': ['mean', 'std', 'min', 'max'],
            'NumMentions': ['sum', 'mean'],
            'AvgTone': ['mean', 'std', 'min', 'max'],
            'EventCode': 'count',
            'QuadClass': lambda x: x.mode().iloc[0] if not x.empty else None
        }).round(3)
        
        # Flatten column names
        daily_agg.columns = ['_'.join(col).strip() for col in daily_agg.columns]
        daily_agg = daily_agg.reset_index()
        
        # Rename for clarity
        daily_agg = daily_agg.rename(columns={
            'EventCode_count': 'event_count',
            'NumMentions_sum': 'total_mentions',
            'NumMentions_mean': 'avg_mentions_per_event'
        })
        
        return daily_agg
        
    def calculate_volume_spikes(self, df: pd.DataFrame, baseline_days: int = 30) -> pd.DataFrame:
        """Calculate volume spikes vs baseline for each company."""
        if df.empty:
            return pd.DataFrame()
            
        results = []
        
        for company in df['primary_company'].unique():
            company_data = df[df['primary_company'] == company].copy()
            company_data = company_data.sort_values('date')
            
            # Calculate rolling baseline
            company_data['baseline_events'] = company_data['event_count'].rolling(
                window=baseline_days, min_periods=1
            ).mean()
            
            # Calculate spike ratio
            company_data['spike_ratio'] = (
                company_data['event_count'] / company_data['baseline_events']
            ).replace([np.inf, -np.inf], 0)
            
            results.append(company_data)
            
        return pd.concat(results, ignore_index=True) if results else pd.DataFrame()
        
    def get_top_countries_sources(self, df: pd.DataFrame, top_n: int = 10) -> Dict[str, pd.DataFrame]:
        """Get top countries and sources for each company."""
        results = {}
        
        for company in df['primary_company'].unique():
            company_data = df[df['primary_company'] == company]
            
            # Top countries by event count
            country_counts = pd.concat([
                company_data['Actor1CountryCode'].value_counts(),
                company_data['Actor2CountryCode'].value_counts(),
                company_data['ActionGeo_CountryCode'].value_counts()
            ]).groupby(level=0).sum().sort_values(ascending=False).head(top_n)
            
            # Top source domains
            if 'SOURCEURL' in company_data.columns:
                company_data['domain'] = company_data['SOURCEURL'].str.extract(
                    r'https?://(?:www\.)?([^/]+)'
                )[0]
                domain_counts = company_data['domain'].value_counts().head(top_n)
            else:
                domain_counts = pd.Series(dtype='int64')
            
            results[company] = {
                'countries': country_counts,
                'domains': domain_counts
            }
            
        return results
        
    def analyze_tone_extremes(self, df: pd.DataFrame, percentile: int = 95) -> pd.DataFrame:
        """Identify tone extremes (very positive/negative) for each company."""
        if df.empty:
            return pd.DataFrame()
            
        results = []
        
        for company in df['primary_company'].unique():
            company_data = df[df['primary_company'] == company]
            
            if company_data.empty:
                continue
                
            # Calculate percentile thresholds
            low_threshold = np.percentile(company_data['AvgTone_mean'].dropna(), 100 - percentile)
            high_threshold = np.percentile(company_data['AvgTone_mean'].dropna(), percentile)
            
            # Mark extremes
            company_data = company_data.copy()
            company_data['tone_extreme'] = 'normal'
            company_data.loc[company_data['AvgTone_mean'] <= low_threshold, 'tone_extreme'] = 'very_negative'
            company_data.loc[company_data['AvgTone_mean'] >= high_threshold, 'tone_extreme'] = 'very_positive'
            
            results.append(company_data)
            
        return pd.concat(results, ignore_index=True) if results else pd.DataFrame()
        
    def prepare_scatter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for tone vs volume scatter plot."""
        if df.empty:
            return pd.DataFrame()
            
        scatter_data = df[['date', 'primary_company', 'event_count', 'AvgTone_mean']].copy()
        scatter_data = scatter_data.dropna()
        
        # Add quadrants for interpretation
        median_volume = scatter_data['event_count'].median()
        median_tone = scatter_data['AvgTone_mean'].median()
        
        scatter_data['quadrant'] = 'low_volume_neutral'
        
        mask_high_vol_neg = (scatter_data['event_count'] > median_volume) & (scatter_data['AvgTone_mean'] < median_tone)
        mask_high_vol_pos = (scatter_data['event_count'] > median_volume) & (scatter_data['AvgTone_mean'] > median_tone)
        mask_low_vol_neg = (scatter_data['event_count'] <= median_volume) & (scatter_data['AvgTone_mean'] < median_tone)
        
        scatter_data.loc[mask_high_vol_neg, 'quadrant'] = 'loud_and_negative'
        scatter_data.loc[mask_high_vol_pos, 'quadrant'] = 'loud_and_positive'
        scatter_data.loc[mask_low_vol_neg, 'quadrant'] = 'quiet_and_negative'
        
        return scatter_data
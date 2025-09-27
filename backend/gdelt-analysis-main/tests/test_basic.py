"""Basic tests for GDELT analysis pipeline."""

import sys
import os
import pytest
import pandas as pd
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import COMPANY_MAPPINGS, get_date_range, ensure_directories
from src.data_processor import GDELTDataProcessor
from src.visualizer import GDELTVisualizer


def test_company_mappings():
    """Test that company mappings are properly configured."""
    assert 'apple' in COMPANY_MAPPINGS
    assert 'google' in COMPANY_MAPPINGS
    assert len(COMPANY_MAPPINGS['apple']) > 0
    assert len(COMPANY_MAPPINGS['google']) > 0
    assert 'Apple Inc' in COMPANY_MAPPINGS['apple']
    assert 'Google' in COMPANY_MAPPINGS['google']


def test_date_range():
    """Test date range generation."""
    start_date, end_date = get_date_range()
    assert len(start_date) == 8  # YYYYMMDD format
    assert len(end_date) == 8
    assert start_date <= end_date
    assert start_date.isdigit()
    assert end_date.isdigit()


def test_ensure_directories():
    """Test directory creation."""
    try:
        ensure_directories()
        assert os.path.exists('data')
        assert os.path.exists('data/cache')
        assert os.path.exists('data/exports')
    except Exception as e:
        pytest.fail(f"Directory creation failed: {e}")


class TestGDELTDataProcessor:
    """Test data processing functionality."""
    
    def setup_method(self):
        """Setup test processor."""
        self.processor = GDELTDataProcessor()
    
    def test_match_company(self):
        """Test company matching logic."""
        # Test Apple matches
        assert self.processor.match_company("Apple Inc") == "apple"
        assert self.processor.match_company("iPhone sales") == "apple"
        assert self.processor.match_company("AAPL") == "apple"
        
        # Test Google matches  
        assert self.processor.match_company("Google LLC") == "google"
        assert self.processor.match_company("YouTube") == "google"
        assert self.processor.match_company("GOOGL") == "google"
        
        # Test unknown
        assert self.processor.match_company("Microsoft") == "unknown"
        assert self.processor.match_company("") == "unknown"
        assert self.processor.match_company(None) == "unknown"
    
    def test_enrich_events_data_empty(self):
        """Test enrichment with empty data."""
        df = pd.DataFrame()
        result = self.processor.enrich_events_data(df)
        assert result.empty
    
    def test_enrich_events_data_sample(self):
        """Test enrichment with sample data."""
        sample_data = pd.DataFrame({
            'SQLDATE': ['20240101', '20240102'],
            'Actor1Name': ['Apple Inc', 'Google LLC'],
            'Actor2Name': ['', ''],
            'EventCode': ['010', '020'],
            'GoldsteinScale': [1.5, -2.0],
            'NumMentions': [10, 15],
            'AvgTone': [2.5, -1.0]
        })
        
        result = self.processor.enrich_events_data(sample_data)
        
        assert 'date' in result.columns
        assert 'company_actor1' in result.columns
        assert 'primary_company' in result.columns
        assert len(result) > 0
        assert result['company_actor1'].iloc[0] == 'apple'
        assert result['company_actor1'].iloc[1] == 'google'
    
    def test_aggregate_daily_metrics_empty(self):
        """Test aggregation with empty data."""
        df = pd.DataFrame()
        result = self.processor.aggregate_daily_metrics(df)
        assert result.empty


class TestGDELTVisualizer:
    """Test visualization functionality."""
    
    def setup_method(self):
        """Setup test visualizer."""
        self.visualizer = GDELTVisualizer("test_output")
    
    def test_visualizer_init(self):
        """Test visualizer initialization."""
        assert self.visualizer.output_dir == "test_output"
        assert 'apple' in self.visualizer.colors
        assert 'google' in self.visualizer.colors
    
    def test_plot_with_empty_data(self):
        """Test plotting functions handle empty data gracefully."""
        df = pd.DataFrame()
        
        # These should return "No data" messages, not crash
        result1 = self.visualizer.plot_volume_trends(df)
        result2 = self.visualizer.plot_tone_trends(df)
        result3 = self.visualizer.plot_scatter_tone_volume(df)
        
        assert "No data" in result1
        assert "No data" in result2 or "AvgTone_mean" in result2
        assert "No data" in result3


@pytest.fixture
def sample_events_data():
    """Create sample events data for testing."""
    return pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10, freq='D'),
        'primary_company': ['apple', 'google'] * 5,
        'event_count': [5, 8, 3, 12, 7, 9, 4, 6, 11, 8],
        'AvgTone_mean': [1.2, -0.5, 2.1, -1.8, 0.3, 1.1, -0.2, 0.8, -2.1, 1.5],
        'GoldsteinScale_mean': [2.1, -1.2, 1.8, -0.5, 0.8, 1.5, -0.8, 1.2, -1.5, 0.9],
        'NumMentions_sum': [100, 150, 80, 200, 120, 180, 90, 110, 220, 160]
    })


def test_data_processing_pipeline(sample_events_data):
    """Test the complete data processing pipeline."""
    processor = GDELTDataProcessor()
    
    # Test spike calculation
    result = processor.calculate_volume_spikes(sample_events_data)
    assert 'spike_ratio' in result.columns
    assert len(result) == len(sample_events_data)
    
    # Test scatter data preparation
    scatter_data = processor.prepare_scatter_data(sample_events_data)
    assert 'quadrant' in scatter_data.columns
    assert not scatter_data.empty


def test_visualization_pipeline(sample_events_data):
    """Test visualization with sample data."""
    visualizer = GDELTVisualizer("test_output")
    
    # Test that plots are created without errors
    try:
        plot1 = visualizer.plot_volume_trends(sample_events_data)
        plot2 = visualizer.plot_tone_trends(sample_events_data)
        plot3 = visualizer.plot_company_comparison_summary(sample_events_data)
        
        # Should return filenames, not error messages
        assert "No data" not in plot1
        assert "No data" not in plot2
        assert "No data" not in plot3
        
    except Exception as e:
        pytest.fail(f"Visualization failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
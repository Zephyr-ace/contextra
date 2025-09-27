"""Visualization functions for GDELT analysis."""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class GDELTVisualizer:
    """Create visualizations for GDELT analysis results."""
    
    def __init__(self, output_dir: str = "vizuals/plots"):
        """Initialize visualizer with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up consistent styling
        self.colors = {
            'apple': '#007AFF',
            'google': '#4285F4',
            'unknown': '#8E8E93'
        }
        
        self.figsize = (12, 8)
        
    def save_plot(self, fig, filename: str, dpi: int = 300):
        """Save plot with consistent formatting."""
        filepath = os.path.join(self.output_dir, filename)
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        print(f"Saved plot: {filepath}")
        
    def plot_volume_trends(self, df: pd.DataFrame) -> str:
        """Create time series plot of event volumes by company."""
        if df.empty:
            return "No data for volume trends"
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, sharex=True)
        
        # Plot 1: Event counts over time
        for company in df['primary_company'].unique():
            company_data = df[df['primary_company'] == company]
            ax1.plot(company_data['date'], company_data['event_count'], 
                    label=company.title(), 
                    color=self.colors.get(company, '#333333'),
                    linewidth=2, marker='o', markersize=3)
        
        ax1.set_title('Daily Event Counts by Company', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Event Count', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Volume spikes (ratio to baseline)
        if 'spike_ratio' in df.columns:
            for company in df['primary_company'].unique():
                company_data = df[df['primary_company'] == company]
                ax2.plot(company_data['date'], company_data['spike_ratio'], 
                        label=company.title(),
                        color=self.colors.get(company, '#333333'),
                        linewidth=2, marker='s', markersize=3)
            
            ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Baseline')
            ax2.set_title('Volume Spike Ratio (vs 30-day baseline)', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Spike Ratio', fontsize=12)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        filename = f"volume_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.save_plot(fig, filename)
        return filename
        
    def plot_tone_trends(self, df: pd.DataFrame) -> str:
        """Create time series plot of average tone by company."""
        if df.empty or 'AvgTone_mean' not in df.columns:
            return "No data for tone trends"
            
        fig, ax = plt.subplots(figsize=self.figsize)
        
        for company in df['primary_company'].unique():
            company_data = df[df['primary_company'] == company]
            ax.plot(company_data['date'], company_data['AvgTone_mean'], 
                   label=company.title(),
                   color=self.colors.get(company, '#333333'),
                   linewidth=2, marker='o', markersize=3)
        
        # Add reference lines
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5, label='Neutral')
        ax.axhline(y=2, color='green', linestyle='--', alpha=0.7, label='Positive threshold')
        ax.axhline(y=-2, color='red', linestyle='--', alpha=0.7, label='Negative threshold')
        
        ax.set_title('Average Tone Trends by Company', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Average Tone', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        filename = f"tone_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.save_plot(fig, filename)
        return filename
        
    def plot_goldstein_events(self, df: pd.DataFrame) -> str:
        """Create Goldstein scale weighted events visualization."""
        if df.empty or 'GoldsteinScale_mean' not in df.columns:
            return "No data for Goldstein events"
            
        fig, ax = plt.subplots(figsize=self.figsize)
        
        for company in df['primary_company'].unique():
            company_data = df[df['primary_company'] == company]
            
            # Weight events by Goldstein scale
            weighted_events = company_data['event_count'] * company_data['GoldsteinScale_mean']
            
            ax.plot(company_data['date'], weighted_events,
                   label=company.title(),
                   color=self.colors.get(company, '#333333'),
                   linewidth=2, marker='o', markersize=3)
        
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        ax.set_title('Goldstein-Weighted Events by Company', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Weighted Event Score', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        filename = f"goldstein_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.save_plot(fig, filename)
        return filename
        
    def plot_top_countries_bar(self, country_data: Dict) -> str:
        """Create bar charts of top countries by company."""
        if not country_data:
            return "No country data available"
            
        n_companies = len(country_data)
        fig, axes = plt.subplots(n_companies, 1, figsize=(12, 6 * n_companies))
        
        if n_companies == 1:
            axes = [axes]
            
        for i, (company, data) in enumerate(country_data.items()):
            if 'countries' not in data or data['countries'].empty:
                continue
                
            countries = data['countries'].head(10)
            axes[i].bar(range(len(countries)), countries.values,
                       color=self.colors.get(company, '#333333'), alpha=0.7)
            axes[i].set_title(f'Top Countries for {company.title()}', 
                             fontsize=14, fontweight='bold')
            axes[i].set_ylabel('Event Count', fontsize=12)
            axes[i].set_xticks(range(len(countries)))
            axes[i].set_xticklabels(countries.index, rotation=45)
            axes[i].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        filename = f"top_countries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.save_plot(fig, filename)
        return filename
        
    def plot_scatter_tone_volume(self, df: pd.DataFrame) -> str:
        """Create scatter plot of tone vs volume to identify patterns."""
        if df.empty:
            return "No data for scatter plot"
            
        # Prepare scatter data
        from .data_processor import GDELTDataProcessor
        processor = GDELTDataProcessor()
        scatter_data = processor.prepare_scatter_data(df)
        
        if scatter_data.empty:
            return "No data for scatter plot after processing"
            
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot by company with different colors
        for company in scatter_data['primary_company'].unique():
            company_data = scatter_data[scatter_data['primary_company'] == company]
            ax.scatter(company_data['AvgTone_mean'], company_data['event_count'],
                      label=company.title(),
                      color=self.colors.get(company, '#333333'),
                      alpha=0.6, s=50)
        
        # Add quadrant lines
        ax.axhline(y=scatter_data['event_count'].median(), color='gray', 
                  linestyle='--', alpha=0.5, label='Median Volume')
        ax.axvline(x=scatter_data['AvgTone_mean'].median(), color='gray', 
                  linestyle='--', alpha=0.5, label='Median Tone')
        
        # Annotate quadrants
        ax.text(0.05, 0.95, 'Quiet &\\nNegative', transform=ax.transAxes, 
               fontsize=10, alpha=0.7, ha='left', va='top')
        ax.text(0.95, 0.95, 'Loud &\\nPositive', transform=ax.transAxes, 
               fontsize=10, alpha=0.7, ha='right', va='top')
        ax.text(0.95, 0.05, 'Loud &\\nNegative', transform=ax.transAxes, 
               fontsize=10, alpha=0.7, ha='right', va='bottom')
        
        ax.set_title('Tone vs Volume Analysis', fontsize=14, fontweight='bold')
        ax.set_xlabel('Average Tone', fontsize=12)
        ax.set_ylabel('Event Count', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = f"tone_volume_scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.save_plot(fig, filename)
        return filename
        
    def create_dashboard(self, df: pd.DataFrame, country_data: Dict = None) -> List[str]:
        """Create a comprehensive dashboard with multiple visualizations."""
        if df.empty:
            return ["No data available for dashboard"]
            
        plots = []
        
        # Time series plots
        plots.append(self.plot_volume_trends(df))
        plots.append(self.plot_tone_trends(df))
        plots.append(self.plot_goldstein_events(df))
        
        # Scatter plot
        plots.append(self.plot_scatter_tone_volume(df))
        
        # Bar charts if country data available
        if country_data:
            plots.append(self.plot_top_countries_bar(country_data))
        
        return [plot for plot in plots if plot and "No data" not in plot]
        
    def plot_company_comparison_summary(self, df: pd.DataFrame) -> str:
        """Create a summary comparison plot of key metrics by company."""
        if df.empty:
            return "No data for company comparison"
            
        # Calculate summary statistics by company
        summary_stats = df.groupby('primary_company').agg({
            'event_count': ['sum', 'mean'],
            'AvgTone_mean': 'mean',
            'GoldsteinScale_mean': 'mean',
            'spike_ratio': 'max' if 'spike_ratio' in df.columns else lambda x: 0
        }).round(2)
        
        summary_stats.columns = ['Total Events', 'Avg Daily Events', 'Avg Tone', 'Avg Goldstein', 'Max Spike']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        companies = summary_stats.index
        
        # Total events
        bars1 = ax1.bar(companies, summary_stats['Total Events'], 
                       color=[self.colors.get(c, '#333333') for c in companies], alpha=0.7)
        ax1.set_title('Total Events by Company', fontweight='bold')
        ax1.set_ylabel('Total Events')
        
        # Average tone
        bars2 = ax2.bar(companies, summary_stats['Avg Tone'], 
                       color=[self.colors.get(c, '#333333') for c in companies], alpha=0.7)
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax2.set_title('Average Tone by Company', fontweight='bold')
        ax2.set_ylabel('Average Tone')
        
        # Average Goldstein
        bars3 = ax3.bar(companies, summary_stats['Avg Goldstein'], 
                       color=[self.colors.get(c, '#333333') for c in companies], alpha=0.7)
        ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax3.set_title('Average Goldstein Scale by Company', fontweight='bold')
        ax3.set_ylabel('Average Goldstein Scale')
        
        # Max spike ratio
        bars4 = ax4.bar(companies, summary_stats['Max Spike'], 
                       color=[self.colors.get(c, '#333333') for c in companies], alpha=0.7)
        ax4.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Baseline')
        ax4.set_title('Maximum Volume Spike by Company', fontweight='bold')
        ax4.set_ylabel('Max Spike Ratio')
        
        # Add value labels on bars
        for ax, bars in [(ax1, bars1), (ax2, bars2), (ax3, bars3), (ax4, bars4)]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        filename = f"company_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.save_plot(fig, filename)
        return filename
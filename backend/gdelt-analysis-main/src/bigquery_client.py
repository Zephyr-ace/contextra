"""BigQuery client for GDELT data access."""

import os
from typing import Optional
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from .config import PROJECT_ID, get_date_range


class GDELTBigQueryClient:
    """Client for accessing GDELT data from BigQuery."""
    
    def __init__(self):
        """Initialize BigQuery client with authentication."""
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
            
        self.client = bigquery.Client()
        self.project_id = PROJECT_ID
        
    def test_connection(self) -> bool:
        """Test BigQuery connection and access to GDELT dataset."""
        try:
            query = f"""
            SELECT COUNT(*) as count
            FROM `{self.project_id}.gdeltv2.events`
            WHERE SQLDATE >= CAST(FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)) AS INT64)
            LIMIT 1
            """
            result = self.client.query(query).to_dataframe()
            return len(result) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
            
    def query_events(self, companies: list, start_date: str, end_date: str) -> pd.DataFrame:
        """Query GDELT events for specified companies and date range."""
        company_filter = " OR ".join([
            f"UPPER(Actor1Name) LIKE UPPER('%{company}%') OR UPPER(Actor2Name) LIKE UPPER('%{company}%')"
            for company in companies
        ])
        
        query = f"""
        SELECT 
            SQLDATE,
            Actor1Name,
            Actor2Name, 
            EventCode,
            EventRootCode,
            QuadClass,
            GoldsteinScale,
            NumMentions,
            AvgTone,
            Actor1CountryCode,
            Actor2CountryCode,
            ActionGeo_CountryCode,
            SOURCEURL
        FROM `{self.project_id}.gdeltv2.events`
        WHERE SQLDATE BETWEEN CAST('{start_date}' AS INT64) AND CAST('{end_date}' AS INT64)
        AND ({company_filter})
        ORDER BY SQLDATE DESC
        """
        
        return self.client.query(query).to_dataframe()
        
    def query_mentions(self, companies: list, start_date: str, end_date: str) -> pd.DataFrame:
        """Query GDELT mentions for specified companies and date range."""
        company_filter = " OR ".join([
            f"UPPER(SOURCEURL) LIKE UPPER('%{company}%')"
            for company in companies
        ])
        
        query = f"""
        SELECT 
            DATE,
            MentionType,
            MentionSourceName,
            MentionIdentifier,
            SentenceID,
            Actor1CharOffset,
            Actor2CharOffset,
            ActionCharOffset,
            InRawText,
            Confidence,
            MentionDocLen,
            MentionDocTone
        FROM `{self.project_id}.gdeltv2.mentions`
        WHERE DATE BETWEEN '{start_date}' AND '{end_date}'
        AND ({company_filter})
        LIMIT 10000
        """
        
        return self.client.query(query).to_dataframe()
        
    def query_gkg(self, companies: list, start_date: str, end_date: str) -> pd.DataFrame:
        """Query GDELT GKG (Global Knowledge Graph) for specified companies."""
        company_filter = " OR ".join([
            f"UPPER(DocumentIdentifier) LIKE UPPER('%{company}%') OR UPPER(Themes) LIKE UPPER('%{company}%')"
            for company in companies
        ])
        
        query = f"""
        SELECT 
            DATE,
            DocumentIdentifier,
            Themes,
            Locations,
            Persons,
            Organizations,
            Tone,
            Counts,
            SharingImage,
            RelatedImages,
            SocialImageEmbeds,
            SocialVideoEmbeds,
            Quotations,
            AllNames
        FROM `{self.project_id}.gdeltv2.gkg_partitioned`
        WHERE DATE(_PARTITIONTIME) BETWEEN '{start_date}' AND '{end_date}'
        AND ({company_filter})
        LIMIT 5000
        """

        return self.client.query(query).to_dataframe()

    def cooccurrence(self, entity_a: str, entity_b: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> int:
        """
        Count document-level co-occurrences of two entities in GDELT GKG.

        Args:
            entity_a: First entity to search for
            entity_b: Second entity to search for
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            Number of GKG documents where both entities appear

        Raises:
            ValueError: If entities are empty or date format is invalid
            Exception: If BigQuery query fails
        """
        if not entity_a or not entity_a.strip():
            raise ValueError("entity_a cannot be empty")
        if not entity_b or not entity_b.strip():
            raise ValueError("entity_b cannot be empty")

        # Validate date formats if provided
        if start_date:
            try:
                from datetime import datetime
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("start_date must be in YYYY-MM-DD format")

        if end_date:
            try:
                from datetime import datetime
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("end_date must be in YYYY-MM-DD format")
        query = """
        DECLARE a_norm STRING DEFAULT LOWER(TRIM(@a));
        DECLARE b_norm STRING DEFAULT LOWER(TRIM(@b));
        WITH g AS (
          SELECT
            SPLIT(LOWER(IFNULL(V2Persons,'')),';') persons,
            SPLIT(LOWER(IFNULL(V2Organizations,'')),';') orgs,
            SPLIT(LOWER(IFNULL(V2Locations,'')),';') locs,
            SPLIT(LOWER(IFNULL(V2Themes,'')),';') themes
          FROM `gdelt-bq.gdeltv2.gkg`
          WHERE DATE(date) BETWEEN IFNULL(@start, DATE '1970-01-01') AND IFNULL(@end, CURRENT_DATE())
        )
        SELECT COUNT(*) cooccurrence
        FROM g
        WHERE (a_norm IN UNNEST(persons) OR a_norm IN UNNEST(orgs) OR a_norm IN UNNEST(locs) OR a_norm IN UNNEST(themes))
          AND (b_norm IN UNNEST(persons) OR b_norm IN UNNEST(orgs) OR b_norm IN UNNEST(locs) OR b_norm IN UNNEST(themes));
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("a", "STRING", entity_a),
                bigquery.ScalarQueryParameter("b", "STRING", entity_b),
                bigquery.ScalarQueryParameter("start", "DATE", start_date),
                bigquery.ScalarQueryParameter("end", "DATE", end_date),
            ]
        )

        try:
            result = self.client.query(query, job_config=job_config).to_dataframe()
            if result.empty:
                return 0
            return int(result.iloc[0]['cooccurrence'])
        except Exception as e:
            raise Exception(f"BigQuery execution failed: {str(e)}")
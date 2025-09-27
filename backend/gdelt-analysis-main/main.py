#!/usr/bin/env python3
"""
GDELT Cooccurrence Analysis - Simple standalone implementation
"""

import os
import random
from typing import Optional, Dict, Any, List
from google.cloud import bigquery
from llm.llm_OA import LLM_OA, CausalJudgment
from llm.prompt import prompt


def cooccurrence(entity_a: str, entity_b: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Count document-level co-occurrences of two entities in GDELT GKG.

    Args:
        entity_a: First entity to search for
        entity_b: Second entity to search for
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        Dictionary containing:
        - cooccurrence: Number of GKG documents where both entities appear
        - entity_a_count: Number of documents containing entity_a
        - entity_b_count: Number of documents containing entity_b
        - normalized_cooccurrence: Co-occurrence normalized by individual occurrences
        - total_documents: Total documents in the time period

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

    # Initialize BigQuery client
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    client = bigquery.Client()

    query = """
    DECLARE a_norm STRING DEFAULT LOWER(TRIM(@a));
    DECLARE b_norm STRING DEFAULT LOWER(TRIM(@b));
    WITH docs AS (
      SELECT
        GKGRECORDID,
        CASE WHEN (
          LOWER(IFNULL(V2Persons,'')) LIKE CONCAT('%', a_norm, '%')
          OR LOWER(IFNULL(V2Organizations,'')) LIKE CONCAT('%', a_norm, '%')
          OR LOWER(IFNULL(V2Locations,'')) LIKE CONCAT('%', a_norm, '%')
          OR LOWER(IFNULL(V2Themes,'')) LIKE CONCAT('%', a_norm, '%')
        ) THEN 1 ELSE 0 END as has_entity_a,
        CASE WHEN (
          LOWER(IFNULL(V2Persons,'')) LIKE CONCAT('%', b_norm, '%')
          OR LOWER(IFNULL(V2Organizations,'')) LIKE CONCAT('%', b_norm, '%')
          OR LOWER(IFNULL(V2Locations,'')) LIKE CONCAT('%', b_norm, '%')
          OR LOWER(IFNULL(V2Themes,'')) LIKE CONCAT('%', b_norm, '%')
        ) THEN 1 ELSE 0 END as has_entity_b
      FROM `gdelt-bq.gdeltv2.gkg_partitioned`
      WHERE DATE(_PARTITIONTIME) BETWEEN IFNULL(@start, DATE '1970-01-01') AND IFNULL(@end, CURRENT_DATE())
    )
    SELECT
      SUM(CASE WHEN has_entity_a = 1 AND has_entity_b = 1 THEN 1 ELSE 0 END) as cooccurrence,
      SUM(has_entity_a) as entity_a_count,
      SUM(has_entity_b) as entity_b_count,
      COUNT(*) as total_documents
    FROM docs;
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
        result = client.query(query, job_config=job_config).to_dataframe()
        if result.empty:
            return {
                'cooccurrence': 0,
                'entity_a_count': 0,
                'entity_b_count': 0,
                'normalized_cooccurrence': 0.0,
                'total_documents': 0
            }

        row = result.iloc[0]
        cooccur = int(row['cooccurrence'])
        count_a = int(row['entity_a_count'])
        count_b = int(row['entity_b_count'])
        total_docs = int(row['total_documents'])

        # Calculate normalized co-occurrence: Jaccard similarity
        # cooccurrence / (entity_a_count + entity_b_count - cooccurrence)
        if count_a > 0 and count_b > 0:
            normalized = cooccur / (count_a + count_b - cooccur) if (count_a + count_b - cooccur) > 0 else 0.0
        else:
            normalized = 0.0

        return {
            'cooccurrence': cooccur,
            'entity_a_count': count_a,
            'entity_b_count': count_b,
            'normalized_cooccurrence': round(normalized, 4),
            'total_documents': total_docs
        }
    except Exception as e:
        raise Exception(f"BigQuery execution failed: {str(e)}")


def hybrid_cooccurrence(entity_a: str, entity_b: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Count document-level co-occurrences using hybrid approach:
    - Structured entity fields (V2Persons, V2Organizations, V2Locations, V2Themes)
    - PLUS regex matching in DocumentIdentifier (URLs/headlines)

    Args:
        entity_a: First entity to search for
        entity_b: Second entity to search for
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        Dictionary containing:
        - cooccurrence: Number of GKG documents where both entities appear
        - entity_a_count: Number of documents containing entity_a
        - entity_b_count: Number of documents containing entity_b
        - normalized_cooccurrence: Co-occurrence normalized by individual occurrences
        - total_documents: Total documents in the time period

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

    # Initialize BigQuery client
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    client = bigquery.Client()

    query = """
    DECLARE a_norm STRING DEFAULT LOWER(TRIM(@a));
    DECLARE b_norm STRING DEFAULT LOWER(TRIM(@b));
    WITH docs AS (
      SELECT
        GKGRECORDID,
        -- Structured entity matching (strict mode)
        CASE WHEN (
          LOWER(IFNULL(V2Persons,'')) LIKE CONCAT('%', a_norm, '%')
          OR LOWER(IFNULL(V2Organizations,'')) LIKE CONCAT('%', a_norm, '%')
          OR LOWER(IFNULL(V2Locations,'')) LIKE CONCAT('%', a_norm, '%')
          OR LOWER(IFNULL(V2Themes,'')) LIKE CONCAT('%', a_norm, '%')
        ) THEN 1 ELSE 0 END as has_entity_a_structured,

        CASE WHEN (
          LOWER(IFNULL(V2Persons,'')) LIKE CONCAT('%', b_norm, '%')
          OR LOWER(IFNULL(V2Organizations,'')) LIKE CONCAT('%', b_norm, '%')
          OR LOWER(IFNULL(V2Locations,'')) LIKE CONCAT('%', b_norm, '%')
          OR LOWER(IFNULL(V2Themes,'')) LIKE CONCAT('%', b_norm, '%')
        ) THEN 1 ELSE 0 END as has_entity_b_structured,

        -- Text matching in DocumentIdentifier (URLs/headlines)
        CASE WHEN REGEXP_CONTAINS(LOWER(IFNULL(DocumentIdentifier,'')), CONCAT(r'\\b', a_norm, r'\\b')) THEN 1 ELSE 0 END as has_entity_a_text,
        CASE WHEN REGEXP_CONTAINS(LOWER(IFNULL(DocumentIdentifier,'')), CONCAT(r'\\b', b_norm, r'\\b')) THEN 1 ELSE 0 END as has_entity_b_text

      FROM `gdelt-bq.gdeltv2.gkg_partitioned`
      WHERE DATE(_PARTITIONTIME) BETWEEN IFNULL(@start, DATE '1970-01-01') AND IFNULL(@end, CURRENT_DATE())
    ),
    hybrid_docs AS (
      SELECT
        GKGRECORDID,
        -- Hybrid matching: entity found in EITHER structured fields OR text
        GREATEST(has_entity_a_structured, has_entity_a_text) as has_entity_a,
        GREATEST(has_entity_b_structured, has_entity_b_text) as has_entity_b
      FROM docs
    )
    SELECT
      SUM(CASE WHEN has_entity_a = 1 AND has_entity_b = 1 THEN 1 ELSE 0 END) as cooccurrence,
      SUM(has_entity_a) as entity_a_count,
      SUM(has_entity_b) as entity_b_count,
      COUNT(*) as total_documents
    FROM hybrid_docs;
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
        result = client.query(query, job_config=job_config).to_dataframe()
        if result.empty:
            return {
                'cooccurrence': 0,
                'entity_a_count': 0,
                'entity_b_count': 0,
                'normalized_cooccurrence': 0.0,
                'total_documents': 0
            }

        row = result.iloc[0]
        cooccur = int(row['cooccurrence'])
        count_a = int(row['entity_a_count'])
        count_b = int(row['entity_b_count'])
        total_docs = int(row['total_documents'])

        # Calculate normalized co-occurrence: Jaccard similarity
        if count_a > 0 and count_b > 0:
            normalized = cooccur / (count_a + count_b - cooccur) if (count_a + count_b - cooccur) > 0 else 0.0
        else:
            normalized = 0.0

        return {
            'cooccurrence': cooccur,
            'entity_a_count': count_a,
            'entity_b_count': count_b,
            'normalized_cooccurrence': round(normalized, 4),
            'total_documents': total_docs
        }
    except Exception as e:
        raise Exception(f"BigQuery execution failed: {str(e)}")


def fetch_co_mention_snippets(entity_a: str, entity_b: str, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 1000) -> List[str]:
    """
    Fetch snippets (URLs/headlines) that mention both entities.

    Args:
        entity_a: First entity to search for
        entity_b: Second entity to search for
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        limit: Maximum number of snippets to return

    Returns:
        List of DocumentIdentifier strings (URLs/headlines) containing both entities
    """
    if not entity_a or not entity_a.strip():
        raise ValueError("entity_a cannot be empty")
    if not entity_b or not entity_b.strip():
        raise ValueError("entity_b cannot be empty")

    # Initialize BigQuery client
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    client = bigquery.Client()

    query = """
    DECLARE a_norm STRING DEFAULT LOWER(TRIM(@a));
    DECLARE b_norm STRING DEFAULT LOWER(TRIM(@b));
    SELECT DISTINCT
      DocumentIdentifier
    FROM `gdelt-bq.gdeltv2.gkg_partitioned`
    WHERE DATE(_PARTITIONTIME) BETWEEN IFNULL(@start, DATE '1970-01-01') AND IFNULL(@end, CURRENT_DATE())
      AND (
        LOWER(IFNULL(V2Persons,'')) LIKE CONCAT('%', a_norm, '%')
        OR LOWER(IFNULL(V2Organizations,'')) LIKE CONCAT('%', a_norm, '%')
        OR LOWER(IFNULL(V2Locations,'')) LIKE CONCAT('%', a_norm, '%')
        OR LOWER(IFNULL(V2Themes,'')) LIKE CONCAT('%', a_norm, '%')
        OR REGEXP_CONTAINS(LOWER(IFNULL(DocumentIdentifier,'')), CONCAT(r'\\b', a_norm, r'\\b'))
      )
      AND (
        LOWER(IFNULL(V2Persons,'')) LIKE CONCAT('%', b_norm, '%')
        OR LOWER(IFNULL(V2Organizations,'')) LIKE CONCAT('%', b_norm, '%')
        OR LOWER(IFNULL(V2Locations,'')) LIKE CONCAT('%', b_norm, '%')
        OR LOWER(IFNULL(V2Themes,'')) LIKE CONCAT('%', b_norm, '%')
        OR REGEXP_CONTAINS(LOWER(IFNULL(DocumentIdentifier,'')), CONCAT(r'\\b', b_norm, r'\\b'))
      )
    LIMIT @limit_val
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("a", "STRING", entity_a),
            bigquery.ScalarQueryParameter("b", "STRING", entity_b),
            bigquery.ScalarQueryParameter("start", "DATE", start_date),
            bigquery.ScalarQueryParameter("end", "DATE", end_date),
            bigquery.ScalarQueryParameter("limit_val", "INT64", limit),
        ]
    )

    try:
        result = client.query(query, job_config=job_config).to_dataframe()
        if result.empty:
            return []
        return result['DocumentIdentifier'].tolist()
    except Exception as e:
        raise Exception(f"BigQuery execution failed: {str(e)}")


def get_causal_weight_score(entity_a: str, entity_b: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Return directional causal edge weights by combining normalized_co_occurrence (Jaccard)
    and average_connection_weight from LLM-scored co-mention snippets.

    Args:
        entity_a: First entity (A)
        entity_b: Second entity (B)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        Dictionary containing:
        - weight_a_to_b: Final causal weight from A to B
        - weight_b_to_a: Final causal weight from B to A
        - jaccard: Normalized co-occurrence (Jaccard similarity)
        - avg_strength: Average strength of causal claims
        - p_a_to_b: Probability A causes B
        - p_b_to_a: Probability B causes A
        - p_bidirectional: Probability of bidirectional causation
        - p_no_causal: Probability of no causal relationship
        - n_scored: Number of snippets scored by LLM
    """
    # Get normalized co-occurrence (Jaccard similarity)
    cooccur_result = hybrid_cooccurrence(entity_a, entity_b, start_date, end_date)
    jaccard = cooccur_result['normalized_cooccurrence']

    # Fetch co-mention snippets
    snippets = fetch_co_mention_snippets(entity_a, entity_b, start_date, end_date)

    # If no snippets found, return base result with jaccard only
    if not snippets:
        return {
            'weight_a_to_b': 0.0,
            'weight_b_to_a': 0.0,
            'jaccard': jaccard,
            'avg_strength': 0.0,
            'p_a_to_b': 0.0,
            'p_b_to_a': 0.0,
            'p_bidirectional': 0.0,
            'p_no_causal': 1.0,
            'n_scored': 0
        }

    # Sample up to 200 snippets for LLM scoring
    sample_size = min(200, len(snippets))
    sampled_snippets = random.sample(snippets, sample_size)

    # Initialize LLM client
    llm = LLM_OA("gpt-4o-mini")

    # Score snippets with LLM
    judgments = []
    for snippet in sampled_snippets:
        try:
            # Create prompt with entities and snippet
            llm_prompt = f"{prompt}\n\nEntities: A='{entity_a}', B='{entity_b}'\nText snippet: {snippet}"

            # Get structured judgment from LLM
            judgment = llm.generate_structured(llm_prompt, CausalJudgment)
            judgments.append(judgment)
        except Exception as e:
            # Skip snippets that cause errors
            print(f"Warning: Failed to score snippet: {str(e)}")
            continue

    # If no successful judgments, return base result
    if not judgments:
        return {
            'weight_a_to_b': 0.0,
            'weight_b_to_a': 0.0,
            'jaccard': jaccard,
            'avg_strength': 0.0,
            'p_a_to_b': 0.0,
            'p_b_to_a': 0.0,
            'p_bidirectional': 0.0,
            'p_no_causal': 1.0,
            'n_scored': 0
        }

    # Aggregate LLM outputs
    n_scored = len(judgments)
    avg_strength = sum(j.strength for j in judgments) / n_scored
    p_a_to_b = sum(j.p_a_to_b for j in judgments) / n_scored
    p_b_to_a = sum(j.p_b_to_a for j in judgments) / n_scored
    p_bidirectional = sum(j.p_bidirectional for j in judgments) / n_scored
    p_no_causal = sum(j.p_no_causal for j in judgments) / n_scored

    # Compute average connection weights for each direction
    avg_connection_weight_a_to_b = avg_strength * p_a_to_b
    avg_connection_weight_b_to_a = avg_strength * p_b_to_a

    # Compute final weights: jaccard * average_connection_weight
    weight_a_to_b = jaccard * avg_connection_weight_a_to_b
    weight_b_to_a = jaccard * avg_connection_weight_b_to_a

    return {
        'weight_a_to_b': round(weight_a_to_b, 4),
        'weight_b_to_a': round(weight_b_to_a, 4),
        'jaccard': jaccard,
        'avg_strength': round(avg_strength, 4),
        'p_a_to_b': round(p_a_to_b, 4),
        'p_b_to_a': round(p_b_to_a, 4),
        'p_bidirectional': round(p_bidirectional, 4),
        'p_no_causal': round(p_no_causal, 4),
        'n_scored': n_scored
    }


def main():
    """Main function with sample queries comparing strict vs hybrid modes."""
    print("🌍 GDELT Entity Cooccurrence Analysis")
    print("=" * 60)

    try:
        # Sample query 1: Biden and Ukraine (should be similar in both modes)
        print("Sample 1: Biden and Ukraine Co-occurrences")
        print("=" * 40)

        print("STRICT MODE (structured fields only):")
        result1_strict = cooccurrence('biden', 'ukraine', start_date='2024-01-01', end_date='2024-01-31')
        print(f"  Co-occurrence: {result1_strict['cooccurrence']} documents")
        print(f"  Biden: {result1_strict['entity_a_count']} docs | Ukraine: {result1_strict['entity_b_count']} docs")
        print(f"  Normalized (Jaccard): {result1_strict['normalized_cooccurrence']}")

        print("\nHYBRID MODE (structured + text matching):")
        result1_hybrid = hybrid_cooccurrence('biden', 'ukraine', start_date='2024-01-01', end_date='2024-01-31')
        print(f"  Co-occurrence: {result1_hybrid['cooccurrence']} documents")
        print(f"  Biden: {result1_hybrid['entity_a_count']} docs | Ukraine: {result1_hybrid['entity_b_count']} docs")
        print(f"  Normalized (Jaccard): {result1_hybrid['normalized_cooccurrence']}")

        print("\n" + "=" * 60)

        # Sample query 2: Apple and iPhone (should show major improvement in hybrid mode)
        print("Sample 2: Apple and iPhone Co-occurrences")
        print("=" * 40)

        print("STRICT MODE (structured fields only):")
        result2_strict = cooccurrence('apple', 'iphone', start_date='2024-09-01', end_date='2024-09-30')
        print(f"  Co-occurrence: {result2_strict['cooccurrence']} documents")
        print(f"  Apple: {result2_strict['entity_a_count']} docs | iPhone: {result2_strict['entity_b_count']} docs")
        print(f"  Normalized (Jaccard): {result2_strict['normalized_cooccurrence']}")

        print("\nHYBRID MODE (structured + text matching):")
        result2_hybrid = hybrid_cooccurrence('apple', 'iphone', start_date='2024-09-01', end_date='2024-09-30')
        print(f"  Co-occurrence: {result2_hybrid['cooccurrence']} documents")
        print(f"  Apple: {result2_hybrid['entity_a_count']} docs | iPhone: {result2_hybrid['entity_b_count']} docs")
        print(f"  Normalized (Jaccard): {result2_hybrid['normalized_cooccurrence']}")

        # Show improvement metrics
        improvement_factor = result2_hybrid['cooccurrence'] / max(result2_strict['cooccurrence'], 1)
        print(f"\n📈 HYBRID MODE IMPROVEMENT:")
        print(f"  Co-occurrence boost: {improvement_factor:.1f}x")
        print(f"  iPhone detection boost: {result2_hybrid['entity_b_count'] / max(result2_strict['entity_b_count'], 1):.1f}x")

        print("\n" + "=" * 60)

        # Sample query 3: Causal weight analysis
        print("Sample 3: Causal Weight Analysis - Biden and Ukraine")
        print("=" * 40)

        print("CAUSAL WEIGHT ANALYSIS:")
        causal_result = get_causal_weight_score('biden', 'ukraine', start_date='2024-01-01', end_date='2024-01-31')
        print(f"  Weight Biden → Ukraine: {causal_result['weight_a_to_b']}")
        print(f"  Weight Ukraine → Biden: {causal_result['weight_b_to_a']}")
        print(f"  Jaccard similarity: {causal_result['jaccard']}")
        print(f"  Average causal strength: {causal_result['avg_strength']}")
        print(f"  P(Biden → Ukraine): {causal_result['p_a_to_b']}")
        print(f"  P(Ukraine → Biden): {causal_result['p_b_to_a']}")
        print(f"  P(Bidirectional): {causal_result['p_bidirectional']}")
        print(f"  P(No causal): {causal_result['p_no_causal']}")
        print(f"  Snippets scored: {causal_result['n_scored']}")

        print(f"\n✅ Analysis complete!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
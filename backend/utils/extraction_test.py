import sys
import os
sys.path.append('/Users/levinniederer/PycharmProjects/contextra')

# Ensure we're running from the project root
os.chdir('/Users/levinniederer/PycharmProjects/contextra')

from backend.utils.extractor import Extractor

extractor = Extractor(target="Apple")
print(f"Cache path: {extractor.cache_path}")
print(f"Cache exists: {os.path.exists(extractor.cache_path)}")

# Test loading the data
research_data = extractor._fetch_data()
print(f"Research data loaded: {len(research_data)} characters")

nodes, edges = extractor.extract()

print(f"Extracted {len(nodes)} nodes and {len(edges)} edges")

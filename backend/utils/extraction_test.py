import sys
sys.path.append('/Users/levinniederer/PycharmProjects/contextra')

from backend.utils.extractor import Extractor

extractor = Extractor(target="Apple")
nodes, edges = extractor.extract()

print(f"Extracted {len(nodes)} nodes and {len(edges)} edges")

from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict, Any, ForwardRef, TYPE_CHECKING

# Import Node only for type checking to avoid circular import
if TYPE_CHECKING:
    from .Node import Node

class Edge(BaseModel):
    """
    Edge class representing a connection between two nodes in the graph.

    Attributes:
        title (str): Primary name/identifier of the edge
        description (str): Brief description of the connection
        start (Node): Starting node of the edge
        end (Node): Ending node of the edge
        importance_score (float): Importance score of the edge (0.5-1.0, higher = stronger connection)
    """
    title: str = Field(..., description="Primary name/identifier")
    description: str = Field(..., description="Brief description of the connection")
    start: 'Node' = Field(..., description="Starting node")
    end: 'Node' = Field(..., description="Ending node")
    importance_score: float = Field(default=0.75, description="Importance score of the edge (0.5-1.0, higher = stronger connection)")
    
    class Config:
        arbitrary_types_allowed = True

# Update forward references
from .Node import Node
Edge.update_forward_refs()
from pydantic import BaseModel
from typing import List, Union, Optional, Dict, Any, Field


# stage 2 ----------------------
class Edge(BaseModel):

    """Node class"""
    titel: str = Field(..., description="Primary name/identifier")
    description: str = Field(..., description="Brief description of the entity")
    start: str = Field(..., description="starting Node")
    end: str = Field(..., description="ending Node")
from pydantic import BaseModel
from typing import List, Union, Optional, Dict, Any, Field


# stage 2 ----------------------
class Node(BaseModel):

    """Node class"""
    name: str = Field(..., description="Primary name/identifier")
    aliases: List[str] = Field(default_factory=list, description="Known name variations")
    description: str = Field(..., description="Brief description of the entity")
    type: str = Field(..., description="Entity type (Company, Person, etc.)")
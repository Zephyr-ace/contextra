from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict, Any


class Node(BaseModel):
    """
    Node class representing an entity in the graph.
    
    Attributes:
        title (str): Primary name/identifier of the node (used for graph operations)
        name (str): Primary name/identifier (for backward compatibility)
        aliases (List[str]): Known name variations
        description (str): Brief description of the entity
        type (str): Entity type (Company, Person, etc.)
    """
    name: str = Field(..., description="Primary name/identifier")
    aliases: List[str] = Field(default_factory=list, description="Known name variations")
    description: str = Field(..., description="Brief description of the entity")
    type: str = Field(..., description="Entity type (Company, Person, etc.)")
    
    @property
    def title(self) -> str:
        """Return the title of the node (alias for name)."""
        return self.name
        
    @title.setter
    def title(self, value: str) -> None:
        """Set the title of the node (updates name)."""
        self.name = value
from enum import Enum
from typing import Dict, List, Optional, Literal

from pydantic import BaseModel


class RebalancingFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUALLY = "semiannually"
    ANNUALLY = "annually"


class Strategy(BaseModel):
    name: str
    description: str
    time_horizon: str
    risk_level: str
    asset_classes: List[str]
    rebalancing_frequency: RebalancingFrequency
    allocation_targets: Dict[str, float]
    preferences: Optional[List[str]] = None


class CoreStrategy(Strategy):
    name: Literal["Core"] = "Core"
    description: str = "Broadly diversified, stable base portfolio focused on long-term growth and/or income."


class SatelliteStrategy(Strategy):
    name: Literal["Satellite"] = "Satellite"
    description: str = "Focused, high-conviction or thematic investments that complement a core portfolio."


class CoreSatelliteStrategy(Strategy):
    name: Literal["Core Satellite"] = "Core Satellite"
    description: str = "Combination of a stable core allocation with satellite positions for tactical opportunities."

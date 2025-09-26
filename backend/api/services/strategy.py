from api.models.strategy import (
    CoreSatelliteStrategy,
    RebalancingFrequency,
    Strategy,
)
from api.util.asset import Bond, Commodity, Equity, RealEstate


def get_investment_strategy() -> Strategy:
    # Example: Core Satellite strategy with simple allocation targets
    return CoreSatelliteStrategy(
        risk_level="Medium",
        time_horizon="Long-term (5+ years)",
        asset_classes=[Equity, Bond, RealEstate, Commodity],
        allocation_targets={
            "equity": 0.6,
            "bond": 0.25,
            "real_estate": 0.1,
            "commodity": 0.05,
        },
        rebalancing_frequency=RebalancingFrequency.SEMIANNUALLY,
        preferences=["Sustainable", "Technology", "Healthcare"],
    )

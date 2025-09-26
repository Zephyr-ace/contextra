from api.models.portfolio import Portfolio, Position


def get_portfolio() -> Portfolio:
    return Portfolio(
        positions=[
            Position(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=120,
                average_cost=168.40,
                market_value=21480.0,
                pl_percent=4.2,
                color="var(--ubs-red)",
            ),
            Position(
                symbol="MSFT",
                name="Microsoft",
                quantity=80,
                average_cost=310.20,
                market_value=25200.0,
                pl_percent=-1.1,
                color="var(--ubs-yellow)",
            ),
            Position(
                symbol="UBSG",
                name="UBS Group",
                quantity=1382819,
                average_cost=23.50,
                market_value=183217.0,
                pl_percent=2718211.72,
                currency="CHF",
                color="var(--ubs-black)",
            ),
        ]
    )

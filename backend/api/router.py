from fastapi import APIRouter

from api.models.portfolio import Portfolio
from api.models.strategy import Strategy
from api.services.portfolio import get_portfolio as get_portfolio_service
from api.services.strategy import get_investment_strategy as get_investment_strategy_service


router = APIRouter()


@router.get("/healthz")
def health_check() -> dict:
    return {"status": "ok"}


@router.get("/portfolio", response_model=Portfolio)
def get_portfolio() -> Portfolio:
    return get_portfolio_service()


@router.get("/investment-strategy", response_model=Strategy)
def get_investment_strategy() -> Strategy:
    return get_investment_strategy_service()

from app.agents.router import IntentRouter
from app.domain.enums import Domain


def test_router_detects_equipment() -> None:
    assert IntentRouter().route("设备振动如何处理", Domain.AUTO) is Domain.EQUIPMENT

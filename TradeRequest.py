from datetime import datetime
from enum import Enum
from typing import Optional
from Team import Team
from Player import Player
import random


class TradeStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    EXECUTED = "executed"


class TradeRequest:
    def __init__(
        self,
        from_team: Team, #Team requesting the trade
        to_team: Team, #Team recieving the trade
        offer_player: Player,
        request_player: Player,
        cash: int = 0,
        expires_in_seconds: int = 600  # 10 minutes default
    ):
        self.id = create_id()
        self.from_team = from_team
        self.to_team = to_team
        self.offer_player = offer_player
        self.request_player = request_player
        self.cash = cash

        self.status = TradeStatus.PENDING
        self.created_at = datetime.utcnow()
        self.expires_at = (
            self.created_at.timestamp() + expires_in_seconds
        )

    # ------------------------
    # State Checks
    # ------------------------

    def is_expired(self) -> bool:
        return datetime.utcnow().timestamp() > self.expires_at

    def can_execute(self) -> bool:
        if self.status != TradeStatus.ACCEPTED:
            return False
        if self.is_expired():
            self.status = TradeStatus.EXPIRED
            return False
        return True

    # ------------------------
    # Actions
    # ------------------------

    def accept(self) -> tuple[bool, str]:
        if self.is_expired():
            self.status = TradeStatus.EXPIRED
            return False, "Trade request has expired."

        self.status = TradeStatus.ACCEPTED
        return True, "Trade accepted."

    def decline(self) -> tuple[bool, str]:
        if self.status != TradeStatus.PENDING:
            return False, "Trade is no longer pending."

        self.status = TradeStatus.DECLINED
        return True, "Trade declined."

    def execute(self) -> tuple[bool, str]:
        if not self.can_execute():
            return False, "Trade cannot be executed."

        success, message = self.from_team.execute_trade(
            other=self.to_team,
            export_player=self.offer_player,
            import_player=self.request_player,
            cash=self.cash
        )

        if success:
            self.status = TradeStatus.EXECUTED

        return success, message
    
def create_id():
    id = random.randint(100,999)
    print(f"Trade ID Created! Trade ID: {id}")
    return int(id)

def main():
    team_a = Team("A", "Team A")
    team_b = Team("B", "Team B")
    p1 = Team.add_player("Alexander","Zverev")
    p2 = Team.add_player("Ben", "Shelton")

    trade = TradeRequest(team_a, team_b, p1, p2, cash=10)

    assert trade.status.name == "PENDING"
    trade.accept()
    assert trade.status.name == "ACCEPTED"

    print("TradeRequest test PASSED")

if __name__ == "__main__":
    main()

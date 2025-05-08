from src.modules.dnse.realtime_data_provider import RealtimeDataProvider
from src.modules.investors.entities import Accounts, Holdings
from src.modules.investors.repositories import AccountsRepo, HoldingsRepo
from src.modules.auth.types import JwtPayload

class HoldingsService:
    repo = HoldingsRepo

    @classmethod
    async def get_all_holdings(cls, payload: JwtPayload):
        conditions = {Accounts.user_id.name: payload.userId}
        records = await AccountsRepo.get_by_condition(conditions=conditions)
        holdings = {}
        if records:
            record = records[0]
            holdings_condition = {Holdings.account_id.name: record[Accounts.id.name]}
            raw_holdings = await cls.repo.get_by_condition(conditions=holdings_condition)
            if raw_holdings:
                for holding in raw_holdings:
                    market_price = RealtimeDataProvider.get_market_price(holding[Holdings.symbol.name])
                    holdings[holding[Holdings.symbol.name]] = {
                        "quantity": holding[Holdings.quantity.name],
                        "cost_basis": holding[Holdings.cost_basis_per_share.name],
                        "market_price": market_price,
                        "locked_quantity": holding[Holdings.locked_quantity.name]
                    }
        return holdings

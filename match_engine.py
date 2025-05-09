import asyncio
from backend.modules.matching_engine.services import MatchEngineService


if __name__ == "__main__":
    asyncio.run(MatchEngineService.run())
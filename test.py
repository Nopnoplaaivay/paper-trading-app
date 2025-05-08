from src.modules.yfinance.crawler import YfinanceCrawler

import asyncio
from sqlalchemy import text
from src.db.sessions import backend_session_scope


# async def example_usage():
#     async with backend_session_scope(new=True) as session:
#         result = await session.execute(text("SELECT 42 AS test;"))
#         data = result.all()
#         print(data)
#
#
# if __name__ == "__main__":
#     asyncio.run(example_usage())

if __name__ == "__main__":
    # Test the YfinanceCrawler
    symbol = "VCB"
    interval = "1d"
    time_range = "1y"

    # Download historical price data
    df = YfinanceCrawler.download(symbol, interval, time_range)

    # Print the first few rows of the DataFrame
    print(df.head())
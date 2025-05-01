import aiohttp
import requests
import asyncio
import pandas as pd
import streamlit as st

from src.utils.logger import LOGGER
from src.common.consts import YfinanceConsts


class YfinanceCrawler:
    MARKET = "VN"  # Assuming this is a constant for the market suffix

    @classmethod
    def download(
        cls, symbol: str  = "BID", interval: str = "1d", time_range: str = "1y"
    ) -> pd.DataFrame:
        if time_range not in YfinanceConsts.VALID_RANGES:
            raise ValueError(f"Invalid range value: {time_range}")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.{cls.MARKET}?interval={interval}&range={time_range}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            # Extract relevant data from the JSON response
            quote_data = data["chart"]["result"][0]["indicators"]["quote"][0]
            df = pd.DataFrame(quote_data)

            # Add timestamp column
            df["timestamp"] = data["chart"]["result"][0]["timestamp"]
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
            df["time"] = df["timestamp"].dt.date

            # df.set_index("timestamp", inplace=True)
            # df.columns = [
            #     f"{symbol}_{col}" for col in df.columns if col != "timestamp"
            # ]
            return df
        except Exception as e:
            LOGGER.error(f"Failed to fetch data for {symbol}: {e}")
            st.warning(f"Yfinance doesn't provide data for {symbol}")
            return pd.DataFrame()
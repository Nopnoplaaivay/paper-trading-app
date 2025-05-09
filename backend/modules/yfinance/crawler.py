import requests
import pandas as pd
import streamlit as st

from backend.utils.logger import LOGGER
from backend.common.consts import YfinanceConsts


class YfinanceCrawler:
    @classmethod
    def download(
        cls, symbol: str = "BID", interval: str = "1d", time_range: str = "1y"
    ) -> pd.DataFrame:
        if time_range not in YfinanceConsts.VALID_RANGES:
            raise ValueError(f"Invalid range value: {time_range}")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.VN?events=capitalGain%7Cdiv%7Csplit&formatted=true&includeAdjustedClose=true&interval={interval}&period1=1714953600&period2=1746635464&symbol={symbol}.VN&userYfid=true&lang=en-US&region=US"
        headers = {"User-Agent": "PostmanRuntime/7.43.4",}
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

            # drop nan
            df = df.dropna()
            return df
        except Exception as e:
            raise e
            LOGGER.error(f"Failed to fetch data for {symbol}: {e}")
            st.warning(f"Yfinance doesn't provide data for {symbol}")
            return pd.DataFrame()
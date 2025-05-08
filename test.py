from src.modules.yfinance.crawler import YfinanceCrawler


if __name__ == "__main__":
    # Test the YfinanceCrawler
    symbol = "VCB"
    interval = "1d"
    time_range = "1y"

    # Download historical price data
    df = YfinanceCrawler.download(symbol, interval, time_range)

    # Print the first few rows of the DataFrame
    print(df.head())
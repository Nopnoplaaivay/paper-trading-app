from src.websocket import TradeData


if __name__ == "__main__":
    # Test the TradeData class
    data = TradeData.get_stock_info()
    if data:
        print("OHLCCache data retrieved successfully.")
    else:
        print("Failed to retrieve OHLCCache data.")

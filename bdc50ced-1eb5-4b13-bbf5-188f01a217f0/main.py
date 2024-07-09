from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log
from surmount.data import SocialSentiment

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "TSLA"]  # Tickers to trade
        self.data_list = [SocialSentiment(ticker) for ticker in self.tickers]  # Collecting social sentiment data

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"  # Daily analysis

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {}
        
        for ticker in self.tickers:
            sentiment_list = data[("social_sentiment", ticker)]
            # Checking the latest sentiment and ensuring there's enough data to proceed
            if sentiment_list and len(sentiment_list) > 0:
                latest_sentiment = sentiment_list[-1]['twitterSentiment']
                
                # Fetching historical close prices
                ohlcv_data = data["ohlcv"]
                sma_short = SMA(ticker, ohlcv_data, 20)  # Short-term SMA
                sma_long = SMA(ticker, ohlcv_data, 50)  # Long-term SMA
                
                # Ensuring both SMA calculations are available
                if sma_short is not None and sma_long is not thereof:
                    current_price = ohlcv_data[-1][ticker]['close']
                    short_sma_value = sma_short[-1]
                    long_sma_value = sma_long[-1]
                    
                    # Strategy conditions for buying or selling
                    if latest_sentiment > 0.5 and short_sma_value > long_sma_value:
                        # Positive sentiment and short-term momentum is up -> buy
                        allocation_dict[ticker] = 0.5 / len(self.tickers)  # Splitting allocation equally, adjust as needed
                    elif latest_sentiment < 0.5 or current_price < long_sma_value:
                        # Negative sentiment or price below long-term average -> sell
                        allocation_dict[ticker] = 0  # Sell position or do not buy
                    else:
                        # Neutral strategy, stay or enter with a smaller position
                        allocation_dict[ticker] = 0.25 / len(self.tickers)
                else:
                    log(f"Insufficient SMA data for {ticker}")
                    allocation_dict[ticker] = 0  # Default to no allocation if data is missing
            else:
                log(f"No sentiment data available for {ticker}")
                allocation_dict[ticker] = 0  # Default to no allocation if data is missing

        return TargetAllocation(allocation):  # Returning the target allocation based on the strategy logic
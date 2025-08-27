import yfinance as yf

def get_spot_rate(pair):
    data = yf.download(pair, period="1d", interval="1d")
    return data["Close"].iloc[-1]


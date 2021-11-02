
from datetime import datetime as dt
import pandas as pd
from binance.client import Client
from datetime import timedelta
client = Client("", "")


def DOWNLOAD_INTERVAL(symbol, interval, futures=False):
    start_date = "2018-01-01"
    
    start = dt.strptime(start_date, "%Y-%m-%d")

    end = dt.today()

    # print(f"{symbol}({interval}) From {start} -> {end}")

    def download(start, end):
        if end <= start:
            return None
        modified_interval = "1M" if interval == "1Mo" else interval
        print(modified_interval)
        if futures:
            jdata = client.futures_historical_klines(symbol, modified_interval, start_str=int(
                start.timestamp()*1000), end_str=int(end.timestamp()*1000))
        else:
            jdata = client.get_historical_klines(symbol, modified_interval, start_str=int(
                start.timestamp()*1000), end_str=int(end.timestamp()*1000))

        if len(jdata) == 0:
            return None

        data = pd.DataFrame(jdata)
        data.columns = ["date", "open", "high", "low", "close", "volume",
                        "closetime", "QuoteAV", "NT", "Taker.buy.base", "Taker.buy", "Ignore", ]
        data = data[['date', 'open', 'high', 'low', 'close', "volume"]]
        data['date'] = pd.to_datetime(data['date'], unit='ms')
        return data

    file_prefix = ""
    if futures:
        file_prefix = "F"

    has_df = False
    try:
        df = pd.read_csv(
            f"Data/Binance_{file_prefix}{symbol}_{interval}.csv", parse_dates=["date"])
        has_df = True
    except FileNotFoundError:
        print("File Not Found")

    if has_df:
        # df.date = pd.to_datetime(df.date)
        df_start = df.date[0] - timedelta(seconds=1)
        df_end = df.date[len(df)-1] + timedelta(seconds=1)
        df = pd.concat((download(start, df_start), df, download(df_end, end)))
    else:
        df = download(start, end)

    df.to_csv(
        f"Data/Binance_{file_prefix}{symbol}_{interval}.csv", index=False)
    
    
    
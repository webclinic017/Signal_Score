import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas_ta as ta


class MACD():

    parameters = 3

    def __init__(self, df: pd.DataFrame,  fast=None, slow=None, singal=None) -> None:
        self.fast = fast
        self.slow = slow
        self.signal = singal
        self.df = df.set_index("date")
        self.macd = ta.macd(df["close"], fast, slow, singal).set_index(self.df.index)

    def getSignals(self):
        signals = self.macd
        c = self.macd.columns
        sbuy = signals[(signals[c[1]] > signals[c[2]]) & (
            signals[c[1]].shift(1) < signals[c[2]].shift(1))].copy()
        sbuy["singal"] = 1

        ssell = signals[(signals[c[1]] < signals[c[2]]) & (
            signals[c[1]].shift(1) > signals[c[2]].shift(1))].copy()
        ssell["singal"] = -1
        

        return pd.concat((sbuy, ssell)).sort_index()


d = pd.read_csv("Data\Binance_BTCUSDT_1d.csv")
m = MACD(d)
m.macd
m.getSignals()
ta.ema(d["close"] , 9)
d
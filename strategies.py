import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_ta.utils import data
import plotly.graph_objects as go
import pandas_ta as ta
import Score
from importlib import reload

from Tester import Tester


class RSI():

    def __init__(self, df, rsi_length=14, thr_low=30, thr_high=70) -> None:
        self.df = df
        self.df['RSI'] = ta.rsi(df.close, rsi_length)
        self.df['RSI_shift1'] = self.df.RSI.shift(1)
        self.thr_low = thr_low
        self.thr_high = thr_high

    def get_signals(self):

        def RSI_Strategy(x):
            [rsi_current, rsi_previous] = x
            if pd.isna(rsi_current) or pd.isna(rsi_previous):
                return 0
            elif rsi_current < self.thr_low and rsi_previous >= self.thr_low:
                return 1
            elif rsi_current > self.thr_high and rsi_previous <= self.thr_high:
                return -1
            else:
                return 0

        self.df['RSI_Strategy'] = self.df[[
            'RSI', 'RSI_shift1']].apply(RSI_Strategy, axis=1)
        df = self.df
        df.date = pd.to_datetime(df.date)
        
        
        return (df[df["RSI_Strategy"] != 0][["date", "RSI_Strategy"]]).values.tolist()
        


class CCI():

    def __init__(self, df,cci_length = 20, thr_low=-100, thr_high=100) -> None:
        df['CCI'] = ta.cci(df.high,df.low,df.close, cci_length)
        df['CCI_shift1'] = df.CCI.shift(1)
        self.df = df
        self.thr_low = thr_low
        self.thr_high = thr_high
    
    def get_signals(self):

        def CCI_Strategy(x, thr_low=-100, thr_high=100):
            [cci_current, cci_previous] = x
            if pd.isna(cci_current) or pd.isna(cci_previous):
                return 0
            elif cci_current>thr_low and cci_previous<=thr_low:
                return 1
            elif cci_current<thr_high and cci_previous>=thr_high:
                return -1
            else:
                return 0


        df = self.df
        df['CCI_Strategy'] = df[['CCI','CCI_shift1']].apply(CCI_Strategy, axis=1)
        return df[df["CCI_Strategy"] != 0][["date", "CCI_Strategy"]].values.tolist()



t = Tester("BTCUSDT")
df = pd.read_csv("Data\Binance_BTCUSDT_1h.csv")


for i in np.arange(-10,10,1):

    t.test(RSI(df,14+i).get_signals() , f"RSI_{14+i}_30_70")
    t.test(CCI(df,20+i,).get_signals() , f"RSI_{14+i}_-100_100")



for k,v in t.Scores.items():
    print(k,v,":::::")


t.print_all()

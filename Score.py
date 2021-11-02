import calendar
from typing import Dict, Iterable, List
import pandas as pd
import numpy as np
from datetime import datetime as dt, timedelta
import downloader
import pprint
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go


INTERVALS = ['1Mo', '1d', '1h', '1m']


INTERVALS_by_minutes = {"1m": 1, "1h": 60, "1d": 1440, "1Mo": 1440*30}


def elu(x, alpha=0.99999):
    if x >= 0:
        return x
    else:
        return alpha * (np.exp(x) - 1.0)


class Signals():
    LONG = 1
    SHORT = -1


class Strategy_Types():
    NORMAL = 0
    BUY_ONLY = 2
    SHORT_ONLY = 3


global_datas = {}


class Score():

    datas: Dict[str, pd.DataFrame] = None
    alphas = None

    @staticmethod
    def timedelta_to_minutes(t: timedelta):
        return t.days * 1440 + t.seconds // 60

    def __init__(self, symbol, Strategy_type=Strategy_Types.NORMAL) -> None:
        self.folder = "Data/"
        self.symbol = symbol
        self.datas = {}
        # self.download_data()
        self.load_datas()
        self.positions_details = []
        self.strategy_type = Strategy_type
        self.alphas = []
        self.score = -999998

    def download_data(self):
        '''
        Download Latest Candles
        '''
        for i in INTERVALS:
            # print("Downloading .... ", i , end=" ")
            downloader.DOWNLOAD_INTERVAL(self.symbol, i)

    def load_datas(self):
        '''
        Load Latest Candles
        '''
        global global_datas
        if len(global_datas):
            ">NO Loading ...."
            self.datas = global_datas
            return

        for i in INTERVALS:
            self.datas[i] = pd.read_csv(
                self.folder + f"Binance_{self.symbol}_{i}.csv", parse_dates=["date"], index_col="date")

        global_datas = self.datas

    def effective_profit_rate(self, alpha_array: np.ndarray, t_array: np.ndarray, mode="COMPOUND"):
        '''
        Final Score Aggreagation Based On Positions alphas
        '''
        if mode == "COMPOUND":
            r = np.sum(np.log(alpha_array+1.1))/np.sum(t_array)
            return r
        elif mode == "SIMPLE":
            exit(-1)
            r = np.log(1+np.sum(alpha_array))/np.sum(t_array)
            return r
        elif mode == "AVERAGE":
            r = np.mean(np.log(1+alpha_array) / t_array)
            return r
        else:
            raise("The 'mode' must be 'COMPOUND' or 'SIMPLE'.")

    def test(self, signals: Iterable):
        '''
        Test All Signal
        Paramas : Signals as tuple (Date:dt , Signal_type:int )  
        '''
        alpha_array = []
        t2c_array = []

        for index in range(len(signals) - 1):
            date, sig = signals[index]
            next_date, _ = signals[index + 1]
            if self.strategy_type == Strategy_Types.BUY_ONLY:
                if sig == Signals.SHORT:
                    continue
            elif self.strategy_type == Strategy_Types.SHORT_ONLY:
                if sig == Signals.SHORT:
                    continue

            tm = self.timedelta_to_minutes(next_date - date)

            position_info = self.get_position_information(date, next_date, sig)

            self.positions_details.append(position_info)
            alpha = self.get_pscore(sig, *position_info)

            alpha_array.append(alpha)
            self.alphas.append(alpha)

            t2c_array.append(tm)

        alpha_array = np.array(alpha_array)
        t2c_array = np.array(t2c_array)

        self.score = self.effective_profit_rate(alpha_array, t2c_array, )

    def get_score(self, signals=None):
        if signals != None:
            self.test(signals)
        return self.score

    def split_time(self, diff, time_options, indexes):
        result = []
        for index in indexes:
            coef = diff // time_options[index]
            if coef > 0:
                diff -= coef * time_options[index]
                result.append((index, coef))
        return result

    def get_position_information(self, entry_date: dt, exit_date: dt, signal_type):
        '''
        Get Position Entry , MaxDrawdown , Close
        '''

        minutes_diff = self.timedelta_to_minutes((exit_date - entry_date))
        if minutes_diff < 60:
            upmin = (exit_date.minute - entry_date.minute) % 60
            downmin = 0

            uphour = 0
            downhour = 0

            upday = 0
            downday = 0
        elif exit_date.month == entry_date.month and exit_date.day == entry_date.day:

            upmin = 60 - entry_date.minute
            downmin = exit_date.minute

            uphour = 0
            downhour = max(0, exit_date.hour - entry_date.hour - 1)

            upday = 0
            downday = 0

        elif exit_date.month == entry_date.month:

            upmin = 60 - entry_date.minute
            downmin = exit_date.minute

            uphour = 24 - entry_date.hour - 1
            downhour = exit_date.hour

            upday = 0
            downday = max(0, exit_date.day - entry_date.day - 1)

        else:
            upmin = 60 - entry_date.minute
            downmin = exit_date.minute

            uphour = 24 - entry_date.hour - 1
            downhour = exit_date.hour

            upday = calendar.monthrange(entry_date.year, entry_date.month)[
                1] - entry_date.day - 1
            downday = exit_date.day

        month_diff = exit_date.month - entry_date.month - 1
        month_diff += (exit_date.year - entry_date.year) * 12

        candles_info = [
            (upmin, "1m"),
            (uphour, "1h"),
            (upday, "1d"),
            (max(0, month_diff), "1Mo",),
            (downday, "1d"),
            (downhour, "1h"),
            (downmin, "1m"),

        ]
        # pprint.pprint(candles_info, width=40)

        candles = []
        start_date = entry_date
        for coeff, interval in candles_info:
            # print(start_date)
            candles.append(self.datas[interval][start_date:].head(coeff))

            # print(self.datas[interval][start_date:].head(coeff))
            if interval != "1Mo":
                start_date += timedelta(seconds=60 *
                                        INTERVALS_by_minutes[interval] * coeff)
            else:
                start_date += relativedelta(months=coeff)

        candles = pd.concat(candles)
        # return (candles)

        if signal_type == Signals.LONG:

            return (
                candles["open"][0],
                candles["low"].min(),
                candles["close"][-1],
            )

        if signal_type == Signals.SHORT:

            return (
                candles["open"][0],
                candles["high"].max(),
                candles["close"][-1],
            )

    def _ScoreFunction(self, a, b, c, m, mode):
        if mode == Signals.LONG:
            if c >= a:
                r = np.exp(m*(((c/a-1) / (c/b - b/a)) - 1)) * (c/a - 1)
            else:
                r = np.exp(m * (1 - (c/a - 1) / (b/a - c/b))) * (c/a - 1)
        elif mode == Signals.SHORT:
            if c <= a:
                r = np.exp(m*(((1 - c/a) / (-c/b + b/a)) - 1)) * (1 - c/a)
            else:
                r = np.exp(m * (1 - (1 - c/a) / (- b/a + c/b))) * (1 - c/a)

        
        
        return elu(r)


    def get_pscore(self, signal_type, entry, drawdown, close, power=2):
        

        return self._ScoreFunction(entry, drawdown, close, power, signal_type)


# Buy And Hold Strategy
# f = Score("Data/", "ETHUSDT")
# f = Score("Data/", "BTCUSDT")

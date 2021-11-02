from Score import Score, Strategy_Types
from datetime import datetime as dt


class Tester():

    def __init__(self, symbol,  start_time=None, end_time=None) -> None:
        self.start_time = start_time or dt(2015, 1, 1)
        self.end_time = end_time or dt(2025, 1, 1)
        self.Scorers = {}
        self.Scores = {}
        self.symbol = symbol

    def test(self, signals: list, name: str, Strategy_type=Strategy_Types.NORMAL):
        new_signals = signals
        # for date, signal in signals:
        #     if self.start_time <= date >= self.end_time:
        #         new_signals.append(date, signal)
        # if len(new_signals)==0:
        #     print(signals)


        s = Score(self.symbol, Strategy_type)
        s.test(new_signals)

        self.Scorers[name] = s
        self.Scores[name] = s.get_score()

    def print_all(self):
        for k,v in self.Scores.items():
            print(k,v,":::::")
            
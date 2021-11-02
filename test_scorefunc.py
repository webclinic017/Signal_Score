import pandas_ta as ta
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pprint

long = 1
short = -1


def _ScoreFunction(a, b, c, mode, m=2):
    if mode == long:
        if c >= a:
            r = np.exp(m*(((c/a-1) / (c/b - b/a)) - 1)) * (c/a - 1)
        else:
            r = np.exp(m * (1 - (c/a - 1) / (b/a - c/b))) * (c/a - 1)
    elif mode == short:
        if c <= a:
            r = np.exp(m*(((1 - c/a) / (-c/b + b/a)) - 1)) * (1 - c/a)
        else:
            r = np.exp(m * (1 - (1 - c/a) / (- b/a + c/b))) * (1 - c/a)

    return elu(r)


tests = [

    _ScoreFunction(1, 0.99, 1.05, long),
    _ScoreFunction(1, 0.95, 1.05, long),
    _ScoreFunction(1, 0.90, 1.1, long),
    _ScoreFunction(1, 0.7, 1.3, long),
    _ScoreFunction(1, 0.5, 1.5, long),
    _ScoreFunction(1, 0.1, 2, long),
    _ScoreFunction(1, 0.0001, 2, long),
    _ScoreFunction(1, 0.0001, 0.9, long),

    "----------------------------------------------",

    _ScoreFunction(1, 1.01, 0.95, short),
    _ScoreFunction(1, 1.05, 0.95, short),
    _ScoreFunction(1, 1.1, 0.9, short),
    _ScoreFunction(1, 1.3, 0.7, short),
    _ScoreFunction(1, 1.5, 0.7, short),
    _ScoreFunction(1, 2, 0.5, short),
    _ScoreFunction(1, 2.5, 1.5, short),
    _ScoreFunction(1, 2.5, 1.1, short),


]


pprint.pprint(tests)

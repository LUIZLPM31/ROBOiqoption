# Arquivo: indicators.py

import pandas as pd
import pandas_ta as ta

def calculate_indicators(df):
    # Calcular Bandas de Bollinger com desvio 3
    df.ta.bbands(close='close', length=20, std=3, append=True) # std=3 para desvio 3

    # Calcular RSI com período 4
    df.ta.rsi(close='close', length=4, append=True) # length=4 para período 4

    return df
# Arquivo: indicators.py (Calibrado)

import pandas as pd
import pandas_ta as ta

def calculate_indicators(df):
    # --- MUDANÇA APLICADA ---
    # Calcular Bandas de Bollinger com desvio padrão 2.0 (mais comum e sensível)
    df.ta.bbands(close='close', length=20, std=2.0, append=True)

    # Calcular RSI com período 4 (mantido)
    df.ta.rsi(close='close', length=4, append=True)

    return df

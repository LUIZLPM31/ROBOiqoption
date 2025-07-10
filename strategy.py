# Arquivo: strategy.py (Calibrado)

import pandas as pd
import logging
from indicators import calculate_indicators

def check_signal(df):
    if df.empty or len(df) < 21:
        return None

    # O nome da coluna das bandas mudará por causa da alteração no 'indicators.py'
    df_with_indicators = calculate_indicators(df.copy())
    
    bb_lower_col = 'BBL_20_2.0' # Nome da coluna atualizado para std 2.0
    bb_upper_col = 'BBU_20_2.0' # Nome da coluna atualizado para std 2.0
    rsi_col = 'RSI_4'

    if not all([bb_lower_col in df_with_indicators.columns, bb_upper_col in df_with_indicators.columns, rsi_col in df_with_indicators.columns]):
        logging.error("Colunas de indicadores não encontradas. Verifique os nomes.")
        return None

    open_price_current = df_with_indicators["open"].iloc[-1]
    bb_lower_current = df_with_indicators[bb_lower_col].iloc[-1]
    bb_upper_current = df_with_indicators[bb_upper_col].iloc[-1]
    rsi_previous = df_with_indicators[rsi_col].iloc[-2]

    logging.info(f"[DEBUG ESTRATÉGIA] Abertura: {open_price_current:.5f} | "
                 f"RSI(-1): {rsi_previous:.2f} | "
                 f"Banda Superior: {bb_upper_current:.5f} | "
                 f"Banda Inferior: {bb_lower_current:.5f}")

    signal = None
    
    # --- MUDANÇA APLICADA ---
    # Condição de Compra (CALL) com RSI < 30
    is_below_band = open_price_current < bb_lower_current
    is_oversold = rsi_previous < 30 # Alterado de 20 para 30
    if is_below_band and is_oversold:
        signal = "CALL"
        logging.warning(f"SINAL DE COMPRA (CALL) DETECTADO! Abertura < B.Inf ({is_below_band}) E RSI < 30 ({is_oversold})")

    # Condição de Venda (PUT) com RSI > 70
    is_above_band = open_price_current > bb_upper_current
    is_overbought = rsi_previous > 70 # Alterado de 80 para 70
    if is_above_band and is_overbought:
        signal = "PUT"
        logging.warning(f"SINAL DE VENDA (PUT) DETECTADO! Abertura > B.Sup ({is_above_band}) E RSI > 70 ({is_overbought})")

    return signal

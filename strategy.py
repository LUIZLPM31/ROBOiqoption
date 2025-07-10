# Arquivo: strategy.py (Atualizado com Debug)

import pandas as pd
import logging
from indicators import calculate_indicators

def check_signal(df):
    if df.empty or len(df) < 21: # Aumentado para 21 para garantir que iloc[-2] funcione
        return None

    df_with_indicators = calculate_indicators(df.copy())

    bb_lower_col = 'BBL_20_3.0'
    bb_upper_col = 'BBU_20_3.0'
    rsi_col = 'RSI_4'

    if not all([bb_lower_col in df_with_indicators.columns, bb_upper_col in df_with_indicators.columns, rsi_col in df_with_indicators.columns]):
        logging.error("Colunas de indicadores não encontradas. Verifique os nomes em 'indicators.py'.")
        return None

    # --- INÍCIO DA SEÇÃO DE DEBUG ---
    # Pegando os valores que o robô está usando para a decisão
    open_price_current = df_with_indicators["open"].iloc[-1]
    bb_lower_current = df_with_indicators[bb_lower_col].iloc[-1]
    bb_upper_current = df_with_indicators[bb_upper_col].iloc[-1]
    # Usamos iloc[-2] para o RSI porque ele é calculado com base na vela anterior que já fechou
    rsi_previous = df_with_indicators[rsi_col].iloc[-2]

    # Imprimindo os valores no log para podermos ver o "pensamento" do robô
    logging.info(f"[DEBUG ESTRATÉGIA] Abertura: {open_price_current:.5f} | "
                 f"RSI(-1): {rsi_previous:.2f} | "
                 f"Banda Superior: {bb_upper_current:.5f} | "
                 f"Banda Inferior: {bb_lower_current:.5f}")
    # --- FIM DA SEÇÃO DE DEBUG ---

    signal = None
    
    # Condição de Compra (CALL)
    is_below_band = open_price_current < bb_lower_current
    is_oversold = rsi_previous < 20
    if is_below_band and is_oversold:
        signal = "CALL"
        logging.warning(f"SINAL DE COMPRA (CALL) DETECTADO! Abertura < B.Inf ({is_below_band}) E RSI < 20 ({is_oversold})")

    # Condição de Venda (PUT)
    is_above_band = open_price_current > bb_upper_current
    is_overbought = rsi_previous > 80
    if is_above_band and is_overbought:
        signal = "PUT"
        logging.warning(f"SINAL DE VENDA (PUT) DETECTADO! Abertura > B.Sup ({is_above_band}) E RSI > 80 ({is_overbought})")

    return signal
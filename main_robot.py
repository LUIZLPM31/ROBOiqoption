import time
import logging
from datetime import datetime, timedelta

from iq_option_connection import IQOptionConnection
from strategy import check_signal
from risk_management import RiskManagement

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Configurações do Robô --- #
EMAIL = "luizpaulomoura@icloud.com"
PASSWORD = "Noah2806@"

# Apenas liste os nomes base dos pares que você tem interesse.
PREFERRED_ASSETS = ["EURUSD", "EURJPY", "GBPUSD", "AUDCAD", "USDCAD", "BTCUSD"]

TIMEFRAME = 60
EXPIRATION_TIME = 1 

INITIAL_BALANCE = 1000.0
STAKE_PERCENTAGE = 1.0
DAILY_STOP_LOSS_PERCENTAGE = 5.0
DAILY_TAKE_PROFIT_PERCENTAGE = 10.0

# --- Inicialização --- #
iq_connection = IQOptionConnection(EMAIL, PASSWORD)
risk_manager = RiskManagement(
    initial_balance=INITIAL_BALANCE,
    stake_percentage=STAKE_PERCENTAGE,
    daily_stop_loss_percentage=DAILY_STOP_LOSS_PERCENTAGE,
    daily_take_profit_percentage=DAILY_TAKE_PROFIT_PERCENTAGE
)

last_candle_times = {}

def find_active_assets(preferred, open_binary, open_digital):
    """
    Encontra a melhor versão disponível de cada ativo preferido (com prioridade)
    e ignora as versões que a biblioteca não suporta (como '-op').
    """
    final_assets = []
    processed_prefs = set()

    # Define a ordem de prioridade para as variações de cada ativo
    for pref_asset in preferred:
        if pref_asset in processed_prefs:
            continue

        # Prioridade 1: Nome exato (ex: "EURUSD") em Digitais
        if pref_asset in open_digital:
            final_assets.append({'name': pref_asset, 'type': 'digital'})
            processed_prefs.add(pref_asset)
            continue # Pula para o próximo ativo preferido

        # Prioridade 2: Nome exato (ex: "EURUSD") em Binárias
        if pref_asset in open_binary:
            final_assets.append({'name': pref_asset, 'type': 'binary'})
            processed_prefs.add(pref_asset)
            continue

        # Prioridade 3: Versão TURBO (ex: "EURUSD-TURBO") em Binárias
        turbo_name = f"{pref_asset}-TURBO"
        if turbo_name in open_binary:
            final_assets.append({'name': turbo_name, 'type': 'binary'})
            processed_prefs.add(pref_asset)
            continue
            
        # Prioridade 4: Versão OTC (ex: "EURUSD-OTC") em Binárias
        otc_name = f"{pref_asset}-OTC"
        if otc_name in open_binary:
            final_assets.append({'name': otc_name, 'type': 'binary'})
            processed_prefs.add(pref_asset)
            continue

    return final_assets


def main():
    if not iq_connection.connect(): return
    try:
        iq_connection.api.change_balance('PRACTICE')
    except Exception as e:
        logging.error(f"Não foi possível alterar para a conta de prática: {e}")
        return

    logging.info("Robô iniciado.")
    logging.info("Pressione Ctrl+C para parar.")

    active_assets_to_monitor = find_active_assets(
        PREFERRED_ASSETS, 
        iq_connection.open_binary_assets, 
        iq_connection.open_digital_assets
    )
    logging.info(f"Ativos encontrados para monitorar: {[a['name'] for a in active_assets_to_monitor]}")

    try:
        while True:
            now = datetime.now()
            if now.minute % 5 == 0 and now.second < 5:
                iq_connection.update_open_assets()
                active_assets_to_monitor = find_active_assets(
                    PREFERRED_ASSETS, 
                    iq_connection.open_binary_assets, 
                    iq_connection.open_digital_assets
                )
                logging.info(f"Lista de ativos para monitorar atualizada: {[a['name'] for a in active_assets_to_monitor]}")

            if now.hour == 0 and now.minute == 0 and now.second < 5:
                risk_manager.reset_daily_stats()
            if risk_manager.check_stop_loss() or risk_manager.check_take_profit():
                logging.info("Metas de risco atingidas. Pausando até amanhã.")
                tomorrow = now + timedelta(days=1)
                midnight = tomorrow.replace(hour=0, minute=0, second=5)
                time.sleep((midnight - now).total_seconds())
                continue

            for asset_info in active_assets_to_monitor:
                asset_name = asset_info['name']
                option_type = asset_info['type']

                logging.info(f"--- Analisando {asset_name} ({option_type}) ---")
                
                candles_df = iq_connection.get_candles(asset_name, TIMEFRAME, 30, time.time())

                if candles_df is None or candles_df.empty: 
                    logging.warning(f"Não foi possível obter velas para {asset_name}. A biblioteca pode não suportar este ativo.")
                    continue
                
                current_candle_timestamp = candles_df.index[-1]

                if asset_name not in last_candle_times or current_candle_timestamp > last_candle_times.get(asset_name, 0):
                    last_candle_times[asset_name] = current_candle_timestamp
                    logging.info(f"Nova vela para {asset_name}: {current_candle_timestamp}")
                    signal = check_signal(candles_df)

                    if signal:
                        stake = risk_manager.calculate_stake()
                        logging.warning(f"SINAL {signal} EM {asset_name} ({option_type})! Entrada: {stake:.2f} USD")
                        
                        order_id = None
                        if option_type == 'binary':
                            order_id = iq_connection.buy_binary(stake, asset_name, signal.lower(), EXPIRATION_TIME)
                        elif option_type == 'digital':
                            order_id = iq_connection.buy_digital(stake, asset_name, signal.lower(), EXPIRATION_TIME)
                        
                        if order_id:
                            logging.info(f"Ordem executada com ID: {order_id}")
                        else:
                            logging.error(f"Falha ao executar ordem para {asset_name}.")
                else:
                    logging.info(f"Aguardando nova vela para {asset_name}.")
            
            current_time = datetime.now()
            seconds_to_wait = TIMEFRAME - (current_time.second % TIMEFRAME)
            logging.info(f"Ciclo concluído. Aguardando {seconds_to_wait}s...")
            time.sleep(seconds_to_wait)

    except KeyboardInterrupt:
        logging.info("Sinal de interrupção recebido...")
    finally:
        logging.info("Robô finalizado.")

if __name__ == "__main__":
    main()
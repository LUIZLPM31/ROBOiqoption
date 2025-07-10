from iqoptionapi.stable_api import IQ_Option
import logging
import pandas as pd
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IQOptionConnection:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.api = None
        # Dicionários separados para cada tipo de mercado
        self.open_binary_assets = {}
        self.open_digital_assets = {}

    def connect(self):
        logging.info("Tentando conectar à IQ Option...")
        self.api = IQ_Option(self.email, self.password)
        check, reason = self.api.connect()

        if check:
            logging.info("Conexão bem-sucedida!")
            self.update_open_assets()
            return True
        else:
            logging.error(f"Falha na conexão: {reason}")
            return False

    def update_open_assets(self):
        """Atualiza a lista de ativos abertos para Binárias e Digitais."""
        logging.info("Atualizando a lista de ativos abertos...")
        try:
            all_assets = self.api.get_all_open_time()
            
            # Pega os ativos de Binárias/Turbo
            self.open_binary_assets = all_assets.get('binary', {})
            logging.info(f"{len(self.open_binary_assets)} ativos de Binárias/Turbo estão abertos.")
            logging.info(f"Nomes (Binárias): {list(self.open_binary_assets.keys())[:30]}")

            # Pega os ativos de Digitais
            self.open_digital_assets = all_assets.get('digital', {})
            logging.info(f"{len(self.open_digital_assets)} ativos de Digitais estão abertos.")
            logging.info(f"Nomes (Digitais): {list(self.open_digital_assets.keys())[:30]}")

        except Exception as e:
            logging.error(f"Não foi possível obter a lista de ativos abertos: {e}")
            self.open_binary_assets = {}
            self.open_digital_assets = {}

    def check_asset_open(self, asset_name, option_type):
        """Verifica se um ativo específico está aberto para o tipo de opção desejado."""
        asset_name = asset_name.upper()
        if option_type == 'binary':
            return self.open_binary_assets.get(asset_name, {}).get('open', False)
        elif option_type == 'digital':
            return self.open_digital_assets.get(asset_name, {}).get('open', False)
        return False

    def get_candles(self, asset, interval, count, endtime):
        # Esta função permanece a mesma
        if not self.api or not self.api.check_connect(): return None
        candles = self.api.get_candles(asset, interval, count, endtime)
        if candles:
            df = pd.DataFrame(candles)
            if 'max' in df.columns and 'min' in df.columns:
                df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)
            required_cols = ['open', 'high', 'low', 'close', 'volume', 'from', 'to', 'id']
            if not all(col in df.columns for col in required_cols): return None
            df = df[required_cols]
            df['from'] = pd.to_datetime(df['from'], unit='s')
            df.set_index('from', inplace=True)
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            return df.sort_index()
        return None

    def buy_binary(self, amount, asset, action, duration):
        """Função para comprar Opções Binárias/Turbo."""
        logging.info(f"Executando ordem BINÁRIA de {action} para {asset}...")
        status, order_id = self.api.buy(amount, asset, action, duration)
        if status:
            return order_id
        else:
            logging.error(f"Falha ao executar ordem BINÁRIA: {order_id}")
            return None

    def buy_digital(self, amount, asset, action, duration):
        """Função para comprar Opções Digitais."""
        logging.info(f"Executando ordem DIGITAL de {action} para {asset}...")
        # A duração para digitais é em minutos e deve ser 1, 5 ou 15.
        _, order_id = self.api.buy_digital_spot(asset, amount, action, duration)
        if order_id != "error":
            return order_id
        else:
            logging.error("Falha ao executar ordem DIGITAL.")
            return None
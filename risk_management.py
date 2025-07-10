class RiskManagement:
    def __init__(self, initial_balance, stake_percentage, daily_stop_loss_percentage, daily_take_profit_percentage):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.stake_percentage = stake_percentage
        self.daily_stop_loss_percentage = daily_stop_loss_percentage
        self.daily_take_profit_percentage = daily_take_profit_percentage
        self.daily_profit_loss = 0.0
        self.trades_today = 0

    def calculate_stake(self):
        return self.current_balance * (self.stake_percentage / 100)

    def update_daily_profit_loss(self, profit_loss):
        self.daily_profit_loss += profit_loss
        self.current_balance += profit_loss
        self.trades_today += 1

    def check_stop_loss(self):
        max_loss = self.initial_balance * (self.daily_stop_loss_percentage / 100)
        return self.daily_profit_loss <= -max_loss

    def check_take_profit(self):
        min_profit = self.initial_balance * (self.daily_take_profit_percentage / 100)
        return self.daily_profit_loss >= min_profit

    def reset_daily_stats(self):
        self.daily_profit_loss = 0.0
        self.trades_today = 0

# Exemplo de uso (para teste)
# if __name__ == "__main__":
#     rm = RiskManagement(initial_balance=1000, stake_percentage=1, daily_stop_loss_percentage=5, daily_take_profit_percentage=10)
#     print(f"Stake inicial: {rm.calculate_stake():.2f}")

#     # Simular algumas operações
#     rm.update_daily_profit_loss(10) # Ganho
#     print(f"Lucro/Perda diário: {rm.daily_profit_loss:.2f}, Saldo atual: {rm.current_balance:.2f}")
#     print(f"Atingiu Stop Loss? {rm.check_stop_loss()}")
#     print(f"Atingiu Take Profit? {rm.check_take_profit()}")

#     rm.update_daily_profit_loss(-30) # Perda
#     print(f"Lucro/Perda diário: {rm.daily_profit_loss:.2f}, Saldo atual: {rm.current_balance:.2f}")
#     print(f"Atingiu Stop Loss? {rm.check_stop_loss()}")
#     print(f"Atingiu Take Profit? {rm.check_take_profit()}")

#     rm.update_daily_profit_loss(100) # Ganho grande
#     print(f"Lucro/Perda diário: {rm.daily_profit_loss:.2f}, Saldo atual: {rm.current_balance:.2f}")
#     print(f"Atingiu Stop Loss? {rm.check_stop_loss()}")
#     print(f"Atingiu Take Profit? {rm.check_take_profit()}")

#     rm.reset_daily_stats()
#     print(f"Após reset: Lucro/Perda diário: {rm.daily_profit_loss:.2f}")



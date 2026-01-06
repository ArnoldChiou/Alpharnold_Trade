from binance.client import Client
from binance import AsyncClient, BinanceSocketManager
import config

class BinanceManager:
    def __init__(self):
        # 1. 初始化同步客戶端 (用於 REST API：查餘額、下單)
        self.rest_client = Client(
            config.API_KEY, 
            config.API_SECRET, 
            testnet=config.IS_TESTNET
        )
        
        # 2. 初始化非同步客戶端屬性 (用於 WebSocket)
        self.async_client = None
        self.socket_manager = None

    async def init_websocket(self):
        """初始化非同步連線"""
        self.async_client = await AsyncClient.create(
            config.API_KEY, 
            config.API_SECRET, 
            testnet=config.IS_TESTNET
        )
        self.socket_manager = BinanceSocketManager(self.async_client)
        return self.socket_manager

    def place_futures_order(self, symbol, side, qty, order_type="MARKET"):
        """統一的下單入口，處理異常"""
        try:
            order = self.rest_client.futures_create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=qty
            )
            return True, order
        except Exception as e:
            return False, str(e)

    def get_total_balance(self):
        """獲取合約帳戶 USDT 的錢包餘額"""
        try:
            # 獲取合約帳戶資訊
            account = self.rest_client.futures_account()
            for asset in account['assets']:
                if asset['asset'] == 'USDT':
                    return float(asset['walletBalance'])
            return 0.0
        except Exception as e:
            print(f"餘額抓取失敗: {e}")
            return 0.0

    async def close(self):
        """安全關閉連線"""
        if self.async_client:
            await self.async_client.close_connection()
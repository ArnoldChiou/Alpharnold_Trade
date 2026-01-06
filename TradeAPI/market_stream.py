import asyncio
import threading
from PySide6.QtCore import QObject, Signal
from binance import AsyncClient, BinanceSocketManager

class MarketStream(QObject):
    # 當任何幣種價格更新時發射：(symbol, price)
    price_updated = Signal(str, float)

    def __init__(self, symbols, is_testnet=False):
        super().__init__()
        self.symbols = [s.lower() for s in symbols]
        self.is_testnet = is_testnet
        self._running = False

    def start(self):
        self._running = True
        # 在獨立執行緒啟動事件迴圈
        threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._listen_prices())

    async def _listen_prices(self):
        client = await AsyncClient.create(testnet=self.is_testnet)
        bsm = BinanceSocketManager(client)
        
        # 建立多幣種流 (Combined Streams)
        # 格式: <symbol>@markPrice 或 <symbol>@ticker
        streams = [f"{s}@ticker" for s in self.symbols]
        ts = bsm.multiplex_socket(streams)

        async with ts as tscm:
            while self._running:
                res = await tscm.recv()
                if res and 'data' in res:
                    data = res['data']
                    symbol = data['s']
                    price = float(data['c']) # 'c' 代表當前成交價
                    self.price_updated.emit(symbol, price)

        await client.close_connection()

    def stop(self):
        self._running = False
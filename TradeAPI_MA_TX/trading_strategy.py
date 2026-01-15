from PySide6.QtCore import QObject, Signal
import config
from sk_utils import sk

class TradingWorker(QObject):
    log_signal = Signal(str)

    def __init__(self, order_obj, params, symbol):
        super().__init__()
        self.order = order_obj
        self.params = params
        self.symbol = symbol
        
        self.history_prices = [] 
        self.ma_len = params.get('ma', 5)
        self.current_ma = 0.0
        self.history_ready = False

        # 交易狀態初始化
        self.in_position = False
        self.current_side = None
        self.entry_price = 0.0
        self.extreme_price = 0.0
        self.ttp_active = False

    def add_history(self, close_price, is_history=False):
        """ 不斷存入最新價格，並更新內部 MA 數值 """
        self.history_prices.append(close_price)
        
        # 保持長度為 MA 週期，這樣桶子裡永遠是「最近的 N 根 K 棒」
        if len(self.history_prices) > self.ma_len:
            self.history_prices.pop(0)

        # 每次存入都偷偷算一下 MA
        if len(self.history_prices) >= self.ma_len:
            ma_val = sum(self.history_prices) / self.ma_len
            self.current_ma = round(ma_val, 2)

    def reload_history(self, new_prices):
        """ 
        [新增] 熱更新功能：
        清空舊資料並重新載入 (用於每日 15:00 換日更新) 
        """
        self.history_prices = []
        self.history_ready = False
        
        # 逐筆加入，讓 add_history 自動處理 MA 計算與長度控制
        for p in new_prices:
            self.add_history(p, is_history=True)
            
        # 重新發送狀態報告 (顯示新的 MA)
        self.report_status()

    def report_status(self):
        """ 由 UI 觸發，顯示最終結果 """
        if len(self.history_prices) < self.ma_len:
            self.log_signal.emit(f"⚠️ 資料載入中... 目前 {len(self.history_prices)} 筆")
            return

        buffer_val = self.params.get('buffer', 0.1)
        threshold = self.current_ma * (1 + buffer_val / 100)
        
        msg = (
            f"\n{'='*40}\n"
            f"🔄 均線數據已更新 (夜盤模式)\n"
            f" ● 基準 MA({self.ma_len}): {self.current_ma:.2f}\n"
            f" ● 買進門檻價: {threshold:.2f}\n"
            f" ● 參考資料長度: {len(self.history_prices)} 筆\n"
            f"{'='*40}"
        )
        self.log_signal.emit(msg)
        self.history_ready = True

    def process_quote(self, price):
        """ 接收即時報價：直接比對固定門檻 """
        if not self.history_ready:
            return 

        if not self.in_position:
            # 使用目前的 MA 門檻
            buffer_val = self.params.get('buffer', 0.1)
            static_threshold = self.current_ma * (1 + buffer_val / 100)
            
            # 觸發進場
            if price >= static_threshold:
                self.execute_order("BUY", price)
        else:
            self.manage_exit(price)

    def execute_order(self, side, price):
        """ 發送下單指令到群益 API """
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = self.params['account']
        pOrder.bstrStockNo = self.symbol
        pOrder.sBuySell = 0 if side == "BUY" else 1
        pOrder.sTradeType = 0 # 自動
        pOrder.sNewClose = 0  # 新倉
        pOrder.bstrPrice = str(int(price))
        pOrder.nQty = int(self.params['qty'])

        # 下單
        res = self.order.SendFutureOrderCLR(config.USER_ID, False, pOrder)
        self.log_signal.emit(f"🚀 {side} 指令發送：{price} | API 回傳碼: {res}")
        
        if side == "BUY":
            self.in_position, self.current_side, self.entry_price, self.extreme_price = True, side, price, price
        else:
            self.in_position = False
            self.ttp_active = False
            self.entry_price = 0.0
            self.extreme_price = 0.0

    def manage_exit(self, price):
        """ 停損與移動停利管理 """
        # 1. 固定停損 (SL)
        if price <= self.entry_price * (1 - self.params['sl'] / 100):
            self.log_signal.emit(f"🚩 觸發固定停損點：{price}")
            self.execute_order("SELL", price)
            return
        
        # 更新最高價
        if price > self.extreme_price: 
            self.extreme_price = price

        # 2. 移動停利觸發
        ttp_trig_p = self.entry_price * (1 + self.params['ttp_trig'] / 100)
        if not self.ttp_active and price >= ttp_trig_p:
            self.ttp_active = True
            self.log_signal.emit(f"🎯 獲利達到 {self.params['ttp_trig']}%，開啟移動停利追蹤")

        # 3. 移動停利回撤平倉
        if self.ttp_active:
            retrace_p = self.extreme_price * (1 - self.params['ttp_call'] / 100)
            if price <= retrace_p:
                self.log_signal.emit(f"💰 獲利回撤平倉：{price} (高點 {self.extreme_price})")
                self.execute_order("SELL", price)
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
        self.current_ma = 0.0      # 這將是一個固定的昨日 MA
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
        
        # 保持長度為 5，這樣桶子裡永遠是「最近的 5 根 K 棒」
        if len(self.history_prices) > self.ma_len:
            self.history_prices.pop(0)

        # 每次存入都偷偷算一下 MA，但不顯示
        if len(self.history_prices) >= self.ma_len:
            ma_val = sum(self.history_prices) / self.ma_len
            self.current_ma = round(ma_val, 2)

    def report_status(self):
        """ 由 UI 觸發，顯示最終結果 """
        if len(self.history_prices) < self.ma_len:
            self.log_signal.emit(f"⚠️ 資料載入中... 目前 {len(self.history_prices)} 筆")
            return

        buffer_val = self.params.get('buffer', 0.1)
        threshold = self.current_ma * (1 + buffer_val / 100)
        
        # 這裡印出來的 current_ma 一定是桶子裡最後存進去的那 5 筆算出來的
        msg = (
            f"\n{'='*40}\n"
            f"📈 均線數據計算成功！\n"
            f" ● 基準 MA({self.ma_len}): {self.current_ma:.2f}\n"
            f" ● 買進門檻價: {threshold:.2f}\n"
            f" ● 歷史筆數: {len(self.history_prices)} 筆 (已更新至最新)\n"
            f"{'='*40}"
        )
        self.log_signal.emit(msg)
        self.history_ready = True

    def process_quote(self, price):
        """ 接收即時報價：直接比對固定門檻 """
        if not self.history_ready:
            return 

        if not self.in_position:
            # 直接使用 report_status 算好的固定 MA
            buffer_val = self.params.get('buffer', 0.1)
            static_threshold = self.current_ma * (1 + buffer_val / 100)
            
            # 只要現在價格突破昨日 MA 門檻
            if price >= static_threshold:
                self.execute_order("BUY", price)
        else:
            self.manage_exit(price)

        

    def execute_order(self, side, price):
        """ 發送下單指令到群益 API """
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = self.params['account']
        pOrder.bstrStockNo = self.symbol
        # 0 為買，1 為賣
        pOrder.sBuySell = 0 if side == "BUY" else 1
        pOrder.sTradeType = 0 # 自動
        pOrder.sNewClose = 0  # 新倉
        pOrder.bstrPrice = str(int(price))
        pOrder.nQty = int(self.params['qty'])

        # 這裡會真正下單到市場
        res = self.order.SendFutureOrderCLR(config.USER_ID, False, pOrder)
        self.log_signal.emit(f"🚀 {side} 指令發送：{price} | API 回傳碼: {res}")
        
        if side == "BUY":
            self.in_position, self.current_side, self.entry_price, self.extreme_price = True, side, price, price
        else:
            # 平倉後清空狀態
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

        # 2. 移動停利觸發 (TTP Trigger)
        ttp_trig_p = self.entry_price * (1 + self.params['ttp_trig'] / 100)
        if not self.ttp_active and price >= ttp_trig_p:
            self.ttp_active = True
            self.log_signal.emit(f"🎯 獲利達到 {self.params['ttp_trig']}%，開啟移動停利追蹤")

        # 3. 移動停利回撤平倉 (TTP Call)
        if self.ttp_active:
            retrace_p = self.extreme_price * (1 - self.params['ttp_call'] / 100)
            if price <= retrace_p:
                self.log_signal.emit(f"💰 獲利回撤平倉：{price} (高點 {self.extreme_price})")
                self.execute_order("SELL", price)

    def close_position(self):
        """ 強制平倉介面 (視需求呼叫) """
        if self.in_position:
            # 這裡應補上讀取當前報價來平倉的邏輯
            self.log_signal.emit("⏹️ 執行手動停止策略，平倉清倉")
            # 實作時可呼叫 execute_order("SELL", ...)
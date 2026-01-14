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
        
        self.price_history = []
        self.in_position = False
        self.current_side = None
        self.entry_price = 0.0
        self.extreme_price = 0.0
        self.ttp_active = False

    def add_history(self, price):
        """ 接收歷史數據填補 MA """
        self.price_history.append(price)
        if len(self.price_history) > self.params['ma']:
            self.price_history.pop(0)
        
        # 歷史資料補滿時，立刻顯示計算結果
        if len(self.price_history) == self.params['ma']:
            self.report_initial_values()

    def report_initial_values(self):
        """ 依要求顯示 MA 數值與進場門檻 """
        avg_p = sum(self.price_history) / len(self.price_history)
        # 進場價 = MA * (1 + Buffer%)
        entry_threshold = avg_p * (1 + self.params['buffer'] / 100)
        
        self.log_signal.emit("=" * 40)
        self.log_signal.emit(f"📈 均線數據計算完成：")
        self.log_signal.emit(f"   ● 當前 MA({self.params['ma']}): {avg_p:.2f}")
        self.log_signal.emit(f"   ● 買進觸發價格: {entry_threshold:.2f} (緩衝 {self.params['buffer']}%)")
        self.log_signal.emit("=" * 40)

    def process_quote(self, price):
        if not self.price_history: return
        
        # 用最新報價更新序列
        self.price_history[-1] = price
        ma_val = sum(self.price_history) / len(self.price_history)
        
        if not self.in_position:
            # 突破買進判斷
            threshold = ma_val * (1 + self.params['buffer'] / 100)
            if price >= threshold:
                self.execute_order("BUY", price)
        else:
            self.manage_exit(price)

    def execute_order(self, side, price):
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = self.params['account']
        pOrder.bstrStockNo = self.symbol
        pOrder.sBuySell = 0 if side == "BUY" else 1
        pOrder.sTradeType = 0
        pOrder.sNewClose = 0
        pOrder.bstrPrice = str(int(price))
        pOrder.nQty = int(self.params['qty'])

        res = self.order.SendFutureOrderCLR(config.USER_ID, False, pOrder)
        self.log_signal.emit(f"🚀 {side} 進場：{price} | 指令回傳: {res}")
        
        self.in_position, self.current_side, self.entry_price, self.extreme_price = True, side, price, price

    def manage_exit(self, price):
        # 停損
        if price <= self.entry_price * (1 - self.params['sl'] / 100):
            self.log_signal.emit(f"🚩 停損平倉：{price}")
            self.close_position()
            return
        
        if price > self.extreme_price: self.extreme_price = price

        # 移停邏輯
        ttp_trig_p = self.entry_price * (1 + self.params['ttp_trig'] / 100)
        if not self.ttp_active and price >= ttp_trig_p:
            self.ttp_active = True
            self.log_signal.emit("🎯 達到移動停利門檻，開始追蹤")

        if self.ttp_active:
            retrace_p = self.extreme_price * (1 - self.params['ttp_call'] / 100)
            if price <= retrace_p:
                self.log_signal.emit(f"💰 移停平倉：{price} (回檔自 {self.extreme_price})")
                self.close_position()

    def close_position(self):
        self.in_position, self.ttp_active = False, False
        self.log_signal.emit("⏹️ 交易流程結束。")
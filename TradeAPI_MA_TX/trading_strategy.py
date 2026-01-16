from PySide6.QtCore import QObject, Signal
import json
import os
import config
from sk_utils import sk

# 用於儲存狀態的資料夾
STATE_FOLDER = "tx_states"
if not os.path.exists(STATE_FOLDER):
    os.makedirs(STATE_FOLDER)

class TradingWorker(QObject):
    log_signal = Signal(str)
    status_signal = Signal(str) # 新增訊號：回傳倉位狀態給 UI 表格

    def __init__(self, order_obj, params, symbol):
        super().__init__()
        self.order = order_obj
        self.params = params
        self.symbol = symbol
        
        # 唯一的狀態檔案路徑 (使用帳號作為檔名)
        self.state_file = os.path.join(STATE_FOLDER, f"{params['account']}_{symbol}.json")
        
        self.history_prices = [] 
        self.ma_len = params.get('ma', 5)
        self.current_ma = 0.0
        self.history_ready = False

        # 交易狀態 (將會從檔案讀取)
        self.in_position = False
        self.current_side = None
        self.entry_price = 0.0
        self.extreme_price = 0.0
        self.ttp_active = False
        
        # 初始化時載入狀態
        self.load_state()

    def add_history(self, close_price, is_history=False):
        self.history_prices.append(close_price)
        if len(self.history_prices) > self.ma_len:
            self.history_prices.pop(0)
        if len(self.history_prices) >= self.ma_len:
            ma_val = sum(self.history_prices) / self.ma_len
            self.current_ma = round(ma_val, 2)

    def reload_history(self, new_prices):
        self.history_prices = []
        self.history_ready = False
        for p in new_prices:
            self.add_history(p, is_history=True)
        self.report_status()

    def report_status(self):
        if len(self.history_prices) < self.ma_len:
            return
            
        buffer_val = self.params.get('buffer', 0.1)
        threshold = self.current_ma * (1 + buffer_val / 100)
        
        msg = (
            f"均線更新 MA({self.ma_len}): {self.current_ma:.2f} | 門檻: {threshold:.2f}"
        )
        self.log_signal.emit(msg)
        self.history_ready = True
        
        # 若目前有倉位，發送狀態到表格
        if self.in_position:
            self.status_signal.emit(f"{'多' if self.current_side=='BUY' else '空'} @ {self.entry_price}")

    def process_quote(self, price):
        if not self.history_ready:
            return 

        if not self.in_position:
            # 簡單策略：只做多範例 (若需做空請自行還原)
            buffer_val = self.params.get('buffer', 0.1)
            static_threshold = self.current_ma * (1 + buffer_val / 100)
            
            if price >= static_threshold:
                self.execute_order("BUY", price)
        else:
            self.manage_exit(price)

    def execute_order(self, side, price):
        # 每次下單前驗證憑證
        self.order.ReadCertByID(config.USER_ID)
        
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = self.params['account'] # 這裡會自動填入正確的子帳號
        pOrder.bstrStockNo = self.symbol
        pOrder.sBuySell = 0 if side == "BUY" else 1
        pOrder.sTradeType = 0 
        pOrder.sNewClose = 0  
        pOrder.bstrPrice = str(int(price))
        pOrder.nQty = int(self.params['qty'])

        res = self.order.SendFutureOrderCLR(config.USER_ID, False, pOrder)
        self.log_signal.emit(f"🚀 {side} 指令發送：{price} | API: {res}")
        
        if side == "BUY":
            self.in_position = True
            self.current_side = side
            self.entry_price = price
            self.extreme_price = price
            self.status_signal.emit(f"多 @ {price}")
        else:
            # 平倉 (SELL)
            self.in_position = False
            self.ttp_active = False
            self.entry_price = 0.0
            self.extreme_price = 0.0
            self.status_signal.emit("---")
            
        # 下單後立即存檔
        self.save_state()

    def manage_exit(self, price):
        # 1. 固定停損
        if price <= self.entry_price * (1 - self.params['sl'] / 100):
            self.log_signal.emit(f"🚩 觸發停損：{price}")
            self.execute_order("SELL", price)
            return
        
        # 更新最高價
        if price > self.extreme_price: 
            self.extreme_price = price
            # 發生變動時也存一下比較保險
            self.save_state()

        # 2. 移動停利
        ttp_trig_p = self.entry_price * (1 + self.params['ttp_trig'] / 100)
        if not self.ttp_active and price >= ttp_trig_p:
            self.ttp_active = True
            self.log_signal.emit(f"🎯 移動停利啟動")
            self.save_state()

        # 3. 回撤平倉
        if self.ttp_active:
            retrace_p = self.extreme_price * (1 - self.params['ttp_call'] / 100)
            if price <= retrace_p:
                self.log_signal.emit(f"💰 獲利回撤平倉：{price}")
                self.execute_order("SELL", price)

    def save_state(self):
        """ 將當前倉位狀態寫入 JSON """
        state = {
            "in_position": self.in_position,
            "current_side": self.current_side,
            "entry_price": self.entry_price,
            "extreme_price": self.extreme_price,
            "ttp_active": self.ttp_active
        }
        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"存檔失敗: {e}")

    def load_state(self):
        """ 啟動時讀取 JSON """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    self.in_position = state.get("in_position", False)
                    self.current_side = state.get("current_side", None)
                    self.entry_price = state.get("entry_price", 0.0)
                    self.extreme_price = state.get("extreme_price", 0.0)
                    self.ttp_active = state.get("ttp_active", False)
                    
                    if self.in_position:
                        self.status_signal.emit(f"接管: {self.current_side} @ {self.entry_price}")
            except Exception as e:
                self.log_signal.emit(f"⚠️ 讀取狀態失敗: {e}")
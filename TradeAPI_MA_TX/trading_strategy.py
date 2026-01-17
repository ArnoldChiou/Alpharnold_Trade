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

        # 分離多空參數
        self.long_p = params['long']
        self.short_p = params['short']

        # 決定需要保留的最大歷史長度
        self.max_ma_len = max(self.long_p['ma'], self.short_p['ma'])
        
        # 唯一的狀態檔案路徑 (使用帳號作為檔名)
        self.state_file = os.path.join(STATE_FOLDER, f"{params['account']}_{symbol}.json")
        
        self.history_prices = [] 
        self.current_ma_long = 0.0
        self.current_ma_short = 0.0
        self.history_ready = False

        # 交易狀態
        self.in_position = False
        self.current_side = None # "BUY" (做多) 或 "SELL" (做空)
        self.entry_price = 0.0
        self.best_price = 0.0 # 多單為最高價，空單為最低價
        self.ttp_active = False
        
        # 初始化時載入狀態
        self.load_state()

    def add_history(self, close_price, is_history=False):
        self.history_prices.append(close_price)
        if len(self.history_prices) > self.max_ma_len:
            self.history_prices.pop(0)
            
        # 計算兩條 MA
        if len(self.history_prices) >= self.long_p['ma']:
            sub_list = self.history_prices[-self.long_p['ma']:]
            self.current_ma_long = round(sum(sub_list) / len(sub_list), 2)
            
        if len(self.history_prices) >= self.short_p['ma']:
            sub_list = self.history_prices[-self.short_p['ma']:]
            self.current_ma_short = round(sum(sub_list) / len(sub_list), 2)

    def reload_history(self, new_prices):
        self.history_prices = []
        self.history_ready = False
        for p in new_prices:
            self.add_history(p, is_history=True)
        self.report_status()

    def report_status(self):
        if len(self.history_prices) < self.max_ma_len:
            return
            
        long_thresh = self.current_ma_long * (1 + self.long_p['buffer'] / 100)
        short_thresh = self.current_ma_short * (1 - self.short_p['buffer'] / 100)
        
        msg = (
            f"MAL({self.long_p['ma']}):{self.current_ma_long:.0f} (多:{long_thresh:.0f}) | "
            f"MAS({self.short_p['ma']}):{self.current_ma_short:.0f} (空:{short_thresh:.0f})"
        )
        self.log_signal.emit(msg)
        self.history_ready = True
        
        if self.in_position:
            side_text = '多' if self.current_side=='BUY' else '空'
            self.status_signal.emit(f"{side_text} @ {self.entry_price}")

    def process_quote(self, price):
        if not self.history_ready:
            return 

        if not self.in_position:
            self.check_entry(price)
        else:
            if self.current_side == "BUY":
                self.manage_long_exit(price)
            elif self.current_side == "SELL":
                self.manage_short_exit(price)

    def check_entry(self, price):
        # --- 判斷做多 ---
        long_thresh = self.current_ma_long * (1 + self.long_p['buffer'] / 100)
        if price >= long_thresh:
            if self.check_slippage(price, long_thresh, "BUY"):
                self.execute_order("BUY", price, self.long_p['qty'])
            return

        # --- 判斷做空 ---
        short_thresh = self.current_ma_short * (1 - self.short_p['buffer'] / 100)
        if price <= short_thresh:
            if self.check_slippage(price, short_thresh, "SELL"):
                self.execute_order("SELL", price, self.short_p['qty'])
            return

    def check_slippage(self, price, target_price, side):
        max_slippage = 5.0
        # 做多：價格遠高於目標價 -> 不追
        if side == "BUY" and price > (target_price + max_slippage):
            self.log_signal.emit(f"⚠️ 價格過高 ({price})！高於進場價 {target_price:.0f}，放棄追多")
            return False
        # 做空：價格遠低於目標價 -> 不追
        if side == "SELL" and price < (target_price - max_slippage):
            self.log_signal.emit(f"⚠️ 價格過低 ({price})！低於進場價 {target_price:.0f}，放棄追空")
            return False
        return True

    def execute_order(self, side, price, qty):
        self.order.ReadCertByID(config.USER_ID)
        
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = self.params['account']
        pOrder.bstrStockNo = self.symbol
        pOrder.sBuySell = 0 if side == "BUY" else 1
        pOrder.sTradeType = 0 
        pOrder.sNewClose = 0 
        pOrder.bstrPrice = str(int(price))
        pOrder.nQty = int(qty)

        res = self.order.SendFutureOrderCLR(config.USER_ID, False, pOrder)
        self.log_signal.emit(f"🚀 {side} 指令發送：{price} (Qty:{qty}) | API: {res}")
        
        # 進入倉位狀態
        # 若原本無倉位 -> 建立新倉位
        if not self.in_position:
            self.in_position = True
            self.current_side = side
            self.entry_price = price
            self.best_price = price # 多:最高, 空:最低
            self.status_signal.emit(f"{'多' if side=='BUY' else '空'} @ {price}")
        else:
            # 原本有倉位 -> 視為平倉 (假設反向單即平倉)
            self.in_position = False
            self.ttp_active = False
            self.entry_price = 0.0
            self.best_price = 0.0
            self.status_signal.emit("---")
            
        self.save_state()

    def manage_long_exit(self, price):
        # 1. 固定停損 (價格下跌)
        sl_price = self.entry_price * (1 - self.long_p['sl'] / 100)
        if price <= sl_price:
            self.log_signal.emit(f"🚩 多單停損觸發：{price}")
            self.execute_order("SELL", price, self.long_p['qty'])
            return
        
        # 更新最高價
        if price > self.best_price: 
            self.best_price = price
            self.save_state()

        # 2. 移動停利 (價格回檔)
        ttp_trig_p = self.entry_price * (1 + self.long_p['ttp_trig'] / 100)
        if not self.ttp_active and price >= ttp_trig_p:
            self.ttp_active = True
            self.log_signal.emit(f"🎯 多單移停啟動")
            self.save_state()

        if self.ttp_active:
            retrace_p = self.best_price * (1 - self.long_p['ttp_call'] / 100)
            if price <= retrace_p:
                self.log_signal.emit(f"💰 多單獲利回撤平倉：{price}")
                self.execute_order("SELL", price, self.long_p['qty'])

    def manage_short_exit(self, price):
        # 1. 固定停損 (價格上漲)
        sl_price = self.entry_price * (1 + self.short_p['sl'] / 100)
        if price >= sl_price:
            self.log_signal.emit(f"🚩 空單停損觸發：{price}")
            self.execute_order("BUY", price, self.short_p['qty'])
            return
        
        # 更新最低價
        if price < self.best_price: 
            self.best_price = price
            self.save_state()

        # 2. 移動停利 (價格反彈)
        # 空單獲利是價格下跌，觸發點為 價格 <= 進場 * (1 - %)
        ttp_trig_p = self.entry_price * (1 - self.short_p['ttp_trig'] / 100)
        if not self.ttp_active and price <= ttp_trig_p:
            self.ttp_active = True
            self.log_signal.emit(f"🎯 空單移停啟動")
            self.save_state()

        if self.ttp_active:
            # 回撤是價格上漲，回撤點為 最低價 * (1 + %)
            retrace_p = self.best_price * (1 + self.short_p['ttp_call'] / 100)
            if price >= retrace_p:
                self.log_signal.emit(f"💰 空單獲利反彈平倉：{price}")
                self.execute_order("BUY", price, self.short_p['qty'])

    def save_state(self):
        state = {
            "in_position": self.in_position,
            "current_side": self.current_side,
            "entry_price": self.entry_price,
            "best_price": self.best_price,
            "ttp_active": self.ttp_active
        }
        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"存檔失敗: {e}")

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    self.in_position = state.get("in_position", False)
                    self.current_side = state.get("current_side", None)
                    self.entry_price = state.get("entry_price", 0.0)
                    self.best_price = state.get("best_price", 0.0) # 相容舊版 extreme_price
                    if self.best_price == 0.0:
                         self.best_price = state.get("extreme_price", 0.0)
                    self.ttp_active = state.get("ttp_active", False)
                    
                    if self.in_position:
                        side_text = '多' if self.current_side=='BUY' else '空'
                        self.status_signal.emit(f"接管: {side_text} @ {self.entry_price}")
            except Exception as e:
                self.log_signal.emit(f"⚠️ 讀取狀態失敗: {e}")
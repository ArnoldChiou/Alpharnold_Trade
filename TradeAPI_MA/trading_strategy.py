import time, json, os, hashlib, threading
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from market_utils import get_ma_level, get_symbol_rules, round_step_size

STATE_FOLDER = "position_states"

class TradingWorker(QObject):
    price_update = Signal(float)
    log_update = Signal(str)
    finished = Signal()

    def __init__(self, client, params, symbol, wait_for_reset=False):
        super().__init__()
        self.client = client
        self.params = params
        self.symbol = symbol
        self.is_running = False
        self.curr_price = 0.0
        
        api_str = getattr(client, 'API_KEY', 'unknown')
        api_hash = hashlib.md5(str(api_str).encode()).hexdigest()[:8]
        self.state_file = os.path.join(STATE_FOLDER, f"state_{api_hash}_{self.symbol}.json")
        
        self.in_position = False
        self.current_side = None # "BUY" (做多) 或 "SELL" (做空)
        self.position_qty = 0.0
        self.entry_price = 0.0
        self.extreme_price = 0.0 # 多單紀錄最高價，空單紀錄最低價
        self.ttp_active = False
        self.sl_price = 0.0
        self.next_rollover_ms = 0
        self.long_trigger = float('inf')
        self.short_trigger = 0.0
        
        if not os.path.exists(STATE_FOLDER): os.makedirs(STATE_FOLDER)
        self.load_state()

    def safe_emit_log(self, msg):
        try: self.log_update.emit(msg)
        except RuntimeError: pass

    def update_strategy_levels(self):
        """根據參數計算 MA 突破位"""
        # 使用傳入的 MA 天數參數
        win = int(self.params.get('ma_window', 6))
        ma_val = get_ma_level(self.client, self.symbol, win)
        
        if ma_val:
            # 多頭觸發 = MA * (1 + buffer%)
            self.long_trigger = ma_val * (1 + self.params['long_buffer'] / 100)
            # 空頭觸發 = MA * (1 - buffer%)
            self.short_trigger = ma_val * (1 - self.params['short_buffer'] / 100)
            now_str = datetime.now().strftime("%H:%M:%S")
            self.safe_emit_log(f"⏰ [{now_str}] MA({win})更新 | 多頭位:{self.long_trigger:.2f} | 空頭位:{self.short_trigger:.2f}")

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                # 換日 K 線對齊與 MA 更新
                now_ms = int(time.time() * 1000)
                if self.next_rollover_ms == 0 or now_ms >= self.next_rollover_ms:
                    klines = self.client.futures_klines(symbol=self.symbol, interval='1d', limit=1)
                    if klines:
                        self.update_strategy_levels()
                        self.next_rollover_ms = klines[0][6] + 1
                
                curr_price = self.curr_price
                if curr_price <= 0:
                    time.sleep(0.5); continue
                
                self.price_update.emit(curr_price)

                if not self.in_position:
                    direction = self.params.get('direction', 'BOTH')
                    # 進場邏輯
                    if direction in ["BOTH", "LONG"] and curr_price >= self.long_trigger:
                        self.execute_entry(curr_price, "BUY")
                    elif direction in ["BOTH", "SHORT"] and curr_price <= self.short_trigger:
                        self.execute_entry(curr_price, "SELL")
                else:
                    self.manage_position(curr_price)
                
                time.sleep(0.1)
            except Exception as e:
                self.safe_emit_log(f"系統異常: {e}"); time.sleep(2)

    def execute_entry(self, price, side):
        try:
            rules = get_symbol_rules(self.client, self.symbol)
            if not rules: return
            
            # 計算數量 (比例或固定)
            if self.params['order_mode'] == "FIXED":
                qty = round_step_size(self.params['fixed_qty'], rules['stepSize'])
            else:
                acc = self.client.futures_account()
                bal = next(float(a['walletBalance']) for a in acc['assets'] if a['asset'] == 'USDT')
                qty = round_step_size((bal * (self.params['trade_pct'] / 100) * 20.0) / price, rules['stepSize'])
            
            # 下市價單
            self.client.futures_create_order(symbol=self.symbol, side=side, type='MARKET', quantity=qty)
            
            self.in_position, self.current_side, self.position_qty = True, side, qty
            self.entry_price = price
            self.extreme_price = price
            self.ttp_active = False
            
            # 設定初始硬停損位
            sl_pct = self.params['long_sl'] if side == "BUY" else self.params['short_sl']
            self.sl_price = price * (1 - sl_pct/100) if side == "BUY" else price * (1 + sl_pct/100)
            
            self.save_state()
            self.safe_emit_log(f"✅ 【{side} 進場】價格:{price:.2f} | 停損:{self.sl_price:.2f}")
        except Exception as e:
            self.safe_emit_log(f"❌ 進場失敗: {e}")

    def manage_position(self, curr_price):
        side, ref = self.current_side, self.entry_price
        sl_pct = self.params['long_sl'] if side == "BUY" else self.params['short_sl']
        trig_pct = self.params['long_ttp_trig'] if side == "BUY" else self.params['short_ttp_trig']
        call_pct = self.params['long_ttp_call'] if side == "BUY" else self.params['short_ttp_call']

        # 1. 硬停損判定
        if (side == "BUY" and curr_price <= ref * (1 - sl_pct/100)) or \
           (side == "SELL" and curr_price >= ref * (1 + sl_pct/100)):
            self.safe_emit_log(f"🚨 【硬停損觸發】價格:{curr_price:.2f}")
            self.close_position(); return

        # 2. 移動停利邏輯 (TTP)
        if side == "BUY":
            if curr_price > self.extreme_price:
                self.extreme_price = curr_price
                if self.ttp_active: self.sl_price = self.extreme_price * (1 - call_pct/100)
            if not self.ttp_active and curr_price >= ref * (1 + trig_pct/100):
                self.ttp_active = True
                self.safe_emit_log("🔥 【多單移停啟動】")
            if self.ttp_active and curr_price <= self.sl_price:
                self.safe_emit_log(f"💰 【移停獲利】價格:{curr_price:.2f}"); self.close_position()
        else: # 做空
            if curr_price < self.extreme_price or self.extreme_price == 0:
                self.extreme_price = curr_price
                if self.ttp_active: self.sl_price = self.extreme_price * (1 + call_pct/100)
            if not self.ttp_active and curr_price <= ref * (1 - trig_pct/100):
                self.ttp_active = True
                self.safe_emit_log("🔥 【空單移停啟動】")
            if self.ttp_active and curr_price >= self.sl_price:
                self.safe_emit_log(f"💰 【移停獲利】價格:{curr_price:.2f}"); self.close_position()

    def close_position(self):
        try:
            side_to_close = "SELL" if self.current_side == "BUY" else "BUY"
            self.client.futures_create_order(symbol=self.symbol, side=side_to_close, type='MARKET', quantity=self.position_qty, reduceOnly=True)
            self.clear_state()
            self.safe_emit_log("⏹️ 【策略已平倉】")
        except Exception as e:
            self.safe_emit_log(f"❌ 平倉失敗: {e}")

    def save_state(self):
        state = {"in_position": self.in_position, "current_side": self.current_side, "position_qty": self.position_qty, "entry_price": self.entry_price, "extreme_price": self.extreme_price, "ttp_active": self.ttp_active, "sl_price": self.sl_price}
        with open(self.state_file, "w") as f: json.dump(state, f)

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    d = json.load(f)
                    self.in_position = d.get("in_position", False)
                    self.current_side = d.get("current_side")
                    self.position_qty = d.get("position_qty", 0.0)
                    self.entry_price = d.get("entry_price", 0.0)
                    self.extreme_price = d.get("extreme_price", 0.0)
                    self.ttp_active = d.get("ttp_active", False)
                    self.sl_price = d.get("sl_price", 0.0)
            except: pass

    def clear_state(self):
        self.in_position = False
        self.current_side = None
        self.position_qty = 0.0
        self.save_state()

    def update_price(self, price):
        self.curr_price = price

    def stop(self):
        self.is_running = False
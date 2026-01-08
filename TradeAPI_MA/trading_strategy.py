import time, json, os, hashlib, threading
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from market_utils import get_ma_level, get_symbol_rules, round_step_size

STATE_FOLDER = "position_states"

class TradingWorker(QObject):
    price_update = Signal(float)
    log_update = Signal(str)
    finished = Signal()

    def __init__(self, client, params, symbol, strategy_name, wait_for_reset=False):
        super().__init__()
        self.client = client
        self.params = params
        self.symbol = symbol
        self.strategy_name = strategy_name 
        self.is_running = False
        self.curr_price = 0.0
        self.wait_for_reset = wait_for_reset
        
        api_str = getattr(client, 'API_KEY', 'unknown')
        api_hash = hashlib.md5(str(api_str).encode()).hexdigest()[:8]
        self.state_file = os.path.join(STATE_FOLDER, f"state_{api_hash}_{self.symbol}_{self.strategy_name}.json")
        
        self.in_position = False
        self.current_side = None
        self.position_qty = 0.0
        self.entry_price = 0.0
        self.extreme_price = 0.0
        self.ttp_active = False
        self.sl_price = 0.0
        self.next_rollover_ms = 0
        self.long_trigger = float('inf')
        self.short_trigger = 0.0

        # --- [新增] 與 BT 版本一致的統計變數 ---
        self.daily_trades = 0
        self.total_trades = 0
        self.last_trade_date = ""
        
        if not os.path.exists(STATE_FOLDER): os.makedirs(STATE_FOLDER)
        self.load_state()
        self.save_state()  # [新增] 啟動時立即產生檔案

    def check_global_clear(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return not json.load(f).get("in_position", False)
            except: return True
        return True

    def safe_emit_log(self, msg):
        try: self.log_update.emit(msg)
        except RuntimeError: pass

    def update_strategy_levels(self):
        """[MA專用] 計算觸發位 - 修正版"""
        # 1. 分別從參數中抓取多頭與空頭的 MA 天數，若抓不到才用預設值
        l_win = int(self.params.get('long_ma_window', 6))
        s_win = int(self.params.get('short_ma_window', 29))
    
        # 2. 分別獲取兩條均線的數值
        ma_long = get_ma_level(self.client, self.symbol, l_win)
        ma_short = get_ma_level(self.client, self.symbol, s_win)
    
        if ma_long:
            # 使用多頭緩衝計算進場位
            self.long_trigger = ma_long * (1 + self.params['long_buffer'] / 100)
    
        if ma_short:
            # 使用空頭緩衝計算進場位
            self.short_trigger = ma_short * (1 - self.params['short_buffer'] / 100)
        
        # 3. 更新日誌顯示，反映你介面上輸入的真實天數
        now_str = datetime.now().strftime("%H:%M:%S")
        self.safe_emit_log(f"⏰ MA更新 | 多({l_win}):{self.long_trigger:.4f} | 空({s_win}):{self.short_trigger:.4f}")

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                # --- [新增] 換日檢查邏輯 (與 BT 一致) ---
                today = datetime.now().strftime("%Y-%m-%d")
                if self.last_trade_date != today:
                    self.last_trade_date = today
                    self.daily_trades = 0
                    self.save_state()

                now_ms = int(time.time() * 1000)
                # [修改] 仿照 BT 版本，加入啟動時的系統通知
                if self.next_rollover_ms == 0:
                    klines = self.client.futures_klines(symbol=self.symbol, interval='1d', limit=1)
                    if klines:
                        self.update_strategy_levels()
                        self.next_rollover_ms = klines[0][6] + 1
                        # 加入這行來發送「策略已啟動」日誌
                        target_time = datetime.fromtimestamp(self.next_rollover_ms/1000).strftime('%Y-%m-%d %H:%M:%S')
                        self.safe_emit_log(f"🚀 [系統] 策略已啟動，目標換日時間: {target_time}")
                
                # 如果是換日輪詢觸發
                elif now_ms >= self.next_rollover_ms:
                    klines = self.client.futures_klines(symbol=self.symbol, interval='1d', limit=1)
                    if klines:
                        self.update_strategy_levels()
                        self.next_rollover_ms = klines[0][6] + 1
                        self.safe_emit_log(f"⏰ [系統] 偵測到換日成功，已重新計算策略邊界 ({self.symbol})")
                
                curr_price = self.curr_price
                if curr_price <= 0:
                    time.sleep(0.5); continue
                
                self.price_update.emit(curr_price)

                if not self.in_position:
                    # --- 進場邏輯修正：增加區間限制 ---
                    direction = self.params.get('direction', 'BOTH')
                    
                    # 容許範圍 (例如 0.5%，避免現價已經衝太高才進場)
                    # 您可以根據需求調整 0.005 這個數值
                    tolerance = 0.005 

                    # 做多判斷：現價要在【觸發位】與【觸發位+0.5%】之間才進場
                    if direction in ["BOTH", "LONG"] and (self.long_trigger <= curr_price <= self.long_trigger * (1 + tolerance)):
                        self.execute_entry(curr_price, "BUY")
                    
                    # 做空判斷：現價要在【觸發位】與【觸發位-0.5%】之間才進場
                    elif direction in ["BOTH", "SHORT"] and (self.short_trigger * (1 - tolerance) <= curr_price <= self.short_trigger):
                        self.execute_entry(curr_price, "SELL")
                else:
                    self.manage_position(curr_price)
                
                time.sleep(0.1)
            except Exception as e:
                self.safe_emit_log(f"系統異常: {e}"); time.sleep(2)

    def execute_entry(self, price, side):
        try:
            # 1. 獲取帳戶資訊
            acc_info = self.client.futures_account()
            # 2. 檢查舊有倉位接管邏輯
            existing_pos = next((p for p in acc_info['positions'] if p['symbol'] == self.symbol), None)
            if existing_pos and float(existing_pos['positionAmt']) != 0:
                current_amt = float(existing_pos['positionAmt'])
                # 檢查方向是否一致 (多單對正數，空單對負數)
                if (side == "BUY" and current_amt > 0) or (side == "SELL" and current_amt < 0):
                    self.safe_emit_log("⚠️ 偵測到已有倉位，自動接管。")
                    self.in_position = True
                    self.current_side = side
                    self.position_qty = abs(current_amt)
                    self.entry_price, self.extreme_price = price, price
                    sl_pct = self.params['long_sl'] if side == "BUY" else self.params['short_sl']
                    self.sl_price = price * (1 - sl_pct/100) if side == "BUY" else price * (1 + sl_pct/100)
                    self.save_state()
                    return # 直接結束，不下單
            # 3. 若無現有倉位，執行原有下單流程    
            rules = get_symbol_rules(self.client, self.symbol)
            if not rules: return
            
            if self.params['order_mode'] == "FIXED":
                qty = round_step_size(self.params['fixed_qty'], rules['stepSize'])
            else:
                acc = self.client.futures_account()
                bal = next(float(a['walletBalance']) for a in acc['assets'] if a['asset'] == 'USDT')
                qty = round_step_size((bal * (self.params['trade_pct'] / 100) * 20.0) / price, rules['stepSize'])
            
            self.client.futures_create_order(symbol=self.symbol, side=side, type='MARKET', quantity=qty)
            
            # --- [新增] 更新交易次數統計 ---
            self.daily_trades += 1
            self.total_trades += 1
            self.last_trade_date = datetime.now().strftime("%Y-%m-%d")

            self.in_position, self.current_side, self.position_qty = True, side, qty
            self.entry_price, self.extreme_price = price, price
            sl_pct = self.params['long_sl'] if side == "BUY" else self.params['short_sl']
            self.sl_price = price * (1 - sl_pct/100) if side == "BUY" else price * (1 + sl_pct/100)
            
            self.save_state()
            self.safe_emit_log(f"✅ 【{self.strategy_name} 進場】價格:{price:.2f}")
        except Exception as e:
            self.safe_emit_log(f"❌ {self.strategy_name} 進場失敗: {e}")

    def manage_position(self, curr_price):
        # ... (此部分與上一篇提供的 manage_position 邏輯相同) ...
        side, ref = self.current_side, self.entry_price
        sl_pct = self.params['long_sl'] if side == "BUY" else self.params['short_sl']
        trig_pct = self.params['long_ttp_trig'] if side == "BUY" else self.params['short_ttp_trig']
        call_pct = self.params['long_ttp_call'] if side == "BUY" else self.params['short_ttp_call']

        if (side == "BUY" and curr_price <= ref * (1 - sl_pct/100)) or \
           (side == "SELL" and curr_price >= ref * (1 + sl_pct/100)):
            self.close_position(); return

        if side == "BUY":
            if curr_price > self.extreme_price:
                self.extreme_price = curr_price
                if self.ttp_active: self.sl_price = self.extreme_price * (1 - call_pct/100)
            if not self.ttp_active and curr_price >= ref * (1 + trig_pct/100):
                self.ttp_active = True
            if self.ttp_active and curr_price <= self.sl_price:
                self.close_position()
        else:
            if curr_price < self.extreme_price or self.extreme_price == 0:
                self.extreme_price = curr_price
                if self.ttp_active: self.sl_price = self.extreme_price * (1 + call_pct/100)
            if not self.ttp_active and curr_price <= ref * (1 - trig_pct/100):
                self.ttp_active = True
            if self.ttp_active and curr_price >= self.sl_price:
                self.close_position()

    def close_position(self):
        try:
            side_to_close = "SELL" if self.current_side == "BUY" else "BUY"
            # 只平掉自己記錄的 position_qty，不影響其他策略
            self.client.futures_create_order(symbol=self.symbol, side=side_to_close, type='MARKET', quantity=self.position_qty, reduceOnly=True)
            self.clear_state()
            self.safe_emit_log(f"⏹️ 【{self.strategy_name} 平倉】")
        except Exception as e:
            self.safe_emit_log(f"❌ 平倉失敗: {e}")

    def save_state(self):
        # --- [修改] 加入統計變數至存檔 ---
        state = {
            "in_position": self.in_position, 
            "current_side": self.current_side, 
            "position_qty": self.position_qty, 
            "entry_price": self.entry_price, 
            "extreme_price": self.extreme_price, 
            "ttp_active": self.ttp_active, 
            "sl_price": self.sl_price,
            "daily_trades": self.daily_trades,
            "total_trades": self.total_trades,
            "last_trade_date": self.last_trade_date
        }
        with open(self.state_file, "w") as f: json.dump(state, f)

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    d = json.load(f)
                    # --- [新增] 讀取統計數據與換日判定 ---
                    self.daily_trades = d.get("daily_trades", 0)
                    self.total_trades = d.get("total_trades", 0)
                    self.last_trade_date = d.get("last_trade_date", "")
                    
                    today = datetime.now().strftime("%Y-%m-%d")
                    if self.last_trade_date != today:
                        self.daily_trades = 0
                        self.last_trade_date = today

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

    def update_price(self, price): self.curr_price = price
    def stop(self): self.is_running = False
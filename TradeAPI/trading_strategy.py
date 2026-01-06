import time
import json
import os
import hashlib
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from market_utils import get_breakout_levels, get_symbol_rules, round_step_size

STATE_FOLDER = "position_states"

class TradingWorker(QObject):
    price_update = Signal(float)
    log_update = Signal(str)
    finished = Signal()

    def __init__(self, client, params, symbol, wait_for_reset=False):
        super().__init__()
        self.client = client
        self.params = params
        self.symbol = symbol  # [修改] 接收外部傳入的 Symbol
        self.is_running = False
        
        if not os.path.exists(STATE_FOLDER):
            os.makedirs(STATE_FOLDER)
        
        # 使用 getattr 安全獲取 API KEY 雜湊
        api_str = getattr(client, 'api_key', 'unknown')
        api_hash = hashlib.md5(str(api_str).encode()).hexdigest()[:8]
        self.state_file = os.path.join(STATE_FOLDER, f"state_{api_hash}_{self.symbol}.json") # [修改] 檔名加入 Symbol 區分
        
        self.in_position = False
        self.current_side = None
        self.position_qty = 0.0
        self.entry_price = 0.0
        self.extreme_price = 0.0
        self.ttp_active = False
        self.sl_price = 0.0
        self.daily_trades = 0
        self.total_trades = 0
        self.last_trade_date = ""
        self.wait_for_reset = wait_for_reset 
        self.last_candle_open_time = 0
        self.long_trigger = float('inf')
        self.short_trigger = 0.0
        
        # [優化] 初始化時快取交易規則，避免下單時卡頓
        self.symbol_rules = None 
        self.last_kline_check = 0 # [優化] 限制 K 線檢查頻率
        
        self.load_state()
        self.init_rules()

    def init_rules(self):
        """[優化] 預先獲取並快取交易規則"""
        try:
            self.symbol_rules = get_symbol_rules(self.client, self.symbol)
            if self.symbol_rules:
                self.safe_emit_log(f"✅ 交易規則已快取: 最小數量 {self.symbol_rules['minQty']}")
            else:
                self.safe_emit_log("⚠️ 無法獲取交易規則，將於下單時重試")
        except Exception as e:
            self.safe_emit_log(f"⚠️ 初始化規則失敗: {e}")

    def safe_emit_log(self, msg):
        try:
            self.log_update.emit(msg)
        except RuntimeError:
            pass

    def save_state(self):
        try:
            state = {
                "in_position": self.in_position,
                "current_side": self.current_side,
                "position_qty": self.position_qty,
                "entry_price": self.entry_price,
                "extreme_price": self.extreme_price,
                "ttp_active": self.ttp_active,
                "daily_trades": self.daily_trades,
                "total_trades": self.total_trades,
                "last_trade_date": self.last_trade_date,
                "sl_price": self.sl_price
            }
            with open(self.state_file, "w") as f:
                json.dump(state, f)
        except Exception as e:
            self.safe_emit_log(f"狀態儲存失敗: {e}")

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    self.daily_trades = data.get("daily_trades", 0)
                    self.total_trades = data.get("total_trades", 0)
                    self.sl_price = data.get("sl_price", 0.0)
                    self.last_trade_date = data.get("last_trade_date", "")
                    
                    today = datetime.now().strftime("%Y-%m-%d")
                    if self.last_trade_date != today:
                        self.daily_trades = 0
                        self.last_trade_date = today
                    
                    if data.get("in_position"):
                        self.in_position = data['in_position']
                        self.current_side = data['current_side']
                        self.position_qty = data['position_qty']
                        self.entry_price = data['entry_price']
                        self.extreme_price = data['extreme_price']
                        self.ttp_active = data['ttp_active']
            except:
                pass

    def clear_state(self):
        self.in_position = False
        self.current_side = None
        self.position_qty = 0.0
        self.entry_price = 0.0
        self.extreme_price = 0.0
        self.ttp_active = False
        self.sl_price = 0.0
        self.save_state()
        self.safe_emit_log(">>> [系統] 持倉標記已重置")

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                if self.last_trade_date != today:
                    self.daily_trades = 0
                    self.last_trade_date = today
                    self.save_state()

                # [優化] 減少 K 線請求頻率，每 60 秒檢查一次即可
                now_ts = time.time()
                if now_ts - self.last_kline_check > 60:
                    klines = self.client.futures_klines(symbol=self.symbol, interval='1d', limit=1)
                    if klines and klines[0][0] > self.last_candle_open_time:
                        self.last_candle_open_time = klines[0][0]
                        self.update_breakout_levels()
                    self.last_kline_check = now_ts
                
                # 獲取價格
                ticker = self.client.futures_symbol_ticker(symbol=self.symbol)
                curr_price = float(ticker['price'])
                try:
                    self.price_update.emit(curr_price)
                except RuntimeError:
                    break
                
                if not self.in_position:
                    if self.wait_for_reset:
                        if self.check_global_clear():
                            self.wait_for_reset = False
                    
                    if not self.wait_for_reset:
                        direction = self.params.get('direction', 'BOTH')
                        # 0.01% 的極小容許範圍判斷進場
                        tolerance = 0.0001 
                        
                        can_long = direction in ["BOTH", "LONG"]
                        can_short = direction in ["BOTH", "SHORT"]
                        
                        if can_long and (self.long_trigger <= curr_price <= (self.long_trigger * (1 + tolerance))):
                            self.execute_entry(curr_price, "BUY")
                        elif can_short and ((self.short_trigger * (1 - tolerance)) <= curr_price <= self.short_trigger):
                            self.execute_entry(curr_price, "SELL")
                else:
                    self.manage_position(curr_price)
                
                for _ in range(10): # 1秒的 sleep 分割成 10 次，提高響應速度
                    if not self.is_running:
                        break
                    time.sleep(0.1)
            except Exception as e:
                self.safe_emit_log(f"循環異常: {e}")
                time.sleep(2)
        self.finished.emit()

    def check_global_clear(self):
        try:
            for f in os.listdir(STATE_FOLDER):
                if f.endswith(f"_{self.symbol}.json"): # 只檢查當前幣種
                    with open(os.path.join(STATE_FOLDER, f), "r") as j:
                        if json.load(j).get("in_position", False):
                            return False
            return True
        except:
            return False

    def update_breakout_levels(self):
        l, s = int(self.params['long_lookback']), int(self.params['short_lookback'])
        h, _ = get_breakout_levels(self.client, self.symbol, l)
        _, low = get_breakout_levels(self.client, self.symbol, s)
        if h and low:
            self.long_trigger = h * (1 + self.params['long_buffer'] / 100)
            self.short_trigger = low * (1 - self.params['short_buffer'] / 100)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.safe_emit_log(f"📅 [{now_str}] 每日換日更新 | 多單觸發: {self.long_trigger:.2f} | 空單觸發: {self.short_trigger:.2f}")

    def execute_entry(self, price, side, test_mode=False):
        try:
            acc_info = self.client.futures_account()
            
            # 非測試模式才檢查舊有倉位接管
            if not test_mode:
                existing_pos = next((p for p in acc_info['positions'] if p['symbol'] == self.symbol), None)
                if existing_pos and float(existing_pos['positionAmt']) != 0:
                    current_amt = float(existing_pos['positionAmt'])
                    if (side == "BUY" and current_amt > 0) or (side == "SELL" and current_amt < 0):
                        self.safe_emit_log("⚠️ 偵測到已有倉位，自動接管。")
                        self.in_position = True
                        self.current_side = side
                        self.position_qty = abs(current_amt)
                        ref = self.long_trigger if (side=="BUY" and self.long_trigger != float('inf')) else (self.short_trigger if (side=="SELL" and self.short_trigger != 0) else price)
                        self.entry_price = ref
                        self.extreme_price = price
                        sl_pct = self.params['long_sl'] if side == "BUY" else self.params['short_sl']
                        self.sl_price = ref * (1 - sl_pct/100) if side == "BUY" else ref * (1 + sl_pct/100)
                        self.save_state()
                        return

            # [優化] 使用快取的規則
            rules = self.symbol_rules
            if not rules:
                rules = get_symbol_rules(self.client, self.symbol)
            
            if not rules:
                 self.safe_emit_log(f"❌ 無法獲取交易規則，取消下單")
                 return

            if self.params['order_mode'] == "FIXED":
                qty = round_step_size(self.params['fixed_qty'], rules['stepSize'])
            else:
                bal = next(float(a['walletBalance']) for a in acc_info['assets'] if a['asset'] == 'USDT')
                qty = round_step_size((bal * (self.params['trade_pct'] / 100) * 20.0) / price, rules['stepSize'])
            
            # 下單
            self.client.futures_create_order(symbol=self.symbol, side=side, type='MARKET', quantity=qty)
            
            if test_mode:
                now_str = datetime.now().strftime("%H:%M:%S")
                self.safe_emit_log(f"🧪 【測試單成交】 {side} {qty} @ {price:.2f} (未寫入狀態)")
                return

            self.daily_trades += 1
            self.total_trades += 1
            self.last_trade_date = datetime.now().strftime("%Y-%m-%d")
            
            ref = self.long_trigger if (side=="BUY" and self.long_trigger != float('inf')) else (self.short_trigger if (side=="SELL" and self.short_trigger != 0) else price)
            sl_pct = self.params['long_sl'] if side == "BUY" else self.params['short_sl']
            self.sl_price = ref * (1 - sl_pct/100) if side == "BUY" else ref * (1 + sl_pct/100)
            
            self.in_position, self.current_side, self.position_qty = True, side, qty
            self.entry_price, self.extreme_price, self.ttp_active = ref, price, False
            self.save_state()
            self.safe_emit_log(f"✅ 【成功進場】停損位:{self.sl_price:.2f}")
        except Exception as e:
            self.safe_emit_log(f"❌ 進場失敗: {e}")

    def manage_position(self, curr_price):
        side, ref = self.current_side, self.entry_price
        sl_pct = self.params['long_sl'] if side == "BUY" else self.params['short_sl']
        trig_pct = self.params['long_ttp_trig'] if side == "BUY" else self.params['short_ttp_trig']
        call_pct = self.params['long_ttp_call'] if side == "BUY" else self.params['short_ttp_call']

        if (side == "BUY" and curr_price <= ref * (1 - sl_pct/100)) or (side == "SELL" and curr_price >= ref * (1 + sl_pct/100)):
            self.safe_emit_log(f"🚨 【硬停損觸發】現價 {curr_price:.2f}")
            self.close_position()
            return

        if side == "BUY":
            if curr_price > self.extreme_price:
                self.extreme_price = curr_price
                if self.ttp_active:
                    self.sl_price = self.extreme_price * (1 - call_pct/100)
                self.save_state()
            if not self.ttp_active and curr_price >= ref * (1 + trig_pct/100):
                self.ttp_active = True
                self.sl_price = self.extreme_price * (1 - call_pct/100)
                self.save_state()
                self.safe_emit_log(f"🔥 【移停啟動】開始追蹤！")
            if self.ttp_active and curr_price <= self.sl_price:
                self.safe_emit_log(f"💰 【移停獲利】出場: {curr_price:.2f}")
                self.close_position()
        else:
            if curr_price < self.extreme_price or self.extreme_price == 0:
                self.extreme_price = curr_price
                if self.ttp_active:
                    self.sl_price = self.extreme_price * (1 + call_pct/100)
                self.save_state()
            if not self.ttp_active and curr_price <= ref * (1 - trig_pct/100):
                self.ttp_active = True
                self.sl_price = self.extreme_price * (1 + call_pct/100)
                self.save_state()
                self.safe_emit_log(f"🔥 【移停啟動】開始追蹤！")
            if self.ttp_active and curr_price >= self.sl_price:
                self.safe_emit_log(f"💰 【移停獲利】出場: {curr_price:.2f}")
                self.close_position()

    def close_position(self):
        try:
            side_to_close = "SELL" if self.current_side == "BUY" else "BUY"
            self.client.futures_create_order(symbol=self.symbol, side=side_to_close, type='MARKET', quantity=self.position_qty, reduceOnly=True)
            self.clear_state()
            self.safe_emit_log("⏹️ 【策略已平倉】")
        except Exception as e:
            self.safe_emit_log(f"❌ 平倉失敗: {e}")

    def stop(self):
        self.is_running = False
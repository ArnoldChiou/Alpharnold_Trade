import sys
import os
import subprocess
import csv
import comtypes.client
import json
import time
from datetime import datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from crypto_utils import encrypt_text, decrypt_text
import config
from sk_utils import handle_code, sk
from request_futures_data import QuoteFetcher
from trading_strategy import TradingWorker

CREDENTIALS_FILE = "credentials.json"

# --- LoginDialog (維持不變) ---
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("群益 API 登入")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background: #222; color: white; font-size: 14px;")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.id_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        style = "QLineEdit { padding: 5px; border: 1px solid #555; background: #333; color: #0f0; }"
        self.id_input.setStyleSheet(style)
        self.pass_input.setStyleSheet(style)
        form.addRow("身分證字號:", self.id_input)
        form.addRow("API 密碼:", self.pass_input)
        layout.addLayout(form)
        self.remember_chk = QCheckBox("記住帳密 (加密儲存)")
        self.remember_chk.setChecked(True)
        self.remember_chk.setStyleSheet("color: #ccc;")
        layout.addWidget(self.remember_chk)
        btn_box = QHBoxLayout()
        self.login_btn = QPushButton("登入系統")
        self.login_btn.setStyleSheet("background: #27ae60; color: white; padding: 8px; font-weight: bold;")
        self.login_btn.clicked.connect(self.save_and_accept)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet("background: #c0392b; color: white; padding: 8px;")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.login_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)
        self.load_credentials()

    def load_credentials(self):
        if os.path.exists(CREDENTIALS_FILE):
            try:
                with open(CREDENTIALS_FILE, "r") as f:
                    data = json.load(f)
                    self.id_input.setText(decrypt_text(data.get("id", "")))
                    self.pass_input.setText(decrypt_text(data.get("pass", "")))
            except: pass

    def save_and_accept(self):
        uid = self.id_input.text().strip().upper()
        upass = self.pass_input.text().strip()
        if not uid or not upass:
            QMessageBox.warning(self, "錯誤", "請輸入完整的帳號密碼")
            return
        import config
        config.USER_ID = uid
        config.USER_PASS = upass
        if self.remember_chk.isChecked():
            data = {"id": encrypt_text(uid), "pass": encrypt_text(upass)}
            with open(CREDENTIALS_FILE, "w") as f: json.dump(data, f)
        self.accept()

# --- 新增: K線下載執行緒 (避免 UI 凍結) ---
class DownloadThread(QThread):
    finished_signal = Signal(bool, str) # success, message

    def __init__(self, s_dt, e_dt, symbol):
        super().__init__()
        self.s_dt = s_dt
        self.e_dt = e_dt
        self.symbol = symbol # 這裡會強制傳 TX00

    def run(self):
        script_path = os.path.join(os.path.dirname(__file__), "KLine_Fetch.py")
        try:
            # 呼叫外部程式下載
            subprocess.run(["python", script_path, self.s_dt, self.e_dt, self.symbol], check=True)
            self.finished_signal.emit(True, "下載完成")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

# --- 1. 橋接器 ---
class PriceBridge(QObject):
    price_signal = Signal(str, float) 
    account_signal = Signal(str)
    log_signal = Signal(str)
    server_ready = Signal()

# --- 2. Fetcher ---
class UIBridgedFetcher(QuoteFetcher):
    def __init__(self, bridge):
        import pythoncom
        pythoncom.CoInitialize()
        super().__init__()
        self.bridge = bridge

    def OnNotifyQuoteLONG(self, sMarketNo, nIndex):
        super().OnNotifyQuoteLONG(sMarketNo, nIndex)
        pSKStock = sk.SKSTOCKLONG()
        res = self.m_pSKQuote.SKQuoteLib_GetStockByIndexLONG(sMarketNo, nIndex, pSKStock)
        if isinstance(res, tuple): pSKStock = res[0]
        
        price = pSKStock.nClose / 100.0
        symbol = pSKStock.bstrStockNo.strip()
        if price > 0:
            self.bridge.price_signal.emit(symbol, price)

    def OnAccount(self, bstrLogInID, bstrAccountData):
        super().OnAccount(bstrLogInID, bstrAccountData)
        if bstrAccountData.startswith("TF"):
            data = bstrAccountData.split(',')
            account = data[1] + data[3]
            self.bridge.account_signal.emit(account)

    def OnConnection(self, nKind, nCode):
        super().OnConnection(nKind, nCode)
        if nKind == 3003:
            self.bridge.log_signal.emit("🚀 報價伺服器就緒 (3003)")
            self.bridge.server_ready.emit()
    
    # 重新連線功能
    def reconnect_quote(self):
        import config
        # 1. 重新登入 (因為被 KLine_Fetch 踢掉了)
        self.bridge.log_signal.emit("🔄 偵測到連線中斷，正在重新登入...")
        self.m_pSKCenter.SKCenterLib_Login(config.USER_ID, config.USER_PASS)
        # 2. 重新進入監控
        self.m_pSKQuote.SKQuoteLib_EnterMonitorLONG()
        # (成功連線後，會觸發 OnConnection 3003，介面會自動訂閱)

# --- 3. 執行緒 ---
class FetcherThread(QThread):
    def __init__(self, bridge):
        super().__init__()
        self.bridge = bridge
        self.fetcher = None

    def run(self):
        self.fetcher = UIBridgedFetcher(self.bridge)
        self.fetcher.start()

# --- 4. 主視窗 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capital MA Trader - 自動重連版")
        self.setMinimumSize(1100, 750)
        
        self.is_ready = False
        self.workers = {} 
        self.accounts_list = [] 
        self.last_auto_update = ""
        self.current_symbol = "TX00"
        
        # 暫存啟動資訊
        self.pending_account = None
        self.pending_row = None
        self.pending_params = None
        self.pending_trade_symbol = None
        
        self.init_ui()
        
        self.bridge = PriceBridge()
        self.bridge.price_signal.connect(self.on_price_update)
        self.bridge.account_signal.connect(self.on_account_found)
        self.bridge.log_signal.connect(self.append_log)
        self.bridge.server_ready.connect(self.on_server_ready)
        
        self.engine_thread = FetcherThread(self.bridge)
        self.engine_thread.start()
        self.append_log(">>> 系統啟動中...")

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_daily_update)
        self.update_timer.start(60000)

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)

        self.price_label = QLabel("等待報價...")
        self.price_label.setStyleSheet("font-size: 36px; color: #00ff00; background: #111; padding: 15px; border: 2px solid #333; font-weight: bold;")
        self.price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.price_label)

        mid_layout = QHBoxLayout()
        
        param_group = QGroupBox("設定")
        param_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #555; margin-top: 10px; }")
        form = QFormLayout(param_group)
        
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(["TX00 (大台)", "MTX00 (小台)", "TM0000 (微台)"])
        self.symbol_combo.setStyleSheet("background: #333; color: white; padding: 8px; font-size: 14px;")
        self.symbol_combo.currentTextChanged.connect(self.change_market_subscription)
        
        self.ma_in = QLineEdit("5")  
        self.qty_in = QLineEdit("1")
        self.buffer_in = QLineEdit("0.1")
        self.sl_in = QLineEdit("1.5")
        self.ttp_trig_in = QLineEdit("2.0")
        self.ttp_call_in = QLineEdit("0.5")
        
        form.addRow("交易商品:", self.symbol_combo)
        form.addRow("MA 週期 (日):", self.ma_in)
        form.addRow("下單口數 (Qty):", self.qty_in)
        form.addRow("進場緩衝 %:", self.buffer_in)
        form.addRow("固定停損 %:", self.sl_in)
        form.addRow("移停觸發 %:", self.ttp_trig_in)
        form.addRow("移停回撤 %:", self.ttp_call_in)
        
        self.update_kline_btn = QPushButton("手動下載 K 線 (TX00)")
        self.update_kline_btn.setStyleSheet("background-color: #2980b9; color: white; padding: 5px;")
        self.update_kline_btn.clicked.connect(self.manual_download)
        form.addRow(self.update_kline_btn)

        mid_layout.addWidget(param_group, 1)

        table_group = QGroupBox("帳戶監控")
        table_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #555; margin-top: 10px; }")
        tl = QVBoxLayout(table_group)
        
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(5)
        self.account_table.setHorizontalHeaderLabels(["期貨帳號", "商品", "狀態", "資訊", "操作"])
        self.account_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.account_table.setStyleSheet("QTableWidget { background: #1a1a1a; color: #eee; } QHeaderView::section { background: #333; color: white; }")
        tl.addWidget(self.account_table)
        
        mid_layout.addWidget(table_group, 2)
        layout.addLayout(mid_layout)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background: #000; color: #0f0; font-family: Consolas; border: 1px solid #555;")
        self.log_box.setFixedHeight(200)
        layout.addWidget(self.log_box)

    def update_subscriptions(self):
        if not self.is_ready: return
        active_symbols = set()
        for worker in self.workers.values():
            if worker: active_symbols.add(worker.symbol)
        
        current_selection = self.symbol_combo.currentText().split(' ')[0]
        self.current_symbol = current_selection
        active_symbols.add(current_selection)

        target_str = ",".join(active_symbols)
        self.append_log(f"🔄 訂閱更新: [{target_str}]")
        self.price_label.setText(f"{self.current_symbol} 連線中...")
        
        if self.engine_thread and self.engine_thread.fetcher:
            self.engine_thread.fetcher.subscribe_market_data(target_str)

    def change_market_subscription(self, text):
        self.update_subscriptions()

    def on_price_update(self, symbol, price):
        if symbol == self.current_symbol:
            self.price_label.setText(f"{symbol}: {price:,.0f}")
        
        for acc, worker in self.workers.items():
            if worker and worker.symbol == symbol:
                worker.process_quote(price)

    def on_account_found(self, account):
        if account in self.accounts_list: return
        self.accounts_list.append(account)
        self.workers[account] = None
        
        row = self.account_table.rowCount()
        self.account_table.insertRow(row)
        self.account_table.setItem(row, 0, QTableWidgetItem(account))
        self.account_table.setItem(row, 1, QTableWidgetItem("-")) 
        
        status_item = QTableWidgetItem("待機中")
        status_item.setForeground(QColor("#aaaaaa"))
        self.account_table.setItem(row, 2, status_item)
        self.account_table.setItem(row, 3, QTableWidgetItem("---"))
        
        btn = QPushButton("啟動")
        btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn.clicked.connect(lambda checked=False, acc=account, r=row: self.toggle_account_strategy(acc, r))
        self.account_table.setCellWidget(row, 4, btn)
        self.append_log(f"✅ 發現帳號: {account}")

    def toggle_account_strategy(self, account, row):
        # 注意：這裡不檢查 is_ready，因為我們允許斷線重連
        btn = self.account_table.cellWidget(row, 4)
        
        if self.workers[account] is None:
            # --- 啟動流程 ---
            try:
                params = {
                    'ma': int(self.ma_in.text()), 
                    'qty': int(self.qty_in.text()),
                    'buffer': float(self.buffer_in.text()), 
                    'sl': float(self.sl_in.text()),
                    'ttp_trig': float(self.ttp_trig_in.text()), 
                    'ttp_call': float(self.ttp_call_in.text()),
                    'account': account
                }
            except ValueError:
                QMessageBox.critical(self, "錯誤", "參數格式有誤")
                return

            self.pending_account = account
            self.pending_row = row
            self.pending_params = params
            self.pending_trade_symbol = self.current_symbol # 使用當前選單的商品作為交易目標
            
            # 強制下載 TX00 (大台)
            kline_target = "TX00"
            s_dt, e_dt = self.get_kline_date_range()
            
            self.append_log(f"📥 啟動下載程序 ({kline_target})...")
            btn.setText("下載中...")
            btn.setEnabled(False)
            
            # 使用 QThread 執行外部程式，避免 UI 卡死
            self.dl_thread = DownloadThread(s_dt, e_dt, kline_target)
            self.dl_thread.finished_signal.connect(self.on_download_finished)
            self.dl_thread.start()

        else:
            # --- 停止流程 ---
            self.workers[account] = None
            btn.setText("啟動")
            btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
            self.account_table.item(row, 2).setText("已停止")
            self.account_table.item(row, 2).setForeground(QColor("#aaaaaa"))
            self.account_table.item(row, 3).setText("---")
            self.append_log(f"⏹️ 帳號 {account} 策略已停止")
            self.update_subscriptions()

    def on_download_finished(self, success, msg):
        if not success:
            self.append_log(f"❌ 下載失敗: {msg}")
            # 恢復按鈕
            if self.pending_row is not None:
                btn = self.account_table.cellWidget(self.pending_row, 4)
                btn.setText("啟動")
                btn.setEnabled(True)
            return
        
        self.append_log("✅ K 線下載完成，正在恢復連線...")
        
        # [關鍵步驟] 執行重新連線 (因為剛剛 subprocess 登入把我們踢掉了)
        if self.engine_thread and self.engine_thread.fetcher:
            self.engine_thread.fetcher.reconnect_quote()
            
        # 讀取 CSV (這裡讀取 TX00)
        prices = self.read_csv_prices("TX00")
        if not prices:
             self.append_log("❌ 讀取 CSV 失敗")
             return

        # 啟動 Worker
        self.finalize_start_worker(prices)

    def read_csv_prices(self, symbol):
        csv_path = f"history_kline.csv"
        if not os.path.exists(csv_path): return None
        prices = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 5: prices.append(float(row[4]))
            return prices
        except: return None

    def finalize_start_worker(self, prices):
        account = self.pending_account
        row = self.pending_row
        params = self.pending_params
        trade_symbol = self.pending_trade_symbol
        
        order_obj = self.engine_thread.fetcher.m_pSKOrder
        worker = TradingWorker(order_obj, params, trade_symbol)
        
        worker.log_signal.connect(lambda msg, acc=account: self.append_log(f"【{acc}】{msg}"))
        worker.status_signal.connect(lambda info, r=row: self.update_table_status(r, info))
        
        worker.reload_history(prices)
        self.workers[account] = worker
        
        btn = self.account_table.cellWidget(row, 4)
        btn.setText("停止")
        btn.setEnabled(True)
        btn.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
        
        self.account_table.item(row, 1).setText(trade_symbol)
        self.account_table.item(row, 2).setText("監控中")
        self.account_table.item(row, 2).setForeground(QColor("#00ff00"))
        
        self.append_log(f"▶️ 帳號 {account} 策略啟動 (目標:{trade_symbol})")

    def on_server_ready(self):
        # 3003 訊號回來了，代表重連成功，重新訂閱
        self.is_ready = True
        self.append_log(">>> 連線已恢復，重新訂閱行情...")
        self.update_subscriptions()

    def update_table_status(self, row, info_text):
        self.account_table.item(row, 3).setText(info_text)

    def manual_download(self):
        s_dt, e_dt = self.get_kline_date_range()
        self.append_log("📥 手動下載 TX00 中...")
        self.dl_thread = DownloadThread(s_dt, e_dt, "TX00")
        self.dl_thread.finished_signal.connect(lambda s, m: self.append_log(f"下載結果: {m} (請等待自動重連)"))
        self.dl_thread.finished_signal.connect(lambda: self.engine_thread.fetcher.reconnect_quote())
        self.dl_thread.start()

    def get_kline_date_range(self):
        now = datetime.now()
        if now.hour >= 15:
            e_dt = now.strftime("%Y%m%d")
        else:
            e_dt = (now - timedelta(days=1)).strftime("%Y%m%d")
        s_dt = (now - timedelta(days=80)).strftime("%Y%m%d")
        return s_dt, e_dt

    def check_daily_update(self):
        now = datetime.now()
        if now.hour == 15 and 0 <= now.minute <= 10:
            today_str = now.strftime("%Y%m%d")
            if self.last_auto_update != today_str:
                self.append_log(f"⏰ 執行換日下載...")
                # 這裡也要用 Thread 下載，不然會卡 UI
                s_dt, e_dt = self.get_kline_date_range()
                self.dl_thread = DownloadThread(s_dt, e_dt, "TX00")
                self.dl_thread.finished_signal.connect(self.daily_reload_finished)
                self.dl_thread.start()
                self.last_auto_update = today_str
    
    def daily_reload_finished(self):
        self.engine_thread.fetcher.reconnect_quote()
        prices = self.read_csv_prices("TX00")
        if prices:
            for w in self.workers.values():
                if w: w.reload_history(prices)
            self.append_log("✅ 換日資料更新完畢")

    def append_log(self, msg):
        self.log_box.append(msg)
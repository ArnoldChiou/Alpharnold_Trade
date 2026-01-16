import sys
import os
import subprocess
import csv
import comtypes.client
from datetime import datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import config
from sk_utils import handle_code, sk
from request_futures_data import QuoteFetcher
from trading_strategy import TradingWorker
from crypto_utils import encrypt_text, decrypt_text
import json

CREDENTIALS_FILE = "credentials.json"
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("群益 API 登入")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background: #222; color: white; font-size: 14px;")
        
        layout = QVBoxLayout(self)
        
        # 輸入區
        form = QFormLayout()
        self.id_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        
        # 樣式
        style = "QLineEdit { padding: 5px; border: 1px solid #555; background: #333; color: #0f0; }"
        self.id_input.setStyleSheet(style)
        self.pass_input.setStyleSheet(style)
        
        form.addRow("身分證字號:", self.id_input)
        form.addRow("API 密碼:", self.pass_input)
        layout.addLayout(form)
        
        # 選項
        self.remember_chk = QCheckBox("記住帳密 (加密儲存)")
        self.remember_chk.setChecked(True)
        self.remember_chk.setStyleSheet("color: #ccc;")
        layout.addWidget(self.remember_chk)
        
        # 按鈕
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
            
        # 寫入 Config (這是關鍵，讓後面的程式讀得到)
        import config
        config.USER_ID = uid
        config.USER_PASS = upass
        
        # 加密儲存
        if self.remember_chk.isChecked():
            data = {
                "id": encrypt_text(uid),
                "pass": encrypt_text(upass)
            }
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(data, f)
                
        self.accept()

# 1. 橋接器
class PriceBridge(QObject):
    price_signal = Signal(float)
    account_signal = Signal(str)
    log_signal = Signal(str)

# 2. Fetcher (維持原樣)
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
        if price > 0:
            self.bridge.price_signal.emit(price)

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

# 3. 執行緒 (維持原樣)
class FetcherThread(QThread):
    def __init__(self, bridge):
        super().__init__()
        self.bridge = bridge
        self.fetcher = None

    def run(self):
        self.fetcher = UIBridgedFetcher(self.bridge)
        self.fetcher.start()

# 4. 主視窗 (大幅修改以支援多帳戶)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capital MA Trader - 群益多帳戶下單系統")
        self.setMinimumSize(1000, 700)
        
        self.is_ready = False
        
        # 帳戶管理容器
        # key: account_id (str), value: TradingWorker (obj) or None
        self.workers = {} 
        self.accounts_list = [] # 儲存發現的帳號字串
        
        # 紀錄上次自動更新的日期字串
        self.last_auto_update = ""

        self.init_ui()
        
        # --- 啟動橋接引擎 ---
        self.bridge = PriceBridge()
        self.bridge.price_signal.connect(self.on_price_update)
        self.bridge.account_signal.connect(self.on_account_found) # 改名為 on_account_found
        self.bridge.log_signal.connect(self.append_log)
        
        self.engine_thread = FetcherThread(self.bridge)
        self.engine_thread.start()
        self.append_log(">>> 報價引擎啟動中...")

        # --- 定時器 ---
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_daily_update)
        self.update_timer.start(60000)

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)

        # 頂部：報價顯示
        self.price_label = QLabel("等待報價...")
        self.price_label.setStyleSheet("font-size: 28px; color: #00ff00; background: #111; padding: 10px; border: 2px solid #333; font-weight: bold;")
        self.price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.price_label)

        # 中間：左右分割 (左邊參數，右邊表格)
        mid_layout = QHBoxLayout()
        
        # --- 左側：策略參數 ---
        param_group = QGroupBox("全域策略參數 (Global Strategy)")
        param_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #555; margin-top: 10px; }")
        form = QFormLayout(param_group)
        
        self.ma_in = QLineEdit("5")  
        self.qty_in = QLineEdit("1")
        self.buffer_in = QLineEdit("0.1")
        self.sl_in = QLineEdit("1.5")
        self.ttp_trig_in = QLineEdit("2.0")
        self.ttp_call_in = QLineEdit("0.5")
        
        form.addRow("MA 週期 (日):", self.ma_in)
        form.addRow("下單口數 (Qty):", self.qty_in)
        form.addRow("進場緩衝 %:", self.buffer_in)
        form.addRow("固定停損 %:", self.sl_in)
        form.addRow("移停觸發 %:", self.ttp_trig_in)
        form.addRow("移停回撤 %:", self.ttp_call_in)
        
        self.update_kline_btn = QPushButton("手動更新 K 線數據")
        self.update_kline_btn.setStyleSheet("background-color: #2980b9; color: white; padding: 5px;")
        self.update_kline_btn.clicked.connect(self.fetch_and_load_prices)
        form.addRow(self.update_kline_btn)

        mid_layout.addWidget(param_group, 1)

        # --- 右側：帳戶列表 ---
        table_group = QGroupBox("帳戶監控面板 (Account Control)")
        table_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #555; margin-top: 10px; }")
        tl = QVBoxLayout(table_group)
        
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(4)
        self.account_table.setHorizontalHeaderLabels(["期貨帳號", "狀態", "倉位資訊", "操作"])
        self.account_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.account_table.setStyleSheet("QTableWidget { background: #1a1a1a; color: #eee; } QHeaderView::section { background: #333; color: white; }")
        tl.addWidget(self.account_table)
        
        mid_layout.addWidget(table_group, 2)
        layout.addLayout(mid_layout)

        # 底部：Log
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background: #000; color: #0f0; font-family: Consolas; border: 1px solid #555;")
        self.log_box.setFixedHeight(200)
        layout.addWidget(self.log_box)

    def on_price_update(self, price):
        self.is_ready = True
        self.price_label.setText(f"TX00 成交: {price:,.2f}")
        
        # 遍歷所有活躍的 Worker 進行報價更新
        for acc, worker in self.workers.items():
            if worker:
                worker.process_quote(price)

    def on_account_found(self, account):
        """ 當 API 回傳帳號時，動態加入表格 """
        if account in self.accounts_list:
            return # 已存在
            
        self.accounts_list.append(account)
        self.workers[account] = None # 初始化
        
        row = self.account_table.rowCount()
        self.account_table.insertRow(row)
        
        # 1. 帳號
        self.account_table.setItem(row, 0, QTableWidgetItem(account))
        
        # 2. 狀態
        status_item = QTableWidgetItem("待機中")
        status_item.setForeground(QColor("#aaaaaa"))
        self.account_table.setItem(row, 1, status_item)
        
        # 3. 倉位
        self.account_table.setItem(row, 2, QTableWidgetItem("---"))
        
        # 4. 按鈕
        btn = QPushButton("啟動")
        btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn.clicked.connect(lambda checked=False, acc=account, r=row: self.toggle_account_strategy(acc, r))
        self.account_table.setCellWidget(row, 3, btn)
        
        self.append_log(f"✅ 發現帳號: {account}")

    def toggle_account_strategy(self, account, row):
        """ 針對單一帳號的啟動/停止邏輯 """
        if not self.is_ready:
            QMessageBox.warning(self, "警告", "報價尚未就緒，無法啟動")
            return

        btn = self.account_table.cellWidget(row, 3)
        
        if self.workers[account] is None:
            # --- 啟動流程 ---
            # 1. 確保有 K 線資料
            prices = self.fetch_and_load_prices()
            if not prices: return

            # 2. 準備參數
            try:
                params = {
                    'ma': int(self.ma_in.text()), 
                    'qty': int(self.qty_in.text()),
                    'buffer': float(self.buffer_in.text()), 
                    'sl': float(self.sl_in.text()),
                    'ttp_trig': float(self.ttp_trig_in.text()), 
                    'ttp_call': float(self.ttp_call_in.text()),
                    'account': account # 關鍵：綁定該帳號
                }
            except ValueError:
                QMessageBox.critical(self, "錯誤", "參數輸入格式有誤")
                return

            # 3. 建立 Worker
            order_obj = self.engine_thread.fetcher.m_pSKOrder
            worker = TradingWorker(order_obj, params, "TX00")
            
            # 連接訊號
            worker.log_signal.connect(lambda msg, acc=account: self.append_log(f"【{acc}】{msg}"))
            worker.status_signal.connect(lambda info, r=row: self.update_table_status(r, info))
            
            # 注入歷史數據 & 啟動
            worker.reload_history(prices)
            self.workers[account] = worker
            
            # 更新 UI
            btn.setText("停止")
            btn.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
            self.account_table.item(row, 1).setText("監控中")
            self.account_table.item(row, 1).setForeground(QColor("#00ff00"))
            self.append_log(f"▶️ 帳號 {account} 策略已啟動")
            
        else:
            # --- 停止流程 ---
            self.workers[account] = None
            btn.setText("啟動")
            btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
            self.account_table.item(row, 1).setText("已停止")
            self.account_table.item(row, 1).setForeground(QColor("#aaaaaa"))
            self.account_table.item(row, 2).setText("---")
            self.append_log(f"⏹️ 帳號 {account} 策略已停止")

    def update_table_status(self, row, info_text):
        """ 接收 Worker 回傳的倉位狀態文字 (例如: 多單@18000) """
        self.account_table.item(row, 2).setText(info_text)

    # --- 核心邏輯：K 線下載與更新 (保持原樣) ---
    def get_kline_date_range(self):
        now = datetime.now()
        if now.hour >= 15:
            e_dt = now.strftime("%Y%m%d")
        else:
            e_dt = (now - timedelta(days=1)).strftime("%Y%m%d")
        s_dt = (now - timedelta(days=80)).strftime("%Y%m%d")
        return s_dt, e_dt

    def fetch_and_load_prices(self):
        # 為了避免頻繁下載，可以加個簡單的快取判斷，或維持每次啟動下載
        s_dt, e_dt = self.get_kline_date_range()
        script_path = os.path.join(os.path.dirname(__file__), "KLine_Fetch.py")
        
        try:
            subprocess.run(["python", script_path, s_dt, e_dt], check=True)
        except Exception as e:
            self.append_log(f"❌ K線下載失敗: {e}")
            return None

        csv_path = "history_kline.csv"
        if not os.path.exists(csv_path): return None

        prices = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 5: prices.append(float(row[4]))
            self.append_log(f"📊 K線數據已更新 ({len(prices)} 筆)")
            return prices
        except: return None

    def check_daily_update(self):
        now = datetime.now()
        if now.hour == 15 and 0 <= now.minute <= 10:
            today_str = now.strftime("%Y%m%d")
            if self.last_auto_update != today_str:
                self.append_log(f"⏰ 執行全帳戶換日更新...")
                prices = self.fetch_and_load_prices()
                if prices:
                    for acc, worker in self.workers.items():
                        if worker:
                            worker.reload_history(prices)
                            self.append_log(f" -> 帳號 {acc} 數據更新完畢")
                self.last_auto_update = today_str

    def append_log(self, msg):
        self.log_box.append(msg)
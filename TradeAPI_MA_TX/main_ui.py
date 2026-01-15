import sys
import os
import subprocess
import csv
import comtypes.client
from datetime import datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import config
from sk_utils import handle_code, sk
from request_futures_data import QuoteFetcher
from trading_strategy import TradingWorker

# 1. 橋接器
class PriceBridge(QObject):
    price_signal = Signal(float)
    account_signal = Signal(str)
    log_signal = Signal(str)

# 2. Fetcher
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

# 3. 執行緒
class FetcherThread(QThread):
    def __init__(self, bridge):
        super().__init__()
        self.bridge = bridge
        self.fetcher = None

    def run(self):
        self.fetcher = UIBridgedFetcher(self.bridge)
        self.fetcher.start()

# 4. 主視窗
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capital MA Trader - 群益下單機 Pro")
        self.setMinimumSize(800, 650)
        
        self.target_account = ""
        self.is_ready = False
        self.worker = None 
        
        # 紀錄上次自動更新的日期字串 (例如 "20250115")
        self.last_auto_update = ""

        self.init_ui()
        
        # --- 啟動橋接引擎 ---
        self.bridge = PriceBridge()
        self.bridge.price_signal.connect(self.on_price_update)
        self.bridge.account_signal.connect(self.on_account_ready)
        self.bridge.log_signal.connect(self.append_log)
        
        self.engine_thread = FetcherThread(self.bridge)
        self.engine_thread.start()
        self.append_log(">>> 報價引擎啟動中...")

        # --- 新增：定時器 (每分鐘檢查一次時間) ---
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_daily_update)
        self.update_timer.start(60000) # 60秒觸發一次

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)

        self.price_label = QLabel("等待報價...")
        self.price_label.setStyleSheet("font-size: 32px; color: #00ff00; background: #111; padding: 10px; border: 2px solid #333;")
        self.price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.price_label)

        form = QFormLayout()
        self.ma_in = QLineEdit("5")  
        self.qty_in = QLineEdit("1")
        self.buffer_in = QLineEdit("0.1")
        self.sl_in = QLineEdit("1.5")
        self.ttp_trig_in = QLineEdit("2.0")
        self.ttp_call_in = QLineEdit("0.5")
        layout.addLayout(form)
        form.addRow("MA 週期 (日):", self.ma_in)
        form.addRow("下單口數:", self.qty_in)
        form.addRow("進場緩衝 %:", self.buffer_in)
        form.addRow("固定停損 %:", self.sl_in)
        form.addRow("移停觸發 %:", self.ttp_trig_in)
        form.addRow("移停回撤 %:", self.ttp_call_in)

        self.start_btn = QPushButton("啟動策略")
        self.start_btn.setFixedHeight(50)
        self.start_btn.setStyleSheet("font-weight: bold; background-color: #27ae60; color: white;")
        self.start_btn.clicked.connect(self.toggle_strategy)
        layout.addWidget(self.start_btn)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background: #000; color: #0f0; font-family: Consolas;")
        layout.addWidget(self.log_box)

    def on_price_update(self, price):
        self.is_ready = True
        self.price_label.setText(f"TX00 成交: {price:,.2f}")
        if self.worker:
            self.worker.process_quote(price)

    def on_account_ready(self, account):
        self.target_account = account
        self.append_log(f"✅ 帳號確認: {self.target_account}")

    # --- 核心邏輯：判斷日期範圍 ---
    def get_kline_date_range(self):
        """ 判斷目前時間，決定要抓取到哪一天的 K 線 """
        now = datetime.now()
        # 如果超過 15:00，代表日盤結束，算下一交易日，所以要抓到「今天」
        if now.hour >= 15:
            e_dt = now.strftime("%Y%m%d")
        else:
            # 如果還沒 15:00，今天的 K 線還沒收完，只能抓到「昨天」
            e_dt = (now - timedelta(days=1)).strftime("%Y%m%d")
            
        # 起始日抓 80 天前，確保 MA 夠用
        s_dt = (now - timedelta(days=80)).strftime("%Y%m%d")
        return s_dt, e_dt

    # --- 核心邏輯：呼叫外部程式並讀取 CSV ---
    def fetch_and_load_prices(self):
        """ 執行下載並回傳價格列表 """
        s_dt, e_dt = self.get_kline_date_range()
        self.append_log(f"📥 開始下載 K 線資料 ({s_dt} ~ {e_dt})...")
        
        script_path = os.path.join(os.path.dirname(__file__), "KLine_Fetch.py")
        
        try:
            # 呼叫 subprocess (會暫時卡住 UI 幾秒鐘)
            subprocess.run(["python", script_path, s_dt, e_dt], check=True)
        except Exception as e:
            self.append_log(f"❌ 下載失敗: {e}")
            return None

        # 讀取 CSV
        csv_path = "history_kline.csv"
        if not os.path.exists(csv_path):
            self.append_log("❌ 找不到 CSV 檔案")
            return None

        prices = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None) # 跳過標頭
                for row in reader:
                    if len(row) >= 5:
                        prices.append(float(row[4]))
            self.append_log(f"✅ 讀取完成，共 {len(prices)} 筆歷史收盤價")
            return prices
        except Exception as e:
            self.append_log(f"❌ CSV 解析失敗: {e}")
            return None

    # --- 自動排程檢查 ---
    def check_daily_update(self):
        """ 定時檢查是否需要換日更新 """
        now = datetime.now()
        
        # 條件：下午 3 點過後，且今天還沒更新過
        # (這裡設 15:00 ~ 15:10 之間觸發，避免重複執行)
        if now.hour == 15 and 0 <= now.minute <= 10:
            today_str = now.strftime("%Y%m%d")
            
            if self.last_auto_update != today_str:
                self.append_log(f"⏰ 檢測到時間已過 15:00，執行換日更新...")
                self.perform_hot_update()
                self.last_auto_update = today_str

    def perform_hot_update(self):
        """ 熱更新：不停止策略，只更新 MA 數據 """
        if not self.worker:
            self.append_log("⚠️ 策略未啟動，跳過更新")
            return

        prices = self.fetch_and_load_prices()
        if prices:
            # 呼叫 Worker 的新方法，更新內部數據
            self.worker.reload_history(prices)
            self.append_log("✅ 換日數據更新完畢，策略繼續執行 (夜盤模式)")

    def toggle_strategy(self):
        if not self.is_ready:
            self.append_log("⚠️ 報價尚未就緒")
            return
            
        if self.start_btn.text() == "啟動策略":
            # 1. 取得歷史資料
            prices = self.fetch_and_load_prices()
            if not prices:
                return # 下載失敗就中止

            # 2. 初始化 Worker
            params = {
                'ma': int(self.ma_in.text()), 
                'qty': int(self.qty_in.text()),
                'buffer': float(self.buffer_in.text()), 
                'sl': float(self.sl_in.text()),
                'ttp_trig': float(self.ttp_trig_in.text()), 
                'ttp_call': float(self.ttp_call_in.text()),
                'account': self.target_account
            }
            order_obj = self.engine_thread.fetcher.m_pSKOrder
            self.worker = TradingWorker(order_obj, params, "TX00")
            self.worker.log_signal.connect(self.append_log)

            # 3. 注入資料 (這裡直接用新寫的 reload 方法也可以)
            self.worker.reload_history(prices)

            self.start_btn.setText("停止策略")
            self.start_btn.setStyleSheet("background-color: #c0392b; color: white;")
            self.append_log(f"▶️ 策略啟動！監控中...")

        else:
            self.worker = None
            self.start_btn.setText("啟動策略")
            self.start_btn.setStyleSheet("background-color: #27ae60; color: white;")
            self.append_log("⏹️ 策略已停止")

    def append_log(self, msg):
        self.log_box.append(msg)
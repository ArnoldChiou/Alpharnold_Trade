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

# 1. 橋接器：只保留報價、帳號與 Log 相關訊號
class PriceBridge(QObject):
    price_signal = Signal(float)
    account_signal = Signal(str)
    log_signal = Signal(str)
    # 這裡已經移除了 kline_data_signal 與 request_kline_command

# 2. Fetcher：只專注於即時報價與連線狀態
class UIBridgedFetcher(QuoteFetcher):
    def __init__(self, bridge):
        import pythoncom
        pythoncom.CoInitialize() # 確保 COM 在此執行緒可用
        super().__init__()
        self.bridge = bridge
        # 修正：移除舊的 request_kline_command 連接
        # self.bridge.request_kline_command.connect(self.request_kline) <-- 這行刪除

    # 複寫報價事件：轉發給 UI
    def OnNotifyQuoteLONG(self, sMarketNo, nIndex):
        # 執行原本 request_futures_data.py 的邏輯 (print)
        super().OnNotifyQuoteLONG(sMarketNo, nIndex)
        
        # 額外發送訊號給 UI
        pSKStock = sk.SKSTOCKLONG()
        res = self.m_pSKQuote.SKQuoteLib_GetStockByIndexLONG(sMarketNo, nIndex, pSKStock)
        if isinstance(res, tuple): pSKStock = res[0]
        
        price = pSKStock.nClose / 100.0
        if price > 0:
            self.bridge.price_signal.emit(price)

    # 複寫帳號事件：轉發給 UI
    def OnAccount(self, bstrLogInID, bstrAccountData):
        super().OnAccount(bstrLogInID, bstrAccountData)
        if bstrAccountData.startswith("TF"):
            data = bstrAccountData.split(',')
            # 格式範例: TF,9876543,10,Y,TWD,...
            # 組合出分公司碼+帳號 (例如 9876543)
            account = data[1] + data[3]
            self.bridge.account_signal.emit(account)

    # 複寫連線事件：更新 Log
    def OnConnection(self, nKind, nCode):
        super().OnConnection(nKind, nCode)
        if nKind == 3003:
            self.bridge.log_signal.emit("🚀 報價伺服器就緒 (3003)")

    # 移除：request_kline 方法 (已移至外部程式 KLine_Fetch.py)
    # 移除：OnNotifyKLineData 方法 (已移至外部程式 KLine_Fetch.py)

# 3. 執行緒：負責跑 QuoteFetcher 的 Event Loop
class FetcherThread(QThread):
    def __init__(self, bridge):
        super().__init__()
        self.bridge = bridge
        self.fetcher = None

    def run(self):
        # 初始化 Fetcher
        self.fetcher = UIBridgedFetcher(self.bridge)
        # 啟動 (這會進入 while 迴圈或 mainloop，視 request_futures_data 實作而定)
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
        
        self.init_ui()
        
        # --- 啟動橋接引擎 ---
        self.bridge = PriceBridge()
        self.bridge.price_signal.connect(self.on_price_update)
        self.bridge.account_signal.connect(self.on_account_ready)
        self.bridge.log_signal.connect(self.append_log)
        
        self.engine_thread = FetcherThread(self.bridge)
        self.engine_thread.start()
        self.append_log(">>> 報價引擎啟動中...")

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)

        self.price_label = QLabel("等待報價...")
        self.price_label.setStyleSheet("font-size: 32px; color: #00ff00; background: #111; padding: 10px; border: 2px solid #333;")
        self.price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.price_label)

        form = QFormLayout()
        self.ma_in = QLineEdit("5")  # 預設 5 日線
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

    def toggle_strategy(self):
        if not self.is_ready:
            self.append_log("⚠️ 報價尚未就緒，請等待左上角出現價格")
            return
            
        if self.start_btn.text() == "啟動策略":
            # 1. 準備日期參數
            ma_days = int(self.ma_in.text())
            today = datetime.now()
            # 抓取比 MA 天數多一點的資料，確保足夠計算
            fetch_days = ma_days + 60 
            s_dt = (today - timedelta(days=fetch_days)).strftime("%Y%m%d")
            e_dt = (today - timedelta(days=1)).strftime("%Y%m%d")

            # 2. 呼叫外部程式下載 K 線
            self.append_log(f"📥 啟動外部程式下載 K 線 ({s_dt} ~ {e_dt})...")
            
            # 取得 KLine_Fetch.py 的絕對路徑
            script_path = os.path.join(os.path.dirname(__file__), "KLine_Fetch.py")
            
            try:
                # 呼叫 subprocess 並等待完成
                # 注意：這裡會暫時卡住 UI 直到下載完成，這是正常的
                subprocess.run(["python", script_path, s_dt, e_dt], check=True)
            except subprocess.CalledProcessError as e:
                self.append_log(f"❌ K 線下載失敗，請檢查 Log (Code: {e.returncode})")
                return
            except Exception as e:
                self.append_log(f"❌ 執行錯誤: {e}")
                return

            # 3. 讀取 CSV
            csv_path = "history_kline.csv"
            if not os.path.exists(csv_path):
                self.append_log("❌ 找不到 history_kline.csv，無法計算 MA")
                return

            # 4. 初始化策略 Worker
            params = {
                'ma': ma_days, 
                'qty': int(self.qty_in.text()),
                'buffer': float(self.buffer_in.text()), 
                'sl': float(self.sl_in.text()),
                'ttp_trig': float(self.ttp_trig_in.text()), 
                'ttp_call': float(self.ttp_call_in.text()),
                'account': self.target_account
            }
            # 取得 order 物件
            order_obj = self.engine_thread.fetcher.m_pSKOrder
            self.worker = TradingWorker(order_obj, params, "TX00")
            self.worker.log_signal.connect(self.append_log)

            # 5. 載入歷史資料到 Worker
            try:
                count = 0
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None) # 跳過標頭
                    for row in reader:
                        if len(row) >= 5:
                            # 欄位 4 是收盤價 (Close)
                            close_p = float(row[4])
                            self.worker.add_history(close_p, is_history=True)
                            count += 1
                
                self.append_log(f"✅ 成功載入 {count} 筆歷史資料")
                # 計算最終 MA 數值
                self.worker.report_status()
                
            except Exception as e:
                self.append_log(f"❌ 讀取 CSV 失敗: {e}")
                self.worker = None
                return

            # 6. 更新 UI 狀態
            self.start_btn.setText("停止策略")
            self.start_btn.setStyleSheet("background-color: #c0392b; color: white;")
            self.append_log(f"▶️ 策略正式啟動！MA({ma_days}) 監控中...")

        else:
            # 停止策略
            self.worker = None
            self.start_btn.setText("啟動策略")
            self.start_btn.setStyleSheet("background-color: #27ae60; color: white;")
            self.append_log("⏹️ 策略已停止")

    def append_log(self, msg):
        self.log_box.append(msg)
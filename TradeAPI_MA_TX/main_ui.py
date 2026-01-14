import sys
import comtypes.client
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import config
from sk_utils import handle_code, sk # 使用共用的工具
from request_futures_data import QuoteFetcher # 直接導入您那隻會動的程式
from trading_strategy import TradingWorker
from KLine_Fetch import KLineFetcher
from datetime import datetime, timedelta # 新增：日期計算

# 1. 建立一個橋接器，負責把 request_futures_data 的資料傳給 PySide6 UI
class PriceBridge(QObject):
    price_signal = Signal(float)
    account_signal = Signal(str)
    log_signal = Signal(str)
    kline_data_signal = Signal(str, str) # 傳遞 K 線字串
    request_kline_command = Signal(str, str) # 傳送指令 請求 K 線資料

# 2. 繼承您原始的 QuoteFetcher，複寫它的事件來抓取資料，但不改動原始檔案內容
class UIBridgedFetcher(QuoteFetcher):
    def __init__(self, bridge):
        import pythoncom
        pythoncom.CoInitialize() # 務必新增這行，確保 COM 元件跨執行緒運作
        super().__init__()
        self.bridge = bridge
        self.bridge.request_kline_command.connect(self.request_kline)

    # 複寫報價事件：執行原本的 print，並額外發送訊號給 UI
    def OnNotifyQuoteLONG(self, sMarketNo, nIndex):
        # 執行原本 request_futures_data.py 裡的邏輯 (包含 print)
        super().OnNotifyQuoteLONG(sMarketNo, nIndex)
        
        # 額外抓出價格發給 UI
        pSKStock = sk.SKSTOCKLONG()
        res = self.m_pSKQuote.SKQuoteLib_GetStockByIndexLONG(sMarketNo, nIndex, pSKStock)
        if isinstance(res, tuple): pSKStock = res[0]
        
        price = pSKStock.nClose / 100.0
        if price > 0:
            self.bridge.price_signal.emit(price)

    # 複寫帳號事件：把帳號傳給 UI
    def OnAccount(self, bstrLogInID, bstrAccountData):
        super().OnAccount(bstrLogInID, bstrAccountData)
        if bstrAccountData.startswith("TF"):
            data = bstrAccountData.split(',')
            account = data[1] + data[3]
            self.bridge.account_signal.emit(account)

    # 複寫連線事件：更新狀態
    def OnConnection(self, nKind, nCode):
        super().OnConnection(nKind, nCode)
        if nKind == 3003:
            self.bridge.log_signal.emit("🚀 報價伺服器就緒")

    def request_kline(self, start_date, end_date):
        target = "TX00"
        res = self.m_pSKQuote.SKQuoteLib_RequestKLineAMByDate(target, 4, 1, 0, start_date, end_date, 1)
        return self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(res))
    

    # --- 新增這個事件 (對接 RequestKLineAMByDate 的回傳) ---
    def OnNotifyKLineData(self, bstrStockNo, bstrData):
        # 無論是否有資料，都轉發給 UI
        if bstrData:
            # 傳送 K 線資料字串
            self.bridge.kline_data_signal.emit(bstrStockNo, bstrData)
        else:
            # 資料傳完了，傳送一個空字串作為「結束標記」
            self.bridge.log_signal.emit(f"📊 {bstrStockNo} 歷史 K 線讀取完成。")
            self.bridge.kline_data_signal.emit(bstrStockNo, "")

# 3. 建立執行緒來運行原本的 tkinter 訊息幫浦
class FetcherThread(QThread):
    def __init__(self, bridge):
        super().__init__()
        self.bridge = bridge
        self.fetcher = None

    def run(self):
        # 在獨立執行緒中初始化，確保 root.mainloop 跑在這裡不卡 UI
        self.fetcher = UIBridgedFetcher(self.bridge)
        # 執行原本 request_futures_data.py 的啟動流程
        self.fetcher.start()

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
        self.bridge.kline_data_signal.connect(self.on_history_received)
        
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
        self.ma_in = QLineEdit("60")
        self.qty_in = QLineEdit("1")
        self.buffer_in = QLineEdit("0.1")
        self.sl_in = QLineEdit("1.5")
        self.ttp_trig_in = QLineEdit("2.0")
        self.ttp_call_in = QLineEdit("0.5")
        layout.addLayout(form)
        form.addRow("MA 週期 (K棒):", self.ma_in)
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
            self.append_log("⚠️ 報價尚未就緒")
            return
            
        if self.start_btn.text() == "啟動策略":
            # --- 新增：自動計算日期 ---
            today = datetime.now()
            s_dt = (today - timedelta(days=60)).strftime("%Y%m%d")
            e_dt = (today - timedelta(days=1)).strftime("%Y%m%d")

            params = {
                'ma': int(self.ma_in.text()), 'qty': int(self.qty_in.text()),
                'buffer': float(self.buffer_in.text()), 'sl': float(self.sl_in.text()),
                'ttp_trig': float(self.ttp_trig_in.text()), 'ttp_call': float(self.ttp_call_in.text()),
                'account': self.target_account
            }
            # 使用引擎內建立好的 order 物件進行下單
            self.worker = TradingWorker(self.engine_thread.fetcher.m_pSKOrder, params, "TX00")
            self.worker.log_signal.connect(self.append_log)
            
            # 請求歷史 K 線
            self.bridge.request_kline_command.emit(s_dt, e_dt)
            
            self.start_btn.setText("停止策略")
            self.start_btn.setStyleSheet("background-color: #c0392b; color: white;")
            self.append_log(f"▶️ 策略啟動：正在計算 MA({params['ma']})...")
        else:
            self.worker = None
            self.start_btn.setText("啟動策略")
            self.start_btn.setStyleSheet("background-color: #27ae60; color: white;")
            self.append_log("⏹️ 策略已停止")

    # 處理回傳的歷史資料
    def on_history_received(self, bstrStockNo, bstrData):
        if self.worker and "TX" in bstrStockNo:
            # 當收到空字串，代表 60 天資料全部跑完了
            if not bstrData: 
                self.append_log("✅ 歷史資料讀取完畢，顯示最新數據...")
                # 此時 worker.history_prices 已經被 add_history 填滿了最後 5 筆
                self.worker.report_status() 
                return
                
            cols = bstrData.split(',')
            if len(cols) >= 5:
                # 這裡會不斷更新 worker 內部的 current_ma
                self.worker.add_history(float(cols[4]), is_history=True)

    def append_log(self, msg):
        self.log_box.append(msg)

    # 轉發原本的 OnKLine 事件給 worker
    def OnKLine(self, bstrStockNo, bstrData):
        if self.worker and bstrStockNo == "TX00":
            cols = bstrData.split(',')
            if len(cols) >= 5:
                self.worker.add_history(float(cols[4]))
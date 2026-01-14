import comtypes.client
import os
import sys
import csv
import tkinter as tk
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()
USER_ID = os.getenv("CAPITAL_USER_ID")
USER_PASS = os.getenv("CAPITAL_PASSWORD")

# 2. DLL 元件初始化
DLL_PATH = r'C:\Trading\TradeAPI_MA_TX\units\SKCOM.dll'
comtypes.client.GetModule(DLL_PATH)
import comtypes.gen.SKCOMLib as sk

def handle_code(res):
    if isinstance(res, (list, tuple)):
        return int(res[-1])
    return int(res)

class KLineFetcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.m_pSKCenter = comtypes.client.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
        self.m_pSKQuote = comtypes.client.CreateObject(sk.SKQuoteLib, interface=sk.ISKQuoteLib)
        self.m_pSKReply = comtypes.client.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)
        self.m_pSKOrder = comtypes.client.CreateObject(sk.SKOrderLib, interface=sk.ISKOrderLib)
        
        self.reply_handler = comtypes.client.GetEvents(self.m_pSKReply, self)
        self.quote_handler = comtypes.client.GetEvents(self.m_pSKQuote, self)
        
        self.is_ready = False
        self.has_requested = False
        self.exit_timer = None 
        self.csv_file = None
        self.csv_writer = None

    def OnReplyMessage(self, bstrUserID, bstrMessages):
        return -1

    def OnConnection(self, nKind, nCode):
        if nKind == 3003 and not self.has_requested:
            self.is_ready = True
            print(f"Server Ready (3003), Requesting: {self.start_date} -> {self.end_date}")
            self.request_kline(self.start_date, self.end_date)

    def OnNotifyKLineData(self, bstrStockNo, bstrData):
        if bstrData:
            print(f"Data: {bstrData}")
            # --- 修改重點：寫入 CSV ---
            # 資料格式通常為: Date, Open, High, Low, Close, Volume
            # 可能一次回傳多行，需逐行處理
            lines = bstrData.split('\n')
            for line in lines:
                cols = line.strip().split(',')
                # 簡單檢查欄位數量是否足夠
                if len(cols) >= 5: 
                    self.csv_writer.writerow(cols)

            # 重置結束計時器
            if self.exit_timer:
                self.root.after_cancel(self.exit_timer)
            self.exit_timer = self.root.after(2000, self.force_exit)
        else:
            print(f">>> {bstrStockNo} 下載完成")
            self.root.after(500, self.force_exit)

    def force_exit(self):
        print(">>> 資料抓取完畢，寫入檔案並結束。")
        if self.csv_file:
            self.csv_file.close()
        self.m_pSKQuote.SKQuoteLib_LeaveMonitor()
        self.root.quit()
        self.root.destroy()

    def start(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        # 開啟 CSV 檔案準備寫入
        self.csv_file = open("history_kline.csv", "w", newline="", encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        # 寫入標頭 (可選)
        self.csv_writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])

        self.m_pSKCenter.SKCenterLib_SetLogPath(r"C:\skcom_logs")
        self.m_pSKCenter.SKCenterLib_SetAuthority(0) 

        print(f"步驟 1: 執行登入 ({USER_ID})...")
        self.m_pSKCenter.SKCenterLib_Login(USER_ID, USER_PASS)
        
        self.m_pSKOrder.SKOrderLib_Initialize()
        self.m_pSKOrder.GetUserAccount()
        
        print("步驟 2: 開啟報價伺服器監控...")
        self.m_pSKQuote.SKQuoteLib_EnterMonitorLONG()
        
        # 備援：5秒沒反應主動請求
        self.root.after(5000, lambda: self.m_pSKQuote.SKQuoteLib_RequestStockList(2))
        
        self.root.mainloop()

    def request_kline(self, start_date, end_date):
        self.has_requested = True
        target = "TX00"
        self.m_pSKQuote.SKQuoteLib_RequestKLineAMByDate(target, 4, 1, 0, start_date, end_date, 1)

if __name__ == "__main__":
    fetcher = KLineFetcher()
    # 從命令列讀取日期參數
    s_dt = sys.argv[1] if len(sys.argv) > 1 else "20250101"
    e_dt = sys.argv[2] if len(sys.argv) > 2 else "20251231"
    
    try:
        fetcher.start(s_dt, e_dt)
    except KeyboardInterrupt:
        fetcher.force_exit()
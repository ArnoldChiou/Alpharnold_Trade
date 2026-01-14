import comtypes.client
import os
import time
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

# 3. K 線抓取控制器
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
        self.exit_timer = None # 自動結束計時器

        # 用於儲存要請求的日期
        self.start_date = ""
        self.end_date = ""

    def OnReplyMessage(self, bstrUserID, bstrMessages):
        return -1

    def OnConnection(self, nKind, nCode):
        kind_msg = self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(nKind))
        print(f"【連線事件】種類: {kind_msg}({nKind}), 結果: {nCode}")
        
        if nKind == 3003 and not self.has_requested:
            self.is_ready = True
            # 2. 修改這裡：呼叫時傳入剛才存好的日期變數
            result_msg = self.request_kline(self.start_date, self.end_date)
            print(f"請求結果: {result_msg}")

    def OnNotifyKLineData(self, bstrStockNo, bstrData):
        if bstrData:
            print(f"【K線回傳】{bstrStockNo}: {bstrData}")
            
            # --- 核心修改：計時器自動結束邏輯 ---
            if self.exit_timer:
                self.root.after_cancel(self.exit_timer)
            # 2秒內沒新資料就判定結束並關閉
            self.exit_timer = self.root.after(2000, self.force_exit)
        else:
            print(f"\n>>> [通知] {bstrStockNo} 歷史資料讀取完成。")
            self.root.after(500, self.force_exit)

    def force_exit(self):
        """ 統一關閉流程 """
        print(">>> 正在切斷連線並結束程式...")
        self.m_pSKQuote.SKQuoteLib_LeaveMonitor()
        self.root.quit()
        self.root.destroy()

    def start(self, start_date, end_date):
        self.m_pSKCenter.SKCenterLib_SetLogPath(r"C:\skcom_logs")
        # 修改：確保連線環境
        self.m_pSKCenter.SKCenterLib_SetAuthority(0) 

        """ 啟動時傳入日期並存入 self """
        self.start_date = start_date
        self.end_date = end_date
        
        print(f"步驟 1: 執行登入 ({USER_ID})...")
        login_res = self.m_pSKCenter.SKCenterLib_Login(USER_ID, USER_PASS)
        if handle_code(login_res) != 0:
            print(f"登入失敗: {self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(login_res))}")
            return

        # 修改：同步權限與帳號
        self.m_pSKOrder.SKOrderLib_Initialize()
        self.m_pSKOrder.GetUserAccount()
        
        print("步驟 2: 開啟報價伺服器監控...")
        self.m_pSKQuote.SKQuoteLib_EnterMonitorLONG()
        
        # 加強：若 2 秒內沒出現 3003，主動引導一次
        self.root.after(5000, lambda: self.m_pSKQuote.SKQuoteLib_RequestStockList(2))
        
        print(">>> 系統運行中，等待 3003 訊號...")
        self.root.mainloop()

    def request_kline(self, start_date, end_date):
        self.has_requested = True
        target = "TX00"
        # 執行 K 線請求，使用傳入的 start_date 與 end_date
        res = self.m_pSKQuote.SKQuoteLib_RequestKLineAMByDate(target, 4, 1, 0, start_date, end_date, 1)
        # 回傳解析後的訊息字串
        return self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(res))


if __name__ == "__main__":
    fetcher = KLineFetcher()
    try:
        fetcher.start("20260101", "20260114")
    except KeyboardInterrupt:
        fetcher.force_exit()
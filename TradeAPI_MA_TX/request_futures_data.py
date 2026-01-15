import comtypes.client
import os
import time
import ctypes
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

# 輔助：處理 comtypes 回傳的 [out] 參數與 list/tuple 格式
def handle_code(res):
    if isinstance(res, (list, tuple)):
        return int(res[-1])
    return int(res)

# 3. 核心報價控制器 (完全同步 Quote.py 運作環境)
class QuoteFetcher:
    def __init__(self):
        # 建立隱藏 Tk 提供與 Quote.py 一致的訊息泵環境
        self.root = tk.Tk()
        self.root.withdraw()
        
        # 宣告所有物件 (依照 Quote.py 順序)
        self.m_pSKCenter = comtypes.client.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
        self.m_pSKQuote = comtypes.client.CreateObject(sk.SKQuoteLib, interface=sk.ISKQuoteLib)
        self.m_pSKOSQuote = comtypes.client.CreateObject(sk.SKOSQuoteLib, interface=sk.ISKOSQuoteLib)
        self.m_pSKOOQuote = comtypes.client.CreateObject(sk.SKOOQuoteLib, interface=sk.ISKOOQuoteLib)
        self.m_pSKReply = comtypes.client.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)
        self.m_pSKOrder = comtypes.client.CreateObject(sk.SKOrderLib, interface=sk.ISKOrderLib)
        
        # 註冊事件監聽 (Sink 為 self)
        self.reply_handler = comtypes.client.GetEvents(self.m_pSKReply, self)
        self.quote_handler = comtypes.client.GetEvents(self.m_pSKQuote, self)
        self.order_handler = comtypes.client.GetEvents(self.m_pSKOrder, self)
        
        self.is_ready = False

    # --- 移植 Quote.py 的事件方法 ---
    def OnReplyMessage(self, bstrUserID, bstrMessages):
        print(f"【系統公告】{bstrUserID}: {bstrMessages}")
        return -1

    def OnAccount(self, bstrLogInID, bstrAccountData):
        print(f"【權限確認】帳號: {bstrAccountData}")

    def OnConnection(self, nKind, nCode):
        # 轉譯狀態碼
        kind_msg = self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(nKind))
        code_msg = self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(nCode))
        print(f"【連線事件】種類: {kind_msg}({nKind}), 結果: {code_msg}({nCode})")
        
        # 關鍵修正：判斷 nKind (種類) 是否為 3003 (Stocks Ready)
        if nKind == 3003:
            print("\n>>> [重要訊號] 商品同步完成，啟動訂閱流程...")
            self.is_ready = True
            self.subscribe_market_data()

    def OnNotifyQuoteLONG(self, sMarketNo, nIndex):
        pSKStock = sk.SKSTOCKLONG()
        # 參考 Quote.py 邏輯取得資料結構
        res = self.m_pSKQuote.SKQuoteLib_GetStockByIndexLONG(sMarketNo, nIndex, pSKStock)
        if isinstance(res, tuple): pSKStock = res[0]
        
        # 價格除以 100.0 (Quote.py 標準寫法)
        # 注意：TX00 在盤後(夜盤)會有成交價跳動
        #print(f"【{pSKStock.bstrStockNo} {pSKStock.bstrStockName.strip()}】"
              #f"成交: {pSKStock.nClose/100.0:>8} | 總量: {pSKStock.nTQty}")

    # --- 流程控制 ---
    def start(self):
        # A. 啟動準備
        self.m_pSKCenter.SKCenterLib_SetLogPath(r"C:\skcom_logs")
        self.m_pSKCenter.SKCenterLib_SetAuthority(0) # 正式環境

        # B. 登入
        print(f"步驟 1: 執行登入 ({USER_ID})...")
        login_res = self.m_pSKCenter.SKCenterLib_Login(USER_ID, USER_PASS)
        if handle_code(login_res) != 0:
            print(f"登入失敗: {self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(login_res))}")
            return

        # C. 模仿 Quote.py 同步交易權限 (重要)
        self.m_pSKOrder.SKOrderLib_Initialize()
        self.m_pSKOrder.GetUserAccount()

        # D. 進入監控
        print("步驟 2: 開啟報價伺服器監控...")
        self.m_pSKQuote.SKQuoteLib_EnterMonitorLONG()
        
        # 每秒檢查一次 IsConnected 狀態作為備援機制
        self.root.after(1000, self.backup_check)
        
        # E. 進入訊息泵循環
        print(">>> 系統運行中，等待報價事件 (Ctrl+C 結束)...")
        self.root.mainloop()

    def backup_check(self):
        """ 如果 OnConnection 沒被正確捕捉，由備援機制觸發訂閱 """
        if self.is_ready: return
        
        status = self.m_pSKQuote.SKQuoteLib_IsConnected()
        if status == 3:
            print("\n>>> [備援檢測] 伺服器狀態為 3，強制執行訂閱")
            self.is_ready = True
            self.subscribe_market_data()
        elif status == 2:
            # 模仿 Quote.py 點擊商品清單，引導同步
            self.m_pSKQuote.SKQuoteLib_RequestStockList(2) # 2=期貨
        
        self.root.after(1000, self.backup_check)

    def subscribe_market_data(self):
        # 訂閱 TX00 (台指期全盤)
        target = "TX00"
        print(f"步驟 3: 發送訂閱請求 [{target}]...")
        # 參考 Quote.py: RequestStocks(頁碼, 代碼)
        res = self.m_pSKQuote.SKQuoteLib_RequestStocks(1, target)
        nCode = handle_code(res)
        print(f"訂閱請求結果: {self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)}")

if __name__ == "__main__":
    fetcher = QuoteFetcher()
    try:
        fetcher.start()
    except KeyboardInterrupt:
        print("\n使用者停止程式")
        fetcher.m_pSKQuote.SKQuoteLib_LeaveMonitor()
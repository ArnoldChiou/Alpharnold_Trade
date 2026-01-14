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

# 3. 帳戶權益數查詢控制器
class FuturesEquityFetcher:
    def __init__(self):
        # 建立隱藏視窗提供訊息泵
        self.root = tk.Tk()
        self.root.withdraw()
        
        # 宣告核心物件
        self.m_pSKCenter = comtypes.client.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
        self.m_pSKReply = comtypes.client.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)
        self.m_pSKOrder = comtypes.client.CreateObject(sk.SKOrderLib, interface=sk.ISKOrderLib)
        
        # 註冊事件監聽
        self.reply_handler = comtypes.client.GetEvents(self.m_pSKReply, self)
        self.order_handler = comtypes.client.GetEvents(self.m_pSKOrder, self)
        
        self.target_account = "" 

    # --- 系統事件方法 ---
    def OnReplyMessage(self, bstrUserID, bstrMessages):
        print(f"【系統公告】{bstrUserID}: {bstrMessages}")
        return -1

    def OnAccount(self, bstrLogInID, bstrAccountData):
        """ 帳號資訊回報 """
        values = bstrAccountData.split(',')
        if values[0] == "TF": # 國內期貨
            self.target_account = values[1] + values[3]
            print(f"【確認期貨帳號】: {self.target_account}")

    def OnFutureRights(self, bstrData):
        """ 
        權益數查詢結果 (依照官方提供之 41 個欄位解析) 
        """
        # 檢查結束符號
        if bstrData.startswith("##"):
            print(">>> 權益數查詢結束。")
            return

        items = bstrData.split(',')
        # 確保資料長度符合官方定義 (至少要有 41 欄)
        if len(items) < 41:
            return

        print("\n" + "="*60)
        print(f"      [國內期貨] 帳戶權益數回報 (幣別: {items[25]})")
        print("="*60)
        
        try:
            # 依照您提供的官方定義表進行對照
            print(f"帳號 (ACCOUNT_NO)  : {items[40]}")
            print(f"權益數 (Index 6)    : {items[6]}")
            print(f"可用餘額 (Index 31) : {items[31]}")
            print(f"風險指標 (Index 34) : {items[34]} %")
            print("-" * 30)
            print(f"浮動損益 (Index 1)  : {items[1]}")
            print(f"期貨平倉損益 (Index 11): {items[11]}")
            print(f"原始保證金 (Index 13): {items[13]}")
            print(f"維持保證金 (Index 14): {items[14]}")
            print(f"預扣權利金 (Index 4) : {items[4]}")
            print(f"昨日餘額 (Index 22) : {items[22]}")
        except Exception as e:
            print(f"解析發生錯誤: {e}")
            print(f"原始字串: {bstrData}")
            
        print("="*60 + "\n")

    # --- 流程控制 ---
    def start(self):
        self.m_pSKCenter.SKCenterLib_SetLogPath(r"C:\skcom_logs")
        self.m_pSKCenter.SKCenterLib_SetAuthority(0)

        print(f"1. 執行登入程序...")
        login_res = self.m_pSKCenter.SKCenterLib_Login(USER_ID, USER_PASS)
        if handle_code(login_res) != 0:
            print(f"登入失敗: {self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(login_res))}")
            return

        print("2. 初始化下單元件並獲取交易帳號...")
        self.m_pSKOrder.SKOrderLib_Initialize()
        self.m_pSKOrder.GetUserAccount()
        
        # 延遲 3 秒確保帳號事件處理完畢後才查詢
        self.root.after(3000, self.request_info)
        
        print(">>> 正在等待帳務資料回傳...")
        self.root.mainloop()

    def request_info(self):
        if not self.target_account:
            print("錯誤: 找不到可用的期貨帳號。")
            return

        print(f"3. 執行 GetFutureRights (帳號: {self.target_account}, 幣別: 1)...")
        # 幣別依照官方範例: 1 為基幣 (台幣 TWD)
        nCode = self.m_pSKOrder.GetFutureRights(USER_ID, self.target_account, 1)
        
        if handle_code(nCode) != 0:
            print(f"指令發送失敗: {self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(nCode))}")

if __name__ == "__main__":
    fetcher = FuturesEquityFetcher()
    try:
        fetcher.start()
    except KeyboardInterrupt:
        print("\n使用者結束程式")
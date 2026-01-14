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

# 3. 下單控制器
class FuturesOrderBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.m_pSKCenter = comtypes.client.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
        self.m_pSKReply = comtypes.client.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)
        self.m_pSKOrder = comtypes.client.CreateObject(sk.SKOrderLib, interface=sk.ISKOrderLib)
        
        self.reply_handler = comtypes.client.GetEvents(self.m_pSKReply, self)
        self.order_handler = comtypes.client.GetEvents(self.m_pSKOrder, self)
        
        self.target_account = "" 

    def OnReplyMessage(self, bstrUserID, bstrMessages):
        print(f"【系統公告】{bstrUserID}: {bstrMessages}")
        return -1

    def OnAccount(self, bstrLogInID, bstrAccountData):
        values = bstrAccountData.split(',')
        if values[0] == "TF": 
            self.target_account = values[1] + values[3]
            print(f"【確認交易帳號】: {self.target_account}")

    def OnAsyncOrder(self, nThreadID, nCode, bstrMessage):
        print(f"【非同步下單回報】{bstrMessage} (代碼: {nCode})")

    # --- 下單執行流程 ---
    def start(self):
        self.m_pSKCenter.SKCenterLib_SetLogPath(r"C:\skcom_logs")
        
        # 設定為測試環境 (2: 測試環境)
        print("步驟 1: 設定為 [正式環境]...")
        self.m_pSKCenter.SKCenterLib_SetAuthority(1)

        # 執行登入
        login_res = self.m_pSKCenter.SKCenterLib_Login(USER_ID, USER_PASS)
        if handle_code(login_res) != 0:
            print(f"登入失敗: {self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(handle_code(login_res))}")
            return

        # 初始化下單元件
        print("步驟 2: 初始化下單元件...")
        self.m_pSKOrder.SKOrderLib_Initialize()
        
        # ======================================================
        # 【關鍵加入】讀取憑證資訊 (ReadCertByID)
        # 必須在下單前執行，且參數必須是登入 ID (UserID)
        # ======================================================
        print(f"步驟 2.1: 正在讀取憑證 ({USER_ID})...")
        cert_res = self.m_pSKOrder.ReadCertByID(USER_ID)
        nCertCode = handle_code(cert_res)
        cert_msg = self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCertCode)
        print(f"憑證讀取結果: {cert_msg}")
        
        if nCertCode != 0:
            print("警告: 憑證讀取失敗，下單可能會失敗。請確認憑證是否已安裝至系統。")
        # ======================================================

        self.m_pSKOrder.GetUserAccount()
        
        # 等待 3 秒獲取帳號後下單
        self.root.after(3000, self.execute_test_order)
        self.root.mainloop()

    def execute_test_order(self):
        if not self.target_account:
            print("錯誤: 找不到期貨帳號。")
            return

        print(f"\n步驟 3: 發送委託指令 (帳號: {self.target_account})...")

        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = self.target_account
        pOrder.bstrStockNo = "TX00"      # 台指近
        pOrder.sBuySell = 0               # 0:買進
        pOrder.sTradeType = 0             # 0:ROD
        pOrder.sDayTrade = 0              
        pOrder.sNewClose = 0              # 0:新倉
        pOrder.sReserved = 0              
        pOrder.bstrPrice = "28000"        # 測試價
        pOrder.nQty = 1                   

        # 執行同步下單
        res_val = self.m_pSKOrder.SendFutureOrderCLR(USER_ID, False, pOrder)
        
        if isinstance(res_val, tuple):
            bstrMessage, nCode = res_val
            msg = self.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
            print(f"下單指令結果: {msg}")
            print(f"伺服器回傳訊息: {bstrMessage}")
        else:
            print(f"執行失敗，回傳: {res_val}")

        print("\n>>> 測試結束。")

if __name__ == "__main__":
    bot = FuturesOrderBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n使用者停止程式")
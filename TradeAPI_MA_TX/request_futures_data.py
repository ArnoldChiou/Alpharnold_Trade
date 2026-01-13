import comtypes.client
import os
import time
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()
USER_ID = os.getenv("CAPITAL_USER_ID")
USER_PASS = os.getenv("CAPITAL_PASSWORD")

# 2. 設定 DLL 相對路徑
dll_path = r"units\SKCOM.dll"
comtypes.client.GetModule(dll_path)
import comtypes.gen.SKCOMLib as sk

# 3. 定義事件類別
class SKEvents:
    def __init__(self):
        self.is_connected = False

    # 【核心】公告回報：必須回傳 -1
    def OnReplyMessage(self, bstrUserID, bstrMessages):
        print(f"【系統公告】{bstrMessages}")
        return -1

    # 報價連線狀態
    def OnConnection(self, nKind, nCode):
        if nKind == 3: 
            if nCode == 3: 
                print("\n>>> [系統] 報價伺服器連線成功 (狀態 3)")
                self.is_connected = True
            elif nCode == 2:
                print(".", end="", flush=True)

    # 即時報價 (使用 LONG 版本)
    def OnNotifyQuoteLONG(self, sMarketNo, nIndex):
        pStock = sk.SKSTOCKLONG()
        pStock, nCode = skQ.SKQuoteLib_GetStockByIndexLONG(sMarketNo, nIndex, pStock)
        if nCode == 0:
            name = pStock.bstrStockName.strip()
            price = pStock.nClose / 100.0
            print(f"【{name}】成交: {price:.2f} | 總量: {pStock.nTQty}")

# 4. 初始化物件與註冊事件
skC = comtypes.client.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
skR = comtypes.client.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)
global skQ
skQ = comtypes.client.CreateObject(sk.SKQuoteLib, interface=sk.ISKQuoteLib)

# 建立事件實體
handler = SKEvents()

# 【關鍵修正】必須賦值給變數，避免物件被回收
# 順序：先註冊公告 (Reply)，再註冊報價 (Quote)
reply_connection = comtypes.client.GetEvents(skR, handler)
quote_connection = comtypes.client.GetEvents(skQ, handler)

def main():
    # A. 設定環境 (0:正式)
    skC.SKCenterLib_SetAuthority(0)
    
    # B. 登入 (在此之前已經註冊好公告事件了)
    login_code = skC.SKCenterLib_Login(USER_ID, USER_PASS)
    print(f"1. 登入狀態: {skC.SKCenterLib_GetReturnCodeMessage(login_code)}")
    
    if login_code != 0:
        return

    # C. 進入報價伺服器
    skQ.SKQuoteLib_EnterMonitorLONG()
    
    print("2. 正在與伺服器同步資料 (狀態 2)...")
    
    # 增加一個計數器，方便觀察有沒有在跑
    check_count = 0
    while not handler.is_connected:
        comtypes.client.PumpEvents(0.5)
        # 每隔幾秒主動查一下目前的狀態碼
        current_status = skQ.SKQuoteLib_IsConnected() 
        
        # 0:斷線, 1:連線中, 2:下載中, 3:連線成功
        if check_count % 10 == 0: # 每 5 秒印一次狀態
            status_text = {0:"斷線", 1:"連線中", 2:"下載資料中", 3:"連線成功"}.get(current_status, "未知")
            print(f"   [目前連線狀態]: {current_status} ({status_text})")
            
        check_count += 1
        time.sleep(0.5)
    
    # D. 訂閱商品 (現在是夜盤，建議使用具體月份代碼)
    target = "2330" 
    print(f"3. 開始訂閱 {target}...")
    skQ.SKQuoteLib_RequestStocks(1, target)
    
    try:
        while True:
            comtypes.client.PumpEvents(0.1)
    except KeyboardInterrupt:
        print("\n使用者結束監控")
        skQ.SKQuoteLib_LeaveMonitor()

if __name__ == "__main__":
    main()
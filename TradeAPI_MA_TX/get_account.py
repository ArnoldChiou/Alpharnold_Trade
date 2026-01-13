import comtypes.client
import os
import time
from dotenv import load_dotenv

# 1. 載入環境變數與初始化
load_dotenv()
USER_ID = os.getenv("CAPITAL_USER_ID")
USER_PASS = os.getenv("CAPITAL_PASSWORD")

dll_path = r"units\SKCOM.dll"
comtypes.client.GetModule(dll_path)
import comtypes.gen.SKCOMLib as sk

# 2. 定義事件類別來接收帳號資料
class SKOrderLibEvents:
    def OnAccount(self, bstrLogInID, bstrAccountData):
        # bstrAccountData 格式通常為: 帳號類型,經紀商代碼,帳號,姓名...
        print(f"【收到帳號回報】ID: {bstrLogInID} | 資料: {bstrAccountData}")

class SKReplyLibEvents:
    def OnReplyMessage(self, bstrUserID, bstrMessages):
        return -1

# 3. 建立物件與註冊事件
skC = comtypes.client.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
skO = comtypes.client.CreateObject(sk.SKOrderLib, interface=sk.ISKOrderLib)
skR = comtypes.client.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)

# 註冊事件監聽
order_events = SKOrderLibEvents()
order_handler = comtypes.client.GetEvents(skO, order_events)

reply_events = SKReplyLibEvents()
reply_handler = comtypes.client.GetEvents(skR, reply_events)

def get_trading_accounts():
    # A. 登入
    login_code = skC.SKCenterLib_Login(USER_ID, USER_PASS)
    if login_code != 0:
        print(f"登入失敗: {skC.SKCenterLib_GetReturnCodeMessage(login_code)}")
        return

    # B. 初始化下單物件 (必做)
    skO.SKOrderLib_Initialize()
    
    # C. 呼叫取得帳號函式
    print("正在請求交易帳號列表...")
    skO.GetUserAccount()

    # D. 進入迴圈等待事件回傳 (暫停 2 秒讓資料回來)
    time.sleep(2)

if __name__ == "__main__":
    get_trading_accounts()
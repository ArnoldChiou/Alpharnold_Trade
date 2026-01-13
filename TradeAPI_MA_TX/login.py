import comtypes.client
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()
# 從環境變數抓取帳密
USER_ID = os.getenv("CAPITAL_USER_ID")
USER_PASS = os.getenv("CAPITAL_PASSWORD")

# 1. API com元件路徑初始化 (請確保此路徑正確)
dll_path = r"units\SKCOM.dll"
comtypes.client.GetModule(dll_path)
import comtypes.gen.SKCOMLib as sk

# 2. 宣告物件
m_pSKCenter = comtypes.client.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
m_pSKReply = comtypes.client.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)
m_pSKOrder = comtypes.client.CreateObject(sk.SKOrderLib, interface=sk.ISKOrderLib)

# 3. 定義並註冊必要事件 (登入前必須註冊 Reply 事件)
class SKReplyLibEvent:
    def OnReplyMessage(self, bstrUserID, bstrMessages):
        print(f"【公告通知】{bstrUserID}: {bstrMessages}")
        return -1

# 建立事件監聽
SKReplyEvent = SKReplyLibEvent()
SKReplyLibEventHandler = comtypes.client.GetEvents(m_pSKReply, SKReplyEvent)

# --- 登入函式 ---
def start_login():
    if not USER_ID or not USER_PASS:
        print("錯誤：找不到 .env 帳號密碼設定")
        return

    # 執行登入
    login_code = m_pSKCenter.SKCenterLib_Login(USER_ID.strip(), USER_PASS.strip())
    print(f"登入結果: {m_pSKCenter.SKCenterLib_GetReturnCodeMessage(login_code)}")

    if login_code == 0:
        # 初始化下單物件
        m_pSKOrder.SKOrderLib_Initialize()
        # 讀取憑證
        cert_code = m_pSKOrder.ReadCertByID(USER_ID.strip())
        print(f"憑證讀取結果: {m_pSKCenter.SKCenterLib_GetReturnCodeMessage(cert_code)}")

if __name__ == "__main__":
    start_login()
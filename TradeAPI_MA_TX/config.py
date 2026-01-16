# TradeAPI_MA_TX/config.py
import os
import json
from crypto_utils import decrypt_text

# 元件路徑
DLL_PATH = r'units\SKCOM.dll'
CREDENTIALS_FILE = "credentials.json"

def load_and_decrypt_credentials():
    """
    嘗試從 credentials.json 讀取並解密帳號密碼。
    如果檔案不存在或解密失敗，回傳空字串。
    """
    u_id = ""
    u_pass = ""
    
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                data = json.load(f)
                # 使用 crypto_utils 解密
                u_id = decrypt_text(data.get("id", ""))
                u_pass = decrypt_text(data.get("pass", ""))
        except Exception as e:
            print(f"Warning: 無法讀取或解密憑證檔 ({e})")
            
    return u_id, u_pass

# 初始化變數：程式啟動時自動嘗試載入
USER_ID, USER_PASS = load_and_decrypt_credentials()

# 測試環境設定
IS_TESTNET = False
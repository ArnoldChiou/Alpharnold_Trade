# TradeAPI_MA_TX/config.py
import os
from dotenv import load_dotenv

# 嘗試讀取 .env 作為預設值 (保留相容性)
load_dotenv()

# 元件路徑
DLL_PATH = r'units\SKCOM.dll'

# 將變數改為可被修改的全域變數
USER_ID = os.getenv("CAPITAL_USER_ID", "")
USER_PASS = os.getenv("CAPITAL_PASSWORD", "")

# 測試環境設定
IS_TESTNET = False
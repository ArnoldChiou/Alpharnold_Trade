#控制測試環境或正式環境
import os
from dotenv import load_dotenv

load_dotenv()

# 是否為測試環境 (True: 測試環境, False: 正式環境)
IS_TESTNET = False 

# 元件路徑
DLL_PATH = r'units\SKCOM.dll'

# 帳號資訊
USER_ID = os.getenv("CAPITAL_USER_ID")
USER_PASS = os.getenv("CAPITAL_PASSWORD")
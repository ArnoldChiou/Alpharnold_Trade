# crypto_utils.py
from cryptography.fernet import Fernet
import os

# 這是加密用的主金鑰。在實際生產環境中，建議將此金鑰儲存在更安全的地方，
# 或者根據使用者的電腦硬體資訊（如 MAC 地址）動態生成。
# 這裡我們生成一個固定的金鑰檔案，如果不存在就建立。
KEY_FILE = "secret.key"

def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

# 初始化加密器
cipher_suite = Fernet(load_or_generate_key())

def encrypt_text(text: str) -> str:
    """將純文字加密為字串"""
    if not text: return ""
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text: str) -> str:
    """將加密字串還原為純文字"""
    if not encrypted_text: return ""
    try:
        return cipher_suite.decrypt(encrypted_text.encode()).decode()
    except:
        return "解密失敗"
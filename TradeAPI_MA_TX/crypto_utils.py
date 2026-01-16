import os
from cryptography.fernet import Fernet

KEY_FILE = "secret.key"

def load_key():
    """ 讀取或產生新的加密金鑰 """
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

def encrypt_text(text):
    if not text: return ""
    f = Fernet(load_key())
    return f.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text):
    if not encrypted_text: return ""
    try:
        f = Fernet(load_key())
        return f.decrypt(encrypted_text.encode()).decode()
    except:
        return ""
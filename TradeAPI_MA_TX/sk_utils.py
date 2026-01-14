#負責處理 DLL 載入、錯誤碼轉譯及 K 線資料解析
import comtypes.client
import config

# 預先載入模組
comtypes.client.GetModule(config.DLL_PATH)
import comtypes.gen.SKCOMLib as sk

def get_sk_lib():
    """建立並回傳完整核心元件環境 (參考 request_futures_data.py)"""
    # 建立所有物件以確保環境穩定
    center = comtypes.client.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
    quote = comtypes.client.CreateObject(sk.SKQuoteLib, interface=sk.ISKQuoteLib)
    os_quote = comtypes.client.CreateObject(sk.SKOSQuoteLib, interface=sk.ISKOSQuoteLib)
    oo_quote = comtypes.client.CreateObject(sk.SKOOQuoteLib, interface=sk.ISKOOQuoteLib)
    order = comtypes.client.CreateObject(sk.SKOrderLib, interface=sk.ISKOrderLib)
    reply = comtypes.client.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)
    
    # 回傳時將這些物件保存，避免被垃圾回收
    return center, quote, order, reply, os_quote, oo_quote

def handle_code(res):
    if isinstance(res, (list, tuple)):
        return int(res[-1])
    return int(res)
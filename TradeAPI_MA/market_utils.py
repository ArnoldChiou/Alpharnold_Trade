from binance.client import Client
import math

def get_ma_level(client, symbol, window, check_time=None):
    """
    獲取前 W 天的收盤價均線
    :param check_time: (選填) 若有傳入，會檢查最後一根 K 線的 OpenTime 是否 >= check_time
                       若否，代表抓到舊資料，回傳 None 以便重試
    """
    try:
        # 抓取 window + 1 根 (最後一根是當前未收盤)
        klines = client.futures_klines(symbol=symbol, interval='1d', limit=window + 1)
        
        if len(klines) < window + 1:
            return None

        # [新增] 嚴格檢查：確認抓回來的最後一根 K 線，時間是否正確
        if check_time is not None:
            last_open_time = klines[-1][0]
            if last_open_time < check_time:
                # 抓到的資料過舊（還沒換日），回傳失敗
                print(f"[{symbol}] 資料過舊，重試中... (預期: {check_time}, 實際: {last_open_time})")
                return None

        # 排除最後一根（當前未收盤），只取已收盤的
        closed_klines = klines[:-1]
        closes = [float(k[4]) for k in closed_klines] 
        return sum(closes) / len(closes)
    except Exception as e:
        print(f"獲取 MA 失敗: {e}")
        return None

def get_symbol_rules(client, symbol):
    try:
        info = client.futures_exchange_info()
        ticker = client.futures_symbol_ticker(symbol=symbol)
        curr_price = float(ticker['price'])
        for s in info['symbols']:
            if s['symbol'] == symbol:
                rules = {'price': curr_price}
                for f in s['filters']:
                    if f['filterType'] == 'LOT_SIZE':
                        rules['minQty'] = float(f['minQty'])
                        rules['stepSize'] = float(f['stepSize'])
                    if f['filterType'] == 'MIN_NOTIONAL':
                        rules['minNotional'] = float(f['notional'])
                min_qty_by_money = rules['minNotional'] / curr_price
                rules['actualMinQty'] = max(rules['minQty'], min_qty_by_money)
                rules['actualMinQty'] = math.ceil(rules['actualMinQty'] / rules['stepSize']) * rules['stepSize']
                return rules
        return None
    except: return None

def round_step_size(quantity, step_size):
    precision = int(round(-math.log10(step_size), 0))
    factor = 10 ** precision
    return math.floor(quantity * factor) / factor
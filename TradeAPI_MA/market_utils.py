from binance.client import Client
import math

def get_ma_level(client, symbol, window):
    """獲取前 W 天的收盤價均線 (不含當前未收盤的 K 線)"""
    try:
        # 抓取 window + 1 根日 K，最後一根為今天（未完成），故排除
        klines = client.futures_klines(symbol=symbol, interval='1d', limit=window + 1)
        if len(klines) < window + 1:
            return None
            
        closed_klines = klines[:-1] # 只取已收盤的天數
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
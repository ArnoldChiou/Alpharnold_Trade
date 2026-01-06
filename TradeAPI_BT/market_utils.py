from binance.client import Client
import math

def get_breakout_levels(client, symbol, lookback):
    try:
        # 抓取 lookback + 1 根，因為最後一根是「今天」不能算
        klines = client.futures_klines(symbol=symbol, interval='1d', limit=lookback + 1)
        if len(klines) < lookback + 1:
            return None, None
            
        # [:-1] 代表排除掉最後一根（今天），只取前面「已完成收盤」的天數
        closed_klines = klines[:-1]
        
        highs = [float(k[2]) for k in closed_klines]
        lows = [float(k[3]) for k in closed_klines]
        
        return max(highs), min(lows)
    except:
        return None, None
    
def get_quantity_precision(client, symbol):
    """從幣安獲取該幣種的數量精度與最小步進"""
    try:
        info = client.futures_exchange_info()
        for s in info['symbols']:
            if s['symbol'] == symbol:
                for f in s['filters']:
                    if f['filterType'] == 'LOT_SIZE':
                        step_size = float(f['stepSize'])
                        # 計算小數位數 (例如 0.001 -> 3)
                        precision = int(round(-math.log10(step_size), 0))
                        return step_size, precision
        return None, None
    except Exception as e:
        print(f"獲取精度失敗: {e}")
        return None, None

def round_step_size(quantity, step_size):
    """根據步進長度進行精確捨去"""
    # 避免浮點數精度問題，使用小數校正
    precision = int(round(-math.log10(step_size), 0))
    return floor_to_precision(quantity, precision)

def floor_to_precision(value, precision):
    """無條件捨去到指定位數"""
    factor = 10 ** precision
    return math.floor(value * factor) / factor

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
                        rules['qtyPrecision'] = int(round(-math.log10(rules['stepSize']), 0))
                    
                    if f['filterType'] == 'MIN_NOTIONAL':
                        # 這是「最小需下單多少 USDT」
                        rules['minNotional'] = float(f['notional'])
                
                # 計算基於金額的最小數量： $MinQty_{money} = \frac{MinNotional}{Price}$
                min_qty_by_money = rules['minNotional'] / curr_price
                
                # 真正的最小量 = max(數量限制, 金額限制)
                rules['actualMinQty'] = max(rules['minQty'], min_qty_by_money)
                
                # 根據步進單位進行向上取整，確保符合規則
                rules['actualMinQty'] = math.ceil(rules['actualMinQty'] / rules['stepSize']) * rules['stepSize']
                
                return rules
        return None
    except Exception as e:
        print(f"獲取規則失敗: {e}")
        return None
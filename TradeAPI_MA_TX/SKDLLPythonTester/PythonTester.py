from SKDLLPython import SK
from PythonTesterUI import MainApp
import tkinter as tk

def on_reply_message(strLoginID, strMessage):
    app = MainApp.instance
    if app:
        login_ui = app.login_frame
        login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[OnReplyMessage] 回傳值: {strLoginID} _ {strMessage}"))
SK.OnReplyMessage(on_reply_message)

def on_Connection_message(loginID, code):
    app = MainApp.instance
    if app:
        login_ui = app.login_frame
        login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[OnConnection]使用者 {loginID} 狀態碼: {SK.GetMessage(code)}"))
SK.OnConnection(on_Connection_message)

def on_OnProxyOrder_message(StampID, Code, Message):
    app = MainApp.instance
    if app:
        login_ui = app.login_frame
        login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[OnProxyOrder]回傳值: StampID[{StampID}] 狀態碼: {SK.GetMessage(Code)} 訊息: {Message}"))
SK.OnProxyOrder(on_OnProxyOrder_message)

def on_OnComplete_message(loginID):
    app = MainApp.instance
    if app:
        reply_ui = app.reply_frame
        reply_ui.after(0, lambda: reply_ui.listOnNewOrderData.insert("end", f"[OnComplete]委託回補完成通知：{loginID}"))
        reply_ui.after(0, lambda: reply_ui.listOnNewFulfillData.insert("end", f"[OnComplete]成交回補完成通知：{loginID}"))
SK.OnComplete(on_OnComplete_message)

#OnNewData 為委託+成交回報，建議與 OnNewOrderData(委託回報) 跟 OnNewFulfillData(成交回報) 擇一使用
'''
def on_OnNewData_message(loginID, data):
    app = MainApp.instance
    if app:
        reply_ui = app.reply_frame
        reply_ui.after(0, lambda: reply_ui.listOnNewOrderData.insert("end", f"[{loginID}]{data.Raw}"))
        reply_ui.after(0, lambda: reply_ui.listOnNewOrderData.insert("end", f"{data.OrderNo}")) # 例如取 委託書號OrderNo
SK.OnNewData(on_OnNewData_message)
'''

def on_OnNewOrderData_message(loginID, data):
    app = MainApp.instance
    if app:
        reply_ui = app.reply_frame
        reply_ui.after(0, lambda: reply_ui.listOnNewOrderData.insert("end", f"[{loginID}]{data.Raw}"))
        reply_ui.after(0, lambda: reply_ui.listOnNewOrderData.insert("end", f"{data.OrderNo}")) # 例如取 委託書號OrderNo
SK.OnNewOrderData(on_OnNewOrderData_message)

def on_OnNewFulfillData_message(loginID, data):
    app = MainApp.instance
    if app:
        reply_ui = app.reply_frame
        reply_ui.after(0, lambda: reply_ui.listOnNewFulfillData.insert("end", f"[{loginID}]{data.Raw}"))
        reply_ui.after(0, lambda: reply_ui.listOnNewFulfillData.insert("end", f"{data.OrderNo}")) # 例如取 委託書號OrderNo
SK.OnNewFulfillData(on_OnNewFulfillData_message)

def on_OnNotifyQuoteLONG_message(nMarketNo, strStockNo):
    app = MainApp.instance
    if app:
        quote_ui = app.quote_frame  # 根據你 GUI 架構命名的報價區域

        # 呼叫 DLL 取得報價物件
        stock_data = SK.SKQuoteLib_GetStockByStockNo(nMarketNo, strStockNo)

        #更新 UI（ OnUpdateDataRow()）
        app.quote_frame.after(0, lambda: quote_ui.OnUpDateDataRow(stock_data))
SK.OnNotifyQuoteLONG(on_OnNotifyQuoteLONG_message)

def on_OnNotifyTicksLONG_message(marketNo, strStockNo, ptr, date, timeHMS, timeMicro, bid, ask, close, qty, simulate):
    app = MainApp.instance
    if not app:
        return

    quote_ui = app.quote_frame
    kMarketPrice = 0

    strData = ""

    # ➤ 判斷 chkbox_msms（是否只顯示毫秒）
    if quote_ui.chkbox_msms_var.get():
        strData = f"{strStockNo},{ptr},{date} {timeHMS},{bid},{ask},{close},{qty}"
    else:
        strData = f"{strStockNo},{ptr},{date} {timeHMS} {timeMicro},{bid},{ask},{close},{qty}"

    # ➤ 判斷 Box_M（是否套用市價轉換）
    if quote_ui.Box_M_var.get():
        if bid == kMarketPrice:
            strData = f"{strStockNo},{ptr},{date} {timeHMS},M,{ask},{close},{qty}"
        elif ask == kMarketPrice:
            strData = f"{strStockNo},{ptr},{date} {timeHMS},{bid},M,{close},{qty}"
        else:
            strData = f"{strStockNo},{ptr},{date} {timeHMS},{bid},{ask},{close},{qty}"

    # ➤ 判斷 chkBoxSimulate 以及 simulate 值
    if strData != "" and (quote_ui.chkBoxSimulate_var.get() or (not quote_ui.chkBoxSimulate_var.get() and simulate == 0)):
        quote_ui.after(0, lambda: quote_ui.listTicks.insert("end", f"[OnNotifyTicksLONG]{strData}"))
SK.OnNotifyTicksLONG(on_OnNotifyTicksLONG_message)

def on_OnNotifyBest5LONG_message(marketNo, strStockNo, bids, bidQtys, asks, askQtys, extendBid, extendBidQty, extendAsk, extendAskQty, simulate):
    app = MainApp.instance
    if not app:
        return

    quote_ui = app.quote_frame

    # ➤ 呼叫 UI 執行緒內的更新函式
    quote_ui.after(0, lambda: quote_ui.UpdateBest5Grid(
        marketNo, bids, bidQtys, asks, askQtys, extendBid, extendBidQty, extendAsk, extendAskQty, simulate
    ))   
SK.OnNotifyBest5LONG(on_OnNotifyBest5LONG_message)

def on_OnNotifyOSQuoteLONG_message(strStockNo):
    app = MainApp.instance
    if app:
        quote_ui = app.quote_frame  # 根據你 GUI 架構命名的報價區域

        # 呼叫 DLL 取得報價物件
        stock_data = SK.SKOSQuoteLib_GetStockByNoNineDigitLONG(strStockNo)

        #更新 UI（ OnUpDateDataQuote()）
        app.quote_frame.after(0, lambda: quote_ui.OnUpDateDataQuote(stock_data))
SK.OnNotifyOSQuoteLONG(on_OnNotifyOSQuoteLONG_message)

def on_OnNotifyOOQuoteLONG_message(strStockNo):
    app = MainApp.instance
    if app:
        quote_ui = app.quote_frame  # 根據你 GUI 架構命名的報價區域

        # 呼叫 DLL 取得報價物件
        stock_data = SK.SKOOQuoteLib_GetStockByNoLONG(strStockNo)

        #更新 UI（ OnUpDateDataQuote2()）
        app.quote_frame.after(0, lambda: quote_ui.OnUpDateDataQuote2(stock_data))
SK.OnNotifyOOQuoteLONG(on_OnNotifyOOQuoteLONG_message)

def on_OnNotifyOSTicks_message(strStockNo, nPtr, nDate, nTime, nClose, nQty):
    app = MainApp.instance
    if not app:
        return

    quote_ui = app.quote_frame
    strData = f"{strStockNo},{nPtr},{nDate} {nTime},{nClose},{nQty}"

    quote_ui.after(0, lambda: quote_ui.listTicksOS.insert("end", f"[OnNotifyOSTicks]{strData}"))
SK.OnNotifyOSTicks(on_OnNotifyOSTicks_message)

def on_OnNotifyOSBest10_message(strStockNo, nBestBid, nBestBidQty, nBestAsk, nBestAskQty):
    app = MainApp.instance
    if not app:
        return

    quote_ui = app.quote_frame

    # ➤ 呼叫 UI 執行緒內的更新函式
    quote_ui.after(0, lambda: quote_ui.UpdateBest10Grid(
        nBestBid, nBestBidQty, nBestAsk, nBestAskQty
    ))   
SK.OnNotifyOSBest10(on_OnNotifyOSBest10_message)

def on_OnNotifyOOTicks_message(strStockNo, nPtr, nDate, nTime, nClose, nQty):
    app = MainApp.instance
    if not app:
        return

    quote_ui = app.quote_frame
    strData = f"{strStockNo},{nPtr},{nDate} {nTime},{nClose},{nQty}"

    quote_ui.after(0, lambda: quote_ui.listTicksOO.insert("end", f"[OnNotifyOOTicks]{strData}"))
SK.OnNotifyOOTicks(on_OnNotifyOOTicks_message)

def on_OnNotifyOOBest10_message(strStockNo, nBestBid, nBestBidQty, nBestAsk, nBestAskQty):
    app = MainApp.instance
    if not app:
        return

    quote_ui = app.quote_frame

    # ➤ 呼叫 UI 執行緒內的更新函式
    quote_ui.after(0, lambda: quote_ui.UpdateBest10Grid2(
        nBestBid, nBestBidQty, nBestAsk, nBestAskQty
    ))   
SK.OnNotifyOOBest10(on_OnNotifyOOBest10_message)

def on_login_click():
    app = MainApp.instance  # 取得目前的 MainApp 實例
    login_ui = app.login_frame

    strLoginID=login_ui.textBoxUserID.get()
    strPassword=login_ui.textBoxPassword.get()
    nAuthorityFlag=login_ui.comboBoxAuthorityFlag.current()

    result = SK.Login(strLoginID, strPassword, nAuthorityFlag)

    # 顯示回傳訊息
    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[Login] 回傳值: {SK.GetMessage(result.Code)}"))

    # 更新帳號下拉選單
    if result.Code == 0:
        def update_accounts():
            login_ui.comboBoxTS["values"] = [f"{a.LoginID} {a.FullAccount}" for a in result.TSAccounts]
            login_ui.comboBoxOS["values"] = [f"{a.LoginID} {a.FullAccount}" for a in result.OSAccounts]
            login_ui.comboBoxTF["values"] = [f"{a.LoginID} {a.FullAccount}" for a in result.TFAccounts]
            login_ui.comboBoxOF["values"] = [f"{a.LoginID} {a.FullAccount}" for a in result.OFAccounts]

            # 設定預設選項
            if result.TSAccounts: login_ui.comboBoxTS.current(0)
            if result.OSAccounts: login_ui.comboBoxOS.current(0)
            if result.TFAccounts: login_ui.comboBoxTF.current(0)
            if result.OFAccounts: login_ui.comboBoxOF.current(0)

        login_ui.after(0, update_accounts)

def on_ManageServerConnection_click():
    app = MainApp.instance  # 取得目前的 MainApp 實例
    login_ui = app.login_frame

    strLoginID=login_ui.textBoxUserID.get()
    nStatus=login_ui.comboBoxStatus.current()
    nTargetType=login_ui.comboBoxTargetType.current()

    result = SK.ManageServerConnection(strLoginID, nStatus, nTargetType)

    # 顯示回傳訊息
    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[ManageServerConnection] 回傳值: {SK.GetMessage(result)}"))

def on_LoadCommodity_click():
    app = MainApp.instance  # 取得目前的 MainApp 實例
    login_ui = app.login_frame

    nMarketNo=login_ui.comboBoxnMarketNo.current()
    result = SK.LoadCommodity(nMarketNo)

    # 顯示回傳訊息
    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[LoadCommodity] 回傳值: {SK.GetMessage(result)}"))

def on_SendStockProxyOrder_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxTS.get()
    parts = selectedText.split(' ')  # 以空白分隔
    if len(parts) >= 2:
        loginID = parts[0]  # 第一部分就是登入ID
        account = parts[1]  # 第二部分就是帳號

    if order_ui.txtProxyStockNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strStockNo = order_ui.txtProxyStockNo.get().strip()

    if order_ui.ProxyOrderTypeBox.current() < 0:
        messagebox.showinfo("錯誤", "請選擇下單類別")
        return
    nORDERType = order_ui.ProxyOrderTypeBox.current() + 1

    if order_ui.ProxyPriceTypeBox.current() < 0:
        messagebox.showinfo("錯誤", "請選擇價格類別")
        return
    nPriceType = order_ui.ProxyPriceTypeBox.current() + 1

    if order_ui.ProxyTimeBox.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託時效")
        return
    nTimeInForce = order_ui.ProxyTimeBox.current()

    if order_ui.ProxyMarketBox.current() < 0:
        messagebox.showinfo("錯誤", "請選擇盤別")
        return
    nMarketType = order_ui.ProxyMarketBox.current()

    try:
        dPrice = float(order_ui.txtProxyStockPrice.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託價請輸入數字")
        return
    strPrice = order_ui.txtProxyStockPrice.get().strip()

    try:
        Qty = int(order_ui.txtStockQty.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    if order_ui.ProxyPriceMarkBox.current() < 0:
        messagebox.showinfo("錯誤", "請選擇價格旗標")
        return
    nPriceMark = order_ui.ProxyPriceMarkBox.current()

    OrderType = ""
    if nORDERType == 1:
        OrderType = "1"
    elif nORDERType == 2:
        OrderType = "2"
    elif nORDERType == 3:
        OrderType = "3"
    elif nORDERType == 4:
        OrderType = "4"
    elif nORDERType == 5:
        OrderType = "5"
    elif nORDERType == 6:
        OrderType = "6"
    elif nORDERType == 7:
        OrderType = "7"

    #loginID = order_ui.textBoxUserID.get()

    nCode, message = SK.SendStockProxyOrder(loginID, strStockNo, account, strPrice, OrderType,
                                            nPriceType, nTimeInForce, nMarketType, Qty)

    # 若要使用包含價格旗標的版本，請改成以下註解：
    # nCode, message = SK.SendStockProxyOrder(loginID, strStockNo, account, strPrice, OrderType,
    #                                         nPriceType, nTimeInForce, nMarketType, Qty, nPriceMark)

    # 顯示回傳訊息
    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SendStockProxyOrder]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendStockProxyAlter_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxTS.get()
    parts = selectedText.split(' ')  # 以空白分隔
    if len(parts) >= 2:
        loginID = parts[0]  # 第一部分就是登入ID
        account = parts[1]  # 第二部分就是帳號

    if order_ui.txtProxyStockNo2.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strStockNo = order_ui.txtProxyStockNo2.get().strip()

    if order_ui.ProxyOrderTypeBox2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇下單類別")
        return
    nORDERType = order_ui.ProxyOrderTypeBox2.current()

    if order_ui.ProxyPriceTypeBox2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇價格類別")
        return
    nPriceType = order_ui.ProxyPriceTypeBox2.current() + 1

    if order_ui.ProxyTimeBox2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託時效")
        return
    nTimeInForce = order_ui.ProxyTimeBox2.current()

    if order_ui.ProxyMarketBox2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇盤別")
        return
    nMarketType = order_ui.ProxyMarketBox2.current()

    try:
        dPrice = float(order_ui.txtProxyStockPrice2.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託價請輸入數字")
        return
    strPrice = order_ui.txtProxyStockPrice2.get().strip()

    try:
        Qty = int(order_ui.txtStockQty2.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    if order_ui.ProxyPriceMarkBox2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇價格旗標")
        return
    nPriceMark = order_ui.ProxyPriceMarkBox2.current()

    if order_ui.txtStockBookNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託書號")
        return
    strOrderNo = order_ui.txtStockBookNo.get().strip()

    if order_ui.txtStockSeqNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託序號")
        return
    strSeqNo = order_ui.txtStockSeqNo.get().strip()

    OrderType = ""
    if nORDERType == 0:
        OrderType = "0"
    elif nORDERType == 1:
        OrderType = "1"
    elif nORDERType == 2:
        OrderType = "2"

    # 若要使用包含價格旗標的版本，請改成以下註解：
    # nCode, message = SK.SendStockProxyAlter(loginID, strStockNo, account, strSeqNo, strOrderNo, strPrice, OrderType,
    #                                         nPriceType, nTimeInForce, nMarketType, Qty, nPriceMark)

    nCode, message = SK.SendStockProxyAlter(loginID, strStockNo, account, strSeqNo, strOrderNo, strPrice, OrderType,
                                            nPriceType, nTimeInForce, nMarketType, Qty)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SendStockProxyAlter]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendFutureProxyOrder_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ""
    account = ""
    selectedText = login_ui.comboBoxTF.get()
    parts = selectedText.split(' ')  # 以空白分隔
    if len(parts) >= 2:
        loginID = parts[0]  # 第一部分就是登入ID
        account = parts[1]  # 第二部分就是帳號

    if order_ui.txtFutureNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strFutureNo = order_ui.txtFutureNo.get().strip()

    if order_ui.txtProxyYM.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品年月")
        return
    strYM = order_ui.txtProxyYM.get().strip()

    if order_ui.boxProxyBS.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別")
        return
    nBS = order_ui.boxProxyBS.current()

    if order_ui.boxProxyCOND.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return
    nCOND = order_ui.boxProxyCOND.current()

    if order_ui.boxDayTrade.current() < 0:
        messagebox.showinfo("錯誤", "請選擇當沖與否")
        return
    nDayTrade = order_ui.boxDayTrade.current()

    try:
        dPrice = float(order_ui.txtFuturePrice.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託價請輸入數字")
        return
    strPrice = order_ui.txtFuturePrice.get().strip()

    try:
        nQty = int(order_ui.txtFutureQty.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    if order_ui.boxProxyPriceFlag.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委價類別")
        return
    nPriceFlag = order_ui.boxProxyPriceFlag.current()

    if order_ui.boxProxyORDERType.current() < 0:
        messagebox.showinfo("錯誤", "請選擇倉別")
        return
    nORDERType = order_ui.boxProxyORDERType.current()

    if order_ui.boxProxyPreOrder.current() < 0:
        messagebox.showinfo("錯誤", "請選擇盤別")
        return
    nPreOrder = order_ui.boxProxyPreOrder.current()

    strOrderType = ""
    if nORDERType == 0:
        strOrderType = "0"
    elif nORDERType == 1:
        strOrderType = "1"
    elif nORDERType == 2:
        strOrderType = "2"

    nCode, message = SK.SendFutureProxyOrder(
        loginID, account, strFutureNo, strYM, nBS, nPriceFlag, nDayTrade,
        strOrderType, nPreOrder, nQty, strPrice, nCOND
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SendFutureProxyOrder]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendFutureProxyAlter_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxTF.get()
    parts = selectedText.split(' ')  # 以空白分隔
    if len(parts) >= 2:
        loginID = parts[0]  # 第一部分就是登入ID
        account = parts[1]  # 第二部分就是帳號

    if order_ui.boxProxyCOND2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return
    nCOND = order_ui.boxProxyCOND2.current()

    if order_ui.boxProxyPreOrder2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇盤別")
        return
    nPreOrder = order_ui.boxProxyPreOrder2.current()

    if order_ui.boxProxyORDERType2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託類別")
        return
    nORDERType = order_ui.boxProxyORDERType2.current()

    strPrice = ""
    if nORDERType == 2:
        try:
            float(order_ui.txtProxyPrice2.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "委託價請輸入數字")
            return
        strPrice = order_ui.txtProxyPrice2.get().strip()

    nQty = 0
    if nORDERType == 0 or nORDERType == 1:
        try:
            nQty = int(order_ui.txtProxyQty2.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "委託量請輸入數字")
            return

    if order_ui.txtProxyOrderNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託書號")
        return
    strOrderNo = order_ui.txtProxyOrderNo.get().strip()

    if order_ui.txtProxySeqNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託序號")
        return
    strSeqNo = order_ui.txtProxySeqNo.get().strip()

    OrderType = ""
    if nORDERType == 0:
        OrderType = "0"
    elif nORDERType == 1:
        OrderType = "1"
    elif nORDERType == 2:
        OrderType = "2"

    nCode, message = SK.SendFutureProxyAlter(
        loginID, account, OrderType, strPrice, nPreOrder, nQty, nCOND, strOrderNo, strSeqNo
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SendFutureProxyAlter]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendOptionProxyOrder_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxTF.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.txtOptionNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strFutureNo = order_ui.txtOptionNo.get().strip()

    if order_ui.txtOptionYM.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品年月")
        return
    strYM = order_ui.txtOptionYM.get().strip()

    if order_ui.txtProxyStrike.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入履約價")
        return
    strStrike = order_ui.txtProxyStrike.get().strip()

    if order_ui.boxProxyCP.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣權")
        return
    nCP = order_ui.boxProxyCP.current()

    if order_ui.boxOptionBS.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別")
        return
    nBS = order_ui.boxOptionBS.current()

    if order_ui.boxOptionCOND.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return
    nCOND = order_ui.boxOptionCOND.current()

    if order_ui.boxORDERType.current() < 0:
        messagebox.showinfo("錯誤", "請選擇倉別")
        return
    nORDERType = order_ui.boxORDERType.current()

    strPrice = order_ui.txtOptionPrice.get().strip()
    try:
        if strPrice not in ["M", "P"]:
            float(strPrice)
    except ValueError:
        messagebox.showinfo("錯誤", "委託價請輸入數字")
        return

    try:
        nQty = int(order_ui.txtOptionQty.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    if order_ui.boxOptionDayTrade.current() < 0:
        messagebox.showinfo("錯誤", "請選擇是否當沖")
        return
    nDayTrade = order_ui.boxOptionDayTrade.current()

    if order_ui.boxPreOrder.current() < 0:
        messagebox.showinfo("錯誤", "請選擇盤別")
        return
    nPreOrder = order_ui.boxPreOrder.current()

    if order_ui.boxPriceFlag.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委價類別")
        return
    nPriceFlag = order_ui.boxPriceFlag.current()

    OrderType = ""
    if nORDERType == 0:
        OrderType = "0"
    elif nORDERType == 1:
        OrderType = "1"
    elif nORDERType == 2:
        OrderType = "2"

    nCode, message = SK.SendOptionProxyOrder(
        loginID, account, strFutureNo, strPrice, strYM, strStrike, OrderType,
        nPreOrder, nQty, nCP, nBS, nPriceFlag, nCOND, nDayTrade
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SendOptionProxyOrder]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendDuplexProxyOrder_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxTF.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.txtOptionNo1.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strFutureNo = order_ui.txtOptionNo1.get().strip()

    if order_ui.txtOptionNo2.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼2")
        return
    strFutureNo2 = order_ui.txtOptionNo2.get().strip()

    if order_ui.txtProxyYM1.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品年月")
        return
    strYM = order_ui.txtProxyYM1.get().strip()

    if order_ui.txtProxyYM2.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品年月2")
        return
    strYM2 = order_ui.txtProxyYM2.get().strip()

    if order_ui.txtProxyStrike1.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入履約價")
        return
    strStrike = order_ui.txtProxyStrike1.get().strip()

    if order_ui.txtProxyStrike2.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入履約價2")
        return
    strStrike2 = order_ui.txtProxyStrike2.get().strip()

    if order_ui.boxProxyCP1.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣權")
        return
    nCP = order_ui.boxProxyCP1.current()

    if order_ui.boxProxyCP2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣權2")
        return
    nCP2 = order_ui.boxProxyCP2.current()

    if order_ui.boxProxyBS1.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別")
        return
    nBS = order_ui.boxProxyBS1.current()

    if order_ui.boxProxyBS2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別2")
        return
    nBS2 = order_ui.boxProxyBS2.current()

    if order_ui.boxOptionCOND2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return
    nCOND = order_ui.boxOptionCOND2.current()

    if order_ui.boxORDERType2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇倉別")
        return
    nORDERType = order_ui.boxORDERType2.current()

    strPrice = order_ui.txtOptionPrice2.get().strip()
    try:
        if strPrice not in ["M", "P"]:
            float(strPrice)
    except ValueError:
        messagebox.showinfo("錯誤", "委託價請輸入數字")
        return

    try:
        nQty = int(order_ui.txtOptionQty2.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    if order_ui.boxDayTrade2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇是否當沖")
        return
    nDayTrade = order_ui.boxDayTrade2.current()

    if order_ui.boxPreOrder2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇盤別")
        return
    nPreOrder = order_ui.boxPreOrder2.current()

    if order_ui.boxPriceFlag2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委價類別")
        return
    nPriceFlag = order_ui.boxPriceFlag2.current()

    strOrderType = ""
    if nORDERType == 0:
        strOrderType = "0"
    elif nORDERType == 1:
        strOrderType = "1"
    elif nORDERType == 2:
        strOrderType = "2"

    nCode, message = SK.SendDuplexProxyOrder(
        loginID, account, strFutureNo, strPrice, strYM, strStrike, strYM2,
        strStrike2, strOrderType, nPreOrder, nQty, nCP, nBS, strFutureNo2,
        nCP2, nBS2, nPriceFlag, nCOND, nDayTrade
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SendDuplexProxyOrder]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendOptionProxyAlter_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxTF.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.boxProxyCOND3.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return
    nCOND = order_ui.boxProxyCOND3.current()

    if order_ui.boxProxyPreOrder3.current() < 0:
        messagebox.showinfo("錯誤", "請選擇盤別")
        return
    nPreOrder = order_ui.boxProxyPreOrder3.current()

    if order_ui.boxProxyORDERType3.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託類別")
        return
    nORDERType = order_ui.boxProxyORDERType3.current()

    strPrice = ""
    nQty = 0

    if nORDERType == 2:
        strPrice = order_ui.txtProxyPrice3.get().strip()
        try:
            float(strPrice)
        except ValueError:
            messagebox.showinfo("錯誤", "委託價請輸入數字")
            return

    if nORDERType in [0, 1]:
        try:
            nQty = int(order_ui.txtProxyQty3.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "委託量請輸入數字")
            return

    if order_ui.txtProxyOrderNo3.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託書號")
        return
    strOrderNo = order_ui.txtProxyOrderNo3.get().strip()

    if order_ui.txtProxySeqNo3.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託序號")
        return
    strSeqNo = order_ui.txtProxySeqNo3.get().strip()

    strOrderType = ""
    if nORDERType == 0:
        strOrderType = "0"
    elif nORDERType == 1:
        strOrderType = "1"
    elif nORDERType == 2:
        strOrderType = "2"

    nCode, message = SK.SendOptionProxyAlter(
        loginID, account, strOrderType, strPrice,
        nPreOrder, nQty, nCOND, strOrderNo, strSeqNo
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SendOptionProxyAlter]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendOverseaFutureProxyOrder_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxOF.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.txtProxyTradeNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入交易所代號")
        return
    strTradeName = order_ui.txtProxyTradeNo.get().strip()

    if order_ui.txtOFutureNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strStockNo = order_ui.txtOFutureNo.get().strip()

    if order_ui.txtProxyYearMonth.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入年月")
        return
    strYearMonth = order_ui.txtProxyYearMonth.get().strip()

    strOrder = order_ui.txtProxyOrder.get().strip()
    strOrderNumerator = order_ui.txtProxyOrderNumerator.get().strip()
    strOrderDeno = order_ui.txtProxyOrderDeno.get().strip()
    strTrigger = order_ui.txtProxyTrigger.get().strip()
    strTriggerNumerator = order_ui.txtProxyTriggerNumerator.get().strip()

    dPrice = 0.0
    idxSpecialTrade = order_ui.boxProxySpecialTradeType.current()

    if idxSpecialTrade in [0, 2]:
        try:
            float(strOrder)
        except ValueError:
            messagebox.showinfo("錯誤", "委託價請輸入數字")
            return

        try:
            float(strOrderNumerator)
        except ValueError:
            messagebox.showinfo("錯誤", "委託價分子請輸入數字")
            return

    if idxSpecialTrade in [2, 3]:
        try:
            float(strTrigger)
        except ValueError:
            messagebox.showinfo("錯誤", "觸發價請輸入數字")
            return

        try:
            float(strTriggerNumerator)
        except ValueError:
            messagebox.showinfo("錯誤", "觸發價分子請輸入數字")
            return

    try:
        nQty = int(order_ui.txtOFQty.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    nBuySell = order_ui.boxOFBS.current()
    if nBuySell < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別")
        return

    nNewClose = order_ui.boxProxyNewClose.current()
    if nNewClose < 0:
        messagebox.showinfo("錯誤", "請選擇倉別")
        return

    nDayTrade = order_ui.boxProxyFlag.current()
    if nDayTrade < 0:
        messagebox.showinfo("錯誤", "請選擇當沖與否")
        return

    nTradeType = order_ui.boxProxyPeriod.current()
    if nTradeType < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return

    if idxSpecialTrade < 0:
        messagebox.showinfo("錯誤", "請選擇委託類型")
        return
    nSpecialTradeType = idxSpecialTrade

    nCode, message = SK.SendOverseaFutureProxyOrder(
        loginID, account, strTradeName, strStockNo, strYearMonth,
        strOrder, strOrderNumerator, strTrigger, strTriggerNumerator,
        nBuySell, nNewClose, nDayTrade, nTradeType, nSpecialTradeType, nQty
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[SendOverseaFutureProxyOrder]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendOverseaFutureSpreadProxyOrder_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxOF.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.txtProxyTradeNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入交易所代號")
        return
    strTradeName = order_ui.txtProxyTradeNo.get().strip()

    if order_ui.txtOFutureNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strStockNo = order_ui.txtOFutureNo.get().strip()

    if order_ui.txtProxyYearMonth.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入年月")
        return
    strYearMonth = order_ui.txtProxyYearMonth.get().strip()

    if order_ui.txtProxyYearMonth2.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入年月(遠月)")
        return
    strYearMonth2 = order_ui.txtProxyYearMonth2.get().strip()

    dPrice = 0.0

    idxSpecialTrade = order_ui.boxProxySpecialTradeType.current()

    if idxSpecialTrade in [0, 2]:
        try:
            float(order_ui.txtProxyOrder.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "委託價請輸入數字")
            return
    strOrder = order_ui.txtProxyOrder.get().strip()

    if idxSpecialTrade in [0, 2]:
        try:
            float(order_ui.txtProxyOrderNumerator.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "委託價分子請輸入數字")
            return
    strOrderNumerator = order_ui.txtProxyOrderNumerator.get().strip()

    if idxSpecialTrade in [2, 3]:
        try:
            float(order_ui.txtProxyTrigger.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "觸發價請輸入數字")
            return
    strTrigger = order_ui.txtProxyTrigger.get().strip()

    if idxSpecialTrade in [2, 3]:
        try:
            float(order_ui.txtProxyTriggerNumerator.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "觸發價分子請輸入數字")
            return
    strTriggerNumerator = order_ui.txtProxyTriggerNumerator.get().strip()

    try:
        nQty = int(order_ui.txtOFQty.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    if order_ui.boxOFBS.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別")
        return
    nBuySell = order_ui.boxOFBS.current()

    if order_ui.boxProxyNewClose.current() < 0:
        messagebox.showinfo("錯誤", "請選擇倉別")
        return
    nNewClose = order_ui.boxProxyNewClose.current()

    if order_ui.boxProxyFlag.current() < 0:
        messagebox.showinfo("錯誤", "請選擇當沖與否")
        return
    nDayTrade = order_ui.boxProxyFlag.current()

    if order_ui.boxProxyPeriod.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return
    nTradeType = order_ui.boxProxyPeriod.current()

    if idxSpecialTrade < 0:
        messagebox.showinfo("錯誤", "請選擇委託類型")
        return
    nSpecialTradeType = idxSpecialTrade

    nCode, message = SK.SendOverseaFutureSpreadProxyOrder(
        loginID, account, strTradeName, strStockNo, strYearMonth, strYearMonth2,
        strOrder, strOrderNumerator, strTrigger, strTriggerNumerator,
        nBuySell, nNewClose, nDayTrade, nTradeType, nSpecialTradeType, nQty
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[SendOverseaFutureSpreadProxyOrder]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendOverseaFutureProxyAlter_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxOF.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.txtProxyTradeNo2.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入交易所代號")
        return
    strTradeName = order_ui.txtProxyTradeNo2.get().strip()

    if order_ui.txtOFutureNo2.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strStockNo = order_ui.txtOFutureNo2.get().strip()

    if order_ui.txtProxyYearMonth3.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入年月")
        return
    strYearMonth = order_ui.txtProxyYearMonth3.get().strip()

    strYearMonth2 = order_ui.txtProxyYearMonth4.get().strip()

    strOrder = order_ui.txtProxyOrder2.get().strip()
    strOrderNumerator = order_ui.txtProxyOrderNumerator2.get().strip()
    strOrderD = order_ui.txtProxyPriceD.get().strip()

    try:
        nQty = int(order_ui.txtOFQty2.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    if order_ui.boxProxyNewClose2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇倉別")
        return
    nNewClose = order_ui.boxProxyNewClose2.current()

    if order_ui.boxProxyPeriod2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return
    nTradeType = order_ui.boxProxyPeriod2.current()

    if order_ui.boxProxySpecialTradeType2.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託類型")
        return
    nSpecialTradeType = order_ui.boxProxySpecialTradeType2.current()

    if order_ui.boxFunCode.current() < 0:
        messagebox.showinfo("錯誤", "請選擇異動功能(刪單/減量/改價)")
        return
    nFunCode = order_ui.boxFunCode.current()

    if order_ui.txtOFBookNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託書號")
        return
    strOrderNo = order_ui.txtOFBookNo.get().strip()

    if order_ui.txtSeqNo4.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託序號")
        return
    strSeqNo = order_ui.txtSeqNo4.get().strip()

    nSpread = order_ui.BoxAlterSpread.current()

    if nSpread == 2:
        if order_ui.txt_Strike_proxy.get().strip() == "":
            messagebox.showinfo("錯誤", "請輸入履約價")
            return
    strStrikePrice = order_ui.txt_Strike_proxy.get().strip()

    if nSpread == 2:
        if order_ui.boxCallPutAlter.current() < 0:
            messagebox.showinfo("錯誤", "請選擇買賣權")
            return
    nCallPut = order_ui.boxCallPutAlter.current()

    nCode, message = SK.SendOverseaFutureProxyAlter(
        loginID, account, strTradeName, strStockNo,
        strYearMonth, strYearMonth2, strOrder, strOrderNumerator,
        strOrderD, nNewClose, nTradeType, nSpecialTradeType,
        nQty, strOrderNo, strSeqNo, nSpread, nFunCode,
        strStrikePrice, nCallPut
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[SendOverseaFutureProxyAlter]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendOverseaOptionProxyOrder_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxOF.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.txtOOTradeNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入交易所代號")
        return
    strTradeName = order_ui.txtOOTradeNo.get().strip()

    if order_ui.txtOONo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strStockNo = order_ui.txtOONo.get().strip()

    if order_ui.txtOOYM.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入年月")
        return
    strYearMonth = order_ui.txtOOYM.get().strip()

    dPrice = 0.0
    try:
        dPrice = float(order_ui.txtOOPrice.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託價請輸入數字")
        return
    strOrder = order_ui.txtOOPrice.get().strip()

    try:
        dPrice = float(order_ui.txtOONumerator.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託價分子請輸入數字")
        return
    strOrderNumerator = order_ui.txtOONumerator.get().strip()

    strOrderDeno = order_ui.txtOODeno.get().strip()
    strTrigger = order_ui.txtOOTrigger.get().strip()
    strTriggerNumerator = order_ui.txtOOTriggerNumerator.get().strip()
    strStrikePrice = order_ui.txtProxyStrikePrice.get().strip()

    try:
        nQty = int(order_ui.txtOOQty.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託量請輸入數字")
        return

    if order_ui.boxOOBS.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別")
        return
    nBuySell = order_ui.boxOOBS.current()

    if order_ui.boxOONewClose.current() < 0:
        messagebox.showinfo("錯誤", "請選擇倉別")
        return
    nNewClose = order_ui.boxOONewClose.current()

    if order_ui.boxOOFlag.current() < 0:
        messagebox.showinfo("錯誤", "請選擇當沖與否")
        return
    nDayTrade = order_ui.boxOOFlag.current()

    if order_ui.boxOOPeriod.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託條件")
        return
    nTradeType = order_ui.boxOOPeriod.current()

    if order_ui.boxOOSpecialTradeType.current() < 0:
        messagebox.showinfo("錯誤", "請選擇委託類型")
        return
    nSpecialTradeType = order_ui.boxOOSpecialTradeType.current()

    if order_ui.boxProxyCallPut.current() < 0:
        messagebox.showinfo("錯誤", "請選擇CALL PUT")
        return
    nCallPut = order_ui.boxProxyCallPut.current()

    nCode, message = SK.SendOverseaOptionProxyOrder(
        loginID, account, strTradeName, strStockNo, strYearMonth,
        strOrder, strOrderNumerator, strOrderDeno, strTrigger, strTriggerNumerator,
        nBuySell, nNewClose, nDayTrade, nTradeType, nSpecialTradeType,
        strStrikePrice, nCallPut, nQty
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[SendOverseaOptionProxyOrder]回傳值: {SK.GetMessage(nCode)} {message}"))

def on_SendForeignStockProxyOrder_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxOS.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.boxProxyAccountType.current() < 0:
        messagebox.showinfo("錯誤", "請選擇專戶別")
        return
    nAccountType = order_ui.boxProxyAccountType.current() + 1

    if order_ui.boxProxyExchange.current() < 0:
        messagebox.showinfo("錯誤", "請選擇交易所")
        return
    exchange_idx = order_ui.boxProxyExchange.current()
    exchange_dict = {
        0: "US",
        1: "HK",
        2: "JP",
        3: "SP",
        4: "SG",
        5: "SA",
        6: "HA",
    }
    strExchangeNo = exchange_dict.get(exchange_idx, "")

    if order_ui.boxProxyBidAsk.current() == 0 and order_ui.boxProxyCurrency1.current() < 0:
        messagebox.showinfo("錯誤", "買單請至少選擇扣款幣別 1")
        return

    strCurrency1 = order_ui.boxProxyCurrency1.get()
    strCurrency2 = order_ui.boxProxyCurrency2.get()
    strCurrency3 = order_ui.boxProxyCurrency3.get()

    if order_ui.txtProxyOStockNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strStockNo = order_ui.txtProxyOStockNo.get().strip()

    if order_ui.boxProxyBidAsk.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別")
        return
    nBidAsk = order_ui.boxProxyBidAsk.current()

    try:
        dPrice = float(order_ui.txtProxyPrice.get().strip())
    except ValueError:
        messagebox.showinfo("錯誤", "委託價請輸入數字")
        return
    strPrice = order_ui.txtProxyPrice.get().strip()

    if nBidAsk == 1 and strExchangeNo == "US":
        if order_ui.boxProxyTradeType.current() < 0:
            messagebox.showinfo("錯誤", "請選擇庫存別")
            return
        nTradeType = order_ui.boxProxyTradeType.current() + 1
    else:
        nTradeType = 0 if order_ui.boxProxyTradeType.current() < 0 else order_ui.boxProxyTradeType.current() + 1

    if nBidAsk == 1 and strExchangeNo == "US" and nTradeType == 2:
        try:
            dQty = float(order_ui.txtProxyQty.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "委託量請輸入數字")
            return
    else:
        try:
            nQty = int(order_ui.txtProxyQty.get().strip())
        except ValueError:
            messagebox.showinfo("錯誤", "委託量請輸入整數數字")
            return

    strProxyQty = order_ui.txtProxyQty.get().strip()

    nCode, message = SK.SendForeignStockProxyOrder(
        loginID, account, strStockNo, strExchangeNo, strPrice,
        strCurrency1, strCurrency2, strCurrency3, strProxyQty,
        nAccountType, nBidAsk + 1, nTradeType
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[SendForeignStockProxyOrder]回傳值: {SK.GetMessage(nCode)} {message}"
    ))

def on_SendForeignStockProxyCancel_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxOS.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.boxProxyCancelExchange.current() < 0:
        messagebox.showinfo("錯誤", "請選擇交易所")
        return

    exchange_idx = order_ui.boxProxyCancelExchange.current()
    exchange_dict = {
        0: "US",
        1: "HK",
        2: "JP",
        3: "SP",
        4: "SG",
        5: "SA",
        6: "HA",
    }
    strExchangeNo = exchange_dict.get(exchange_idx, "")

    if order_ui.txtProxyOStockNo2.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入商品代碼")
        return
    strStockNo = order_ui.txtProxyOStockNo2.get().strip()

    if order_ui.txtProxyCancelSeqNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託序號")
        return
    strSeqNo = order_ui.txtProxyCancelSeqNo.get().strip()

    if order_ui.txtProxyCancelBookNo.get().strip() == "":
        messagebox.showinfo("錯誤", "請輸入委託書號")
        return
    strOrderNo = order_ui.txtProxyCancelBookNo.get().strip()

    nCode, message = SK.SendForeignStockProxyCancel(
        loginID, account, strStockNo, strExchangeNo, strSeqNo, strOrderNo
    )

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[SendForeignStockProxyCancel]回傳值: {SK.GetMessage(nCode)} {message}"
    ))

def on_RequestStockList_click():
    app = MainApp.instance
    quote_ui = app.quote_frame

    quote_ui.StockList.delete(0, tk.END)

    if quote_ui.MarketNo_txt.get().strip() == "":
        messagebox.showinfo("提示", "請輸入市場代碼")
        return

    nMarketNo = int(quote_ui.MarketNo_txt.get().strip())
    parser = SK.RequestStockList(nMarketNo)
    a = parser.RawData()
    print(a)
    # 全部商品清單
    for result in parser.AllTypeLists:
        quote_ui.StockList.insert(tk.END, f"【類別:{result.TypeNo},{result.TypeName}】")
        for item in result.Items:
            quote_ui.StockList.insert(tk.END, f"  {item.strQuoteCode},{item.strStockName},{item.strOrderCode},{item.strExpiryDate}")

    # 特定類別
    try:
        typeNo = int(quote_ui.TypeNo_txt.get())
    except ValueError:
        typeNo = -1

    result2 = parser.GetTypeNo(typeNo)
    if result2:
        quote_ui.StockList.insert(tk.END, f"【%{result2.TypeNo}% {result2.TypeName}】")
        for item in result2.Items:
            quote_ui.StockList.insert(tk.END, f"  {item.strQuoteCode},{item.strStockName},{item.strOrderCode},{item.strExpiryDate}")
    else:
        quote_ui.StockList.insert(tk.END, f"查無 TypeNo {typeNo}")

    # 取得所有分類資訊（如 "1水泥", "2食品"）
    AllType = "".join(parser.GetAllType())

def on_SKQuoteLib_RequestStocks_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtStocks.get().strip()  # 對應 txtStocks.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入股票代碼")
        return

    # ➤ 清除 Treeview 資料
    grid = quote_ui.gridStocks
    for item in grid.get_children():
        grid.delete(item)

    nCode = SK.SKQuoteLib_RequestStocks(stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKQuoteLib_RequestStocks] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKQuoteLib_RequestStocksOddLot_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtStocks2.get().strip()  # 對應 txtStocks2.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入股票代碼")
        return
    
    # ➤ 清除 Treeview 資料
    grid = quote_ui.gridStocks
    for item in grid.get_children():
        grid.delete(item)

    nCode = SK.SKQuoteLib_RequestStocksOddLot(stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKQuoteLib_RequestStocksOddLot] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKQuoteLib_CancelRequestStocks_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtStocks.get().strip()  # 對應 txtStocks.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入股票代碼")
        return

    nCode = SK.SKQuoteLib_CancelRequestStocks(stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKQuoteLib_CancelRequestStocks] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKQuoteLib_RequestTicks_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtTick.get().strip()  # 對應 txtTick.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入股票代碼")
        return

    ItemNo = int(quote_ui.txtItemNoQuote.get())
    nCode = SK.SKQuoteLib_RequestTicks(ItemNo, stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKQuoteLib_RequestTicks] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKQuoteLib_RequestTicksOddLot_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtTick.get().strip()  # 對應 txtTick.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入股票代碼")
        return

    ItemNo = int(quote_ui.txtItemNoQuote.get())
    nCode = SK.SKQuoteLib_RequestTicksOddLot(ItemNo, stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKQuoteLib_RequestTicksOddLot] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKQuoteLib_CancelRequestTicks_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtTick.get().strip()  # 對應 txtTick.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入股票代碼")
        return

    nCode = SK.SKQuoteLib_CancelRequestTicks(stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKQuoteLib_CancelRequestTicks] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKOSQuoteLib_RequestStocks_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtStocksOS.get().strip()  # 對應 txtStocksOS.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入商品代碼")
        return

    # ➤ 清除 Treeview 資料
    grid = quote_ui.gridStocksOS
    for item in grid.get_children():
        grid.delete(item)

    nCode = SK.SKOSQuoteLib_RequestStocks(stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKOSQuoteLib_RequestStocks] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKOOQuoteLib_RequestStocks_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtStocksOO.get().strip()  # 對應 txtStocksOS.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入商品代碼")
        return

    # ➤ 清除 Treeview 資料
    grid = quote_ui.gridStocksOO
    for item in grid.get_children():
        grid.delete(item)

    nCode = SK.SKOOQuoteLib_RequestStocks(stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKOOQuoteLib_RequestStocks] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKOSQuoteLib_RequestTicks_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtTickOS.get().strip()  # 對應 txtTickOS.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入股票代碼")
        return

    ItemNo = int(quote_ui.txtItemQuoteOS.get())
    nCode = SK.SKOSQuoteLib_RequestTicks(ItemNo, stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKOSQuoteLib_RequestTicks] 回傳值: {SK.GetMessage(nCode)}"))

def on_SKOOQuoteLib_RequestTicks_click():
    app = MainApp.instance
    quote_ui = app.quote_frame
    login_ui = app.login_frame

    stock_text = quote_ui.txtTickOO.get().strip()  # 對應 txtTickOO.Text.Trim()
    if not stock_text:
        messagebox.showinfo("提示", "請輸入股票代碼")
        return

    ItemNo = int(quote_ui.txtItemQuoteOO.get())
    nCode = SK.SKOOQuoteLib_RequestTicks(ItemNo, stock_text)

    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert("end", f"[SKOOQuoteLib_RequestTicks] 回傳值: {SK.GetMessage(nCode)}"))

def on_GetForeignBlock_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ''
    account = ''
    selectedText = login_ui.comboBoxOS.get()
    parts = selectedText.split(' ')
    if len(parts) >= 2:
        loginID = parts[0]
        account = parts[1]

    if order_ui.comboBoxGetForeignBlocknFunc.current() < 0:
        messagebox.showinfo("錯誤", "請選擇幣別")
        return
    nCurrencyType = order_ui.comboBoxGetForeignBlocknFunc.current()

    result = SK.GetForeignBlock(loginID, account, nCurrencyType)

    # 顯示回傳訊息
    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[GetForeignBlock]回傳值: {result.StatusCode} {result.Message}"
    ))

    # 直接逐筆列出每筆帳務資料
    if result.StatusCode == 0 and len(result.Blocks) > 0:
        for block in result.Blocks:
            login_ui.after(0, lambda b=block: login_ui.listOnReplyMessage.insert(
                "end",
                f"銀行: {b.BankName.decode('ansi')} "
                f"({b.BankCode.decode('ansi')}-"
                f"{b.BankBranchCode.decode('ansi')}-"
                f"{b.BankAccount.decode('ansi')})"
            ))

            login_ui.after(0, lambda b=block: login_ui.listOnReplyMessage.insert(
                "end",
                f"幣別: {b.Currency.decode('ansi')}, "
                f"圈存金額: {b.UnpayableAmt.decode('ansi')}, "
                f"買進未扣款: {b.UnpayableBuy.decode('ansi')}, "
                f"股市委買: {b.TodayOrder.decode('ansi')}, "
                f"匯出換匯金額: {b.OutAmt.decode('ansi')}, "
                f"可解圈金額: {b.UnblockAmt.decode('ansi')}, "
                f"基金委買: {b.FundOrderAmt.decode('ansi')}"
            ))

            login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
                "end", "--------------------------------------------------"
            ))
    else:
        login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
            "end", "[GetForeignBlock]沒有資料或回傳錯誤"
        ))  

def on_WithDraw_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    strLoginID = login_ui.textBoxUserID.get()
    strAccountOut = ""
    strAccountIn = ""
    nTypeOut = 0
    nTypeIn = 0
    nCurrency = 0
    strDollars = ""
    strPWD = ""

    if order_ui.boxTypeOut.current() < 0:
        messagebox.showinfo("錯誤", "請選擇轉出類別")
        return
    nTypeOut = order_ui.boxTypeOut.current()

    if order_ui.textBoxAccountOut.get() == "":
        messagebox.showinfo("錯誤", "請輸入轉出帳號")
        return
    strAccountOut = order_ui.textBoxAccountOut.get()

    if order_ui.boxTypeIn.current() < 0:
        messagebox.showinfo("錯誤", "請選擇轉入類別")
        return
    nTypeIn = order_ui.boxTypeIn.current()

    if order_ui.textBoxAccountIn.get() == "":
        messagebox.showinfo("錯誤", "請輸入轉入帳號")
        return
    strAccountIn = order_ui.textBoxAccountIn.get()

    if order_ui.boxCurrency.current() < 0:
        messagebox.showinfo("錯誤", "請選擇幣別")
        return
    nCurrency = order_ui.boxCurrency.current()

    if order_ui.txtDollars.get() == "":
        messagebox.showinfo("錯誤", "請輸入互轉金額")
        return
    strDollars = order_ui.txtDollars.get()

    if order_ui.txtPWD.get() == "":
        messagebox.showinfo("錯誤", "請輸入出金密碼")
        return
    strPWD = order_ui.txtPWD.get()
    # listOnReplyMessage 是用來顯示回應訊息的 Listbox 控件
    # 參數設定程式碼省略(可參考完整Python範例程式)

    # 呼叫 API
    result = SK.WithDraw(strLoginID, strAccountOut, nTypeOut,
                         strAccountIn, nTypeIn, nCurrency,
                         strDollars, strPWD)

    # 顯示回傳訊息
    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[WithDraw]回傳值: {result[0]} {result[1]}"
    ))

def on_SendTFOffset_click():
    app = MainApp.instance
    order_ui = app.order_frame
    login_ui = app.login_frame

    loginID = ""
    account = ""
    selectedText = login_ui.comboBoxTF.get()
    parts = selectedText.split(' ')  # 以空白分隔
    if len(parts) >= 2:
        loginID = parts[0]  # 第一部分就是登入ID
        account = parts[1]  # 第二部分就是帳號
    
    nBidAsk = 0
    nQty = 0
    nQty_2 = 0
    nQty_3 = 0
    nCommodity = 0
    strYearMonth = ''

    if order_ui.txtOffsetNewYearMonth.get() == "":
        messagebox.showinfo("錯誤", "請輸入年月")
        return
    strYearMonth = order_ui.txtOffsetNewYearMonth.get()

    if order_ui.CommodityBoxNew.current() < 0:
        messagebox.showinfo("錯誤", "請選擇互抵商品")
        return
    nCommodity = order_ui.CommodityBoxNew.current()

    if order_ui.boxOffsetNewBuySell.current() < 0:
        messagebox.showinfo("錯誤", "請選擇買賣別")
        return
    nBidAsk = order_ui.boxOffsetNewBuySell.current()

    if order_ui.txtOffsetNewQty.get() == "":
        messagebox.showinfo("錯誤", "委託量1請輸入數字")
        return
    nQty = int(order_ui.txtOffsetNewQty.get())

    if order_ui.txtOffsetNewQty_2.get() == "":
        messagebox.showinfo("錯誤", "委託量2請輸入數字")
        return
    nQty_2 = int(order_ui.txtOffsetNewQty_2.get())

    if order_ui.txtOffsetNewQty_3.get() == "":
        messagebox.showinfo("錯誤", "委託量3請輸入數字")
        return
    nQty_3 = int(order_ui.txtOffsetNewQty_3.get())

    # listOnReplyMessage 是用來顯示回應訊息的 Listbox 控件
    # 參數設定程式碼省略(可參考完整Python範例程式)

    # 呼叫 API
    nCode, message = SK.SendTFOffset(loginID, account, nCommodity,
                         strYearMonth, nBidAsk, nQty,
                         nQty_2, nQty_3)

    # 顯示回傳訊息
    login_ui.after(0, lambda: login_ui.listOnReplyMessage.insert(
        "end", f"[SendTFOffset]回傳值: {SK.GetMessage(nCode)} {message}"
    ))
    
if __name__ == "__main__":
    app = MainApp()

    # 綁定事件
    app.login_frame.buttonSKCenterLib_Login.config(command=on_login_click)
    app.login_frame.buttonManageServerConnection.config(command=on_ManageServerConnection_click)
    app.login_frame.buttonLoadCommodity.config(command=on_LoadCommodity_click)

    app.order_frame.btnSendStockProxyOrder.config(command=on_SendStockProxyOrder_click)
    app.order_frame.btnSendStockProxyAlter.config(command=on_SendStockProxyAlter_click)
    app.order_frame.btnSendProxyFutureOrderCLR.config(command=on_SendFutureProxyOrder_click)
    app.order_frame.btnProxyFutureAlter.config(command=on_SendFutureProxyAlter_click)
    app.order_frame.btnSendProxyOptionOrder.config(command=on_SendOptionProxyOrder_click)
    app.order_frame.btnSendProxyDuplexOrder.config(command=on_SendDuplexProxyOrder_click)
    app.order_frame.btnProxyOptionAlter.config(command=on_SendOptionProxyAlter_click)
    app.order_frame.btnSendOverseaFutureProxyOrder.config(command=on_SendOverseaFutureProxyOrder_click)

    app.order_frame.btnSendOverseaFutureSpreadProxyOrder.config(command=on_SendOverseaFutureSpreadProxyOrder_click)
    app.order_frame.btnSendOverseaFutureProxyAlter.config(command=on_SendOverseaFutureProxyAlter_click)
    app.order_frame.btnSendOverseaOptionProxyOrder.config(command=on_SendOverseaOptionProxyOrder_click)
    app.order_frame.btnSendForeignStockProxyOrder.config(command=on_SendForeignStockProxyOrder_click)
    app.order_frame.btnProxyCancelForeignOrderBySeqNo.config(command=on_SendForeignStockProxyCancel_click)

    app.quote_frame.RequestStockListBtn.config(command=on_RequestStockList_click)
    app.quote_frame.btnQueryStocks.config(command=on_SKQuoteLib_RequestStocks_click)
    app.quote_frame.btnQueryOddLot.config(command=on_SKQuoteLib_RequestStocksOddLot_click)
    app.quote_frame.btnCancelStocks.config(command=on_SKQuoteLib_CancelRequestStocks_click)

    app.quote_frame.btnTicks.config(command=on_SKQuoteLib_RequestTicks_click)
    app.quote_frame.btnTicks_OddLot.config(command=on_SKQuoteLib_RequestTicksOddLot_click)
    app.quote_frame.btnTickStop.config(command=on_SKQuoteLib_CancelRequestTicks_click)

    app.quote_frame.btnQueryStocksOS.config(command=on_SKOSQuoteLib_RequestStocks_click)
    app.quote_frame.btnQueryStocksOO.config(command=on_SKOOQuoteLib_RequestStocks_click)

    app.quote_frame.btnTicksOS.config(command=on_SKOSQuoteLib_RequestTicks_click)
    app.quote_frame.btnTicksOO.config(command=on_SKOOQuoteLib_RequestTicks_click)

    app.order_frame.buttonGetForeignBlock.config(command=on_GetForeignBlock_click)
    app.order_frame.btnSend.config(command=on_WithDraw_click)
    app.order_frame.btnSendTFOffset.config(command=on_SendTFOffset_click)


    app.mainloop()
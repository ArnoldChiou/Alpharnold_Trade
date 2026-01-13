import Global
import comtypes.gen.SKCOMLib as sk

skC = Global.skC
skO = Global.skO
skR = Global.skR
skQ = Global.skQ
skOSQ = Global.skOSQ
skOOQ = Global.skOOQ

# 畫視窗用物件
from tkinter import *
from tkinter.ttk import *

# 載入其他物件
#from StopLossOrder import FutureStopLossOrder
#from StopLossOrder import MovingStopLossOrder
#from StopLossOrder import OptionStopLossOrder
#from StopLossOrder import FutureOCOOrder
#from StopLossOrder import CancelStopLossOrder

import Config
import MessageControl

#----------------------------------------------------------------------------------------------------------------------------------------------------
# 期貨停損委託
class FutureStopLossOrder(Frame):
    def __init__(self, master=None, information=None):
        Frame.__init__(self)
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = '',
        )

        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="期貨停損委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 0, row = 1, padx = 5, pady = 3)

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 1, row = 0)
            # 輸入框
        boxBuySell = Combobox(frame, width = 5, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 1, row = 1, padx = 5)

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 2, row = 0)
            # 輸入框
        boxPeriod = Combobox(frame, width = 8, state='readonly')
        boxPeriod['values'] = Config.PERIODSET['future']
        boxPeriod.grid(column = 2, row = 1, padx = 5)

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 3, row = 0)
            # 輸入框
        boxNewClose = Combobox(frame, width = 5, state='readonly')
        boxNewClose['values'] = Config.NEWCLOSESET['future']
        boxNewClose.grid(column = 3, row = 1, padx = 5)

        # 當沖與否
        lbFlag = Label(frame, style="Pink.TLabel", text = "當沖與否")
        lbFlag.grid(column = 4, row = 0)
            # 輸入框
        boxFlag = Combobox(frame, width = 8, state='readonly')
        boxFlag['values'] = Config.FLAGSET['future']
        boxFlag.grid(column = 4, row = 1, padx = 5)

        # 委託價
        lbPrice = Label(frame, style="Pink.TLabel", text = "委託價")
        lbPrice.grid(column = 5, row = 0)
            # 輸入框
        txtPrice = Entry(frame, width = 10)
        txtPrice.grid(column = 5, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 6, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 6, row = 1, padx = 5)

        # 觸發價
        lbTrigger = Label(frame, style="Pink.TLabel", text = "觸發價")
        lbTrigger.grid(column = 7, row = 0)
            # 輸入框
        txtTrigger = Entry(frame, width = 10)
        txtTrigger.grid(column = 7, row = 1, padx = 5)

        # 盤別
        lbReserved = Label(frame, style="Pink.TLabel", text = "盤別")
        lbReserved.grid(column = 8, row = 0)
            # 輸入框
        boxReserved = Combobox(frame, width = 8, state='readonly')
        boxReserved['values'] = Config.RESERVEDSET
        boxReserved.grid(column = 8, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 9, row =  0, padx = 5)

        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 9, row =  1, padx = 5)

        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxNewClose'] = boxNewClose
        self.__dOrder['boxFlag'] = boxFlag
        self.__dOrder['txtPrice'] = txtPrice
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['txtTrigger'] = txtTrigger
        self.__dOrder['boxReserved'] = boxReserved


    # 4.下單送出
    # sBuySell, sTradeType, sNewClose, sDayTrade, sReserved
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxPeriod'].get() == "ROD":
                sTradeType = 0
            elif self.__dOrder['boxPeriod'].get() == "IOC":
                sTradeType = 1
            elif self.__dOrder['boxPeriod'].get() == "FOK":
                sTradeType = 2

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0
            elif self.__dOrder['boxNewClose'].get() == "平倉":
                sNewClose = 1
            elif self.__dOrder['boxNewClose'].get() == "自動":
                sNewClose = 2

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

            if self.__dOrder['boxReserved'].get() == "盤中":
                sReserved = 0
            elif self.__dOrder['boxReserved'].get() == "T盤預約":
                sReserved = 1

            # 建立下單用的參數(FUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.FUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 買賣別
            oOrder.sBuySell = sBuySell
            # ROD、IOC、FOK
            oOrder.sTradeType = sTradeType
            # 新倉、平倉、自動
            oOrder.sNewClose = sNewClose
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # 委託價
            oOrder.bstrPrice = self.__dOrder['txtPrice'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            # 盤中、T盤預約
            oOrder.sReserved = sReserved

            message, m_nCode = skO.SendFutureStopLossOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendFutureStopLossOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode ==0:                    
                        strMsg = "期貨停損委託: " + str(message)
                        self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 期貨移動停損委託
class MovingStopLossOrder(Frame):
    def __init__(self, master=None, information=None):
        Frame.__init__(self)
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = '',
        )

        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="期貨移動停損委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 1, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 0, row = 1, padx = 5, pady = 3)

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 1, row = 0)
            # 輸入框
        boxBuySell = Combobox(frame, width = 5, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 1, row = 1, padx = 5)

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 2, row = 0)
            # 輸入框
        boxPeriod = Combobox(frame, width = 8, state='readonly')
        boxPeriod['values'] = Config.PERIODSET['moving_stop_loss']
        boxPeriod.grid(column = 2, row = 1, padx = 5)

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 3, row = 0)
            # 輸入框
        boxNewClose = Combobox(frame, width = 5, state='readonly')
        boxNewClose['values'] = Config.NEWCLOSESET['future']
        boxNewClose.grid(column = 3, row = 1, padx = 5)

        # 當沖與否
        lbFlag = Label(frame, style="Pink.TLabel", text = "當沖與否")
        lbFlag.grid(column = 4, row = 0)
            # 輸入框
        boxFlag = Combobox(frame, width = 8, state='readonly')
        boxFlag['values'] = Config.FLAGSET['future']
        boxFlag.grid(column = 4, row = 1, padx = 5)

        # 移動點數
        lbMovingPoint = Label(frame, style="Pink.TLabel", text = "移動點數")
        lbMovingPoint.grid(column = 5, row = 0)
            # 輸入框
        txtMovingPoint = Entry(frame, width = 10)
        txtMovingPoint.grid(column = 5, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 6, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 6, row = 1, padx = 5)

        # 觸發價
        lbTrigger = Label(frame, style="Pink.TLabel", text = "觸發價")
        lbTrigger.grid(column = 7, row = 0)
            # 輸入框
        txtTrigger = Entry(frame, width = 10)
        txtTrigger.grid(column = 7, row = 1, padx = 5)

        # 盤別
        lbReserved = Label(frame, style="Pink.TLabel", text = "盤別")
        lbReserved.grid(column = 8, row = 0)
            # 輸入框
        boxReserved = Combobox(frame, width = 8, state='readonly')
        boxReserved['values'] = Config.RESERVEDSET
        boxReserved.grid(column = 8, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 9, row =  0, padx = 5)

        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 9, row =  1, padx = 5)

        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxNewClose'] = boxNewClose
        self.__dOrder['boxFlag'] = boxFlag
        self.__dOrder['txtMovingPoint'] = txtMovingPoint
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['txtTrigger'] = txtTrigger
        self.__dOrder['boxReserved'] = boxReserved

    # 4.下單送出
    # sBuySell, sTradeType, sNewClose, sDayTrade, sReserved
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxPeriod'].get() == "IOC":
                sTradeType = 1
            elif self.__dOrder['boxPeriod'].get() == "FOK":
                sTradeType = 2

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0
            elif self.__dOrder['boxNewClose'].get() == "平倉":
                sNewClose = 1
            elif self.__dOrder['boxNewClose'].get() == "自動":
                sNewClose = 2

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

            if self.__dOrder['boxReserved'].get() == "盤中":
                sReserved = 0
            elif self.__dOrder['boxReserved'].get() == "T盤預約":
                sReserved = 1

            # 建立下單用的參數(FUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.FUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 買賣別
            oOrder.sBuySell = sBuySell
            # ROD、IOC、FOK
            oOrder.sTradeType = sTradeType
            # 新倉、平倉、自動
            oOrder.sNewClose = sNewClose
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # 移動點數
            oOrder.bstrMovingPoint = self.__dOrder['txtMovingPoint'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            # 盤中、T盤預約
            oOrder.sReserved = sReserved

            message, m_nCode = skO.SendMovingStopLossOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendMovingStopLossOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode ==0:                    
                    strMsg = "期貨移動停損委託: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 選擇權停損委託
class OptionStopLossOrder(Frame):
    def __init__(self, master=None, information=None):
        Frame.__init__(self)
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = '',
        )

        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="選擇權停損委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 2, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 0, row = 1, padx = 5, pady = 3)

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 1, row = 0)
        # 輸入框
        boxBuySell = Combobox(frame, width = 5, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 1, row = 1, padx = 5)

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 2, row = 0)
        # 輸入框
        boxPeriod = Combobox(frame, width = 8, state='readonly')
        boxPeriod['values'] = Config.PERIODSET['future']
        boxPeriod.grid(column = 2, row = 1, padx = 5)

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 3, row = 0)
            # 輸入框
        boxNewClose = Combobox(frame, width = 5, state='readonly')
        boxNewClose['values'] = Config.NEWCLOSESET['future']
        boxNewClose.grid(column = 3, row = 1, padx = 5)

        Label(frame, style="PinkFiller.TLabel", text = "_________").grid(column = 4, row = 0, padx = 7)

        # 委託價
        lbPrice = Label(frame, style="Pink.TLabel", text = "委託價")
        lbPrice.grid(column = 5, row = 0)
            # 輸入框
        txtPrice = Entry(frame, width = 10)
        txtPrice.grid(column = 5, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 6, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 6, row = 1, padx = 5)

        # 觸發價
        lbTrigger = Label(frame, style="Pink.TLabel", text = "觸發價")
        lbTrigger.grid(column = 7, row = 0)
            # 輸入框
        txtTrigger = Entry(frame, width = 10)
        txtTrigger.grid(column = 7, row = 1, padx = 5)

        # 盤別
        lbReserved = Label(frame, style="Pink.TLabel", text = "盤別")
        lbReserved.grid(column = 8, row = 0)
            # 輸入框
        boxReserved = Combobox(frame, width = 8, state='readonly')
        boxReserved['values'] = Config.RESERVEDSET
        boxReserved.grid(column = 8, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 9, row =  0, padx = 5)

        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 9, row =  1, padx = 5)

        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxNewClose'] = boxNewClose
        self.__dOrder['txtPrice'] = txtPrice
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['txtTrigger'] = txtTrigger
        self.__dOrder['boxReserved'] = boxReserved

    # 4.下單送出
    # sBuySell, sTradeType, sNewClose, sReserved
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxPeriod'].get() == "ROD":
                sTradeType = 0
            elif self.__dOrder['boxPeriod'].get() == "IOC":
                sTradeType = 1
            elif self.__dOrder['boxPeriod'].get() == "FOK":
                sTradeType = 2

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0
            elif self.__dOrder['boxNewClose'].get() == "平倉":
                sNewClose = 1
            elif self.__dOrder['boxNewClose'].get() == "自動":
                sNewClose = 2

            if self.__dOrder['boxReserved'].get() == "盤中":
                sReserved = 0
            elif self.__dOrder['boxReserved'].get() == "T盤預約":
                sReserved = 1

            # 建立下單用的參數(FUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.FUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 買賣別
            oOrder.sBuySell = sBuySell
            # ROD、IOC、FOK
            oOrder.sTradeType = sTradeType
            # 新倉、平倉、自動
            oOrder.sNewClose = sNewClose
            # 委託價
            oOrder.bstrPrice = self.__dOrder['txtPrice'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            # 盤中、T盤預約
            oOrder.sReserved = sReserved

            message, m_nCode = skO.SendOptionStopLossOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendOptionStopLossOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode ==0:                    
                        strMsg = "選擇權停損委託: " + str(message)
                        self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 期貨OCO委託
class FutureOCOOrder(Frame):
    def __init__(self, master=None, information=None):
        Frame.__init__(self)
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = '',
        )

        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="期貨OCO委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 3, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')
        # frame.grid_columnconfigure(7, minsize = 10)

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 0, row = 1, rowspan = 2, padx = 5, pady = 3)

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 1, row = 0)
            # 輸入框
        boxBuySell = Combobox(frame, width = 5, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 1, row = 1, padx = 5)

        # 買賣別2
            # 輸入框
        boxBuySell2 = Combobox(frame, width = 5, state='readonly')
        boxBuySell2['values'] = Config.BUYSELLSET
        boxBuySell2.grid(column = 1, row = 2, padx = 5)

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 2, row = 0)
            # 輸入框
        boxPeriod = Combobox(frame, width = 8, state='readonly')
        boxPeriod['values'] = Config.PERIODSET['future']
        boxPeriod.grid(column = 2, row = 1, rowspan = 2, padx = 5)

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 3, row = 0)
            # 輸入框
        boxNewClose = Combobox(frame, width = 5, state='readonly')
        boxNewClose['values'] = Config.NEWCLOSESET['future']
        boxNewClose.grid(column = 3, row = 1, rowspan = 2, padx = 5)

        # 當沖與否
        lbFlag = Label(frame, style="Pink.TLabel", text = "當沖與否")
        lbFlag.grid(column = 4, row = 0)
            # 輸入框
        boxFlag = Combobox(frame, width = 8, state='readonly')
        boxFlag['values'] = Config.FLAGSET['future']
        boxFlag.grid(column = 4, row = 1, rowspan = 2, padx = 5)

        # 委託價
        lbPrice = Label(frame, style="Pink.TLabel", text = "委託價")
        lbPrice.grid(column = 5, row = 0)
            # 輸入框
        txtPrice = Entry(frame, width = 10)
        txtPrice.grid(column = 5, row = 1, padx = 5)

        # 委託價2
            # 輸入框
        txtPrice2 = Entry(frame, width = 10)
        txtPrice2.grid(column = 5, row = 2, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 6, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 6, row = 1, rowspan = 2, padx = 5)

        # 觸發價
        Label(frame, style="Pink.TLabel", text = ">=").grid(column = 7, row = 1)
        lbTrigger = Label(frame, style="Pink.TLabel", text = "觸發價")
        lbTrigger.grid(column = 8, row = 0)
            # 輸入框
        txtTrigger = Entry(frame, width = 10)
        txtTrigger.grid(column = 8, row = 1, padx = 5)

        # 觸發價2
        Label(frame, style="Pink.TLabel", text = "<=").grid(column = 7, row = 2)
            # 輸入框
        txtTrigger2 = Entry(frame, width = 10)
        txtTrigger2.grid(column = 8, row = 2, padx = 5)

        # 盤別
        lbReserved = Label(frame, style="Pink.TLabel", text = "盤別")
        lbReserved.grid(column = 9, row = 0)
            # 輸入框
        boxReserved = Combobox(frame, width = 8, state='readonly')
        boxReserved['values'] = Config.RESERVEDSET
        boxReserved.grid(column = 9, row = 1, rowspan = 2, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 10, row =  0, padx = 5, rowspan = 2)

        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 10, row =  1, padx = 5, rowspan = 2)
        
        # 價格類別
        lbSpecPriceType = Label(frame, style="Pink.TLabel", text = "委託價類別")
        lbSpecPriceType.grid(column = 11, row = 0)
        # 輸入框
        boxSpecPriceType = Combobox(frame, width = 8, state='readonly')
        boxSpecPriceType['values'] = Config.STRADETYPE['strategy']
        boxSpecPriceType.grid(column = 11, row = 1, rowspan = 2, padx = 5)

        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['boxBuySell2'] = boxBuySell2
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxNewClose'] = boxNewClose
        self.__dOrder['boxFlag'] = boxFlag
        self.__dOrder['txtPrice'] = txtPrice
        self.__dOrder['txtPrice2'] = txtPrice2
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['txtTrigger'] = txtTrigger
        self.__dOrder['txtTrigger2'] = txtTrigger2
        self.__dOrder['boxReserved'] = boxReserved
        self.__dOrder['boxSpecPriceType'] = boxSpecPriceType

    # 4.下單送出
    # sBuySell, sBuySell2, sTradeType, sNewClose, sDayTrade, sReserved
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxBuySell2'].get() == "買進":
                sBuySell2 = 0
            elif self.__dOrder['boxBuySell2'].get() == "賣出":
                sBuySell2 = 1

            if self.__dOrder['boxPeriod'].get() == "ROD":
                sTradeType = 0
            elif self.__dOrder['boxPeriod'].get() == "IOC":
                sTradeType = 1
            elif self.__dOrder['boxPeriod'].get() == "FOK":
                sTradeType = 2

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0
            elif self.__dOrder['boxNewClose'].get() == "平倉":
                sNewClose = 1
            elif self.__dOrder['boxNewClose'].get() == "自動":
                sNewClose = 2

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

            if self.__dOrder['boxReserved'].get() == "盤中":
                sReserved = 0
            elif self.__dOrder['boxReserved'].get() == "T盤預約":
                sReserved = 1
                
            if self.__dOrder['boxSpecPriceType'].get() == "範圍市價":
                sPriceType = 3
            elif self.__dOrder['boxSpecPriceType'].get() == "限價":
                sPriceType = 3

            # 建立下單用的參數(FUTUREOCOORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.FUTUREOCOORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 買賣別
            oOrder.sBuySell = sBuySell
            oOrder.sBuySell2 = sBuySell2
            # ROD、IOC、FOK
            oOrder.sTradeType = sTradeType
            # 新倉、平倉、自動
            oOrder.sNewClose = sNewClose
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # 委託價
            oOrder.bstrPrice = self.__dOrder['txtPrice'].get()
            oOrder.bstrPrice2 = self.__dOrder['txtPrice2'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            oOrder.bstrTrigger2 = self.__dOrder['txtTrigger2'].get()
            # 盤中、T盤預約
            oOrder.sReserved = sReserved
            
            # 限價 _範圍市價
            oOrder.nOrderPriceType1 = sPriceType

            message, m_nCode = skO.SendFutureOCOOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendFutureOCOOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode ==0:                    
                strMsg = "期貨OCO委託: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 智慧單刪單
class CancelStopLossOrder(Frame):
    def __init__(self, master=None, information=None):
        Frame.__init__(self)
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = '',
        )

        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="智慧單刪單", style="Pink.TLabelframe")
        group.grid(column = 0, row = 4, padx = 5, pady = 5, columnspan = 2, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 智慧單序號
        lbSmartKey = Label(frame, style="Pink.TLabel", text = "智慧單序號：")
        lbSmartKey.grid(column = 0, row = 0, pady = 3)
        # 輸入
        self.txtSmartKey = Entry(frame, width = 10)
        self.txtSmartKey.grid(column = 1, row = 0, padx = 5, pady = 3)

        # 智慧單類型(MST)
        lbTradeKind = Label(frame, style="Pink.TLabel", text = "智慧單類型：")
        lbTradeKind.grid(column = 2, row = 0, pady = 3)
        # 輸入
        self.boxTradeKind = Combobox(frame, width = 5, state='readonly')
        self.boxTradeKind['values'] = Config.STOPLOSSKIND["delete"]
        self.boxTradeKind.grid(column = 3, row = 0, padx = 5)

        # 期貨停損刪單
        btnCancelFutureStopLoss = Button(frame, style = "Pink.TButton", text = "期貨停損刪單")
        btnCancelFutureStopLoss["command"] = self.__btnCancelFutureStopLoss_Click
        btnCancelFutureStopLoss.grid(column = 4, row =  0, padx = 5)

        # 移動停損委託刪單
        btnCancelMovingStopLoss = Button(frame, style = "Pink.TButton", text = "移動停損刪單")
        btnCancelMovingStopLoss["command"] = self.__btnCancelMovingStopLoss_Click
        btnCancelMovingStopLoss.grid(column = 5, row =  0, padx = 5)

        # 移動停損委託刪單
        btnCancelOptionStopLoss = Button(frame, style = "Pink.TButton", text = "選擇權停損刪單")
        btnCancelOptionStopLoss["command"] = self.__btnCancelOptionStopLoss_Click
        btnCancelOptionStopLoss.grid(column = 6, row =  0, padx = 5)

        # OCO刪單
        btnCancelFutureOCO = Button(frame, style = "Pink.TButton", text = "OCO刪單")
        btnCancelFutureOCO["command"] = self.__btnCancelFutureOCO_Click
        btnCancelFutureOCO.grid(column = 7, row =  0, padx = 5)

    def __btnCancelFutureStopLoss_Click(self,bAsyncOrder = True):
        try:
            message, m_nCode = skO.CancelFutureStopLoss(Global.Global_IID, bAsyncOrder,\
                self.__dOrder['boxAccount'], self.txtSmartKey.get(), self.boxTradeKind.get())
            self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelFutureStopLoss", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode ==0:                    
                strMsg = "期貨停損刪單: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

    def __btnCancelMovingStopLoss_Click(self,bAsyncOrder = True):
        try:
            message, m_nCode = skO.CancelMovingStopLoss(Global.Global_IID, bAsyncOrder,\
                self.__dOrder['boxAccount'], self.txtSmartKey.get(), self.boxTradeKind.get())
            self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelMovingStopLoss", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode ==0:                    
                strMsg = "期貨移動停損刪單: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)


    def __btnCancelOptionStopLoss_Click(self,bAsyncOrder = True):
        try:
            message, m_nCode = skO.CancelOptionStopLoss(Global.Global_IID,bAsyncOrder,\
                self.__dOrder['boxAccount'], self.txtSmartKey.get(), self.boxTradeKind.get())
            self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelOptionStopLoss", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode ==0:                    
                strMsg = "選擇權停損刪單: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

    def __btnCancelFutureOCO_Click(self,bAsyncOrder = True):
        try:
            message, m_nCode = skO.CancelFutureOCO(Global.Global_IID,bAsyncOrder,\
                self.__dOrder['boxAccount'], self.txtSmartKey.get(), self.boxTradeKind.get())
            self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelFutureOCO", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode ==0:                    
                        strMsg = "期貨OCO刪單: " + str(message)
                        self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 智慧單查詢
class GetReport(Frame):
    def __init__(self, master=None, information=None):
        Frame.__init__(self)
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = '',
        )

        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="智慧單查詢", style="Pink.TLabelframe")
        group.grid(column = 1, row = 0, rowspan = 5, padx = 5, pady = 5, sticky = 'n')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 智慧單類別
        lbReportStatus = Label(frame, style="Pink.TLabel", text = "類別")
        lbReportStatus.grid(column = 0, row = 0, pady = 3)
        # 輸入
        self.boxReportStatus = Combobox(frame, width = 12, state='readonly')
        self.boxReportStatus['values'] = "全部的委託單"
        self.boxReportStatus.grid(column = 0, row = 1, padx = 5)

        # 智慧單類型
        lbTradeKind = Label(frame, style="Pink.TLabel", text = "智慧單類型")
        lbTradeKind.grid(column = 0, row = 2, pady = 3)
            # 輸入
        self.boxTradeKind = Combobox(frame, width = 5, state='readonly')
        self.boxTradeKind['values'] = Config.STOPLOSSKIND["report"]
        self.boxTradeKind.grid(column = 0, row = 3, padx = 5)

        def __clear_entry(event, txtDate):
            self.txtDate.delete(0, END)
            self.txtDate['foreground'] = "#000000"
        # 查詢日期
        lbDate = Label(frame, style="Pink.TLabel", text = "查詢日期")
        lbDate.grid(column = 0, row = 4, pady = 3)
            # 輸入框
        self.txtDate = Entry(frame, width = 12)
        self.txtDate.grid(column = 0, row = 6, padx = 5, pady = 3)
        self.txtDate['foreground'] = "#b3b3b3"
        self.txtDate.insert(0, "YYYYMMDD")
        self.txtDate.bind("<FocusIn>", lambda event: __clear_entry(event, self.txtDate))

        btnSend = Button(frame, style = "Pink.TButton", text = "查詢")
        btnSend["command"] = self.__btnSend_Click
        btnSend.grid(column = 0, row =  7, padx = 5)


    def __btnSend_Click(self):
        try:
            if self.boxReportStatus.get() ==  "全部的委託單":
                nReportStatus = 0
            m_nCode = skO.GetStopLossReport(Global.Global_IID, self.__dOrder["boxAccount"],\
                nReportStatus, self.boxTradeKind.get(), self.txtDate.get())
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetStopLossReport", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

class StopLossOrderGui(Frame):
    def __init__(self, information=None):
        Frame.__init__(self)
        self.__obj = dict(
            future = FutureStopLossOrder(master = self, information = information),
            moving = MovingStopLossOrder(master = self, information = information),
            option = OptionStopLossOrder(master = self, information = information),
            future_oco = FutureOCOOrder(master = self, information = information),
            cancael = CancelStopLossOrder(master = self, information = information),
            report = GetReport(master = self, information = information),
        )

    def SetAccount(self, account):
        for _ in 'future', 'moving', 'option', 'future_oco', "cancael", "report":
            self.__obj[_].SetAccount(account)

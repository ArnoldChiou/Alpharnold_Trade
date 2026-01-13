# 先把API com元件初始化
import os
import Global

skC = Global.skC
skO = Global.skO
skR = Global.skR
skQ = Global.skQ
skOSQ = Global.skOSQ
skOOQ = Global.skOOQ

# 第二種讓群益API元件可導入Python code內用的物件宣告
import comtypes.client
#comtypes.client.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\SKCOM.dll')
import comtypes.gen.SKCOMLib as sk
# skC = comtypes.client.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
# skO = comtypes.client.CreateObject(sk.SKOrderLib,interface=sk.ISKOrderLib)

# 畫視窗用物件
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

# 載入其他物件
import Config
import MessageControl
#----------------------------------------------------------------------------------------------------------------------------------------------------
# 選擇權下單(新增非同步)
class Order(Frame):
    def __init__(self, master=None, information=None):
        Frame.__init__(self)
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = ''
        )

        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="選擇權委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 0, padx = 5, pady = 5, columnspan = 3, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 15)
        txtStockNo.grid(column = 0, row = 1, padx = 10, pady = 3, sticky = 'w')

        #買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 1, row = 0)
            # 輸入框
        boxBuySell = Combobox(frame, width = 5, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 1, row = 1, padx = 10, sticky = 'w')

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 2, row = 0)
            # 輸入框
        boxPeriod = Combobox(frame, width = 10, state='readonly')
        boxPeriod['values'] = Config.PERIODSET['future']
        boxPeriod.grid(column = 2, row = 1, padx = 10, sticky = 'w')

        # 委託價
        lbPrice = Label(frame, style="Pink.TLabel", text = "委託價")
        lbPrice.grid(column = 3, row = 0)
            # 輸入框
        txtPrice = Entry(frame, width = 15)
        txtPrice.grid(column = 3, row = 1, padx = 10, sticky = 'w')

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 4, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 4, row = 1, padx = 10, sticky = 'w')

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 5, row = 0)
            # 輸入框
        boxNewClose = Combobox(frame, width = 5, state='readonly')
        boxNewClose['values'] = Config.NEWCLOSESET['future']
        boxNewClose.grid(column = 5, row = 1, padx = 10, sticky = 'w')

        # 盤別
        lbReserved = Label(frame, style="Pink.TLabel", text = "盤別")
        lbReserved.grid(column = 6, row = 0)
            # 輸入框
        boxReserved = Combobox(frame, width = 10, state='readonly')
        boxReserved['values'] = Config.RESERVEDSET
        boxReserved.grid(column = 6, row = 1, padx = 10, sticky = 'w')

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 7, row =  0, padx = 10)

        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 7, row =  1, padx = 10)


        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['txtPrice'] = txtPrice
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['boxNewClose'] = boxNewClose
        self.__dOrder['boxReserved'] = boxReserved

    # 4.下單送出
    # sPeriod, sBuySell, sTradeType, sNewClose, sReserved
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
            # 委託價
            oOrder.bstrPrice = self.__dOrder['txtPrice'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 新倉、平倉、自動
            oOrder.sNewClose = sNewClose
            # 盤中、T盤預約
            oOrder.sReserved = sReserved

            message, m_nCode = skO.SendOptionOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendOptionOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "選擇權委託: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 選擇權複式單(同步&非同步)
class DuplexOrder():
    def __init__(self, master=None, information=None):
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = ''
        )
        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="複式單委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 1, padx = 5, pady = 5, columnspan = 2,sticky = "w")

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')
        # 商品代碼1
        Merchandise1 = Label(frame, style="Pink.TLabel", text = "商品代碼1")
        Merchandise1.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        self.txtMerchandise1 = Entry(frame, width = 15)
        self.txtMerchandise1.grid(column = 0, row = 1, padx = 5)
        # 商品代碼2
        Merchandise2 = Label(frame, style="Pink.TLabel", text = "商品代碼2")
        Merchandise2.grid(column = 0, row = 2, pady = 3)
            # 輸入框
        self.txtMerchandise2 = Entry(frame, width = 15)
        self.txtMerchandise2.grid(column = 0, row = 3, padx = 5)

        # 買賣別1
        BuyOrSell1 = Label(frame, style="Pink.TLabel", text = "買賣別1")
        BuyOrSell1.grid(column = 1, row = 0)
            # 輸入框
        self.boxBuyOrSell1 = Combobox(frame, width = 10, state='readonly')
        self.boxBuyOrSell1['values'] = Config.BUYSELLSET
        self.boxBuyOrSell1.grid(column = 1, row = 1, padx = 5)
        # 買賣別2
        BuyOrSell2 = Label(frame, style="Pink.TLabel", text = "買賣別2")
        BuyOrSell2.grid(column = 1, row = 2)
            # 輸入框
        self.boxBuyOrSell2 = Combobox(frame, width = 10, state='readonly')
        self.boxBuyOrSell2['values'] = Config.BUYSELLSET
        self.boxBuyOrSell2.grid(column = 1, row = 3, padx = 5)

        # 委託條件
        TradeType = Label(frame, style="Pink.TLabel", text = "委託條件")
        TradeType.grid(column = 2, row = 1)
            # 輸入框
        self.TradeType = Combobox(frame, width = 10, state='readonly')
        self.TradeType['values'] = Config.PERIODSET["moving_stop_loss"]
        self.TradeType.grid(column = 2, row = 2, padx = 5)

        # 倉別
        NewOrClose = Label(frame, style="Pink.TLabel", text = "倉別")
        NewOrClose.grid(column = 3, row = 1)
            # 輸入框
        self.boxNewOrClose = Combobox(frame, width = 10, state='readonly')
        self.boxNewOrClose['values'] = Config.NEWCLOSESET["option_future"]
        self.boxNewOrClose.grid(column = 3, row = 2, padx = 5)

        # 委託價
        lbPrice = Label(frame, style="Pink.TLabel", text = "委託價")
        lbPrice.grid(column = 4, row = 1)
            # 輸入框
        self.txtPrice = Entry(frame, width = 10)
        self.txtPrice.grid(column = 4, row = 2, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 5, row = 1)
            # 輸入框
        self.txtQty = Entry(frame, width = 10)
        self.txtQty.grid(column = 5, row = 2, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 6, row =  1, padx = 5)
        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 6, row =  2, padx = 5)

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
            if self.boxBuyOrSell1.get() == "買進":
                sBuySell = 0
            elif self.boxBuyOrSell1.get() == "賣出":
                sBuySell = 1

            if self.boxBuyOrSell2.get() == "買進":
                sBuySell2 = 0
            elif self.boxBuyOrSell2.get() == "賣出":
                sBuySell2 = 1

            if self.TradeType.get() == "IOC":
                sTradeType = 1
            elif self.TradeType.get() == "FOK":
                sTradeType = 2

            if self.boxNewOrClose.get() == "新倉":
                sNewClose = 0
            elif self.boxNewOrClose.get() == "平倉":
                sNewClose = 1

            # 建立下單用的參數(FUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.FUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號1
            oOrder.bstrStockNo = self.txtMerchandise1.get()
            # 填入期權代號2
            oOrder.bstrStockNo2 = self.txtMerchandise2.get()
            # 買賣別1
            oOrder.sBuySell = sBuySell
            # 買賣別2
            oOrder.sBuySell2 = sBuySell2
            # IOC、FOK
            oOrder.sTradeType = sTradeType
            # 委託價
            oOrder.bstrPrice = self.txtPrice.get()
            # 委託數量
            oOrder.nQty = int(self.txtQty.get())
            # 新倉、平倉
            oOrder.sNewClose = sNewClose

            message, m_nCode = skO.SendDuplexOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendDuplexOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "複式單委託: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)
# 依序號/書號改價(選擇權)
class CorrectPrice():
    def __init__(self, master=None, information=None):
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = ''
        )
        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="選擇權改價", style="Pink.TLabelframe")
        group.grid(column = 0, row = 2, padx = 5, pady = 5, columnspan = 3,sticky = "w")

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 委託序號，委託書號
        column = 0
        self.__CorrectPriceRadVar = IntVar()

        for _ in 'txtPriceSeqNo', 'txtPriceBookNo':
                # 輸入框
            self.__dOrder[_] = Entry(frame, width = 15, state = 'disabled')
            self.__dOrder[_].grid(column = column + 1, row = 0, padx = 5)

            if _ == 'txtPriceSeqNo':
                text = '委託序號'
            elif _ == 'txtPriceBookNo':
                text = '委託書號'

            rb = Radiobutton(frame, style="Pink.TRadiobutton", text = text, variable = self.__CorrectPriceRadVar, value = column, command = self.__CorrectPriceRadCall)
            rb.grid(column = column, row = 0, pady = 3, sticky = 'ew')

            column = column + 2
        self.__dOrder['txtPriceSeqNo']['state'] = '!disabled'

        # 修改價格
        lbCorrectPrice = Label(frame, style="Pink.TLabel", text = "修改價格")
        lbCorrectPrice.grid(column = 4, row = 0, pady = 3)
            # 輸入框
        self.txtCorrectPrice = Entry(frame, width = 10)
        self.txtCorrectPrice.grid(column = 5, row = 0, padx = 5, pady = 3)

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 6, row = 0)
            # 輸入框
        self.boxPeriod = Combobox(frame, width = 5, state='readonly')
        self.boxPeriod['values'] = Config.PERIODSET['future']
        self.boxPeriod.grid(column = 7, row = 0, padx = 5)

        # 按鈕
        btnCorrectPrice = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnCorrectPrice["command"] = self.__btnCorrectPrice_Click
        btnCorrectPrice.grid(column = 8, row =  0, padx = 5)

        btnAsyncCorrectPrice = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnAsyncCorrectPrice["command"] = self.__btnAsyncCorrectPrice_Click
        btnAsyncCorrectPrice.grid(column = 9, row =  0, padx = 5)

    def __btnCorrectPrice_Click(self):
        self.__SendCorrectPrice_Click(False)

    def __btnAsyncCorrectPrice_Click(self):
        self.__SendCorrectPrice_Click(True)

    def __SendCorrectPrice_Click(self,bAsyncOrder):
        try:
            if self.__CorrectPriceRadVar.get() == 0:
                if self.boxPeriod.get() == "ROD":
                    nTradeType = 0
                elif self.boxPeriod.get() == "IOC":
                    nTradeType = 1
                elif self.boxPeriod.get() == "FOK":
                    nTradeType = 2

                message,m_nCode = skO.CorrectPriceBySeqNo(Global.Global_IID,bAsyncOrder,\
                    self.__dOrder['boxAccount'],self.__dOrder['txtPriceSeqNo'].get(),self.txtCorrectPrice.get(),nTradeType)
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CorrectPriceBySeqNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "選擇權改價: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

            elif self.__CorrectPriceRadVar.get() == 2:
                bstrMarketSymbol = "TO"
                if self.boxPeriod.get() == "ROD":
                    nTradeType = 0
                elif self.boxPeriod.get() == "IOC":
                    nTradeType = 1
                elif self.boxPeriod.get() == "FOK":
                    nTradeType = 2

                message,m_nCode = skO.CorrectPriceByBookNo(Global.Global_IID,bAsyncOrder,\
                    self.__dOrder['boxAccount'],bstrMarketSymbol,self.__dOrder['txtPriceBookNo'].get(),self.txtCorrectPrice.get(),nTradeType)
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CorrectPriceByBookNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "選擇權改價: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)

    def __CorrectPriceRadCall(self):
        CorrectPriceRadVar = self.__CorrectPriceRadVar.get()
        self.__dOrder['txtPriceSeqNo']['state'] = '!disabled' if CorrectPriceRadVar == 0 else 'disabled'
        self.__dOrder['txtPriceBookNo']['state'] = '!disabled' if CorrectPriceRadVar == 2 else 'disabled'
# 複式單拆解
class DisassembleOption():
    def __init__(self, master=None, information=None):
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = ''
        )
        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="複式單拆解(未實測)", style="Pink.TLabelframe")
        # group.grid(column = 0, row = 3, padx = 5, pady = 5,sticky = "w")

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 商品代碼1
        lbStockNo1 = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo1.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        self.txtStockNo1 = Entry(frame, width = 15)
        self.txtStockNo1.grid(column = 0, row = 1, padx = 5)

        # 買賣別
        lbBuyOrSell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuyOrSell.grid(column = 2, row = 0)
            # 輸入框
        self.boxBuyOrSell1 = Combobox(frame, width = 10, state='readonly')
        self.boxBuyOrSell1['values'] = Config.BUYSELLSET
        self.boxBuyOrSell1.grid(column = 2, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 3, row = 0)
            # 輸入框
        self.txtQty = Entry(frame, width = 10)
        self.txtQty.grid(column = 3, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 4, row =  0, padx = 5)
        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 4, row =  1, padx = 5)

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
            if self.boxBuyOrSell1.get() == "買進":
                sBuySell = 0
            elif self.boxBuyOrSell1.get() == "賣出":
                sBuySell = 1

            # 建立下單用的參數(FUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.FUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號1
            oOrder.bstrStockNo = self.txtStockNo1.get()
            # 買賣別
            oOrder.sBuySell = sBuySell
            # 委託數量
            oOrder.nQty = int(self.txtQty.get())

            message, m_nCode = skO.DisassembleOptions(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "DisassembleOptions", self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)
# 雙邊部位了結
class CoverProduct():
    def __init__(self, master=None, information=None):
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            boxAccount = ''
        )
        self.__CreateWidget()

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="雙邊部位了結(未實測)", style="Pink.TLabelframe")
        # group.grid(column = 1, row = 3, padx = 5, pady = 5,sticky = "w")

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 商品代碼
        lbMerchandise1 = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbMerchandise1.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        self.txtMerchandise1 = Entry(frame, width = 15)
        self.txtMerchandise1.grid(column = 0, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 1, row = 0)
            # 輸入框
        self.txtQty = Entry(frame, width = 10)
        self.txtQty.grid(column = 1, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        # btnSendOrder.grid(column = 2, row =  0, padx = 5)
        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 2, row =  1, padx = 5)

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
            # 建立下單用的參數(FUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.FUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號
            oOrder.bstrStockNo = self.txtMerchandise1.get()
            # 委託數量
            oOrder.nQty = int(self.txtQty.get())

            message, m_nCode = skO.CoverAllProduct(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "CoverAllProduct", self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)

class OptionOrder(Frame):
    def __init__(self, information=None):
        Frame.__init__(self)
        self.__obj = dict(
            order = Order(master = self, information = information),
            duplexorder = DuplexOrder(master = self, information = information),
            correct = CorrectPrice(master = self, information = information),
            dissemble = DisassembleOption(master = self, information = information),
            cover = CoverProduct(master = self, information = information),
        )

    def SetAccount(self, account):
        for _ in 'order',"duplexorder","correct","dissemble","cover":
            self.__obj[_].SetAccount(account)

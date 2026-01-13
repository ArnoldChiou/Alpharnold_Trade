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

# 畫視窗用物件
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

# 載入其他物件
import Config
import MessageControl
#----------------------------------------------------------------------------------------------------------------------------------------------------
# 委託
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
        group = LabelFrame(self.__master, text="海選委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 0, padx = 5, pady = 5, columnspan = 2,sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        # 交易所代號
        lbExchangeNo = Label(frame, style="Pink.TLabel", text = "交易所代號")
        lbExchangeNo.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtExchangeNo = Entry(frame, width = 10)
        txtExchangeNo.grid(column = 0, row = 1, padx = 5, pady = 3)

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 1, row = 0)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 1, row = 1, padx = 5)

        def __clear_entry(event, txtYearMonth):
            txtYearMonth.delete(0, END)
            txtYearMonth['foreground'] = "#000000"
        # 商品年月
        lbYearMonth = Label(frame, style="Pink.TLabel", text = "商品年月")
        lbYearMonth.grid(column = 2, row = 0)
            # 輸入框
        txtYearMonth = Entry(frame, width = 10)
        txtYearMonth.grid(column = 2, row = 1, padx = 5)
        txtYearMonth['foreground'] = "#b3b3b3"
        txtYearMonth.insert(0, "YYYYMM")
        txtYearMonth.bind("<FocusIn>", lambda event: __clear_entry(event, txtYearMonth))

        # 履約價
        lbStrikePrice = Label(frame, style="Pink.TLabel", text = "履約價")
        lbStrikePrice.grid(column = 3, row = 0)
            # 輸入框
        txtStrikePrice = Entry(frame, width = 10)
        txtStrikePrice.grid(column = 3, row = 1, padx = 5)

        # Call Put
        lbCallPut = Label(frame, style="Pink.TLabel", text = "CALL PUT")
        lbCallPut.grid(column = 4, row = 0)
            # 輸入框
        boxCallPut = Combobox(frame, width = 8, state='readonly')
        boxCallPut['values'] = Config.CALLPUTSET
        boxCallPut.grid(column = 4, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 5, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 5, row = 1, padx = 5)

        # 委託價
        lbOrder = Label(frame, style="Pink.TLabel", text = "委託價")
        lbOrder.grid(column = 6, row = 0)
            # 輸入框
        txtOrder = Entry(frame, width = 10)
        txtOrder.grid(column = 6, row = 1, padx = 5)

        # 委託價分子
        lbOrderNumerator = Label(frame, style="Pink.TLabel", text = "委託價分子")
        lbOrderNumerator.grid(column = 7, row = 0)
            # 輸入框
        txtOrderNumerator = Entry(frame, width = 10)
        txtOrderNumerator.grid(column = 7, row = 1, padx = 5)
        #--------------------------------------------------------------------------------------------------------------------------------------------

        # frame = Frame(group, style="Pink.TFrame")
        # frame.grid(column = 0, row = 1, padx = 5, pady = 5, sticky = 'ew')

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 0, row = 2, pady = 3)
            # 輸入框
        boxBuySell = Combobox(frame, width = 8, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 0, row = 3, padx = 5)

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 1, row = 2)
            # 輸入框
        boxNewClose = Combobox(frame, width = 8, state='readonly')
        boxNewClose['values'] = Config.NEWCLOSESET['option_future']
        boxNewClose.grid(column = 1, row = 3, padx = 5)

        # 當沖與否
        lbFlag = Label(frame, style="Pink.TLabel", text = "當沖與否")
        lbFlag.grid(column = 2, row = 2)
            # 輸入框
        boxFlag = Combobox(frame, width = 8, state='readonly')
        boxFlag['values'] = Config.FLAGSET['future']
        boxFlag.grid(column = 2, row = 3, padx = 5)

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 3, row = 2)
            # 輸入框
        boxPeriod = Combobox(frame, width = 8, state='readonly')
        boxPeriod['values'] = Config.PERIODSET['sea_future']
        boxPeriod.grid(column = 3, row = 3, padx = 5)

        # 委託類型
        lbSpecialTradeType = Label(frame, style="Pink.TLabel", text = "委託類型")
        lbSpecialTradeType.grid(column = 4, row = 2, columnspan = 2)
            # 輸入框
        boxSpecialTradeType = Combobox(frame, width = 20, state='readonly')
        boxSpecialTradeType['values'] = Config.STRADETYPE['sea_option']
        boxSpecialTradeType.grid(column = 4, row = 3, padx = 5, columnspan = 2)

        # 觸發價
        lbTrigger = Label(frame, style="Pink.TLabel", text = "觸發價")
        lbTrigger.grid(column = 6, row = 2)
            # 輸入框
        txtTrigger = Entry(frame, width = 10)
        txtTrigger.grid(column = 6, row = 3, padx = 5)

        # 觸發價分子
        lbTriggerNumerator = Label(frame, style="Pink.TLabel", text = "觸發價分子")
        lbTriggerNumerator.grid(column = 7, row = 2)
            # 輸入框
        txtTriggerNumerator = Entry(frame, width = 10)
        txtTriggerNumerator.grid(column = 7, row = 3, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 8, row =  1, padx = 5)

        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 8, row =  2, padx = 5)


        self.__dOrder['txtExchangeNo'] = txtExchangeNo
        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['txtYearMonth'] = txtYearMonth
        self.__dOrder['txtStrikePrice'] = txtStrikePrice
        self.__dOrder['boxCallPut'] = boxCallPut
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['txtOrder'] = txtOrder
        self.__dOrder['txtOrderNumerator'] = txtOrderNumerator

        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['boxNewClose'] = boxNewClose
        self.__dOrder['boxFlag'] = boxFlag
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxSpecialTradeType'] = boxSpecialTradeType
        self.__dOrder['txtTrigger'] = txtTrigger
        self.__dOrder['txtTriggerNumerator'] = txtTriggerNumerator

    # 4.下單送出
    # sCallPut, sBuySell, sNewClose, boxFlag, boxPeriod, sSpecialTradeType
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇海期帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇海期帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__dOrder['boxCallPut'].get() == "CALL":
                sCallPut = 0
            elif self.__dOrder['boxCallPut'].get() == "PUT":
                sCallPut = 1

            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0
            elif self.__dOrder['boxNewClose'].get() == "平倉":
                sNewClose = 1

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

            if self.__dOrder['boxPeriod'].get() == "ROD":
                sTradeType = 0

            if self.__dOrder['boxSpecialTradeType'].get() == "LMT（限價）":
                sSpecialTradeType = 0

            # 建立下單用的參數(OVERSEAFUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.OVERSEAFUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入交易所代號
            oOrder.bstrExchangeNo = self.__dOrder['txtExchangeNo'] .get()
            # 填入期權代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 近月商品年月
            oOrder.bstrYearMonth = self.__dOrder['txtYearMonth'].get()
            # 履約價
            oOrder.bstrStrikePrice = self.__dOrder['txtStrikePrice'].get()
            # Call Put
            oOrder.sCallPut = sCallPut
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 委託價
            oOrder.bstrOrder = self.__dOrder['txtOrder'].get()
            # 委託價分子
            oOrder.bstrOrderNumerator = self.__dOrder['txtOrderNumerator'].get()
            # 買賣別
            oOrder.sBuySell = sBuySell
            # 新倉、平倉
            oOrder.sNewClose = sNewClose
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # ROD
            oOrder.sTradeType = sTradeType
            # LMT（限價）
            oOrder.sSpecialTradeType = sSpecialTradeType
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            # 觸發價分子
            oOrder.bstrTriggerNumerator = self.__dOrder['txtTriggerNumerator'].get()

            message, m_nCode = skO.SendOverSeaOptionOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendOverSeaOptionOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "海選委託: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 改價
class CorrectPrice(Frame):
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
        group = LabelFrame(self.__master, text="海選改價", style="Pink.TLabelframe")
        group.grid(column = 0, row = 1,padx = 5, pady = 5, sticky = 'ew')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 委託書號
        lbBookNo = Label(frame, style="Pink.TLabel", text = "委託書號")
        lbBookNo.grid(column = 0, row = 0)
            # 輸入框
        self.txtBookNo = Entry(frame, width = 10)
        self.txtBookNo.grid(column = 0, row = 1, padx = 5, pady = 3)

        # 交易所代號
        lbExchangeNo = Label(frame, style="Pink.TLabel", text = "交易所代號")
        lbExchangeNo.grid(column = 1, row = 0, pady = 3)
            # 輸入框
        self.txtExchangeNo = Entry(frame, width = 10)
        self.txtExchangeNo.grid(column = 1, row = 1, padx = 5, pady = 3)

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 2, row = 0, pady = 3)
            # 輸入框
        self.txtStockNo = Entry(frame, width = 10)
        self.txtStockNo.grid(column = 2, row = 1, padx = 5, pady = 3)

        def __clear_entry(event, txtYearMonth):
            self.txtYearMonth.delete(0, END)
            self.txtYearMonth['foreground'] = "#000000"
        # 商品年月
        lbYearMonth = Label(frame, style="Pink.TLabel", text = "商品年月")
        lbYearMonth.grid(column = 3, row = 0, pady = 3)
            # 輸入框
        self.txtYearMonth = Entry(frame, width = 10)
        self.txtYearMonth.grid(column = 3, row = 1, padx = 5, pady = 3)
        self.txtYearMonth['foreground'] = "#b3b3b3"
        self.txtYearMonth.insert(0, "YYYYMM")
        self.txtYearMonth.bind("<FocusIn>", lambda event: __clear_entry(event, self.txtYearMonth))

        # 履約價
        lbStrikePrice = Label(frame, style="Pink.TLabel", text = "履約價")
        lbStrikePrice.grid(column = 4, row = 0, pady = 3)
            # 輸入框
        self.txtStrikePrice = Entry(frame, width = 10)
        self.txtStrikePrice.grid(column = 4, row = 1, padx = 5, pady = 3)

        # 新委託價
        lbOrder = Label(frame, style="Pink.TLabel", text = "新委託價")
        lbOrder.grid(column = 5, row = 0)
            # 輸入框
        self.txtOrder = Entry(frame, width = 10)
        self.txtOrder.grid(column = 5, row = 1, padx = 5)

        # 新委託價分子
        lbOrderNumerator = Label(frame, style="Pink.TLabel", text = "新委託價分子")
        lbOrderNumerator.grid(column = 6, row = 0)
            # 輸入框
        self.txtOrderNumerator = Entry(frame, width = 10)
        self.txtOrderNumerator.grid(column = 6, row = 1, padx = 5)

        #--------------------------------------------------------------------------------------------------------------------------------------------

        # 新委託價分母
        lbOrderDenominator = Label(frame, style="Pink.TLabel", text = "新委託價分母")
        lbOrderDenominator.grid(column = 0, row = 2)
            # 輸入框
        self.txtOrderDenominator = Entry(frame, width = 10)
        self.txtOrderDenominator.grid(column = 0, row = 3, padx = 5)

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 1, row = 2)
            # 輸入框
        self.boxBuySell = Combobox(frame, width = 8, state='readonly')
        self.boxBuySell['values'] = Config.BUYSELLSET
        self.boxBuySell.grid(column = 1, row = 3, padx = 5)

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 2, row = 2)
            # 輸入框
        self.boxNewClose = Combobox(frame, width = 8, state='readonly')
        self.boxNewClose['values'] = Config.NEWCLOSESET['sea_future']
        self.boxNewClose.grid(column = 2, row = 3, padx = 5)

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 3, row = 2)
            # 輸入框
        self.boxPeriod = Combobox(frame, width = 8, state='readonly')
        self.boxPeriod['values'] = Config.PERIODSET['sea_future']
        self.boxPeriod.grid(column = 3, row = 3, padx = 5)

        # 委託類型
        lbSpecialTradeType = Label(frame, style="Pink.TLabel", text = "委託類型")
        lbSpecialTradeType.grid(column = 4, row = 2, columnspan = 2)
            # 輸入框
        self.boxSpecialTradeType = Combobox(frame, width = 20, state='readonly')
        self.boxSpecialTradeType['values'] = Config.STRADETYPE['sea_option']
        self.boxSpecialTradeType.grid(column = 4, row = 3, padx = 5, columnspan = 2)

        # 買賣權
        lbCallPut = Label(frame, style="Pink.TLabel", text = "Call/Put")
        lbCallPut.grid(column = 6, row = 2, pady = 3)
            # 輸入框
        self.boxCallPut = Combobox(frame, width = 8, state='readonly')
        self.boxCallPut['values'] = Config.CALLPUTSET
        self.boxCallPut.grid(column = 6, row = 3, padx = 5)

        # 海選改價同步委託
        btnSendCorrectPrice = Button(frame, style = "Pink.TButton", text = "改價同步委託")
        btnSendCorrectPrice["command"] = self.__btnSendCorrectPrice_Click
        btnSendCorrectPrice.grid(column = 7, row = 0, rowspan = 2, padx = 5)

        # 海選改價非同步委託
        btnSendCorrectPriceAsync = Button(frame, style = "Pink.TButton", text = "改價非同步委託")
        btnSendCorrectPriceAsync["command"] = self.__btnSendCorrectPriceAsync_Click
        btnSendCorrectPriceAsync.grid(column = 7, row = 2, rowspan = 2, padx = 5)

    def __btnSendCorrectPrice_Click(self):
        self.__SendCorrectPrice(False)

    def __btnSendCorrectPriceAsync_Click(self):
        self.__SendCorrectPrice(True)

    def __SendCorrectPrice(self,bAsyncOrder):
        try:
            if self.boxBuySell.get() == "買進":
                nBuySell = 0
            elif self.boxBuySell.get() == "賣出":
                nBuySell = 1

            if self.boxNewClose.get() == "新倉":
                nNewClose = 0

            if self.boxPeriod.get() == "ROD":
                nTradeType = 0

            if self.boxSpecialTradeType.get() == "LMT（限價）":
                nSpecialTradeType = 0

            if self.boxCallPut.get() == "CALL":
                nCallPut = 0
            elif self.boxCallPut.get() == "PUT":
                nCallPut = 1

            # 建立下單用的參數(OVERSEAFUTUREORDERGW)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.OVERSEAFUTUREORDERFORGW()
            # 填入完整帳號
            oOrder.bstrFullAccount = self.__dOrder['boxAccount']
            # 填入交易所代號
            oOrder.bstrExchangeNo = str(self.txtExchangeNo.get())
            # 填入商品代號
            oOrder.bstrStockNo = str(self.txtStockNo.get())
            # 近月商品年月
            oOrder.bstrYearMonth = str(self.txtYearMonth.get())
            # 新委託價
            oOrder.bstrOrderPrice = str(self.txtOrder.get())
            # 新委託價分子
            oOrder.bstrOrderNumerator = str(self.txtOrderNumerator.get())
            # 新委託價分母
            oOrder.bstrOrderDenominator = str(self.txtOrderDenominator.get())
            # 委託書號
            oOrder.bstrBookNo = self.txtBookNo.get()
            # 履約價
            oOrder.bstrStrikePrice = self.txtStrikePrice.get()

            # 買賣別
            oOrder.nBuySell = nBuySell
            # 新倉
            oOrder.nNewClose = nNewClose
            # ROD
            oOrder.nTradeType = nTradeType
            # CALL or PUT
            oOrder.nCallPut = nCallPut
            # LMT（限價）、MKT（市價）、STL（停損限價）、STP（停損市價）
            oOrder.nSpecialTradeType = nSpecialTradeType

            message, m_nCode = skO.OverSeaOptionCorrectPriceByBookNo(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "OverSeaOptionCorrectPriceByBookNo", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "海選改價: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)
# 海外選擇權商品清單
class OverseaOptions():
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
        group = LabelFrame(self.__master, text="可交易商品", style="Pink.TLabelframe")
        group.grid(column = 0, row = 2, padx = 5, pady = 5,sticky = "w")

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        btnGetOverseaOptions = Button(frame, style = "Pink.TButton", text = "商品查詢")
        btnGetOverseaOptions["command"] = self.__btnGetOverseaOptions_Click
        btnGetOverseaOptions.grid(column = 0, row = 0, padx = 5)

    def __btnGetOverseaOptions_Click(self):
        try:
            m_nCode = skO.GetOverseaOptions()
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetOverseaOptions", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

class SeaOptionOrder(Frame):
    def __init__(self, information=None):
        Frame.__init__(self)
        self.__obj = dict(
            order = Order(master = self, information = information),
            sea = OverseaOptions(master = self, information = information),
            correct = CorrectPrice(master = self, information = information),
        )

    def SetAccount(self, account):
        for _ in 'order', "sea", "correct":
            self.__obj[_].SetAccount(account)

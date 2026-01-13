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
# 委託
class Order(Frame):
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
        group = LabelFrame(self.__master, text="海期委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 0, columnspan = 3,padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = 'w')

        # 交易所代號
        lbExchangeNo = Label(frame, style="Pink.TLabel", text = "交易所代號")
        lbExchangeNo.grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtExchangeNo = Entry(frame, width = 10)
        txtExchangeNo.grid(column = 0, row = 1, padx = 5, pady = 3)

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 1, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 1, row = 1, padx = 5, pady = 3)

        def __clear_entry(event, txtYearMonth):
            txtYearMonth.delete(0, END)
            txtYearMonth['foreground'] = "#000000"
        # 商品年月
        lbYearMonth = Label(frame, style="Pink.TLabel", text = "商品年月")
        lbYearMonth.grid(column = 2, row = 0, pady = 3)
            # 輸入框
        txtYearMonth = Entry(frame, width = 10)
        txtYearMonth.grid(column = 2, row = 1, padx = 5, pady = 3)
        txtYearMonth['foreground'] = "#b3b3b3"
        txtYearMonth.insert(0, "YYYYMM")
        txtYearMonth.bind("<FocusIn>", lambda event: __clear_entry(event, txtYearMonth))

        # 委託價
        lbOrder = Label(frame, style="Pink.TLabel", text = "委託價")
        lbOrder.grid(column = 3, row = 0)
            # 輸入框
        txtOrder = Entry(frame, width = 10)
        txtOrder.grid(column = 3, row = 1, padx = 5)

        # 委託價分子
        lbOrderNumerator = Label(frame, style="Pink.TLabel", text = "委託價分子")
        lbOrderNumerator.grid(column = 4, row = 0)
            # 輸入框
        txtOrderNumerator = Entry(frame, width = 10)
        txtOrderNumerator.grid(column = 4, row = 1, padx = 5)

        # 觸發價
        lbTrigger = Label(frame, style="Pink.TLabel", text = "觸發價")
        lbTrigger.grid(column = 5, row = 0)
            # 輸入框
        txtTrigger = Entry(frame, width = 10)
        txtTrigger.grid(column = 5, row = 1, padx = 5)

        # 觸發價分子
        lbTriggerNumerator = Label(frame, style="Pink.TLabel", text = "觸發價分子")
        lbTriggerNumerator.grid(column = 6, row = 0)
            # 輸入框
        txtTriggerNumerator = Entry(frame, width = 10)
        txtTriggerNumerator.grid(column = 6, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 7, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 7, row = 1, padx = 5)
        #-----------------------------------------------------------------------
        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 0, row = 2)
            # 輸入框
        boxBuySell = Combobox(frame, width = 8, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 0, row = 3, padx = 5)

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 1, row = 2)
            # 輸入框
        boxNewClose = Combobox(frame, width = 8, state='readonly')
        boxNewClose['values'] = Config.NEWCLOSESET['sea_future']
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
        boxSpecialTradeType['values'] = Config.STRADETYPE['sea_future']
        boxSpecialTradeType.grid(column = 4, row = 3, padx = 5, columnspan = 2)

        # 自訂欄位
        lbOrderLinked = Label(frame, style="Pink.TLabel", text = "自訂欄位(OLID)")
        lbOrderLinked.grid(column = 6, row = 2, columnspan = 2)
            # 輸入框
        self.txtOrderLinke = Entry(frame, width = 20)
        self.txtOrderLinke.grid(column = 6, row = 3, padx = 5,columnspan = 2)

        # 同步
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 8, row =  0, padx = 5)

        # 非同步
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 8, row =  1, padx = 5)

        # 委託(OLID)
        btnSendOrderOLID = Button(frame, style = "Pink.TButton", text = "委託(OLID)")
        btnSendOrderOLID["command"] = self.__btnSendOrderOLID_Click
        btnSendOrderOLID.grid(column = 8, row =  2, padx = 5,rowspan = 2)

        # 價差
        groupYearMonth2 = LabelFrame(frame, style="Pink.TLabelframe", text = "商品年月(遠月)")
        groupYearMonth2.grid(column = 9, row = 0, rowspan = 4)

        def __clear_entry(event, txtYearMonth2):
            txtYearMonth2.delete(0, END)
            txtYearMonth2['foreground'] = "#000000"
            # 輸入框
        txtYearMonth2 = Entry(groupYearMonth2, width = 10)
        txtYearMonth2.grid(column = 0, row = 0, padx = 5)
        txtYearMonth2['foreground'] = "#b3b3b3"
        txtYearMonth2.insert(0, "YYYYMM")
        txtYearMonth2.bind("<FocusIn>", lambda event: __clear_entry(event, txtYearMonth2))


        btnSendSpreadOrder = Button(groupYearMonth2, style = "Pink.TButton", text = "價差委託")
        btnSendSpreadOrder["command"] = self.__btnSendSpreadOrder_Click
        btnSendSpreadOrder.grid(column = 0, row =  1, padx = 5)

        btnSendSpreadOrderOLID = Button(groupYearMonth2, style = "Pink.TButton", text = "價差委託(OLID)")
        btnSendSpreadOrderOLID["command"] = self.__btnSendSpreadOrderOLID_Click
        btnSendSpreadOrderOLID.grid(column = 0, row =  2, padx = 5)

        self.__dOrder['txtExchangeNo'] = txtExchangeNo
        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['txtYearMonth'] = txtYearMonth
        self.__dOrder["txtYearMonth2"] = txtYearMonth2
        self.__dOrder['txtOrder'] = txtOrder
        self.__dOrder['txtOrderNumerator'] = txtOrderNumerator
        self.__dOrder['txtTrigger'] = txtTrigger
        self.__dOrder['txtTriggerNumerator'] = txtTriggerNumerator
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['boxNewClose'] = boxNewClose
        self.__dOrder['boxFlag'] = boxFlag
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxSpecialTradeType'] = boxSpecialTradeType
    # 4.下單送出
    # sBuySell, sNewClose, boxFlag, boxPeriod, sSpecialTradeType
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
            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

            if self.__dOrder['boxPeriod'].get() == "ROD":
                sTradeType = 0

            if self.__dOrder['boxSpecialTradeType'].get() == "LMT（限價）":
                sSpecialTradeType = 0
            elif self.__dOrder['boxSpecialTradeType'].get() == "MKT（市價）":
                sSpecialTradeType = 1
            elif self.__dOrder['boxSpecialTradeType'].get() == "STL（停損限價）":
                sSpecialTradeType = 2
            elif self.__dOrder['boxSpecialTradeType'].get() == "STP（停損市價）":
                sSpecialTradeType = 3

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
            # 委託價
            oOrder.bstrOrder = self.__dOrder['txtOrder'].get()
            # 委託價分子
            oOrder.bstrOrderNumerator = self.__dOrder['txtOrderNumerator'].get()
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            # 觸發價分子
            oOrder.bstrTriggerNumerator = self.__dOrder['txtTriggerNumerator'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 買賣別
            oOrder.sBuySell = sBuySell
            # 新倉
            oOrder.sNewClose = sNewClose
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # ROD
            oOrder.sTradeType = sTradeType
            # LMT（限價）、MKT（市價）、STL（停損限價）、STP（停損市價）
            oOrder.sSpecialTradeType = sSpecialTradeType

            message, m_nCode = skO.SendOverSeaFutureOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendOverSeaFutureOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "海期委託: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)

    def __btnSendOrderOLID_Click(self,bAsyncOrder = True):
        try:
            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

            if self.__dOrder['boxPeriod'].get() == "ROD":
                sTradeType = 0

            if self.__dOrder['boxSpecialTradeType'].get() == "LMT（限價）":
                sSpecialTradeType = 0
            elif self.__dOrder['boxSpecialTradeType'].get() == "MKT（市價）":
                sSpecialTradeType = 1
            elif self.__dOrder['boxSpecialTradeType'].get() == "STL（停損限價）":
                sSpecialTradeType = 2
            elif self.__dOrder['boxSpecialTradeType'].get() == "STP（停損市價）":
                sSpecialTradeType = 3

            # 建立下單用的參數(OVERSEAFUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.OVERSEAFUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入交易所代號
            oOrder.bstrExchangeNo = self.__dOrder['txtExchangeNo'].get()
            # 填入期權代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 近月商品年月
            oOrder.bstrYearMonth = self.__dOrder['txtYearMonth'].get()
            # 委託價
            oOrder.bstrOrder = self.__dOrder['txtOrder'].get()
            # 委託價分子
            oOrder.bstrOrderNumerator = self.__dOrder['txtOrderNumerator'].get()
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            # 觸發價分子
            oOrder.bstrTriggerNumerator = self.__dOrder['txtTriggerNumerator'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 買賣別
            oOrder.sBuySell = sBuySell
            # 新倉
            oOrder.sNewClose = sNewClose
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # ROD
            oOrder.sTradeType = sTradeType
            # LMT（限價）、MKT（市價）、STL（停損限價）、STP（停損市價）
            oOrder.sSpecialTradeType = sSpecialTradeType

            message, m_nCode = skO.SendOverSeaFutureOrderOLID(Global.Global_IID, bAsyncOrder, oOrder, self.txtOrderLinke.get())
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendOverSeaFutureOrderOLID", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

    def __btnSendSpreadOrder_Click(self,bAsyncOrder = True):
        try:
            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

            if self.__dOrder['boxPeriod'].get() == "ROD":
                sTradeType = 0

            if self.__dOrder['boxSpecialTradeType'].get() == "LMT（限價）":
                sSpecialTradeType = 0
            elif self.__dOrder['boxSpecialTradeType'].get() == "MKT（市價）":
                sSpecialTradeType = 1
            elif self.__dOrder['boxSpecialTradeType'].get() == "STL（停損限價）":
                sSpecialTradeType = 2
            elif self.__dOrder['boxSpecialTradeType'].get() == "STP（停損市價）":
                sSpecialTradeType = 3

            # 建立下單用的參數(OVERSEAFUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.OVERSEAFUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入交易所代號
            oOrder.bstrExchangeNo = self.__dOrder['txtExchangeNo'].get()
            # 填入期權代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 近月商品年月
            oOrder.bstrYearMonth = self.__dOrder['txtYearMonth'].get()
            # 價差商品年月
            oOrder.bstrYearMonth2 = self.__dOrder["txtYearMonth2"].get()
            # 委託價
            oOrder.bstrOrder = self.__dOrder['txtOrder'].get()
            # 委託價分子
            oOrder.bstrOrderNumerator = self.__dOrder['txtOrderNumerator'].get()
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            # 觸發價分子
            oOrder.bstrTriggerNumerator = self.__dOrder['txtTriggerNumerator'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 買賣別
            oOrder.sBuySell = sBuySell
            # 新倉
            oOrder.sNewClose = sNewClose
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # ROD
            oOrder.sTradeType = sTradeType
            # LMT（限價）、MKT（市價）、STL（停損限價）、STP（停損市價）
            oOrder.sSpecialTradeType = sSpecialTradeType

            message, m_nCode = skO.SendOverSeaFutureSpreadOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendOverSeaFutureSpreadOrder", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

    def __btnSendSpreadOrderOLID_Click(self):
        try:
            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            if self.__dOrder['boxNewClose'].get() == "新倉":
                sNewClose = 0

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

            if self.__dOrder['boxPeriod'].get() == "ROD":
                sTradeType = 0

            if self.__dOrder['boxSpecialTradeType'].get() == "LMT（限價）":
                sSpecialTradeType = 0
            elif self.__dOrder['boxSpecialTradeType'].get() == "MKT（市價）":
                sSpecialTradeType = 1
            elif self.__dOrder['boxSpecialTradeType'].get() == "STL（停損限價）":
                sSpecialTradeType = 2
            elif self.__dOrder['boxSpecialTradeType'].get() == "STP（停損市價）":
                sSpecialTradeType = 3

            # 建立下單用的參數(OVERSEAFUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.OVERSEAFUTUREORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入交易所代號
            oOrder.bstrExchangeNo = self.__dOrder['txtExchangeNo'].get()
            # 填入期權代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 近月商品年月
            oOrder.bstrYearMonth = self.__dOrder['txtYearMonth'].get()
            # 價差商品年月
            oOrder.bstrYearMonth2 = self.__dOrder["txtYearMonth2"].get()
            # 委託價
            oOrder.bstrOrder = self.__dOrder['txtOrder'].get()
            # 委託價分子
            oOrder.bstrOrderNumerator = self.__dOrder['txtOrderNumerator'].get()
            # 觸發價
            oOrder.bstrTrigger = self.__dOrder['txtTrigger'].get()
            # 觸發價分子
            oOrder.bstrTriggerNumerator = self.__dOrder['txtTriggerNumerator'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 買賣別
            oOrder.sBuySell = sBuySell
            # 新倉
            oOrder.sNewClose = sNewClose
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # ROD
            oOrder.sTradeType = sTradeType
            # LMT（限價）、MKT（市價）、STL（停損限價）、STP（停損市價）
            oOrder.sSpecialTradeType = sSpecialTradeType

            message, m_nCode = skO.SendOverSeaFutureSpreadOrderOLID(Global.Global_IID, True, oOrder, self.txtOrderLinke.get())
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendOverSeaFutureSpreadOrderOLID", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 委託減量
class DecreaseOrder(Frame):
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
        group = LabelFrame(self.__master, text="委託減量", style="Pink.TLabelframe")
        group.grid(column = 0, row = 1,padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 委託序號
        Label(frame, style="Pink.TLabel", text = "委託序號：").grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtSqlNo = Entry(frame, width = 18)
        txtSqlNo.grid(column = 1, row = 0, padx = 5)

        # 欲減少的數量
        Label(frame, style="Pink.TLabel", text = "欲減少的數量：").grid(column = 2, row = 0)
            # 輸入框
        txtDecreaseQty = Entry(frame, width = 10)
        txtDecreaseQty.grid(column = 3, row = 0, padx = 10)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 4, row =  0, padx = 10)

        # btnSendOrder
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 5, row =  0, padx = 10)

        self.__dOrder['txtSqlNo'] = txtSqlNo
        self.__dOrder['txtDecreaseQty'] = txtDecreaseQty

    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇海期帳號！')
        else:
            self.__SendOrder_Click(False)

    # 送出
    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇海期帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            message, m_nCode = skO.OverSeaDecreaseOrderBySeqNo( Global.Global_IID, bAsyncOrder, self.__dOrder['boxAccount'],\
                self.__dOrder['txtSqlNo'].get(), int(self.__dOrder['txtDecreaseQty'].get()) )
            self.__oMsg.SendReturnMessage("Order", m_nCode, "OverSeaDecreaseOrderBySeqNo", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "海期減量: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)
# 取消委託
class CancelOrder(Frame):
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
        group = LabelFrame(self.__master, text="取消委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 2, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 10, pady = 5)

        # 委託序號、委託書號
        column = 0
        self.__radVar = IntVar()

        for _ in 'txtSeqNo', 'txtBookNo':
                # 輸入框
            self.__dOrder[_] = Entry(frame, width = 15, state = 'disabled')
            self.__dOrder[_].grid(column = column+1, row = 0, padx = 10)

            if _ == 'txtSeqNo':
                text = '委託序號'
            elif _ == 'txtBookNo':
                text = '委託書號'

            rb = Radiobutton(frame, style="Pink.TRadiobutton", text = text, variable = self.__radVar, value = column, command = self.__radCall)
            rb.grid(column = column, row = 0, pady = 3, sticky = 'ew')

            column = column + 2
        self.__dOrder['txtSeqNo']['state'] = '!disabled'

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 4, row =  0, padx = 10)

        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 5, row =  0, padx = 10)

    def __radCall(self):
        radSel = self.__radVar.get()
        self.__dOrder['txtSeqNo']['state'] = '!disabled' if radSel == 0 else 'disabled'
        self.__dOrder['txtBookNo']['state'] = '!disabled' if radSel == 2 else 'disabled'

    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇海期帳號！')
        elif self.__radVar.get() == 0 and self.__dOrder['txtSeqNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託序號！')
        elif self.__radVar.get() == 2 and self.__dOrder['txtBookNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託書號！')
        else:
            self.__SendOrder_Click(False)

    # 送出
    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇海期帳號！')
        elif self.__radVar.get() == 0 and self.__dOrder['txtSeqNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託序號！')
        elif self.__radVar.get() == 2 and self.__dOrder['txtBookNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託書號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__radVar.get() == 0:
                message, m_nCode = skO.OverSeaCancelOrderBySeqNo( Global.Global_IID, bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtSeqNo'].get() )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "OverSeaCancelOrderBySeqNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "海期刪單: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

            elif self.__radVar.get() == 2:
                message, m_nCode = skO.OverSeaCancelOrderByBookNo( Global.Global_IID, bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtBookNo'].get() )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "OverSeaCancelOrderByBookNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "海期刪單: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)
# 海外期貨未平倉
class SeaFutureOpenInterest(Frame):
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
        group = LabelFrame(self.__master, text="海外未平倉查詢", style="Pink.TLabelframe")
        group.grid(column = 1, row = 1, padx = 5, pady = 5, sticky = 'ew')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        btnGetOverSeaFutureOpenInterest = Button(frame, style = "Pink.TButton", text = "未平倉查詢")
        btnGetOverSeaFutureOpenInterest["command"] = self.__btnGetOverSeaFutureOpenInterest_Click
        btnGetOverSeaFutureOpenInterest.grid(column = 0, row = 0, padx = 5)

    def __btnGetOverSeaFutureOpenInterest_Click(self):
        try:
            m_nCode = skO.GetOverSeaFutureOpenInterest(Global.Global_IID,self.__dOrder['boxAccount'])
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetOverSeaFutureOpenInterest", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 海外期貨權益數
class SeaFutureRight(Frame):
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
        group = LabelFrame(self.__master, text="海期權益查詢", style="Pink.TLabelframe")
        group.grid(column = 2, row = 1, padx = 5, pady = 5, sticky = 'ew')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        btnGetRequestOverSeaFutureRight = Button(frame, style = "Pink.TButton", text = "權益查詢")
        btnGetRequestOverSeaFutureRight["command"] = self.__btnGetRequestOverSeaFutureRight_Click
        btnGetRequestOverSeaFutureRight.grid(column = 0, row = 0, padx = 5)

    def __btnGetRequestOverSeaFutureRight_Click(self):
        try:
            m_nCode = skO.GetRequestOverSeaFutureRight(Global.Global_IID,self.__dOrder['boxAccount'])
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetRequestOverSeaFutureRight", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 海外期貨商品清單
class OverseaFutures(Frame):
    def __init__(self, master=None, information=None):
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
        group = LabelFrame(self.__master, text="可交易商品", style="Pink.TLabelframe")
        group.grid(column = 1, row = 2, padx = 5, pady = 5, sticky = 'ew')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        btnGetOverseaFutures = Button(frame, style = "Pink.TButton", text = "商品查詢")
        btnGetOverseaFutures["command"] = self.__btnGetOverseaFutures_Click
        btnGetOverseaFutures.grid(column = 0, row = 0, padx = 5)

    def __btnGetOverseaFutures_Click(self):
        try:
            m_nCode = skO.GetOverseaFutures()
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetOverseaFutures", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 海期改價
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
        group = LabelFrame(self.__master, text="海期改價", style="Pink.TLabelframe")
        group.grid(column = 0, row = 3, columnspan = 2,padx = 5, pady = 5, sticky = 'ew')

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

        # 新委託價
        lbOrder = Label(frame, style="Pink.TLabel", text = "新委託價")
        lbOrder.grid(column = 4, row = 0)
            # 輸入框
        self.txtOrder = Entry(frame, width = 10)
        self.txtOrder.grid(column = 4, row = 1, padx = 5)

        # 新委託價分子
        lbOrderNumerator = Label(frame, style="Pink.TLabel", text = "新委託價分子")
        lbOrderNumerator.grid(column = 5, row = 0)
            # 輸入框
        self.txtOrderNumerator = Entry(frame, width = 10)
        self.txtOrderNumerator.grid(column = 5, row = 1, padx = 5)

        # 新委託價分母
        lbOrderDenominator = Label(frame, style="Pink.TLabel", text = "新委託價分母")
        lbOrderDenominator.grid(column = 6, row = 0)
            # 輸入框
        self.txtOrderDenominator = Entry(frame, width = 10)
        self.txtOrderDenominator.grid(column = 6, row = 1, padx = 5)

        # -----------------------------------------------------------------------


        #--------------------------------------------------------------------------------------------------------------------------------------------

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 0, row = 2)
            # 輸入框
        self.boxBuySell = Combobox(frame, width = 8, state='readonly')
        self.boxBuySell['values'] = Config.BUYSELLSET
        self.boxBuySell.grid(column = 0, row = 3, padx = 5)

        # 倉別
        lbNewClose = Label(frame, style="Pink.TLabel", text = "倉別")
        lbNewClose.grid(column = 1, row = 2)
            # 輸入框
        self.boxNewClose = Combobox(frame, width = 8, state='readonly')
        self.boxNewClose['values'] = Config.NEWCLOSESET['sea_future']
        self.boxNewClose.grid(column = 1, row = 3, padx = 5)

        # 委託條件
        lbPeriod = Label(frame, style="Pink.TLabel", text = "委託條件")
        lbPeriod.grid(column = 2, row = 2)
            # 輸入框
        self.boxPeriod = Combobox(frame, width = 8, state='readonly')
        self.boxPeriod['values'] = Config.PERIODSET['sea_future']
        self.boxPeriod.grid(column = 2, row = 3, padx = 5)

        # 委託類型
        lbSpecialTradeType = Label(frame, style="Pink.TLabel", text = "委託類型")
        lbSpecialTradeType.grid(column = 3, row = 2, columnspan = 2)
            # 輸入框
        self.boxSpecialTradeType = Combobox(frame, width = 20, state='readonly')
        self.boxSpecialTradeType['values'] = Config.STRADETYPE['sea_option']
        self.boxSpecialTradeType.grid(column = 3, row = 3, padx = 5, columnspan = 2)

        # 商品代碼2
        lbStockNo2 = Label(frame, style="Pink.TLabel", text = "商品代碼2")
        lbStockNo2.grid(column = 5, row = 2, pady = 3)
            # 輸入框
        self.txtStockNo2 = Entry(frame, width = 10)
        self.txtStockNo2.grid(column = 5, row = 3, padx = 5, pady = 3)

        def __clearr_entry(event, txtYearMonth2):
            self.txtYearMonth2.delete(0, END)
            self.txtYearMonth2['foreground'] = "#000000"
        # 商品年月2
        lbYearMonth2 = Label(frame, style="Pink.TLabel", text = "商品年月2")
        lbYearMonth2.grid(column = 6, row = 2, pady = 3)
            # 輸入框
        self.txtYearMonth2 = Entry(frame, width = 10)
        self.txtYearMonth2.grid(column = 6, row = 3, padx = 5, pady = 3)
        self.txtYearMonth2['foreground'] = "#b3b3b3"
        self.txtYearMonth2.insert(0, "YYYYMM")
        self.txtYearMonth2.bind("<FocusIn>", lambda event: __clearr_entry(event, self.txtYearMonth2))

        # 海期改價同步委託
        btnSendCorrectPrice = Button(frame, style = "Pink.TButton", text = "改價同步委託")
        btnSendCorrectPrice["command"] = self.__btnSendCorrectPrice_Click
        btnSendCorrectPrice.grid(column = 7, row = 0, padx = 5)

        # 海期改價非同步委託
        btnSendCorrectPriceAsync = Button(frame, style = "Pink.TButton", text = "改價非同步委託")
        btnSendCorrectPriceAsync["command"] = self.__btnSendCorrectPriceAsync_Click
        btnSendCorrectPriceAsync.grid(column = 7, row = 1, padx = 5)

        # 價差改價同步委託
        btnSendPriceSpread = Button(frame, style = "Pink.TButton", text = "價差同步改價")
        btnSendPriceSpread["command"] = self.__btnSendPriceSpread_Click
        btnSendPriceSpread.grid(column = 7, row = 2, padx = 5)

        # 價差非同步改價
        btnSendPriceSpreadAsync = Button(frame, style = "Pink.TButton", text = "價差非同步改價")
        btnSendPriceSpreadAsync["command"] = self.__btnSendPriceSpreadAsync_Click
        btnSendPriceSpreadAsync.grid(column = 7, row = 3, padx = 5)

    def __btnSendCorrectPrice_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇海期帳號！')
        else:
            self.__SendCorrectPrice(False)

    def __btnSendCorrectPriceAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇海期帳號！')
        else:
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

            # 建立下單用的參數(OVERSEAFUTUREORDERGW)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.OVERSEAFUTUREORDERFORGW()
            # 填入完整帳號
            oOrder.bstrFullAccount = self.__dOrder['boxAccount']
            # 填入交易所代號
            oOrder.bstrExchangeNo = str(self.txtExchangeNo.get())
            # 填入期權代號
            oOrder.bstrStockNo = str(self.txtStockNo.get())
            # # 填入商品代號2
            # oOrder.bstrStockNo2 = self.txtStockNo2.get()
            # 近月商品年月
            oOrder.bstrYearMonth = str(self.txtYearMonth.get())
            # # 價差商品年月
            # oOrder.bstrYearMonth = self.__dOrder['txtYearMonth'].get()
            # 新委託價
            oOrder.bstrOrderPrice = str(self.txtOrder.get())
            # 新委託價分子
            oOrder.bstrOrderNumerator = str(self.txtOrderNumerator.get())
            # 新委託價分母
            oOrder.bstrOrderDenominator = str(self.txtOrderDenominator.get())
            # 委託書號
            oOrder.bstrBookNo = self.txtBookNo.get()
            # 買賣別
            oOrder.nBuySell = nBuySell
            # 新倉
            oOrder.nNewClose = nNewClose
            # ROD
            oOrder.nTradeType = nTradeType
            # LMT（限價）、MKT（市價）、STL（停損限價）、STP（停損市價）
            oOrder.nSpecialTradeType = nSpecialTradeType

            message, m_nCode = skO.OverSeaCorrectPriceByBookNo(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "OverSeaCorrectPriceSpreadByBookNo", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "海期改價: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)

    def __btnSendPriceSpread_Click(self):
        self.__SendCorrectPriceSpread(False)

    def __btnSendPriceSpreadAsync_Click(self):
        self.__SendCorrectPriceSpread(True)

    def __SendCorrectPriceSpread(self,bAsyncOrder):
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

            # 建立下單用的參數(OVERSEAFUTUREORDERGW)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.OVERSEAFUTUREORDERFORGW()
            # 填入完整帳號
            oOrder.bstrFullAccount = self.__dOrder['boxAccount']
            # 填入交易所代號
            oOrder.bstrExchangeNo = str(self.txtExchangeNo.get())
            # 填入期權代號
            oOrder.bstrStockNo = str(self.txtStockNo.get())
            # # 填入商品代號2
            oOrder.bstrStockNo2 = self.txtStockNo2.get()
            # 近月商品年月
            oOrder.bstrYearMonth = str(self.txtYearMonth.get())
            # # 價差商品年月
            oOrder.bstrYearMonth2 = self.txtYearMonth2.get()
            # 新委託價
            oOrder.bstrOrderPrice = str(self.txtOrder.get())
            # 新委託價分子
            oOrder.bstrOrderNumerator = str(self.txtOrderNumerator.get())
            # 新委託價分母
            oOrder.bstrOrderDenominator = str(self.txtOrderDenominator.get())
            # 委託書號
            oOrder.bstrBookNo = self.txtBookNo.get()
            # 買賣別
            oOrder.sBuySell = nBuySell
            # 新倉
            oOrder.nNewClose = nNewClose
            # ROD
            oOrder.nTradeType = nTradeType
            # LMT（限價）、MKT（市價）、STL（停損限價）、STP（停損市價）
            oOrder.nSpecialTradeType = nSpecialTradeType
            message, m_nCode = skO.OverSeaCorrectPriceSpreadByBookNo(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "OverSeaCorrectPriceSpreadByBookNo", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "海期價差改價: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)


class SeaFutureOrder(Frame):
    def __init__(self, information=None ):
        Frame.__init__(self)
        self.__obj = dict(
            order = Order(master = self, information = information),
            decrease = DecreaseOrder(master = self, information = information),
            cancel = CancelOrder(master = self, information = information ),
            openinterest = SeaFutureOpenInterest(master = self, information = information),
            right = SeaFutureRight(master = self, information = information),
            sea = OverseaFutures(master = self, information = information),
            correct = CorrectPrice(master = self, information = information),
        )

    def SetAccount(self, account):
        for _ in 'order', 'decrease', 'cancel','openinterest','right','sea','correct':
            self.__obj[_].SetAccount(account)

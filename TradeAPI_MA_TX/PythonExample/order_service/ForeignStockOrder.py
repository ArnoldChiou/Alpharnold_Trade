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

class Order(Frame):
    def __init__(self, master=None, information=None):
        Frame.__init__(self)
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            txtID = '',
            boxAccount = '',
        )

        self.__CreateWidget()

    def SetID(self, id):
        self.__dOrder['txtID'] = id

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="複委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 0, padx = 10, pady = 10)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = 'ew')

        # 專戶別
        Label(frame, style="Pink.TLabel", text = "專戶別：").grid(column = 0, row = 0, pady = 3)
            # 輸入框
        boxAccountType = Combobox(frame, width = 10, state='readonly')
        boxAccountType['values'] = Config.ACCOUNTTYPESET
        boxAccountType.grid(column = 1, row = 0, padx = 10)

        Label(frame, style="PinkFiller.TLabel", text = "一一一").grid(column = 2, row = 0)

        # 扣幣別順序
        Label(frame, style="Pink.TLabel", text = "扣幣別順序：  1.").grid(column = 3, row = 0)
            # 輸入框
        boxCurrency1 = Combobox(frame, width = 10, state='readonly')
        boxCurrency1['values'] = Config.CURRENCYSET
        boxCurrency1.grid(column = 4, row = 0, padx = 10)

        Label(frame, style="Pink.TLabel", text = "2.").grid(column = 5, row = 0)
            # 輸入框
        boxCurrency2 = Combobox(frame, width = 10, state='readonly')
        boxCurrency2['values'] = Config.CURRENCYSET
        boxCurrency2.grid(column = 6, row = 0, padx = 10)

        Label(frame, style="Pink.TLabel", text = "3.").grid(column = 7, row = 0)
            # 輸入框
        boxCurrency3 = Combobox(frame, width = 10, state='readonly')
        boxCurrency3['values'] = Config.CURRENCYSET
        boxCurrency3.grid(column = 8, row = 0, padx = 10)
        #--------------------------------------------------------------------------------------------------------------------------------------------
        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 1, padx = 10, pady = 5, sticky = 'ew')

        # 交易所
        Label(frame, style="Pink.TLabel", text = "交易所").grid(column = 0, row = 1, pady = 3)
        # 輸入框
        boxExchangeNo = Combobox(frame, width = 10, state='readonly')
        boxExchangeNo['values'] = Config.EXCHANGENOSET
        boxExchangeNo.grid(column = 0, row = 2, padx = 10)

        # 商品代碼
        Label(frame, style="Pink.TLabel", text = "商品代碼").grid(column = 1, row = 1)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 1, row = 2, padx = 10)

        # 買賣別
        Label(frame, style="Pink.TLabel", text = "買賣別").grid(column = 2, row = 1)
            # 輸入框
        boxBuySell = Combobox(frame, width = 10, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 2, row = 2, padx = 10)

        # 委託價
        Label(frame, style="Pink.TLabel", text = "委託價").grid(column = 3, row = 1)
            # 輸入框
        txtPrice = Entry(frame, width = 8)
        txtPrice.grid(column = 3, row = 2, padx = 10)

        # 委託量
        Label(frame, style="Pink.TLabel", text = "委託量").grid(column = 4, row = 1)
        # 輸入框
        txtQty = Entry(frame, width = 8)
        txtQty.grid(column = 4, row = 2, padx = 10)

         # 同步與否
        lbReserved = Label(frame, style="Pink.TLabel", text = "同步與否")
        lbReserved.grid(column = 8, row = 1)
        # 輸入框
        boxASYNC = Combobox(frame, width = 8, state='readonly')
        boxASYNC['values'] = Config.ASYNC
        boxASYNC.grid(column = 8, row = 2, padx = 10)


        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "送出委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 9, row =  2, padx = 10)
        
        #SendOrderAsync
        #self.btnSendOrderAsync = Button(self)
        #self.btnSendOrderAsync["text"] = "非同步送單"
        #self.btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        #self.btnSendOrderAsync.grid(column = 7, row = 4)

        self.__dOrder['boxAccountType'] = boxAccountType
        self.__dOrder['boxCurrency1'] = boxCurrency1
        self.__dOrder['boxCurrency2'] = boxCurrency2
        self.__dOrder['boxCurrency3'] = boxCurrency3

        self.__dOrder['boxExchangeNo'] = boxExchangeNo
        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['txtPrice'] = txtPrice
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['boxASYNC'] = boxASYNC

    # 4.下單送出
    # nAccountType, Currency1, Currency2, Currency3, bstrExchangeNo, sBuySell
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇複委託帳號！')
        else:
            if self.__dOrder['boxASYNC'].get() == "同步":
                bAsyncOrder = 0
                self.__SendOrder_Click(False)
            elif self.__dOrder['boxASYNC'].get() == "非同步":
                bAsyncOrder = 1
                self.__SendOrder_Click(True)
            

    def __btnSendOrderAsync_Click(self):
        self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__dOrder['boxAccountType'].get() == "外幣專戶":
                nAccountType = 1
            elif self.__dOrder['boxAccountType'].get() == "台幣專戶":
                nAccountType = 2

            if self.__dOrder['boxExchangeNo'].get() == "美股":
                bstrExchangeNo = 'US'

            if self.__dOrder['boxBuySell'].get() == "買進":
                sBuySell = 0
            elif self.__dOrder['boxBuySell'].get() == "賣出":
                sBuySell = 1

            # 建立下單用的參數(FOREIGNORDER)物件(下單時要填股票代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.FOREIGNORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount = self.__dOrder['boxAccount']
            # 專戶別
            oOrder.nAccountType = nAccountType
            # 扣款幣別(順序)
            oOrder.bstrCurrency1 = self.__dOrder['boxCurrency1'].get()
            oOrder.bstrCurrency2 = self.__dOrder['boxCurrency2'].get()
            oOrder.bstrCurrency3 = self.__dOrder['boxCurrency3'].get()
            # 交易所
            oOrder.bstrExchangeNo = bstrExchangeNo
            # 填入股票代號
            oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
            # 買賣別
            oOrder.sBuySell = sBuySell
            # 委託價
            oOrder.bstrPrice = self.__dOrder['txtPrice'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())

            message, m_nCode = skO.SendForeignStockOrder(self.__dOrder['txtID'], bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendForeignStockOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "複委託: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

class CancelOrder():
    def __init__(self, master=None, information=None):
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
        # UI variable
        self.__dOrder = dict(
            listInformation = information,
            txtID = '',
            boxAccount = '',
        )

        self.__CreateWidget()

    def SetID(self, id):
        self.__dOrder['txtID'] = id

    def SetAccount(self, account):
        self.__dOrder['boxAccount'] = account

    def __CreateWidget(self):
        group = LabelFrame(self.__master, text="取消委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'ew')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 10, pady = 5)

        # 交易所
        Label(frame, style="Pink.TLabel", text = "交易所").grid(column = 0, row = 0)
        Label(frame, style="PinkFiller.TLabel", text = "一一").grid(column = 1, row = 0)
            # 輸入框
        self.__dOrder['boxExchangeNo'] = Combobox(frame, width = 10, state='readonly')
        self.__dOrder['boxExchangeNo']['values'] = Config.EXCHANGENOSET
        self.__dOrder['boxExchangeNo'].grid(column = 0, row = 1, padx = 10)
        Label(frame, style="PinkFiller.TLabel", text = "一一").grid(column = 1, row = 0)

        # 委託序號、委託書號
        row = 0
        self.__radVar = IntVar()

        for _ in 'txtSeqNo', 'txtBookNo':
                # 輸入框
            self.__dOrder[_] = Entry(frame, width = 18, state = 'disabled')
            self.__dOrder[_].grid(column = 3, row = row, padx = 10)

            if _ == 'txtSeqNo':
                text = '委託序號'
            elif _ == 'txtBookNo':
                text = '委託書號'

            rb = Radiobutton(frame, style="Pink.TRadiobutton", text = text, variable = self.__radVar, value = row, command = self.__radCall)
            rb.grid(column = 2, row = row, pady = 3, sticky = 'ew')

            row = row + 1
        self.__dOrder['txtSeqNo']['state'] = '!disabled'

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "送出")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 4, row =  1, padx = 50)

    def __radCall(self):
        radSel = self.__radVar.get()
        self.__dOrder['txtSeqNo']['state'] = '!disabled' if radSel == 0 else 'disabled'
        self.__dOrder['txtBookNo']['state'] = '!disabled' if radSel == 1 else 'disabled'

    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇複委託帳號！')
        elif self.__radVar.get() == 0 and self.__dOrder['txtSeqNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託序號！')
        elif self.__radVar.get() == 1 and self.__dOrder['txtBookNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託書號！')
        else:
            self.__SendOrder_Click(False)

    def __SendOrder_Click(self, bAsyncOrder):
        # 交易所
        if self.__dOrder['boxExchangeNo'].get() == "美股":
            bstrExchangeNo = 'US'

        try:
            if self.__radVar.get() == 0:
                message, m_nCode = skO.CancelForeignStockOrderBySeqNo( self.__dOrder['txtID'], bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtSeqNo'].get(), bstrExchangeNo )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelForeignStockOrderBySeqNo", self.__dOrder['listInformation'])
            elif self.__radVar.get() == 1:
                message, m_nCode = skO.CancelForeignStockOrderByBookNo( self.__dOrder['txtID'], bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtBookNo'].get(), bstrExchangeNo )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelForeignStockOrderByBookNo", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

class ForeignStockOrder(Frame):
    def __init__(self, information=None):
        Frame.__init__(self)
        self.__obj = dict(
            order = Order(master = self, information = information),
            cancel = CancelOrder(master = self, information = information),
        )

    def SetID(self, id):
        for _ in 'order', 'cancel':
            self.__obj[_].SetID(id)

    def SetAccount(self, account):
        for _ in 'order', 'cancel':
            self.__obj[_].SetAccount(account)

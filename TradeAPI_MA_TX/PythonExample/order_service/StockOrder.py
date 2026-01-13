# 先把API com元件初始化
import os
import Global
# 第二種讓群益API元件可導入Python code內用的物件宣告
import comtypes.client as cc
#comtypes.client.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\SKCOM.dll')
import comtypes.gen.SKCOMLib as sk
skC = Global.skC
skO = Global.skO

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
        group = LabelFrame(self.__master, text="證券委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 0,columnspan = 5,  padx = 10, pady = 10)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = 'ew')

        # 商品代碼
        Label(frame, style="Pink.TLabel", text = "商品代碼").grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 0, row = 1, padx = 10, pady = 3)

        # 上市櫃-興櫃
        Label(frame, style="Pink.TLabel", text = "上市櫃-興櫃").grid(column = 1, row = 0)
            #輸入框
        boxPrime = Combobox(frame, width = 10, state='readonly')
        boxPrime['values'] = Config.PRIMESET
        boxPrime.grid(column = 1, row = 1, padx = 10)

        # 買賣別
        Label(frame, style="Pink.TLabel", text = "買賣別").grid(column = 2, row = 0)
            # 輸入框
        boxBuySell = Combobox(frame, width = 10, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 2, row = 1, padx = 10)

        # 委託條件
        Label(frame, style="Pink.TLabel", text = "委託條件").grid(column = 3, row = 0)
            # 輸入框
        boxPeriod = Combobox(frame, width = 10, state='readonly')
        boxPeriod['values'] = Config.PERIODSET['stock']
        boxPeriod.grid(column = 3, row = 1, padx = 10)

        # 當沖與否
        Label(frame, style="Pink.TLabel", text = "當沖與否").grid(column = 4, row = 0)
            # 輸入框
        boxFlag = Combobox(frame, width = 10, state='readonly')
        boxFlag['values'] = Config.FLAGSET['stock']
        boxFlag.grid(column = 4, row = 1, padx = 10)

        # 委託時效
        Label(frame, style="Pink.TLabel", text = "委託時效").grid(column = 5, row = 0)
            # 輸入框
        boxTradeType = Combobox(frame, width = 10, state='readonly')
        boxTradeType['values'] = Config.PERIODSET['stock_tradetype']
        boxTradeType.grid(column = 5, row = 1, padx = 10)

        # 限市價
        Label(frame, style="Pink.TLabel", text = "限市價").grid(column = 6, row = 0)
            # 輸入框
        boxSpecialTradeType = Combobox(frame, width = 10, state='readonly')
        boxSpecialTradeType['values'] = Config.STRADETYPE['stock']
        boxSpecialTradeType.grid(column = 6, row = 1, padx = 10)

        # 委託價
        Label(frame, style="Pink.TLabel", text = "委託價").grid(column = 7, row = 0)
            # 輸入框
        txtPrice = Entry(frame, width = 15)
        txtPrice.grid(column = 7, row = 1, padx = 10)

        # 委託量
        Label(frame, style="Pink.TLabel", text = "委託量").grid(column = 8, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 8, row = 1, padx = 10)

        # 同步/非同步
        Label(frame, style="Pink.TLabel", text = "同步/非同步").grid(column = 9, row = 0)
            # 輸入框
        boxAsync = Combobox(frame, width = 10, state='readonly')
        boxAsync['values'] = Config.ASYNC
        boxAsync.grid(column = 9, row = 1, padx = 10)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "送出委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 10, row =  1, padx = 10)


        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['boxPrime'] = boxPrime
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxFlag'] = boxFlag
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['boxTradeType'] = boxTradeType
        self.__dOrder['boxSpecialTradeType'] = boxSpecialTradeType
        self.__dOrder['txtPrice'] = txtPrice
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['boxAsync'] = boxAsync

    # 4.下單送出
    # sPrime, sPeriod, sFlag, sBuySell,
    def __btnSendOrder_Click(self):
        try:
            if self.__dOrder['boxAccount'] == '':
                messagebox.showerror("error！", '請選擇證券帳號！')
            else:
                if self.__dOrder['boxPrime'].get() == "上市櫃":
                    sPrime = 0
                elif self.__dOrder['boxPrime'].get() == "興櫃":
                    sPrime = 1

                if self.__dOrder['boxPeriod'].get() == "盤中":
                    sPeriod = 0
                elif self.__dOrder['boxPeriod'].get() == "盤後":
                    sPeriod = 1
                elif self.__dOrder['boxPeriod'].get() == "零股":
                    sPeriod = 2
                elif self.__dOrder['boxPeriod'].get() == "盤中零股":
                    sPeriod = 4

                if self.__dOrder['boxFlag'].get() == "現股":
                    sFlag = 0
                elif self.__dOrder['boxFlag'].get() == "融資":
                    sFlag = 1
                elif self.__dOrder['boxFlag'].get() == "融券":
                    sFlag = 2
                elif self.__dOrder['boxFlag'].get() == "無券":
                    sFlag = 3

                if self.__dOrder['boxBuySell'].get() == "買進":
                    sBuySell = 0
                elif self.__dOrder['boxBuySell'].get() == "賣出":
                    sBuySell = 1

                if self.__dOrder['boxTradeType'].get() == "ROD":
                    nTradeType = 0
                elif self.__dOrder['boxTradeType'].get() == "IOC":
                    nTradeType = 1
                elif self.__dOrder['boxTradeType'].get() == "FOK":
                    nTradeType = 2

                if self.__dOrder['boxSpecialTradeType'].get() == "市價":
                    nSpecialTradeType = 1
                elif self.__dOrder['boxSpecialTradeType'].get() == "限價":
                    nSpecialTradeType = 2

                if self.__dOrder['boxAsync'].get() == "同步":
                    bAsyncOrder = 0
                elif self.__dOrder['boxAsync'].get() == "非同步":
                    bAsyncOrder = 1

                # 建立下單用的參數(STOCKORDER)物件(下單時要填股票代號,買賣別,委託價,數量等等的一個物件)
                oOrder = sk.STOCKORDER()
                # 填入完整帳號
                oOrder.bstrFullAccount = self.__dOrder['boxAccount']
                # 填入股票代號
                oOrder.bstrStockNo = self.__dOrder['txtStockNo'].get()
                # 上市、上櫃、興櫃
                oOrder.sPrime = sPrime
                # 盤中、盤後、零股
                oOrder.sPeriod = sPeriod
                # 現股、融資、融券、無券
                oOrder.sFlag = sFlag
                # 買賣別
                oOrder.sBuySell = sBuySell
                # ROD、IOC、FOK
                oOrder.nTradeType = nTradeType
                # 市價、限價
                oOrder.nSpecialTradeType = nSpecialTradeType
                # 委託價
                oOrder.bstrPrice = self.__dOrder['txtPrice'].get()
                # 委託數量
                oOrder.nQty = int(self.__dOrder['txtQty'].get())

            if sPeriod != 4 :
                message, m_nCode = skO.SendStockOrder(self.__dOrder['txtID'], bAsyncOrder, oOrder)
                self.__oMsg.SendReturnMessage("Order", m_nCode, "SendStockOrder:", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "證券委託: " + str(message)                
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
                    
            elif sPeriod == 4 :
                oOrder.sFlag = 0
                oOrder.nTradeType = 0
                oOrder.nSpecialTradeType =2
                message, m_nCode = skO.SendStockOddLotOrder(self.__dOrder['txtID'], bAsyncOrder, oOrder)
                self.__oMsg.SendReturnMessage("Order", m_nCode, "SendStockOddLotOrder:", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "證券盤中零股委託: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

            
        except Exception as e:
                        messagebox.showerror("error！", e)

class DecreaseOrder():
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
        group = LabelFrame(self.__master, text="委託減量", style="Pink.TLabelframe")
        group.grid(column = 0, row = 1,columnspan = 5, padx = 10, pady = 10, sticky = 'ew')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 10, pady = 5)

        # 委託序號
        Label(frame, style="Pink.TLabel", text = "委託序號").grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtSqlNo = Entry(frame, width = 18)
        txtSqlNo.grid(column = 1, row = 0, padx = 10)

        Label(frame, style="PinkFiller.TLabel", text = "一一").grid(column = 2, row = 0)

        # 欲減少的數量
        Label(frame, style="Pink.TLabel", text = "欲減少的數量").grid(column = 3, row = 0)
            # 輸入框
        txtDecreaseQty = Entry(frame, width = 10)
        txtDecreaseQty.grid(column = 4, row = 0, padx = 10)

        #同步/非同步
        Label(frame, style="Pink.TLabel", text = "同步/非同步").grid(column = 5, row = 0)
            # 輸入框
        boxAsync = Combobox(frame, width = 10, state='readonly')
        boxAsync['values'] = Config.ASYNC
        boxAsync.grid(column = 6, row = 0, padx = 10)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "送出")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 7, row =  0, padx = 10)

        self.__dOrder['txtSqlNo'] = txtSqlNo
        self.__dOrder['txtDecreaseQty'] = txtDecreaseQty
        self.__dOrder['boxAsync'] = boxAsync

    # 送出
    def __btnSendOrder_Click(self):
        try:
            if self.__dOrder['boxAccount'] == '':
                messagebox.showerror("error！", '請選擇證券帳號！')
            else:
                if self.__dOrder['boxAsync'].get() == "同步":
                        bAsyncOrder = 0
                elif self.__dOrder['boxAsync'].get() == "非同步":
                        bAsyncOrder = 1

                message, m_nCode = skO.DecreaseOrderBySeqNo( self.__dOrder['txtID'], bAsyncOrder, self.__dOrder['boxAccount'],\
                        self.__dOrder['txtSqlNo'].get(), int(self.__dOrder['txtDecreaseQty'].get()) )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "DecreaseOrderBySeqNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "證券減量: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)

class CorrectPriceOrder():
    def __init__(self, master=None, information=None):
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
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
        group = LabelFrame(self.__master, text="改價委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 2,  columnspan = 10, padx = 10, pady = 10, sticky = E+W)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 10, pady = 5)

        # 委託序號、委託書號
        row = 0
        self.__radVar = IntVar()

        for _ in 'txtSeqNo', 'txtBookNo':
                # 輸入框
            self.__dOrder[_] = Entry(frame, width = 18, state = 'disabled')
            self.__dOrder[_].grid(column = 1, row = row, padx = 10)

            if _ == 'txtSeqNo':
                text = '委託序號'
            elif _ == 'txtBookNo':
                text = '委託書號'

            rb = Radiobutton(frame, style="Pink.TRadiobutton", text = text, variable = self.__radVar, value = row, command = self.__radCall)
            rb.grid(column = 0, row = row, pady = 3, sticky = 'e')

            row = row + 1

        self.__dOrder['txtSeqNo']['state'] = '!disabled'

        #同步/非同步
        Label(frame, style="Pink.TLabel", text = "同步/非同步").grid(column = 2, row = 0,sticky='w')
        # 輸入框
        boxAsync = Combobox(frame, width = 10, state='readonly')
        boxAsync['values'] = Config.ASYNC
        boxAsync.grid(column = 3, row = 0, sticky='w')

        # 欲更改的價格
        Label(frame, style="Pink.TLabel", text = "欲更改價格").grid(column = 2, row = 1, sticky='w')
            # 輸入框
        txtCorrectPrice = Entry(frame, width = 10)
        txtCorrectPrice.grid(column = 3, row = 1, sticky='w')

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "送出")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 3, row =  2, sticky='w')

        self.__dOrder['boxAsync'] = boxAsync
        self.__dOrder['txtCorrectPrice'] = txtCorrectPrice

    def __radCall(self):
        radSel = self.__radVar.get()
        self.__dOrder['txtSeqNo']['state'] = '!disabled' if radSel == 0 else 'disabled'
        self.__dOrder['txtBookNo']['state'] = '!disabled' if radSel == 1 else 'disabled'


    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        elif self.__radVar.get() == 0 and self.__dOrder['txtSeqNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲改價的委託序號！')
        elif self.__radVar.get() == 1 and self.__dOrder['txtBookNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲改價的委託書號！')
        elif self.__dOrder['txtCorrectPrice'].get() == '':
            messagebox.showerror("error！", '請輸入欲更改價格！')
        else:
            self.__SendOrder_Click(False)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__dOrder['boxAsync'].get() == "同步":
                        bAsyncOrder = 0
            elif self.__dOrder['boxAsync'].get() == "非同步":
                        bAsyncOrder = 1

            if self.__radVar.get() == 0:
                message, m_nCode = skO.CorrectPriceBySeqNo( self.__dOrder['txtID'], bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtSeqNo'].get(), self.__dOrder['txtCorrectPrice'].get(), 0)
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CorrectPriceOrderBySeqNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "證券序號改價: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
            elif self.__radVar.get() == 1:
                message, m_nCode = skO.CorrectPriceByBookNo( self.__dOrder['txtID'], bAsyncOrder, self.__dOrder['boxAccount'], "TS",\
                    self.__dOrder['txtBookNo'].get(), self.__dOrder['txtCorrectPrice'].get(), 0)
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CorrectPriceOrderByBookNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "證券書號改價: " + str(message)
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
        group.grid(column = 2, row = 2,  columnspan = 5,padx = 10, pady = 10, sticky = E+W)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 10, pady = 5)

        # 商品代碼、委託序號、委託書號
        row = 0
        self.__radVar = IntVar()

        for _ in 'txtStockNo', 'txtSeqNo', 'txtBookNo':
                # 輸入框
            self.__dOrder[_] = Entry(frame, width = 18, state = 'disabled')
            self.__dOrder[_].grid(column = 1, row = row, padx = 10)

            if _ == 'txtStockNo':
                text = '商品代碼'
            elif _ == 'txtSeqNo':
                text = '委託序號'
            elif _ == 'txtBookNo':
                text = '委託書號'

            rb = Radiobutton(frame, style="Pink.TRadiobutton", text = text, variable = self.__radVar, value = row, command = self.__radCall)
            rb.grid(column = 0, row = row, pady = 3, sticky = 'ew')

            row = row + 1
        self.__dOrder['txtStockNo']['state'] = '!disabled'

        #同步/非同步
        Label(frame, style="Pink.TLabel", text = "同步/非同步").grid(column = 2, row = 0,sticky='w')
        # 輸入框
        boxAsync = Combobox(frame, width = 10, state='readonly')
        boxAsync['values'] = Config.ASYNC
        boxAsync.grid(column = 3, row = 0, sticky='w')


        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "送出")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 3, row =  2, sticky='w')

        self.__dOrder['boxAsync'] = boxAsync

    def __radCall(self):
        radSel = self.__radVar.get()
        self.__dOrder['txtStockNo']['state'] = '!disabled' if radSel == 0 else 'disabled'
        self.__dOrder['txtSeqNo']['state'] = '!disabled' if radSel == 1 else 'disabled'
        self.__dOrder['txtBookNo']['state'] = '!disabled' if radSel == 2 else 'disabled'


    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        elif self.__radVar.get() == 0 and self.__dOrder['txtStockNo'].get() == '':
            ans = messagebox.askquestion("提示", '未輸入商品代碼會刪除所有委託單，是否刪單？')
            if ans == 'yes':
                self.__SendOrder_Click(False)
            else:
                return
        elif self.__radVar.get() == 1 and self.__dOrder['txtSeqNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託序號！')
        elif self.__radVar.get() == 2 and self.__dOrder['txtBookNo'].get() == '':
            messagebox.showerror("error！", 'No BookNO!委託書號！')
        else:
            self.__SendOrder_Click(False)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__dOrder['boxAsync'].get() == "同步":
                        bAsyncOrder = 0
            elif self.__dOrder['boxAsync'].get() == "非同步":
                        bAsyncOrder = 1

            if self.__radVar.get() == 0:
                message, m_nCode = skO.CancelOrderByStockNo( self.__dOrder['txtID'], bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtStockNo'].get() )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelOrderByStockNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "證券商品代碼刪單: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
            elif self.__radVar.get() == 1:
                message, m_nCode = skO.CancelOrderBySeqNo( self.__dOrder['txtID'], bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtSeqNo'].get() )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelOrderBySeqNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "證券序號刪單: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
            elif self.__radVar.get() == 2:
                message, m_nCode = skO.CancelOrderByBookNo( self.__dOrder['txtID'], bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtBookNo'].get() )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelOrderByBookNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "證券書號刪單: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)


class GetRealBalanceOrder():
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
        group = LabelFrame(self.__master, text="證券即時庫存", style="Pink.TLabelframe")
        group.grid(column = 0, row = 3, padx = 10, pady = 3, sticky = E+W)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0,  padx = 10, pady = 3)


        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "開始查詢")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 2, row =  2, padx = 10,pady = 3)

        ##訊息欄
        #self.listInformation = Listbox(frame, height = 5)
        #self.listInformation.grid(column = 0, columnspan = 5, row = 3, sticky = 'ew')

        #sb = Scrollbar(frame)
        #self.listInformation.config(yscrollcommand = sb.set)
        #sb.config(command = self.listInformation.yview)
        #sb.grid(row = 3, column = 5, sticky = 'ns')

        #sb = Scrollbar(frame, orient = 'horizontal')
        #self.listInformation.config(xscrollcommand = sb.set)
        #sb.config(command = self.listInformation.xview)
        #sb.grid(row = 3, column = 0, columnspan = 5, sticky = 'ew')
    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
            try:
                m_nCode = skO.GetRealBalanceReport( self.__dOrder['txtID'], self.__dOrder['boxAccount'])
                self.__oMsg.SendReturnMessage("Order", m_nCode, "GetRealBalanceReport", self.__dOrder['listInformation'])
            except Exception as e:
                messagebox.showerror("error！", e)


class GetRequestProfitOrder():
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
        group = LabelFrame(self.__master, text="證券即時損益", style="Pink.TLabelframe")
        group.grid(column = 1, row = 3, padx = 10, pady = 3, sticky = E+W)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0,padx = 10, pady = 3)


        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "開始查詢")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 2, row =  2,padx = 10,pady = 3)


    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
            try:
                m_nCode = skO.GetRequestProfitReport( self.__dOrder['txtID'], self.__dOrder['boxAccount'])
                self.__oMsg.SendReturnMessage("Order", m_nCode, "GetRequestProfitReport", self.__dOrder['listInformation'])
            except Exception as e:
                messagebox.showerror("error！", e)

class GetMarginPurchaseAmountLimitOrder():
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
        group = LabelFrame(self.__master, text="資券配額查詢", style="Pink.TLabelframe")
        group.grid(column = 2, row = 3, padx = 10, pady = 3, sticky = E+W)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0,padx = 10, pady = 3)

        # 商品代碼
        Label(frame, style="Pink.TLabel", text = "商品代碼").grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 1, row = 0, padx = 10, pady = 3)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "開始查詢")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 2, row =  0,padx = 10,pady = 3)

        self.__dOrder['txtStockNo'] = txtStockNo
        #股票代號



    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':

            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
             try:
                    m_nCode = skO.GetMarginPurchaseAmountLimit( self.__dOrder['txtID'], self.__dOrder['boxAccount'],\
                        self.__dOrder['txtStockNo'].get() )
                    self.__oMsg.SendReturnMessage("Order", m_nCode, "GetMarginPurchaseAmountLimit", self.__dOrder['listInformation'])
             except Exception as e:
                    messagebox.showerror("error！", e)

class GetBalanceQuery():
    def __init__(self, master=None, information=None):
        self.__master = master
        self.__oMsg = MessageControl.MessageControl()
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
        group = LabelFrame(self.__master, text="證券集保庫存", style="Pink.TLabelframe")
        group.grid(column = 3, row = 3, padx = 10, pady = 3, sticky = E+W)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0,padx = 10, pady = 3)

        # 商品代碼
        Label(frame, style="Pink.TLabel", text = "商品代碼").grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 10)
        txtStockNo.grid(column = 1, row = 0, padx = 10, pady = 3)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "開始查詢")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 2, row =  0,padx = 10,pady = 3)

        self.__dOrder['txtStockNo'] = txtStockNo
        #股票代號



    # 送出
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':

            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
             try:
                    m_nCode = skO.GetBalanceQuery( self.__dOrder['txtID'], self.__dOrder['boxAccount'],\
                        self.__dOrder['txtStockNo'].get() )
                    self.__oMsg.SendReturnMessage("Order", m_nCode, "GetBalanceQuery", self.__dOrder['listInformation'])
             except Exception as e:
                    messagebox.showerror("error！", e)



#class StockderEvents:
#    #def __init__(self):
#    #    #初始化，設定一些變數供使用

#    #    self.RealBalance=[]

#    def OnRealBalanceReport(self,bstrData):
#        strMsg = bstrData.split(',')
#        self.__oMsg.WriteMessage(strMsg,self.__dOrder['listInformation'])
#        WriteMessage(strMsg,GlobalListInformation)

#    def OnBalanceQuery(self, bstrData):
#        strMsg = bstrData.split(',')
#        m_nCode = skO.OnBalanceQuery(strMsg)
#        self.__oMsg.SendReturnMessage("Order", m_nCode, "OnBalanceQuery", self.__dOrder['listInformation'])
#        WriteMessage(strMsg,GlobalListInformation)

#    def OnRequestProfitReport(self, bstrData):
#        strMsg = bstrData.split(',')
#        m_nCode = skO.OnRequestProfitReport(strMsg)
#        self.__oMsg.SendReturnMessage("Order", m_nCode, "OnRequestProfitReport", self.__dOrder['listInformation'])
#        WriteMessage(strMsg,GlobalListInformation)

#    def OnMarginPurchaseAmountLimit(self,bstrData):
#        strMsg = bstrData.split(',')
#        self.oMsg.WriteMessage(strMsg,self.__dOrder['listInformation'])
#        WriteMessage(strMsg,GlobalListInformation)

#SKQuoteEvent=StockderEvents()
#SKQuoteLibEventHandler = cc.GetEvents(skO, SKQuoteEvent)



class StockOrder(Frame):
    def __init__(self, information=None):
        Frame.__init__(self)
        self.__obj = dict(
            order = Order(master = self, information = information),
            decrease = DecreaseOrder(master = self, information = information),
            correctprice = CorrectPriceOrder(master = self, information = information),
            cancel = CancelOrder(master = self, information = information),
            GetRealBalance = GetRealBalanceOrder(master = self, information = information),
            GetRequestProfit = GetRequestProfitOrder(master = self, information = information),
            GetMarginPurchaseAmountLimit = GetMarginPurchaseAmountLimitOrder(master = self, information = information),
            GetBalanceQ = GetBalanceQuery(master = self, information = information),
        )

    def SetID(self, id):
        for _ in 'order', 'decrease', 'correctprice', 'cancel','GetRealBalance','GetRequestProfit','GetMarginPurchaseAmountLimit','GetBalanceQ':
            self.__obj[_].SetID(id)

    def SetAccount(self, account):
        for _ in 'order', 'decrease', 'correctprice', 'cancel','GetRealBalance','GetRequestProfit','GetMarginPurchaseAmountLimit','GetBalanceQ':
            self.__obj[_].SetAccount(account)

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
#import comtypes.client
#comtypes.client.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\SKCOM.dll')

import comtypes.gen.SKCOMLib as sk
# import comtypes.client

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
        group = LabelFrame(self.__master, text="期貨委託", style="Pink.TLabelframe")
        group.grid(column = 0, row = 0, padx = 5, pady = 5,columnspan = 2,sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'ew')

        # 商品代碼
        Label(frame, style="Pink.TLabel", text = "商品代碼").grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtStockNo = Entry(frame, width = 5)
        txtStockNo.grid(column = 0, row = 1, padx = 5, pady = 3)

        # 買賣別
        Label(frame, style="Pink.TLabel", text = "買賣別").grid(column = 1, row = 0)
            # 輸入框
        boxBuySell = Combobox(frame, width = 5, state='readonly')
        boxBuySell['values'] = Config.BUYSELLSET
        boxBuySell.grid(column = 1, row = 1, padx = 5)

        # 委託條件
        Label(frame, style="Pink.TLabel", text = "委託條件").grid(column = 2, row = 0)
            # 輸入框
        boxPeriod = Combobox(frame, width = 10, state='readonly')
        boxPeriod['values'] = Config.PERIODSET['future']
        boxPeriod.grid(column = 2, row = 1, padx = 5)

        # 當沖與否
        Label(frame, style="Pink.TLabel", text = "當沖與否").grid(column = 3, row = 0)
            # 輸入框
        boxFlag = Combobox(frame, width = 10, state='readonly')
        boxFlag['values'] = Config.FLAGSET['future']
        boxFlag.grid(column = 3, row = 1, padx = 5)

        # 委託價
        Label(frame, style="Pink.TLabel", text = "委託價").grid(column = 4, row = 0)
            # 輸入框
        txtPrice = Entry(frame, width = 12)
        txtPrice.grid(column = 4, row = 1, padx = 5)

        # 委託量
        Label(frame, style="Pink.TLabel", text = "委託量").grid(column = 5, row = 0)
            # 輸入框
        txtQty = Entry(frame, width = 10)
        txtQty.grid(column = 5, row = 1, padx = 5)

        # 倉別
        Label(frame, style="Pink.TLabel", text = "倉別").grid(column = 6, row = 0)
            # 輸入框
        boxNewClose = Combobox(frame, width = 5, state='readonly')
        boxNewClose['values'] = Config.NEWCLOSESET['future']
        boxNewClose.grid(column = 6, row = 1, padx = 5)

        # 盤別
        Label(frame, style="Pink.TLabel", text = "盤別").grid(column = 7, row = 0)
            # 輸入框
        boxReserved = Combobox(frame, width = 10, state='readonly')
        boxReserved['values'] = Config.RESERVEDSET
        boxReserved.grid(column = 7, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 8, row =  0, padx = 5)

        btnAsyncSendOrder = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnAsyncSendOrder["command"] = self.__btnAsyncSendOrder_Click
        btnAsyncSendOrder.grid(column = 8, row =  1, padx = 5)

        btnSendOrderCLR = Button(frame, style = "Pink.TButton", text = "同步委託(含倉別/盤別)")
        btnSendOrderCLR["command"] = self.__btnSendOrderCLR_Click
        btnSendOrderCLR.grid(column = 9, row =  0, padx = 5)

        btnAsyncSendOrderCLR = Button(frame, style = "Pink.TButton", text = "非同步委託(含倉別/盤別)")
        btnAsyncSendOrderCLR["command"] = self.__btnAsyncSendOrderCLR_Click
        btnAsyncSendOrderCLR.grid(column = 9, row =  1, padx = 5)

        self.__dOrder['txtStockNo'] = txtStockNo
        self.__dOrder['boxPeriod'] = boxPeriod
        self.__dOrder['boxFlag'] = boxFlag
        self.__dOrder['boxBuySell'] = boxBuySell
        self.__dOrder['txtPrice'] = txtPrice
        self.__dOrder['txtQty'] = txtQty
        self.__dOrder['boxNewClose'] = boxNewClose
        self.__dOrder['boxReserved'] = boxReserved

    # 4.下單送出
    # sBuySell, sTradeType, sDayTrade, sNewClose, sReserved
    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnAsyncSendOrder_Click(self):
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

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

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
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # 委託價
            oOrder.bstrPrice = self.__dOrder['txtPrice'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())

            message, m_nCode = skO.SendFutureOrder(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendFutureOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "期貨委託: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

    def __btnSendOrderCLR_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrderCLR_Click(False)

    def __btnAsyncSendOrderCLR_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        else:
            self.__SendOrderCLR_Click(True)

    def __SendOrderCLR_Click(self, bAsyncOrder):
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

            if self.__dOrder['boxFlag'].get() == "非當沖":
                sDayTrade = 0
            elif self.__dOrder['boxFlag'].get() == "當沖":
                sDayTrade = 1

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
            # 非當沖、當沖
            oOrder.sDayTrade = sDayTrade
            # 委託價
            oOrder.bstrPrice = self.__dOrder['txtPrice'].get()
            # 委託數量
            oOrder.nQty = int(self.__dOrder['txtQty'].get())
            # 新倉、平倉、自動
            oOrder.sNewClose = sNewClose
            # 盤中、T盤預約
            oOrder.sReserved = sReserved

            message, m_nCode = skO.SendFutureOrderCLR(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendFutureOrderCLR", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "期貨委託帶倉別/盤別: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

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
        group.grid(column = 0, row = 1, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 委託序號
        Label(frame, style="Pink.TLabel", text = "委託序號").grid(column = 0, row = 0, pady = 3)
            # 輸入框
        txtSqlNo = Entry(frame, width = 15)
        txtSqlNo.grid(column = 1, row = 0, padx = 5)

        # 欲減少的數量
        Label(frame, style="Pink.TLabel", text = "欲減少的數量").grid(column = 3, row = 0)
            # 輸入框
        txtDecreaseQty = Entry(frame, width = 10)
        txtDecreaseQty.grid(column = 4, row = 0, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 5, row =  0, padx = 5)

        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 6, row =  0, padx = 5)


        self.__dOrder['txtSqlNo'] = txtSqlNo
        self.__dOrder['txtDecreaseQty'] = txtDecreaseQty

    # 送出
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
            message, m_nCode = skO.DecreaseOrderBySeqNo( Global.Global_IID, bAsyncOrder, self.__dOrder['boxAccount'],\
                self.__dOrder['txtSqlNo'].get(), int(self.__dOrder['txtDecreaseQty'].get()) )
            self.__oMsg.SendReturnMessage("Order", m_nCode, "DecreaseOrderBySeqNo", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "期貨委託減量: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 刪單
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
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 商品代碼、委託序號、委託書號
        column = 0
        self.__radVar = IntVar()

        for _ in 'txtStockNo', 'txtSeqNo', 'txtBookNo':
                # 輸入框
            self.__dOrder[_] = Entry(frame, width = 15, state = 'disabled')
            self.__dOrder[_].grid(column = column, row = 1, padx = 5)

            if _ == 'txtStockNo':
                text = '商品代碼'
            elif _ == 'txtSeqNo':
                text = '委託序號'
            elif _ == 'txtBookNo':
                text = '委託書號'

            rb = Radiobutton(frame, style="Pink.TRadiobutton", text = text, variable = self.__radVar, value = column, command = self.__radCall)
            rb.grid(column = column, row = 0, pady = 3, sticky = 'ew')

            column = column + 1
        self.__dOrder['txtStockNo']['state'] = '!disabled'

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 3, row =  1, padx = 5)

        btnAsyncSendOrder = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnAsyncSendOrder["command"] = self.__btnAsyncSendOrder_Click
        btnAsyncSendOrder.grid(column = 4, row =  1, padx = 5)


    def __radCall(self):
        radSel = self.__radVar.get()
        self.__dOrder['txtStockNo']['state'] = '!disabled' if radSel == 0 else 'disabled'
        self.__dOrder['txtSeqNo']['state'] = '!disabled' if radSel == 1 else 'disabled'
        self.__dOrder['txtBookNo']['state'] = '!disabled' if radSel == 2 else 'disabled'

    # 送出
    def __btnAsyncSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        elif self.__radVar.get() == 0 and self.__dOrder['txtStockNo'].get() == '':
            ans = messagebox.askquestion("提示", '未輸入商品代碼會刪除所有委託單，是否刪單？')
            if ans == 'yes':
                self.__SendOrder_Click(True)
            else:
                return
        elif self.__radVar.get() == 1 and self.__dOrder['txtSeqNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託序號！')
        elif self.__radVar.get() == 2 and self.__dOrder['txtBookNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託書號！')
        else:
            self.__SendOrder_Click(True)

    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇期貨帳號！')
        elif self.__radVar.get() == 0 and self.__dOrder['txtStockNo'].get() == '':
            ans = messagebox.askquestion("提示", '未輸入商品代碼會刪除所有委託單，是否刪單？')
            if ans == 'yes':
                self.__SendOrder_Click(False)
            else:
                return
        elif self.__radVar.get() == 1 and self.__dOrder['txtSeqNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託序號！')
        elif self.__radVar.get() == 2 and self.__dOrder['txtBookNo'].get() == '':
            messagebox.showerror("error！", '請輸入欲取消的委託書號！')
        else:
            self.__SendOrder_Click(False)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.__radVar.get() == 0:
                message, m_nCode = skO.CancelOrderByStockNo( Global.Global_IID, bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtStockNo'].get() )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelOrderByStockNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "期貨委託刪單依商品代碼: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
            elif self.__radVar.get() == 1:
                message, m_nCode = skO.CancelOrderBySeqNo( Global.Global_IID, bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtSeqNo'].get() )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelOrderBySeqNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "期貨委託刪單依委託序號: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
            elif self.__radVar.get() == 2:
                message, m_nCode = skO.CancelOrderByBookNo( Global.Global_IID, bAsyncOrder, self.__dOrder['boxAccount'],\
                    self.__dOrder['txtBookNo'].get() )
                self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelOrderByBookNo", self.__dOrder['listInformation'])
                if bAsyncOrder == False and m_nCode == 0:
                    strMsg = "期貨委託刪單依委託書號: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 未平倉查詢
class OpenInterest(Frame):
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
        group = LabelFrame(self.__master, text="未平倉查詢", style="Pink.TLabelframe")
        group.grid(column = 1, row = 1, padx = 5, pady = 5 ,sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 未平倉量查詢
        # 按鈕
        btnGetOpenInterest = Button(frame, style = "Pink.TButton", text = "查詢")
        btnGetOpenInterest["command"] = self.__btnGetOpenInterest_Click
        btnGetOpenInterest.grid(column = 0, row = 0, padx = 5)

        # 格式選取
        lbGetOpenInterestWithFormat = Label(frame, style="Pink.TLabel", text = "格式")
        lbGetOpenInterestWithFormat.grid(column = 1, row = 0, pady = 5)
            # 輸入框
        self.boxGetOpenInterestWithFormat = Combobox(frame, state='readonly',width = 13)
        self.boxGetOpenInterestWithFormat.grid(column = 2, row = 0, padx = 5)
        self.boxGetOpenInterestWithFormat["values"]=Config.OPENINTERSETFORMAT

        btnGetOpenInterestWithFormat = Button(frame, style = "Pink.TButton", text = "查詢含格式")
        btnGetOpenInterestWithFormat["command"] = self.__btnGetOpenInterestWithFormat_Click
        btnGetOpenInterestWithFormat.grid(column = 3, row = 0, padx = 5)

        self.__dOrder["btnGetOpenInterestWithFormat"] = self.boxGetOpenInterestWithFormat.get()

    def __btnGetOpenInterest_Click(self):
        try:
            m_nCode = skO.GetOpenInterest(Global.Global_IID,self.__dOrder['boxAccount'])
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetOpenInterest", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

    def __btnGetOpenInterestWithFormat_Click(self):
        try:
            if self.boxGetOpenInterestWithFormat.get() == "1.完整":
                nFormat = 1
            elif self.boxGetOpenInterestWithFormat.get() == "2.格式一":
                nFormat = 2
            elif self.boxGetOpenInterestWithFormat.get() == "3.格式二-含損益":
                nFormat = 3
            m_nCode = skO.GetOpenInterestWithFormat(Global.Global_IID,self.__dOrder['boxAccount'],nFormat)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetOpenInterestWithFormat", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 權益數查詢
class GetFutureRight(Frame):
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
        group = LabelFrame(self.__master, text="權益數查詢", style="Pink.TLabelframe")
        group.grid(column = 1, row = 2, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        # 幣別
        lbCoinType = Label(frame, style="Pink.TLabel", text = "幣別")
        lbCoinType.grid(column = 1, row = 0, pady = 5)
            # 輸入框
        self.boxCoinType = Combobox(frame, state='readonly')
        self.boxCoinType.grid(column = 2, row = 0, padx = 5)
        self.boxCoinType["values"]=Config.COINTYPE
        # 查詢按鈕
        btnCoinType = Button(frame, style = "Pink.TButton", text = "查詢")
        btnCoinType["command"] = self.__btnCoinType_Click
        btnCoinType.grid(column = 3, row = 0, padx = 5)

    def __btnCoinType_Click(self):
        try:
            if self.boxCoinType.get() == "ALL":
                nCoinType = 0
            elif self.boxCoinType.get() == "新台幣(TWD)":
                nCoinType = 1
            elif self.boxCoinType.get() == "人民幣(RMB)":
                nCoinType = 2
            m_nCode = skO.GetFutureRights(Global.Global_IID,self.__dOrder['boxAccount'],nCoinType)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetFutureRights", self.__dOrder['listInformation'])
        except Exception as e:
            if self.boxCoinType.get() == "":
                messagebox.showerror("Error！", "請選擇幣別！")
            else:
                messagebox.showerror("Error！", e)
# 依書號/序號 改價(選擇權拆分)
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
        group = LabelFrame(self.__master, text="期貨改價", style="Pink.TLabelframe")
        group.grid(column = 0, row = 3, padx = 5, pady = 5,columnspan = 2 ,sticky = 'ew')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

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
                    strMsg = "期貨委託改價依委託序號: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
            elif self.__CorrectPriceRadVar.get() == 2:
                bstrMarketSymbol = "TF"
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
                    strMsg = "期貨委託改價依委託書號: " + str(message)
                    self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

    def __CorrectPriceRadCall(self):
        CorrectPriceRadVar = self.__CorrectPriceRadVar.get()
        self.__dOrder['txtPriceSeqNo']['state'] = '!disabled' if CorrectPriceRadVar == 0 else 'disabled'
        self.__dOrder['txtPriceBookNo']['state'] = '!disabled' if CorrectPriceRadVar == 2 else 'disabled'
# 大小台互抵
class TXOffset(Frame):
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
        group = LabelFrame(self.__master, text="大小台互抵(未實測)", style="Red.TLabelframe")
        # group.grid(column = 0, row = 4, padx = 5, pady = 5, sticky = 'ew')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        def __clear_entry(event, txtYearMonth):
            self.txtYearMonth.delete(0, END)
            self.txtYearMonth['foreground'] = "#000000"
        # 年月
        lbYearMonth = Label(frame, style="Pink.TLabel", text = "年月：")
        lbYearMonth.grid(column = 0, row = 0,padx = 5)
            # 輸入框
        self.txtYearMonth = Entry(frame, width = 10)
        self.txtYearMonth.grid(column = 1, row = 0,padx = 5)
        self.txtYearMonth['foreground'] = "#b3b3b3"
        self.txtYearMonth.insert(0, "YYYYMM")
        self.txtYearMonth.bind("<FocusIn>", lambda event: __clear_entry(event, self.txtYearMonth))

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 2, row = 0)
            # 輸入框
        self.boxBuySell = Combobox(frame, width = 10, state='readonly')
        self.boxBuySell['values'] = Config.BUYSELLSET
        self.boxBuySell.grid(column = 3, row = 0, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量：")
        lbQty.grid(column = 4, row = 0)
            # 輸入框
        self.txtQty = Entry(frame, width = 10)
        self.txtQty.grid(column = 5, row = 0)

        # 按鈕
        btnSendTXOffset = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendTXOffset["command"] = self.__btnSendTXOffset_Click
        btnSendTXOffset.grid(column = 8, row =  0, padx = 5)

    def __btnSendTXOffset_Click(self):
        try:
            if self.boxBuySell.get() == "買進":
                nBuySell = 0
            elif self.boxBuySell.get() == "賣出":
                nBuySell = 1
            message, m_nCode = skO.SendTXOffset( Global.Global_IID, True, self.__dOrder['boxAccount'],\
                self.txtYearMonth.get(), nBuySell, int(self.txtQty.get()))
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendTXOffset", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)

class FutureOrder(Frame):

    def __init__(self, information=None):
        Frame.__init__(self)
        self.__obj = dict(
            order = Order(master = self, information = information),
            decrease = DecreaseOrder(master = self, information = information),
            cancel = CancelOrder(master = self, information = information),
            openinterest = OpenInterest(master = self, information = information),
            right = GetFutureRight(master = self, information = information),
            correct = CorrectPrice(master = self, information = information),
            txoffset = TXOffset(master = self, information = information),
        )

    def SetAccount(self, account):
        for _ in 'order', 'decrease', 'cancel',"openinterest","right","correct","txoffset":
            self.__obj[_].SetAccount(account)

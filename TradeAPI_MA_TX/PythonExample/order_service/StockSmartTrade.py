# 先把API com元件初始化
import os,time
from ctypes import wintypes

# 第一種讓群益API元件可導入讓Python code使用的方法 win32com
#import win32com.client
#from ctypes import WinDLL,byref
#from ctypes.wintypes import MSG
#SKCenterLib = win32com.client.Dispatch("{AC30BAB5-194A-4515-A8D3-6260749F8577}")
#SKOrderLib = win32com.client.Dispatch("{54FE0E28-89B6-43A7-9F07-BE988BB40299}")
#SKReply = win32com.client.Dispatch("{72D98963-03E9-42AB-B997-BB2E5CCE78DD}")
#SKQuote = win32com.client.Dispatch("{E7BCB8BB-E1F0-4F6F-A944-2679195E5807}")
#SKOSQuote = win32com.client.Dispatch("{E3CB8A7C-896F-4828-85FC-8975E56BA2C4}")
#SKOOQuote = win32com.client.Dispatch("{853EC706-F437-46E2-80E0-896901A5B490}")

# 第二種讓群益API元件可導入Python code內用的物件宣告 comtypes
import comtypes.client
# comtypes.client.GetModule(os.path.split(os.path.realpath(__file__))[0] + r"/SKCOM.dll")
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
from tkinter import messagebox

# 載入其他物件
import Config
import MessageControl
# 當沖組合
class StockStrategyDayTrade(Frame):
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
        group = LabelFrame(self.__master, text="現股當沖組合", style="Pink.TLabelframe")
        group.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 0, row = 0)
            # 輸入框
        self.txtStockNo = Entry(frame, width = 8)
        self.txtStockNo.grid(column = 0, row = 1, padx = 5)

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 1, row = 0)
            # 輸入框
        self.boxBuySell = Combobox(frame, width = 8, state='readonly')
        self.boxBuySell['values'] = Config.STOCKSMARTDAYTRADE
        self.boxBuySell.grid(column = 1, row = 1, padx = 5)

        # 委託價
        lbOrderPrice = Label(frame, style="Pink.TLabel", text = "委託價")
        lbOrderPrice.grid(column = 2, row = 0)
            # 輸入框
        self.txtOrderPrice = Entry(frame, width = 10)
        self.txtOrderPrice.grid(column = 2, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 3, row = 0)
            # 輸入框
        self.txtQty = Entry(frame, width = 10)
        self.txtQty.grid(column = 3, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 4, row =  0, padx = 5)
        # btnAsyncSendOrder
        btnAsyncSendOrder = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnAsyncSendOrder["command"] = self.__btnSendOrderAsync_Click
        btnAsyncSendOrder.grid(column = 4, row =  1, padx = 5)

# --------------------------------------------------------------------------------------------------
        # 當沖組合
        groupDayTrade = LabelFrame(frame, style="Pink.TLabelframe", text = "當沖組合")
        groupDayTrade.grid(column = 0, row = 2, padx = 5, columnspan = 5)
# ------------------------------------------------------------------------------------
        # 停利
        self.__TakeProfitFlag = IntVar()
        Checkbutton(groupDayTrade, style="Pink.TCheckbutton", text='停利', variable = self.__TakeProfitFlag, onvalue = 1, offvalue = 0).grid(column = 0, row = 0,padx = 5)

        groupTPPercnet = LabelFrame(groupDayTrade, style="Pink.TLabelframe")
        groupTPPercnet.grid(column = 1, row = 0, padx = 5)

        column = 0
        self.__TPPercnetradVar = IntVar()

        for _ in 'txtTPPercnet', 'txtTPTrigger':
                # 輸入框
            self.__dOrder[_] = Entry(groupTPPercnet, width = 6, state = 'disabled')
            self.__dOrder[_].grid(column = column+1, row = 0, padx = 3)

            if _ == 'txtTPPercnet':
                text = '漲幅'
            elif _ == 'txtTPTrigger':
                text = '觸發價'

            rb = Radiobutton(groupTPPercnet, style="Pink.TRadiobutton", text = text, variable = self.__TPPercnetradVar, value = column, command = self.__TPPercnetradCall)
            rb.grid(column = column, row = 0, padx = 3, sticky = 'ew')

            column = column + 3
        self.__dOrder['txtTPPercnet']['state'] = '!disabled'

        # %
        lbTPPercnet =  Label(groupTPPercnet, style="Pink.TLabel", text = "%")
        lbTPPercnet.grid(column = 2, row = 0, pady = 3)

        groupTPPrice = LabelFrame(groupDayTrade, style="Pink.TLabelframe")
        groupTPPrice.grid(column = 2, row = 0, padx = 5)

        # 停利第二框
        self.__TPPriceradVar = IntVar()
        # 選擇紐
        rbTPOrderPrice = Radiobutton(groupTPPrice, style="Pink.TRadiobutton", text = "委託價", variable = self.__TPPriceradVar, value = 0, command = self.__TPPriceradCall)
        rbTPOrderPrice.grid(column = 0, row = 0, padx = 3, sticky = 'ew')
        # 輸入框
        self.txtTPOrderPrice = Entry(groupTPPrice, width = 6, state = 'disabled')
        self.txtTPOrderPrice.grid(column = 1, row = 0, padx = 3)
        self.txtTPOrderPrice['state'] = '!disabled'

        rbTPMarketPrice = Radiobutton(groupTPPrice, style="Pink.TRadiobutton", text = "市價", variable = self.__TPPriceradVar, value = 2, command = self.__TPPriceradCall)
        rbTPMarketPrice.grid(column = 2, row = 0, padx = 3, sticky = 'ew')
# -----------------------------------------------------------------------------------------
        # 停損
        self.__StopLossFlag = IntVar()
        Checkbutton(groupDayTrade, style="Pink.TCheckbutton", text='停損', variable = self.__StopLossFlag, onvalue = 1, offvalue = 0).grid(column = 0, row = 1, padx = 5)

        groupSLPercnet = LabelFrame(groupDayTrade, style="Pink.TLabelframe")
        groupSLPercnet.grid(column = 1, row = 1, padx = 5)

        column = 0
        self.__SLPercnetradVar = IntVar()

        for _ in 'txtSLPercnet', 'txtSLTrigger':
                # 輸入框
            self.__dOrder[_] = Entry(groupSLPercnet, width = 6, state = 'disabled')
            self.__dOrder[_].grid(column = column+1, row = 0, padx = 3)

            if _ == 'txtSLPercnet':
                text = '跌幅'
            elif _ == 'txtSLTrigger':
                text = '觸發價'

            rb = Radiobutton(groupSLPercnet, style="Pink.TRadiobutton", text = text, variable = self.__SLPercnetradVar, value = column, command = self.__SLPercnetradCall)
            rb.grid(column = column, row = 0, padx = 3, sticky = 'ew')

            column = column + 3
        self.__dOrder['txtSLPercnet']['state'] = '!disabled'

        # %
        lbPercnet =  Label(groupSLPercnet, style="Pink.TLabel", text = "%")
        lbPercnet.grid(column = 2, row = 0, pady = 3)

        groupSLPrice = LabelFrame(groupDayTrade, style="Pink.TLabelframe")
        groupSLPrice.grid(column = 2, row = 1, padx = 5)

        # 停損第二框
        self.__SLPriceradVar = IntVar()
        # 選擇紐
        rbSLOrderPrice = Radiobutton(groupSLPrice, style="Pink.TRadiobutton", text = "委託價", variable = self.__SLPriceradVar, value = 0, command = self.__SLPriceradCall)
        rbSLOrderPrice.grid(column = 0, row = 0, padx = 3, sticky = 'ew')
        # 輸入框
        self.txtSLOrderPrice = Entry(groupSLPrice, width = 6, state = 'disabled')
        self.txtSLOrderPrice.grid(column = 1, row = 0, padx = 3)
        self.txtSLOrderPrice['state'] = '!disabled'

        rbSLMarketPrice = Radiobutton(groupSLPrice, style="Pink.TRadiobutton", text = "市價", variable = self.__SLPriceradVar, value = 2, command = self.__SLPriceradCall)
        rbSLMarketPrice.grid(column = 2, row = 0, padx = 3, sticky = 'ew')
# ---------------------------------------------------------------------------------------------------------------------------
        # 出清
        self.__ClearAllFlag = IntVar()
        Checkbutton(groupDayTrade, style="Pink.TCheckbutton", text='出清', variable = self.__ClearAllFlag, onvalue = 1, offvalue = 0).grid(column = 0, row = 2,padx = 5)

        groupClearTime = LabelFrame(groupDayTrade, style="Pink.TLabelframe")
        groupClearTime.grid(column = 1, row = 2, padx = 5, sticky = "w")

        lbClearCancelTime = Label(groupClearTime, style="Pink.TLabel", text = "時間")
        lbClearCancelTime.grid(column = 0, row = 0, pady = 3)
        # 小時
        self.boxHour = Combobox(groupClearTime, width = 5, state='readonly')
        self.boxHour['values'] = "09","10","11","12","13"
        self.boxHour.grid(column = 1, row = 0, padx = 5)
        # 分鐘
        self.boxMinute = Combobox(groupClearTime, width = 5, state='readonly')
        minute = []
        for i in range(00,60):
            minute.append(str(i).zfill(2))
        self.boxMinute['values'] = minute
        self.boxMinute.grid(column = 2, row = 0, padx = 5)

        groupClearPrice = LabelFrame(groupDayTrade, style="Pink.TLabelframe")
        groupClearPrice.grid(column = 2, row = 2, padx = 5)

        # 出清第二框
        self.__ClearPriceradVar = IntVar()
        # 選擇紐
        rbClearOrderPrice = Radiobutton(groupClearPrice, style="Pink.TRadiobutton", text = "委託價", variable = self.__ClearPriceradVar, value = 0, command = self.__ClearPriceradCall)
        rbClearOrderPrice.grid(column = 0, row = 0, padx = 3, sticky = 'ew')
        # 輸入框
        self.txtClearOrderPrice = Entry(groupClearPrice, width = 6, state = 'disabled')
        self.txtClearOrderPrice.grid(column = 1, row = 0, padx = 3)
        self.txtClearOrderPrice['state'] = '!disabled'

        rbClearMarketPrice = Radiobutton(groupClearPrice, style="Pink.TRadiobutton", text = "市價", variable = self.__ClearPriceradVar, value = 2, command = self.__ClearPriceradCall)
        rbClearMarketPrice.grid(column = 2, row = 0, padx = 3, sticky = 'ew')

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # 盤後定盤交易
        self.__FinalClearFlag = IntVar()
        Checkbutton(groupDayTrade, style="Pink.TCheckbutton", text='盤後定盤交易', variable = self.__FinalClearFlag, onvalue = 1, offvalue = 0).grid(column = 0, row = 3,padx = 5, columnspan = 2, sticky = "w")

    def __TPPercnetradCall(self):
        radSel = self.__TPPercnetradVar.get()
        self.__dOrder['txtTPPercnet']['state'] = '!disabled' if radSel == 0 else 'disabled'
        self.__dOrder['txtTPTrigger']['state'] = '!disabled' if radSel == 3 else 'disabled'

    def __TPPriceradCall(self):
        radSel = self.__TPPriceradVar.get()
        self.txtTPOrderPrice['state'] = '!disabled' if radSel == 0 else 'disabled'

    def __SLPercnetradCall(self):
        radSel = self.__SLPercnetradVar.get()
        self.__dOrder['txtSLPercnet']['state'] = '!disabled' if radSel == 0 else 'disabled'
        self.__dOrder['txtSLTrigger']['state'] = '!disabled' if radSel == 3 else 'disabled'

    def __SLPriceradCall(self):
        radSel = self.__SLPriceradVar.get()
        self.txtSLOrderPrice['state'] = '!disabled' if radSel == 0 else 'disabled'

    def __ClearPriceradCall(self):
        radSel = self.__ClearPriceradVar.get()
        self.txtClearOrderPrice['state'] = '!disabled' if radSel == 0 else 'disabled'

    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            # 建立下單用的參數(STOCKSTRATEGYORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.STOCKSTRATEGYORDER()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號
            oOrder.bstrStockNo = self.txtStockNo.get()
            # 委託數量
            oOrder.nQty = int(self.txtQty.get())
            # 委託價
            oOrder.bstrOrderPrice = self.txtOrderPrice.get()
            # 停利條件設置
            if self.__TakeProfitFlag.get() == 1:
                oOrder.nTakeProfitFlag = 1
                if self.__TPPercnetradVar.get() == 0:
                    oOrder.nRDOTPPercent = 1
                    oOrder.bstrTPPercnet = self.__dOrder['txtTPPercnet'].get()
                elif self.__TPPercnetradVar.get() == 3:
                    oOrder.nRDOTPPercent = 0
                    oOrder.bstrTPTrigger = self.__dOrder['txtTPTrigger'].get()

                if self.__TPPriceradVar.get() == 0:
                    oOrder.nRDTPMarketPriceType = 2
                    oOrder.bstrTPOrderPrice = self.txtTPOrderPrice.get()
                elif self.__TPPriceradVar.get() == 2:
                    oOrder.nRDTPMarketPriceType = 1
            elif self.__TakeProfitFlag.get() == 0:
                oOrder.nTakeProfitFlag = 0
            # -----------------------------------------------------
            # 停損條件設置
            if self.__StopLossFlag.get() == 1:
                oOrder.nStopLossFlag = 1
                if self.__SLPercnetradVar.get() == 0:
                    oOrder.nRDOSLPercent = 1
                    oOrder.bstrSLPerent = self.__dOrder['txtSLPercnet'].get()
                elif self.__SLPercnetradVar.get() == 3:
                    oOrder.nRDOSLPercent = 0
                    oOrder.bstrSLTrigger = self.__dOrder['txtSLTrigger'].get()

                if self.__SLPriceradVar.get() == 0:
                    oOrder.nRDSLMarketPriceType = 2
                    oOrder.bstrSLOrderPrice = self.txtSLOrderPrice.get()
                elif self.__SLPriceradVar.get() == 2:
                    oOrder.nRDSLMarketPriceType = 1
            elif self.__StopLossFlag.get() == 0:
                oOrder.nStopLossFlag = 0
            # -----------------------------------------------------
            # 出清條件委託
            if self.__ClearAllFlag.get() == 1:
                oOrder.nClearAllFlag = 1
                oOrder.bstrClearCancelTime = self.boxHour.get() + self.boxMinute.get()
                if self.__ClearPriceradVar.get() == 0:
                    oOrder.nClearAllPriceType = 2
                    oOrder.bstrClearAllOrderPrice = self.txtClearOrderPrice.get()
                elif self.__ClearPriceradVar.get() == 2:
                    oOrder.nClearAllPriceType = 1
            elif self.__ClearAllFlag.get() == 0:
                oOrder.nClearAllFlag = 0
            # -----------------------------------------------------
            # 盤後條件設定
            if self.__FinalClearFlag.get() == 1:
                oOrder.sFinalClearFlag = 1
            elif self.__FinalClearFlag.get() == 0:
                oOrder.sFinalClearFlag = 0
            # -----------------------------------------------------
            if self.boxBuySell.get() == "現股買":
                oOrder.nBuySell = 0
            elif self.boxBuySell.get() == "無券賣出":
                oOrder.nBuySell = 1
            # -----------------------------------------------------
            # 建立下單用的參數(OVERSEAFUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            # oOrder = sk.STOCKSTRATEGYORDER()
            # # 填入完整帳號
            # oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # # 買賣別
            # oOrder.nBuySell = nBuySell
            # # 執行時間出清
            # oOrder.nClearAllFlag = nClearAllFlag
            # # 出清時間
            # oOrder.bstrClearCancelTime = bstrClearCancelTime
            # # 出清委託價方式
            # oOrder.nClearAllPriceType = nClearAllPriceType
            # # 出清委託價
            # oOrder.bstrClearAllOrderPrice = bstrClearAllOrderPrice
            # # 盤後定盤交易
            # oOrder.sFinalClearFlag = sFinalClearFlag
            #
            # # 出場停利條件
            # oOrder.nTakeProfitFlag = nTakeProfitFlag
            # # 停利類型
            # oOrder.nRDOTPPercent = nRDOTPPercent
            # # 停利漲幅百分比
            # oOrder.bstrTPPercnet = bstrTPPercnet
            # # 停利觸發價
            # oOrder.bstrTPTrigger = bstrTPTrigger
            # # 停利委託價方式
            # oOrder.nRDTPMarketPriceType = nRDTPMarketPriceType
            # # 停利委託價
            # oOrder.bstrTPOrderPrice = bstrTPOrderPrice
            #
            # # 出場停損條件
            # oOrder.nStopLossFlag = nStopLossFlag
            # # 停損類型
            # oOrder.nRDOSLPercent = nRDOSLPercent
            # # 停損百分比
            # oOrder.bstrSLPerent = bstrSLPerent
            # # 停損觸發價
            # oOrder.bstrSLTrigger = bstrSLTrigger
            # # 停損委託價方式
            # oOrder.nRDSLMarketPriceType = nRDSLMarketPriceType
            # # 停損委託價
            # oOrder.bstrSLOrderPrice = bstrSLOrderPrice

            message, m_nCode = skO.SendStockStrategyDayTrade(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendStockStrategyDayTrade", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "現股當沖組合: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 出清策略
class StockStrategyClear(Frame):
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
        group = LabelFrame(self.__master, text="出清策略", style="Pink.TLabelframe")
        group.grid(column = 1, row = 0, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 商品代碼
        lbStockNo = Label(frame, style="Pink.TLabel", text = "商品代碼")
        lbStockNo.grid(column = 0, row = 0)
            # 輸入框
        self.txtStockNo = Entry(frame, width = 8)
        self.txtStockNo.grid(column = 0, row = 1, padx = 5)

        # 買賣別
        lbBuySell = Label(frame, style="Pink.TLabel", text = "買賣別")
        lbBuySell.grid(column = 1, row = 0)
            # 輸入框
        self.boxBuySell = Combobox(frame, width = 5, state='readonly')
        self.boxBuySell['values'] = Config.BUYSELLSET
        self.boxBuySell.grid(column = 1, row = 1, padx = 5)

        # 委託價
        lbOrderType = Label(frame, style="Pink.TLabel", text = "現資券")
        lbOrderType.grid(column = 2, row = 0)
            # 輸入框
        self.boxOrderType = Combobox(frame, width = 5, state='readonly')
        self.boxOrderType['values'] = Config.STOCKSTRATEGYORDERTYPE
        self.boxOrderType.grid(column = 2, row = 1, padx = 5)

        # 委託量
        lbQty = Label(frame, style="Pink.TLabel", text = "委託量")
        lbQty.grid(column = 3, row = 0)
            # 輸入框
        self.txtQty = Entry(frame, width = 10)
        self.txtQty.grid(column = 3, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步委託")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 4, row =  0, padx = 5)
        # btnAsyncSendOrder
        btnAsyncSendOrder = Button(frame, style = "Pink.TButton", text = "非同步委託")
        btnAsyncSendOrder["command"] = self.__btnSendOrderAsync_Click
        btnAsyncSendOrder.grid(column = 4, row =  1, padx = 5)

# --------------------------------------------------------------------------------------------------
        # 組合條件
        groupCombination = LabelFrame(frame, style="Pink.TLabelframe", text = "組合條件")
        groupCombination.grid(column = 0, row = 2, padx = 5, columnspan = 5)
# ------------------------------------------------------------------------------------
        # 條件一
        gropuConditionOne = LabelFrame(groupCombination, style="Pink.TLabelframe", text = "條件一")
        gropuConditionOne.grid(column = 0, row = 0, padx = 5)

        # 成交價大於
        self.__GTEFlag = IntVar()
        Checkbutton(gropuConditionOne, style="Pink.TCheckbutton", text='成交價大於', variable = self.__GTEFlag, onvalue = 1, offvalue = 0).grid(column = 0, row = 0,padx = 5)

        self.txtGTETriggerPrice = Entry(gropuConditionOne, width = 8)
        self.txtGTETriggerPrice.grid(column = 1, row = 0, padx = 5)

        # 條件一 第二框
        gropuGTEOrderPrice = LabelFrame(groupCombination, style="Pink.TLabelframe")
        gropuGTEOrderPrice.grid(column = 1, row = 0, padx = 5)

        self.__GTEPriceradVar = IntVar()
        # 選擇紐
        rbGTEOrderPrice = Radiobutton(gropuGTEOrderPrice, style="Pink.TRadiobutton", text = "委託價", variable = self.__GTEPriceradVar, value = 0, command = self.__GTEPriceradCall)
        rbGTEOrderPrice.grid(column = 0, row = 0, padx = 3, sticky = 'ew')
        # 輸入框
        self.txtGTEOrderPrice = Entry(gropuGTEOrderPrice, width = 6, state = 'disabled')
        self.txtGTEOrderPrice.grid(column = 1, row = 0, padx = 3)
        self.txtGTEOrderPrice['state'] = '!disabled'

        rbGTEMarketPrice = Radiobutton(gropuGTEOrderPrice, style="Pink.TRadiobutton", text = "市價", variable = self.__GTEPriceradVar, value = 2, command = self.__GTEPriceradCall)
        rbGTEMarketPrice.grid(column = 2, row = 0, padx = 3, sticky = 'ew')
# -----------------------------------------------------------------------------------------
        # 條件二
        gropuConditionTwo = LabelFrame(groupCombination, style="Pink.TLabelframe", text = "條件二")
        gropuConditionTwo.grid(column = 0, row = 1, padx = 5)

        # 成交價小於
        self.__LTEFlag = IntVar()
        Checkbutton(gropuConditionTwo, style="Pink.TCheckbutton", text='成交價小於', variable = self.__LTEFlag, onvalue = 1, offvalue = 0).grid(column = 0, row = 0,padx = 5)

        self.txtLTETriggerPrice = Entry(gropuConditionTwo, width = 8)
        self.txtLTETriggerPrice.grid(column = 1, row = 0, padx = 5)

        # 條件二 第二框
        gropuLTEOrderPrice = LabelFrame(groupCombination, style="Pink.TLabelframe")
        gropuLTEOrderPrice.grid(column = 1, row = 1, padx = 5)

        self.__LTEPriceradVar = IntVar()
        # 選擇紐
        rbLTEOrderPrice = Radiobutton(gropuLTEOrderPrice, style="Pink.TRadiobutton", text = "委託價", variable = self.__LTEPriceradVar, value = 0, command = self.__LTEPriceradCall)
        rbLTEOrderPrice.grid(column = 0, row = 0, padx = 3, sticky = 'ew')
        # 輸入框
        self.txtLTEOrderPrice = Entry(gropuLTEOrderPrice, width = 6, state = 'disabled')
        self.txtLTEOrderPrice.grid(column = 1, row = 0, padx = 3)
        self.txtLTEOrderPrice['state'] = '!disabled'

        rbLTEMarketPrice = Radiobutton(gropuLTEOrderPrice, style="Pink.TRadiobutton", text = "市價", variable = self.__LTEPriceradVar, value = 2, command = self.__LTEPriceradCall)
        rbLTEMarketPrice.grid(column = 2, row = 0, padx = 3, sticky = 'ew')
# ---------------------------------------------------------------------------------------------------------------------------
        # 條件三
        groupConditionThree = LabelFrame(groupCombination, style="Pink.TLabelframe", text = "條件三")
        groupConditionThree.grid(column = 0, row = 2, padx = 5, sticky = "w")

        self.__ClearAllFlag = IntVar()
        Checkbutton(groupConditionThree, style="Pink.TCheckbutton", text='時間', variable = self.__ClearAllFlag, onvalue = 1, offvalue = 0).grid(column = 0, row = 0,padx = 5)

        # 小時
        self.boxHour = Combobox(groupConditionThree, width = 3, state='readonly')
        self.boxHour['values'] = "09","10","11","12","13"
        self.boxHour.grid(column = 1, row = 0, padx = 5)
        # 分鐘
        self.boxMinute = Combobox(groupConditionThree, width = 3, state='readonly')
        minute = []
        for i in range(00,60):
            minute.append(str(i).zfill(2))
        self.boxMinute['values'] = minute
        self.boxMinute.grid(column = 2, row = 0)

        groupClearPrice = LabelFrame(groupCombination, style="Pink.TLabelframe")
        groupClearPrice.grid(column = 1, row = 2, padx = 5)

        # 出清第二框
        self.__ClearPriceradVar = IntVar()
        # 選擇紐
        rbClearOrderPrice = Radiobutton(groupClearPrice, style="Pink.TRadiobutton", text = "委託價", variable = self.__ClearPriceradVar, value = 0, command = self.__ClearPriceradCall)
        rbClearOrderPrice.grid(column = 0, row = 0, padx = 3, sticky = 'ew')
        # 輸入框
        self.txtClearOrderPrice = Entry(groupClearPrice, width = 6, state = 'disabled')
        self.txtClearOrderPrice.grid(column = 1, row = 0, padx = 3)
        self.txtClearOrderPrice['state'] = '!disabled'

        rbClearMarketPrice = Radiobutton(groupClearPrice, style="Pink.TRadiobutton", text = "市價", variable = self.__ClearPriceradVar, value = 2, command = self.__ClearPriceradCall)
        rbClearMarketPrice.grid(column = 2, row = 0, padx = 3, sticky = 'ew')

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # 條件四
        groupConditionFour = LabelFrame(groupCombination, style="Pink.TLabelframe", text = "條件四")
        groupConditionFour.grid(column = 0, row = 3, padx = 5, sticky = "w")
        # 盤後定盤交易
        self.__FinalClearFlag = IntVar()
        Checkbutton(groupConditionFour, style="Pink.TCheckbutton", text='盤後定盤交易', variable = self.__FinalClearFlag, onvalue = 1, offvalue = 0).grid(column = 0, row = 3,padx = 5, columnspan = 2, sticky = "w")

    def __GTEPriceradCall(self):
        radSel = self.__GTEPriceradVar.get()
        self.txtGTEOrderPrice['state'] = '!disabled' if radSel == 0 else 'disabled'

    def __LTEPriceradCall(self):
        radSel = self.__LTEPriceradVar.get()
        self.txtLTEOrderPrice['state'] = '!disabled' if radSel == 0 else 'disabled'

    def __ClearPriceradCall(self):
        radSel = self.__ClearPriceradVar.get()
        self.txtClearOrderPrice['state'] = '!disabled' if radSel == 0 else 'disabled'

    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            # 建立下單用的參數(STOCKSTRATEGYORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
            oOrder = sk.STOCKSTRATEGYORDEROUT()
            # 填入完整帳號
            oOrder.bstrFullAccount =  self.__dOrder['boxAccount']
            # 填入期權代號
            oOrder.bstrStockNo = self.txtStockNo.get()
            # 委託數量
            oOrder.nQty = int(self.txtQty.get())

            # 條件一參數設置
            if self.__GTEFlag.get() == 1:
                oOrder.nGTEFlag = 1
                oOrder.bstrGTETriggerPrice = self.txtGTETriggerPrice.get()
                if self.__GTEPriceradVar.get() == 0:
                    oOrder.nGTEMarketPrice = 0
                    oOrder.bstrGTEOrderPrice = self.txtGTEOrderPrice.get()
                elif self.__GTEPriceradVar.get() == 2:
                    oOrder.nGTEMarketPrice = 1
            elif self.__GTEFlag.get() == 0:
                oOrder.nGTEFlag = 0
            # -----------------------------------------------------
            # 條件二參數設置
            if self.__LTEFlag.get() == 1:
                oOrder.nLTEFlag = 1
                oOrder.bstrLTETriggerPrice = self.txtLTETriggerPrice.get()
                if self.__LTEPriceradVar.get() == 0:
                    oOrder.nLTEMarketPrice = 0
                    oOrder.bstrLTEOrderPrice = self.txtLTEOrderPrice.get()
                elif self.__LTEPriceradVar.get() == 2:
                    oOrder.nLTEMarketPrice = 1
            elif self.__LTEFlag.get() == 0:
                oOrder.nLTEFlag = 0
            # -----------------------------------------------------
            # 條件三參數設置
            if self.__ClearAllFlag.get() == 1:
                oOrder.nClearAllFlag = 1
                oOrder.bstrClearCancelTime = self.boxHour.get() + self.boxMinute.get()
                if self.__ClearPriceradVar.get() == 0:
                    oOrder.nClearAllPriceType = 2
                    oOrder.bstrClearAllOrderPrice = self.txtClearOrderPrice.get()
                elif self.__ClearPriceradVar.get() == 2:
                    oOrder.nClearAllPriceType = 1
            elif self.__ClearAllFlag.get() == 0:
                oOrder.nClearAllFlag = 0
            # -----------------------------------------------------
            # 盤後條件設定
            if self.__FinalClearFlag.get() == 1:
                oOrder.sFinalClearFlag = 1
            elif self.__FinalClearFlag.get() == 0:
                oOrder.sFinalClearFlag = 0
            # -----------------------------------------------------
            if self.boxBuySell.get() == "買進":
                oOrder.nBuySell = 0
            elif self.boxBuySell.get() == "賣出":
                oOrder.nBuySell = 1
            # -----------------------------------------------------
            if self.boxOrderType == "現股":
                oOrder.nOrderType = 0
            elif self.boxOrderType == "融資":
                oOrder.nOrderType = 1
            elif self.boxOrderType == "融券":
                oOrder.nOrderType = 2
            # -----------------------------------------------------

            # # 買賣別
            # oOrder.nBuySell = nBuySell
            # # 進場委託別
            # oOrder.nOrderType = nOrderType
            #
            # # 執行時間出清
            # oOrder.nClearAllFlag = nClearAllFlag
            # # 出清時間
            # oOrder.bstrClearCancelTime = bstrClearCancelTime
            # # 出清委託價方式
            # oOrder.nClearAllPriceType = nClearAllPriceType
            # # 出清委託價
            # oOrder.bstrClearAllOrderPrice = bstrClearAllOrderPrice
            #
            # # 盤後定盤交易
            # oOrder.sFinalClearFlag = sFinalClearFlag
            #
            # # 出場條件(大於)
            # oOrder.nGTEFlag = nGTEFlag
            # # (大於)觸發價
            # oOrder.bstrGTETriggerPrice = bstrGTETriggerPrice
            # # (大於)委託價
            # oOrder.bstrGTEOrderPrice = bstrGTEOrderPrice
            # # (大於)市價與否
            # oOrder.nGTEMarketPrice = nGTEMarketPrice
            #
            # # 出場條件(小於)
            # oOrder.nLTEFlag = nLTEFlag
            # # (小於)觸發價
            # oOrder.bstrLTETriggerPrice = bstrLTETriggerPrice
            # # (小於)委託價
            # oOrder.bstrLTEOrderPrice = bstrLTEOrderPrice
            # # (小於)市價與否
            # oOrder.nLTEMarketPrice = nLTEMarketPrice
            #
            # # 停損委託價方式
            # oOrder.nRDSLMarketPriceType = nRDSLMarketPriceType
            # # 停損委託價
            # oOrder.bstrSLOrderPrice = bstrSLOrderPrice

            message, m_nCode = skO.SendStockStrategyClear(Global.Global_IID, bAsyncOrder, oOrder)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "SendStockStrategyClear", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "出清策略: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 證券智慧單查詢
class TSSmartStrategyReport(Frame):
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
        group = LabelFrame(self.__master, text="證券智慧單查詢", style="Pink.TLabelframe")
        group.grid(column = 0, row = 1, padx = 5, pady = 5, sticky = 'w')

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 買賣別
        lbKind = Label(frame, style="Pink.TLabel", text = "種類")
        lbKind.grid(column = 0, row = 0)
            # 輸入框
        self.boxKind = Combobox(frame, width = 8, state='readonly')
        self.boxKind['values'] = Config.STOCKSMARTSTRATEGYKIND
        self.boxKind.grid(column = 1, row = 0, padx = 5)

        def __clear_entry(event, txtDate):
            self.txtDate.delete(0, END)
            self.txtDate['foreground'] = "#000000"
        # 查詢日期
        lbDate = Label(frame, style="Pink.TLabel", text = "查詢日期")
        lbDate.grid(column = 2, row = 0, pady = 3)
            # 輸入框
        self.txtDate = Entry(frame, width = 12)
        self.txtDate.grid(column = 3, row = 0, padx = 5, pady = 3)
        self.txtDate['foreground'] = "#b3b3b3"
        self.txtDate.insert(0, "YYYYMMDD")
        self.txtDate.bind("<FocusIn>", lambda event: __clear_entry(event, self.txtDate))

        btnSend = Button(frame, style = "Pink.TButton", text = "查詢")
        btnSend["command"] = self.__btnSend_Click
        btnSend.grid(column = 4, row =  0, padx = 5)

    def __btnSend_Click(self):
        try:
            if self.boxKind.get() == "當沖":
                bstrKind = "DayTrade"
            elif self.boxKind.get() == "出清":
                bstrKind = "ClearOut"
            bstrMarketType = "TS"
            nReportStatus = 0
            m_nCode = skO.GetTSSmartStrategyReport(Global.Global_IID, self.__dOrder["boxAccount"],\
                bstrMarketType, nReportStatus, bstrKind, self.txtDate.get())
            self.__oMsg.SendReturnMessage("Order", m_nCode, "GetTSSmartStrategyReport", self.__dOrder['listInformation'])
        except Exception as e:
            messagebox.showerror("error！", e)
# 證券智慧單刪單
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
        group = LabelFrame(self.__master, text="證券智慧單刪單", style="Pink.TLabelframe")
        group.grid(column = 1, row = 1, padx = 5, pady = 5, sticky = 'w', columnspan = 2)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5)

        # 智慧單序號
        lbSmartKey = Label(frame, style="Pink.TLabel", text = "智慧單序號")
        lbSmartKey.grid(column = 0, row = 0, pady = 3)
        # 輸入
        self.txtSmartKey = Entry(frame, width = 10)
        self.txtSmartKey.grid(column = 0, row = 1, padx = 5, pady = 3)

        # 智慧單種類
        lbTradeKind = Label(frame, style="Pink.TLabel", text = "智慧單種類")
        lbTradeKind.grid(column = 1, row = 0, pady = 3)
        # 輸入
        self.boxTradeKind = Combobox(frame, width = 10, state='readonly')
        self.boxTradeKind['values'] = Config.STCOKSTRATEGYTRADEKIND
        self.boxTradeKind.grid(column = 1, row = 1, padx = 5)

        # btnSendOrder
        btnSendOrder = Button(frame, style = "Pink.TButton", text = "同步")
        btnSendOrder["command"] = self.__btnSendOrder_Click
        btnSendOrder.grid(column = 2, row =  0, padx = 5)
        # btnSendOrderAsync
        btnSendOrderAsync = Button(frame, style = "Pink.TButton", text = "非同步")
        btnSendOrderAsync["command"] = self.__btnSendOrderAsync_Click
        btnSendOrderAsync.grid(column = 2, row =  1, padx = 5)

    def __btnSendOrder_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
            self.__SendOrder_Click(False)

    def __btnSendOrderAsync_Click(self):
        if self.__dOrder['boxAccount'] == '':
            messagebox.showerror("error！", '請選擇證券帳號！')
        else:
            self.__SendOrder_Click(True)

    def __SendOrder_Click(self, bAsyncOrder):
        try:
            if self.boxTradeKind.get() == "當沖母單":
                nTradeKind = 1
            elif self.boxTradeKind.get() == "當沖未成交入場單":
                nTradeKind = 2
            elif self.boxTradeKind.get() == "當沖已進場單":
                nTradeKind = 3
            elif self.boxTradeKind.get() == "出清":
                nTradeKind = 4

            message, m_nCode = skO.CancelTSStrategyOrder(Global.Global_IID, bAsyncOrder,\
                self.__dOrder['boxAccount'], self.txtSmartKey.get(), nTradeKind)
            self.__oMsg.SendReturnMessage("Order", m_nCode, "CancelTSStrategyOrder", self.__dOrder['listInformation'])
            if bAsyncOrder == False and m_nCode == 0:
                strMsg = "證券智慧單刪單: " + str(message)
                self.__oMsg.WriteMessage( strMsg, self.__dOrder['listInformation'])

        except Exception as e:
            messagebox.showerror("error！", e)



class StockSmartTrade(Frame):
    def __init__(self, information=None):
        Frame.__init__(self)
        self.__obj = dict(
            daytrade = StockStrategyDayTrade(master = self, information = information),
            clear = StockStrategyClear(master = self, information = information),
            report = TSSmartStrategyReport(master = self, information = information),
            cancel = CancelOrder(master = self, information = information),
        )

    def SetAccount(self, account):
        for _ in 'daytrade',"clear","report","cancel":
            self.__obj[_].SetAccount(account)

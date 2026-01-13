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
comtypes.client.GetModule(os.path.split(os.path.realpath(__file__))[0] + r"/SKCOM.dll")
import Global

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

# 數學計算用物件
import math

# 載入其他物件
import StockOrder
import FutureOrder
import OptionOrder
import SeaFutureOrder
import SeaOptionOrder
import StopLossOrderGui
import SendMITOrder
import ForeignStockOrder
import MessageControl
import Config
#import WithDraw
import StockSmartTrade
#----------------------------------------------------------------------------------------------------------------------------------------------------

# 上半部登入框
class __FrameLogin(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.__oMsg = MessageControl.MessageControl()
        self.group = LabelFrame(master, text="Center", style="Pink.TLabelframe")
        self.group.grid(column = 0, row = 0, padx = 5, pady = 5,sticky = 'W')

        self.__CreateWidget()

    def __CreateWidget(self):
        frame = Frame(self.group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = 'W')
        frame.grid_columnconfigure(6, minsize = 530)
        frame.grid_rowconfigure(1, minsize = 40)
        # 帳號
        Label(frame, style="Pink.TLabel", text = "帳號：").grid(column = 0, row = 0)
            # 輸入框
        self.textID = Entry(frame, width = 20)
        self.textID.grid(column = 1, row = 0)

        # 密碼4
        Label(frame, style="Pink.TLabel", text = "密碼：").grid(column = 0, row = 1)
            # 輸入框
        self.textPassword = Entry(frame, width = 20)
        self.textPassword['show'] = '*'
        self.textPassword.grid(column = 1, row = 1)

        # 伺服器
        

        # SGX 專線屬性
        #self.__SGXAuthority = IntVar()
        #Checkbutton(frame, style="Pink.TCheckbutton", text="disable SGX", variable = self.__SGXAuthority, onvalue = 1, offvalue = 0).grid(column = 5, row = 0, padx=10,sticky = "w")

        # 按鈕
        Button(frame, style = "Pink.TButton", text = "登入", command = self.__buttonlogin_Click).grid(column = 3, row = 1,padx=10)

        # ID
        lbID = Label(frame, style="Pink.TLabel", text = "<<ID>>")
        lbID.grid(column = 4, row = 1)

        # 訊息欄
        self.listInformation = Listbox(frame, height = 5,width = 80)
        self.listInformation.grid(column = 0,  row = 2,columnspan = 8, sticky = 'ew')

        sb = Scrollbar(frame, orient = 'horizontal')
        # self.listInformation.config(xscrollcommand = sb.set)
        sb.config(command = self.listInformation.xview)
        sb.grid(row = 3, column = 0, columnspan = 8,sticky = 'ew')


        # global variable
        global GlobalListInformation, Global_ID
        GlobalListInformation = self.listInformation
        Global_ID = lbID

    def __buttonlogin_Click(self):
        try:
            self.__obj = dict(
                # 證券
                stock = StockOrder.StockOrder(information = self.listInformation),
                # 期貨
                future = FutureOrder.FutureOrder(information = self.listInformation),
                # 選擇權
                option = OptionOrder.OptionOrder(information = self.listInformation),
                # 海期
                sea_future = SeaFutureOrder.SeaFutureOrder(information = self.listInformation),
                # 海選
                sea_option = SeaOptionOrder.SeaOptionOrder(information = self.listInformation),
                # 智慧單-停損
                stop_loss = StopLossOrderGui.StopLossOrderGui(information = self.listInformation),
                # 智慧單-MIT
                mit = SendMITOrder.SendMITOrder(information = self.listInformation),
                # 智慧單-證券
                stock_smart = StockSmartTrade.StockSmartTrade(information = self.listInformation),
                # 複委託
                foreign_stock = ForeignStockOrder.ForeignStockOrder(information = self.listInformation),
                # 出入金
                #withdraw = WithDraw.WithDraw(information = self.listInformation),
            )
            # 設置路徑
            m_nCode = skC.SKCenterLib_SetLogPath(os.path.split(os.path.realpath(__file__))[0] + "\\CapitalLog_Order")
            # Debug
            m_nCode = skC.SKCenterLib_Debug(os.path.split(os.path.realpath(__file__))[0] + "\\CapitalLog_Order")      
                         
            m_nCode = skC.SKCenterLib_login(self.textID.get(),self.textPassword.get())
            if(m_nCode == 0):
                 Global_ID["text"] = self.textID.get().replace(' ','')
                 Global.SetID(Global_ID["text"])
                 self.__oMsg.WriteMessage("【 登入成功 】", self.listInformation)
            else:
                 self.__oMsg.SendReturnMessage("Login", m_nCode, "Login", self.listInformation)

        except Exception as e:
            messagebox.showerror("error！",e)

# 下半部-下單
class __FrameOrder(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.__obj = dict(
            msg = MessageControl.MessageControl(),
        )

        self.__CreateWidget()

    def __CreateWidget(self):
        frame = Frame(self, style="Pink.TFrame")
        frame.grid(column = 0, row = 0)

        self.__AddTab(frame)
        self.__FOrder(frame)
        self.__FAccount(frame)
        self.__QuoteLimit(frame)

    def __FOrder(self, master):
        frame = Frame(master, style="Pink.TFrame")
        frame.grid(column = 0, row = 0,columnspan = 2, sticky = 'ew')

        # 初始化
        lbInitialize = Label(frame, style="Pink.TLabel", text = "1.下單物件初始")
        lbInitialize.grid(column = 0, row = 1)
            # 按鈕
        btnInitialize = Button(frame, style = "Pink.TButton", text = "下單初始設定")
        btnInitialize["command"] = self.__btnInitialize_Click
        btnInitialize.grid(column = 1, row = 1, padx = 5)

       # 讀取憑證
        lbReadCert = Label(frame, style="Pink.TLabel", text = "2.讀取憑證")
        lbReadCert.grid(column = 3, row = 1)
            # 按鈕
        btnReadCert = Button(frame, style = "Pink.TButton", text = "讀取憑證")
        btnReadCert["command"] = self.__btnReadCert_Click
        btnReadCert.grid(column = 4, row = 1, padx = 5)

        # 讀取憑證
        lbGetAccount = Label(frame, style="Pink.TLabel", text = "3.取得下單帳號")
        lbGetAccount.grid(column = 6, row = 1)
            # 按鈕
        btnGetAccount = Button(frame, style = "Pink.TButton", text = "載入帳號")
        btnGetAccount["command"] = self.__btnGetAccount_Click
        btnGetAccount.grid(column = 7, row =  1, padx = 5)

         # 按鈕
        btnUpLoadLOG = Button(frame, style = "Pink.TButton", text = "UploadLOG")
        btnUpLoadLOG["command"] = self.__btnUpLoadLOG_Click
        btnUpLoadLOG.grid(column = 8, row =  1, padx = 10)

        # 按鈕
        group = LabelFrame(frame, text="4.海期選下單設定", style="Pink.TLabelframe")
        group.grid(column = 9, row = 1, padx = 30)

        frame = Frame(group, style="Pink.TFrame")
        frame.grid(column = 0, row = 0, sticky = 'ew', padx = 10, pady = 10)

        Button(frame, style = "Pink.TButton", text = "下載海期商品檔", command = self.__btnLoadOSCommodity_Click).grid(column = 0, row =  0, padx = 5)

        Button(frame, style = "Pink.TButton", text = "下載海選商品檔", command = self.__btnLoadOOCommodity_Click).grid(column = 1, row =  0, padx = 5)

       

    # 選帳號
    def __FAccount(self, master):
        frame = Frame(master, style="Pink.TFrame")
        frame.grid(column = 0, row = 1, sticky = 'ew')

        def __StockCallBack(even):
            self.__obj['stock'].SetAccount(self.boxStockAccount.get())
            self.__obj['stock_smart'].SetAccount(self.boxStockAccount.get())

        # 證券
        lbStockAccount = Label(frame, style="Pink.TLabel", text = "證券帳號")
        lbStockAccount.grid(column = 0, row = 2, pady = 5)
            # 輸入框
        self.boxStockAccount = Combobox(frame, state='readonly',width = 25)
        self.boxStockAccount.grid(column = 0, row = 3, padx = 10)
        self.boxStockAccount.bind("<<ComboboxSelected>>", __StockCallBack)

        def __FutureCallBack(even):
            self.__obj['future'].SetAccount(self.boxFutureAccount.get())
            self.__obj['option'].SetAccount(self.boxFutureAccount.get())
            self.__obj['stop_loss'].SetAccount(self.boxFutureAccount.get())
            #self.__obj['withdraw'].SetAccount(self.boxFutureAccount.get())
            self.__obj['mit'].SetAccount(self.boxFutureAccount.get())

        # 期貨
        lbFutureAccount = Label(frame, style="Pink.TLabel", text = "期貨帳號")
        lbFutureAccount.grid(column = 1, row = 2, pady = 5)
            # 輸入框
        self.boxFutureAccount = Combobox(frame, state='readonly',width = 25)
        self.boxFutureAccount.grid(column = 1, row = 3, padx = 10)
        self.boxFutureAccount.bind("<<ComboboxSelected>>", __FutureCallBack )

        def __SeaFutureCallBack(even):
            self.__obj['sea_future'].SetAccount(self.boxSeaFutureAccount.get())
            self.__obj['sea_option'].SetAccount(self.boxSeaFutureAccount.get())
            self.__obj['withdraw'].SetAccount(self.boxSeaFutureAccount.get())
        # 海期
        lbSeaFutureAccount = Label(frame, style="Pink.TLabel", text = "海期帳號")
        lbSeaFutureAccount.grid(column = 2, row = 2, pady = 5)
            # 輸入框
        self.boxSeaFutureAccount = Combobox(frame, state='readonly',width = 25)
        self.boxSeaFutureAccount.grid(column = 2, row = 3, padx = 10)
        self.boxSeaFutureAccount.bind("<<ComboboxSelected>>", __SeaFutureCallBack )

        # 複委託
        lbForeignStockAccount = Label(frame, style="Pink.TLabel", text = "複委託帳號")
        lbForeignStockAccount.grid(column = 3, row = 2, pady = 5)
            # 輸入框
        self.boxForeignStockAccount = Combobox(frame, state='readonly',width = 25)
        self.boxForeignStockAccount.grid(column = 3, row = 3, padx = 10)
        self.boxForeignStockAccount.bind("<<ComboboxSelected>>", lambda _ : self.__obj['foreign_stock'].SetAccount(self.boxForeignStockAccount.get()))

        # global variable
        global GlobalboxStockAccount, GlobalboxFutureAccount, GlobalboxSeaFutureAccount, GlobalboxForeignStockAccount
        GlobalboxStockAccount = self.boxStockAccount
        GlobalboxFutureAccount = self.boxFutureAccount
        GlobalboxSeaFutureAccount = self.boxSeaFutureAccount
        GlobalboxForeignStockAccount = self.boxForeignStockAccount

    # 下單限制
    def __QuoteLimit(self,master):
        frame = LabelFrame(master, text="每秒下單限制", style="Pink.TLabelframe")
        frame.grid(column = 0, row = 2,columnspan = 2, sticky = 'W')
        # 市場別
        lbMarketChoice = Label(frame, style="Pink.TLabel", text = "市場: ")
        lbMarketChoice.grid(column = 0, row = 0, pady = 5)
            # 輸入框
        self.boxMarketChoice = Combobox(frame, state='readonly')
        self.boxMarketChoice.grid(column = 1, row = 0, padx = 10)
        self.boxMarketChoice["values"]=Config.MARKETTYPE

        # 每秒委託「量」限制
        lbMaxQuantity = Label(frame, style="Pink.TLabel", text = "口數: ")
        lbMaxQuantity.grid(column = 2, row = 0)
        self.lbMaxQuantity = Entry(frame, width = 10)
        self.lbMaxQuantity.grid(column = 3, row = 0, padx = 5)
            # 按鈕
        btnMaxQuantity = Button(frame, style = "Pink.TButton", text = "設置委託量")
        btnMaxQuantity["command"] = self.__btnMaxQuantity_Click
        btnMaxQuantity.grid(column = 4, row =  0, padx = 10)

        #每秒委託筆數限制
        lbMaxCount = Label(frame, style="Pink.TLabel", text = "筆數: ")
        lbMaxCount.grid(column = 5, row = 0)
        self.lbMaxCount = Entry(frame, width = 10)
        self.lbMaxCount.grid(column = 6, row = 0, padx = 5)
            # 按鈕
        btnMaxCount = Button(frame, style = "Pink.TButton", text = "設置筆數")
        btnMaxCount["command"] = self.__btnMaxCount_Click
        btnMaxCount.grid(column = 7, row =  0, padx = 10)

        #下單解鎖
        lbGetAccount = Label(frame, style="Pink.TLabel", text = "下單解鎖")
        lbGetAccount.grid(column = 8, row = 0)
            # 按鈕
        btnUnlockOrder = Button(frame, style = "Pink.TButton", text = "解鎖帳號")
        btnUnlockOrder["command"] = self.__btnUnlockOrder_Click
        btnUnlockOrder.grid(column = 9, row =  0, padx = 10)
        


    def __AddTab(self, master):
        tab = Notebook(master, style="Pink.TNotebook")
        tab.grid(column = 0, row = 3,columnspan = 2, sticky = 'ew')

        # 證券
        self.__obj['stock'] = StockOrder.StockOrder(information = GlobalListInformation)
        tab.add(self.__obj['stock'], text="證券   ")

        # 期貨
        self.__obj['future'] = FutureOrder.FutureOrder(information = GlobalListInformation)
        tab.add(self.__obj['future'], text="期貨  ")

        # 選擇權
        self.__obj['option'] = OptionOrder.OptionOrder(information = GlobalListInformation)
        tab.add(self.__obj['option'], text="選擇權 ")

        # 海期
        self.__obj['sea_future'] = SeaFutureOrder.SeaFutureOrder(information = GlobalListInformation)
        tab.add(self.__obj['sea_future'], text="海期  ")

        # 海選
        self.__obj['sea_option'] = SeaOptionOrder.SeaOptionOrder(information = GlobalListInformation)
        tab.add(self.__obj['sea_option'], text="海選  ")

        # 停損
        self.__obj['stop_loss'] = StopLossOrderGui.StopLossOrderGui(information = GlobalListInformation)
        tab.add(self.__obj['stop_loss'], text="智慧單-停損  ")

        #MIT
        self.__obj['mit'] = SendMITOrder.SendMITOrder(information = GlobalListInformation)
        tab.add(self.__obj['mit'], text="智慧單-MIT  ")

        # 證券智慧單
        self.__obj['stock_smart'] = StockSmartTrade.StockSmartTrade(information = GlobalListInformation)
        tab.add(self.__obj['stock_smart'], text="智慧單-證券  ")

        # 出入金
        #self.__obj['withdraw'] = WithDraw.WithDraw(information = GlobalListInformation)
        # tab.add(self.__obj['withdraw'], text="出入金(未實測) ")

        # 複委託
        self.__obj['foreign_stock'] = ForeignStockOrder.ForeignStockOrder(information = GlobalListInformation)
        tab.add(self.__obj['foreign_stock'], text="複委託  ")

    # 下單function
    # 1.下單物件初始
    def __btnInitialize_Click(self):
        try:
            m_nCode = skO.SKOrderLib_Initialize()
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "SKOrderLib_Initialize", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)

    # 2.讀取憑證
    def __btnReadCert_Click(self):
        try:
            m_nCode = skO.ReadCertByID(Global_ID["text"])
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "ReadCertByID", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)

    # 3.取得下單帳號
    def __btnGetAccount_Click(self):
        try:
            m_nCode = skO.GetUserAccount()
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "GetUserAccount", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)
    
    def __btnUpLoadLOG_Click(self):
        try:
            m_nCode = skO.SKOrderLib_LogUpload()
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "LOGUpLoad", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)

    # 4.下載海期商品檔
    def __btnLoadOSCommodity_Click(self):
        try:
            m_nCode = skO.SKOrderLib_LoadOSCommodity()
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "SKOrderLib_LoadOSCommodity", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)

    # 4.下載海選商品檔
    def __btnLoadOOCommodity_Click(self):
        try:
            m_nCode = skO.SKOrderLib_LoadOOCommodity()
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "SKOrderLib_LoadOOCommodity", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)

    #5.限制委託量
    def __btnMaxQuantity_Click(self):
        try:
            if self.boxMarketChoice.get() == "TS (證券)":
                nMarketType = 0
            elif self.boxMarketChoice.get() == "TF(期貨)":
                nMarketType = 1
            elif self.boxMarketChoice.get() == "TO(選擇權)":
                nMarketType = 2
            elif self.boxMarketChoice.get() == "OS(複委託)":
                nMarketType = 3
            elif self.boxMarketChoice.get() == "OF(海外期貨)":
                nMarketType = 4
            elif self.boxMarketChoice.get() == "OO(海外選擇權)":
                nMarketType = 5
            m_nCode = skO.SetMaxQty(nMarketType,int(self.lbMaxQuantity.get()))
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "SetMaxQty", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)

    # 6.限制委託筆數
    def __btnMaxCount_Click(self):
        try:
            if self.boxMarketChoice.get() == "TS (證券)":
                nMarketType = 0
            elif self.boxMarketChoice.get() == "TF(期貨)":
                nMarketType = 1
            elif self.boxMarketChoice.get() == "TO(選擇權)":
                nMarketType = 2
            elif self.boxMarketChoice.get() == "OS(複委託)":
                nMarketType = 3
            elif self.boxMarketChoice.get() == "OF(海外期貨)":
                nMarketType = 4
            elif self.boxMarketChoice.get() == "OO(海外選擇權)":
                nMarketType = 5
            m_nCode = skO.SetMaxCount(nMarketType,int(self.lbMaxCount.get()))
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "SetMaxCount", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)

    #7.帳號解鎖
    def __btnUnlockOrder_Click(self):
        try:
            if self.boxMarketChoice.get() == "TS (證券)":
                nMarketType = 0
            elif self.boxMarketChoice.get() == "TF(期貨)":
                nMarketType = 1
            elif self.boxMarketChoice.get() == "TO(選擇權)":
                nMarketType = 2
            elif self.boxMarketChoice.get() == "OS(複委託)":
                nMarketType = 3
            elif self.boxMarketChoice.get() == "OF(海外期貨)":
                nMarketType = 4
            elif self.boxMarketChoice.get() == "OO(海外選擇權)":
                nMarketType = 5
            m_nCode = skO.UnlockOrder(nMarketType)
            self.__obj['msg'].SendReturnMessage("Order", m_nCode, "UnlockOrder", GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！", e)
            
    

class SKCenterLibEvent():
    def __init__(self):
        self.__obj = dict(
            msg = MessageControl.MessageControl(),
        )

    # #定時Timer通知
    # def OnTimer(self,nTime):
    #     nTime = str(nTime).zfill(6)
    #     strMsg = "OnTime： " + nTime[0:2] + ":" + nTime[2:4] + ":" + nTime[4:]
    #     self.__obj["msg"].WriteMessage(strMsg,GlobalListInformation)

    #同意書未簽署通知
    def OnShowAgreement(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    #SGX API DMA專線下單連線狀態。
    def OnNotifySGXAPIOrderStatus(self,nStatus,bstrOFAccount):
        if nStatus == 3026:
            strMsg = (bstrOFAccount+"SGX_API專線建立完成")
        elif nStatus == 3002:
            strMsg = (bstrOFAccount+"SGX_API專線斷線")
        else:
            strMsg = (bstrOFAccount+"SGX_API登入失敗")
        self.__obj["msg"].WriteMessage(strMsg,GlobalListInformation)

class SKOrderLibEvent():
    __account_list = dict(
        stock = [],
        future = [],
        sea_future = [],
        foreign_stock = [],
    )

    def __init__(self):
        self.__obj = dict(
            msg = MessageControl.MessageControl(),
        )

    def OnAccount(self, bstrLogInID, bstrAccountData):
        strValues = bstrAccountData.split(',')
        strAccount = strValues[1] + strValues[3]

        if strValues[0] == 'TS':
            SKOrderLibEvent.__account_list['stock'].append(strAccount)
            GlobalboxStockAccount['values'] = SKOrderLibEvent.__account_list['stock']

        elif strValues[0] == 'TF':
            SKOrderLibEvent.__account_list['future'].append(strAccount)
            GlobalboxFutureAccount['values'] = SKOrderLibEvent.__account_list['future']
        elif strValues[0] == 'OF':
            SKOrderLibEvent.__account_list['sea_future'].append(strAccount)
            GlobalboxSeaFutureAccount['values'] = SKOrderLibEvent.__account_list['sea_future']
        elif strValues[0] == 'OS':
            SKOrderLibEvent.__account_list['foreign_stock'].append(strAccount)
            GlobalboxForeignStockAccount['values'] = SKOrderLibEvent.__account_list['foreign_stock']

    def OnOpenInterest(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnFutureRights(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnAsyncOrder(self,nThreadID,nCode,bstrMessage):
        self.__obj["msg"].WriteMessage("ThreadID:"+str(nThreadID)+"_Code:"+str(nCode)+"_Message:"+bstrMessage,GlobalListInformation)

    def OnOverseaFutureOpenInterest(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnOverSeaFutureRight(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnOverseaFuture(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnOverseaOption(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnRealBalanceReport(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnBalanceQuery(self, bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnRequestProfitReport(self, bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnMarginPurchaseAmountLimit(self,bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnAsyncOrderOLID(self,nThreadID,nCode,bstrMessage,bstrOrderLinkedID):
        strMsg = "Message: "+bstrMessage+" "+bstrOrderLinkedID
        self.__obj["msg"].WriteMessage("ThreadID:"+str(nThreadID)+"_Code:"+str(nCode)+"_Message:"+strMsg,GlobalListInformation)

    def OnStopLossReport(self, bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)

    def OnTSSmartStrategyReport(self, bstrData):
        self.__obj["msg"].WriteMessage(bstrData,GlobalListInformation)


class SKReplyLibEvent():
    def __init__(self):
        self.__obj = dict(
            msg = MessageControl.MessageControl(),
        )

    def OnReplyMessage(self,bstrUserID, bstrMessages):
        sConfirmCode = -1
        self.__obj["msg"].WriteMessage(bstrMessages,GlobalListInformation)
        return sConfirmCode

# comtypes使用此方式註冊callback
SKReplyEvent = SKReplyLibEvent()
SKReplyLibEventHandler = comtypes.client.GetEvents(skR, SKReplyEvent)

#comtypes使用此方式註冊callback
SKOrderEvent = SKOrderLibEvent()
SKOrderLibEventHandler = comtypes.client.GetEvents(skO, SKOrderEvent)

# comtypes使用此方式註冊callback
SKCenterEvent = SKCenterLibEvent()
SKCenterLibEventHandler = comtypes.client.GetEvents(skC,SKCenterEvent)

# win32com使用此方式註冊callback
# SKOrderLibEventHandler = win32com.client.WithEvents(SKOrderLib, SKOrderLibEvent)

if __name__ == '__main__':
    root = Tk()
    root.title("PythonExampleOrder")
    root["background"] = "#F5F5F5"

    s = Style()

    for _ in "Red.TLabelframe",:
        s.configure(_, foreground = "#FFC0CB", background = "#F5F5F5")

    for _ in "Pink.TFrame", "Pink.TLabelframe", "Pink.TNotebook":
        s.configure(_, background = "#F5F5F5")

    for _ in "Pink.TLabel", "Pink.TRadiobutton", "Pink.TCheckbutton":
        s.configure(_, font = 1, foreground = "#000000", background = "#F5F5F5")

    s.configure("Pink.TButton", font = 1, foreground = "#000000", background = "#F5F5F5")
    s.configure("PinkFiller.TLabel", font = 1, foreground = "#F5F5F5", background = "#F5F5F5")

    # Center
    __FrameLogin(master = root)

    # OrderTab
    root.TabControl = Notebook(root, style="Pink.TNotebook")
    root.TabControl.grid(column = 0, row = 1, sticky = 'ew', padx = 10, pady = 5)
    root.TabControl.add(__FrameOrder(master = root), text="下單")

    root.mainloop()

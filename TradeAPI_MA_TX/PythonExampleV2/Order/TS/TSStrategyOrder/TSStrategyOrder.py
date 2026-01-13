# API com元件初始化
import comtypes.client
comtypes.client.GetModule(r'SKCOM.dll')
import comtypes.gen.SKCOMLib as sk

# 群益API元件導入Python code內用的物件宣告
m_pSKCenter = comtypes.client.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
m_pSKReply = comtypes.client.CreateObject(sk.SKReplyLib,interface=sk.ISKReplyLib)
m_pSKOrder = comtypes.client.CreateObject(sk.SKOrderLib,interface=sk.ISKOrderLib)

# 畫視窗用物件
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import messagebox
from tkinter import filedialog

# 引入設定檔 (Settings for Combobox)
import Config as Config

# 全域變數

# 登入帳號:交易帳號
dictUserID = {}
dictUserID["更新帳號"] = ["無"]

# 是否為非同步委託
bAsyncOrder = False

######################################################################################################################################
# ReplyLib事件
class SKReplyLibEvent():
    def OnReplyMessage(self, bstrUserID, bstrMessages):
        nConfirmCode = -1
        msg = "【註冊公告OnReplyMessage】" + bstrUserID + "_" + bstrMessages;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
        return nConfirmCode
SKReplyEvent = SKReplyLibEvent();
SKReplyLibEventHandler = comtypes.client.GetEvents(m_pSKReply, SKReplyEvent);

# OrderLib事件
class SKOrderLibEvent():
    # 帳號資訊
    def OnAccount(self, bstrLogInID, bstrAccountData):
        msg = "【OnAccount】" + bstrLogInID + "_" + bstrAccountData;        
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')

        values = bstrAccountData.split(',')
        # broker ID (IB)4碼 + 帳號7碼
        Account = values[1] + values[3]

        if bstrLogInID in dictUserID:
            accountExists = False
            for value in dictUserID[bstrLogInID]:
                if value == Account:
                    accountExists = True
                    break
            if accountExists == False:
                dictUserID[bstrLogInID].append(Account)
        else:
            dictUserID[bstrLogInID] = [Account]
    # 證券智慧單被動查詢結果。透過呼叫GetTSSmartStrategyReport後，資訊由該事件回傳。
    def OnTSSmartStrategyReport(self, bstrData):
        msg = "【OnTSSmartStrategyReport】" + bstrData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 非同步委託結果。
    def OnAsyncOrder(self, nThreadID, nCode, bstrMessage):
        msg = "【OnAsyncOrder】" + str(nThreadID) + str(nCode) + bstrMessage
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
SKOrderEvent = SKOrderLibEvent()
SKOrderLibEventHandler = comtypes.client.GetEvents(m_pSKOrder, SKOrderEvent)

######################################################################################################################################
# GUI
######################################################################################################################################
#MessageForm
class MessageForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        #richTextBox

        # richTextBoxMethodMessage
        self.richTextBoxMethodMessage = tk.Listbox(self, height=5, width=150)
        self.richTextBoxMethodMessage.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxMethodMessage
        richTextBoxMethodMessage = self.richTextBoxMethodMessage

        # richTextBoxMessage
        self.richTextBoxMessage = tk.Listbox(self, height=5, width=150)
        self.richTextBoxMessage.grid(column = 0, row = 10, columnspan=5)

        global richTextBoxMessage
        richTextBoxMessage = self.richTextBoxMessage

        # comboBoxSKCenterLib_SetAuthority
        tk.Label(self, text = "連線環境").grid(row = 12,column = 0)
            #輸入框
        comboBoxSKCenterLib_SetAuthority = ttk.Combobox(self, state='readonly')
        comboBoxSKCenterLib_SetAuthority['values'] = Config.comboBoxSKCenterLib_SetAuthority
        comboBoxSKCenterLib_SetAuthority.grid(row = 13,column = 0)

        def on_comboBoxSKCenterLib_SetAuthority(event):
            if comboBoxSKCenterLib_SetAuthority.get() == "正式環境":
                nAuthorityFlag = 0
            elif comboBoxSKCenterLib_SetAuthority.get() == "正式環境SGX":
                nAuthorityFlag = 1
            elif comboBoxSKCenterLib_SetAuthority.get() == "測試環境":
                nAuthorityFlag = 2
            elif comboBoxSKCenterLib_SetAuthority.get() == "測試環境SGX":
                nAuthorityFlag = 3
            nCode = m_pSKCenter.SKCenterLib_SetAuthority(nAuthorityFlag)
            msg = "【SKCenterLib_SetAuthority】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')

        comboBoxSKCenterLib_SetAuthority.bind("<<ComboboxSelected>>", on_comboBoxSKCenterLib_SetAuthority)

        # textBoxCustCertID
        self.labelCustCertID = tk.Label(self)
        self.labelCustCertID["text"] = "CustCertID:"
            #輸入框
        self.textBoxCustCertID = tk.Entry(self)


        # checkBoxisAP
        self.checkBoxisAP = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxisAP["variable"] = self.var1
        self.checkBoxisAP["onvalue"] = 1
        self.checkBoxisAP["offvalue"] = 0
        self.checkBoxisAP["text"] = "AP/APH身分"
        self.checkBoxisAP["command"] = self.checkBoxisAP_CheckedChanged
        self.checkBoxisAP.grid( row = 14,column = 0)


        tk.Label(self, text = "登入後請選擇這裡=>").grid(column = 0, row = 11)
            #輸入框
        self.comboBoxUserID = ttk.Combobox(self, state='readonly')
        self.comboBoxUserID['values'] = list(dictUserID.keys())
        self.comboBoxUserID.grid(column = 1, row = 11)
        global comboBoxUserID
        comboBoxUserID = self.comboBoxUserID

        def on_comboBoxUserID(event):
            m_pSKOrder.SKOrderLib_Initialize() # 這裡有做下單初始化
            m_pSKOrder.GetUserAccount() # 拿到交易帳號
            self.comboBoxUserID['values'] = list(dictUserID.keys())
            self.comboBoxAccount['values'] = dictUserID[self.comboBoxUserID.get()]
        self.comboBoxUserID.bind("<<ComboboxSelected>>", on_comboBoxUserID)

        # comboBoxAccount
            #輸入框
        self.comboBoxAccount = ttk.Combobox(self, state='readonly')
        self.comboBoxAccount.grid(column = 2, row = 11)  
        global comboBoxAccount
        comboBoxAccount = self.comboBoxAccount

        # textBoxUserID
        self.labelUserID = tk.Label(self)
        self.labelUserID["text"] = "UserID："
        self.labelUserID.grid(row=13, column=1)
            #輸入框
        self.textBoxUserID = tk.Entry(self)
        self.textBoxUserID.grid(row=13, column=2)

        global textBoxUserID
        textBoxUserID = self.textBoxUserID

        # textBoxPassword
        self.labelPassword = tk.Label(self)
        self.labelPassword["text"] = "Password："
        self.labelPassword.grid(row=14, column=1)
            #輸入框
        self.textBoxPassword = tk.Entry(self)
        self.textBoxPassword['show'] = '*'
        self.textBoxPassword.grid(row=14, column=2)

        global textBoxPassword
        textBoxPassword = self.textBoxPassword

        # labelSKCenterLib_GetSKAPIVersionAndBit
        self.labelSKCenterLib_GetSKAPIVersionAndBit = tk.Label(self)
        self.labelSKCenterLib_GetSKAPIVersionAndBit["text"] = m_pSKCenter.SKCenterLib_GetSKAPIVersionAndBit("xxxxxxxxxx")
        self.labelSKCenterLib_GetSKAPIVersionAndBit.grid(row = 11, column = 4)

        # buttonSKCenterLib_SetLogPath
        self.buttonSKCenterLib_SetLogPath = tk.Button(self)
        self.buttonSKCenterLib_SetLogPath["text"] = "變更LOG路徑"
        self.buttonSKCenterLib_SetLogPath["command"] = self.buttonSKCenterLib_SetLogPath_Click
        self.buttonSKCenterLib_SetLogPath.grid(row = 11, column = 3)
        
        # buttonSKCenterLib_RequestAgreement
        self.buttonSKCenterLib_RequestAgreement = tk.Button(self)
        self.buttonSKCenterLib_RequestAgreement["text"] = "同意書簽署狀態"
        self.buttonSKCenterLib_RequestAgreement["command"] = self.buttonSKCenterLib_RequestAgreement_Click
        self.buttonSKCenterLib_RequestAgreement.grid(row = 12, column = 3)

        # buttonSKCenterLib_GetLastLogInfo
        self.buttonSKCenterLib_GetLastLogInfo = tk.Button(self)
        self.buttonSKCenterLib_GetLastLogInfo["text"] = "最後一筆LOG"
        self.buttonSKCenterLib_GetLastLogInfo["command"] = self.buttonSKCenterLib_GetLastLogInfo_Click
        self.buttonSKCenterLib_GetLastLogInfo.grid(row = 13, column = 3)
            
        # buttonSKCenterLib_Login
        self.buttonSKCenterLib_Login = tk.Button(self)
        self.buttonSKCenterLib_Login["text"] = "Login"
        self.buttonSKCenterLib_Login["command"] = self.buttonSKCenterLib_Login_Click
        self.buttonSKCenterLib_Login.grid(row=15, column=2)

        # buttonSKCenterLib_GenerateKeyCert
        self.buttonSKCenterLib_GenerateKeyCert = tk.Button(self)
        self.buttonSKCenterLib_GenerateKeyCert["text"] = "雙因子驗證KEY"
        self.buttonSKCenterLib_GenerateKeyCert["command"] = self.buttonSKCenterLib_GenerateKeyCert_Click

        # buttonSKOrderLib_InitialProxyByID
        self.buttonSKOrderLib_InitialProxyByID = tk.Button(self)
        self.buttonSKOrderLib_InitialProxyByID["text"] = "Proxy初始/連線"
        self.buttonSKOrderLib_InitialProxyByID["command"] = self.buttonSKOrderLib_InitialProxyByID_Click
        self.buttonSKOrderLib_InitialProxyByID.grid(row=12, column=4)

        # buttonProxyDisconnectByID
        self.buttonProxyDisconnectByID = tk.Button(self)
        self.buttonProxyDisconnectByID["text"] = "Proxy斷線"
        self.buttonProxyDisconnectByID["command"] = self.buttonProxyDisconnectByID_Click
        self.buttonProxyDisconnectByID.grid(row=13, column=4)

        # buttonProxyReconnectByID
        self.buttonProxyReconnectByID = tk.Button(self)
        self.buttonProxyReconnectByID["text"] = "Proxy重新連線"
        self.buttonProxyReconnectByID["command"] = self.buttonProxyReconnectByID_Click
        self.buttonProxyReconnectByID.grid(row=14, column=4)
        
        # buttonAddSGXAPIOrderSocket_Click
        self.buttonAddSGXAPIOrderSocket_Click = tk.Button(self)
        self.buttonAddSGXAPIOrderSocket_Click["text"] = "建立SGX專線"
        self.buttonAddSGXAPIOrderSocket_Click["command"] = self.buttonAddSGXAPIOrderSocket_Click_Click
        self.buttonAddSGXAPIOrderSocket_Click.grid(row=15, column=0)
        
    # buttonSKCenterLib_Login
    def buttonSKCenterLib_Login_Click(self):
        nCode = m_pSKCenter.SKCenterLib_Login(textBoxUserID.get(),textBoxPassword.get())

        msg = "【SKCenterLib_Login】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    # checkBoxisAP
    def checkBoxisAP_CheckedChanged(self):
        if self.var1.get() == 1:
            self.labelCustCertID.grid(row = 12, column = 1)
            self.textBoxCustCertID.grid( row = 12,column = 2)
            self.buttonSKCenterLib_GenerateKeyCert.grid(row = 15, column = 1)
        else:
            self.labelCustCertID.grid_remove()
            self.textBoxCustCertID.grid_remove()
            self.buttonSKCenterLib_GenerateKeyCert.grid_remove()
    
    # buttonSKCenterLib_GenerateKeyCert_Click
    def buttonSKCenterLib_GenerateKeyCert_Click(self):    
        # 僅適用AP及APH無憑證身份
        # 請在登入前，安裝附屬帳號ID有效憑證，再透過此函式產生雙因子登入憑證資訊
        # 雙因子登入必須透過憑證，使用群組的帳號登入，必須自行選擇群組內其一附屬帳號，以進行驗證憑證相關程序    
        nCode = m_pSKCenter.SKCenterLib_GenerateKeyCert(self.textBoxUserID.get(),self.textBoxCustCertID.get())

        msg = "【SKCenterLib_GenerateKeyCert】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonSKOrderLib_InitialProxyByID_Click(self):
        nCode = m_pSKOrder.SKOrderLib_InitialProxyByID(comboBoxUserID.get())

        msg = "【SKOrderLib_InitialProxyByID】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonProxyDisconnectByID_Click(self):
        nCode = m_pSKOrder.ProxyDisconnectByID(comboBoxUserID.get())

        msg = "【ProxyDisconnectByID】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonProxyReconnectByID_Click(self):
        nCode = m_pSKOrder.ProxyReconnectByID(comboBoxUserID.get())

        msg = "【ProxyReconnectByID】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    # buttonAddSGXAPIOrderSocket_Click_Click
    def buttonAddSGXAPIOrderSocket_Click_Click(self):
        # 建立SGX API專線。注意，SGX API DMA專線需先向交易後台申請，方可使用。
        nCode = m_pSKOrder.AddSGXAPIOrderSocket(comboBoxUserID.get(),comboBoxAccount.get())

        msg = "【AddSGXAPIOrderSocket】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

        # buttonSKCenterLib_SetLogPath_Click
    def buttonSKCenterLib_SetLogPath_Click(self):
        def select_folder():
            bstrPath = ""
            folder_selected = filedialog.askdirectory(title="選擇資料夾")

            if folder_selected:
                bstrPath = folder_selected
                messagebox.showinfo("選擇的資料夾", "選擇的資料夾: " + bstrPath)

            return bstrPath

        bstrPath = select_folder()
        if not bstrPath:
            messagebox.showwarning("未選擇資料夾!", "未選擇資料夾!")
        else:
            # 設定LOG檔存放路徑。預設LOG存放於執行之應用程式下，如要變更LOG路徑，此函式需最先呼叫。
            nCode = m_pSKCenter.SKCenterLib_SetLogPath(bstrPath)

            # 取得回傳訊息
            msg = "【SKCenterLib_SetLogPath】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
            richTextBoxMethodMessage.insert('end', msg + "\n")
            richTextBoxMethodMessage.see('end')

    # buttonSKCenterLib_RequestAgreement_Click
    def buttonSKCenterLib_RequestAgreement_Click(self):    
        # 取得所有聲明書及同意書簽署狀態
        nCode = m_pSKCenter.SKCenterLib_RequestAgreement(comboBoxUserID.get())

        msg = "【SKCenterLib_RequestAgreement】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    # buttonSKCenterLib_GetLastLogInfo_Click
    def buttonSKCenterLib_GetLastLogInfo_Click(self):    
        # 取得最後一筆LOG內容
        msg = m_pSKCenter.SKCenterLib_GetLastLogInfo()

        msg = "【SKCenterLib_GetLastLogInfo】" + msg
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#DayTradeForm
class DayTradeForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrStockNoDT
        tk.Label(self, text = "委託股票代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoDT = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoDT.grid(row=0, column=2)

        global textBoxbstrStockNoDT
        textBoxbstrStockNoDT = self.textBoxbstrStockNoDT

        # comboBoxnBuySellDT
        tk.Label(self, text = "0:現股買/1:無券賣出").grid(row=0, column=3)
            #輸入框
        self.comboBoxnBuySellDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySellDT['values'] = Config.comboBoxnBuySellDT
        self.comboBoxnBuySellDT.grid(row=0, column=4)

        global comboBoxnBuySellDT
        comboBoxnBuySellDT = self.comboBoxnBuySellDT

        # textBoxnQtyDT
        tk.Label(self, text = "委託張數").grid(row=1, column=1)
        #輸入框
        self.textBoxnQtyDT = tk.Entry(self, width= 6)
        self.textBoxnQtyDT.grid(row=1, column=2)

        global textBoxnQtyDT
        textBoxnQtyDT = self.textBoxnQtyDT

        # comboBoxnOrderPriceCondDT
        tk.Label(self, text = "委託時效").grid(row=1, column=3)
            #輸入框
        self.comboBoxnOrderPriceCondDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceCondDT['values'] = Config.comboBoxnOrderPriceCondDT
        self.comboBoxnOrderPriceCondDT.grid(row=1, column=4)

        global comboBoxnOrderPriceCondDT
        comboBoxnOrderPriceCondDT = self.comboBoxnOrderPriceCondDT

        # textBoxbstrOrderPriceDT
        tk.Label(self, text = "當沖單進場委託價").grid(row=2, column=1)
        #輸入框
        self.textBoxbstrOrderPriceDT = tk.Entry(self, width= 6)
        self.textBoxbstrOrderPriceDT.grid(row=2, column=2)

        global textBoxbstrOrderPriceDT
        textBoxbstrOrderPriceDT = self.textBoxbstrOrderPriceDT

        # comboBoxnOrderPriceTypeDT
        tk.Label(self, text = "委託價類別").grid(row=2, column=3)
            #輸入框
        self.comboBoxnOrderPriceTypeDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeDT['values'] = Config.comboBoxnOrderPriceTypeDT
        self.comboBoxnOrderPriceTypeDT.grid(row=2, column=4)

        global comboBoxnOrderPriceTypeDT
        comboBoxnOrderPriceTypeDT = self.comboBoxnOrderPriceTypeDT

        # comboBoxnInnerOrderIsMITDT
        tk.Label(self, text = "進場是否MIT").grid(row=3, column=1)
            #輸入框
        self.comboBoxnInnerOrderIsMITDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnInnerOrderIsMITDT['values'] = Config.comboBoxnInnerOrderIsMITDT
        self.comboBoxnInnerOrderIsMITDT.grid(row=3, column=2)

        global comboBoxnInnerOrderIsMITDT
        comboBoxnInnerOrderIsMITDT = self.comboBoxnInnerOrderIsMITDT

        # comboBoxnMITDirDT
        tk.Label(self, text = "進場MIT觸價方向").grid(row=3, column=3)
            #輸入框
        self.comboBoxnMITDirDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnMITDirDT['values'] = Config.comboBoxnMITDirDT
        self.comboBoxnMITDirDT.grid(row=3, column=4)

        global comboBoxnMITDirDT
        comboBoxnMITDirDT = self.comboBoxnMITDirDT

        # textBoxbstrMITTriggerPriceDT
        tk.Label(self, text = "進場MIT觸發價(若未啟用MIT,請填0)").grid(row=3, column=5)
        #輸入框
        self.textBoxbstrMITTriggerPriceDT = tk.Entry(self, width= 6)
        self.textBoxbstrMITTriggerPriceDT.grid(row=3, column=6)

        global textBoxbstrMITTriggerPriceDT
        textBoxbstrMITTriggerPriceDT = self.textBoxbstrMITTriggerPriceDT

        # textBoxbstrMITDealPriceDT
        tk.Label(self, text = "進場MIT當下市價(若未啟用MIT,請填0)").grid(row=3, column=7)
        #輸入框
        self.textBoxbstrMITDealPriceDT = tk.Entry(self, width= 6)
        self.textBoxbstrMITDealPriceDT.grid(row=3, column=8)

        global textBoxbstrMITDealPriceDT
        textBoxbstrMITDealPriceDT = self.textBoxbstrMITDealPriceDT

        # comboBoxnStopLossFlagDT
        tk.Label(self, text = "出場停損條件").grid(row=4, column=1)
            #輸入框
        self.comboBoxnStopLossFlagDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnStopLossFlagDT['values'] = Config.comboBoxnStopLossFlagDT
        self.comboBoxnStopLossFlagDT.grid(row=4, column=2)

        global comboBoxnStopLossFlagDT
        comboBoxnStopLossFlagDT = self.comboBoxnStopLossFlagDT

        # comboBoxnRDOSLPercent
        tk.Label(self, text = "停損類型").grid(row=4, column=3)
            #輸入框
        self.comboBoxnRDOSLPercent = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnRDOSLPercent['values'] = Config.comboBoxnRDOSLPercent
        self.comboBoxnRDOSLPercent.grid(row=4, column=4)

        global comboBoxnRDOSLPercent
        comboBoxnRDOSLPercent = self.comboBoxnRDOSLPercent

        # textBoxbstrSLTrigger
        tk.Label(self, text = "停損觸發價").grid(row=4, column=5)
        #輸入框
        self.textBoxbstrSLTrigger = tk.Entry(self, width= 6)
        self.textBoxbstrSLTrigger.grid(row=4, column=6)

        global textBoxbstrSLTrigger
        textBoxbstrSLTrigger = self.textBoxbstrSLTrigger

        # textBoxbstrSLPercentDT
        tk.Label(self, text = "停損百分比").grid(row=4, column=7)
        #輸入框
        self.textBoxbstrSLPercentDT = tk.Entry(self, width= 6)
        self.textBoxbstrSLPercentDT.grid(row=4, column=8)

        global textBoxbstrSLPercentDT
        textBoxbstrSLPercentDT = self.textBoxbstrSLPercentDT

        # textBoxbstrSLOrderPriceDT
        tk.Label(self, text = "停損委託價").grid(row=4, column=9)
        #輸入框
        self.textBoxbstrSLOrderPriceDT = tk.Entry(self, width= 6)
        self.textBoxbstrSLOrderPriceDT.grid(row=4, column=10)

        global textBoxbstrSLOrderPriceDT
        textBoxbstrSLOrderPriceDT = self.textBoxbstrSLOrderPriceDT

        # comboBoxnRDSLMarketPriceType
        tk.Label(self, text = "停損委託價方式").grid(row=4, column=11)
            #輸入框
        self.comboBoxnRDSLMarketPriceType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnRDSLMarketPriceType['values'] = Config.comboBoxnRDSLMarketPriceType
        self.comboBoxnRDSLMarketPriceType.grid(row=4, column=12)

        global comboBoxnRDSLMarketPriceType
        comboBoxnRDSLMarketPriceType = self.comboBoxnRDSLMarketPriceType

        # comboBoxnStopLossOrderCond
        tk.Label(self, text = "停損出場時效").grid(row=4, column=13)
            #輸入框
        self.comboBoxnStopLossOrderCond = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnStopLossOrderCond['values'] = Config.comboBoxnStopLossOrderCond
        self.comboBoxnStopLossOrderCond.grid(row=4, column=14)

        global comboBoxnStopLossOrderCond
        comboBoxnStopLossOrderCond = self.comboBoxnStopLossOrderCond

        # comboBoxnTakeProfitFlagDT
        tk.Label(self, text = "出場停利條件").grid(row=5, column=1)
            #輸入框
        self.comboBoxnTakeProfitFlagDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTakeProfitFlagDT['values'] = Config.comboBoxnTakeProfitFlagDT
        self.comboBoxnTakeProfitFlagDT.grid(row=5, column=2)

        global comboBoxnTakeProfitFlagDT
        comboBoxnTakeProfitFlagDT = self.comboBoxnTakeProfitFlagDT

        # comboBoxnRDOTPPercent
        tk.Label(self, text = "停利類型").grid(row=5, column=3)
            #輸入框
        self.comboBoxnRDOTPPercent = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnRDOTPPercent['values'] = Config.comboBoxnRDOTPPercent
        self.comboBoxnRDOTPPercent.grid(row=5, column=4)

        global comboBoxnRDOTPPercent
        comboBoxnRDOTPPercent = self.comboBoxnRDOTPPercent

        # textBoxbstrTPTrigger
        tk.Label(self, text = "停利觸發價").grid(row=5, column=5)
        #輸入框
        self.textBoxbstrTPTrigger = tk.Entry(self, width= 6)
        self.textBoxbstrTPTrigger.grid(row=5, column=6)

        global textBoxbstrTPTrigger
        textBoxbstrTPTrigger = self.textBoxbstrTPTrigger

        # textBoxbstrTPPercent
        tk.Label(self, text = "停利百分比").grid(row=5, column=7)
        #輸入框
        self.textBoxbstrTPPercent = tk.Entry(self, width= 6)
        self.textBoxbstrTPPercent.grid(row=5, column=8)

        global textBoxbstrTPPercent
        textBoxbstrTPPercent = self.textBoxbstrTPPercent

        # textBoxbstrTPOrderPriceDT
        tk.Label(self, text = "停利委託價").grid(row=5, column=9)
        #輸入框
        self.textBoxbstrTPOrderPriceDT = tk.Entry(self, width= 6)
        self.textBoxbstrTPOrderPriceDT.grid(row=5, column=10)

        global textBoxbstrTPOrderPriceDT
        textBoxbstrTPOrderPriceDT = self.textBoxbstrTPOrderPriceDT

        # comboBoxnRDTPMarketPriceType
        tk.Label(self, text = "停利委託價方式").grid(row=5, column=11)
            #輸入框
        self.comboBoxnRDTPMarketPriceType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnRDTPMarketPriceType['values'] = Config.comboBoxnRDTPMarketPriceType
        self.comboBoxnRDTPMarketPriceType.grid(row=5, column=12)

        global comboBoxnRDTPMarketPriceType
        comboBoxnRDTPMarketPriceType = self.comboBoxnRDTPMarketPriceType

        # comboBoxnTakeProfitOrderCond
        tk.Label(self, text = "停利出場時效").grid(row=5, column=13)
            #輸入框
        self.comboBoxnTakeProfitOrderCond = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTakeProfitOrderCond['values'] = Config.comboBoxnTakeProfitOrderCond
        self.comboBoxnTakeProfitOrderCond.grid(row=5, column=14)

        global comboBoxnTakeProfitOrderCond
        comboBoxnTakeProfitOrderCond = self.comboBoxnTakeProfitOrderCond

        # comboBoxnClearAllFlagDT
        tk.Label(self, text = "執行時間出清").grid(row=6, column=1)
            #輸入框
        self.comboBoxnClearAllFlagDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnClearAllFlagDT['values'] = Config.comboBoxnClearAllFlagDT
        self.comboBoxnClearAllFlagDT.grid(row=6, column=2)

        global comboBoxnClearAllFlagDT
        comboBoxnClearAllFlagDT = self.comboBoxnClearAllFlagDT

        # textBoxbstrClearCancelTimeDT
        tk.Label(self, text = "出清時間-時＋分（hhmm）{每日13:20截止)").grid(row=6, column=3)
        #輸入框
        self.textBoxbstrClearCancelTimeDT = tk.Entry(self, width= 6)
        self.textBoxbstrClearCancelTimeDT.grid(row=6, column=4)

        global textBoxbstrClearCancelTimeDT
        textBoxbstrClearCancelTimeDT = self.textBoxbstrClearCancelTimeDT

        # textBoxbstrClearAllOrderPriceDT
        tk.Label(self, text = "出清委託價").grid(row=6, column=5)
        #輸入框
        self.textBoxbstrClearAllOrderPriceDT = tk.Entry(self, width= 6)
        self.textBoxbstrClearAllOrderPriceDT.grid(row=6, column=6)

        global textBoxbstrClearAllOrderPriceDT
        textBoxbstrClearAllOrderPriceDT = self.textBoxbstrClearAllOrderPriceDT

        # comboBoxnClearAllPriceTypeDT
        tk.Label(self, text = "出清委託價方式").grid(row=6, column=7)
            #輸入框
        self.comboBoxnClearAllPriceTypeDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnClearAllPriceTypeDT['values'] = Config.comboBoxnClearAllPriceTypeDT
        self.comboBoxnClearAllPriceTypeDT.grid(row=6, column=8)

        global comboBoxnClearAllPriceTypeDT
        comboBoxnClearAllPriceTypeDT = self.comboBoxnClearAllPriceTypeDT

        # comboBoxnClearOrderCondDT
        tk.Label(self, text = "出清出場時效").grid(row=6, column=9)
            #輸入框
        self.comboBoxnClearOrderCondDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnClearOrderCondDT['values'] = Config.comboBoxnClearOrderCondDT
        self.comboBoxnClearOrderCondDT.grid(row=6, column=10)

        global comboBoxnClearOrderCondDT
        comboBoxnClearOrderCondDT = self.comboBoxnClearOrderCondDT

        # comboBoxnFinalClearFlagDT
        tk.Label(self, text = "盤後定盤交易").grid(row=7, column=1)
            #輸入框
        self.comboBoxnFinalClearFlagDT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnFinalClearFlagDT['values'] = Config.comboBoxnFinalClearFlagDT
        self.comboBoxnFinalClearFlagDT.grid(row=7, column=2)

        global comboBoxnFinalClearFlagDT
        comboBoxnFinalClearFlagDT = self.comboBoxnFinalClearFlagDT

        # buttonSendStockStrategyDayTrade
        self.buttonSendStockStrategyDayTrade = tk.Button(self)
        self.buttonSendStockStrategyDayTrade["text"] = "當沖送出"
        self.buttonSendStockStrategyDayTrade["command"] = self.buttonSendStockStrategyDayTrade_Click
        self.buttonSendStockStrategyDayTrade.grid(row=8, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendStockStrategyDayTrade_Click(self):
        
        pOrder = sk.STOCKSTRATEGYORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()

        pOrder.bstrStockNo = textBoxbstrStockNoDT.get()
        pOrder.nQty = int(textBoxnQtyDT.get())
        pOrder.bstrOrderPrice = textBoxbstrOrderPriceDT.get()

        if (comboBoxnBuySellDT.get() == "0:現股買") :
            pOrder.nBuySell = 0
        elif (comboBoxnBuySellDT.get() == "1:無券賣出"):
            pOrder.nBuySell = 1

        if (comboBoxnOrderPriceCondDT.get() == "0:ROD"):
            pOrder.nOrderPriceCond = 0
        elif (comboBoxnOrderPriceCondDT.get() == "3:IOC"):
            pOrder.nOrderPriceCond = 3
        elif (comboBoxnOrderPriceCondDT.get() == "4:FOK"):
            pOrder.nOrderPriceCond = 4

        if (comboBoxnOrderPriceTypeDT.get() == "1:市價"):
            pOrder.nOrderPriceType = 1
        elif (comboBoxnOrderPriceTypeDT.get() == "2:限價"):
            pOrder.nOrderPriceType = 2

        if (comboBoxnInnerOrderIsMITDT.get() == "0:N"):
            pOrder.nInnerOrderIsMIT = 0
        elif (comboBoxnInnerOrderIsMITDT.get() == "1:Y"):
            pOrder.nInnerOrderIsMIT = 1

        if (comboBoxnMITDirDT.get() == "0:未啟用MIT"):
            pOrder.nMITDir = 0
        elif (comboBoxnMITDirDT.get() == "1:向上觸發(大於等於)"):
            pOrder.nMITDir = 1
        elif (comboBoxnMITDirDT.get() == "2:向下觸發(小於等於)"):
            pOrder.nMITDir = 2

        pOrder.bstrMITTriggerPrice = textBoxbstrMITTriggerPriceDT.get()
        pOrder.bstrMITDealPrice = textBoxbstrMITDealPriceDT.get()

        if (comboBoxnClearAllFlagDT.get() == "0:否"):
            pOrder.nClearAllFlag = 0
        elif (comboBoxnClearAllFlagDT.get() == "1:是"):
            pOrder.nClearAllFlag = 1

        pOrder.bstrClearCancelTime = textBoxbstrClearCancelTimeDT.get()

        if (comboBoxnClearAllPriceTypeDT.get() == "1:市價"):
            pOrder.nClearAllPriceType = 1
        elif (comboBoxnClearAllPriceTypeDT.get() == "2:限價"):
            pOrder.nClearAllPriceType = 2

        pOrder.bstrClearAllOrderPrice = textBoxbstrClearAllOrderPriceDT.get()

        if (comboBoxnFinalClearFlagDT.get() == "0:否"):
            pOrder.nFinalClearFlag = 0
        elif (comboBoxnFinalClearFlagDT.get() == "1:是"):
            pOrder.nFinalClearFlag = 1

        if (comboBoxnTakeProfitFlagDT.get() == "0:否"):
            pOrder.nTakeProfitFlag = 0
        elif (comboBoxnTakeProfitFlagDT.get() == "1:是"):
            pOrder.nTakeProfitFlag = 1

        if (comboBoxnRDOTPPercent.get() == "0:觸發價"):
            pOrder.nRDOTPPercent = 0
        elif (comboBoxnRDOTPPercent.get() == "1:漲幅"):
            pOrder.nRDOTPPercent = 1

        pOrder.bstrTPPercent = textBoxbstrTPPercent.get()
        pOrder.bstrTPTrigger = textBoxbstrTPTrigger.get()

        if (comboBoxnRDTPMarketPriceType.get() == "1:市價"):
            pOrder.nRDTPMarketPriceType = 1
        elif (comboBoxnRDTPMarketPriceType.get() == "2:限價"):
            pOrder.nRDTPMarketPriceType = 2

        pOrder.bstrTPOrderPrice = textBoxbstrTPOrderPriceDT.get()

        if (comboBoxnStopLossFlagDT.get() == "0:否"):
            pOrder.nStopLossFlag = 0
        elif (comboBoxnStopLossFlagDT.get() == "1:是"):
            pOrder.nStopLossFlag = 1

        if (comboBoxnRDOSLPercent.get() == "0:觸發價"):
            pOrder.nRDOSLPercent = 0
        elif (comboBoxnRDOSLPercent.get() == "1:漲跌幅"):
            pOrder.nRDOSLPercent = 1

        pOrder.bstrSLPercent = textBoxbstrSLPercentDT.get()
        pOrder.bstrSLTrigger = textBoxbstrSLTrigger.get()

        if (comboBoxnRDSLMarketPriceType.get() == "1:市價"):
            pOrder.nRDSLMarketPriceType = 1
        elif (comboBoxnRDSLMarketPriceType.get() == "2:限價"):
            pOrder.nRDSLMarketPriceType = 2

        pOrder.bstrSLOrderPrice = textBoxbstrSLOrderPriceDT.get()

        if (comboBoxnTakeProfitOrderCond.get() == "0:ROD"):
            pOrder.nTakeProfitOrderCond = 0
        elif (comboBoxnTakeProfitOrderCond.get() == "3:IOC"):
            pOrder.nTakeProfitOrderCond = 3
        elif (comboBoxnTakeProfitOrderCond.get() == "4:FOK"):
            pOrder.nTakeProfitOrderCond = 4

        if (comboBoxnStopLossOrderCond.get() == "0:ROD"):
            pOrder.nStopLossOrderCond = 0
        elif (comboBoxnStopLossOrderCond.get() == "3:IOC"):
            pOrder.nStopLossOrderCond = 3
        elif (comboBoxnStopLossOrderCond.get() == "4:FOK"):
            pOrder.nStopLossOrderCond = 4

        if (comboBoxnClearOrderCondDT.get() == "0:ROD"):
            pOrder.nClearOrderCond = 0
        elif (comboBoxnClearOrderCondDT.get() == "3:IOC"):
            pOrder.nClearOrderCond = 3
        elif (comboBoxnClearOrderCondDT.get() == "4:FOK"):
            pOrder.nClearOrderCond = 4

        # 送出證券智慧單當沖條件委託。
        bstrMessage,nCode= m_pSKOrder.SendStockStrategyDayTrade(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockStrategyDayTrade】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 

######################################################################################################################################
#ClearForm
class ClearForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrStockNoC
        tk.Label(self, text = "委託股票代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoC = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoC.grid(row=0, column=2)

        global textBoxbstrStockNoC
        textBoxbstrStockNoC = self.textBoxbstrStockNoC

        # comboBoxnBuySellC
        tk.Label(self, text = "0買;1賣").grid(row=0, column=3)
            #輸入框
        self.comboBoxnBuySellC = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySellC['values'] = Config.comboBoxnBuySellC
        self.comboBoxnBuySellC.grid(row=0, column=4)

        global comboBoxnBuySellC
        comboBoxnBuySellC = self.comboBoxnBuySellC

        # comboBoxnOrderTypeC
        tk.Label(self, text = "出清進場委託交易別(0:現股, 3:融資, 4:融券)").grid(row=0, column=5)
            #輸入框
        self.comboBoxnOrderTypeC = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderTypeC['values'] = Config.comboBoxnOrderTypeC
        self.comboBoxnOrderTypeC.grid(row=0, column=6)

        global comboBoxnOrderTypeC
        comboBoxnOrderTypeC = self.comboBoxnOrderTypeC

        # textBoxnQtyC
        tk.Label(self, text = "委託張數").grid(row=1, column=1)
        #輸入框
        self.textBoxnQtyC = tk.Entry(self, width= 6)
        self.textBoxnQtyC.grid(row=1, column=2)

        global textBoxnQtyC
        textBoxnQtyC = self.textBoxnQtyC

        # comboBoxnGTEFlag
        tk.Label(self, text = "出場成交價大於指定價後觸發0:否；1:是").grid(row=2, column=1)
            #輸入框
        self.comboBoxnGTEFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnGTEFlag['values'] = Config.comboBoxnGTEFlag
        self.comboBoxnGTEFlag.grid(row=2, column=2)

        global comboBoxnGTEFlag
        comboBoxnGTEFlag = self.comboBoxnGTEFlag

        # textBoxbstrGTETriggerPrice
        tk.Label(self, text = "指定價").grid(row=2, column=3)
        #輸入框
        self.textBoxbstrGTETriggerPrice = tk.Entry(self, width= 6)
        self.textBoxbstrGTETriggerPrice.grid(row=2, column=4)

        global textBoxbstrGTETriggerPrice
        textBoxbstrGTETriggerPrice = self.textBoxbstrGTETriggerPrice

        # textBoxbstrGTEOrderPrice
        tk.Label(self, text = "委託價").grid(row=2, column=5)
        #輸入框
        self.textBoxbstrGTEOrderPrice = tk.Entry(self, width= 6)
        self.textBoxbstrGTEOrderPrice.grid(row=2, column=6)

        global textBoxbstrGTEOrderPrice
        textBoxbstrGTEOrderPrice = self.textBoxbstrGTEOrderPrice

        # comboBoxnGTEMarketPrice
        tk.Label(self, text = "(大於條件)以1:市價;2:限價 做為出場價格").grid(row=2, column=7)
            #輸入框
        self.comboBoxnGTEMarketPrice = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnGTEMarketPrice['values'] = Config.comboBoxnGTEMarketPrice
        self.comboBoxnGTEMarketPrice.grid(row=2, column=8)

        global comboBoxnGTEMarketPrice
        comboBoxnGTEMarketPrice = self.comboBoxnGTEMarketPrice

        # comboBoxnGTEOrderCond
        tk.Label(self, text = "大於條件出場時效0:ROD;3:IOC;4:FOK").grid(row=2, column=9)
            #輸入框
        self.comboBoxnGTEOrderCond = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnGTEOrderCond['values'] = Config.comboBoxnGTEOrderCond
        self.comboBoxnGTEOrderCond.grid(row=2, column=10)

        global comboBoxnGTEOrderCond
        comboBoxnGTEOrderCond = self.comboBoxnGTEOrderCond

        # comboBoxnLTEFlag
        tk.Label(self, text = "出場成交價小於指定價後觸發0:否；1:是").grid(row=3, column=1)
            #輸入框
        self.comboBoxnLTEFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLTEFlag['values'] = Config.comboBoxnLTEFlag
        self.comboBoxnLTEFlag.grid(row=3, column=2)

        global comboBoxnLTEFlag
        comboBoxnLTEFlag = self.comboBoxnLTEFlag

        # textBoxbstrLTETriggerPrice
        tk.Label(self, text = "指定價").grid(row=3, column=3)
        #輸入框
        self.textBoxbstrLTETriggerPrice = tk.Entry(self, width= 6)
        self.textBoxbstrLTETriggerPrice.grid(row=3, column=4)

        global textBoxbstrLTETriggerPrice
        textBoxbstrLTETriggerPrice = self.textBoxbstrLTETriggerPrice

        # textBoxbstrLTEOrderPrice
        tk.Label(self, text = "委託價").grid(row=3, column=5)
        #輸入框
        self.textBoxbstrLTEOrderPrice = tk.Entry(self, width= 6)
        self.textBoxbstrLTEOrderPrice.grid(row=3, column=6)

        global textBoxbstrLTEOrderPrice
        textBoxbstrLTEOrderPrice = self.textBoxbstrLTEOrderPrice

        # comboBoxnLTEMarketPrice
        tk.Label(self, text = "(小於條件)以1:市價;2:限價 做為出場價格").grid(row=3, column=7)
            #輸入框
        self.comboBoxnLTEMarketPrice = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLTEMarketPrice['values'] = Config.comboBoxnLTEMarketPrice
        self.comboBoxnLTEMarketPrice.grid(row=3, column=8)

        global comboBoxnLTEMarketPrice
        comboBoxnLTEMarketPrice = self.comboBoxnLTEMarketPrice

        # comboBoxnLTEOrderCond
        tk.Label(self, text = "小於條件出場時效0:ROD;3:IOC;4:FOK").grid(row=3, column=9)
            #輸入框
        self.comboBoxnLTEOrderCond = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLTEOrderCond['values'] = Config.comboBoxnLTEOrderCond
        self.comboBoxnLTEOrderCond.grid(row=3, column=10)

        global comboBoxnLTEOrderCond
        comboBoxnLTEOrderCond = self.comboBoxnLTEOrderCond

        # comboBoxnClearAllFlagC
        tk.Label(self, text = "執行時間出清0:否；1:是").grid(row=4, column=1)
            #輸入框
        self.comboBoxnClearAllFlagC = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnClearAllFlagC['values'] = Config.comboBoxnClearAllFlagC
        self.comboBoxnClearAllFlagC.grid(row=4, column=2)

        global comboBoxnClearAllFlagC
        comboBoxnClearAllFlagC = self.comboBoxnClearAllFlagC

        # textBoxbstrClearCancelTimeC
        tk.Label(self, text = "出清時間-時＋分（hhmm）{每日13:20截止)").grid(row=4, column=3)
        #輸入框
        self.textBoxbstrClearCancelTimeC = tk.Entry(self, width= 6)
        self.textBoxbstrClearCancelTimeC.grid(row=4, column=4)

        global textBoxbstrClearCancelTimeC
        textBoxbstrClearCancelTimeC = self.textBoxbstrClearCancelTimeC

        # textBoxbstrClearAllOrderPriceC
        tk.Label(self, text = "出清委託價").grid(row=4, column=5)
        #輸入框
        self.textBoxbstrClearAllOrderPriceC = tk.Entry(self, width= 6)
        self.textBoxbstrClearAllOrderPriceC.grid(row=4, column=6)

        global textBoxbstrClearAllOrderPriceC
        textBoxbstrClearAllOrderPriceC = self.textBoxbstrClearAllOrderPriceC

        # comboBoxnClearAllPriceTypeC
        tk.Label(self, text = "出清委託價方式= 1:市價;2:限價").grid(row=4, column=7)
            #輸入框
        self.comboBoxnClearAllPriceTypeC = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnClearAllPriceTypeC['values'] = Config.comboBoxnClearAllPriceTypeC
        self.comboBoxnClearAllPriceTypeC.grid(row=4, column=8)

        global comboBoxnClearAllPriceTypeC
        comboBoxnClearAllPriceTypeC = self.comboBoxnClearAllPriceTypeC

        # comboBoxnClearOrderCondC
        tk.Label(self, text = "出清出場時效 0:ROD;3:IOC;4:FOK").grid(row=4, column=9)
            #輸入框
        self.comboBoxnClearOrderCondC = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnClearOrderCondC['values'] = Config.comboBoxnClearOrderCondC
        self.comboBoxnClearOrderCondC.grid(row=4, column=10)

        global comboBoxnClearOrderCondC
        comboBoxnClearOrderCondC = self.comboBoxnClearOrderCondC

        # comboBoxnFinalClearFlagC
        tk.Label(self, text = "盤後定盤交易 0:否；1:是").grid(row=5, column=1)
            #輸入框
        self.comboBoxnFinalClearFlagC = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnFinalClearFlagC['values'] = Config.comboBoxnFinalClearFlagC
        self.comboBoxnFinalClearFlagC.grid(row=5, column=2)

        global comboBoxnFinalClearFlagC
        comboBoxnFinalClearFlagC = self.comboBoxnFinalClearFlagC

        # buttonSendStockStrategyClear
        self.buttonSendStockStrategyClear = tk.Button(self)
        self.buttonSendStockStrategyClear["text"] = "出清送出"
        self.buttonSendStockStrategyClear["command"] = self.buttonSendStockStrategyClear_Click
        self.buttonSendStockStrategyClear.grid(row=6, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False

    def buttonSendStockStrategyClear_Click(self):
        
        pOrder = sk.STOCKSTRATEGYORDEROUT()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoC.get()
        pOrder.bstrClearCancelTime = textBoxbstrClearCancelTimeC.get()
        pOrder.bstrClearAllOrderPrice = textBoxbstrClearAllOrderPriceC.get()

        pOrder.bstrLTETriggerPrice = textBoxbstrLTETriggerPrice.get()
        pOrder.bstrLTEOrderPrice = textBoxbstrLTEOrderPrice.get()
        pOrder.bstrGTETriggerPrice = textBoxbstrGTETriggerPrice.get()
        pOrder.bstrGTEOrderPrice = textBoxbstrGTEOrderPrice.get()

        pOrder.nQty = int(textBoxnQtyC.get())

        if (comboBoxnBuySellC.get() == "0:買"):
            pOrder.nBuySell = 0
        elif (comboBoxnBuySellC.get() == "1:賣"):
            pOrder.nBuySell = 1

        if (comboBoxnClearAllFlagC.get() == "0:否"):
            pOrder.nClearAllFlag = 0
        elif (comboBoxnClearAllFlagC.get() == "1:是"):
            pOrder.nClearAllFlag = 1

        if (comboBoxnClearAllPriceTypeC.get() == "1:市價"):
            pOrder.nClearAllPriceType = 1
        elif (comboBoxnClearAllPriceTypeC.get() == "2:限價"):
            pOrder.nClearAllPriceType = 2

        if (comboBoxnFinalClearFlagC.get() == "0:否"):
            pOrder.nFinalClearFlag = 0
        elif (comboBoxnFinalClearFlagC.get() == "1:是"):
            pOrder.nFinalClearFlag = 1

        if (comboBoxnOrderTypeC.get() == "0:現股"):
            pOrder.nOrderType = 0
        elif (comboBoxnOrderTypeC.get() == "3:融資"):
            pOrder.nOrderType = 3
        elif (comboBoxnOrderTypeC.get() == "4:融券"):
            pOrder.nOrderType = 4

        if (comboBoxnLTEFlag.get() == "0:否"):
            pOrder.nLTEFlag = 0
        elif (comboBoxnLTEFlag.get() == "1:是"):
            pOrder.nLTEFlag = 1

        if (comboBoxnLTEMarketPrice.get() == "1:市價"):
            pOrder.nLTEMarketPrice = 1
        elif (comboBoxnLTEMarketPrice.get() == "2:限價"):
            pOrder.nLTEMarketPrice = 2

        if (comboBoxnGTEFlag.get() == "0:否"):
            pOrder.nGTEFlag = 0
        elif (comboBoxnGTEFlag.get() == "1:是"):
            pOrder.nGTEFlag = 1

        if (comboBoxnGTEMarketPrice.get() == "1:市價"):
            pOrder.nGTEMarketPrice = 1
        elif (comboBoxnGTEMarketPrice.get() == "2:限價"):
            pOrder.nGTEMarketPrice = 2

        if (comboBoxnGTEOrderCond.get() == "0:ROD"):
            pOrder.nGTEOrderCond = 0
        elif (comboBoxnGTEOrderCond.get() == "3:IOC"):
            pOrder.nGTEOrderCond = 3
        elif (comboBoxnGTEOrderCond.get() == "4:FOK"):
            pOrder.nGTEOrderCond = 4

        if (comboBoxnLTEOrderCond.get() == "0:ROD"):
            pOrder.nLTEOrderCond = 0
        elif (comboBoxnLTEOrderCond.get() == "3:IOC"):
            pOrder.nLTEOrderCond = 3
        elif (comboBoxnLTEOrderCond.get() == "4:FOK"):
            pOrder.nLTEOrderCond = 4

        if (comboBoxnClearOrderCondC.get() == "0:ROD"):
            pOrder.nClearOrderCond = 0
        elif (comboBoxnClearOrderCondC.get() == "3:IOC"):
            pOrder.nClearOrderCond = 3
        elif (comboBoxnClearOrderCondC.get() == "4:FOK"):
            pOrder.nClearOrderCond = 4

        # 送出證券智慧單出清條件委託。
        bstrMessage,nCode= m_pSKOrder.SendStockStrategyClear(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockStrategyClear】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 

######################################################################################################################################
#MITForm
class MITForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrStockNoMIT
        tk.Label(self, text = "委託股票代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoMIT = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoMIT.grid(row=0, column=2)

        global textBoxbstrStockNoMIT
        textBoxbstrStockNoMIT = self.textBoxbstrStockNoMIT

        # textBoxbstrDealPriceMIT
        tk.Label(self, text = "成交價(當下市價)，洗價機留存用").grid(row=0, column=3)
        #輸入框
        self.textBoxbstrDealPriceMIT = tk.Entry(self, width= 6)
        self.textBoxbstrDealPriceMIT.grid(row=0, column=4)

        global textBoxbstrDealPriceMIT
        textBoxbstrDealPriceMIT = self.textBoxbstrDealPriceMIT

        # comboBoxnOrderTypeMIT
        tk.Label(self, text = "委託交易別(0:現股, 3:融資, 4:融券, 8:無券普賣)").grid(row=1, column=1)
            #輸入框
        self.comboBoxnOrderTypeMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderTypeMIT['values'] = Config.comboBoxnOrderTypeMIT
        self.comboBoxnOrderTypeMIT.grid(row=1, column=2)

        global comboBoxnOrderTypeMIT
        comboBoxnOrderTypeMIT = self.comboBoxnOrderTypeMIT

        # comboBoxnOrderCondMIT
        tk.Label(self, text = "0:ROD;3:IOC;4:FOK:").grid(row=1, column=3)
            #輸入框
        self.comboBoxnOrderCondMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderCondMIT['values'] = Config.comboBoxnOrderCondMIT
        self.comboBoxnOrderCondMIT.grid(row=1, column=4)

        global comboBoxnOrderCondMIT
        comboBoxnOrderCondMIT = self.comboBoxnOrderCondMIT

        # comboBoxnBuySellMIT
        tk.Label(self, text = "0買;1賣").grid(row=1, column=5)
            #輸入框
        self.comboBoxnBuySellMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySellMIT['values'] = Config.comboBoxnBuySellMIT
        self.comboBoxnBuySellMIT.grid(row=1, column=6)

        global comboBoxnBuySellMIT
        comboBoxnBuySellMIT = self.comboBoxnBuySellMIT

        # comboBoxnTriggerDirMIT
        tk.Label(self, text = "觸價方向(1:GTE大於等於,2:LTE小於等於)").grid(row=2, column=1)
            #輸入框
        self.comboBoxnTriggerDirMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTriggerDirMIT['values'] = Config.comboBoxnTriggerDirMIT
        self.comboBoxnTriggerDirMIT.grid(row=2, column=2)

        global comboBoxnTriggerDirMIT
        comboBoxnTriggerDirMIT = self.comboBoxnTriggerDirMIT

        # textBoxbstrTriggerPriceMIT
        tk.Label(self, text = "觸發價").grid(row=2, column=3)
        #輸入框
        self.textBoxbstrTriggerPriceMIT = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerPriceMIT.grid(row=2, column=4)

        global textBoxbstrTriggerPriceMIT
        textBoxbstrTriggerPriceMIT = self.textBoxbstrTriggerPriceMIT

        # textBoxnQtyMIT
        tk.Label(self, text = "委託張數").grid(row=2, column=5)
        #輸入框
        self.textBoxnQtyMIT = tk.Entry(self, width= 6)
        self.textBoxnQtyMIT.grid(row=2, column=6)

        global textBoxnQtyMIT
        textBoxnQtyMIT = self.textBoxnQtyMIT

        # comboBoxnOrderPriceTypeMIT
        tk.Label(self, text = "委託價類別(1:市價; 2:限價)").grid(row=2, column=7)
            #輸入框
        self.comboBoxnOrderPriceTypeMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeMIT['values'] = Config.comboBoxnOrderPriceTypeMIT
        self.comboBoxnOrderPriceTypeMIT.grid(row=2, column=8)

        global comboBoxnOrderPriceTypeMIT
        comboBoxnOrderPriceTypeMIT = self.comboBoxnOrderPriceTypeMIT

        # textBoxbstrOrderPriceMIT
        tk.Label(self, text = "委託價(若為市價單, 委託價請填0)").grid(row=2, column=9)
        #輸入框
        self.textBoxbstrOrderPriceMIT = tk.Entry(self, width= 6)
        self.textBoxbstrOrderPriceMIT.grid(row=2, column=10)

        global textBoxbstrOrderPriceMIT
        textBoxbstrOrderPriceMIT = self.textBoxbstrOrderPriceMIT

        # comboBoxnLongActionFlagMIT
        tk.Label(self, text = "是否為長效單(0:否, 1:是):").grid(row=3, column=1)
            #輸入框
        self.comboBoxnLongActionFlagMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLongActionFlagMIT['values'] = Config.comboBoxnLongActionFlagMIT
        self.comboBoxnLongActionFlagMIT.grid(row=3, column=2)

        global comboBoxnLongActionFlagMIT
        comboBoxnLongActionFlagMIT = self.comboBoxnLongActionFlagMIT

        # textBoxbstrLongEndDateMIT
        tk.Label(self, text = "長效單結束日期(YYYYMMDD共8碼, EX:20220630)").grid(row=3, column=3)
        #輸入框
        self.textBoxbstrLongEndDateMIT = tk.Entry(self, width= 6)
        self.textBoxbstrLongEndDateMIT.grid(row=3, column=4)

        global textBoxbstrLongEndDateMIT
        textBoxbstrLongEndDateMIT = self.textBoxbstrLongEndDateMIT
        
        # comboBoxnLATypeMIT
        tk.Label(self, text = "觸發結束條件(1:效期內觸發即失效, 3:效期內完全成交即失效):").grid(row=3, column=5)
            #輸入框
        self.comboBoxnLATypeMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLATypeMIT['values'] = Config.comboBoxnLATypeMIT
        self.comboBoxnLATypeMIT.grid(row=3, column=6)

        global comboBoxnLATypeMIT
        comboBoxnLATypeMIT = self.comboBoxnLATypeMIT

        # comboBoxnPreRiskFlag
        tk.Label(self, text = "預風控功能 0:關閉預風控 ;1:開啟預風控(不支援信用交易)").grid(row=4, column=1)
            #輸入框
        self.comboBoxnPreRiskFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnPreRiskFlag['values'] = Config.comboBoxnPreRiskFlag
        self.comboBoxnPreRiskFlag.grid(row=4, column=2)

        global comboBoxnPreRiskFlag
        comboBoxnPreRiskFlag = self.comboBoxnPreRiskFlag

        # buttonSendStockStrategyMIT
        self.buttonSendStockStrategyMIT = tk.Button(self)
        self.buttonSendStockStrategyMIT["text"] = "MIT送出"
        self.buttonSendStockStrategyMIT["command"] = self.buttonSendStockStrategyMIT_Click
        self.buttonSendStockStrategyMIT.grid(row=5, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendStockStrategyMIT_Click(self):
        
        pOrder = sk.STOCKSTRATEGYORDERMIT()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoMIT.get()
        pOrder.bstrOrderPrice = textBoxbstrOrderPriceMIT.get()
        pOrder.bstrTriggerPrice = textBoxbstrTriggerPriceMIT.get()
        pOrder.bstrDealPrice = textBoxbstrDealPriceMIT.get()
        pOrder.bstrLongEndDate = textBoxbstrLongEndDateMIT.get()
        pOrder.nQty = int(textBoxnQtyMIT.get())

        if (comboBoxnOrderTypeMIT.get() == "0:現股"):
            pOrder.nOrderType = 0
        elif (comboBoxnOrderTypeMIT.get() == "3:融資"):
            pOrder.nOrderType = 3
        elif (comboBoxnOrderTypeMIT.get() == "4:融券"):
            pOrder.nOrderType = 4
        elif (comboBoxnOrderTypeMIT.get() == "8:無券普賣"):
            pOrder.nOrderType = 8

        if (comboBoxnBuySellMIT.get() == "0:買"):
            pOrder.nBuySell = 0
        elif (comboBoxnBuySellMIT.get() == "1:賣"):
            pOrder.nBuySell = 1

        if (comboBoxnOrderPriceTypeMIT.get() == "1:市價"):
            pOrder.nOrderPriceType = 1
        elif (comboBoxnOrderPriceTypeMIT.get() == "2:限價"):
            pOrder.nOrderPriceType = 2

        if (comboBoxnOrderCondMIT.get() == "0:ROD"):
            pOrder.nOrderCond = 0
        elif (comboBoxnOrderCondMIT.get() == "3:IOC"):
            pOrder.nOrderCond = 3
        elif (comboBoxnOrderCondMIT.get() == "4:FOK"):
            pOrder.nOrderCond = 4

        if (comboBoxnTriggerDirMIT.get() == "1:GTE大於等於"):
            pOrder.nTriggerDir = 1
        elif (comboBoxnTriggerDirMIT.get() == "2:LTE小於等於"):
            pOrder.nTriggerDir = 2

        if (comboBoxnPreRiskFlag.get() == "0:關閉預風控"):
            pOrder.nPreRiskFlag = 0
        elif (comboBoxnPreRiskFlag.get() == "1:開啟預風控"):
            pOrder.nPreRiskFlag = 1

        if (comboBoxnLongActionFlagMIT.get() == "0:否"):
            pOrder.nLongActionFlag = 0
        elif (comboBoxnLongActionFlagMIT.get() == "1:是"):
            pOrder.nLongActionFlag = 1

        if (comboBoxnLATypeMIT.get() == "1:效期內觸發即失效"):
            pOrder.nLAType = 1
        elif (comboBoxnLATypeMIT.get() == "3:效期內完全成交即失效"):
            pOrder.nLAType = 3

        # 送出證券智慧單MIT條件委託。
        bstrMessage,nCode= m_pSKOrder.SendStockStrategyMIT(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockStrategyMIT】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 
######################################################################################################################################
#OCOForm
class OCOForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrStockNoOCO
        tk.Label(self, text = "委託股票代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoOCO = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoOCO.grid(row=0, column=2)

        global textBoxbstrStockNoOCO
        textBoxbstrStockNoOCO = self.textBoxbstrStockNoOCO

        # textBoxbstrTriggerUp
        tk.Label(self, text = "第一腳 觸發價").grid(row=1, column=1)
        #輸入框
        self.textBoxbstrTriggerUp = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerUp.grid(row=1, column=2)

        global textBoxbstrTriggerUp
        textBoxbstrTriggerUp = self.textBoxbstrTriggerUp

        # comboBoxnBuySellUp
        tk.Label(self, text = "第一腳 0:買;1:賣").grid(row=1, column=3)
            #輸入框
        self.comboBoxnBuySellUp = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySellUp['values'] = Config.comboBoxnBuySellUp
        self.comboBoxnBuySellUp.grid(row=1, column=4)

        global comboBoxnBuySellUp
        comboBoxnBuySellUp = self.comboBoxnBuySellUp

        # comboBoxnOrderCondUp
        tk.Label(self, text = "第一腳 委託時效(0:ROD,3:IOC,4:FOK)").grid(row=1, column=5)
            #輸入框
        self.comboBoxnOrderCondUp = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderCondUp['values'] = Config.comboBoxnOrderCondUp
        self.comboBoxnOrderCondUp.grid(row=1, column=6)

        global comboBoxnOrderCondUp
        comboBoxnOrderCondUp = self.comboBoxnOrderCondUp

        # comboBoxnOrderTypeUp
        tk.Label(self, text = "第一腳 委託交易別").grid(row=1, column=7)
            #輸入框
        self.comboBoxnOrderTypeUp = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderTypeUp['values'] = Config.comboBoxnOrderTypeUp
        self.comboBoxnOrderTypeUp.grid(row=1, column=8)

        global comboBoxnOrderTypeUp
        comboBoxnOrderTypeUp = self.comboBoxnOrderTypeUp

        # textBoxbstrOrderPriceOCO
        tk.Label(self, text = "第一腳 委託價").grid(row=1, column=9)
        #輸入框
        self.textBoxbstrOrderPriceOCO = tk.Entry(self, width= 6)
        self.textBoxbstrOrderPriceOCO.grid(row=1, column=10)

        global textBoxbstrOrderPriceOCO
        textBoxbstrOrderPriceOCO = self.textBoxbstrOrderPriceOCO

        # comboBoxnOrderPriceTypeUp
        tk.Label(self, text = "第一腳 委託價類別(1:市價; 2:限價)").grid(row=1, column=11)
            #輸入框
        self.comboBoxnOrderPriceTypeUp = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeUp['values'] = Config.comboBoxnOrderPriceTypeUp
        self.comboBoxnOrderPriceTypeUp.grid(row=1, column=12)

        global comboBoxnOrderPriceTypeUp
        comboBoxnOrderPriceTypeUp = self.comboBoxnOrderPriceTypeUp

        # textBoxbstrTriggerDown
        tk.Label(self, text = "第二腳 觸發價").grid(row=2, column=1)
        #輸入框
        self.textBoxbstrTriggerDown = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerDown.grid(row=2, column=2)

        global textBoxbstrTriggerDown
        textBoxbstrTriggerDown = self.textBoxbstrTriggerDown

        # comboBoxnBuySellDown
        tk.Label(self, text = "第二腳 0:買;1:賣").grid(row=2, column=3)
            #輸入框
        self.comboBoxnBuySellDown = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySellDown['values'] = Config.comboBoxnBuySellDown
        self.comboBoxnBuySellDown.grid(row=2, column=4)

        global comboBoxnBuySellDown
        comboBoxnBuySellDown = self.comboBoxnBuySellDown

        # comboBoxnOrderCondDown
        tk.Label(self, text = "第二腳 委託時效(0:ROD,3:IOC,4:FOK)").grid(row=2, column=5)
            #輸入框
        self.comboBoxnOrderCondDown = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderCondDown['values'] = Config.comboBoxnOrderCondDown
        self.comboBoxnOrderCondDown.grid(row=2, column=6)

        global comboBoxnOrderCondDown
        comboBoxnOrderCondDown = self.comboBoxnOrderCondDown

        # comboBoxnOrderTypeDown
        tk.Label(self, text = "第二腳 委託交易別").grid(row=2, column=7)
            #輸入框
        self.comboBoxnOrderTypeDown = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderTypeDown['values'] = Config.comboBoxnOrderTypeDown
        self.comboBoxnOrderTypeDown.grid(row=2, column=8)

        global comboBoxnOrderTypeDown
        comboBoxnOrderTypeDown = self.comboBoxnOrderTypeDown

        # textBoxbstrOrderPrice2
        tk.Label(self, text = "第二腳 委託價").grid(row=2, column=9)
        #輸入框
        self.textBoxbstrOrderPrice2 = tk.Entry(self, width= 6)
        self.textBoxbstrOrderPrice2.grid(row=2, column=10)

        global textBoxbstrOrderPrice2
        textBoxbstrOrderPrice2 = self.textBoxbstrOrderPrice2

        # comboBoxnOrderPriceTypeDown
        tk.Label(self, text = "第二腳 委託價類別(1:市價; 2:限價)").grid(row=2, column=11)
            #輸入框
        self.comboBoxnOrderPriceTypeDown = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeDown['values'] = Config.comboBoxnOrderPriceTypeDown
        self.comboBoxnOrderPriceTypeDown.grid(row=2, column=12)

        global comboBoxnOrderPriceTypeDown
        comboBoxnOrderPriceTypeDown = self.comboBoxnOrderPriceTypeDown

        # textBoxnQtyOCO
        tk.Label(self, text = "委託張數").grid(row=3, column=1)
        #輸入框
        self.textBoxnQtyOCO = tk.Entry(self, width= 6)
        self.textBoxnQtyOCO.grid(row=3, column=2)

        global textBoxnQtyOCO
        textBoxnQtyOCO = self.textBoxnQtyOCO

        # buttonSendStockStrategyOCO
        self.buttonSendStockStrategyOCO = tk.Button(self)
        self.buttonSendStockStrategyOCO["text"] = "OCO送出"
        self.buttonSendStockStrategyOCO["command"] = self.buttonSendStockStrategyOCO_Click
        self.buttonSendStockStrategyOCO.grid(row=4, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendStockStrategyOCO_Click(self):
        
        pOrder = sk.STOCKSTRATEGYORDEROCO()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoOCO.get()
        pOrder.nQty = int(textBoxnQtyOCO.get())
        pOrder.bstrOrderPrice = textBoxbstrOrderPriceOCO.get()

        pOrder.bstrTriggerUp = textBoxbstrTriggerUp.get()
        pOrder.bstrOrderPrice2 = textBoxbstrOrderPrice2.get()
        pOrder.bstrTriggerDown = textBoxbstrTriggerDown.get()

        if (comboBoxnBuySellUp.get() == "0:買"):
            pOrder.nBuySellUp = 0
        elif (comboBoxnBuySellUp.get() == "1:賣"):
            pOrder.nBuySellUp = 1

        if (comboBoxnBuySellDown.get() == "0:買"):
            pOrder.nBuySellDown = 0
        elif (comboBoxnBuySellDown.get() == "1:賣"):
            pOrder.nBuySellDown = 1

        if (comboBoxnOrderCondUp.get() == "0:ROD"):
            pOrder.nOrderCondUp = 0
        elif (comboBoxnOrderCondUp.get() == "3:IOC"):
            pOrder.nOrderCondUp = 3
        elif (comboBoxnOrderCondUp.get() == "4:FOK"):
            pOrder.nOrderCondUp = 4

        if (comboBoxnOrderCondDown.get() == "0:ROD"):
            pOrder.nOrderCondDown = 0
        elif (comboBoxnOrderCondDown.get() == "3:IOC"):
            pOrder.nOrderCondDown = 3
        elif (comboBoxnOrderCondDown.get() == "4:FOK"):
            pOrder.nOrderCondDown = 4

        if (comboBoxnOrderTypeUp.get() == "0:現股"):
            pOrder.nOrderTypeUp = 0
        elif (comboBoxnOrderTypeUp.get() == "3:融資"):
            pOrder.nOrderTypeUp = 3
        elif (comboBoxnOrderTypeUp.get() == "4:融券"):
            pOrder.nOrderTypeUp = 4
        elif (comboBoxnOrderTypeUp.get() == "8:無券普賣"):
            pOrder.nOrderTypeUp = 8

        if (comboBoxnOrderTypeDown.get() == "0:現股"):
            pOrder.nOrderTypeDown = 0
        elif (comboBoxnOrderTypeDown.get() == "3:融資"):
            pOrder.nOrderTypeDown = 3
        elif (comboBoxnOrderTypeDown.get() == "4:融券"):
            pOrder.nOrderTypeDown = 4
        elif (comboBoxnOrderTypeDown.get() == "8:無券普賣"):
            pOrder.nOrderTypeDown = 8

        if (comboBoxnOrderPriceTypeUp.get() == "1:市價"):
            pOrder.nOrderPriceTypeUp = 1
        elif (comboBoxnOrderPriceTypeUp.get() == "2:限價"):
            pOrder.nOrderPriceTypeUp = 2

        if (comboBoxnOrderPriceTypeDown.get() == "1:市價"):
            pOrder.nOrderPriceTypeDown = 1
        elif (comboBoxnOrderPriceTypeDown.get() == "2:限價"):
            pOrder.nOrderPriceTypeDown = 2


        # 送出證券智慧單二擇一OCO條件委託。
        bstrMessage,nCode= m_pSKOrder.SendStockStrategyOCO(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockStrategyOCO】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 
######################################################################################################################################
#MIOCForm
class MIOCForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrStockNoMIOC
        tk.Label(self, text = "委託股票代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoMIOC = tk.Entry(self)
        self.textBoxbstrStockNoMIOC.grid(row=0, column=2)

        global textBoxbstrStockNoMIOC
        textBoxbstrStockNoMIOC = self.textBoxbstrStockNoMIOC

        # comboBoxnPrimeMIOC
        tk.Label(self, text = "0:上市; 1:上櫃").grid(row=0, column=3)
            #輸入框
        self.comboBoxnPrimeMIOC = ttk.Combobox(self, state='readonly')
        self.comboBoxnPrimeMIOC['values'] = Config.comboBoxnPrimeMIOC
        self.comboBoxnPrimeMIOC.grid(row=0, column=4)

        global comboBoxnPrimeMIOC
        comboBoxnPrimeMIOC = self.comboBoxnPrimeMIOC

        # comboBoxnOrderTypeMIOC
        tk.Label(self, text = "委託交易別(0:現股, 3:融資, 4:融券, 8:無券普賣)").grid(row=1, column=1)
            #輸入框
        self.comboBoxnOrderTypeMIOC = ttk.Combobox(self, state='readonly')
        self.comboBoxnOrderTypeMIOC['values'] = Config.comboBoxnOrderTypeMIOC
        self.comboBoxnOrderTypeMIOC.grid(row=1, column=2)

        global comboBoxnOrderTypeMIOC
        comboBoxnOrderTypeMIOC = self.comboBoxnOrderTypeMIOC

        # comboBoxnBuySellMIOC1
        tk.Label(self, text = "1:買 2:賣").grid(row=1, column=3)
            #輸入框
        self.comboBoxnBuySellMIOC1 = ttk.Combobox(self, state='readonly')
        self.comboBoxnBuySellMIOC1['values'] = Config.comboBoxnBuySellMIOC1
        self.comboBoxnBuySellMIOC1.grid(row=1, column=4)

        global comboBoxnBuySellMIOC1
        comboBoxnBuySellMIOC1 = self.comboBoxnBuySellMIOC1

        # comboBoxnOrderPriceTypeMIOC
        tk.Label(self, text = "0:市價; 1:(買單)委賣價或(賣單)委買價; 委買、賣價實際價格由中台決定").grid(row=2, column=1)
            #輸入框
        self.comboBoxnOrderPriceTypeMIOC = ttk.Combobox(self, state='readonly')
        self.comboBoxnOrderPriceTypeMIOC['values'] = Config.comboBoxnOrderPriceTypeMIOC
        self.comboBoxnOrderPriceTypeMIOC.grid(row=2, column=2)

        global comboBoxnOrderPriceTypeMIOC
        comboBoxnOrderPriceTypeMIOC = self.comboBoxnOrderPriceTypeMIOC

        # textBoxnOneceQtyLimit
        tk.Label(self, text = "單次交易張數上限").grid(row=2, column=3)
        #輸入框
        self.textBoxnOneceQtyLimit = tk.Entry(self)
        self.textBoxnOneceQtyLimit.grid(row=2, column=4)

        global textBoxnOneceQtyLimit
        textBoxnOneceQtyLimit = self.textBoxnOneceQtyLimit

        # textBoxbstrOrderPriceUp
        tk.Label(self, text = "委託價上限").grid(row=3, column=1)
        #輸入框
        self.textBoxbstrOrderPriceUp = tk.Entry(self)
        self.textBoxbstrOrderPriceUp.grid(row=3, column=2)

        global textBoxbstrOrderPriceUp
        textBoxbstrOrderPriceUp = self.textBoxbstrOrderPriceUp

        # textBoxbstrOrderPriceDown
        tk.Label(self, text = "委託價下限").grid(row=3, column=3)
        #輸入框
        self.textBoxbstrOrderPriceDown = tk.Entry(self)
        self.textBoxbstrOrderPriceDown.grid(row=3, column=4)

        global textBoxbstrOrderPriceDown
        textBoxbstrOrderPriceDown = self.textBoxbstrOrderPriceDown

        # textBoxnTotalQty
        tk.Label(self, text = "總委張數").grid(row=3, column=5)
        #輸入框
        self.textBoxnTotalQty = tk.Entry(self)
        self.textBoxnTotalQty.grid(row=3, column=6)

        global textBoxnTotalQty
        textBoxnTotalQty = self.textBoxnTotalQty

        # buttonSendStockStrategyMIOC
        self.buttonSendStockStrategyMIOC = tk.Button(self)
        self.buttonSendStockStrategyMIOC["text"] = "MIOC送出"
        self.buttonSendStockStrategyMIOC["command"] = self.buttonSendStockStrategyMIOC_Click
        self.buttonSendStockStrategyMIOC.grid(row=4, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendStockStrategyMIOC_Click(self):
        
        pOrder = sk.STOCKSTRATEGYORDERMIOC()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoMIOC.get()
        pOrder.bstrOrderPriceUp = textBoxbstrOrderPriceUp.get()
        pOrder.bstrOrderPriceDown = textBoxbstrOrderPriceDown.get()
        pOrder.nOneceQtyLimit = int(textBoxnOneceQtyLimit.get())
        pOrder.nTotalQty = int(textBoxnTotalQty.get())

        if (comboBoxnPrimeMIOC.get() == "0:上市"):
            pOrder.nPrime = 0
        elif (comboBoxnPrimeMIOC.get() == "1:上櫃"):
            pOrder.nPrime = 1

        if (comboBoxnBuySellMIOC1.get() == "1:買"):
            pOrder.nBuySell = 1
        elif (comboBoxnBuySellMIOC1.get() == "2:賣"):
            pOrder.nBuySell = 2

        if (comboBoxnOrderTypeMIOC.get() == "0:現股"):
            pOrder.nOrderType = 0
        elif (comboBoxnOrderTypeMIOC.get() == "3:融資"):
            pOrder.nOrderType = 3
        elif (comboBoxnOrderTypeMIOC.get() == "4:融券"):
            pOrder.nOrderType = 4
        elif (comboBoxnOrderTypeMIOC.get() == "8:無券普賣"):
            pOrder.nOrderType = 8

        if (comboBoxnOrderPriceTypeMIOC.get() == "0:市價"):
            pOrder.nOrderPriceType = 1
        elif (comboBoxnOrderPriceTypeMIOC.get() == "1:(買單)委賣價或(賣單)委買價"):
            pOrder.nOrderPriceType = 2

        # 送出證券智慧單多次IOC條件委託。
        bstrMessage,nCode= m_pSKOrder.SendStockStrategyMIOC(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockStrategyMIOC】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 
######################################################################################################################################
#MSTForm
class MSTForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrStockNoMST
        tk.Label(self, text = "委託股票代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoMST = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoMST.grid(row=0, column=2)

        global textBoxbstrStockNoMST
        textBoxbstrStockNoMST = self.textBoxbstrStockNoMST

        # comboBoxnPrimeMST
        tk.Label(self, text = "0:上市; 1:上櫃").grid(row=0, column=3)
            #輸入框
        self.comboBoxnPrimeMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnPrimeMST['values'] = Config.comboBoxnPrimeMST
        self.comboBoxnPrimeMST.grid(row=0, column=4)

        global comboBoxnPrimeMST
        comboBoxnPrimeMST = self.comboBoxnPrimeMST

        # comboBoxnOrderTypeMST
        tk.Label(self, text = "委託交易別(0:現股, 3:融資, 4:融券, 8:無券普賣)").grid(row=1, column=1)
            #輸入框
        self.comboBoxnOrderTypeMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderTypeMST['values'] = Config.comboBoxnOrderTypeMST
        self.comboBoxnOrderTypeMST.grid(row=1, column=2)

        global comboBoxnOrderTypeMST
        comboBoxnOrderTypeMST = self.comboBoxnOrderTypeMST

        # comboBoxnOrderCondMST
        tk.Label(self, text = "委託時效(0:ROD,3:IOC,4:FOK)").grid(row=1, column=3)
            #輸入框
        self.comboBoxnOrderCondMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderCondMST['values'] = Config.comboBoxnOrderCondMST
        self.comboBoxnOrderCondMST.grid(row=1, column=4)

        global comboBoxnOrderCondMST
        comboBoxnOrderCondMST = self.comboBoxnOrderCondMST

        # comboBoxnBuySellMST
        tk.Label(self, text = "0:買; 1:賣").grid(row=1, column=5)
            #輸入框
        self.comboBoxnBuySellMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySellMST['values'] = Config.comboBoxnBuySellMST
        self.comboBoxnBuySellMST.grid(row=1, column=6)

        global comboBoxnBuySellMST
        comboBoxnBuySellMST = self.comboBoxnBuySellMST

        # comboBoxnTriggerMethod
        tk.Label(self, text = "啟動條件(0：以市價立即啟動, 1：以自訂價格啟動)").grid(row=2, column=1)
            #輸入框
        self.comboBoxnTriggerMethod = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTriggerMethod['values'] = Config.comboBoxnTriggerMethod
        self.comboBoxnTriggerMethod.grid(row=2, column=2)

        global comboBoxnTriggerMethod
        comboBoxnTriggerMethod = self.comboBoxnTriggerMethod

        # comboBoxnTriggerDirMST
        tk.Label(self, text = "觸價方向(1:GTE大於等於,2:LTE小於等於)").grid(row=2, column=3)
            #輸入框
        self.comboBoxnTriggerDirMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTriggerDirMST['values'] = Config.comboBoxnTriggerDirMST
        self.comboBoxnTriggerDirMST.grid(row=2, column=4)

        global comboBoxnTriggerDirMST
        comboBoxnTriggerDirMST = self.comboBoxnTriggerDirMST

        # textBoxbstrStartPriceMST
        tk.Label(self, text = "[自訂價格啟動適用]觸發價").grid(row=2, column=5)
        #輸入框
        self.textBoxbstrStartPriceMST = tk.Entry(self, width= 6)
        self.textBoxbstrStartPriceMST.grid(row=2, column=6)

        global textBoxbstrStartPriceMST
        textBoxbstrStartPriceMST = self.textBoxbstrStartPriceMST

        # textBoxbstrDealPriceMST
        tk.Label(self, text = "[市價啟動適用]請填市價").grid(row=2, column=7)
        #輸入框
        self.textBoxbstrDealPriceMST = tk.Entry(self, width= 6)
        self.textBoxbstrDealPriceMST.grid(row=2, column=8)

        global textBoxbstrDealPriceMST
        textBoxbstrDealPriceMST = self.textBoxbstrDealPriceMST

        # textBoxbstrMovePoint
        tk.Label(self, text = "移動點數").grid(row=3, column=1)
        #輸入框
        self.textBoxbstrMovePoint = tk.Entry(self, width= 6)
        self.textBoxbstrMovePoint.grid(row=3, column=2)

        global textBoxbstrMovePoint
        textBoxbstrMovePoint = self.textBoxbstrMovePoint

        # textBoxnQtyMST
        tk.Label(self, text = "委託張數").grid(row=4, column=1)
        #輸入框
        self.textBoxnQtyMST = tk.Entry(self, width= 6)
        self.textBoxnQtyMST.grid(row=4, column=2)

        global textBoxnQtyMST
        textBoxnQtyMST = self.textBoxnQtyMST

        # comboBoxnOrderPriceTypeMST
        tk.Label(self, text = "委託價類別(1:市價; 2:限價)").grid(row=4, column=3)
            #輸入框
        self.comboBoxnOrderPriceTypeMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeMST['values'] = Config.comboBoxnOrderPriceTypeMST
        self.comboBoxnOrderPriceTypeMST.grid(row=4, column=4)

        global comboBoxnOrderPriceTypeMST
        comboBoxnOrderPriceTypeMST = self.comboBoxnOrderPriceTypeMST

        # textBoxbstrOrderPriceMST
        tk.Label(self, text = "委託價").grid(row=4, column=5)
        #輸入框
        self.textBoxbstrOrderPriceMST = tk.Entry(self, width= 6)
        self.textBoxbstrOrderPriceMST.grid(row=4, column=6)

        global textBoxbstrOrderPriceMST
        textBoxbstrOrderPriceMST = self.textBoxbstrOrderPriceMST

        # comboBoxnLongActionFlagMST
        tk.Label(self, text = "是否為長效單(0:否, 1:是):").grid(row=5, column=1)
            #輸入框
        self.comboBoxnLongActionFlagMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLongActionFlagMST['values'] = Config.comboBoxnLongActionFlagMST
        self.comboBoxnLongActionFlagMST.grid(row=5, column=2)

        global comboBoxnLongActionFlagMST
        comboBoxnLongActionFlagMST = self.comboBoxnLongActionFlagMST

        # textBoxbstrLongEndDateMST
        tk.Label(self, text = "長效單結束日期(YYYYMMDD共8碼, EX:20220630)").grid(row=5, column=3)
        #輸入框
        self.textBoxbstrLongEndDateMST = tk.Entry(self, width= 6)
        self.textBoxbstrLongEndDateMST.grid(row=5, column=4)

        global textBoxbstrLongEndDateMST
        textBoxbstrLongEndDateMST = self.textBoxbstrLongEndDateMST

        # comboBoxnLATypeMST
        tk.Label(self, text = "觸發結束條件(1:效期內觸發即失效, 3:效期內完全成交即失效):").grid(row=5, column=5)
            #輸入框
        self.comboBoxnLATypeMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLATypeMST['values'] = Config.comboBoxnLATypeMST
        self.comboBoxnLATypeMST.grid(row=5, column=6)

        global comboBoxnLATypeMST
        comboBoxnLATypeMST = self.comboBoxnLATypeMST


        # buttonSendStockStrategyMST
        self.buttonSendStockStrategyMST = tk.Button(self)
        self.buttonSendStockStrategyMST["text"] = "MST送出"
        self.buttonSendStockStrategyMST["command"] = self.buttonSendStockStrategyMST_Click
        self.buttonSendStockStrategyMST.grid(row=6, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendStockStrategyMST_Click(self):
        
        pOrder = sk.STOCKSTRATEGYORDERMIT()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoMST.get()
        pOrder.bstrOrderPrice = textBoxbstrOrderPriceMST.get()
        pOrder.bstrMovePoint = textBoxbstrMovePoint.get()
        pOrder.bstrDealPrice = textBoxbstrDealPriceMST.get()
        pOrder.bstrStartPrice = textBoxbstrStartPriceMST.get()
        pOrder.nQty = int(textBoxnQtyMST.get())
        pOrder.bstrLongEndDate = textBoxbstrLongEndDateMST.get()

        if (comboBoxnOrderTypeMST.get() == "0:現股"):
            pOrder.nOrderType = 0
        elif (comboBoxnOrderTypeMST.get() == "3融資"):
            pOrder.nOrderType = 3
        elif (comboBoxnOrderTypeMST.get() == "4:融券"):
            pOrder.nOrderType = 4
        elif (comboBoxnOrderTypeMST.get() == "8:無券普賣"):
            pOrder.nOrderType = 8

        if (comboBoxnBuySellMST.get() == "0:買"):
            pOrder.nBuySell = 0
        elif (comboBoxnBuySellMST.get() == "1:賣"):
            pOrder.nBuySell = 1

        if (comboBoxnOrderPriceTypeMST.get() == "1:市價"):
            pOrder.nOrderPriceType = 1
        elif (comboBoxnOrderPriceTypeMST.get() == "2:限價"):
            pOrder.nOrderPriceType = 2

        if (comboBoxnOrderCondMST.get() == "0:ROD"):
            pOrder.nOrderCond = 0
        elif (comboBoxnOrderCondMST.get() == "3:IOC"):
            pOrder.nOrderCond = 3
        elif (comboBoxnOrderCondMST.get() == "4:FOK"):
            pOrder.nOrderCond = 4

        if (comboBoxnTriggerDirMST.get() == "1:GTE大於等於"):
            pOrder.nTriggerDir = 1
        elif (comboBoxnTriggerDirMST.get() == "2:LTE小於等於"):
            pOrder.nTriggerDir = 2

        if (comboBoxnTriggerMethod.get() == "0:否,由市價啟動"):
            pOrder.nTriggerMethod = 0
        elif (comboBoxnTriggerMethod.get() == "1:是,由自訂價格啟動"):
            pOrder.nTriggerMethod = 1

        if (comboBoxnPrimeMST.get() == "0:上市"):
            pOrder.nPrime = 0
        elif (comboBoxnPrimeMST.get() == "1:上櫃"):
            pOrder.nPrime = 1

        if (comboBoxnLongActionFlagMST.get() == "0:否"):
            pOrder.nLongActionFlag = 0
        elif (comboBoxnLongActionFlagMST.get() == "1:是"):
            pOrder.nLongActionFlag = 1

        if (comboBoxnLATypeMST.get() == "0:非長效單"):
            pOrder.nLAType = 0
        elif (comboBoxnLATypeMST.get() == "1:效期內觸發即失效"):
            pOrder.nLAType = 1

        # 送出證券智慧單移動停損條件委託。
        bstrMessage,nCode= m_pSKOrder.SendStockStrategyMST(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockStrategyMST】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 
######################################################################################################################################
#ABForm
class ABForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrStockNo2
        tk.Label(self, text = "A商品 委託股票代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNo2 = tk.Entry(self, width= 6)
        self.textBoxbstrStockNo2.grid(row=0, column=2)

        global textBoxbstrStockNo2
        textBoxbstrStockNo2 = self.textBoxbstrStockNo2

        # comboBoxnMarketNo
        tk.Label(self, text = "A商品 市場編號(1:國內證, 2:國內期, 3:國外證, 4:國外期)").grid(row=0, column=3)
            #輸入框
        self.comboBoxnMarketNo = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnMarketNo['values'] = Config.comboBoxnMarketNo
        self.comboBoxnMarketNo.grid(row=0, column=4)

        global comboBoxnMarketNo
        comboBoxnMarketNo = self.comboBoxnMarketNo

        # textBoxbstrExchangeNo
        tk.Label(self, text = "A商品 交易所代碼(EX: TSE、TAIFEX、CME)").grid(row=0, column=5)
        #輸入框
        self.textBoxbstrExchangeNo = tk.Entry(self, width= 6)
        self.textBoxbstrExchangeNo.grid(row=0, column=6)

        global textBoxbstrExchangeNo
        textBoxbstrExchangeNo = self.textBoxbstrExchangeNo

        # textBoxbstrStartPriceAB
        tk.Label(self, text = "A商品 成交價").grid(row=0, column=7)
        #輸入框
        self.textBoxbstrStartPriceAB = tk.Entry(self, width= 6)
        self.textBoxbstrStartPriceAB.grid(row=0, column=8)

        global textBoxbstrStartPriceAB
        textBoxbstrStartPriceAB = self.textBoxbstrStartPriceAB

        # comboBoxnTriggerDirAB
        tk.Label(self, text = "A商品 觸價方向(1:GTE大於等於,2:LTE小於等於)").grid(row=1, column=1)
            #輸入框
        self.comboBoxnTriggerDirAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTriggerDirAB['values'] = Config.comboBoxnTriggerDirAB
        self.comboBoxnTriggerDirAB.grid(row=1, column=2)

        global comboBoxnTriggerDirAB
        comboBoxnTriggerDirAB = self.comboBoxnTriggerDirAB

        # textBoxbstrTriggerPriceAB
        tk.Label(self, text = "A商品 觸發價").grid(row=1, column=3)
        #輸入框
        self.textBoxbstrTriggerPriceAB = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerPriceAB.grid(row=1, column=4)

        global textBoxbstrTriggerPriceAB
        textBoxbstrTriggerPriceAB = self.textBoxbstrTriggerPriceAB

        # comboBoxnBuySellAB
        tk.Label(self, text = "B商品 買賣別(0:買, 1:賣)").grid(row=2, column=1)
            #輸入框
        self.comboBoxnBuySellAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySellAB['values'] = Config.comboBoxnBuySellAB
        self.comboBoxnBuySellAB.grid(row=2, column=2)

        global comboBoxnBuySellAB
        comboBoxnBuySellAB = self.comboBoxnBuySellAB

        # comboBoxnOrderTypeAB
        tk.Label(self, text = "B商品 委託交易別(0:現股, 3:融資, 4:融券, 8:無券普賣)").grid(row=2, column=3)
            #輸入框
        self.comboBoxnOrderTypeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderTypeAB['values'] = Config.comboBoxnOrderTypeAB
        self.comboBoxnOrderTypeAB.grid(row=2, column=4)

        global comboBoxnOrderTypeAB
        comboBoxnOrderTypeAB = self.comboBoxnOrderTypeAB

        # comboBoxnOrderCondAB
        tk.Label(self, text = "B商品 委託時效(0:ROD,3:IOC,4:FOK)").grid(row=2, column=5)
            #輸入框
        self.comboBoxnOrderCondAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderCondAB['values'] = Config.comboBoxnOrderCondAB
        self.comboBoxnOrderCondAB.grid(row=2, column=6)

        global comboBoxnOrderCondAB
        comboBoxnOrderCondAB = self.comboBoxnOrderCondAB

        # textBoxbstrStockNoAB
        tk.Label(self, text = "B商品 委託股票代號").grid(row=3, column=1)
        #輸入框
        self.textBoxbstrStockNoAB = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoAB.grid(row=3, column=2)

        global textBoxbstrStockNoAB
        textBoxbstrStockNoAB = self.textBoxbstrStockNoAB

        # comboBoxnPrimeAB
        tk.Label(self, text = "B商品 0:上市,1:上櫃").grid(row=3, column=3)
            #輸入框
        self.comboBoxnPrimeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnPrimeAB['values'] = Config.comboBoxnPrimeAB
        self.comboBoxnPrimeAB.grid(row=3, column=4)

        global comboBoxnPrimeAB
        comboBoxnPrimeAB = self.comboBoxnPrimeAB

        # textBoxnQtyAB
        tk.Label(self, text = "B商品 委託張數").grid(row=3, column=5)
        #輸入框
        self.textBoxnQtyAB = tk.Entry(self, width= 6)
        self.textBoxnQtyAB.grid(row=3, column=6)

        global textBoxnQtyAB
        textBoxnQtyAB = self.textBoxnQtyAB

        # comboBoxnOrderPriceTypeAB
        tk.Label(self, text = "B商品委託價類別(1:市價; 2:限價)").grid(row=3, column=7)
            #輸入框
        self.comboBoxnOrderPriceTypeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeAB['values'] = Config.comboBoxnOrderPriceTypeAB
        self.comboBoxnOrderPriceTypeAB.grid(row=3, column=8)

        global comboBoxnOrderPriceTypeAB
        comboBoxnOrderPriceTypeAB = self.comboBoxnOrderPriceTypeAB

        # textBoxbstrOrderPriceAB
        tk.Label(self, text = "B商品 委託價").grid(row=3, column=9)
        #輸入框
        self.textBoxbstrOrderPriceAB = tk.Entry(self, width= 6)
        self.textBoxbstrOrderPriceAB.grid(row=3, column=10)

        global textBoxbstrOrderPriceAB
        textBoxbstrOrderPriceAB = self.textBoxbstrOrderPriceAB

        # comboBoxnReserved
        tk.Label(self, text = "是否為預約單(0:否, 1:是)A商品為國內期選商品時可選預約單，其餘市場為非預約單:").grid(row=4, column=1)
            #輸入框
        self.comboBoxnReserved = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnReserved['values'] = Config.comboBoxnReserved
        self.comboBoxnReserved.grid(row=4, column=2)

        global comboBoxnReserved
        comboBoxnReserved = self.comboBoxnReserved

        # buttonSendStockStrategyAB
        self.buttonSendStockStrategyAB = tk.Button(self)
        self.buttonSendStockStrategyAB["text"] = "AB送出"
        self.buttonSendStockStrategyAB["command"] = self.buttonSendStockStrategyAB_Click
        self.buttonSendStockStrategyAB.grid(row=5, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendStockStrategyAB_Click(self):
        
        pOrder = sk.STOCKSTRATEGYORDERMIT()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoAB.get()
        pOrder.bstrOrderPrice = textBoxbstrOrderPriceAB.get()
        pOrder.bstrTriggerPrice = textBoxbstrTriggerPriceAB.get()
        pOrder.bstrExchangeNo = textBoxbstrExchangeNo.get()
        pOrder.bstrStockNo2 = textBoxbstrStockNo2.get()
        pOrder.bstrStartPrice = textBoxbstrStartPriceAB.get()
        pOrder.nQty = int(textBoxnQtyAB.get())

        if (comboBoxnOrderTypeAB.get() == "0:現股"):
            pOrder.nOrderType = 0
        elif (comboBoxnOrderTypeAB.get() == "3融資"):
            pOrder.nOrderType = 3
        elif (comboBoxnOrderTypeAB.get() == "4:融券"):
            pOrder.nOrderType = 4
        elif (comboBoxnOrderTypeAB.get() == "8:無券普賣"):
            pOrder.nOrderType = 8

        if (comboBoxnBuySellAB.get() == "0:買"):
            pOrder.nBuySell = 0
        elif (comboBoxnBuySellAB.get() == "1:賣"):
            pOrder.nBuySell = 1

        if (comboBoxnOrderPriceTypeAB.get() == "1:市價"):
            pOrder.nOrderPriceType = 1
        elif (comboBoxnOrderPriceTypeAB.get() == "2:限價"):
            pOrder.nOrderPriceType = 2

        if (comboBoxnOrderCondAB.get() == "0:ROD"):
            pOrder.nOrderCond = 0
        elif (comboBoxnOrderCondAB.get() == "3:IOC"):
            pOrder.nOrderCond = 3
        elif (comboBoxnOrderCondAB.get() == "4:FOK"):
            pOrder.nOrderCond = 4

        if (comboBoxnTriggerDirAB.get() == "1:GTE大於等於"):
            pOrder.nTriggerDir = 1
        elif (comboBoxnTriggerDirAB.get() == "2:LTE小於等於"):
            pOrder.nTriggerDir = 2

        if (comboBoxnMarketNo.get() == "1:國內證"):
            pOrder.nMarketNo = 1
        elif (comboBoxnMarketNo.get() == "2:國內期"):
            pOrder.nMarketNo = 2
        elif (comboBoxnMarketNo.get() == "3:國外證"):
            pOrder.nMarketNo = 3
        elif (comboBoxnMarketNo.get() == "4:國外期"):
            pOrder.nMarketNo = 4

        if (comboBoxnReserved.get() == "0:否"):
            pOrder.nReserved = 0
        elif (comboBoxnReserved.get() == "1:是"):
            pOrder.nReserved = 1

        if (comboBoxnPrimeAB.get() == "0:上市"):
            pOrder.nPrime = 1
        elif (comboBoxnPrimeAB.get() == "1:上櫃"):
            pOrder.nPrime = 2

        # 送出證券智慧單看A下B單委託。
        bstrMessage,nCode= m_pSKOrder.SendStockStrategyAB(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockStrategyAB】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 
######################################################################################################################################
#CBForm
class CBForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrStockNoCB
        tk.Label(self, text = "委託股票代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoCB = tk.Entry(self)
        self.textBoxbstrStockNoCB.grid(row=0, column=2)

        global textBoxbstrStockNoCB
        textBoxbstrStockNoCB = self.textBoxbstrStockNoCB

        # comboBoxnOrderTypeCB
        tk.Label(self, text = "委託交易別(0:現股, 3:融資, 4:融券, 8:無券普賣)").grid(row=1, column=1)
            #輸入框
        self.comboBoxnOrderTypeCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnOrderTypeCB['values'] = Config.comboBoxnOrderTypeCB
        self.comboBoxnOrderTypeCB.grid(row=1, column=2)

        global comboBoxnOrderTypeCB
        comboBoxnOrderTypeCB = self.comboBoxnOrderTypeCB

        # comboBoxnOrderPriceCondCB
        tk.Label(self, text = "委託時效(0:ROD,3:IOC,4:FOK)").grid(row=1, column=3)
            #輸入框
        self.comboBoxnOrderPriceCondCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnOrderPriceCondCB['values'] = Config.comboBoxnOrderPriceCondCB
        self.comboBoxnOrderPriceCondCB.grid(row=1, column=4)

        global comboBoxnOrderPriceCondCB
        comboBoxnOrderPriceCondCB = self.comboBoxnOrderPriceCondCB

        # comboBoxnBuySellCB
        tk.Label(self, text = "0買;1賣").grid(row=1, column=5)
            #輸入框
        self.comboBoxnBuySellCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnBuySellCB['values'] = Config.comboBoxnBuySellCB
        self.comboBoxnBuySellCB.grid(row=1, column=6)

        global comboBoxnBuySellCB
        comboBoxnBuySellCB = self.comboBoxnBuySellCB

        # comboBoxnInnerOrderIsMITCB
        tk.Label(self, text = "觸發條件是否為成交價(0:否, 1:是)").grid(row=2, column=1)
            #輸入框
        self.comboBoxnInnerOrderIsMITCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnInnerOrderIsMITCB['values'] = Config.comboBoxnInnerOrderIsMITCB
        self.comboBoxnInnerOrderIsMITCB.grid(row=2, column=2)

        global comboBoxnInnerOrderIsMITCB
        comboBoxnInnerOrderIsMITCB = self.comboBoxnInnerOrderIsMITCB

        # comboBoxnMITDirCB
        tk.Label(self, text = "成交價觸價方向(0:None, 1:GTE大於等於, 2:LTE小於等於)").grid(row=2, column=3)
            #輸入框
        self.comboBoxnMITDirCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnMITDirCB['values'] = Config.comboBoxnMITDirCB
        self.comboBoxnMITDirCB.grid(row=2, column=4)

        global comboBoxnMITDirCB
        comboBoxnMITDirCB = self.comboBoxnMITDirCB

        # textBoxbstrMITTriggerPriceCB
        tk.Label(self, text = "成交價").grid(row=2, column=5)
        #輸入框
        self.textBoxbstrMITTriggerPriceCB = tk.Entry(self)
        self.textBoxbstrMITTriggerPriceCB.grid(row=2, column=6)

        global textBoxbstrMITTriggerPriceCB
        textBoxbstrMITTriggerPriceCB = self.textBoxbstrMITTriggerPriceCB

        # comboBoxnTakeProfitFlagCB
        tk.Label(self, text = "觸發條件是否為委買價 0:否；1:是").grid(row=3, column=1)
            #輸入框
        self.comboBoxnTakeProfitFlagCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnTakeProfitFlagCB['values'] = Config.comboBoxnTakeProfitFlagCB
        self.comboBoxnTakeProfitFlagCB.grid(row=3, column=2)

        global comboBoxnTakeProfitFlagCB
        comboBoxnTakeProfitFlagCB = self.comboBoxnTakeProfitFlagCB

        # comboBoxnTPDir
        tk.Label(self, text = "委買價觸價方向 (0:None, 1:GTE大於等於, 2:LTE小於等於)").grid(row=3, column=3)
            #輸入框
        self.comboBoxnTPDir = ttk.Combobox(self, state='readonly')
        self.comboBoxnTPDir['values'] = Config.comboBoxnTPDir
        self.comboBoxnTPDir.grid(row=3, column=4)

        global comboBoxnTPDir
        comboBoxnTPDir = self.comboBoxnTPDir

        # textBoxbstrTPOrderPriceCB
        tk.Label(self, text = "委買價").grid(row=3, column=5)
        #輸入框
        self.textBoxbstrTPOrderPriceCB = tk.Entry(self)
        self.textBoxbstrTPOrderPriceCB.grid(row=3, column=6)

        global textBoxbstrTPOrderPriceCB
        textBoxbstrTPOrderPriceCB = self.textBoxbstrTPOrderPriceCB

        # comboBoxnUpDownFlag
        tk.Label(self, text = "是否為漲跌幅 (0:否, 1:是)").grid(row=4, column=1)
            #輸入框
        self.comboBoxnUpDownFlag = ttk.Combobox(self, state='readonly')
        self.comboBoxnUpDownFlag['values'] = Config.comboBoxnUpDownFlag
        self.comboBoxnUpDownFlag.grid(row=4, column=2)

        global comboBoxnUpDownFlag
        comboBoxnUpDownFlag = self.comboBoxnUpDownFlag

        # comboBoxnUpDownDir
        tk.Label(self, text = "漲跌幅觸價方向(0:None, 1:GTE大於等於, 2:LTE小於等於)").grid(row=4, column=3)
            #輸入框
        self.comboBoxnUpDownDir = ttk.Combobox(self, state='readonly')
        self.comboBoxnUpDownDir['values'] = Config.comboBoxnUpDownDir
        self.comboBoxnUpDownDir.grid(row=4, column=4)

        global comboBoxnUpDownDir
        comboBoxnUpDownDir = self.comboBoxnUpDownDir

        # textBoxbstrSLPercentCB
        tk.Label(self, text = "漲跌幅數").grid(row=4, column=5)
        #輸入框
        self.textBoxbstrSLPercentCB = tk.Entry(self)
        self.textBoxbstrSLPercentCB.grid(row=4, column=6)

        global textBoxbstrSLPercentCB
        textBoxbstrSLPercentCB = self.textBoxbstrSLPercentCB

        # comboBoxnPreQtyFlagCB
        tk.Label(self, text = "是否執行單量 (0:否, 1:是)").grid(row=5, column=1)
            #輸入框
        self.comboBoxnPreQtyFlagCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnPreQtyFlagCB['values'] = Config.comboBoxnPreQtyFlagCB
        self.comboBoxnPreQtyFlagCB.grid(row=5, column=2)

        global comboBoxnPreQtyFlagCB
        comboBoxnPreQtyFlagCB = self.comboBoxnPreQtyFlagCB

        # comboBoxnPreQtyDirCB
        tk.Label(self, text = "單量觸價方向(0:None, 1:GTE大於等於, 2:LTE小於等於)").grid(row=5, column=3)
            #輸入框
        self.comboBoxnPreQtyDirCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnPreQtyDirCB['values'] = Config.comboBoxnPreQtyDirCB
        self.comboBoxnPreQtyDirCB.grid(row=5, column=4)

        global comboBoxnPreQtyDirCB
        comboBoxnPreQtyDirCB = self.comboBoxnPreQtyDirCB

        # textBoxbstrPreQtyCB
        tk.Label(self, text = "單量").grid(row=5, column=5)
        #輸入框
        self.textBoxbstrPreQtyCB = tk.Entry(self)
        self.textBoxbstrPreQtyCB.grid(row=5, column=6)

        global textBoxbstrPreQtyCB
        textBoxbstrPreQtyCB = self.textBoxbstrPreQtyCB

        # comboBoxnTickFlagCB
        tk.Label(self, text = "是否為tick觸發(0:否, 1:是)").grid(row=6, column=1)
            #輸入框
        self.comboBoxnTickFlagCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnTickFlagCB['values'] = Config.comboBoxnTickFlagCB
        self.comboBoxnTickFlagCB.grid(row=6, column=2)

        global comboBoxnTickFlagCB
        comboBoxnTickFlagCB = self.comboBoxnTickFlagCB

        # comboBoxnTickDir
        tk.Label(self, text = "tick觸發方向 (0:None, 1:GTE大於等於, 2:LTE小於等於)").grid(row=6, column=3)
            #輸入框
        self.comboBoxnTickDir = ttk.Combobox(self, state='readonly')
        self.comboBoxnTickDir['values'] = Config.comboBoxnTickDir
        self.comboBoxnTickDir.grid(row=6, column=4)

        global comboBoxnTickDir
        comboBoxnTickDir = self.comboBoxnTickDir

        # textBoxbstrTickCB
        tk.Label(self, text = "tick數").grid(row=6, column=5)
        #輸入框
        self.textBoxbstrTickCB = tk.Entry(self)
        self.textBoxbstrTickCB.grid(row=6, column=6)

        global textBoxbstrTickCB
        textBoxbstrTickCB = self.textBoxbstrTickCB

        # comboBoxnStopLossFlagCB
        tk.Label(self, text = "是否為委賣價(0:否, 1:是)").grid(row=7, column=1)
            #輸入框
        self.comboBoxnStopLossFlagCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnStopLossFlagCB['values'] = Config.comboBoxnStopLossFlagCB
        self.comboBoxnStopLossFlagCB.grid(row=7, column=2)

        global comboBoxnStopLossFlagCB
        comboBoxnStopLossFlagCB = self.comboBoxnStopLossFlagCB

        # comboBoxnSLDirCB
        tk.Label(self, text = "委賣價觸價方向(0:None, 1:GTE大於等於, 2:LTE小於等於").grid(row=7, column=3)
            #輸入框
        self.comboBoxnSLDirCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnSLDirCB['values'] = Config.comboBoxnSLDirCB
        self.comboBoxnSLDirCB.grid(row=7, column=4)

        global comboBoxnSLDirCB
        comboBoxnSLDirCB = self.comboBoxnSLDirCB

        # textBoxbstrSLOrderPriceCB
        tk.Label(self, text = "委賣價").grid(row=7, column=5)
        #輸入框
        self.textBoxbstrSLOrderPriceCB = tk.Entry(self)
        self.textBoxbstrSLOrderPriceCB.grid(row=7, column=6)

        global textBoxbstrSLOrderPriceCB
        textBoxbstrSLOrderPriceCB = self.textBoxbstrSLOrderPriceCB

        # comboBoxnSumQtyFlagCB
        tk.Label(self, text = "觸發條件是否為總量/(0:否, 1:是)").grid(row=8, column=1)
            #輸入框
        self.comboBoxnSumQtyFlagCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnSumQtyFlagCB['values'] = Config.comboBoxnSumQtyFlagCB
        self.comboBoxnSumQtyFlagCB.grid(row=8, column=2)

        global comboBoxnSumQtyFlagCB
        comboBoxnSumQtyFlagCB = self.comboBoxnSumQtyFlagCB

        # comboBoxnSumQtyDir
        tk.Label(self, text = "總量觸價方向(0:None, 1:GTE大於等於, 2:LTE小於等於)").grid(row=8, column=3)
            #輸入框
        self.comboBoxnSumQtyDir = ttk.Combobox(self, state='readonly')
        self.comboBoxnSumQtyDir['values'] = Config.comboBoxnSumQtyDir
        self.comboBoxnSumQtyDir.grid(row=8, column=4)

        global comboBoxnSumQtyDir
        comboBoxnSumQtyDir = self.comboBoxnSumQtyDir

        # textBoxbstrSumQtyCB
        tk.Label(self, text = "總量").grid(row=8, column=5)
        #輸入框
        self.textBoxbstrSumQtyCB = tk.Entry(self)
        self.textBoxbstrSumQtyCB.grid(row=8, column=6)

        global textBoxbstrSumQtyCB
        textBoxbstrSumQtyCB = self.textBoxbstrSumQtyCB

        # comboBoxnClearAllFlagCB
        tk.Label(self, text = "是否為自訂啟動時間(0:立即,1:自訂)").grid(row=9, column=1)
            #輸入框
        self.comboBoxnClearAllFlagCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnClearAllFlagCB['values'] = Config.comboBoxnClearAllFlagCB
        self.comboBoxnClearAllFlagCB.grid(row=9, column=2)

        global comboBoxnClearAllFlagCB
        comboBoxnClearAllFlagCB = self.comboBoxnClearAllFlagCB

        # textBoxbstrClearCancelTimeCB
        tk.Label(self, text = "自訂啟動時間(14天內) 格式：hhmmss (時時分分秒秒)").grid(row=9, column=3)
        #輸入框
        self.textBoxbstrClearCancelTimeCB = tk.Entry(self)
        self.textBoxbstrClearCancelTimeCB.grid(row=9, column=4)

        global textBoxbstrClearCancelTimeCB
        textBoxbstrClearCancelTimeCB = self.textBoxbstrClearCancelTimeCB

        # comboBoxnFinalClearFlagCB
        tk.Label(self, text = "條件是否為全部成立 (0:任一成立, 1:全部成立)").grid(row=9, column=5)
            #輸入框
        self.comboBoxnFinalClearFlagCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnFinalClearFlagCB['values'] = Config.comboBoxnFinalClearFlagCB
        self.comboBoxnFinalClearFlagCB.grid(row=9, column=6)

        global comboBoxnFinalClearFlagCB
        comboBoxnFinalClearFlagCB = self.comboBoxnFinalClearFlagCB

        # textBoxnQtyCB
        tk.Label(self, text = "委託張數").grid(row=10, column=1)
        #輸入框
        self.textBoxnQtyCB = tk.Entry(self)
        self.textBoxnQtyCB.grid(row=10, column=2)

        global textBoxnQtyCB
        textBoxnQtyCB = self.textBoxnQtyCB

        # comboBoxnOrderPriceTypeCB
        tk.Label(self, text = "委託價類別(1:市價; 2:限價)").grid(row=11, column=1)
            #輸入框
        self.comboBoxnOrderPriceTypeCB = ttk.Combobox(self, state='readonly')
        self.comboBoxnOrderPriceTypeCB['values'] = Config.comboBoxnOrderPriceTypeCB
        self.comboBoxnOrderPriceTypeCB.grid(row=11, column=2)

        global comboBoxnOrderPriceTypeCB
        comboBoxnOrderPriceTypeCB = self.comboBoxnOrderPriceTypeCB

        # textBoxbstrOrderPriceCB
        tk.Label(self, text = "委託價").grid(row=11, column=3)
        #輸入框
        self.textBoxbstrOrderPriceCB = tk.Entry(self)
        self.textBoxbstrOrderPriceCB.grid(row=11, column=4)

        global textBoxbstrOrderPriceCB
        textBoxbstrOrderPriceCB = self.textBoxbstrOrderPriceCB

        # buttonSendStockStrategyCB
        self.buttonSendStockStrategyCB = tk.Button(self)
        self.buttonSendStockStrategyCB["text"] = "CB送出"
        self.buttonSendStockStrategyCB["command"] = self.buttonSendStockStrategyCB_Click
        self.buttonSendStockStrategyCB.grid(row=12, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendStockStrategyCB_Click(self):
        
        pOrder = sk.STOCKSTRATEGYORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoCB.get()
        pOrder.nQty = int(textBoxnQtyCB.get())
        pOrder.bstrOrderPrice = textBoxbstrOrderPriceCB.get()
        pOrder.bstrMITTriggerPrice = textBoxbstrMITTriggerPriceCB.get()
        pOrder.bstrTPOrderPrice = textBoxbstrTPOrderPriceCB.get()
        pOrder.bstrSLOrderPrice = textBoxbstrSLOrderPriceCB.get()
        pOrder.bstrTick = textBoxbstrTickCB.get()
        pOrder.bstrSLPercent = textBoxbstrSLPercentCB.get()
        pOrder.bstrPreQty = textBoxbstrPreQtyCB.get()
        pOrder.bstrSumQty = textBoxbstrSumQtyCB.get()
        pOrder.bstrClearCancelTime = textBoxbstrClearCancelTimeCB.get()

        if (comboBoxnOrderTypeCB.get() == "0:現股"):
            pOrder.nOrderType = 0
        elif (comboBoxnOrderTypeCB.get() == "3:融資"):
            pOrder.nOrderType = 3
        elif (comboBoxnOrderTypeCB.get() == "4:融券"):
            pOrder.nOrderType = 4
        elif (comboBoxnOrderTypeCB.get() == "8:無券普賣"):
            pOrder.nOrderType = 8

        if (comboBoxnOrderPriceCondCB.get() == "0:ROD"):
            pOrder.nOrderPriceCond = 0
        elif (comboBoxnOrderPriceCondCB.get() == "3:IOC"):
            pOrder.nOrderPriceCond = 3
        elif (comboBoxnOrderPriceCondCB.get() == "4:FOK"):
            pOrder.nOrderPriceCond = 4

        if (comboBoxnBuySellCB.get() == "0:買"):
            pOrder.nBuySell = 0
        elif (comboBoxnBuySellCB.get() == "1:賣"):
            pOrder.nBuySell = 1

        if (comboBoxnOrderPriceTypeCB.get() == "1:市價"):
            pOrder.nOrderPriceType = 1
        elif (comboBoxnOrderPriceTypeCB.get() == "2:限價"):
            pOrder.nOrderPriceType = 2

        if (comboBoxnInnerOrderIsMITCB.get() == "0:否"):
            pOrder.nInnerOrderIsMIT = 0
        elif (comboBoxnInnerOrderIsMITCB.get() == "1:是"):
            pOrder.nInnerOrderIsMIT = 1

        if (comboBoxnTPDir.get() == "0:None"):
            pOrder.nTPDir = 0
        elif (comboBoxnTPDir.get() == "1:GTE大於等於"):
            pOrder.nTPDir = 1
        elif (comboBoxnTPDir.get() == "2:LTE小於等於"):
            pOrder.nTPDir = 2

        if (comboBoxnStopLossFlagCB.get() == "0:否"):
            pOrder.nStopLossFlag = 0
        elif (comboBoxnStopLossFlagCB.get() == "1:是"):
            pOrder.nStopLossFlag = 1

        if (comboBoxnSLDirCB.get() == "0:None"):
            pOrder.nSLDir = 0
        elif (comboBoxnSLDirCB.get() == "1:GTE大於等於"):
            pOrder.nSLDir = 1
        elif (comboBoxnSLDirCB.get() == "2:LTE小於等於"):
            pOrder.nSLDir = 2

        if (comboBoxnTickFlagCB.get() == "0:否"):
            pOrder.nTickFlag = 0
        elif (comboBoxnTickFlagCB.get() == "1:是"):
            pOrder.nTickFlag = 1

        if (comboBoxnTickDir.get() == "0:None"):
            pOrder.nTickDir = 0
        elif (comboBoxnTickDir.get() == "1:GTE大於等於"):
            pOrder.nTickDir = 1
        elif (comboBoxnTickDir.get() == "2:LTE小於等於"):
            pOrder.nTickDir = 2

        if (comboBoxnUpDownFlag.get() == "0:否"):
            pOrder.nUpDownFlag = 0
        elif (comboBoxnUpDownFlag.get() == "1:是"):
            pOrder.nUpDownFlag = 1

        if (comboBoxnUpDownDir.get() == "0:None"):
            pOrder.nUpDownDir = 0
        elif (comboBoxnUpDownDir.get() == "1:GTE大於等於"):
            pOrder.nUpDownDir = 1
        elif (comboBoxnUpDownDir.get() == "2:LTE小於等於"):
            pOrder.nUpDownDir = 2

        if (comboBoxnPreQtyFlagCB.get() == "0:否"):
            pOrder.nPreQtyFlag = 0
        elif (comboBoxnPreQtyFlagCB.get() == "1:是"):
            pOrder.nPreQtyFlag = 1

        if (comboBoxnPreQtyDirCB.get() == "0:None"):
            pOrder.nPreQtyDir = 0
        elif (comboBoxnPreQtyDirCB.get() == "1:GTE大於等於"):
            pOrder.nPreQtyDir = 1
        elif (comboBoxnPreQtyDirCB.get() == "2:LTE小於等於"):
            pOrder.nPreQtyDir = 2

        if (comboBoxnSumQtyFlagCB.get() == "0:否"):
            pOrder.nSumQtyFlag = 0
        elif (comboBoxnSumQtyFlagCB.get() == "1:是"):
            pOrder.nSumQtyFlag = 1

        if (comboBoxnSumQtyDir.get() == "0:None"):
            pOrder.nSumQtyDir = 0
        elif (comboBoxnSumQtyDir.get() == "1:GTE大於等於"):
            pOrder.nSumQtyDir = 1
        elif (comboBoxnSumQtyDir.get() == "2:LTE小於等於"):
            pOrder.nSumQtyDir = 2

        if (comboBoxnClearAllFlagCB.get() == "0:否"):
            pOrder.nClearAllFlag = 0
        elif (comboBoxnClearAllFlagCB.get() == "1:是"):
            pOrder.nClearAllFlag = 1

        if (comboBoxnFinalClearFlagCB.get() == "0:否"):
            pOrder.nFinalClearFlag = 0
        elif (comboBoxnFinalClearFlagCB.get() == "1:是"):
            pOrder.nFinalClearFlag = 1

        if (comboBoxnMITDirCB.get() == "0:None"):
            pOrder.nMITDir = 0
        elif (comboBoxnMITDirCB.get() == "1:GTE大於等於"):
            pOrder.nMITDir = 1
        elif (comboBoxnMITDirCB.get() == "2:LTE小於等於"):
            pOrder.nMITDir = 2

        if (comboBoxnTakeProfitFlagCB.get() == "0:否"):
            pOrder.nTakeProfitFlag = 0
        elif (comboBoxnTakeProfitFlagCB.get() == "1:是"):
            pOrder.nTakeProfitFlag = 1

        # 送出證券智慧單自組單委託。
        bstrMessage,nCode= m_pSKOrder.SendStockStrategyCB(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockStrategyCB】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 
######################################################################################################################################
#CancelForm
class CancelForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # checkBoxAsyncOrder
        # 是否為非同步委託

        self.checkBoxAsyncOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxAsyncOrder["variable"] = self.var1
        self.checkBoxAsyncOrder["onvalue"] = True
        self.checkBoxAsyncOrder["offvalue"] = False
        self.checkBoxAsyncOrder["text"] = "非同步委託"
        self.checkBoxAsyncOrder["command"] = self.checkBoxAsyncOrder_CheckedChanged
        self.checkBoxAsyncOrder.grid( row = 0,column = 0)

        # textBoxbstrSmartKey
        tk.Label(self, text = "智慧單號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrSmartKey = tk.Entry(self)
        self.textBoxbstrSmartKey.grid(row=0, column=2)

        global textBoxbstrSmartKey
        textBoxbstrSmartKey = self.textBoxbstrSmartKey

        # comboBoxnMarket
        tk.Label(self, text = "市場別(AB單需選欲刪單之A商品市場)").grid(row=1, column=1)
            #輸入框
        self.comboBoxnMarket = ttk.Combobox(self, state='readonly')
        self.comboBoxnMarket['values'] = Config.comboBoxnMarket
        self.comboBoxnMarket.grid(row=1, column=2)

        global comboBoxnMarket
        comboBoxnMarket = self.comboBoxnMarket

        # textBoxbstrSeqNo
        tk.Label(self, text = "委託序號 (預約單可忽略)").grid(row=2, column=1)
        #輸入框
        self.textBoxbstrSeqNo = tk.Entry(self)
        self.textBoxbstrSeqNo.grid(row=2, column=2)

        global textBoxbstrSeqNo
        textBoxbstrSeqNo = self.textBoxbstrSeqNo

        # textBoxbstrOrderNo
        tk.Label(self, text = "委託書號（若觸發，需給書號）").grid(row=3, column=1)
        #輸入框
        self.textBoxbstrOrderNo = tk.Entry(self)
        self.textBoxbstrOrderNo.grid(row=3, column=2)

        global textBoxbstrOrderNo
        textBoxbstrOrderNo = self.textBoxbstrOrderNo

        # textBoxbstrLongActionKey
        tk.Label(self, text = "長效單號(非長效單可忽略)").grid(row=4, column=1)
        #輸入框
        self.textBoxbstrLongActionKey = tk.Entry(self)
        self.textBoxbstrLongActionKey.grid(row=4, column=2)

        global textBoxbstrLongActionKey
        textBoxbstrLongActionKey = self.textBoxbstrLongActionKey

        # textBoxbstrParentSmartKey
        tk.Label(self, text = "(當沖)智慧母單號").grid(row=5, column=1)
        #輸入框
        self.textBoxbstrParentSmartKey = tk.Entry(self)
        self.textBoxbstrParentSmartKey.grid(row=5, column=2)

        global textBoxbstrParentSmartKey
        textBoxbstrParentSmartKey = self.textBoxbstrParentSmartKey

        # comboBoxnDeletType
        tk.Label(self, text = "(當沖)刪單類型").grid(row=6, column=1)
            #輸入框
        self.comboBoxnDeletType = ttk.Combobox(self, state='readonly')
        self.comboBoxnDeletType['values'] = Config.comboBoxnDeletType
        self.comboBoxnDeletType.grid(row=6, column=2)

        global comboBoxnDeletType
        comboBoxnDeletType = self.comboBoxnDeletType

        # textBoxbstrSmartKeyOut
        tk.Label(self, text = "(當沖)出場單號").grid(row=7, column=1)
        #輸入框
        self.textBoxbstrSmartKeyOut = tk.Entry(self)
        self.textBoxbstrSmartKeyOut.grid(row=7, column=2)

        global textBoxbstrSmartKeyOut
        textBoxbstrSmartKeyOut = self.textBoxbstrSmartKeyOut

        # comboBoxnTradeKind
        tk.Label(self, text = "舊版:6:MIOC;7:MST; 8:MIT").grid(row=8, column=1)
            #輸入框
        self.comboBoxnTradeKind = ttk.Combobox(self, state='readonly')
        self.comboBoxnTradeKind['values'] = Config.comboBoxnTradeKind
        self.comboBoxnTradeKind.grid(row=8, column=2)

        global comboBoxnTradeKind
        comboBoxnTradeKind = self.comboBoxnTradeKind

        # buttonCancelTSStrategyOrder
        self.buttonCancelTSStrategyOrder = tk.Button(self)
        self.buttonCancelTSStrategyOrder["text"] = "(6:MIOC;7:MST; 8:MIT)舊版刪單送出"
        self.buttonCancelTSStrategyOrder["command"] = self.buttonCancelTSStrategyOrder_Click
        self.buttonCancelTSStrategyOrder.grid(row=8, column=3)

        # comboBoxnTradeKindV1
        tk.Label(self, text = "V1版本:3:OCO; 8:MIT;9:MST;10:AB;11:當沖;17:出清;27：CB").grid(row=9, column=1)
            #輸入框
        self.comboBoxnTradeKindV1 = ttk.Combobox(self, state='readonly')
        self.comboBoxnTradeKindV1['values'] = Config.comboBoxnTradeKindV1
        self.comboBoxnTradeKindV1.grid(row=9, column=2)

        global comboBoxnTradeKindV1
        comboBoxnTradeKindV1 = self.comboBoxnTradeKindV1

        # buttonCancelTSStrategyOrderV1
        self.buttonCancelTSStrategyOrderV1 = tk.Button(self)
        self.buttonCancelTSStrategyOrderV1["text"] = "新版刪單送出"
        self.buttonCancelTSStrategyOrderV1["command"] = self.buttonCancelTSStrategyOrderV1_Click
        self.buttonCancelTSStrategyOrderV1.grid(row=9, column=3)
      
        # buttonCancelStrategyList
        self.buttonCancelStrategyList = tk.Button(self)
        self.buttonCancelStrategyList["text"] = "多筆刪單送出(以逗號分隔，EX：682020,682021)"
        self.buttonCancelStrategyList["command"] = self.buttonCancelStrategyList_Click
        self.buttonCancelStrategyList.grid(row=1, column=3)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonCancelTSStrategyOrder_Click(self):
        
        if (comboBoxnTradeKind.get() == "6:MIOC"):
            nTradeKind = 6
        elif (comboBoxnTradeKind.get() == "7:MST"):
            nTradeKind = 7
        elif (comboBoxnTradeKind.get() == "8:MIT"):
            nTradeKind = 8

        # 取消證券智慧單委託。欄位請參考GetTSStrategyOrder 回傳的內容。注意，當已經觸發的智慧單，將無法取消委託。
        bstrMessage,nCode= m_pSKOrder.CancelTSStrategyOrder(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxbstrSmartKey.get(), nTradeKind)

        msg = "【CancelTSStrategyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonCancelTSStrategyOrderV1_Click(self):
        
        pCancelOrder = sk.CANCELSTRATEGYORDER()
        pCancelOrder.bstrFullAccount = comboBoxAccount.get()

        if (comboBoxnMarket.get() == "1：國內證"):
            pCancelOrder.nMarket = 1
        elif (comboBoxnMarket.get() == "2：國內期"):
            pCancelOrder.nMarket = 2
        elif (comboBoxnMarket.get() == "3：國外證"):
            pCancelOrder.nMarket = 3
        elif (comboBoxnMarket.get() == "4：國外期"):
            pCancelOrder.nMarket = 4

        pCancelOrder.bstrParentSmartKey = textBoxbstrParentSmartKey.get()
        pCancelOrder.bstrSmartKey = textBoxbstrSmartKey.get()

        if (comboBoxnTradeKindV1.get() == "3:OCO"):
            pCancelOrder.nTradeKind = 3
        elif (comboBoxnTradeKindV1.get() == "8:MIT"):
            pCancelOrder.nTradeKind = 8
        elif (comboBoxnTradeKindV1.get() == "9:MST"):
            pCancelOrder.nTradeKind = 9
        elif (comboBoxnTradeKindV1.get() == "10:AB"):
            pCancelOrder.nTradeKind = 10
        elif (comboBoxnTradeKindV1.get() == "11:當沖"):
            pCancelOrder.nTradeKind = 11
        elif (comboBoxnTradeKindV1.get() == "17:出清"):
            pCancelOrder.nTradeKind = 17
        elif (comboBoxnTradeKindV1.get() == "27：CB"):
            pCancelOrder.nTradeKind = 27
        else:
            pCancelOrder.nTradeKind = 0

        if (comboBoxnDeletType.get() == "1:全部"):
            pCancelOrder.nDeleteType = 1
        elif (comboBoxnDeletType.get() == "2:進場單"):
            pCancelOrder.nDeleteType = 2
        elif (comboBoxnDeletType.get() == "3:出場單"):
            pCancelOrder.nDeleteType = 3

        pCancelOrder.bstrSeqNo = textBoxbstrSeqNo.get()
        pCancelOrder.bstrOrderNo = textBoxbstrOrderNo.get()
        pCancelOrder.bstrSmartKeyOut = textBoxbstrSmartKeyOut.get()

        # 取消證券智慧單委託。欄位請參考GetTSStrategyOrder 回傳的內容。注意，當已經觸發的智慧單，將無法取消委託。
        bstrMessage,nCode= m_pSKOrder.CancelTSStrategyOrderV1(comboBoxUserID.get(), pCancelOrder)

        msg = "【CancelTSStrategyOrderV1】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonCancelStrategyList_Click(self):
        
        pCancelOrder = sk.CANCELSTRATEGYORDER()
        pCancelOrder.bstrLogInID = comboBoxUserID.get()
        pCancelOrder.bstrFullAccount = comboBoxAccount.get()

        if (comboBoxnMarket.get() == "1：國內證"):
            pCancelOrder.nMarket = 1
        elif (comboBoxnMarket.get() == "2：國內期"):
            pCancelOrder.nMarket = 2
        elif (comboBoxnMarket.get() == "3：國外證"):
            pCancelOrder.nMarket = 3
        elif (comboBoxnMarket.get() == "4：國外期"):
            pCancelOrder.nMarket = 4

        pCancelOrder.bstrSmartKey = textBoxbstrSmartKey.get()

        # 取消多筆智慧單委託。刪單欄位請參考智慧單被動回報回傳的內容。
        bstrMessage,nCode= m_pSKOrder.CancelStrategyList(comboBoxUserID.get(), pCancelOrder)

        msg = "【CancelStrategyList】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#GetForm
class GetForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):

        # comboBoxbstrKind
        tk.Label(self, text = "智慧單類型").grid(row=0, column=1)
            #輸入框
        self.comboBoxbstrKind = ttk.Combobox(self, state='readonly')
        self.comboBoxbstrKind['values'] = Config.comboBoxbstrKind
        self.comboBoxbstrKind.grid(row=0, column=2)

        global comboBoxbstrKind
        comboBoxbstrKind = self.comboBoxbstrKind

        # textBoxbstrDate
        tk.Label(self, text = "查詢日期(ex:20220601)").grid(row=1, column=1)
        #輸入框
        self.textBoxbstrDate = tk.Entry(self)
        self.textBoxbstrDate.grid(row=1, column=2)

        global textBoxbstrDate
        textBoxbstrDate = self.textBoxbstrDate

        # buttonGetTSSmartStrategyReport
        self.buttonGetTSSmartStrategyReport = tk.Button(self)
        self.buttonGetTSSmartStrategyReport["text"] = "查詢送出"
        self.buttonGetTSSmartStrategyReport["command"] = self.buttonGetTSSmartStrategyReport_Click
        self.buttonGetTSSmartStrategyReport.grid(row=1, column=3)
    
    def buttonGetTSSmartStrategyReport_Click(self):

        if (comboBoxbstrKind.get() == "DayTrade:當沖"):
            bstrKind = "DayTrade"
        elif (comboBoxbstrKind.get() == "ClearOut:出清"):
            bstrKind = "ClearOut"
        elif (comboBoxbstrKind.get() == "MIT：觸價單、MIT長效單"):
            bstrKind = "MIT"
        elif (comboBoxbstrKind.get() == "OCO：二擇一"):
            bstrKind = "OCO"
        elif (comboBoxbstrKind.get() == "MIOC：多次IOC"):
            bstrKind = "MIOC"
        elif (comboBoxbstrKind.get() == "MST：移動停損、MST長效單"):
            bstrKind = "MST"
        elif (comboBoxbstrKind.get() == "AB：看A下B單"):
            bstrKind = "AB"
        elif (comboBoxbstrKind.get() == "CB：自組單"):
            bstrKind = "CB"

        # 查詢證券智慧單
        nCode= m_pSKOrder.GetTSSmartStrategyReport(comboBoxUserID.get(), comboBoxAccount.get(), "TS", 0, bstrKind, textBoxbstrDate.get())

        msg = "【GetTSSmartStrategyReport】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
#==========================================
#定義彈出視窗
def popup_window_DayTrade():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("DayTrade")

    # 建立 Frame 作為 DayTradeForm，並添加到彈出窗口
    popup_DayTradeForm = DayTradeForm(popup)
    popup_DayTradeForm.pack(fill=tk.BOTH, expand=True)
def popup_window_Clear():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Clear")

    # 建立 Frame 作為 ClearForm，並添加到彈出窗口
    popup_ClearForm = ClearForm(popup)
    popup_ClearForm.pack(fill=tk.BOTH, expand=True)
def popup_window_MIT():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("MIT")

    # 建立 Frame 作為 MITForm，並添加到彈出窗口
    popup_MITForm = MITForm(popup)
    popup_MITForm.pack(fill=tk.BOTH, expand=True)
def popup_window_OCO():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("OCO")

    # 建立 Frame 作為 OCOForm，並添加到彈出窗口
    popup_OCOForm = OCOForm(popup)
    popup_OCOForm.pack(fill=tk.BOTH, expand=True)
def popup_window_MIOC():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("MIOC")

    # 建立 Frame 作為 MIOCForm，並添加到彈出窗口
    popup_MIOCForm = MIOCForm(popup)
    popup_MIOCForm.pack(fill=tk.BOTH, expand=True)
def popup_window_MST():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("MST")

    # 建立 Frame 作為 MSTForm，並添加到彈出窗口
    popup_MSTForm = MSTForm(popup)
    popup_MSTForm.pack(fill=tk.BOTH, expand=True)
def popup_window_AB():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("AB")

    # 建立 Frame 作為 ABForm，並添加到彈出窗口
    popup_ABForm = ABForm(popup)
    popup_ABForm.pack(fill=tk.BOTH, expand=True)
def popup_window_CB():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("CB")

    # 建立 Frame 作為 CBForm，並添加到彈出窗口
    popup_CBForm = CBForm(popup)
    popup_CBForm.pack(fill=tk.BOTH, expand=True)
def popup_window_Cancel():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Cancel")

    # 建立 Frame 作為 CancelForm，並添加到彈出窗口
    popup_CancelForm = CancelForm(popup)
    popup_CancelForm.pack(fill=tk.BOTH, expand=True)
def popup_window_Get():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Get")

    # 建立 Frame 作為 GetForm，並添加到彈出窗口
    popup_GetForm = GetForm(popup)
    popup_GetForm.pack(fill=tk.BOTH, expand=True)
#開啟Tk視窗
if __name__ == '__main__':
    #建立主視窗
    root = tk.Tk()
    root.title("TSStrategyOrder")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)


    # 開啟DayTrade視窗的按鈕
    popup_button_DayTrade = tk.Button(root, text="當沖", command=popup_window_DayTrade)
    popup_button_DayTrade.grid(row = 1, column= 0)

    # 開啟Clear視窗的按鈕
    popup_button_Clear = tk.Button(root, text="出清", command=popup_window_Clear)
    popup_button_Clear.grid(row = 2, column= 0)

    # 開啟MIT視窗的按鈕
    popup_button_MIT = tk.Button(root, text="MIT", command=popup_window_MIT)
    popup_button_MIT.grid(row = 3, column= 0)

    # 開啟OCO視窗的按鈕
    popup_button_OCO = tk.Button(root, text="OCO", command=popup_window_OCO)
    popup_button_OCO.grid(row = 4, column= 0)

    # 開啟MIOC視窗的按鈕
    popup_button_MIOC = tk.Button(root, text="MIOC", command=popup_window_MIOC)
    popup_button_MIOC.grid(row = 5, column= 0)

    # 開啟MST視窗的按鈕
    popup_button_MST = tk.Button(root, text="MST", command=popup_window_MST)
    popup_button_MST.grid(row = 6, column= 0)

    # 開啟AB視窗的按鈕
    popup_button_AB = tk.Button(root, text="AB", command=popup_window_AB)
    popup_button_AB.grid(row = 7, column= 0)

    # 開啟CB視窗的按鈕
    popup_button_CB = tk.Button(root, text="CB", command=popup_window_CB)
    popup_button_CB.grid(row = 8, column= 0)

    # 開啟Cancel視窗的按鈕
    popup_button_CB = tk.Button(root, text="刪單", command=popup_window_Cancel)
    popup_button_CB.grid(row = 9, column= 0)

    # 開啟Get視窗的按鈕
    popup_button_CB = tk.Button(root, text="查詢", command=popup_window_Get)
    popup_button_CB.grid(row = 10, column= 0)

    root.mainloop()

#==========================================
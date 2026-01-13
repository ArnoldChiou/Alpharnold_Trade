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
    # 一個使用者id會與proxy server建一條連線，此事件回傳此條連線的連線狀態
    def OnProxyStatus(self, bstrUserId, nCode):
        msg = "【OnProxyStatus】" + bstrUserId + "_" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode);
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 證券即時庫存。透過呼叫GetRealBalanceReport後，資訊由該事件回傳。
    def OnRealBalanceReport(self, bstrData):
        msg = "【OnRealBalanceReport】" + bstrData;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 集保庫存查詢。透過呼叫 GetBalanceQuery後，資訊由該事件回傳。
    def OnBalanceQuery(self, bstrData):
        msg = "【OnBalanceQuery】" + bstrData;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 資券配額查詢。透過呼叫 GetMarginPurchaseAmountLimit後，資訊由該事件回傳。
    def OnMarginPurchaseAmountLimit(self, bstrData):
        msg = "【OnMarginPurchaseAmountLimit】" + bstrData;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 證券新損益查詢結果。透過呼叫GetProfitLossGWReport後，資訊由該事件回傳。
    def OnProfitLossGWReport(self, bstrData):
        msg = "【OnProfitLossGWReport】" + bstrData;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 非同步委託結果。
    def OnAsyncOrder(self, nThreadID, nCode, bstrMessage):
        msg = "【OnAsyncOrder】" + str(nThreadID) + str(nCode) + bstrMessage;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # Proxy委託結果。
    def OnProxyOrder(self, nStampID, nCode, bstrMessage):
        msg = "【OnProxyOrder】" + str(nStampID) + str(nCode) + bstrMessage;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
SKOrderEvent = SKOrderLibEvent();
SKOrderLibEventHandler = comtypes.client.GetEvents(m_pSKOrder, SKOrderEvent);

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

#AvgCostForm
class AvgCostForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()   

    def createWidgets(self):
        # textBoxAvgCostStockNo
        tk.Label(self, text = "商品代碼").grid(row=0, column=1)
        #輸入框
        self.textBoxAvgCostStockNo = tk.Entry(self)
        self.textBoxAvgCostStockNo.grid(row=0, column=2)

        global textBoxAvgCostStockNo
        textBoxAvgCostStockNo = self.textBoxAvgCostStockNo

        # comboBoxGetAvgCost
        tk.Label(self, text = "功能").grid(row = 0,column = 3)
        self.comboBoxGetAvgCost = ttk.Combobox(self, state='readonly')
        self.comboBoxGetAvgCost['values'] = Config.comboBoxGetAvgCost
        self.comboBoxGetAvgCost.grid(row=0, column=4)

        global comboBoxGetAvgCost
        comboBoxGetAvgCost = self.comboBoxGetAvgCost

        # buttonGetAvgCost
        self.buttonGetAvgCost = tk.Button(self)
        self.buttonGetAvgCost["text"] = "查詢"
        self.buttonGetAvgCost["command"] = self.buttonGetAvgCost_Click
        self.buttonGetAvgCost.grid(row=1, column=1)

        global buttonGetAvgCost
        buttonGetAvgCost = self.buttonGetAvgCost

    #buttonGetAvgCost_Click
    def buttonGetAvgCost_Click(self):
        pSKAVGCOST = sk.SKAVGCOST()
        pSKAVGCOST.bstrAccount = comboBoxAccount.get()
        pSKAVGCOST.bstrStockNo = textBoxAvgCostStockNo.get()

        if(comboBoxGetAvgCost.get() == "0:查詢昨日未沖銷明細"):
            pSKAVGCOST.bstrFunc = "0"

        bstrMessage, nCode = m_pSKOrder.GetAvgCost(comboBoxUserID.get(), pSKAVGCOST)

        msg = "【GetAvgCostData】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")

        strValues = bstrMessage.split('#')

        for value in strValues:
            if value != "":
                value = "【GetAvgCostData】" + value
                richTextBoxMessage.insert( 'end',  value + "\n")
                richTextBoxMessage.see('end')


######################################################################################################################################
#ReadForm
class ReadForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # buttonGetRealBalanceReport
        self.buttonGetRealBalanceReport = tk.Button(self)
        self.buttonGetRealBalanceReport["text"] = "即時庫存"
        self.buttonGetRealBalanceReport["command"] = self.buttonGetRealBalanceReport_Click
        self.buttonGetRealBalanceReport.grid(row=0, column=1)

        # buttonGetBalanceQuery 
        self.buttonGetBalanceQuery = tk.Button(self)
        self.buttonGetBalanceQuery["text"] = "集保庫存"
        self.buttonGetBalanceQuery["command"] = self.buttonGetBalanceQuery_Click
        self.buttonGetBalanceQuery.grid(row=1, column=1)
            # Entry
        tk.Label(self, text="商品代碼，代空為全部商品回傳").grid(row=1, column=2)
        self.bstrStockNo = tk.Entry(self)
        self.bstrStockNo.grid(row=1, column=3)

        # buttonGetMarginPurchaseAmountLimit 
        self.buttonGetMarginPurchaseAmountLimit = tk.Button(self)
        self.buttonGetMarginPurchaseAmountLimit["text"] = "資券配額"
        self.buttonGetMarginPurchaseAmountLimit["command"] = self.buttonGetMarginPurchaseAmountLimit_Click
        self.buttonGetMarginPurchaseAmountLimit.grid(row=2, column=1)
            # Entry
        tk.Label(self, text="商品代碼，代空為全部商品回傳").grid(row=2, column=2)
        self.bstrStockNo = tk.Entry(self)
        self.bstrStockNo.grid(row=2, column=3)

        # comboBoxnTPQueryType 損益
        tk.Label(self, text = "種類").grid(row=3, column=1)

        self.comboBoxnTPQueryType = ttk.Combobox(self, state='readonly')
        self.comboBoxnTPQueryType['values'] = Config.comboBoxnTPQueryType
        self.comboBoxnTPQueryType.grid(row=3, column=2)

        def on_comboBoxnTPQueryType(event):
            if self.comboBoxnTPQueryType.get() == "未實現損益":
                self.comboBoxnFunc['values'] = Config.comboBoxnFunc0
            elif self.comboBoxnTPQueryType.get() == "已實現損益":
                self.comboBoxnFunc['values'] = Config.comboBoxnFunc1
            else:
                self.comboBoxnFunc['values'] = Config.comboBoxnFunc2
        self.comboBoxnTPQueryType.bind("<<ComboboxSelected>>", on_comboBoxnTPQueryType)

        global comboBoxnTPQueryType
        comboBoxnTPQueryType = self.comboBoxnTPQueryType

        # comboBoxnFunc
        self.comboBoxnFunc = ttk.Combobox(self, state='readonly')
        self.comboBoxnFunc.grid(row=3, column=3)

        def on_comboBoxnFunc(event):
            if self.comboBoxnTPQueryType.get() == "未實現損益" and self.comboBoxnFunc.get() == "1:明細":
                self.comboBoxbstrTradeType['values'] = Config.comboBoxbstrTradeType0
            elif self.comboBoxnTPQueryType.get() == "已實現損益" and self.comboBoxnFunc.get() == "1:明細":
                self.comboBoxbstrTradeType['values'] = Config.comboBoxbstrTradeType1
            else:
                self.comboBoxbstrTradeType['values'] = " "
               
        self.comboBoxnFunc.bind("<<ComboboxSelected>>", on_comboBoxnFunc)

        global comboBoxnFunc
        comboBoxnFunc = self.comboBoxnFunc

        # comboBoxbstrTradeType
        self.comboBoxbstrTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxbstrTradeType.grid(row=3, column=4)

        global comboBoxbstrTradeType
        comboBoxbstrTradeType = self.comboBoxbstrTradeType

        # textBoxbstrStockNo3
        tk.Label(self, text = "商品代碼").grid(row=3, column=5)
            #輸入框
        self.textBoxbstrStockNo3 = tk.Entry(self)
        self.textBoxbstrStockNo3.grid(row=3, column=6)

        global textBoxbstrStockNo3
        textBoxbstrStockNo3 = self.textBoxbstrStockNo3

        # textBoxbstrStartDate
        tk.Label(self, text = "起始日年月日").grid(row=3, column=7)
            #輸入框
        self.textBoxbstrStartDate = tk.Entry(self)
        self.textBoxbstrStartDate.grid(row=3, column=8)

        global textBoxbstrStartDate
        textBoxbstrStartDate = self.textBoxbstrStartDate

        # textBoxbstrEndDate
        tk.Label(self, text = "結束日年月日").grid(row=3, column=9)
            #輸入框
        self.textBoxbstrEndDate = tk.Entry(self)
        self.textBoxbstrEndDate.grid(row=3, column=10)

        global textBoxbstrEndDate
        textBoxbstrEndDate = self.textBoxbstrEndDate

        # textBoxbstrBookNo
        tk.Label(self, text = "委託書號").grid(row=3, column=11)
            #輸入框
        self.textBoxbstrBookNo = tk.Entry(self)
        self.textBoxbstrBookNo.grid(row=3, column=12)

        global textBoxbstrBookNo
        textBoxbstrBookNo = self.textBoxbstrBookNo

        # textBoxbstrSeqNo
        tk.Label(self, text = "委託序號").grid(row=3, column=13)
            #輸入框
        self.textBoxbstrSeqNo = tk.Entry(self)
        self.textBoxbstrSeqNo.grid(row=3, column=14)

        global textBoxbstrSeqNo
        textBoxbstrSeqNo = self.textBoxbstrSeqNo
        
        # buttonGetProfitLossGWReport
        self.buttonGetProfitLossGWReport = tk.Button(self)
        self.buttonGetProfitLossGWReport["text"] = "損益試算"
        self.buttonGetProfitLossGWReport["command"] = self.buttonGetProfitLossGWReport_Click
        self.buttonGetProfitLossGWReport.grid(row=3, column=15)

    def buttonGetRealBalanceReport_Click(self):
        nCode = m_pSKOrder.GetRealBalanceReport(comboBoxUserID.get(), comboBoxAccount.get())

        msg = "【GetRealBalanceReport】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    def buttonGetBalanceQuery_Click(self):
        nCode = m_pSKOrder.GetBalanceQuery(comboBoxUserID.get(), comboBoxAccount.get(), self.bstrStockNo.get())

        msg = "【GetBalanceQuery】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonGetMarginPurchaseAmountLimit_Click(self):
        nCode = m_pSKOrder.GetMarginPurchaseAmountLimit(comboBoxUserID.get(), comboBoxAccount.get(), self.bstrStockNo.get())

        msg = "【GetMarginPurchaseAmountLimit】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonGetProfitLossGWReport_Click(self):
        pPLGWQuery = sk.TSPROFITLOSSGWQUERY()

        pPLGWQuery.bstrFullAccount = comboBoxAccount.get()
        if comboBoxnTPQueryType.get() == "未實現損益":
            pPLGWQuery.nTPQueryType = 0
            
        elif comboBoxnTPQueryType.get() == "已實現損益":
            pPLGWQuery.nTPQueryType = 1
        else:
            pPLGWQuery.nTPQueryType = 2
            if comboBoxnFunc.get() == "1:彙總":
                pPLGWQuery.nFunc = 1
            elif comboBoxnFunc.get() == "2:明細":
                pPLGWQuery.nFunc = 2
        
        if comboBoxnFunc.get() == "0:彙總":
            pPLGWQuery.nFunc = 0
        elif comboBoxnFunc.get() == "1:明細":
            pPLGWQuery.nFunc = 1
        elif comboBoxnFunc.get() == "2:投資總額":
            pPLGWQuery.nFunc = 2
        elif comboBoxnFunc.get() == "3:彙總(依股票代號)":
            pPLGWQuery.nFunc = 3
        
        pPLGWQuery.bstrStockNo = textBoxbstrStockNo3.get()

        if comboBoxbstrTradeType.get() == "0:現股":
            pPLGWQuery.bstrTradeType = "0"
        elif comboBoxbstrTradeType.get() == "1:融資(代)":
            pPLGWQuery.bstrTradeType = "1"
        elif comboBoxbstrTradeType.get() == "2:融券(代)":
            pPLGWQuery.bstrTradeType = "2"
        elif comboBoxbstrTradeType.get() == "3:融資(自)":
            pPLGWQuery.bstrTradeType = "3"
        elif comboBoxbstrTradeType.get() == "4:融券(自)":
            pPLGWQuery.bstrTradeType = "4"    
        elif comboBoxbstrTradeType.get() == "8:券差":
            pPLGWQuery.bstrTradeType = "8"
        elif comboBoxbstrTradeType.get() == "9:無券賣出":
            pPLGWQuery.bstrTradeType = "9"

        pPLGWQuery.bstrStartDate = textBoxbstrStartDate.get()
        pPLGWQuery.bstrEndDate = textBoxbstrEndDate.get()
        pPLGWQuery.bstrBookNo = textBoxbstrBookNo.get()
        pPLGWQuery.bstrSeqNo = textBoxbstrSeqNo.get()

        nCode = m_pSKOrder.GetProfitLossGWReport(comboBoxUserID.get(), pPLGWQuery)

        msg = "【GetProfitLossGWReport】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

######################################################################################################################################
#SendForm
class SendForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
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

        # textBoxStockID
        tk.Label(self, text = "股票代號", fg = "red").grid(row=0, column=1)
            #輸入框
        self.textBoxStockID = tk.Entry(self)
        self.textBoxStockID.grid(row=0, column=2)

        global textBoxStockID
        textBoxStockID = self.textBoxStockID

        # comboBoxPrime
        tk.Label(self, text = "上市上櫃/興櫃").grid(row=1, column=1)
            #輸入框
        self.comboBoxPrime = ttk.Combobox(self, state='readonly')
        self.comboBoxPrime['values'] = Config.comboBoxPrime
        self.comboBoxPrime.grid(row=1, column=2)

        global comboBoxPrime
        comboBoxPrime = self.comboBoxPrime

        # comboBoxPeriod
        tk.Label(self, text = "盤中/盤後/零股").grid(row=2, column=1)
            #輸入框
        self.comboBoxPeriod = ttk.Combobox(self, state='readonly')
        self.comboBoxPeriod['values'] = Config.comboBoxPeriod
        self.comboBoxPeriod.grid(row=2, column=2)

        global comboBoxPeriod
        comboBoxPeriod = self.comboBoxPeriod

        # textBoxnQty
        tk.Label(self, text = "整股(張)/零股(股數)", fg = "red").grid(row=3, column=1)
            #輸入框
        self.textBoxnQty = tk.Entry(self)
        self.textBoxnQty.grid(row=3, column=2)

        global textBoxnQty
        textBoxnQty = self.textBoxnQty

        # comboBoxFlag
        tk.Label(self, text = "現股/融資/融券/無券").grid(row=4, column=1)
            #輸入框
        self.comboBoxFlag = ttk.Combobox(self, state='readonly')
        self.comboBoxFlag['values'] = Config.comboBoxFlag
        self.comboBoxFlag.grid(row=4, column=2)

        global comboBoxFlag
        comboBoxFlag = self.comboBoxFlag

        # comboBoxnTradeType
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=5, column=1)
            #輸入框
        self.comboBoxnTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxnTradeType['values'] = Config.comboBoxnTradeType
        self.comboBoxnTradeType.grid(row=5, column=2)

        global comboBoxnTradeType
        comboBoxnTradeType = self.comboBoxnTradeType

        # comboBoxnSpecialTradeType
        tk.Label(self, text = "市價/限價").grid(row=6, column=1)
            #輸入框
        self.comboBoxnSpecialTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxnSpecialTradeType['values'] = Config.comboBoxnSpecialTradeType
        self.comboBoxnSpecialTradeType.grid(row=6, column=2)

        global comboBoxnSpecialTradeType
        comboBoxnSpecialTradeType = self.comboBoxnSpecialTradeType

        # textBoxbstrPrice
        tk.Label(self, text = "委託價", fg = "red").grid(row=7, column=1)
            #輸入框
        self.textBoxbstrPrice = tk.Entry(self)
        self.textBoxbstrPrice.grid(row=7, column=2)

        global textBoxbstrPrice
        textBoxbstrPrice = self.textBoxbstrPrice
        
        # comboBoxBuySell
        tk.Label(self, text = "買進/賣出", fg = "red").grid(row=8, column=1)

            #輸入框
        self.comboBoxBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxBuySell['values'] = Config.comboBoxBuySell
        self.comboBoxBuySell.grid(row=8, column=2)

        global comboBoxBuySell
        comboBoxBuySell = self.comboBoxBuySell

        # buttonSendStockOddLotOrder
        self.buttonSendStockOddLotOrder = tk.Button(self)
        self.buttonSendStockOddLotOrder["text"] = "盤中零股送出"
        self.buttonSendStockOddLotOrder["fg"] = "red"  # 設置文字顏色變red
        self.buttonSendStockOddLotOrder["command"] = self.buttonSendStockOddLotOrder_Click
        self.buttonSendStockOddLotOrder.grid(row=9, column=1)

        # buttonSendStockOrder
        self.buttonSendStockOrder = tk.Button(self)
        self.buttonSendStockOrder["text"] = "證券送出"
        self.buttonSendStockOrder["command"] = self.buttonSendStockOrder_Click
        self.buttonSendStockOrder.grid(row=9, column=2)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False

    def buttonSendStockOddLotOrder_Click(self):
        pOrder = sk.STOCKORDER()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxStockID.get()
        pOrder.sPeriod = 4 # 盤中零股
        pOrder.sFlag = 0 # 現股

        if comboBoxBuySell.get() == "買進":
            pOrder.sBuySell = 0
        elif comboBoxBuySell.get() == "賣出":
            pOrder.sBuySell = 1

        pOrder.bstrPrice = textBoxbstrPrice.get()
        pOrder.nQty = int(textBoxnQty.get())

        bstrMessage,nCode= m_pSKOrder.SendStockOddLotOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockOddLotOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonSendStockOrder_Click(self):
        pOrder = sk.STOCKORDER()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxStockID.get()

        if comboBoxPrime.get() == "上市上櫃":
            pOrder.sPrime = 0
        elif comboBoxPrime.get() == "興櫃":
            pOrder.sPrime = 1
        
        if comboBoxPeriod.get() == "盤中":
            pOrder.sPeriod = 0
        elif comboBoxPeriod.get() == "盤後":
            pOrder.sPeriod = 1
        elif comboBoxPeriod.get() == "零股":
            pOrder.sPeriod = 2
        
        if comboBoxFlag.get() == "現股":
            pOrder.sFlag = 0
        elif comboBoxFlag.get() == "融資":
            pOrder.sFlag = 1
        elif comboBoxFlag.get() == "融券":
            pOrder.sFlag = 2
        elif comboBoxFlag.get() == "無券":
            pOrder.sFlag = 3
        
        if comboBoxBuySell.get() == "買進":
            pOrder.sBuySell = 0
        elif comboBoxBuySell.get() == "賣出":
            pOrder.sBuySell = 1

        pOrder.bstrPrice = textBoxbstrPrice.get()
        pOrder.nQty = int(textBoxnQty.get())

        if comboBoxnTradeType.get() == "ROD":
            pOrder.nTradeType = 0
        elif comboBoxnTradeType.get() == "IOC":
            pOrder.nTradeType = 1
        elif comboBoxnTradeType.get() == "FOK":
            pOrder.nTradeType = 2

        if comboBoxnSpecialTradeType.get() == "市價":
            pOrder.nSpecialTradeType = 1
        elif comboBoxnSpecialTradeType.get() == "限價":
            pOrder.nSpecialTradeType = 2

        bstrMessage,nCode= m_pSKOrder.SendStockOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendStockOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#UpdateForm
class UpdateForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
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

        # textBoxSeqNo
        tk.Label(self, text = "請輸入委託序號").grid(row=0, column=1)
            #輸入框
        self.textBoxSeqNo = tk.Entry(self)
        self.textBoxSeqNo.grid(row=0, column=2)

        global textBoxSeqNo
        textBoxSeqNo = self.textBoxSeqNo

        # textBoxBookNo
        tk.Label(self, text = "請輸入委託書號").grid(row=1, column=1)
            #輸入框
        self.textBoxBookNo = tk.Entry(self)
        self.textBoxBookNo.grid(row=1, column=2)

        global textBoxBookNo
        textBoxBookNo = self.textBoxBookNo

        # textBoxCancelOrderByStockNo
        tk.Label(self, text = "請輸入商品代號(空白就刪除所有委託)").grid(row=2, column=1)
            #輸入框
        self.textBoxCancelOrderByStockNo = tk.Entry(self)
        self.textBoxCancelOrderByStockNo.grid(row=2, column=2)

        global textBoxCancelOrderByStockNo
        textBoxCancelOrderByStockNo = self.textBoxCancelOrderByStockNo

        # comboBoxCancelOrderByStockNoAdvanceBuySell
        tk.Label(self, text = "買/賣/無").grid(row=2, column=3)
            #輸入框
        self.comboBoxCancelOrderByStockNoAdvanceBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxCancelOrderByStockNoAdvanceBuySell['values'] = Config.comboBoxCancelOrderByStockNoAdvanceBuySell
        self.comboBoxCancelOrderByStockNoAdvanceBuySell.grid(row=2, column=4)

        # textBoxCancelOrderByStockNoAdvancePrice
        tk.Label(self, text = "委託價格").grid(row=2, column=5)
            #輸入框
        self.textBoxCancelOrderByStockNoAdvancePrice = tk.Entry(self)
        self.textBoxCancelOrderByStockNoAdvancePrice.grid(row=2, column=6)

        global textBoxCancelOrderByStockNoAdvancePrice
        textBoxCancelOrderByStockNoAdvancePrice = self.textBoxCancelOrderByStockNoAdvancePrice

        global comboBoxCancelOrderByStockNoAdvanceBuySell
        comboBoxCancelOrderByStockNoAdvanceBuySell = self.comboBoxCancelOrderByStockNoAdvanceBuySell

        # buttonCancelOrderBySeqNo
        self.buttonCancelOrderBySeqNo = tk.Button(self)
        self.buttonCancelOrderBySeqNo["text"] = "刪單(序號)"
        self.buttonCancelOrderBySeqNo["command"] = self.buttonCancelOrderBySeqNo_Click
        self.buttonCancelOrderBySeqNo.grid(row=3, column=1)

        # buttonCancelOrderByBookNo
        self.buttonCancelOrderByBookNo = tk.Button(self)
        self.buttonCancelOrderByBookNo["text"] = "刪單(書號)"
        self.buttonCancelOrderByBookNo["command"] = self.buttonCancelOrderByBookNo_Click
        self.buttonCancelOrderByBookNo.grid(row=3, column=2)

        # buttonCancelOrderByStockNo
        self.buttonCancelOrderByStockNo = tk.Button(self)
        self.buttonCancelOrderByStockNo["text"] = "刪單(代號)"
        self.buttonCancelOrderByStockNo["command"] = self.buttonCancelOrderByStockNo_Click
        self.buttonCancelOrderByStockNo.grid(row=3, column=3)

        # textBoxStockDecreaseQty
        tk.Label(self, text = "請輸入減少數量").grid(row=4, column=1)
            #輸入框
        self.textBoxStockDecreaseQty = tk.Entry(self)
        self.textBoxStockDecreaseQty.grid(row=4, column=2)

        global textBoxStockDecreaseQty
        textBoxStockDecreaseQty = self.textBoxStockDecreaseQty

        # buttonDecreaseOrderBySeqNo
        self.buttonDecreaseOrderBySeqNo = tk.Button(self)
        self.buttonDecreaseOrderBySeqNo["text"] = "減量(序號)"
        self.buttonDecreaseOrderBySeqNo["command"] = self.buttonDecreaseOrderBySeqNo_Click
        self.buttonDecreaseOrderBySeqNo.grid(row=5, column=1)
        
        # textBoxPrice
        tk.Label(self, text = "請輸入修改價格").grid(row=6, column=1)
            #輸入框
        self.textBoxPrice = tk.Entry(self)
        self.textBoxPrice.grid(row=6, column=2)

        global textBoxPrice
        textBoxPrice = self.textBoxPrice

        # comboBoxTradeType
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=7, column=1)
            #輸入框
        self.comboBoxTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxTradeType['values'] = Config.comboBoxTradeType
        self.comboBoxTradeType.grid(row=7, column=2)

        global comboBoxTradeType
        comboBoxTradeType = self.comboBoxTradeType

        # comboBoxMarketSymbol
        tk.Label(self, text = "請輸入市場(※書號)").grid(row=8, column=1)
            #輸入框
        self.comboBoxMarketSymbol = ttk.Combobox(self, state='readonly')
        self.comboBoxMarketSymbol['values'] = Config.comboBoxMarketSymbol
        self.comboBoxMarketSymbol.grid(row=8, column=2)

        global comboBoxMarketSymbol
        comboBoxMarketSymbol = self.comboBoxMarketSymbol

        # buttonCorrectPriceBySeqNo
        self.buttonCorrectPriceBySeqNo = tk.Button(self)
        self.buttonCorrectPriceBySeqNo["text"] = "改價(序號)"
        self.buttonCorrectPriceBySeqNo["command"] = self.buttonCorrectPriceBySeqNo_Click
        self.buttonCorrectPriceBySeqNo.grid(row=9, column=1)

        # buttonCorrectPriceByBookNo
        self.buttonCorrectPriceByBookNo = tk.Button(self)
        self.buttonCorrectPriceByBookNo["text"] = "改價(書號)"
        self.buttonCorrectPriceByBookNo["command"] = self.buttonCorrectPriceByBookNo_Click
        self.buttonCorrectPriceByBookNo.grid(row=9, column=2)

        # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
            
    def buttonCancelOrderBySeqNo_Click(self):
        bstrMessage,nCode= m_pSKOrder.CancelOrderBySeqNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxSeqNo.get())

        msg = "【CancelOrderBySeqNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonCancelOrderByBookNo_Click(self):
        bstrMessage,nCode= m_pSKOrder.CancelOrderByBookNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxBookNo.get())

        msg = "【CancelOrderByBookNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonCancelOrderByStockNo_Click(self):

        if comboBoxCancelOrderByStockNoAdvanceBuySell.get() == "無":
            bstrMessage,nCode= m_pSKOrder.CancelOrderByStockNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxCancelOrderByStockNo.get())
            msg = "【CancelOrderByStockNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        elif  comboBoxCancelOrderByStockNoAdvanceBuySell.get() == "買":
            nBuySell = 0
            bstrMessage,nCode= m_pSKOrder.CancelOrderByStockNoAdvance(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxCancelOrderByStockNo.get(), nBuySell, textBoxCancelOrderByStockNoAdvancePrice.get())
            msg = "【CancelOrderByStockNoAdvance】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
            nBuySell = 1
            bstrMessage,nCode= m_pSKOrder.CancelOrderByStockNoAdvance(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxCancelOrderByStockNo.get(), nBuySell, textBoxCancelOrderByStockNoAdvancePrice.get())
            msg = "【CancelOrderByStockNoAdvance】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage

        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonDecreaseOrderBySeqNo_Click(self):
        bstrMessage,nCode= m_pSKOrder.DecreaseOrderBySeqNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxSeqNo.get(), int(textBoxStockDecreaseQty.get()))

        msg = "【DecreaseOrderBySeqNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonCorrectPriceBySeqNo_Click(self):

        if comboBoxTradeType.get() == "0:ROD":
            nTradeType = 0
        elif  comboBoxTradeType.get() == "1:IOC":
            nTradeType = 1
        else:
            nTradeType = 2 # FOK

        bstrMessage,nCode= m_pSKOrder.CorrectPriceBySeqNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxSeqNo.get(), textBoxPrice.get(), nTradeType)

        msg = "【CorrectPriceBySeqNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonCorrectPriceByBookNo_Click(self):
        
        if comboBoxMarketSymbol.get() == "TS:證券":
            bstrMarketSymbol = "TS"
        elif  comboBoxMarketSymbol.get() == "TF:期貨":
            bstrMarketSymbol = "TF"
        else:
            bstrMarketSymbol = "TO" # TO:選擇權
    
        if comboBoxTradeType.get() == "0:ROD":
            nTradeType = 0
        elif  comboBoxTradeType.get() == "1:IOC":
            nTradeType = 1
        else:
            nTradeType = 2 # FOK

        bstrMessage,nCode= m_pSKOrder.CorrectPriceByBookNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), bstrMarketSymbol, textBoxSeqNo.get(), textBoxPrice.get(), nTradeType)

        msg = "【CorrectPriceByBookNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#SendProxyForm
class SendProxyForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):
        # textBoxStockIDProxy
        tk.Label(self, text = "股票代號").grid(row=0, column=1)
            #輸入框
        self.textBoxStockIDProxy = tk.Entry(self)
        self.textBoxStockIDProxy.grid(row=0, column=2)

        global textBoxStockIDProxy
        textBoxStockIDProxy = self.textBoxStockIDProxy

        # comboBoxPeriodProxy
        tk.Label(self, text = "盤中/盤後/零股").grid(row=1, column=1)
            #輸入框
        self.comboBoxPeriodProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxPeriodProxy['values'] = Config.comboBoxPeriodProxy
        self.comboBoxPeriodProxy.grid(row=1, column=2)

        global comboBoxPeriodProxy
        comboBoxPeriodProxy = self.comboBoxPeriodProxy

        # textBoxnQtyProxy
        tk.Label(self, text = "股數").grid(row=2, column=1)
            #輸入框
        self.textBoxnQtyProxy = tk.Entry(self)
        self.textBoxnQtyProxy.grid(row=2, column=2)

        global textBoxnQtyProxy
        textBoxnQtyProxy = self.textBoxnQtyProxy

        # comboBoxbstrOrderTypeProxy
        tk.Label(self, text = "現股/融資/融券/無券").grid(row=3, column=1)
            #輸入框
        self.comboBoxbstrOrderTypeProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxbstrOrderTypeProxy['values'] = Config.comboBoxbstrOrderTypeProxy
        self.comboBoxbstrOrderTypeProxy.grid(row=3, column=2)

        global comboBoxbstrOrderTypeProxy
        comboBoxbstrOrderTypeProxy = self.comboBoxbstrOrderTypeProxy

        # comboBoxnTradeTypeProxy
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=4, column=1)
            #輸入框
        self.comboBoxnTradeTypeProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxnTradeTypeProxy['values'] = Config.comboBoxnTradeTypeProxy
        self.comboBoxnTradeTypeProxy.grid(row=4, column=2)

        global comboBoxnTradeTypeProxy
        comboBoxnTradeTypeProxy = self.comboBoxnTradeTypeProxy

        # comboBoxnSpecialTradeTypeProxy
        tk.Label(self, text = "市價/限價").grid(row=5, column=1)
            #輸入框
        self.comboBoxnSpecialTradeTypeProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxnSpecialTradeTypeProxy['values'] = Config.comboBoxnSpecialTradeTypeProxy
        self.comboBoxnSpecialTradeTypeProxy.grid(row=5, column=2)

        global comboBoxnSpecialTradeTypeProxy
        comboBoxnSpecialTradeTypeProxy = self.comboBoxnSpecialTradeTypeProxy

        # textBoxbstrPriceProxy
        tk.Label(self, text = "委託價").grid(row=6, column=1)
            #輸入框
        self.textBoxbstrPriceProxy = tk.Entry(self)
        self.textBoxbstrPriceProxy.grid(row=6, column=2)

        global textBoxbstrPriceProxy
        textBoxbstrPriceProxy = self.textBoxbstrPriceProxy

        # comboBoxnPriceMarkProxy
        tk.Label(self, text = "價格旗標").grid(row=7, column=1)
            #輸入框
        self.comboBoxnPriceMarkProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxnPriceMarkProxy['values'] = Config.comboBoxnPriceMarkProxy
        self.comboBoxnPriceMarkProxy.grid(row=7, column=2)

        global comboBoxnPriceMarkProxy
        comboBoxnPriceMarkProxy = self.comboBoxnPriceMarkProxy

        # buttonSendStockProxyOrder
        self.buttonSendStockProxyOrder = tk.Button(self)
        self.buttonSendStockProxyOrder["text"] = "證券送出"
        self.buttonSendStockProxyOrder["command"] = self.buttonSendStockProxyOrder_Click
        self.buttonSendStockProxyOrder.grid(row=8, column=2)

    def buttonSendStockProxyOrder_Click(self):
        pSTOCKPROXYORDER = sk.STOCKPROXYORDER()
        pSTOCKPROXYORDER.bstrFullAccount = comboBoxAccount.get()
        pSTOCKPROXYORDER.bstrStockNo = textBoxStockIDProxy.get()

        if comboBoxbstrOrderTypeProxy.get() == "現股買進":
            pSTOCKPROXYORDER.bstrOrderType = "1"
        elif comboBoxbstrOrderTypeProxy.get() == "現股賣出":
            pSTOCKPROXYORDER.bstrOrderType = "2"
        elif comboBoxbstrOrderTypeProxy.get() == "融資買進":
            pSTOCKPROXYORDER.bstrOrderType = "3"
        elif comboBoxbstrOrderTypeProxy.get() == "融資賣出":
            pSTOCKPROXYORDER.bstrOrderType = "4"
        elif comboBoxbstrOrderTypeProxy.get() == "融券買進":
            pSTOCKPROXYORDER.bstrOrderType = "5"
        elif comboBoxbstrOrderTypeProxy.get() == "融券賣出":
            pSTOCKPROXYORDER.bstrOrderType = "6"
        elif comboBoxbstrOrderTypeProxy.get() == "無券賣出":
            pSTOCKPROXYORDER.bstrOrderType = "7"

        if comboBoxnSpecialTradeTypeProxy.get() == "市價":
            pSTOCKPROXYORDER.nSpecialTradeType = 1
        elif comboBoxnSpecialTradeTypeProxy.get() == "限價":
            pSTOCKPROXYORDER.nSpecialTradeType = 2

        if comboBoxPeriodProxy.get() == "盤中":
            pSTOCKPROXYORDER.nPeriod = 0
        elif comboBoxPeriodProxy.get() == "零股":
            pSTOCKPROXYORDER.nPeriod = 1
        elif comboBoxPeriodProxy.get() == "盤後交易":
            pSTOCKPROXYORDER.nPeriod = 2
        elif comboBoxPeriodProxy.get() == "盤中零股":
            pSTOCKPROXYORDER.nPeriod = 3

        pSTOCKPROXYORDER.bstrPrice = textBoxbstrPriceProxy.get()
        pSTOCKPROXYORDER.nQty = int(textBoxnQtyProxy.get())

        if comboBoxnTradeTypeProxy.get() == "ROD":
            pSTOCKPROXYORDER.nTradeType = 0
        elif comboBoxnTradeTypeProxy.get() == "IOC":
            pSTOCKPROXYORDER.nTradeType = 1
        elif comboBoxnTradeTypeProxy.get() == "FOK":
            pSTOCKPROXYORDER.nTradeType = 2
        
        if comboBoxnPriceMarkProxy.get() == "一般定價":
            pSTOCKPROXYORDER.nPriceMark = 0
        elif comboBoxnPriceMarkProxy.get() == "前日收盤價":
            pSTOCKPROXYORDER.nPriceMark = 1
        elif comboBoxnPriceMarkProxy.get() == "漲停":
            pSTOCKPROXYORDER.nPriceMark = 2
        elif comboBoxnPriceMarkProxy.get() == "跌停":
            pSTOCKPROXYORDER.nPriceMark = 3
        

        bstrMessage,nCode= m_pSKOrder.SendStockProxyOrder(comboBoxUserID.get(), pSTOCKPROXYORDER)

        if bstrMessage is not None:
             msg = "【SendStockProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
             msg = "【SendStockProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#UpdateProxyForm
class UpdateProxyForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):
        # comboBoxbstrOrderTypeProxyAlter
        tk.Label(self, text = "下單類別").grid(row=0, column=1)
            #輸入框
        self.comboBoxbstrOrderTypeProxyAlter = ttk.Combobox(self, state='readonly')
        self.comboBoxbstrOrderTypeProxyAlter['values'] = Config.comboBoxbstrOrderTypeProxyAlter
        self.comboBoxbstrOrderTypeProxyAlter.grid(row=0, column=2)

        global comboBoxbstrOrderTypeProxyAlter
        comboBoxbstrOrderTypeProxyAlter = self.comboBoxbstrOrderTypeProxyAlter

        # textBoxSeqNoProxyAlter
        tk.Label(self, text = "請輸入委託序號").grid(row=1, column=1)
            #輸入框
        self.textBoxSeqNoProxyAlter = tk.Entry(self)
        self.textBoxSeqNoProxyAlter.grid(row=1, column=2)

        global textBoxSeqNoProxyAlter
        textBoxSeqNoProxyAlter = self.textBoxSeqNoProxyAlter

        # textBoxBookNoProxyAlter
        tk.Label(self, text = "請輸入委託書號").grid(row=2, column=1)
            #輸入框
        self.textBoxBookNoProxyAlter = tk.Entry(self)
        self.textBoxBookNoProxyAlter.grid(row=2, column=2)

        global textBoxBookNoProxyAlter
        textBoxBookNoProxyAlter = self.textBoxBookNoProxyAlter

        # textBoxCancelOrderByStockNoProxyAlter
        tk.Label(self, text = "委託股票代號").grid(row=3, column=1)
            #輸入框
        self.textBoxCancelOrderByStockNoProxyAlter = tk.Entry(self)
        self.textBoxCancelOrderByStockNoProxyAlter.grid(row=3, column=2)

        global textBoxCancelOrderByStockNoProxyAlter
        textBoxCancelOrderByStockNoProxyAlter = self.textBoxCancelOrderByStockNoProxyAlter

        # comboBoxnSpecialTradeTypeProxyAlter
        tk.Label(self, text = "市價/限價").grid(row=4, column=1)
            #輸入框
        self.comboBoxnSpecialTradeTypeProxyAlter = ttk.Combobox(self, state='readonly')
        self.comboBoxnSpecialTradeTypeProxyAlter['values'] = Config.comboBoxnSpecialTradeTypeProxyAlter
        self.comboBoxnSpecialTradeTypeProxyAlter.grid(row=4, column=2)

        global comboBoxnSpecialTradeTypeProxyAlter
        comboBoxnSpecialTradeTypeProxyAlter = self.comboBoxnSpecialTradeTypeProxyAlter

        # comboBoxPeriodProxyAlter
        tk.Label(self, text = "盤中/盤後/零股").grid(row=5, column=1)
            #輸入框
        self.comboBoxPeriodProxyAlter = ttk.Combobox(self, state='readonly')
        self.comboBoxPeriodProxyAlter['values'] = Config.comboBoxPeriodProxyAlter
        self.comboBoxPeriodProxyAlter.grid(row=5, column=2)

        global comboBoxPeriodProxyAlter
        comboBoxPeriodProxyAlter = self.comboBoxPeriodProxyAlter

        # textBoxStockDecreaseQtyProxyAlter
        tk.Label(self, text = "請輸入減少數量").grid(row=6, column=1)
            #輸入框
        self.textBoxStockDecreaseQtyProxyAlter = tk.Entry(self)
        self.textBoxStockDecreaseQtyProxyAlter.grid(row=6, column=2)

        global textBoxStockDecreaseQtyProxyAlter
        textBoxStockDecreaseQtyProxyAlter = self.textBoxStockDecreaseQtyProxyAlter

        # textBoxPriceProxyAlter
        tk.Label(self, text = "請輸入修改價格").grid(row=7, column=1)
            #輸入框
        self.textBoxPriceProxyAlter = tk.Entry(self)
        self.textBoxPriceProxyAlter.grid(row=7, column=2)

        global textBoxPriceProxyAlter
        textBoxPriceProxyAlter = self.textBoxPriceProxyAlter

        # comboBoxTradeTypeProxyAlter
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=8, column=1)
            #輸入框
        self.comboBoxTradeTypeProxyAlter = ttk.Combobox(self, state='readonly')
        self.comboBoxTradeTypeProxyAlter['values'] = Config.comboBoxTradeTypeProxyAlter
        self.comboBoxTradeTypeProxyAlter.grid(row=8, column=2)

        global comboBoxTradeTypeProxyAlter
        comboBoxTradeTypeProxyAlter = self.comboBoxTradeTypeProxyAlter

        # comboBoxnPriceMarkProxyAlter
        tk.Label(self, text = "價格旗標").grid(row=9, column=1)
            #輸入框
        self.comboBoxnPriceMarkProxyAlter = ttk.Combobox(self, state='readonly')
        self.comboBoxnPriceMarkProxyAlter['values'] = Config.comboBoxnPriceMarkProxyAlter
        self.comboBoxnPriceMarkProxyAlter.grid(row=9, column=2)

        global comboBoxnPriceMarkProxyAlter
        comboBoxnPriceMarkProxyAlter = self.comboBoxnPriceMarkProxyAlter

        # buttonSendStockProxyAlter
        self.buttonSendStockProxyAlter = tk.Button(self)
        self.buttonSendStockProxyAlter["text"] = "刪改單送出"
        self.buttonSendStockProxyAlter["command"] = self.buttonSendStockProxyAlter_Click
        self.buttonSendStockProxyAlter.grid(row=10, column=2)
    
    def buttonSendStockProxyAlter_Click(self):
        pSTOCKPROXYORDER = sk.STOCKPROXYORDER()

        pSTOCKPROXYORDER.bstrFullAccount = comboBoxAccount.get()
        pSTOCKPROXYORDER.bstrStockNo = textBoxCancelOrderByStockNoProxyAlter.get()

        if comboBoxbstrOrderTypeProxyAlter.get() == "刪單":
            pSTOCKPROXYORDER.bstrOrderType = "0"
        elif comboBoxbstrOrderTypeProxyAlter.get() == "改量":
            pSTOCKPROXYORDER.bstrOrderType = "1"
        elif comboBoxbstrOrderTypeProxyAlter.get() == "改價":
            pSTOCKPROXYORDER.bstrOrderType = "2"

        if comboBoxnSpecialTradeTypeProxyAlter.get() == "市價":
            pSTOCKPROXYORDER.nSpecialTradeType = 1
        elif comboBoxnSpecialTradeTypeProxyAlter.get() == "限價":
            pSTOCKPROXYORDER.nSpecialTradeType = 2

        if comboBoxPeriodProxyAlter.get() == "盤中":
            pSTOCKPROXYORDER.nPeriod = 0
        elif comboBoxPeriodProxyAlter.get() == "零股":
            pSTOCKPROXYORDER.nPeriod = 1
        elif comboBoxPeriodProxyAlter.get() == "盤後交易":
            pSTOCKPROXYORDER.nPeriod = 2
        elif comboBoxPeriodProxyAlter.get() == "盤中零股":
            pSTOCKPROXYORDER.nPeriod = 3

        pSTOCKPROXYORDER.bstrPrice = textBoxPriceProxyAlter.get()
        pSTOCKPROXYORDER.nQty = int(textBoxStockDecreaseQtyProxyAlter.get())

        if comboBoxTradeTypeProxyAlter.get() == "0:ROD":
            pSTOCKPROXYORDER.nTradeType = 0
        elif comboBoxTradeTypeProxyAlter.get() == "1:IOC":
            pSTOCKPROXYORDER.nTradeType = 1
        elif comboBoxTradeTypeProxyAlter.get() == "2:FOK":
            pSTOCKPROXYORDER.nTradeType = 2
        
        if comboBoxnPriceMarkProxyAlter.get() == "一般定價":
            pSTOCKPROXYORDER.nPriceMark = 0
        elif comboBoxnPriceMarkProxyAlter.get() == "前日收盤價":
            pSTOCKPROXYORDER.nPriceMark = 1
        elif comboBoxnPriceMarkProxyAlter.get() == "漲停":
            pSTOCKPROXYORDER.nPriceMark = 2
        elif comboBoxnPriceMarkProxyAlter.get() == "跌停":
            pSTOCKPROXYORDER.nPriceMark = 3
        
        pSTOCKPROXYORDER.bstrBookNo = textBoxBookNoProxyAlter.get()
        pSTOCKPROXYORDER.bstrSeqNo = textBoxSeqNoProxyAlter.get()

        bstrMessage,nCode= m_pSKOrder.SendStockProxyAlter(comboBoxUserID.get(), pSTOCKPROXYORDER)

        if bstrMessage is not None:
             msg = "【SendStockProxyAlter】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
             msg = "【SendStockProxyAlter】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
#==========================================
#定義彈出視窗
def popup_window_Read():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Read")

    # 建立 Frame 作為 ReadForm，並添加到彈出窗口
    popup_ReadForm = ReadForm(popup)
    popup_ReadForm.pack(fill=tk.BOTH, expand=True)

def popup_window_Send():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Send")

    # 建立 Frame 作為 SendForm，並添加到彈出窗口
    popup_SendForm = SendForm(popup)
    popup_SendForm.pack(fill=tk.BOTH, expand=True)

def popup_window_Update():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Update")

    # 建立 Frame 作為 UpdateForm，並添加到彈出窗口
    popup_UpdateForm = UpdateForm(popup)
    popup_UpdateForm.pack(fill=tk.BOTH, expand=True)

def popup_window_SendProxy():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("SendProxy")

    # 建立 Frame 作為 SendProxyForm，並添加到彈出窗口
    popup_SendProxyForm = SendProxyForm(popup)
    popup_SendProxyForm.pack(fill=tk.BOTH, expand=True)

def popup_window_UpdateProxy():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("UpdateProxy")

    # 建立 Frame 作為 UpdateProxyForm，並添加到彈出窗口
    popup_UpdateProxyForm = UpdateProxyForm(popup)
    popup_UpdateProxyForm.pack(fill=tk.BOTH, expand=True)

def popup_window_AvgCost():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("AvgCost")

    # 建立 Frame 作為 OffSetForm，並添加到彈出窗口
    popup_AvgCostForm = AvgCostForm(popup)
    popup_AvgCostForm.pack(fill=tk.BOTH, expand=True)
    
#開啟Tk視窗
if __name__ == '__main__':
    #建立主視窗
    root = tk.Tk()
    root.title("TSOrder")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)


    # 開啟Read視窗的按鈕
    popup_button_Read = tk.Button(root, text="查詢", command=popup_window_Read)
    popup_button_Read.grid(row = 1, column= 0)

    # 開啟Send視窗的按鈕
    popup_button_Send = tk.Button(root, text="一般下單", command=popup_window_Send)
    popup_button_Send.grid(row = 2, column= 0)

    # 開啟Update視窗的按鈕
    popup_button_Update = tk.Button(root, text="一般刪改單", command=popup_window_Update)
    popup_button_Update.grid(row = 3, column= 0)

    # 開啟SendProxy視窗的按鈕
    popup_button_SendProxy = tk.Button(root, text="Proxy下單", command=popup_window_SendProxy)
    popup_button_SendProxy.grid(row = 4, column= 0)

    # 開啟UpdateProxy視窗的按鈕
    popup_button_UpdateProxy = tk.Button(root, text="Proxy刪改單", command=popup_window_UpdateProxy)
    popup_button_UpdateProxy.grid(row = 5, column= 0)

    # 開啟AvgCost視窗的按鈕
    popup_button_OffSet = tk.Button(root, text="昨日未沖銷查詢", command=popup_window_AvgCost)
    popup_button_OffSet.grid(row = 6, column= 0)


    root.mainloop()

#==========================================
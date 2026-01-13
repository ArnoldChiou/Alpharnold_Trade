# API com元件初始化
import comtypes.client
comtypes.client.GetModule(r'C:\Trading\TradeAPI_MA_TX\units\SKCOM.dll')
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
import Config

# 全域變數
dictUserID = {}
dictUserID["更新帳號"] = ["無"]
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

# CenterLib 事件
class SKCenterLibEvent:
    # 定時Timer通知。每分鐘會由該函式得到一個時間。
    def OnTimer(self, nTime):
        msg = "【OnTimer】" + str(nTime) ;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 同意書狀態通知
    def OnShowAgreement(self, bstrData):
        msg = "【OnShowAgreement】" + bstrData;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # SGX API DMA專線下單連線狀態。
    def OnNotifySGXAPIOrderStatus(self, nStatus, bstrOFAccount):
        msg = "【OnNotifySGXAPIOrderStatus】" + nStatus + "_" +bstrOFAccount
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
SKCenterEvent = SKCenterLibEvent();
SKCenterEventHandler = comtypes.client.GetEvents(m_pSKCenter, SKCenterEvent);

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
    # 透過呼叫 SKOrderLib_TelnetTest 後，資訊由該事件回傳
    def OnTelnetTest(self, bstrData):
        msg = "【OnTelnetTest】" + bstrData;
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
######################################################################################################################################
#OrderForm
class OrderForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # button
        # buttonSKOrderLib_Initialize
        self.buttonSKOrderLib_Initialize = tk.Button(self)
        self.buttonSKOrderLib_Initialize["text"] = "下單物件初始化"
        self.buttonSKOrderLib_Initialize["command"] = self.buttonSKOrderLib_Initialize_Click
        self.buttonSKOrderLib_Initialize.grid(column = 0, row = 1)

        # buttonGetUserAccount
        self.buttonGetUserAccount = tk.Button(self)
        self.buttonGetUserAccount["text"] = "取回交易帳號"
        self.buttonGetUserAccount["command"] = self.buttonGetUserAccount_Click
        self.buttonGetUserAccount.grid(column = 0, row = 2)
        
        # buttonReadCertByID
        self.buttonReadCertByID = tk.Button(self)
        self.buttonReadCertByID["text"] = "讀取憑證"
        self.buttonReadCertByID["command"] = self.buttonReadCertByID_Click
        self.buttonReadCertByID.grid(column = 0, row = 3)

        # buttonSKOrderLib_GetLoginType
        self.buttonSKOrderLib_GetLoginType = tk.Button(self)
        self.buttonSKOrderLib_GetLoginType["text"] = "查詢登入帳號"
        self.buttonSKOrderLib_GetLoginType["command"] = self.buttonSKOrderLib_GetLoginType_Click
        self.buttonSKOrderLib_GetLoginType.grid(column = 2, row = 1)

        # buttonSKOrderLib_GetSpeedyType
        self.buttonSKOrderLib_GetSpeedyType = tk.Button(self)
        self.buttonSKOrderLib_GetSpeedyType["text"] = "查詢下單線路"
        self.buttonSKOrderLib_GetSpeedyType["command"] = self.buttonSKOrderLib_GetSpeedyType_Click
        self.buttonSKOrderLib_GetSpeedyType.grid(column = 2, row = 2)

        # comboBoxGetOrderReport
        tk.Label(self, text = "查詢種類").grid(column = 0, row = 7)
            #輸入框
        self.comboBoxGetOrderReport = ttk.Combobox(self, state='readonly')
        self.comboBoxGetOrderReport['values'] = Config.comboBoxGetOrderReport
        self.comboBoxGetOrderReport.grid(column = 1, row = 7)
        global comboBoxGetOrderReport
        comboBoxGetOrderReport = self.comboBoxGetOrderReport

            # buttonGetOrderReport
        self.buttonGetOrderReport = tk.Button(self)
        self.buttonGetOrderReport["text"] = "委託回報查詢"
        self.buttonGetOrderReport["command"] = self.buttonGetOrderReport_Click
        self.buttonGetOrderReport.grid(column = 2, row = 7)

        # comboBoxGetFulfillReport
        tk.Label(self, text = "查詢種類").grid(column = 0, row = 8)
            #輸入框
        self.comboBoxGetFulfillReport = ttk.Combobox(self, state='readonly')
        self.comboBoxGetFulfillReport['values'] = Config.comboBoxGetFulfillReport
        self.comboBoxGetFulfillReport.grid(column = 1, row = 8)
        global comboBoxGetFulfillReport
        comboBoxGetFulfillReport = self.comboBoxGetFulfillReport
            # buttonGetFulfillReport
        self.buttonGetFulfillReport = tk.Button(self)
        self.buttonGetFulfillReport["text"] = "成交回報查詢"
        self.buttonGetFulfillReport["command"] = self.buttonGetFulfillReport_Click
        self.buttonGetFulfillReport.grid(column = 2, row = 8)

        # comboBoxSetMaxQtynMarketType
        tk.Label(self, text="市場種類").grid(column=0, row=9)
            # 輸入框
        self.comboBoxSetMaxQtynMarketType = ttk.Combobox(self, state='readonly')
        self.comboBoxSetMaxQtynMarketType['values'] = Config.comboBoxSetMaxQtynMarketType
        self.comboBoxSetMaxQtynMarketType.grid(column=1, row=9)
        global comboBoxSetMaxQtynMarketType
        comboBoxSetMaxQtynMarketType = self.comboBoxSetMaxQtynMarketType
            # Entry
        tk.Label(self, text="委託量").grid(column=2, row=9)
        self.entrySetMaxQtynMaxQty = tk.Entry(self)
        self.entrySetMaxQtynMaxQty.grid(column=3, row=9)
        global entrySetMaxQtynMaxQty
        entrySetMaxQtynMaxQty = self.entrySetMaxQtynMaxQty

            # buttonSetMaxQty
        self.buttonSetMaxQty = tk.Button(self)
        self.buttonSetMaxQty["text"] = "每秒委託「量」限制"
        self.buttonSetMaxQty["command"] = self.buttonSetMaxQty_Click
        self.buttonSetMaxQty.grid(column=4, row=9)

        # comboBoxSetMaxCountnMarketType
        tk.Label(self, text="市場種類").grid(column=0, row=10)
            # 輸入框
        self.comboBoxSetMaxCountnMarketType = ttk.Combobox(self, state='readonly')
        self.comboBoxSetMaxCountnMarketType['values'] = Config.comboBoxSetMaxCountnMarketType
        self.comboBoxSetMaxCountnMarketType.grid(column=1, row=10)
        global comboBoxSetMaxCountnMarketType
        comboBoxSetMaxCountnMarketType = self.comboBoxSetMaxCountnMarketType
            # Entry
        tk.Label(self, text="委託筆數").grid(column=2, row=10)
        self.entrySetMaxCountnMaxCount = tk.Entry(self)
        self.entrySetMaxCountnMaxCount.grid(column=3, row=10)
        global entrySetMaxCountnMaxCount
        entrySetMaxCountnMaxCount = self.entrySetMaxCountnMaxCount

            # buttonSetMaxCount
        self.buttonSetMaxCount = tk.Button(self)
        self.buttonSetMaxCount["text"] = "每秒委託「筆數」限制"
        self.buttonSetMaxCount["command"] = self.buttonSetMaxCount_Click
        self.buttonSetMaxCount.grid(column=4, row=10)
        
        # comboBoxUnlockOrder
        tk.Label(self, text = "市場種類").grid(column = 0, row = 11)
            #輸入框
        self.comboBoxUnlockOrder = ttk.Combobox(self, state='readonly')
        self.comboBoxUnlockOrder['values'] = Config.comboBoxUnlockOrder
        self.comboBoxUnlockOrder.grid(column = 1, row = 11)
        global comboBoxUnlockOrder
        comboBoxUnlockOrder = self.comboBoxUnlockOrder
            # buttonUnlockOrder
        self.buttonUnlockOrder = tk.Button(self)
        self.buttonUnlockOrder["text"] = "下單解鎖"
        self.buttonUnlockOrder["command"] = self.buttonUnlockOrder_Click
        self.buttonUnlockOrder.grid(column = 2, row = 11)

        # buttonSKOrderLib_PingandTracertTest
        self.buttonSKOrderLib_PingandTracertTest = tk.Button(self)
        self.buttonSKOrderLib_PingandTracertTest["text"] = "Ping測試API使用到的主機是否正常"
        self.buttonSKOrderLib_PingandTracertTest["command"] = self.buttonSKOrderLib_PingandTracertTest_Click
        self.buttonSKOrderLib_PingandTracertTest.grid(column = 1, row = 1)

        # buttonSKOrderLib_TelnetTest
        self.buttonSKOrderLib_TelnetTest = tk.Button(self)
        self.buttonSKOrderLib_TelnetTest["text"] = "Telnet測試API使用到的主機是否正常"
        self.buttonSKOrderLib_TelnetTest["command"] = self.buttonSKOrderLib_TelnetTest_Click
        self.buttonSKOrderLib_TelnetTest.grid(column = 1, row = 2)

        # buttonSKOrderLib_LogUpload
        self.buttonSKOrderLib_LogUpload = tk.Button(self)
        self.buttonSKOrderLib_LogUpload["text"] = "打包近3日LOG"
        self.buttonSKOrderLib_LogUpload["command"] = self.buttonSKOrderLib_LogUpload_Click
        self.buttonSKOrderLib_LogUpload.grid(column = 1, row = 3)


    def buttonSKOrderLib_Initialize_Click(self):
        nCode = m_pSKOrder.SKOrderLib_Initialize()

        msg = "【SKOrderLib_Initialize】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonGetUserAccount_Click(self):
        nCode = m_pSKOrder.GetUserAccount()

        msg = "【GetUserAccount】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonReadCertByID_Click(self):
        nCode = m_pSKOrder.ReadCertByID(comboBoxUserID.get())

        msg = "【ReadCertByID】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKOrderLib_GetLoginType_Click(self):
        nCode = m_pSKOrder.SKOrderLib_GetLoginType(comboBoxUserID.get())
        if nCode == 0:
            msg = "一般帳號"
        else:
            msg = "VIP帳號"
        msg = "【SKOrderLib_GetLoginType】" + msg
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKOrderLib_GetSpeedyType_Click(self):
        nCode = m_pSKOrder.SKOrderLib_GetSpeedyType(comboBoxUserID.get())
        if nCode == 0:
            msg = "一般線路"
        else:
            msg = "Speedy線路"
        msg = "【SKOrderLib_GetSpeedyType】" + msg
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonGetOrderReport_Click(self):
        if comboBoxGetOrderReport.get() == "1:全部":
            format = 1
        elif comboBoxGetOrderReport.get() == "2:有效":
            format = 2
        elif comboBoxGetOrderReport.get() == "3:可消":
            format = 3
        elif comboBoxGetOrderReport.get() == "4:已消":
            format = 4
        elif comboBoxGetOrderReport.get() == "5:已成":
            format = 5
        elif comboBoxGetOrderReport.get() == "6:失敗":
            format = 6
        elif comboBoxGetOrderReport.get() == "7:合併同價格":
            format = 7
        elif comboBoxGetOrderReport.get() == "8:合併同商品":
            format = 8
        elif comboBoxGetOrderReport.get() == "9:預約":
            format = 9
        else:
            format = 1
        bstrResult = m_pSKOrder.GetOrderReport(comboBoxUserID.get(), comboBoxAccount.get(), format)
        msg = "【GetOrderReport】" + bstrResult
        richTextBoxMessage.insert('end',  msg + "\n")
        richTextBoxMessage.see('end')

    def buttonGetFulfillReport_Click(self):
        if comboBoxGetFulfillReport.get() == "1:全部":
            format = 1
        elif comboBoxGetFulfillReport.get() == "2:合併同書號":
            format = 2
        elif comboBoxGetFulfillReport.get() == "3:合併同價格":
            format = 3
        elif comboBoxGetFulfillReport.get() == "4:合併同商品":
            format = 4
        elif comboBoxGetFulfillReport.get() == "5:T+1成交回報":
            format = 5
        else:
            format = 1
        bstrResult = m_pSKOrder.GetFulfillReport(comboBoxUserID.get(), comboBoxAccount.get(), format)
        msg = "【GetFulfillReport】" + bstrResult
        richTextBoxMessage.insert('end',  msg + "\n")
        richTextBoxMessage.see('end')

    def buttonSetMaxQty_Click(self):
        if comboBoxSetMaxQtynMarketType.get() == "0：TS(證券)":
            nMarketType = 0
        elif comboBoxSetMaxQtynMarketType.get() == "1：TF(期貨)":
            nMarketType = 1
        elif comboBoxSetMaxQtynMarketType.get() == "2：TO(選擇權)":
            nMarketType = 2
        elif comboBoxSetMaxQtynMarketType.get() == "3：OS(複委託)":
            nMarketType = 3
        elif comboBoxSetMaxQtynMarketType.get() == "4：OF(海外期貨)":
            nMarketType = 4
        elif comboBoxSetMaxQtynMarketType.get() == "5：OO(海外選擇權)":
            nMarketType = 5
        else:
            nMarketType = 0
        nCode = m_pSKOrder.SetMaxQty(nMarketType, int(entrySetMaxQtynMaxQty.get()))
        msg = "【SetMaxQty】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSetMaxCount_Click(self):
        if comboBoxSetMaxCountnMarketType.get() == "0：TS(證券)":
            nMarketType = 0
        elif comboBoxSetMaxCountnMarketType.get() == "1：TF(期貨)":
            nMarketType = 1
        elif comboBoxSetMaxCountnMarketType.get() == "2：TO(選擇權)":
            nMarketType = 2
        elif comboBoxSetMaxCountnMarketType.get() == "3：OS(複委託)":
            nMarketType = 3
        elif comboBoxSetMaxCountnMarketType.get() == "4：OF(海外期貨)":
            nMarketType = 4
        elif comboBoxSetMaxCountnMarketType.get() == "5：OO(海外選擇權)":
            nMarketType = 5
        else:
            nMarketType = 0
        nCode = m_pSKOrder.SetMaxCount(nMarketType, int(entrySetMaxCountnMaxCount.get()))
        msg = "【SetMaxCount】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonUnlockOrder_Click(self):
        if comboBoxUnlockOrder.get() == "0：TS(證券)":
            nMarketType = 0
        elif comboBoxUnlockOrder.get() == "1：TF(期貨)":
            nMarketType = 1
        elif comboBoxUnlockOrder.get() == "2：TO(選擇權)":
            nMarketType = 2
        elif comboBoxUnlockOrder.get() == "3：OS(複委託)":
            nMarketType = 3
        elif comboBoxUnlockOrder.get() == "4：OF(海外期貨)":
            nMarketType = 4
        elif comboBoxUnlockOrder.get() == "5：OO(海外選擇權)":
            nMarketType = 5
        else:
            nMarketType = 0
        nCode = m_pSKOrder.UnlockOrder(nMarketType)
        msg = "【UnlockOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKOrderLib_PingandTracertTest_Click(self):
        nCode = m_pSKOrder.SKOrderLib_PingandTracertTest()
        msg = "【SKOrderLib_PingandTracertTest】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonSKOrderLib_TelnetTest_Click(self):
        nCode = m_pSKOrder.SKOrderLib_TelnetTest()
        msg = "【SKOrderLib_TelnetTest】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonSKOrderLib_LogUpload_Click(self):
        nCode = m_pSKOrder.SKOrderLib_LogUpload()
        msg = "【SKOrderLib_LogUpload】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

#=========================================================
#開啟Tk視窗
if __name__ == '__main__':
    #建立主視窗
    root = tk.Tk()
    root.title("Login")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.pack(fill=tk.BOTH, expand=True)

    #建立Notebook組件
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # 在 Notebook 中建立一個tab2
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text='下單')

    # 在tab中添加 '下單' 的實例
    login_form2 = OrderForm(tab2)
    login_form2.pack()

    root.mainloop()
#==========================================
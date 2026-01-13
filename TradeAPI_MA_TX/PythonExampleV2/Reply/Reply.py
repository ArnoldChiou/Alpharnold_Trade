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
######################################################################################################################################
# ReplyLib事件
class SKReplyLibEvent():
    def OnReplyMessage(self, bstrUserID, bstrMessages):
        nConfirmCode = -1
        msg = "【註冊公告OnReplyMessage】" + bstrUserID + "_" + bstrMessages
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
        return nConfirmCode
    def OnReplyClearMessage(self, bstrUserID):
        msg = "【OnReplyClearMessage】" + bstrUserID + "_" + "正在清除前日回報!"
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnSolaceReplyConnection(self, bstrUserID, nErrorCode):
        msg = "【OnSolaceReplyConnection】" + bstrUserID + "_" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nErrorCode)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnSolaceReplyDisconnect(self, bstrUserID, nErrorCode):
        msg = "【OnSolaceReplyDisconnect】" + bstrUserID + "_" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nErrorCode)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnComplete(self, bstrUserID):
        msg = "【OnComplete】" + bstrUserID + "_" + "回報連線&資料正常"
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnReplyClear(self, bstrMarket):
        if bstrMarket == "R1":
            msg = "證券"
        elif bstrMarket == "R2":
            msg = "國內期選"
        elif bstrMarket == "R3":
            msg = "海外股市"
        elif bstrMarket == "R4":
            msg = "海外期選"
        elif bstrMarket == "R11":
            msg = "盤中零股"
        elif bstrMarket == "R20" or bstrMarket == "R21" or bstrMarket == "R22" or bstrMarket == "R23":
            msg = "智慧單"

        msg = "【OnReplyClear】" + msg + "_" + "正在清除前日回報!"
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnNewData(self, bstrUserID, bstrData):
        msg = "【OnNewData】" + bstrUserID + "_" + bstrData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')

        values = bstrData.split(',')
        MarketType = values[1]

        if MarketType == "TS":
            richTextBoxTSForm.insert('end', msg + "\n")
            richTextBoxTSForm.see('end')
        elif MarketType == "TA":
            richTextBoxTAForm.insert('end', msg + "\n")
            richTextBoxTAForm.see('end')
        elif MarketType == "TL":
            richTextBoxTLForm.insert('end', msg + "\n")
            richTextBoxTLForm.see('end')           
        elif MarketType == "TP":
            richTextBoxTPForm.insert('end', msg + "\n")
            richTextBoxTPForm.see('end')
        elif MarketType == "TC":
            richTextBoxTCForm.insert('end', msg + "\n")
            richTextBoxTCForm.see('end')    
        elif MarketType == "TF":
            richTextBoxTFForm.insert('end', msg + "\n")
            richTextBoxTFForm.see('end')
        elif MarketType == "TO":
            richTextBoxTOForm.insert('end', msg + "\n")
            richTextBoxTOForm.see('end')
        elif MarketType == "OF":
            richTextBoxOFForm.insert('end', msg + "\n")
            richTextBoxOFForm.see('end')           
        elif MarketType == "OO":
            richTextBoxOOForm.insert('end', msg + "\n")
            richTextBoxOOForm.see('end')
        elif MarketType == "OS":
            richTextBoxOSForm.insert('end', msg + "\n")
            richTextBoxOSForm.see('end')  

    def OnStrategyData(self, bstrUserID, bstrData):
        msg = "【OnStrategyData】" + bstrUserID + "_" + bstrData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')

        values = bstrData.split(',')
        MarketType = values[0]
        TradeKind = values[5]

        if MarketType == "TS":
            if TradeKind == "9":
                richTextBoxTSMSTForm.insert('end', msg + "\n")
                richTextBoxTSMSTForm.see('end')
            elif TradeKind == "29":
                richTextBoxTSMIOCForm.insert('end', msg + "\n")
                richTextBoxTSMIOCForm.see('end')
            elif TradeKind == "8":
                richTextBoxTSMITForm.insert('end', msg + "\n")
                richTextBoxTSMITForm.see('end')           
            elif TradeKind == "11":
                richTextBoxTSDTForm.insert('end', msg + "\n")
                richTextBoxTSDTForm.see('end')
            elif TradeKind == "17":
                richTextBoxTSCOForm.insert('end', msg + "\n")
                richTextBoxTSCOForm.see('end')    
            elif TradeKind == "3":
                richTextBoxTSOCOForm.insert('end', msg + "\n")
                richTextBoxTSOCOForm.see('end')
            elif TradeKind == "10":
                richTextBoxTSABForm.insert('end', msg + "\n")
                richTextBoxTSABForm.see('end')
            elif TradeKind == "27":
                richTextBoxTSCBForm.insert('end', msg + "\n")
                richTextBoxTSCBForm.see('end')          

        elif MarketType == "TF":
            if TradeKind == "5":
                richTextBoxTFSTPForm.insert('end', msg + "\n")
                richTextBoxTFSTPForm.see('end')
            elif TradeKind == "8":
                richTextBoxTFMITForm.insert('end', msg + "\n")
                richTextBoxTFMITForm.see('end')   
            elif TradeKind == "9":
                richTextBoxTFMSTForm.insert('end', msg + "\n")
                richTextBoxTFMSTForm.see('end')
            elif TradeKind == "3":
                richTextBoxTFOCOForm.insert('end', msg + "\n")
                richTextBoxTFOCOForm.see('end') 
            elif TradeKind == "10":
                richTextBoxTFABForm.insert('end', msg + "\n")
                richTextBoxTFABForm.see('end')   
        elif MarketType == "OF":
            if TradeKind == "3":
                richTextBoxOFOCOForm.insert('end', msg + "\n")
                richTextBoxOFOCOForm.see('end') 
            elif TradeKind == "10":
                richTextBoxOFABForm.insert('end', msg + "\n")
                richTextBoxOFABForm.see('end')            

    
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
#ReplyForm
class ReplyForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):
        
        # buttonSKReplyLib_ConnectByID
        self.buttonSKReplyLib_ConnectByID = tk.Button(self)
        self.buttonSKReplyLib_ConnectByID["text"] = "連線回報主機"
        self.buttonSKReplyLib_ConnectByID["command"] = self.buttonSKReplyLib_ConnectByID_Click
        self.buttonSKReplyLib_ConnectByID.grid(row=0, column=1)
                
        # buttonSKReplyLib_SolaceCloseByID
        self.buttonSKReplyLib_SolaceCloseByID = tk.Button(self)
        self.buttonSKReplyLib_SolaceCloseByID["text"] = "斷線Solace主機"
        self.buttonSKReplyLib_SolaceCloseByID["command"] = self.buttonSKReplyLib_SolaceCloseByID_Click
        self.buttonSKReplyLib_SolaceCloseByID.grid(row=1, column=1)
                
        # buttonSKReplyLib_IsConnectedByID
        self.buttonSKReplyLib_IsConnectedByID = tk.Button(self)
        self.buttonSKReplyLib_IsConnectedByID["text"] = "檢查連線狀態"
        self.buttonSKReplyLib_IsConnectedByID["command"] = self.buttonSKReplyLib_IsConnectedByID_Click
        self.buttonSKReplyLib_IsConnectedByID.grid(row=2, column=1)

    def buttonSKReplyLib_ConnectByID_Click(self):
        
        # 指定回報連線的使用者登入帳號
        nCode= m_pSKReply.SKReplyLib_ConnectByID(comboBoxUserID.get())

        msg = "【SKReplyLib_ConnectByID】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKReplyLib_SolaceCloseByID_Click(self):
        
        # 中斷指定帳號的連線
        nCode= m_pSKReply.SKReplyLib_SolaceCloseByID(comboBoxUserID.get())

        msg = "【SKReplyLib_SolaceCloseByID】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKReplyLib_IsConnectedByID_Click(self):
        
        # 檢查輸入的帳號目前連線狀態
        nCode= m_pSKReply.SKReplyLib_IsConnectedByID(comboBoxUserID.get())

        if nCode == 0:
            msg = "斷線"
        elif nCode == 1:
            msg = "連線中"
        elif nCode == 2:
            msg = "下載中"
        else:
            msg = "出錯啦"

        msg = "【SKReplyLib_IsConnectedByID】" + msg
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#TSForm
class TSForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSForm
        self.richTextBoxTSForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSForm
        richTextBoxTSForm = self.richTextBoxTSForm
######################################################################################################################################
#TAForm
class TAForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTAForm
        self.richTextBoxTAForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTAForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTAForm
        richTextBoxTAForm = self.richTextBoxTAForm
######################################################################################################################################
#TLForm
class TLForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTLForm
        self.richTextBoxTLForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTLForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTLForm
        richTextBoxTLForm = self.richTextBoxTLForm
######################################################################################################################################
#TPForm
class TPForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTPForm
        self.richTextBoxTPForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTPForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTPForm
        richTextBoxTPForm = self.richTextBoxTPForm 
######################################################################################################################################
#TCForm
class TCForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTCForm
        self.richTextBoxTCForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTCForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTCForm
        richTextBoxTCForm = self.richTextBoxTCForm
######################################################################################################################################
#TFForm
class TFForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTFForm
        self.richTextBoxTFForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTFForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTFForm
        richTextBoxTFForm = self.richTextBoxTFForm
######################################################################################################################################
#TOForm
class TOForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTOForm
        self.richTextBoxTOForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTOForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTOForm
        richTextBoxTOForm = self.richTextBoxTOForm
######################################################################################################################################
#OFForm
class OFForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxOFForm
        self.richTextBoxOFForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxOFForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxOFForm
        richTextBoxOFForm = self.richTextBoxOFForm  
######################################################################################################################################
#OOForm
class OOForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxOOForm
        self.richTextBoxOOForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxOOForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxOOForm
        richTextBoxOOForm = self.richTextBoxOOForm
######################################################################################################################################
#OSForm
class OSForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxOSForm
        self.richTextBoxOSForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxOSForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxOSForm
        richTextBoxOSForm = self.richTextBoxOSForm                 

######################################################################################################################################
#TSDTForm
class TSDTForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSDTForm
        self.richTextBoxTSDTForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSDTForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSDTForm
        richTextBoxTSDTForm = self.richTextBoxTSDTForm          
######################################################################################################################################
#TSCOForm
class TSCOForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSCOForm
        self.richTextBoxTSCOForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSCOForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSCOForm
        richTextBoxTSCOForm = self.richTextBoxTSCOForm  
######################################################################################################################################
#TSMITForm
class TSMITForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSMITForm
        self.richTextBoxTSMITForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSMITForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSMITForm
        richTextBoxTSMITForm = self.richTextBoxTSMITForm          
######################################################################################################################################
#TSOCOForm
class TSOCOForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSOCOForm
        self.richTextBoxTSOCOForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSOCOForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSOCOForm
        richTextBoxTSOCOForm = self.richTextBoxTSOCOForm 
######################################################################################################################################
#TSMIOCForm
class TSMIOCForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSMIOCForm
        self.richTextBoxTSMIOCForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSMIOCForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSMIOCForm
        richTextBoxTSMIOCForm = self.richTextBoxTSMIOCForm          
######################################################################################################################################
#TSMSTForm
class TSMSTForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSMSTForm
        self.richTextBoxTSMSTForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSMSTForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSMSTForm
        richTextBoxTSMSTForm = self.richTextBoxTSMSTForm  
######################################################################################################################################
#TSABForm
class TSABForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSABForm
        self.richTextBoxTSABForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSABForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSABForm
        richTextBoxTSABForm = self.richTextBoxTSABForm          
######################################################################################################################################
#TSCBForm
class TSCBForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTSCBForm
        self.richTextBoxTSCBForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTSCBForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTSCBForm
        richTextBoxTSCBForm = self.richTextBoxTSCBForm 

######################################################################################################################################
#TFSTPForm
class TFSTPForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTFSTPForm
        self.richTextBoxTFSTPForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTFSTPForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTFSTPForm
        richTextBoxTFSTPForm = self.richTextBoxTFSTPForm          
######################################################################################################################################
#TFMSTForm
class TFMSTForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTFMSTForm
        self.richTextBoxTFMSTForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTFMSTForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTFMSTForm
        richTextBoxTFMSTForm = self.richTextBoxTFMSTForm  
######################################################################################################################################
#TFMITForm
class TFMITForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTFMITForm
        self.richTextBoxTFMITForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTFMITForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTFMITForm
        richTextBoxTFMITForm = self.richTextBoxTFMITForm          
######################################################################################################################################
#TFOCOForm
class TFOCOForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTFOCOForm
        self.richTextBoxTFOCOForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTFOCOForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTFOCOForm
        richTextBoxTFOCOForm = self.richTextBoxTFOCOForm 
######################################################################################################################################
#TFABForm
class TFABForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxTFABForm
        self.richTextBoxTFABForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxTFABForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxTFABForm
        richTextBoxTFABForm = self.richTextBoxTFABForm     


######################################################################################################################################
#OFOCOForm
class OFOCOForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxOFOCOForm
        self.richTextBoxOFOCOForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxOFOCOForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxOFOCOForm
        richTextBoxOFOCOForm = self.richTextBoxOFOCOForm 
######################################################################################################################################
#OFABForm
class OFABForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        
        # richTextBoxOFABForm
        self.richTextBoxOFABForm = tk.Listbox(self, height=5, width=150)
        self.richTextBoxOFABForm.grid(column = 0, row = 0, columnspan=5)

        global richTextBoxOFABForm
        richTextBoxOFABForm = self.richTextBoxOFABForm 
#==========================================
#定義彈出視窗
def popup_window_Reply():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Reply")

    # 建立 Frame 作為 ReplyForm，並添加到彈出窗口
    popup_ReplyForm = ReplyForm(popup)
    popup_ReplyForm.pack(fill=tk.BOTH, expand=True)

#開啟Tk視窗
if __name__ == '__main__':
    #建立主視窗
    root = tk.Tk()
    root.title("Reply")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.pack(fill=tk.BOTH, expand=True)
#================================================#
    #建立Notebook組件(OnNewData)
    notebookOnNewData = ttk.Notebook(root)
    notebookOnNewData.pack(fill='both', expand=True)

    # 在 Notebook 中建立一個tab1
    tab1 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab1, text='證券')
        # 在tab中添加實例
    TSForm1 = TSForm(tab1)
    TSForm1.pack()
    
    # 在 Notebook 中建立一個tab2
    tab2 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab2, text='盤後')
        # 在tab中添加實例
    TAForm1 = TAForm(tab2)
    TAForm1.pack()
    
    # 在 Notebook 中建立一個tab3
    tab3 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab3, text='零股')
        # 在tab中添加實例
    TLForm1 = TLForm(tab3)
    TLForm1.pack()
    
    # 在 Notebook 中建立一個tab4
    tab4 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab4, text='興櫃')
        # 在tab中添加實例
    TPForm1 = TPForm(tab4)
    TPForm1.pack()
    
    # 在 Notebook 中建立一個tab5
    tab5 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab5, text='盤中零股')
        # 在tab中添加實例
    TCForm1 = TCForm(tab5)
    TCForm1.pack()
    
    # 在 Notebook 中建立一個tab6
    tab6 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab6, text='期貨')
        # 在tab中添加實例
    TFForm1 = TFForm(tab6)
    TFForm1.pack()
    
    # 在 Notebook 中建立一個tab7
    tab7 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab7, text='選擇權')
        # 在tab中添加實例
    TOForm1 = TOForm(tab7)
    TOForm1.pack()
    
    # 在 Notebook 中建立一個tab8
    tab8 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab8, text='海期')
        # 在tab中添加實例
    OFForm1 = OFForm(tab8)
    OFForm1.pack()
    
    # 在 Notebook 中建立一個tab9
    tab9 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab9, text='海選')
        # 在tab中添加實例
    OOForm1 = OOForm(tab9)
    OOForm1.pack()
    
    # 在 Notebook 中建立一個tab10
    tab10 = ttk.Frame(notebookOnNewData)
    notebookOnNewData.add(tab10, text='複委託')
        # 在tab中添加實例
    OSForm1 = OSForm(tab10)
    OSForm1.pack()

#================================================#
    #建立Notebook組件(OnStrategyData-TS)
    notebookOnNewData2 = ttk.Notebook(root)
    notebookOnNewData2.pack(fill='both', expand=True)

    # 在 Notebook 中建立一個tab1
    tab1 = ttk.Frame(notebookOnNewData2)
    notebookOnNewData2.add(tab1, text='證券當沖')
        # 在tab中添加實例
    TSDTForm1 = TSDTForm(tab1)
    TSDTForm1.pack()
    
    # 在 Notebook 中建立一個tab2
    tab2 = ttk.Frame(notebookOnNewData2)
    notebookOnNewData2.add(tab2, text='出清')
        # 在tab中添加實例
    TSCOForm1 = TSCOForm(tab2)
    TSCOForm1.pack()
    
    # 在 Notebook 中建立一個tab3
    tab3 = ttk.Frame(notebookOnNewData2)
    notebookOnNewData2.add(tab3, text='MIT')
        # 在tab中添加實例
    TSMITForm1 = TSMITForm(tab3)
    TSMITForm1.pack()
    
    # 在 Notebook 中建立一個tab4
    tab4 = ttk.Frame(notebookOnNewData2)
    notebookOnNewData2.add(tab4, text='OCO')
        # 在tab中添加實例
    TSOCOForm1 = TSOCOForm(tab4)
    TSOCOForm1.pack()
    
    # 在 Notebook 中建立一個tab5
    tab5 = ttk.Frame(notebookOnNewData2)
    notebookOnNewData2.add(tab5, text='MIOC')
        # 在tab中添加實例
    TSMIOCForm1 = TSMIOCForm(tab5)
    TSMIOCForm1.pack()
    
    # 在 Notebook 中建立一個tab6
    tab6 = ttk.Frame(notebookOnNewData2)
    notebookOnNewData2.add(tab6, text='MST')
        # 在tab中添加實例
    TSMSTForm1 = TSMSTForm(tab6)
    TSMSTForm1.pack()
    
    # 在 Notebook 中建立一個tab7
    tab7 = ttk.Frame(notebookOnNewData2)
    notebookOnNewData2.add(tab7, text='AB')
        # 在tab中添加實例
    TSABForm1 = TSABForm(tab7)
    TSABForm1.pack()
    
    # 在 Notebook 中建立一個tab8
    tab8 = ttk.Frame(notebookOnNewData2)
    notebookOnNewData2.add(tab8, text='CB')
        # 在tab中添加實例
    TSCBForm1 = TSCBForm(tab8)
    TSCBForm1.pack()
#================================================#    
    #建立Notebook組件(OnStrategyData-TF)
    notebookOnNewData3 = ttk.Notebook(root)
    notebookOnNewData3.pack(fill='both', expand=True)

    # 在 Notebook 中建立一個tab1
    tab1 = ttk.Frame(notebookOnNewData3)
    notebookOnNewData3.add(tab1, text='期貨STP')
        # 在tab中添加實例
    TFSTPForm1 = TFSTPForm(tab1)
    TFSTPForm1.pack()
    
    # 在 Notebook 中建立一個tab2
    tab2 = ttk.Frame(notebookOnNewData3)
    notebookOnNewData3.add(tab2, text='MST')
        # 在tab中添加實例
    TFMSTForm1 = TFMSTForm(tab2)
    TFMSTForm1.pack()
    
    # 在 Notebook 中建立一個tab3
    tab3 = ttk.Frame(notebookOnNewData3)
    notebookOnNewData3.add(tab3, text='MIT')
        # 在tab中添加實例
    TFMITForm1 = TFMITForm(tab3)
    TFMITForm1.pack()
    
    # 在 Notebook 中建立一個tab4
    tab4 = ttk.Frame(notebookOnNewData3)
    notebookOnNewData3.add(tab4, text='OCO')
        # 在tab中添加實例
    TFOCOForm1 = TFOCOForm(tab4)
    TFOCOForm1.pack()
    
    # 在 Notebook 中建立一個tab5
    tab5 = ttk.Frame(notebookOnNewData3)
    notebookOnNewData3.add(tab5, text='AB')
        # 在tab中添加實例
    TFABForm1 = TFABForm(tab5)
    TFABForm1.pack()
#================================================#    
    #建立Notebook組件(OnStrategyData-OF)
    notebookOnNewData4 = ttk.Notebook(root)
    notebookOnNewData4.pack(fill='both', expand=True)

    # 在 Notebook 中建立一個tab1
    tab1 = ttk.Frame(notebookOnNewData4)
    notebookOnNewData4.add(tab1, text='海期OCO')
        # 在tab中添加實例
    OFOCOForm1 = OFOCOForm(tab1)
    OFOCOForm1.pack()
    
    # 在 Notebook 中建立一個tab2
    tab2 = ttk.Frame(notebookOnNewData4)
    notebookOnNewData4.add(tab2, text='AB')
        # 在tab中添加實例
    OFABForm1 = OFABForm(tab2)
    OFABForm1.pack()
#================================================#
    # 開啟Reply視窗的按鈕
    popup_button_Reply = tk.Button(root, text="回報", command=popup_window_Reply)
    popup_button_Reply.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

#==========================================
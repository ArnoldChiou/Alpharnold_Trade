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
# 是否為價差交易
Spread = False


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
    # 海外期貨下單商品。透過呼叫 GetOverseaFutures 後，資訊由該事件回傳。
    def OnOverseaFuture(self, bstrData):
        msg = "【OnOverseaFuture】" + bstrData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 海外選擇權下單商品。透過呼叫 GetOverseaOptions 後，資訊由該事件回傳。
    def OnOverseaOption(self, bstrData):
        msg = "【OnOverseaOption】" + bstrData;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 海外期貨未平倉彙總資料。透過呼叫GetOverseaFutureOpenInterestGW 後，資訊由該事件回傳。
    def OnOFOpenInterestGWReport(self, bstrData):
        msg = "【OnOFOpenInterestGWReport】" + bstrData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 海外期貨權益數。透過呼叫 GetRequestOverSeaFutureRight後，資訊由該事件回傳。
    def OnOverSeaFutureRight(self, bstrData):
        msg = "【OnOverSeaFutureRight】" + bstrData;
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
######################################################################################################################################
#ReadForm
class ReadForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # buttonGetOverseaFutures
        self.buttonGetOverseaFutures = tk.Button(self)
        self.buttonGetOverseaFutures["text"] = "海期商品檔查詢"
        self.buttonGetOverseaFutures["command"] = self.buttonGetOverseaFutures_Click
        self.buttonGetOverseaFutures.grid(row=0, column=1)
        
        # buttonGetOverseaOptions
        self.buttonGetOverseaOptions = tk.Button(self)
        self.buttonGetOverseaOptions["text"] = "海選商品檔查詢"
        self.buttonGetOverseaOptions["command"] = self.buttonGetOverseaOptions_Click
        self.buttonGetOverseaOptions.grid(row=1, column=1)

        # buttonGetOverseaFutureOpenInterestGW
        self.buttonGetOverseaFutureOpenInterestGW = tk.Button(self)
        self.buttonGetOverseaFutureOpenInterestGW["text"] = "海期未平倉"
        self.buttonGetOverseaFutureOpenInterestGW["command"] = self.buttonGetOverseaFutureOpenInterestGW_Click
        self.buttonGetOverseaFutureOpenInterestGW.grid(row=2, column=1)

        # comboBoxnFormatRead
        tk.Label(self, text = "格式").grid(row = 2,column = 2)
        self.comboBoxnFormatRead = ttk.Combobox(self, state='readonly')
        self.comboBoxnFormatRead['values'] = Config.comboBoxnFormatRead
        self.comboBoxnFormatRead.grid(row=2, column=3)

        global comboBoxnFormatRead
        comboBoxnFormatRead = self.comboBoxnFormatRead

        # buttonGetRequestOverSeaFutureRight
        self.buttonGetRequestOverSeaFutureRight = tk.Button(self)
        self.buttonGetRequestOverSeaFutureRight["text"] = "海外權益數"
        self.buttonGetRequestOverSeaFutureRight["command"] = self.buttonGetRequestOverSeaFutureRight_Click
        self.buttonGetRequestOverSeaFutureRight.grid(row=3, column=1)

    
            
    def buttonGetOverseaFutures_Click(self):
        nCode = m_pSKOrder.GetOverseaFutures()

        msg = "【GetOverseaFutures】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
                    
    def buttonGetOverseaOptions_Click(self):
        nCode = m_pSKOrder.GetOverseaOptions()

        msg = "【GetOverseaOptions】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonGetOverseaFutureOpenInterestGW_Click(self):
        if (comboBoxnFormatRead.get() == "1.彙總"):
            nFormat = 1
        elif (comboBoxnFormatRead.get() == "2.明細"):
            nFormat = 2

        nCode = m_pSKOrder.GetOverseaFutureOpenInterestGW(comboBoxUserID.get(), comboBoxAccount.get(), nFormat)

        msg = "【GetOverseaFutureOpenInterestGW】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonGetRequestOverSeaFutureRight_Click(self):
    
        nCode = m_pSKOrder.GetRequestOverSeaFutureRight(comboBoxUserID.get(), comboBoxAccount.get())

        msg = "【GetRequestOverSeaFutureRight】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#LoadForm
class LoadForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):
        # buttonSKOrderLib_LoadOSCommodity
        self.buttonSKOrderLib_LoadOSCommodity = tk.Button(self)
        self.buttonSKOrderLib_LoadOSCommodity["text"] = "下載海期商品檔"
        self.buttonSKOrderLib_LoadOSCommodity["command"] = self.buttonSKOrderLib_LoadOSCommodity_Click
        self.buttonSKOrderLib_LoadOSCommodity.grid(row=0, column=1)

        global buttonSKOrderLib_LoadOSCommodity
        buttonSKOrderLib_LoadOSCommodity = self.buttonSKOrderLib_LoadOSCommodity

        # buttonSKOrderLib_LoadOOCommodity
        self.buttonSKOrderLib_LoadOOCommodity = tk.Button(self)
        self.buttonSKOrderLib_LoadOOCommodity["text"] = "下載海選商品檔"
        self.buttonSKOrderLib_LoadOOCommodity["command"] = self.buttonSKOrderLib_LoadOOCommodity_Click
        self.buttonSKOrderLib_LoadOOCommodity.grid(row=1, column=1)

        global buttonSKOrderLib_LoadOOCommodity
        buttonSKOrderLib_LoadOOCommodity = self.buttonSKOrderLib_LoadOOCommodity

    def buttonSKOrderLib_LoadOSCommodity_Click(self):
        nCode = m_pSKOrder.SKOrderLib_LoadOSCommodity()

        msg = "【SKOrderLib_LoadOSCommodity】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKOrderLib_LoadOOCommodity_Click(self):
        nCode = m_pSKOrder.SKOrderLib_LoadOOCommodity()

        msg = "【SKOrderLib_LoadOOCommodity】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#WithDrawForm
class WithDrawForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # comboBoxWithDrawnTypeOut
        tk.Label(self, text = "轉出類別").grid(row = 0,column = 1)
        self.comboBoxWithDrawnTypeOut = ttk.Combobox(self, state='readonly')
        self.comboBoxWithDrawnTypeOut['values'] = Config.comboBoxWithDrawnTypeOut
        self.comboBoxWithDrawnTypeOut.grid(row=0, column=2)

        global comboBoxWithDrawnTypeOut
        comboBoxWithDrawnTypeOut = self.comboBoxWithDrawnTypeOut

        # textBoxWithDrawbstrFullAccountOut
        tk.Label(self, text = "轉出期貨帳號").grid(row=1, column=1)
        #輸入框
        self.textBoxWithDrawbstrFullAccountOut = tk.Entry(self)
        self.textBoxWithDrawbstrFullAccountOut.grid(row=1, column=2)

        global textBoxWithDrawbstrFullAccountOut
        textBoxWithDrawbstrFullAccountOut = self.textBoxWithDrawbstrFullAccountOut
        
        # comboBoxWithDrawnTypeIn
        tk.Label(self, text = "轉入類別").grid(row = 2,column = 1)
        self.comboBoxWithDrawnTypeIn = ttk.Combobox(self, state='readonly')
        self.comboBoxWithDrawnTypeIn['values'] = Config.comboBoxWithDrawnTypeIn
        self.comboBoxWithDrawnTypeIn.grid(row=2, column=2)

        global comboBoxWithDrawnTypeIn
        comboBoxWithDrawnTypeIn = self.comboBoxWithDrawnTypeIn

        # textBoxWithDrawbstrFullAccountIn
        tk.Label(self, text = "轉入期貨帳號").grid(row=3, column=1)
        #輸入框
        self.textBoxWithDrawbstrFullAccountIn = tk.Entry(self)
        self.textBoxWithDrawbstrFullAccountIn.grid(row=3, column=2)

        global textBoxWithDrawbstrFullAccountIn
        textBoxWithDrawbstrFullAccountIn = self.textBoxWithDrawbstrFullAccountIn
                
        # comboBoxWithDrawnCurrency
        tk.Label(self, text = "幣別").grid(row = 4,column = 1)
        self.comboBoxWithDrawnCurrency = ttk.Combobox(self, state='readonly')
        self.comboBoxWithDrawnCurrency['values'] = Config.comboBoxWithDrawnCurrency
        self.comboBoxWithDrawnCurrency.grid(row=4, column=2)

        global comboBoxWithDrawnCurrency
        comboBoxWithDrawnCurrency = self.comboBoxWithDrawnCurrency

        # textBoxWithDrawbstrDollars
        tk.Label(self, text = "金額").grid(row=4, column=3)
        #輸入框
        self.textBoxWithDrawbstrDollars = tk.Entry(self)
        self.textBoxWithDrawbstrDollars.grid(row=4, column=4)

        global textBoxWithDrawbstrDollars
        textBoxWithDrawbstrDollars = self.textBoxWithDrawbstrDollars
        
        # textBoxWithDrawbstrPassword
        tk.Label(self, text = "出入金密碼").grid(row=5, column=1)
        #輸入框
        self.textBoxWithDrawbstrPassword = tk.Entry(self)
        self.textBoxWithDrawbstrPassword.grid(row=5, column=2)

        global textBoxWithDrawbstrPassword
        textBoxWithDrawbstrPassword = self.textBoxWithDrawbstrPassword

        # buttonWithDraw
        self.buttonWithDraw = tk.Button(self)
        self.buttonWithDraw["text"] = "出入金互轉"
        self.buttonWithDraw["command"] = self.buttonWithDraw_Click
        self.buttonWithDraw.grid(row=6, column=1)

        global buttonWithDraw
        buttonWithDraw = self.buttonWithDraw

    def buttonWithDraw_Click(self):
        bstrFullAccountOut = textBoxWithDrawbstrFullAccountOut.get()

        selectedValue = comboBoxWithDrawnTypeOut.get()
        if (selectedValue == "國內"):
            nTypeOut = 0
        elif (selectedValue == "國外"):
            nTypeOut = 1

        bstrFullAccountIn = textBoxWithDrawbstrFullAccountIn.get()
                                                                                    
        selectedValue = comboBoxWithDrawnTypeIn.get()
        if (selectedValue == "國內"):
            nTypeIn = 0
        elif (selectedValue == "國外"):
            nTypeIn = 1

        selectedValue = comboBoxWithDrawnCurrency.get()
        if (selectedValue == "澳幣"):
            nCurrency = 0
        elif (selectedValue == "歐元"):
            nCurrency = 1
        elif (selectedValue == "英鎊"):
            nCurrency = 2
        elif (selectedValue == "港幣"):
            nCurrency = 3
        elif (selectedValue == "日元"):
            nCurrency = 4
        elif (selectedValue == "台幣"):
            nCurrency = 5
        elif (selectedValue == "紐幣"):
            nCurrency = 6
        elif (selectedValue == "人民幣"):
            nCurrency = 7
        elif (selectedValue == "美元"):
            nCurrency = 8
        elif (selectedValue == "南非幣"):
            nCurrency = 9
        bstrDollars = textBoxWithDrawbstrDollars.get()
        bstrPassword = textBoxWithDrawbstrPassword.get()

        # 國內外出入金互轉
        bstrMessage, nCode = m_pSKOrder.WithDraw(comboBoxUserID.get(), bstrFullAccountOut, nTypeOut, bstrFullAccountIn, nTypeIn, nCurrency, bstrDollars, bstrPassword)

        msg = "【WithDraw】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # checkBoxSpread
        # 是否為價差交易

        self.checkBoxSpread = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxSpread["variable"] = self.var1
        self.checkBoxSpread["onvalue"] = True
        self.checkBoxSpread["offvalue"] = False
        self.checkBoxSpread["text"] = "是否為價差交易"
        self.checkBoxSpread["command"] = self.checkBoxSpread_CheckedChanged
        self.checkBoxSpread.grid( row = 0,column = 1)

        # textBoxOFExchangeNo
        tk.Label(self, text = "交易所代號").grid(row=1, column=1)
            #輸入框
        self.textBoxOFExchangeNo = tk.Entry(self)
        self.textBoxOFExchangeNo.grid(row=1, column=2)

        global textBoxOFExchangeNo
        textBoxOFExchangeNo = self.textBoxOFExchangeNo

        # textBoxOFStockNo
        tk.Label(self, text = "海外期貨代號").grid(row=2, column=1)
            #輸入框
        self.textBoxOFStockNo = tk.Entry(self)
        self.textBoxOFStockNo.grid(row=2, column=2)

        global textBoxOFStockNo
        textBoxOFStockNo = self.textBoxOFStockNo
        
        # textBoxOFYearMonth
        tk.Label(self, text = "近月商品年月(YYYYMM)").grid(row=3, column=1)
            #輸入框
        self.textBoxOFYearMonth = tk.Entry(self)
        self.textBoxOFYearMonth.grid(row=3, column=2)

        global textBoxOFYearMonth
        textBoxOFYearMonth = self.textBoxOFYearMonth
                
        # textBoxOFYearMonth2
        tk.Label(self, text = "遠月商品年月(YYYYMM)").grid(row=4, column=1)
            #輸入框
        self.textBoxOFYearMonth2 = tk.Entry(self)
        self.textBoxOFYearMonth2.grid(row=4, column=2)

        global textBoxOFYearMonth2
        textBoxOFYearMonth2 = self.textBoxOFYearMonth2
                        
        # textBoxOFOrder
        tk.Label(self, text = "委託價").grid(row=5, column=1)
            #輸入框
        self.textBoxOFOrder = tk.Entry(self)
        self.textBoxOFOrder.grid(row=5, column=2)

        global textBoxOFOrder
        textBoxOFOrder = self.textBoxOFOrder
                                
        # textBoxOFOrderNumerator
        tk.Label(self, text = "委託價分子").grid(row=6, column=1)
            #輸入框
        self.textBoxOFOrderNumerator = tk.Entry(self)
        self.textBoxOFOrderNumerator.grid(row=6, column=2)

        global textBoxOFOrderNumerator
        textBoxOFOrderNumerator = self.textBoxOFOrderNumerator
                                        
        # textBoxOFTrigger
        tk.Label(self, text = "觸發價").grid(row=7, column=1)
            #輸入框
        self.textBoxOFTrigger = tk.Entry(self)
        self.textBoxOFTrigger.grid(row=7, column=2)

        global textBoxOFTrigger
        textBoxOFTrigger = self.textBoxOFTrigger
                                                
        # textBoxOFTriggerNumerator
        tk.Label(self, text = "觸發價分子").grid(row=8, column=1)
            #輸入框
        self.textBoxOFTriggerNumerator = tk.Entry(self)
        self.textBoxOFTriggerNumerator.grid(row=8, column=2)

        global textBoxOFTriggerNumerator
        textBoxOFTriggerNumerator = self.textBoxOFTriggerNumerator
        
        # comboBoxOFBuySell
        tk.Label(self, text = "買進/賣出").grid(row=9, column=1)
            #輸入框
        self.comboBoxOFBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxOFBuySell['values'] = Config.comboBoxOFBuySell
        self.comboBoxOFBuySell.grid(row=9, column=2)

        global comboBoxOFBuySell
        comboBoxOFBuySell = self.comboBoxOFBuySell
                
        # comboBoxOFDayTrade
        tk.Label(self, text = "當沖").grid(row=10, column=1)
            #輸入框
        self.comboBoxOFDayTrade = ttk.Combobox(self, state='readonly')
        self.comboBoxOFDayTrade['values'] = Config.comboBoxOFDayTrade
        self.comboBoxOFDayTrade.grid(row=10, column=2)

        global comboBoxOFDayTrade
        comboBoxOFDayTrade = self.comboBoxOFDayTrade
                        
        # comboBoxOFTradeType
        tk.Label(self, text = "ROD/FOK/IOC").grid(row=11, column=1)
            #輸入框
        self.comboBoxOFTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxOFTradeType['values'] = Config.comboBoxOFTradeType
        self.comboBoxOFTradeType.grid(row=11, column=2)

        global comboBoxOFTradeType
        comboBoxOFTradeType = self.comboBoxOFTradeType
                                
        # comboBoxOFSpecialTradeType
        tk.Label(self, text = "LMT/MKT/STL/STP").grid(row=12, column=1)
            #輸入框
        self.comboBoxOFSpecialTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxOFSpecialTradeType['values'] = Config.comboBoxOFSpecialTradeType
        self.comboBoxOFSpecialTradeType.grid(row=12, column=2)

        global comboBoxOFSpecialTradeType
        comboBoxOFSpecialTradeType = self.comboBoxOFSpecialTradeType
                                                        
        # textBoxOFQty
        tk.Label(self, text = "交易口數").grid(row=13, column=1)
            #輸入框
        self.textBoxOFQty = tk.Entry(self)
        self.textBoxOFQty.grid(row=13, column=2)

        global textBoxOFQty
        textBoxOFQty = self.textBoxOFQty

        # buttonSendOverSeaFutureOrder
        self.buttonSendOverSeaFutureOrder = tk.Button(self)
        self.buttonSendOverSeaFutureOrder["text"] = "海外期貨送出"
        self.buttonSendOverSeaFutureOrder["command"] = self.buttonSendOverSeaFutureOrder_Click
        self.buttonSendOverSeaFutureOrder.grid(row=14, column=1)




        # textBoxOOExchangeNo
        tk.Label(self, text = "交易所代號").grid(row=15, column=1)
            #輸入框
        self.textBoxOOExchangeNo = tk.Entry(self)
        self.textBoxOOExchangeNo.grid(row=15, column=2)

        global textBoxOOExchangeNo
        textBoxOOExchangeNo = self.textBoxOOExchangeNo

        # textBoxOOStockNo
        tk.Label(self, text = "海外選擇權代號").grid(row=16, column=1)
            #輸入框
        self.textBoxOOStockNo = tk.Entry(self)
        self.textBoxOOStockNo.grid(row=16, column=2)

        global textBoxOOStockNo
        textBoxOOStockNo = self.textBoxOOStockNo
        
        # textBoxOOYearMonth
        tk.Label(self, text = "近月商品年月(YYYYMM)").grid(row=17, column=1)
            #輸入框
        self.textBoxOOYearMonth = tk.Entry(self)
        self.textBoxOOYearMonth.grid(row=17, column=2)

        global textBoxOOYearMonth
        textBoxOOYearMonth = self.textBoxOOYearMonth
                
        # textBoxOOOrder
        tk.Label(self, text = "委託價").grid(row=18, column=1)
            #輸入框
        self.textBoxOOOrder = tk.Entry(self)
        self.textBoxOOOrder.grid(row=18, column=2)

        global textBoxOOOrder
        textBoxOOOrder = self.textBoxOOOrder
                        
        # textBoxOOOrderNumerator
        tk.Label(self, text = "委託價分子").grid(row=19, column=1)
            #輸入框
        self.textBoxOOOrderNumerator = tk.Entry(self)
        self.textBoxOOOrderNumerator.grid(row=19, column=2)

        global textBoxOOOrderNumerator
        textBoxOOOrderNumerator = self.textBoxOOOrderNumerator
                                
        # textBoxbstrOrderDenominator
        tk.Label(self, text = "分母").grid(row=19, column=3)
            #輸入框
        self.textBoxbstrOrderDenominator = tk.Entry(self)
        self.textBoxbstrOrderDenominator.grid(row=19, column=4)

        global textBoxbstrOrderDenominator
        textBoxbstrOrderDenominator = self.textBoxbstrOrderDenominator
                                
        # textBoxOOTrigger
        tk.Label(self, text = "觸發價").grid(row=20, column=1)
            #輸入框
        self.textBoxOOTrigger = tk.Entry(self)
        self.textBoxOOTrigger.grid(row=20, column=2)

        global textBoxOOTrigger
        textBoxOOTrigger = self.textBoxOOTrigger
                                        
        # textBoxOOTriggerNumerator
        tk.Label(self, text = "觸發價分子").grid(row=21, column=1)
            #輸入框
        self.textBoxOOTriggerNumerator = tk.Entry(self)
        self.textBoxOOTriggerNumerator.grid(row=21, column=2)

        global textBoxOOTriggerNumerator
        textBoxOOTriggerNumerator = self.textBoxOOTriggerNumerator

        # comboBoxOOBuySell
        tk.Label(self, text = "買進/賣出").grid(row=22, column=1)
            #輸入框
        self.comboBoxOOBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxOOBuySell['values'] = Config.comboBoxOOBuySell
        self.comboBoxOOBuySell.grid(row=22, column=2)

        global comboBoxOOBuySell
        comboBoxOOBuySell = self.comboBoxOOBuySell
        
        # comboBoxOONewClose
        tk.Label(self, text = "新平倉").grid(row=23, column=1)
            #輸入框
        self.comboBoxOONewClose = ttk.Combobox(self, state='readonly')
        self.comboBoxOONewClose['values'] = Config.comboBoxOONewClose
        self.comboBoxOONewClose.grid(row=23, column=2)

        global comboBoxOONewClose
        comboBoxOONewClose = self.comboBoxOONewClose
                
        # comboBoxOODayTrade
        tk.Label(self, text = "當沖").grid(row=24, column=1)
            #輸入框
        self.comboBoxOODayTrade = ttk.Combobox(self, state='readonly')
        self.comboBoxOODayTrade['values'] = Config.comboBoxOODayTrade
        self.comboBoxOODayTrade.grid(row=24, column=2)

        global comboBoxOODayTrade
        comboBoxOODayTrade = self.comboBoxOODayTrade
                        
        # comboBoxOOSpecialTradeType
        tk.Label(self, text = "LMT/MKT/STL/STP").grid(row=25, column=1)
            #輸入框
        self.comboBoxOOSpecialTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxOOSpecialTradeType['values'] = Config.comboBoxOOSpecialTradeType
        self.comboBoxOOSpecialTradeType.grid(row=25, column=2)

        global comboBoxOOSpecialTradeType
        comboBoxOOSpecialTradeType = self.comboBoxOOSpecialTradeType
                                        
        # textBoxOOStrikePrice
        tk.Label(self, text = "履約價").grid(row=26, column=1)
            #輸入框
        self.textBoxOOStrikePrice = tk.Entry(self)
        self.textBoxOOStrikePrice.grid(row=26, column=2)

        global textBoxOOStrikePrice
        textBoxOOStrikePrice = self.textBoxOOStrikePrice
                                
        # comboBoxOOCallPut
        tk.Label(self, text = "CALL/PUT").grid(row=27, column=1)
            #輸入框
        self.comboBoxOOCallPut = ttk.Combobox(self, state='readonly')
        self.comboBoxOOCallPut['values'] = Config.comboBoxOOCallPut
        self.comboBoxOOCallPut.grid(row=27, column=2)

        global comboBoxOOCallPut
        comboBoxOOCallPut = self.comboBoxOOCallPut
                                                
        # textBoxOOQty
        tk.Label(self, text = "交易口數").grid(row=28, column=1)
            #輸入框
        self.textBoxOOQty = tk.Entry(self)
        self.textBoxOOQty.grid(row=28, column=2)

        global textBoxOOQty
        textBoxOOQty = self.textBoxOOQty

        # buttonSendOverseaOptionOrder
        self.buttonSendOverseaOptionOrder = tk.Button(self)
        self.buttonSendOverseaOptionOrder["text"] = "海外選擇權送出"
        self.buttonSendOverseaOptionOrder["command"] = self.buttonSendOverseaOptionOrder_Click
        self.buttonSendOverseaOptionOrder.grid(row=29, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False

    # checkBoxSpread
    def checkBoxSpread_CheckedChanged(self):
        global Spread
        if self.var1.get() == True:
            Spread = True
        else:
            Spread = False

    def buttonSendOverSeaFutureOrder_Click(self):
        pOrder = sk.OVERSEAFUTUREORDER()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxOFStockNo.get()
        pOrder.bstrExchangeNo = textBoxOFExchangeNo.get()
        pOrder.bstrYearMonth = textBoxOFYearMonth.get()
        pOrder.bstrYearMonth2 = textBoxOFYearMonth2.get()
        pOrder.bstrOrder = textBoxOFOrder.get()
        pOrder.bstrOrderNumerator = textBoxOFOrderNumerator.get()       
        pOrder.bstrTrigger = textBoxOFTrigger.get()
        pOrder.bstrTriggerNumerator = textBoxOFTriggerNumerator.get()
        pOrder.sNewClose = 0

        if (comboBoxOFTradeType.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxOFTradeType.get() == "FOK"):
            pOrder.sTradeType = 1
        elif (comboBoxOFTradeType.get() == "IOC"):
            pOrder.sTradeType = 2

        if (comboBoxOFBuySell.get() == "買進"):
            pOrder.sBuySell = 0
        elif (comboBoxOFBuySell.get() == "賣出"):
            pOrder.sBuySell = 1

        if (comboBoxOFDayTrade.get() == "否"):
            pOrder.sDayTrade = 0
        elif (comboBoxOFDayTrade.get() == "是"):
            pOrder.sDayTrade = 1

        if (comboBoxOFSpecialTradeType.get() == "LMT限價單"):
            pOrder.sSpecialTradeType = 0
        elif (comboBoxOFSpecialTradeType.get() == "MKT市價單"):
            pOrder.sSpecialTradeType = 1
        elif (comboBoxOFSpecialTradeType.get() == "STL停損限價"):
            pOrder.sSpecialTradeType = 2
        elif (comboBoxOFSpecialTradeType.get() == "STP停損市價"):
            pOrder.sSpecialTradeType = 3

        pOrder.nQty = int(textBoxOFQty.get())

        if (Spread == False):
            bstrMessage,nCode= m_pSKOrder.SendOverseaFutureOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

            msg = "【SendOverseaFutureOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')
        else:
            # 送出海期委託
            bstrMessage,nCode= m_pSKOrder.SendOverseaFutureSpreadOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

            msg = "【SendOverseaFutureSpreadOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')

    def buttonSendOverseaOptionOrder_Click(self):
        pOrder = sk.OVERSEAFUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxOOStockNo.get()
        pOrder.bstrExchangeNo = textBoxOOExchangeNo.get()
        pOrder.bstrYearMonth = textBoxOOYearMonth.get()
        pOrder.bstrOrder = textBoxOOOrder.get()
        pOrder.bstrOrderNumerator = textBoxOOOrderNumerator.get()
        pOrder.bstrOrderDenominator = textBoxbstrOrderDenominator.get()
        pOrder.bstrTrigger = textBoxOOTrigger.get()
        pOrder.bstrTriggerNumerator = textBoxOOTriggerNumerator.get()
        pOrder.sTradeType = 0

        if (comboBoxOOBuySell.get() == "買進"):
            pOrder.sBuySell = 0
        elif (comboBoxOOBuySell.get() == "賣出"):
            pOrder.sBuySell = 1

        if (comboBoxOODayTrade.get() == "否"):
            pOrder.sDayTrade = 0
        elif (comboBoxOODayTrade.get() == "是"):
            pOrder.sDayTrade = 1

        if (comboBoxOONewClose.get() == "新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxOONewClose.get() == "平倉"):
            pOrder.sNewClose = 1

        if (comboBoxOOSpecialTradeType.get() == "LMT限價單"):
            pOrder.sSpecialTradeType = 0
        elif (comboBoxOOSpecialTradeType.get() == "MKT市價單"):
            pOrder.sSpecialTradeType = 1
        elif (comboBoxOOSpecialTradeType.get() == "STL停損限價"):
            pOrder.sSpecialTradeType = 2
        elif (comboBoxOOSpecialTradeType.get() == "STP停損市價"):
            pOrder.sSpecialTradeType = 3

        pOrder.bstrStrikePrice = textBoxOOStrikePrice.get()

        pOrder.nQty = int(textBoxOOQty.get())

        if (comboBoxOOCallPut.get() == "CALL"):
            pOrder.sCallPut = 0
        elif (comboBoxOOCallPut.get() == "PUT"):
            pOrder.sCallPut = 1

        # 送出選擇權委託
        bstrMessage,nCode= m_pSKOrder.SendOverseaOptionOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendOverseaOptionOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # checkBoxSpread
        # 是否為價差交易

        self.checkBoxSpread = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxSpread["variable"] = self.var1
        self.checkBoxSpread["onvalue"] = True
        self.checkBoxSpread["offvalue"] = False
        self.checkBoxSpread["text"] = "是否為價差交易"
        self.checkBoxSpread["command"] = self.checkBoxSpread_CheckedChanged
        self.checkBoxSpread.grid( row = 1,column = 0)

        # textBoxOverSeaCancelOrderBySeqNo3
        tk.Label(self, text = "請輸入委託序號").grid(row=0, column=1)
            #輸入框
        self.textBoxOverSeaCancelOrderBySeqNo3 = tk.Entry(self)
        self.textBoxOverSeaCancelOrderBySeqNo3.grid(row=0, column=2)

        global textBoxOverSeaCancelOrderBySeqNo3
        textBoxOverSeaCancelOrderBySeqNo3 = self.textBoxOverSeaCancelOrderBySeqNo3

        # textBoxOverSeaCancelOrderByBookNo3
        tk.Label(self, text = "請輸入委託書號").grid(row=1, column=1)
            #輸入框
        self.textBoxOverSeaCancelOrderByBookNo3 = tk.Entry(self)
        self.textBoxOverSeaCancelOrderByBookNo3.grid(row=1, column=2)

        global textBoxOverSeaCancelOrderByBookNo3
        textBoxOverSeaCancelOrderByBookNo3 = self.textBoxOverSeaCancelOrderByBookNo3

        # buttonOverSeaCancelOrderBySeqNo
        self.buttonOverSeaCancelOrderBySeqNo = tk.Button(self)
        self.buttonOverSeaCancelOrderBySeqNo["text"] = "刪單(序號)"
        self.buttonOverSeaCancelOrderBySeqNo["command"] = self.buttonOverSeaCancelOrderBySeqNo_Click
        self.buttonOverSeaCancelOrderBySeqNo.grid(row=2, column=1)

        # buttonOverSeaCancelOrderByBookNo
        self.buttonOverSeaCancelOrderByBookNo = tk.Button(self)
        self.buttonOverSeaCancelOrderByBookNo["text"] = "刪單(書號)"
        self.buttonOverSeaCancelOrderByBookNo["command"] = self.buttonOverSeaCancelOrderByBookNo_Click
        self.buttonOverSeaCancelOrderByBookNo.grid(row=2, column=2)

        # textBoxOverseaFutureDecreaseQty3
        tk.Label(self, text = "請輸入減少數量").grid(row=3, column=1)
            #輸入框
        self.textBoxOverseaFutureDecreaseQty3 = tk.Entry(self)
        self.textBoxOverseaFutureDecreaseQty3.grid(row=3, column=2)

        global textBoxOverseaFutureDecreaseQty3
        textBoxOverseaFutureDecreaseQty3 = self.textBoxOverseaFutureDecreaseQty3

        # buttonOverSeaDecreaseOrderBySeqNo
        self.buttonOverSeaDecreaseOrderBySeqNo = tk.Button(self)
        self.buttonOverSeaDecreaseOrderBySeqNo["text"] = "減量(序號)"
        self.buttonOverSeaDecreaseOrderBySeqNo["command"] = self.buttonOverSeaDecreaseOrderBySeqNo_Click
        self.buttonOverSeaDecreaseOrderBySeqNo.grid(row=4, column=1)

        # textBoxOFExchangeNo3
        tk.Label(self, text = "交易所代號").grid(row=5, column=1)
            #輸入框
        self.textBoxOFExchangeNo3 = tk.Entry(self)
        self.textBoxOFExchangeNo3.grid(row=5, column=2)

        global textBoxOFExchangeNo3
        textBoxOFExchangeNo3 = self.textBoxOFExchangeNo3
        
        # textBoxOFStockNo3
        tk.Label(self, text = "海外期權代號").grid(row=6, column=1)
            #輸入框
        self.textBoxOFStockNo3 = tk.Entry(self)
        self.textBoxOFStockNo3.grid(row=6, column=2)

        global textBoxOFStockNo3
        textBoxOFStockNo3 = self.textBoxOFStockNo3
                
        # textBoxOFStockNo23
        tk.Label(self, text = "海外期價差代號").grid(row=7, column=1)
            #輸入框
        self.textBoxOFStockNo23 = tk.Entry(self)
        self.textBoxOFStockNo23.grid(row=7, column=2)

        global textBoxOFStockNo23
        textBoxOFStockNo23 = self.textBoxOFStockNo23
                        
        # textBoxOFYearMonth3
        tk.Label(self, text = "近月商品年月(YYYYMM)").grid(row=8, column=1)
            #輸入框
        self.textBoxOFYearMonth3 = tk.Entry(self)
        self.textBoxOFYearMonth3.grid(row=8, column=2)

        global textBoxOFYearMonth3
        textBoxOFYearMonth3 = self.textBoxOFYearMonth3
                                
        # textBoxOFYearMonth23
        tk.Label(self, text = "遠月商品年月(YYYYMM)").grid(row=9, column=1)
            #輸入框
        self.textBoxOFYearMonth23 = tk.Entry(self)
        self.textBoxOFYearMonth23.grid(row=9, column=2)

        global textBoxOFYearMonth23
        textBoxOFYearMonth23 = self.textBoxOFYearMonth23
                                        
        # textBoxOFOrder3
        tk.Label(self, text = "新委託價").grid(row=10, column=1)
            #輸入框
        self.textBoxOFOrder3 = tk.Entry(self)
        self.textBoxOFOrder3.grid(row=10, column=2)

        global textBoxOFOrder3
        textBoxOFOrder3 = self.textBoxOFOrder3
                                                
        # textBoxOFOrderNumerator3
        tk.Label(self, text = "新委託價分子").grid(row=11, column=1)
            #輸入框
        self.textBoxOFOrderNumerator3 = tk.Entry(self)
        self.textBoxOFOrderNumerator3.grid(row=11, column=2)

        global textBoxOFOrderNumerator3
        textBoxOFOrderNumerator3 = self.textBoxOFOrderNumerator3
                                                        
        # textBoxOFOrderDenominator3
        tk.Label(self, text = "新委託價分母").grid(row=12, column=1)
            #輸入框
        self.textBoxOFOrderDenominator3 = tk.Entry(self)
        self.textBoxOFOrderDenominator3.grid(row=12, column=2)

        global textBoxOFOrderDenominator3
        textBoxOFOrderDenominator3 = self.textBoxOFOrderDenominator3
                                                                
        # textBoxOOStrikePrice3
        tk.Label(self, text = "履約價(改期貨帶0)").grid(row=13, column=1)
            #輸入框
        self.textBoxOOStrikePrice3 = tk.Entry(self)
        self.textBoxOOStrikePrice3.grid(row=13, column=2)

        global textBoxOOStrikePrice3
        textBoxOOStrikePrice3 = self.textBoxOOStrikePrice3
        
        # comboBoxOOCallPut3
        tk.Label(self, text = "CALL/PUT").grid(row=14, column=1)
            #輸入框
        self.comboBoxOOCallPut3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOOCallPut3['values'] = Config.comboBoxOOCallPut3
        self.comboBoxOOCallPut3.grid(row=14, column=2)

        global comboBoxOOCallPut3
        comboBoxOOCallPut3 = self.comboBoxOOCallPut3

        # buttonOverSeaCorrectPriceByBookNo
        self.buttonOverSeaCorrectPriceByBookNo = tk.Button(self)
        self.buttonOverSeaCorrectPriceByBookNo["text"] = "改價(書號)"
        self.buttonOverSeaCorrectPriceByBookNo["command"] = self.buttonOverSeaCorrectPriceByBookNo_Click
        self.buttonOverSeaCorrectPriceByBookNo.grid(row=15, column=1)

        # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    # checkBoxSpread
    def checkBoxSpread_CheckedChanged(self):
        global Spread
        if self.var1.get() == True:
            Spread = True
        else:
            Spread = False
            
    def buttonOverSeaCancelOrderBySeqNo_Click(self):
        # 海外期貨委託删單(By委託序號)
        bstrMessage,nCode= m_pSKOrder.OverSeaCancelOrderBySeqNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxOverSeaCancelOrderBySeqNo3.get())

        msg = "【OverSeaCancelOrderBySeqNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonOverSeaCancelOrderByBookNo_Click(self):
        # 海外期貨委託删單(By委託書號)
        bstrMessage,nCode= m_pSKOrder.OverSeaCancelOrderByBookNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxOverSeaCancelOrderByBookNo3.get())

        msg = "【OverSeaCancelOrderByBookNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonOverSeaDecreaseOrderBySeqNo_Click(self):
        # 海期委託減量(By委託序號)
        bstrMessage,nCode= m_pSKOrder.OverSeaDecreaseOrderBySeqNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxOverSeaCancelOrderBySeqNo3.get(), int(textBoxOverseaFutureDecreaseQty3.get()))

        msg = "【OverSeaDecreaseOrderBySeqNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonOverSeaCorrectPriceByBookNo_Click(self):
        pOrder = sk.OVERSEAFUTUREORDERFORGW()

        pOrder.bstrBookNo = textBoxOverSeaCancelOrderByBookNo3.get()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrExchangeNo = textBoxOFExchangeNo3.get()
        pOrder.bstrStockNo = textBoxOFStockNo3.get()
        pOrder.bstrStockNo2 = textBoxOFStockNo23.get()
        pOrder.bstrYearMonth = textBoxOFYearMonth3.get()
        pOrder.bstrYearMonth2 = textBoxOFYearMonth23.get()
        pOrder.bstrOrderPrice = textBoxOFOrder3.get()
        pOrder.bstrOrderNumerator = textBoxOFOrderNumerator3.get()
        pOrder.bstrOrderDenominator = textBoxOFOrderDenominator3.get()
        pOrder.bstrStrikePrice = textBoxOOStrikePrice3.get()
        pOrder.nTradeType = 0
        pOrder.nSpecialTradeType = 0

        if (comboBoxOOCallPut3.get() == "CALL"):
            pOrder.nCallPut = 0
        elif (comboBoxOOCallPut3.get() == "PUT"):
            pOrder.nCallPut = 1

        if(textBoxOOStrikePrice3.get() != "0"): # 履約價不為0 => 選擇權
            # 海選改價 (By 委託書號)         
            bstrMessage, nCode = m_pSKOrder.OverSeaOptionCorrectPriceByBookNo(comboBoxUserID.get(), bAsyncOrder, pOrder)
            
            msg = "【OverSeaOptionCorrectPriceByBookNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')
        else:
            if (Spread == True): # 為價差改價
                # 海選價差改價 (By 委託書號)         
                bstrMessage, nCode = m_pSKOrder.OverSeaCorrectPriceSpreadByBookNo(comboBoxUserID.get(), bAsyncOrder, pOrder)
                            
                msg = "【OverSeaCorrectPriceSpreadByBookNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
                richTextBoxMethodMessage.insert('end',  msg + "\n")
                richTextBoxMethodMessage.see('end')
            else:
                # 海選改價 (By 委託書號)         
                bstrMessage, nCode = m_pSKOrder.OverSeaCorrectPriceByBookNo(comboBoxUserID.get(), bAsyncOrder, pOrder)
                                            
                msg = "【OverSeaCorrectPriceByBookNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # checkBoxSpread
        # 是否為價差交易

        self.checkBoxSpread = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxSpread["variable"] = self.var1
        self.checkBoxSpread["onvalue"] = True
        self.checkBoxSpread["offvalue"] = False
        self.checkBoxSpread["text"] = "是否為價差交易"
        self.checkBoxSpread["command"] = self.checkBoxSpread_CheckedChanged
        self.checkBoxSpread.grid( row = 0,column = 1)

        # textBoxOFExchangeNo3
        tk.Label(self, text = "交易所代號").grid(row=1, column=1)
            #輸入框
        self.textBoxOFExchangeNo3 = tk.Entry(self)
        self.textBoxOFExchangeNo3.grid(row=1, column=2)

        global textBoxOFExchangeNo3
        textBoxOFExchangeNo3 = self.textBoxOFExchangeNo3

        # textBoxOFStockNo3
        tk.Label(self, text = "海外期貨代號").grid(row=2, column=1)
            #輸入框
        self.textBoxOFStockNo3 = tk.Entry(self)
        self.textBoxOFStockNo3.grid(row=2, column=2)

        global textBoxOFStockNo3
        textBoxOFStockNo3 = self.textBoxOFStockNo3
        
        # textBoxOFYearMonth3
        tk.Label(self, text = "近月商品年月(YYYYMM)").grid(row=3, column=1)
            #輸入框
        self.textBoxOFYearMonth3 = tk.Entry(self)
        self.textBoxOFYearMonth3.grid(row=3, column=2)

        global textBoxOFYearMonth3
        textBoxOFYearMonth3 = self.textBoxOFYearMonth3
                
        # textBoxOFYearMonth23
        tk.Label(self, text = "遠月商品年月(YYYYMM)").grid(row=4, column=1)
            #輸入框
        self.textBoxOFYearMonth23 = tk.Entry(self)
        self.textBoxOFYearMonth23.grid(row=4, column=2)

        global textBoxOFYearMonth23
        textBoxOFYearMonth23 = self.textBoxOFYearMonth23
                        
        # textBoxOFOrder3
        tk.Label(self, text = "委託價").grid(row=5, column=1)
            #輸入框
        self.textBoxOFOrder3 = tk.Entry(self)
        self.textBoxOFOrder3.grid(row=5, column=2)

        global textBoxOFOrder3
        textBoxOFOrder3 = self.textBoxOFOrder3
                                
        # textBoxOFOrderNumerator3
        tk.Label(self, text = "委託價分子").grid(row=6, column=1)
            #輸入框
        self.textBoxOFOrderNumerator3 = tk.Entry(self)
        self.textBoxOFOrderNumerator3.grid(row=6, column=2)

        global textBoxOFOrderNumerator3
        textBoxOFOrderNumerator3 = self.textBoxOFOrderNumerator3
                                        
        # textBoxOFTrigger3
        tk.Label(self, text = "觸發價").grid(row=7, column=1)
            #輸入框
        self.textBoxOFTrigger3 = tk.Entry(self)
        self.textBoxOFTrigger3.grid(row=7, column=2)

        global textBoxOFTrigger3
        textBoxOFTrigger3 = self.textBoxOFTrigger3
                                                
        # textBoxOFTriggerNumerator3
        tk.Label(self, text = "觸發價分子").grid(row=8, column=1)
            #輸入框
        self.textBoxOFTriggerNumerator3 = tk.Entry(self)
        self.textBoxOFTriggerNumerator3.grid(row=8, column=2)

        global textBoxOFTriggerNumerator3
        textBoxOFTriggerNumerator3 = self.textBoxOFTriggerNumerator3
        
        # comboBoxOFBuySell3
        tk.Label(self, text = "買進/賣出").grid(row=9, column=1)
            #輸入框
        self.comboBoxOFBuySell3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOFBuySell3['values'] = Config.comboBoxOFBuySell3
        self.comboBoxOFBuySell3.grid(row=9, column=2)

        global comboBoxOFBuySell3
        comboBoxOFBuySell3 = self.comboBoxOFBuySell3
                
        # comboBoxOFDayTrade3
        tk.Label(self, text = "當沖").grid(row=10, column=1)
            #輸入框
        self.comboBoxOFDayTrade3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOFDayTrade3['values'] = Config.comboBoxOFDayTrade3
        self.comboBoxOFDayTrade3.grid(row=10, column=2)

        global comboBoxOFDayTrade3
        comboBoxOFDayTrade3 = self.comboBoxOFDayTrade3
                        
        # comboBoxOFTradeType3
        tk.Label(self, text = "ROD/FOK/IOC").grid(row=11, column=1)
            #輸入框
        self.comboBoxOFTradeType3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOFTradeType3['values'] = Config.comboBoxOFTradeType3
        self.comboBoxOFTradeType3.grid(row=11, column=2)

        global comboBoxOFTradeType3
        comboBoxOFTradeType3 = self.comboBoxOFTradeType3
                                
        # comboBoxOFSpecialTradeType3
        tk.Label(self, text = "LMT/MKT/STL/STP").grid(row=12, column=1)
            #輸入框
        self.comboBoxOFSpecialTradeType3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOFSpecialTradeType3['values'] = Config.comboBoxOFSpecialTradeType3
        self.comboBoxOFSpecialTradeType3.grid(row=12, column=2)

        global comboBoxOFSpecialTradeType3
        comboBoxOFSpecialTradeType3 = self.comboBoxOFSpecialTradeType3
                                                        
        # textBoxOFQty3
        tk.Label(self, text = "交易口數").grid(row=13, column=1)
            #輸入框
        self.textBoxOFQty3 = tk.Entry(self)
        self.textBoxOFQty3.grid(row=13, column=2)

        global textBoxOFQty3
        textBoxOFQty3 = self.textBoxOFQty3

        # buttonSendOverseaFutureSpreadProxyOrder
        self.buttonSendOverseaFutureSpreadProxyOrder = tk.Button(self)
        self.buttonSendOverseaFutureSpreadProxyOrder["text"] = "海外期貨送出"
        self.buttonSendOverseaFutureSpreadProxyOrder["command"] = self.buttonSendOverseaFutureSpreadProxyOrder_Click
        self.buttonSendOverseaFutureSpreadProxyOrder.grid(row=14, column=1)




        # textBoxOOExchangeNo3
        tk.Label(self, text = "交易所代號").grid(row=15, column=1)
            #輸入框
        self.textBoxOOExchangeNo3 = tk.Entry(self)
        self.textBoxOOExchangeNo3.grid(row=15, column=2)

        global textBoxOOExchangeNo3
        textBoxOOExchangeNo3 = self.textBoxOOExchangeNo3

        # textBoxOOStockNo3
        tk.Label(self, text = "海外選擇權代號").grid(row=16, column=1)
            #輸入框
        self.textBoxOOStockNo3 = tk.Entry(self)
        self.textBoxOOStockNo3.grid(row=16, column=2)

        global textBoxOOStockNo3
        textBoxOOStockNo3 = self.textBoxOOStockNo3
        
        # textBoxOOYearMonth3
        tk.Label(self, text = "近月商品年月(YYYYMM)").grid(row=17, column=1)
            #輸入框
        self.textBoxOOYearMonth3 = tk.Entry(self)
        self.textBoxOOYearMonth3.grid(row=17, column=2)

        global textBoxOOYearMonth3
        textBoxOOYearMonth3 = self.textBoxOOYearMonth3
                
        # textBoxOOOrder3
        tk.Label(self, text = "委託價").grid(row=18, column=1)
            #輸入框
        self.textBoxOOOrder3 = tk.Entry(self)
        self.textBoxOOOrder3.grid(row=18, column=2)

        global textBoxOOOrder3
        textBoxOOOrder3 = self.textBoxOOOrder3
                        
        # textBoxOOOrderNumerator3
        tk.Label(self, text = "委託價分子").grid(row=19, column=1)
            #輸入框
        self.textBoxOOOrderNumerator3 = tk.Entry(self)
        self.textBoxOOOrderNumerator3.grid(row=19, column=2)

        global textBoxOOOrderNumerator3
        textBoxOOOrderNumerator3 = self.textBoxOOOrderNumerator3
                                
        # textBoxbstrOrderDenominator3
        tk.Label(self, text = "分母").grid(row=19, column=3)
            #輸入框
        self.textBoxbstrOrderDenominator3 = tk.Entry(self)
        self.textBoxbstrOrderDenominator3.grid(row=19, column=4)

        global textBoxbstrOrderDenominator3
        textBoxbstrOrderDenominator3 = self.textBoxbstrOrderDenominator3
                                
        # textBoxOOTrigger3
        tk.Label(self, text = "觸發價").grid(row=20, column=1)
            #輸入框
        self.textBoxOOTrigger3 = tk.Entry(self)
        self.textBoxOOTrigger3.grid(row=20, column=2)

        global textBoxOOTrigger3
        textBoxOOTrigger3 = self.textBoxOOTrigger3
                                        
        # textBoxOOTriggerNumerator3
        tk.Label(self, text = "觸發價分子").grid(row=21, column=1)
            #輸入框
        self.textBoxOOTriggerNumerator3 = tk.Entry(self)
        self.textBoxOOTriggerNumerator3.grid(row=21, column=2)

        global textBoxOOTriggerNumerator3
        textBoxOOTriggerNumerator3 = self.textBoxOOTriggerNumerator3

        # comboBoxOOBuySell3
        tk.Label(self, text = "買進/賣出").grid(row=22, column=1)
            #輸入框
        self.comboBoxOOBuySell3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOOBuySell3['values'] = Config.comboBoxOOBuySell3
        self.comboBoxOOBuySell3.grid(row=22, column=2)

        global comboBoxOOBuySell3
        comboBoxOOBuySell3 = self.comboBoxOOBuySell3
        
        # comboBoxOONewClose3
        tk.Label(self, text = "新平倉").grid(row=23, column=1)
            #輸入框
        self.comboBoxOONewClose3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOONewClose3['values'] = Config.comboBoxOONewClose3
        self.comboBoxOONewClose3.grid(row=23, column=2)

        global comboBoxOONewClose3
        comboBoxOONewClose3 = self.comboBoxOONewClose3
                
        # comboBoxOODayTrade3
        tk.Label(self, text = "當沖").grid(row=24, column=1)
            #輸入框
        self.comboBoxOODayTrade3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOODayTrade3['values'] = Config.comboBoxOODayTrade3
        self.comboBoxOODayTrade3.grid(row=24, column=2)

        global comboBoxOODayTrade3
        comboBoxOODayTrade3 = self.comboBoxOODayTrade3
                        
        # comboBoxOOSpecialTradeType3
        tk.Label(self, text = "LMT/MKT/STL/STP").grid(row=25, column=1)
            #輸入框
        self.comboBoxOOSpecialTradeType3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOOSpecialTradeType3['values'] = Config.comboBoxOOSpecialTradeType3
        self.comboBoxOOSpecialTradeType3.grid(row=25, column=2)

        global comboBoxOOSpecialTradeType3
        comboBoxOOSpecialTradeType3 = self.comboBoxOOSpecialTradeType3
                                        
        # textBoxOOStrikePrice3
        tk.Label(self, text = "履約價").grid(row=26, column=1)
            #輸入框
        self.textBoxOOStrikePrice3 = tk.Entry(self)
        self.textBoxOOStrikePrice3.grid(row=26, column=2)

        global textBoxOOStrikePrice3
        textBoxOOStrikePrice3 = self.textBoxOOStrikePrice3
                                
        # comboBoxOOCallPut34
        tk.Label(self, text = "CALL/PUT").grid(row=27, column=1)
            #輸入框
        self.comboBoxOOCallPut34 = ttk.Combobox(self, state='readonly')
        self.comboBoxOOCallPut34['values'] = Config.comboBoxOOCallPut34
        self.comboBoxOOCallPut34.grid(row=27, column=2)

        global comboBoxOOCallPut34
        comboBoxOOCallPut34 = self.comboBoxOOCallPut34
                                                
        # textBoxOOQty3
        tk.Label(self, text = "交易口數").grid(row=28, column=1)
            #輸入框
        self.textBoxOOQty3 = tk.Entry(self)
        self.textBoxOOQty3.grid(row=28, column=2)

        global textBoxOOQty3
        textBoxOOQty3 = self.textBoxOOQty3

        # buttonSendOverseaOptionProxyOrder
        self.buttonSendOverseaOptionProxyOrder = tk.Button(self)
        self.buttonSendOverseaOptionProxyOrder["text"] = "海外選擇權送出"
        self.buttonSendOverseaOptionProxyOrder["command"] = self.buttonSendOverseaOptionProxyOrder_Click
        self.buttonSendOverseaOptionProxyOrder.grid(row=29, column=1)

    # checkBoxSpread
    def checkBoxSpread_CheckedChanged(self):
        global Spread
        if self.var1.get() == True:
            Spread = True
        else:
            Spread = False

    def buttonSendOverseaFutureSpreadProxyOrder_Click(self):
        pOrder = sk.OVERSEAFUTUREORDER()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxOFStockNo3.get()
        pOrder.bstrExchangeNo = textBoxOFExchangeNo3.get()
        pOrder.bstrYearMonth = textBoxOFYearMonth3.get()
        pOrder.bstrYearMonth2 = textBoxOFYearMonth23.get()
        pOrder.bstrOrder = textBoxOFOrder3.get()
        pOrder.bstrOrderNumerator = textBoxOFOrderNumerator3.get()       
        pOrder.bstrTrigger = textBoxOFTrigger3.get()
        pOrder.bstrTriggerNumerator = textBoxOFTriggerNumerator3.get()
        pOrder.sNewClose = 0

        if (comboBoxOFTradeType3.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxOFTradeType3.get() == "IOC"):
            pOrder.sTradeType = 1
        elif (comboBoxOFTradeType3.get() == "FOK"):
            pOrder.sTradeType = 2

        if (comboBoxOFBuySell3.get() == "買進"):
            pOrder.sBuySell = 0
        elif (comboBoxOFBuySell3.get() == "賣出"):
            pOrder.sBuySell = 1

        if (comboBoxOFDayTrade3.get() == "否"):
            pOrder.sDayTrade = 0
        elif (comboBoxOFDayTrade3.get() == "是"):
            pOrder.sDayTrade = 1

        if (comboBoxOFSpecialTradeType3.get() == "LMT限價單"):
            pOrder.sSpecialTradeType = 0
        elif (comboBoxOFSpecialTradeType3.get() == "MKT市價單"):
            pOrder.sSpecialTradeType = 1
        elif (comboBoxOFSpecialTradeType3.get() == "STL停損限價"):
            pOrder.sSpecialTradeType = 2
        elif (comboBoxOFSpecialTradeType3.get() == "STP停損市價"):
            pOrder.sSpecialTradeType = 3

        pOrder.nQty = int(textBoxOFQty3.get())

        if (Spread == False):
            bstrMessage,nCode= m_pSKOrder.SendOverseaFutureProxyOrder(comboBoxUserID.get(), pOrder)

            if bstrMessage is not None:
                msg = "【SendOverseaFutureProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            else:
                msg = "【SendOverseaFutureProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')
        else:
            # 送出海期委託
            bstrMessage,nCode= m_pSKOrder.SendOverseaFutureSpreadProxyOrder(comboBoxUserID.get(), pOrder)

            if bstrMessage is not None:
                msg = "【SendOverseaFutureSpreadProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            else:
                msg = "【SendOverseaFutureSpreadProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')

    def buttonSendOverseaOptionProxyOrder_Click(self):
        pOrder = sk.OVERSEAFUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxOOStockNo3.get()
        pOrder.bstrExchangeNo = textBoxOOExchangeNo3.get()
        pOrder.bstrYearMonth = textBoxOOYearMonth3.get()
        pOrder.bstrOrder = textBoxOOOrder3.get()
        pOrder.bstrOrderNumerator = textBoxOOOrderNumerator3.get()
        pOrder.bstrOrderDenominator = textBoxbstrOrderDenominator3.get()
        pOrder.bstrTrigger = textBoxOOTrigger3.get()
        pOrder.bstrTriggerNumerator = textBoxOOTriggerNumerator3.get()
        pOrder.sTradeType = 0

        if (comboBoxOOBuySell3.get() == "買進"):
            pOrder.sBuySell = 0
        elif (comboBoxOOBuySell3.get() == "賣出"):
            pOrder.sBuySell = 1

        if (comboBoxOODayTrade3.get() == "否"):
            pOrder.sDayTrade = 0
        elif (comboBoxOODayTrade3.get() == "是"):
            pOrder.sDayTrade = 1

        if (comboBoxOONewClose3.get() == "新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxOONewClose3.get() == "平倉"):
            pOrder.sNewClose = 1

        if (comboBoxOOSpecialTradeType3.get() == "LMT限價單"):
            pOrder.sSpecialTradeType = 0
        elif (comboBoxOOSpecialTradeType3.get() == "MKT市價單"):
            pOrder.sSpecialTradeType = 1
        elif (comboBoxOOSpecialTradeType3.get() == "STL停損限價"):
            pOrder.sSpecialTradeType = 2
        elif (comboBoxOOSpecialTradeType3.get() == "STP停損市價"):
            pOrder.sSpecialTradeType = 3

        pOrder.bstrStrikePrice = textBoxOOStrikePrice3.get()

        pOrder.nQty = int(textBoxOOQty3.get())

        if (comboBoxOOCallPut34.get() == "CALL"):
            pOrder.sCallPut = 0
        elif (comboBoxOOCallPut34.get() == "PUT"):
            pOrder.sCallPut = 1

        # 送出選擇權委託
        bstrMessage,nCode= m_pSKOrder.SendOverseaOptionProxyOrder(comboBoxUserID.get(), pOrder)
        
        if bstrMessage is not None:
            msg = "【SendOverseaOptionProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
            msg = "【SendOverseaOptionProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

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

        # textBoxOverSeaCancelOrderBySeqNo5
        tk.Label(self, text = "請輸入委託序號").grid(row=0, column=1)
            #輸入框
        self.textBoxOverSeaCancelOrderBySeqNo5 = tk.Entry(self)
        self.textBoxOverSeaCancelOrderBySeqNo5.grid(row=0, column=2)

        global textBoxOverSeaCancelOrderBySeqNo5
        textBoxOverSeaCancelOrderBySeqNo5 = self.textBoxOverSeaCancelOrderBySeqNo5

        # textBoxOverSeaCancelOrderByBookNo5
        tk.Label(self, text = "請輸入委託書號").grid(row=1, column=1)
            #輸入框
        self.textBoxOverSeaCancelOrderByBookNo5 = tk.Entry(self)
        self.textBoxOverSeaCancelOrderByBookNo5.grid(row=1, column=2)

        global textBoxOverSeaCancelOrderByBookNo5
        textBoxOverSeaCancelOrderByBookNo5 = self.textBoxOverSeaCancelOrderByBookNo5

        # textBoxOverseaFutureDecreaseQty5
        tk.Label(self, text = "請輸入減少數量").grid(row=2, column=1)
            #輸入框
        self.textBoxOverseaFutureDecreaseQty5 = tk.Entry(self)
        self.textBoxOverseaFutureDecreaseQty5.grid(row=2, column=2)

        global textBoxOverseaFutureDecreaseQty5
        textBoxOverseaFutureDecreaseQty5 = self.textBoxOverseaFutureDecreaseQty5

        # textBoxOFExchangeNo5
        tk.Label(self, text = "交易所代號").grid(row=3, column=1)
            #輸入框
        self.textBoxOFExchangeNo5 = tk.Entry(self)
        self.textBoxOFExchangeNo5.grid(row=3, column=2)

        global textBoxOFExchangeNo5
        textBoxOFExchangeNo5 = self.textBoxOFExchangeNo5

        # textBoxOFStockNo5
        tk.Label(self, text = "海外期權代號").grid(row=4, column=1)
            #輸入框
        self.textBoxOFStockNo5 = tk.Entry(self)
        self.textBoxOFStockNo5.grid(row=4, column=2)

        global textBoxOFStockNo5
        textBoxOFStockNo5 = self.textBoxOFStockNo5
        
        # textBoxOFYearMonth5
        tk.Label(self, text = "近月商品年月(YYYYMM)").grid(row=5, column=1)
            #輸入框
        self.textBoxOFYearMonth5 = tk.Entry(self)
        self.textBoxOFYearMonth5.grid(row=5, column=2)

        global textBoxOFYearMonth5
        textBoxOFYearMonth5 = self.textBoxOFYearMonth5
                
        # textBoxOFYearMonth25
        tk.Label(self, text = "遠月商品年月(YYYYMM)").grid(row=6, column=1)
            #輸入框
        self.textBoxOFYearMonth25 = tk.Entry(self)
        self.textBoxOFYearMonth25.grid(row=6, column=2)

        global textBoxOFYearMonth25
        textBoxOFYearMonth25 = self.textBoxOFYearMonth25
                        
        # textBoxOFOrder5
        tk.Label(self, text = "新委託價").grid(row=7, column=1)
            #輸入框
        self.textBoxOFOrder5 = tk.Entry(self)
        self.textBoxOFOrder5.grid(row=7, column=2)

        global textBoxOFOrder5
        textBoxOFOrder5 = self.textBoxOFOrder5
                                
        # textBoxOFOrderNumerator5
        tk.Label(self, text = "新委託價分子").grid(row=8, column=1)
            #輸入框
        self.textBoxOFOrderNumerator5 = tk.Entry(self)
        self.textBoxOFOrderNumerator5.grid(row=8, column=2)

        global textBoxOFOrderNumerator5
        textBoxOFOrderNumerator5 = self.textBoxOFOrderNumerator5
                                        
        # textBoxOFOrderDenominator5
        tk.Label(self, text = "新委託價分母").grid(row=9, column=1)
            #輸入框
        self.textBoxOFOrderDenominator5 = tk.Entry(self)
        self.textBoxOFOrderDenominator5.grid(row=9, column=2)

        global textBoxOFOrderDenominator5
        textBoxOFOrderDenominator5 = self.textBoxOFOrderDenominator5

        # comboBoxOONewClose5
        tk.Label(self, text = "新平倉").grid(row=10, column=1)
            #輸入框
        self.comboBoxOONewClose5 = ttk.Combobox(self, state='readonly')
        self.comboBoxOONewClose5['values'] = Config.comboBoxOONewClose5
        self.comboBoxOONewClose5.grid(row=10, column=2)

        global comboBoxOONewClose5
        comboBoxOONewClose5 = self.comboBoxOONewClose5
        
        # comboBoxOOSpecialTradeType5
        tk.Label(self, text = "LMT/MKT/STL/STP").grid(row=11, column=1)
            #輸入框
        self.comboBoxOOSpecialTradeType5 = ttk.Combobox(self, state='readonly')
        self.comboBoxOOSpecialTradeType5['values'] = Config.comboBoxOOSpecialTradeType5
        self.comboBoxOOSpecialTradeType5.grid(row=11, column=2)

        global comboBoxOOSpecialTradeType5
        comboBoxOOSpecialTradeType5 = self.comboBoxOOSpecialTradeType5
                                        
        # textBoxOOStrikePrice5
        tk.Label(self, text = "履約價(改期貨帶0)").grid(row=12, column=1)
            #輸入框
        self.textBoxOOStrikePrice5 = tk.Entry(self)
        self.textBoxOOStrikePrice5.grid(row=12, column=2)

        global textBoxOOStrikePrice5
        textBoxOOStrikePrice5 = self.textBoxOOStrikePrice5
                
        # comboBoxOOCallPut5
        tk.Label(self, text = "CALL/PUT").grid(row=13, column=1)
            #輸入框
        self.comboBoxOOCallPut5 = ttk.Combobox(self, state='readonly')
        self.comboBoxOOCallPut5['values'] = Config.comboBoxOOCallPut5
        self.comboBoxOOCallPut5.grid(row=13, column=2)

        global comboBoxOOCallPut5
        comboBoxOOCallPut5 = self.comboBoxOOCallPut5
                        
        # comboBoxnSpreadFlag5
        tk.Label(self, text = "市場別").grid(row=14, column=1)
            #輸入框
        self.comboBoxnSpreadFlag5 = ttk.Combobox(self, state='readonly')
        self.comboBoxnSpreadFlag5['values'] = Config.comboBoxnSpreadFlag5
        self.comboBoxnSpreadFlag5.grid(row=14, column=2)

        global comboBoxnSpreadFlag5
        comboBoxnSpreadFlag5 = self.comboBoxnSpreadFlag5
                        
        # comboBoxnAlterType5
        tk.Label(self, text = "異動項目").grid(row=15, column=1)
            #輸入框
        self.comboBoxnAlterType5 = ttk.Combobox(self, state='readonly')
        self.comboBoxnAlterType5['values'] = Config.comboBoxnAlterType5
        self.comboBoxnAlterType5.grid(row=15, column=2)

        global comboBoxnAlterType5
        comboBoxnAlterType5 = self.comboBoxnAlterType5


        # buttonSendOverseaFutureProxyAlter
        self.buttonSendOverseaFutureProxyAlter = tk.Button(self)
        self.buttonSendOverseaFutureProxyAlter["text"] = "海外期貨刪改單送出"
        self.buttonSendOverseaFutureProxyAlter["command"] = self.buttonSendOverseaFutureProxyAlter_Click
        self.buttonSendOverseaFutureProxyAlter.grid(row=16, column=1)
    
    def buttonSendOverseaFutureProxyAlter_Click(self):
        pSKProxyOrder = sk.OVERSEAFUTUREORDER()
        pSKProxyOrder.bstrFullAccount = comboBoxAccount.get()
        pSKProxyOrder.bstrExchangeNo = textBoxOFExchangeNo5.get()
        pSKProxyOrder.bstrStockNo = textBoxOFStockNo5.get()
        pSKProxyOrder.bstrYearMonth = textBoxOFYearMonth5.get()
        pSKProxyOrder.bstrYearMonth2 = textBoxOFYearMonth25.get()
        pSKProxyOrder.bstrOrder = textBoxOFOrder5.get()
        pSKProxyOrder.bstrOrderNumerator = textBoxOFOrderNumerator5.get()
        pSKProxyOrder.bstrOrderDenominator = textBoxOFOrderDenominator5.get()
        pSKProxyOrder.bstrStrikePrice = textBoxOOStrikePrice5.get()

        if (comboBoxOOCallPut5.get() == "CALL"):
            pSKProxyOrder.sCallPut = 0
        elif (comboBoxOOCallPut5.get() == "PUT"):
            pSKProxyOrder.sCallPut = 1

        if (comboBoxOONewClose5.get() == "新倉"):
            pSKProxyOrder.sNewClose = 0
        elif (comboBoxOONewClose5.get() == "平倉"):
            pSKProxyOrder.sNewClose = 1

        pSKProxyOrder.sTradeType = 0

        if (comboBoxOOSpecialTradeType5.get() == "LMT限價單"):
            pSKProxyOrder.sSpecialTradeType = 0
        elif (comboBoxOOSpecialTradeType5.get() == "MKT市價單"):
            pSKProxyOrder.sSpecialTradeType = 1
        elif (comboBoxOOSpecialTradeType5.get() == "STL停損限價"):
            pSKProxyOrder.sSpecialTradeType = 2
        elif (comboBoxOOSpecialTradeType5.get() == "STP停損市價"):
            pSKProxyOrder.sSpecialTradeType = 3

        pSKProxyOrder.nQty = int(textBoxOverseaFutureDecreaseQty5.get())

        pSKProxyOrder.bstrBookNo = textBoxOverSeaCancelOrderByBookNo5.get()
        pSKProxyOrder.bstrSeqNo = textBoxOverSeaCancelOrderBySeqNo5.get()

        if (comboBoxnSpreadFlag5.get() == "0 :OF海期"):
            pSKProxyOrder.nSpreadFlag = 0
        elif (comboBoxnSpreadFlag5.get() == "1: OF-spread 海期價差"):
            pSKProxyOrder.nSpreadFlag = 1
        elif (comboBoxnSpreadFlag5.get() == "2: OO 海選"):
            pSKProxyOrder.nSpreadFlag = 2

        if (comboBoxnAlterType5.get() == "0: Cancel 刪單"):
            pSKProxyOrder.nAlterType = 0
        elif (comboBoxnAlterType5.get() == "1: Decrease 減量"):
            pSKProxyOrder.nAlterType = 1
        elif (comboBoxnAlterType5.get() == "2: Correct 改價"):
            pSKProxyOrder.nAlterType = 2

        # 經由proxy server送出海期選刪改單
        bstrMessage,nCode= m_pSKOrder.SendOverseaFutureProxyAlter(comboBoxUserID.get(), pSKProxyOrder)

        if bstrMessage is not None:
             msg = "【SendOverseaFutureProxyAlter】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
             msg = "【SendOverseaFutureProxyAlter】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

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

def popup_window_Load():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Load")

    # 建立 Frame 作為 LoadForm，並添加到彈出窗口
    popup_LoadForm = LoadForm(popup)
    popup_LoadForm.pack(fill=tk.BOTH, expand=True)

def popup_window_WithDraw():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("WithDraw")

    # 建立 Frame 作為 WithDrawForm，並添加到彈出窗口
    popup_WithDrawForm = WithDrawForm(popup)
    popup_WithDrawForm.pack(fill=tk.BOTH, expand=True)

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

#開啟Tk視窗
if __name__ == '__main__':
    #建立主視窗
    root = tk.Tk()
    root.title("OFOrder")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)


    # 開啟Read視窗的按鈕
    popup_button_Read = tk.Button(root, text="查詢", command=popup_window_Read)
    popup_button_Read.grid(row = 1, column= 0)

    # 開啟Load視窗的按鈕
    popup_button_Load = tk.Button(root, text="下載商品檔", command=popup_window_Load)
    popup_button_Load.grid(row = 2, column= 0)

    # 開啟WithDraw視窗的按鈕
    popup_button_WithDraw = tk.Button(root, text="出入金互轉", command=popup_window_WithDraw)
    popup_button_WithDraw.grid(row = 3, column= 0)

    # 開啟Send視窗的按鈕
    popup_button_Send = tk.Button(root, text="一般下單", command=popup_window_Send)
    popup_button_Send.grid(row = 4, column= 0)

    # 開啟Update視窗的按鈕
    popup_button_Update = tk.Button(root, text="一般刪改單", command=popup_window_Update)
    popup_button_Update.grid(row = 5, column= 0)

    # 開啟SendProxy視窗的按鈕
    popup_button_SendProxy = tk.Button(root, text="Proxy下單", command=popup_window_SendProxy)
    popup_button_SendProxy.grid(row = 6, column= 0)

    # 開啟UpdateProxy視窗的按鈕
    popup_button_UpdateProxy = tk.Button(root, text="Proxy刪改單", command=popup_window_UpdateProxy)
    popup_button_UpdateProxy.grid(row = 7, column= 0)

    root.mainloop()

#==========================================
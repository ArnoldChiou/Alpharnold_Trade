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
# 是否為複式單
isDuplexOrder = False


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
    # (新)期貨未平倉GW。透過呼叫 GetOpenInterestGW 後，資訊由該事件回傳
    def OnOpenInterest(self, bstrData):
        msg = "【OnOpenInterest】" + bstrData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    # 國內期貨權益數。透過呼叫 GetFutureRights 後，資訊由該事件回傳
    def OnFutureRights(self, bstrData):
        msg = "【OnFutureRights】" + bstrData;
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

        # buttonGetOpenInterestGW
        self.buttonGetOpenInterestGW = tk.Button(self)
        self.buttonGetOpenInterestGW["text"] = "期貨未平倉"
        self.buttonGetOpenInterestGW["command"] = self.buttonGetOpenInterestGW_Click
        self.buttonGetOpenInterestGW.grid(row=0, column=1)

        # buttonGetFutureRights
        self.buttonGetFutureRights = tk.Button(self)
        self.buttonGetFutureRights["text"] = "國內權益數"
        self.buttonGetFutureRights["command"] = self.buttonGetFutureRights_Click
        self.buttonGetFutureRights.grid(row=1, column=1)

        # comboBoxCoinType
        tk.Label(self, text = "幣別").grid(row = 1,column = 2)
        self.comboBoxCoinType = ttk.Combobox(self, state='readonly')
        self.comboBoxCoinType['values'] = Config.comboBoxCoinType
        self.comboBoxCoinType.grid(row=1, column=3)

        global comboBoxCoinType
        comboBoxCoinType = self.comboBoxCoinType
        
    def buttonGetOpenInterestGW_Click(self):
        nCode = m_pSKOrder.GetOpenInterestGW(comboBoxUserID.get(), comboBoxAccount.get(), 1)

        msg = "【buttonGetOpenInterestGW】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonGetFutureRights_Click(self):

        if (comboBoxCoinType.get() == "0:全幣別"):
            sCoinType = 0
        elif (comboBoxCoinType.get() == "1:基幣(台幣TWD)"):
            sCoinType = 1
        elif (comboBoxCoinType.get() == "2:人民幣RMB"):
            sCoinType = 2
    
        nCode = m_pSKOrder.GetFutureRights(comboBoxUserID.get(), comboBoxAccount.get(), sCoinType)

        msg = "【GetFutureRights】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#OffSetForm
class OffSetForm(tk.Frame):
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

        # comboBoxSendTFOffSetnCommodity
        tk.Label(self, text = "類別").grid(row = 0,column = 1)
        self.comboBoxSendTFOffSetnCommodity = ttk.Combobox(self, state='readonly')
        self.comboBoxSendTFOffSetnCommodity['values'] = Config.comboBoxSendTFOffSetnCommodity
        self.comboBoxSendTFOffSetnCommodity.grid(row=0, column=2)

        global comboBoxSendTFOffSetnCommodity
        comboBoxSendTFOffSetnCommodity = self.comboBoxSendTFOffSetnCommodity

        # textBoxSendTFOffSetbstrYearMonth
        tk.Label(self, text = "年月").grid(row=1, column=1)
        #輸入框
        self.textBoxSendTFOffSetbstrYearMonth = tk.Entry(self)
        self.textBoxSendTFOffSetbstrYearMonth.grid(row=1, column=2)

        global textBoxSendTFOffSetbstrYearMonth
        textBoxSendTFOffSetbstrYearMonth = self.textBoxSendTFOffSetbstrYearMonth

        # comboBoxSendTFOffSetnBuySell
        tk.Label(self, text = "買賣別").grid(row = 1,column = 3)
        self.comboBoxSendTFOffSetnBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxSendTFOffSetnBuySell['values'] = Config.comboBoxSendTFOffSetnBuySell
        self.comboBoxSendTFOffSetnBuySell.grid(row=1, column=4)

        global comboBoxSendTFOffSetnBuySell
        comboBoxSendTFOffSetnBuySell = self.comboBoxSendTFOffSetnBuySell

        # textBoxSendTFOffSetnQty
        tk.Label(self, text = "互抵口數").grid(row=2, column=1)
        #輸入框
        self.textBoxSendTFOffSetnQty = tk.Entry(self)
        self.textBoxSendTFOffSetnQty.grid(row=2, column=2)

        global textBoxSendTFOffSetnQty
        textBoxSendTFOffSetnQty = self.textBoxSendTFOffSetnQty

        # buttonSendTFOffSet
        self.buttonSendTFOffSet = tk.Button(self)
        self.buttonSendTFOffSet["text"] = "大小台電金互抵"
        self.buttonSendTFOffSet["command"] = self.buttonSendTFOffSet_Click
        self.buttonSendTFOffSet.grid(row=3, column=1)

        global buttonSendTFOffSet
        buttonSendTFOffSet = self.buttonSendTFOffSet

        # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False

    def buttonSendTFOffSet_Click(self):
        if (comboBoxSendTFOffSetnCommodity.get() == "大小台"):
            nCommodity = 0
        elif (comboBoxSendTFOffSetnCommodity.get() == "大小電"):
            nCommodity = 1
        elif (comboBoxSendTFOffSetnCommodity.get() == "大小金"):
            nCommodity = 2

        if (comboBoxSendTFOffSetnBuySell.get() == "多方(買)"):
            nBuySell = 0
        elif (comboBoxSendTFOffSetnBuySell.get() == "空方(賣)"):
            nBuySell = 1

        nQty = int(textBoxSendTFOffSetnQty.get())

        bstrMessage, nCode = m_pSKOrder.SendTFOffSet(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), nCommodity, textBoxSendTFOffSetbstrYearMonth.get(), nBuySell, nQty)

        msg = "【SendTFOffSet】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#AssembleForm
class AssembleForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # comboBoxAssembleOptions
        tk.Label(self, text = "類別").grid(row = 0,column = 1)
        self.comboBoxAssembleOptions = ttk.Combobox(self, state='readonly')
        self.comboBoxAssembleOptions['values'] = Config.comboBoxAssembleOptions
        self.comboBoxAssembleOptions.grid(row=0, column=2)

        global comboBoxAssembleOptions
        comboBoxAssembleOptions = self.comboBoxAssembleOptions

        # textBoxbstrStockNo
        tk.Label(self, text = "選擇權代號1").grid(row=1, column=1)
        #輸入框
        self.textBoxbstrStockNo = tk.Entry(self)
        self.textBoxbstrStockNo.grid(row=1, column=2)

        global textBoxbstrStockNo
        textBoxbstrStockNo = self.textBoxbstrStockNo

        # textBoxbstrStockNo2
        tk.Label(self, text = "選擇權代號2").grid(row=1, column=3)
        #輸入框
        self.textBoxbstrStockNo2 = tk.Entry(self)
        self.textBoxbstrStockNo2.grid(row=1, column=4)

        global textBoxbstrStockNo2
        textBoxbstrStockNo2 = self.textBoxbstrStockNo2

        # comboBoxsBuySell
        tk.Label(self, text = "0:買進 1:賣出").grid(row = 2,column = 1)
        self.comboBoxsBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxsBuySell['values'] = Config.comboBoxsBuySell
        self.comboBoxsBuySell.grid(row=2, column=2)

        global comboBoxsBuySell
        comboBoxsBuySell = self.comboBoxsBuySell

        # comboBoxsBuySell2
        tk.Label(self, text = "0:買進 1:賣出").grid(row = 2,column = 3)
        self.comboBoxsBuySell2 = ttk.Combobox(self, state='readonly')
        self.comboBoxsBuySell2['values'] = Config.comboBoxsBuySell2
        self.comboBoxsBuySell2.grid(row=2, column=4)

        global comboBoxsBuySell2
        comboBoxsBuySell2 = self.comboBoxsBuySell2

        # textBoxnQty
        tk.Label(self, text = "交易口數").grid(row=3, column=1)
        #輸入框
        self.textBoxnQty = tk.Entry(self)
        self.textBoxnQty.grid(row=3, column=2)

        global textBoxnQty
        textBoxnQty = self.textBoxnQty

        # buttonAssembleOptions
        self.buttonAssembleOptions = tk.Button(self)
        self.buttonAssembleOptions["text"] = "選擇權部位送出"
        self.buttonAssembleOptions["command"] = self.buttonAssembleOptions_Click
        self.buttonAssembleOptions.grid(row=4, column=1)

        global buttonAssembleOptions
        buttonAssembleOptions = self.buttonAssembleOptions

    def buttonAssembleOptions_Click(self):
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNo.get()
        pOrder.bstrStockNo2 = textBoxbstrStockNo2.get()

        if (comboBoxsBuySell.get() == "買進"):
            pOrder.sBuySell = 0
        elif (comboBoxsBuySell.get() == "賣出"):
            pOrder.sBuySell = 1

        if (comboBoxsBuySell2.get() == "買進"):
            pOrder.sBuySell2 = 0
        elif (comboBoxsBuySell2.get() == "賣出"):
            pOrder.sBuySell2 = 1
        pOrder.nQty = int(textBoxnQty.get())

        if (comboBoxAssembleOptions.get() == "組合"):
            # 國內選擇權組合部位
            bstrMessage, nCode = m_pSKOrder.AssembleOptions(comboBoxUserID.get(), bAsyncOrder, pOrder)

            msg = "【AssembleOptions】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')

        elif (comboBoxAssembleOptions.get() == "複式單拆解"):
            # 國內選擇權複式單拆解
            bstrMessage, nCode = m_pSKOrder.DisassembleOptions(comboBoxUserID.get(), bAsyncOrder, pOrder)

            msg = "【DisassembleOptions】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')
        elif (comboBoxAssembleOptions.get() == "雙邊了結"):
            # 國內選擇權雙邊部位了結
            bstrMessage, nCode = m_pSKOrder.CoverAllProduct(comboBoxUserID.get(), bAsyncOrder, pOrder)

            msg = "【CoverAllProduct】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # checkBoxSendDuplexOrder
        # 是否為複式單

        self.checkBoxSendDuplexOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxSendDuplexOrder["variable"] = self.var1
        self.checkBoxSendDuplexOrder["onvalue"] = True
        self.checkBoxSendDuplexOrder["offvalue"] = False
        self.checkBoxSendDuplexOrder["text"] = "是否為複式單"
        self.checkBoxSendDuplexOrder["command"] = self.checkBoxSendDuplexOrder_CheckedChanged
        self.checkBoxSendDuplexOrder.grid( row = 0,column = 1)

        # textBoxFutureID
        tk.Label(self, text = "期貨代號").grid(row=1, column=1)
            #輸入框
        self.textBoxFutureID = tk.Entry(self)
        self.textBoxFutureID.grid(row=1, column=2)

        global textBoxFutureID
        textBoxFutureID = self.textBoxFutureID

        # comboBoxFutureDayTrade
        tk.Label(self, text = "當沖").grid(row=2, column=1)
            #輸入框
        self.comboBoxFutureDayTrade = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureDayTrade['values'] = Config.comboBoxFutureDayTrade
        self.comboBoxFutureDayTrade.grid(row=2, column=2)

        global comboBoxFutureDayTrade
        comboBoxFutureDayTrade = self.comboBoxFutureDayTrade

        # comboBoxFutureReserved
        tk.Label(self, text = "盤別").grid(row=3, column=1)
            #輸入框
        self.comboBoxFutureReserved = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureReserved['values'] = Config.comboBoxFutureReserved
        self.comboBoxFutureReserved.grid(row=3, column=2)

        global comboBoxFutureReserved
        comboBoxFutureReserved = self.comboBoxFutureReserved

        # comboBoxFutureNewClose
        tk.Label(self, text = "新平倉").grid(row=4, column=1)
            #輸入框
        self.comboBoxFutureNewClose = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureNewClose['values'] = Config.comboBoxFutureNewClose
        self.comboBoxFutureNewClose.grid(row=4, column=2)

        global comboBoxFutureNewClose
        comboBoxFutureNewClose = self.comboBoxFutureNewClose

        # textBoxFutureQty
        tk.Label(self, text = "口數").grid(row=5, column=1)
            #輸入框
        self.textBoxFutureQty = tk.Entry(self)
        self.textBoxFutureQty.grid(row=5, column=2)

        global textBoxFutureQty
        textBoxFutureQty = self.textBoxFutureQty

        # comboBoxFutureTradeType
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=6, column=1)
            #輸入框
        self.comboBoxFutureTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureTradeType['values'] = Config.comboBoxFutureTradeType
        self.comboBoxFutureTradeType.grid(row=6, column=2)

        global comboBoxFutureTradeType
        comboBoxFutureTradeType = self.comboBoxFutureTradeType

        # textBoxFuturePrice
        tk.Label(self, text = "委託價").grid(row=7, column=1)
            #輸入框
        self.textBoxFuturePrice = tk.Entry(self)
        self.textBoxFuturePrice.grid(row=7, column=2)

        global textBoxFuturePrice
        textBoxFuturePrice = self.textBoxFuturePrice

        # comboBoxFutureBuySell
        tk.Label(self, text = "買進/賣出").grid(row=8, column=1)
            #輸入框
        self.comboBoxFutureBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureBuySell['values'] = Config.comboBoxFutureBuySell
        self.comboBoxFutureBuySell.grid(row=8, column=2)

        global comboBoxFutureBuySell
        comboBoxFutureBuySell = self.comboBoxFutureBuySell

        # buttonSendFutureOrderCLR
        self.buttonSendFutureOrderCLR = tk.Button(self)
        self.buttonSendFutureOrderCLR["text"] = "期貨送出"
        self.buttonSendFutureOrderCLR["command"] = self.buttonSendFutureOrderCLR_Click
        self.buttonSendFutureOrderCLR.grid(row=9, column=1)

        # textBoxOptionID
        tk.Label(self, text = "選擇權代號").grid(row=10, column=1)
            #輸入框
        self.textBoxOptionID = tk.Entry(self)
        self.textBoxOptionID.grid(row=10, column=2)

        global textBoxOptionID
        textBoxOptionID = self.textBoxOptionID

        # textBoxOptionID2
        tk.Label(self, text = "選擇權代號2(複式單)").grid(row=11, column=1)
            #輸入框
        self.textBoxOptionID2 = tk.Entry(self)
        self.textBoxOptionID2.grid(row=11, column=2)

        global textBoxOptionID2
        textBoxOptionID2 = self.textBoxOptionID2

        # comboBoxOptionDayTrade
        tk.Label(self, text = "當沖").grid(row=12, column=1)
            #輸入框
        self.comboBoxOptionDayTrade = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionDayTrade['values'] = Config.comboBoxOptionDayTrade
        self.comboBoxOptionDayTrade.grid(row=12, column=2)

        global comboBoxOptionDayTrade
        comboBoxOptionDayTrade = self.comboBoxOptionDayTrade

        # comboBoxOptionReserved
        tk.Label(self, text = "盤別").grid(row=13, column=1)
            #輸入框
        self.comboBoxOptionReserved = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionReserved['values'] = Config.comboBoxOptionReserved
        self.comboBoxOptionReserved.grid(row=13, column=2)

        global comboBoxOptionReserved
        comboBoxOptionReserved = self.comboBoxOptionReserved

        # comboBoxOptionNewClose
        tk.Label(self, text = "新平倉").grid(row=14, column=1)
            #輸入框
        self.comboBoxOptionNewClose = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionNewClose['values'] = Config.comboBoxOptionNewClose
        self.comboBoxOptionNewClose.grid(row=14, column=2)

        global comboBoxOptionNewClose
        comboBoxOptionNewClose = self.comboBoxOptionNewClose

        # textBoxOptionQty
        tk.Label(self, text = "口數").grid(row=15, column=1)
            #輸入框
        self.textBoxOptionQty = tk.Entry(self)
        self.textBoxOptionQty.grid(row=15, column=2)

        global textBoxOptionQty
        textBoxOptionQty = self.textBoxOptionQty

        # comboBoxOptionTradeType
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=16, column=1)
            #輸入框
        self.comboBoxOptionTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionTradeType['values'] = Config.comboBoxOptionTradeType
        self.comboBoxOptionTradeType.grid(row=16, column=2)

        global comboBoxOptionTradeType
        comboBoxOptionTradeType = self.comboBoxOptionTradeType

        # textBoxOptionPrice
        tk.Label(self, text = "委託價").grid(row=17, column=1)
            #輸入框
        self.textBoxOptionPrice = tk.Entry(self)
        self.textBoxOptionPrice.grid(row=17, column=2)

        global textBoxOptionPrice
        textBoxOptionPrice = self.textBoxOptionPrice

        # comboBoxOptionBuySell
        tk.Label(self, text = "買進/賣出").grid(row=18, column=1)
            #輸入框
        self.comboBoxOptionBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionBuySell['values'] = Config.comboBoxOptionBuySell
        self.comboBoxOptionBuySell.grid(row=18, column=2)

        global comboBoxOptionBuySell
        comboBoxOptionBuySell = self.comboBoxOptionBuySell

        # comboBoxOptionBuySell2
        tk.Label(self, text = "買進/賣出2(複式單)").grid(row=19, column=1)
            #輸入框
        self.comboBoxOptionBuySell2 = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionBuySell2['values'] = Config.comboBoxOptionBuySell2
        self.comboBoxOptionBuySell2.grid(row=19, column=2)

        global comboBoxOptionBuySell2
        comboBoxOptionBuySell2 = self.comboBoxOptionBuySell2

        # buttonSendOptionOrder
        self.buttonSendOptionOrder = tk.Button(self)
        self.buttonSendOptionOrder["text"] = "選擇權/複式單送出"
        self.buttonSendOptionOrder["command"] = self.buttonSendOptionOrder_Click
        self.buttonSendOptionOrder.grid(row=20, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False

    # checkBoxSendDuplexOrder
    def checkBoxSendDuplexOrder_CheckedChanged(self):
        global isDuplexOrder
        if self.var1.get() == True:
            isDuplexOrder = True
        else:
            isDuplexOrder = False

    def buttonSendFutureOrderCLR_Click(self):
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxFutureID.get()

        if (comboBoxFutureTradeType.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxFutureTradeType.get() == "IOC"):
            pOrder.sTradeType = 1
        elif (comboBoxFutureTradeType.get() == "FOK"):
            pOrder.sTradeType = 2

        if (comboBoxFutureBuySell.get() == "買進"):
            pOrder.sBuySell = 0
        elif (comboBoxFutureBuySell.get() == "賣出"):
            pOrder.sBuySell = 1

        if (comboBoxFutureDayTrade.get() == "否"):
            pOrder.sDayTrade = 0
        elif (comboBoxFutureDayTrade.get() == "是"):
            pOrder.sDayTrade = 1

        if (comboBoxFutureNewClose.get() == "新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxFutureNewClose.get() == "平倉"):
            pOrder.sNewClose = 1
        elif (comboBoxFutureNewClose.get() == "自動"):
            pOrder.sNewClose = 2

        pOrder.bstrPrice = textBoxFuturePrice.get()
        pOrder.nQty = int(textBoxFutureQty.get())

        if (comboBoxFutureReserved.get() == "盤中(T盤及T+1盤)"):
            pOrder.sReserved = 0
        elif (comboBoxFutureReserved.get() == "T盤預約"):
            pOrder.sReserved = 1

        bstrMessage,nCode= m_pSKOrder.SendFutureOrderCLR(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendFutureOrderCLR】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSendOptionOrder_Click(self):
        pOrder = sk.FUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxOptionID.get()

        if (comboBoxOptionTradeType.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxOptionTradeType.get() == "IOC"):
            pOrder.sTradeType = 1
        elif (comboBoxOptionTradeType.get() == "FOK"):
            pOrder.sTradeType = 2

        if (comboBoxOptionBuySell.get() == "買進"):
            pOrder.sBuySell = 0
        elif (comboBoxOptionBuySell.get() == "賣出"):
            pOrder.sBuySell = 1

        if (comboBoxOptionDayTrade.get() == "否"):
            pOrder.sDayTrade = 0
        elif (comboBoxOptionDayTrade.get() == "是"):
            pOrder.sDayTrade = 1

        if (comboBoxOptionNewClose.get() == "新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxOptionNewClose.get() == "平倉"):
            pOrder.sNewClose = 1
        elif (comboBoxOptionNewClose.get() == "自動"):
            pOrder.sNewClose = 2

        pOrder.bstrPrice = textBoxOptionPrice.get()

        pOrder.nQty = int(textBoxOptionQty.get())

        if (comboBoxOptionReserved.get() == "盤中(T盤及T+1盤)"):
            pOrder.sReserved = 0
        elif (comboBoxOptionReserved.get() == "T盤預約"):
            pOrder.sReserved = 1

        if (isDuplexOrder != True):
            # 送出選擇權委託
            bstrMessage,nCode= m_pSKOrder.SendOptionOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

            msg = "【SendOptionOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')
        else:
            pOrder.bstrStockNo2 = textBoxOptionID2.get()

            if (comboBoxOptionBuySell2.get() == "買進"):
                pOrder.sBuySell2 = 0
            elif (comboBoxOptionBuySell2.get() == "賣出"):
                pOrder.sBuySell2 = 1
            # 送出國內選擇權複式單委託
            bstrMessage,nCode= m_pSKOrder.SendDuplexOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

            msg = "【SendDuplexOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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
        bstrMessage,nCode= m_pSKOrder.CancelOrderByStockNo(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), textBoxCancelOrderByStockNo.get())

        msg = "【CancelOrderByStockNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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
        # checkBoxSendDuplexOrder
        # 是否為複式單

        self.checkBoxSendDuplexOrder = tk.Checkbutton(self)
        self.var1 = tk.IntVar()
        self.checkBoxSendDuplexOrder["variable"] = self.var1
        self.checkBoxSendDuplexOrder["onvalue"] = True
        self.checkBoxSendDuplexOrder["offvalue"] = False
        self.checkBoxSendDuplexOrder["text"] = "是否為複式單"
        self.checkBoxSendDuplexOrder["command"] = self.checkBoxSendDuplexOrder_CheckedChanged
        self.checkBoxSendDuplexOrder.grid( row = 0,column = 1)

        # textBoxFutureID3
        tk.Label(self, text = "期貨代號").grid(row=1, column=1)
            #輸入框
        self.textBoxFutureID3 = tk.Entry(self)
        self.textBoxFutureID3.grid(row=1, column=2)

        global textBoxFutureID3
        textBoxFutureID3 = self.textBoxFutureID3

        # textBoxTFbstrSettleYM3
        tk.Label(self, text = "契約年月").grid(row=2, column=1)
            #輸入框
        self.textBoxTFbstrSettleYM3 = tk.Entry(self)
        self.textBoxTFbstrSettleYM3.grid(row=2, column=2)

        global textBoxTFbstrSettleYM3
        textBoxTFbstrSettleYM3 = self.textBoxTFbstrSettleYM3

        # comboBoxTFnPriceFlag3
        tk.Label(self, text = "市價/限價/範圍市價").grid(row=3, column=1)
            #輸入框
        self.comboBoxTFnPriceFlag3 = ttk.Combobox(self, state='readonly')
        self.comboBoxTFnPriceFlag3['values'] = Config.comboBoxTFnPriceFlag3
        self.comboBoxTFnPriceFlag3.grid(row=3, column=2)

        global comboBoxTFnPriceFlag3
        comboBoxTFnPriceFlag3 = self.comboBoxTFnPriceFlag3

        # comboBoxFutureDayTrade3
        tk.Label(self, text = "當沖").grid(row=4, column=1)
            #輸入框
        self.comboBoxFutureDayTrade3 = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureDayTrade3['values'] = Config.comboBoxFutureDayTrade3
        self.comboBoxFutureDayTrade3.grid(row=4, column=2)

        global comboBoxFutureDayTrade3
        comboBoxFutureDayTrade3 = self.comboBoxFutureDayTrade3

        # comboBoxFutureReserved3
        tk.Label(self, text = "盤別").grid(row=5, column=1)
            #輸入框
        self.comboBoxFutureReserved3 = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureReserved3['values'] = Config.comboBoxFutureReserved3
        self.comboBoxFutureReserved3.grid(row=5, column=2)

        global comboBoxFutureReserved3
        comboBoxFutureReserved3 = self.comboBoxFutureReserved3
        
        # comboBoxFutureNewClose3
        tk.Label(self, text = "新平倉").grid(row=6, column=1)
            #輸入框
        self.comboBoxFutureNewClose3 = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureNewClose3['values'] = Config.comboBoxFutureNewClose3
        self.comboBoxFutureNewClose3.grid(row=6, column=2)

        global comboBoxFutureNewClose3
        comboBoxFutureNewClose3 = self.comboBoxFutureNewClose3

        # textBoxFutureQty3
        tk.Label(self, text = "口數").grid(row=7, column=1)
            #輸入框
        self.textBoxFutureQty3 = tk.Entry(self)
        self.textBoxFutureQty3.grid(row=7, column=2)

        global textBoxFutureQty3
        textBoxFutureQty3 = self.textBoxFutureQty3

        # comboBoxFutureTradeType3
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=8, column=1)
            #輸入框
        self.comboBoxFutureTradeType3 = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureTradeType3['values'] = Config.comboBoxFutureTradeType3
        self.comboBoxFutureTradeType3.grid(row=8, column=2)

        global comboBoxFutureTradeType3
        comboBoxFutureTradeType3 = self.comboBoxFutureTradeType3

        # textBoxFuturePrice3
        tk.Label(self, text = "委託價").grid(row=9, column=1)
            #輸入框
        self.textBoxFuturePrice3 = tk.Entry(self)
        self.textBoxFuturePrice3.grid(row=9, column=2)

        global textBoxFuturePrice3
        textBoxFuturePrice3 = self.textBoxFuturePrice3

        # comboBoxFutureBuySell3
        tk.Label(self, text = "買進/賣出").grid(row=10, column=1)
            #輸入框
        self.comboBoxFutureBuySell3 = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureBuySell3['values'] = Config.comboBoxFutureBuySell3
        self.comboBoxFutureBuySell3.grid(row=10, column=2)

        global comboBoxFutureBuySell3
        comboBoxFutureBuySell3 = self.comboBoxFutureBuySell3

        # buttonSendFutureProxyOrderCLR
        self.buttonSendFutureProxyOrderCLR = tk.Button(self)
        self.buttonSendFutureProxyOrderCLR["text"] = "期貨送出"
        self.buttonSendFutureProxyOrderCLR["command"] = self.buttonSendFutureProxyOrderCLR_Click
        self.buttonSendFutureProxyOrderCLR.grid(row=11, column=1)

        # textBoxOptionID3
        tk.Label(self, text = "選擇權代號").grid(row=12, column=1)
            #輸入框
        self.textBoxOptionID3 = tk.Entry(self)
        self.textBoxOptionID3.grid(row=12, column=2)

        global textBoxOptionID3
        textBoxOptionID3 = self.textBoxOptionID3

        # textBoxOptionID23
        tk.Label(self, text = "選擇權代號2(複式單)").grid(row=13, column=1)
            #輸入框
        self.textBoxOptionID23 = tk.Entry(self)
        self.textBoxOptionID23.grid(row=13, column=2)

        global textBoxOptionID23
        textBoxOptionID23 = self.textBoxOptionID23

        # textBoxTObstrSettleYM3
        tk.Label(self, text = "契約年月").grid(row=14, column=1)
            #輸入框
        self.textBoxTObstrSettleYM3 = tk.Entry(self)
        self.textBoxTObstrSettleYM3.grid(row=14, column=2)

        global textBoxTObstrSettleYM3
        textBoxTObstrSettleYM3 = self.textBoxTObstrSettleYM3

        # textBoxTObstrSettleYM23
        tk.Label(self, text = "契約年月2").grid(row=15, column=1)
            #輸入框
        self.textBoxTObstrSettleYM23 = tk.Entry(self)
        self.textBoxTObstrSettleYM23.grid(row=15, column=2)

        global textBoxTObstrSettleYM23
        textBoxTObstrSettleYM23 = self.textBoxTObstrSettleYM23

        # textBoxbstrStrike3
        tk.Label(self, text = "履約價1").grid(row=16, column=1)
            #輸入框
        self.textBoxbstrStrike3 = tk.Entry(self)
        self.textBoxbstrStrike3.grid(row=16, column=2)

        global textBoxbstrStrike3
        textBoxbstrStrike3 = self.textBoxbstrStrike3

        # textBoxbstrStrike23
        tk.Label(self, text = "履約價2").grid(row=17, column=1)
            #輸入框
        self.textBoxbstrStrike23 = tk.Entry(self)
        self.textBoxbstrStrike23.grid(row=17, column=2)

        global textBoxbstrStrike23
        textBoxbstrStrike23 = self.textBoxbstrStrike23

        # comboBoxOptionDayTrade3
        tk.Label(self, text = "當沖").grid(row=18, column=1)
            #輸入框
        self.comboBoxOptionDayTrade3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionDayTrade3['values'] = Config.comboBoxOptionDayTrade3
        self.comboBoxOptionDayTrade3.grid(row=18, column=2)

        global comboBoxOptionDayTrade3
        comboBoxOptionDayTrade3 = self.comboBoxOptionDayTrade3

        # comboBoxOptionReserved3
        tk.Label(self, text = "盤別").grid(row=19, column=1)
            #輸入框
        self.comboBoxOptionReserved3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionReserved3['values'] = Config.comboBoxOptionReserved3
        self.comboBoxOptionReserved3.grid(row=19, column=2)

        global comboBoxOptionReserved3
        comboBoxOptionReserved3 = self.comboBoxOptionReserved3

        # comboBoxOptionbstrOrderType3
        tk.Label(self, text = "新平倉").grid(row=20, column=1)
            #輸入框
        self.comboBoxOptionbstrOrderType3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionbstrOrderType3['values'] = Config.comboBoxOptionbstrOrderType3
        self.comboBoxOptionbstrOrderType3.grid(row=20, column=2)

        global comboBoxOptionbstrOrderType3
        comboBoxOptionbstrOrderType3 = self.comboBoxOptionbstrOrderType3

        # textBoxOptionQty3
        tk.Label(self, text = "口數").grid(row=21, column=1)
            #輸入框
        self.textBoxOptionQty3 = tk.Entry(self)
        self.textBoxOptionQty3.grid(row=21, column=2)

        global textBoxOptionQty3
        textBoxOptionQty3 = self.textBoxOptionQty3

        # comboBoxOptionTradeType3
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=22, column=1)
            #輸入框
        self.comboBoxOptionTradeType3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionTradeType3['values'] = Config.comboBoxOptionTradeType3
        self.comboBoxOptionTradeType3.grid(row=22, column=2)

        global comboBoxOptionTradeType3
        comboBoxOptionTradeType3 = self.comboBoxOptionTradeType3

        # comboBoxnCP3
        tk.Label(self, text = "CALL/PUT").grid(row=23, column=1)
            #輸入框
        self.comboBoxnCP3 = ttk.Combobox(self, state='readonly')
        self.comboBoxnCP3['values'] = Config.comboBoxnCP3
        self.comboBoxnCP3.grid(row=23, column=2)

        global comboBoxnCP3
        comboBoxnCP3 = self.comboBoxnCP3

        # comboBoxnCP23
        tk.Label(self, text = "CALL/PUT2").grid(row=24, column=1)
            #輸入框
        self.comboBoxnCP23 = ttk.Combobox(self, state='readonly')
        self.comboBoxnCP23['values'] = Config.comboBoxnCP23
        self.comboBoxnCP23.grid(row=24, column=2)

        global comboBoxnCP23
        comboBoxnCP23 = self.comboBoxnCP23

        # comboBoxTOnPriceFlag3
        tk.Label(self, text = "市價/限價/範圍市價").grid(row=25, column=1)
            #輸入框
        self.comboBoxTOnPriceFlag3 = ttk.Combobox(self, state='readonly')
        self.comboBoxTOnPriceFlag3['values'] = Config.comboBoxTOnPriceFlag3
        self.comboBoxTOnPriceFlag3.grid(row=25, column=2)

        global comboBoxTOnPriceFlag3
        comboBoxTOnPriceFlag3 = self.comboBoxTOnPriceFlag3

        # textBoxOptionPrice3
        tk.Label(self, text = "委託價").grid(row=26, column=1)
            #輸入框
        self.textBoxOptionPrice3 = tk.Entry(self)
        self.textBoxOptionPrice3.grid(row=26, column=2)

        global textBoxOptionPrice3
        textBoxOptionPrice3 = self.textBoxOptionPrice3

        # comboBoxOptionBuySell3
        tk.Label(self, text = "買進/賣出").grid(row=27, column=1)
            #輸入框
        self.comboBoxOptionBuySell3 = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionBuySell3['values'] = Config.comboBoxOptionBuySell3
        self.comboBoxOptionBuySell3.grid(row=27, column=2)
  
        global comboBoxOptionBuySell3
        comboBoxOptionBuySell3 = self.comboBoxOptionBuySell3

        # comboBoxOptionBuySell23
        tk.Label(self, text = "買進/賣出2").grid(row=28, column=1)
            #輸入框
        self.comboBoxOptionBuySell23 = ttk.Combobox(self, state='readonly')
        self.comboBoxOptionBuySell23['values'] = Config.comboBoxOptionBuySell23
        self.comboBoxOptionBuySell23.grid(row=28, column=2)

        global comboBoxOptionBuySell23
        comboBoxOptionBuySell23 = self.comboBoxOptionBuySell23

        # buttonSendOptionProxyOrder
        self.buttonSendOptionProxyOrder = tk.Button(self)
        self.buttonSendOptionProxyOrder["text"] = "選擇權/複式單送出"
        self.buttonSendOptionProxyOrder["command"] = self.buttonSendOptionProxyOrder_Click
        self.buttonSendOptionProxyOrder.grid(row=29, column=1)

    # checkBoxSendDuplexOrder
    def checkBoxSendDuplexOrder_CheckedChanged(self):
        global isDuplexOrder
        if self.var1.get() == True:
            isDuplexOrder = True
        else:
            isDuplexOrder = False

    def buttonSendFutureProxyOrderCLR_Click(self):
        pFUTUREPROXYORDER = sk.FUTUREPROXYORDER()

        pFUTUREPROXYORDER.bstrFullAccount = comboBoxAccount.get()
        pFUTUREPROXYORDER.bstrStockNo = textBoxFutureID3.get()
        pFUTUREPROXYORDER.bstrSettleYM = textBoxTFbstrSettleYM3.get()

        if (comboBoxTFnPriceFlag3.get() == "市價"):
            pFUTUREPROXYORDER.nPriceFlag = 0
        elif (comboBoxTFnPriceFlag3.get() == "限價"):
            pFUTUREPROXYORDER.nPriceFlag = 1
        elif (comboBoxTFnPriceFlag3.get() == "範圍市價"):
            pFUTUREPROXYORDER.nPriceFlag = 2

        if (comboBoxFutureTradeType3.get() == "ROD"):
            pFUTUREPROXYORDER.nTradeType = 0
        elif (comboBoxFutureTradeType3.get() == "IOC"):
            pFUTUREPROXYORDER.nTradeType = 1
        elif (comboBoxFutureTradeType3.get() == "FOK"):
            pFUTUREPROXYORDER.nTradeType = 2

        if (comboBoxFutureBuySell3.get() == "買進"):
            pFUTUREPROXYORDER.nBuySell = 0
        elif (comboBoxFutureBuySell3.get() == "賣出"):
            pFUTUREPROXYORDER.nBuySell = 1

        if (comboBoxFutureDayTrade3.get() == "否"):
            pFUTUREPROXYORDER.nDayTrade = 0
        elif (comboBoxFutureDayTrade3.get() == "是"):
            pFUTUREPROXYORDER.nDayTrade = 1

        if (comboBoxFutureNewClose3.get() == "0:新倉"):
            pFUTUREPROXYORDER.bstrOrderType = "0"
        elif (comboBoxFutureNewClose3.get() == "1:平倉"):
            pFUTUREPROXYORDER.bstrOrderType = "1"
        elif (comboBoxFutureNewClose3.get() == "2:自動"):
            pFUTUREPROXYORDER.bstrOrderType = "2"

        pFUTUREPROXYORDER.bstrPrice = textBoxFuturePrice3.get()
        pFUTUREPROXYORDER.nQty = int(textBoxFutureQty3.get())

        if (comboBoxFutureReserved3.get() == "盤中單"):
            pFUTUREPROXYORDER.nReserved = 0
        elif (comboBoxFutureReserved3.get() == "預約單"):
            pFUTUREPROXYORDER.nReserved = 1

        # 經由proxy server送出期貨委託，需設倉別與盤別
        bstrMessage,nCode= m_pSKOrder.SendFutureProxyOrderCLR(comboBoxUserID.get(), pFUTUREPROXYORDER)

        if bstrMessage is not None:
             msg = "【SendFutureProxyOrderCLR】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
             msg = "【SendFutureProxyOrderCLR】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"
        
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSendOptionProxyOrder_Click(self):
        pFUTUREPROXYORDER = sk.FUTUREPROXYORDER()

        pFUTUREPROXYORDER.bstrFullAccount = comboBoxAccount.get()
        pFUTUREPROXYORDER.bstrStockNo = textBoxOptionID3.get()
        pFUTUREPROXYORDER.bstrSettleYM = textBoxTObstrSettleYM3.get()
        pFUTUREPROXYORDER.bstrStrike = textBoxbstrStrike3.get()

        if (comboBoxOptionTradeType3.get() == "ROD"):
            pFUTUREPROXYORDER.nTradeType = 0
        elif (comboBoxOptionTradeType3.get() == "IOC"):
            pFUTUREPROXYORDER.nTradeType = 1
        elif (comboBoxOptionTradeType3.get() == "FOK"):
            pFUTUREPROXYORDER.nTradeType = 2

        if (comboBoxOptionBuySell3.get() == "買進"):
            pFUTUREPROXYORDER.nBuySell = 0
        elif (comboBoxOptionBuySell3.get() == "賣出"):
            pFUTUREPROXYORDER.nBuySell = 1

        if (comboBoxOptionDayTrade3.get() == "否"):
            pFUTUREPROXYORDER.nDayTrade = 0
        elif (comboBoxOptionDayTrade3.get() == "是"):
            pFUTUREPROXYORDER.nDayTrade = 1

        if (comboBoxOptionbstrOrderType3.get() == "0:新倉"):
            pFUTUREPROXYORDER.bstrOrderType = "0"
        elif (comboBoxOptionbstrOrderType3.get() == "1:平倉"):
            pFUTUREPROXYORDER.bstrOrderType = "1"
        elif (comboBoxOptionbstrOrderType3.get() == "2:自動"):
            pFUTUREPROXYORDER.bstrOrderType = "2"

        pFUTUREPROXYORDER.bstrPrice = textBoxOptionPrice3.get()
        pFUTUREPROXYORDER.nQty = int(textBoxOptionQty3.get())

        if (comboBoxOptionReserved3.get() == "盤中單"):
            pFUTUREPROXYORDER.nReserved = 0
        elif (comboBoxOptionReserved3.get() == "預約單"):
            pFUTUREPROXYORDER.nReserved = 1

        if (comboBoxnCP3.get() == "CALL"):
            pFUTUREPROXYORDER.nCP = 0
        elif (comboBoxnCP3.get() == "PUT"):
            pFUTUREPROXYORDER.nCP = 1

        if (comboBoxTOnPriceFlag3.get() == "市價"):
            pFUTUREPROXYORDER.nPriceFlag = 0
        elif (comboBoxTOnPriceFlag3.get() == "限價"):
            pFUTUREPROXYORDER.nPriceFlag = 1
        elif (comboBoxTOnPriceFlag3.get() == "範圍市價"):
            pFUTUREPROXYORDER.nPriceFlag = 2

        if (isDuplexOrder != True):
            # 送出選擇權委託
            bstrMessage,nCode= m_pSKOrder.SendOptionProxyOrder(comboBoxUserID.get(), pFUTUREPROXYORDER)

            if bstrMessage is not None:
                msg = "【SendOptionProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            else:
                msg = "【SendOptionProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

            richTextBoxMethodMessage.insert('end',  msg + "\n")
            richTextBoxMethodMessage.see('end')
        else:
            pFUTUREPROXYORDER.bstrStockNo2 = textBoxOptionID23.get()
            pFUTUREPROXYORDER.bstrSettleYM2 = textBoxTObstrSettleYM23.get()
            pFUTUREPROXYORDER.bstrStrike2 = textBoxbstrStrike23.get()

            if (comboBoxnCP23.get() == "CALL"):
                pFUTUREPROXYORDER.nCP2 = 0
            elif (comboBoxnCP23.get() == "PUT"):
                pFUTUREPROXYORDER.nCP2 = 1

            if (comboBoxOptionBuySell23.get() == "買進"):
                pFUTUREPROXYORDER.nBuySell2 = 0
            elif (comboBoxOptionBuySell23.get() == "賣出"):
                pFUTUREPROXYORDER.nBuySell2 = 1
            
            # 經由proxy server送出選擇權複式下單
            bstrMessage,nCode= m_pSKOrder.SendDuplexProxyOrder(comboBoxUserID.get(), pFUTUREPROXYORDER)

            if bstrMessage is not None:
                msg = "【SendDuplexProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
            else:
                msg = "【SendDuplexProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"
                
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
        # comboBoxUpdateTFOrder4
        tk.Label(self, text = "下單類別").grid(row=0, column=1)
            #輸入框
        self.comboBoxUpdateTFOrder4 = ttk.Combobox(self, state='readonly')
        self.comboBoxUpdateTFOrder4['values'] = Config.comboBoxUpdateTFOrder4
        self.comboBoxUpdateTFOrder4.grid(row=0, column=2)

        global comboBoxUpdateTFOrder4
        comboBoxUpdateTFOrder4 = self.comboBoxUpdateTFOrder4

        # textBoxSeqNo4
        tk.Label(self, text = "請輸入委託序號").grid(row=1, column=1)
            #輸入框
        self.textBoxSeqNo4 = tk.Entry(self)
        self.textBoxSeqNo4.grid(row=1, column=2)

        global textBoxSeqNo4
        textBoxSeqNo4 = self.textBoxSeqNo4

        # textBoxBookNo4
        tk.Label(self, text = "請輸入委託書號").grid(row=2, column=1)
            #輸入框
        self.textBoxBookNo4 = tk.Entry(self)
        self.textBoxBookNo4.grid(row=2, column=2)

        global textBoxBookNo4
        textBoxBookNo4 = self.textBoxBookNo4

        # textBoxStockDecreaseQty4
        tk.Label(self, text = "請輸入減少數量").grid(row=3, column=1)
            #輸入框
        self.textBoxStockDecreaseQty4 = tk.Entry(self)
        self.textBoxStockDecreaseQty4.grid(row=3, column=2)

        global textBoxStockDecreaseQty4
        textBoxStockDecreaseQty4 = self.textBoxStockDecreaseQty4

        # textBoxPrice4
        tk.Label(self, text = "請輸入修改價格").grid(row=4, column=1)
            #輸入框
        self.textBoxPrice4 = tk.Entry(self)
        self.textBoxPrice4.grid(row=4, column=2)

        global textBoxPrice4
        textBoxPrice4 = self.textBoxPrice4

        # comboBoxFutureReserved4
        tk.Label(self, text = "盤別").grid(row=5, column=1)
            #輸入框
        self.comboBoxFutureReserved4 = ttk.Combobox(self, state='readonly')
        self.comboBoxFutureReserved4['values'] = Config.comboBoxFutureReserved4
        self.comboBoxFutureReserved4.grid(row=5, column=2)

        global comboBoxFutureReserved4
        comboBoxFutureReserved4 = self.comboBoxFutureReserved4

        # comboBoxTradeType4
        tk.Label(self, text = "ROD/IOC/FOK").grid(row=6, column=1)
            #輸入框
        self.comboBoxTradeType4 = ttk.Combobox(self, state='readonly')
        self.comboBoxTradeType4['values'] = Config.comboBoxTradeType4
        self.comboBoxTradeType4.grid(row=6, column=2)

        global comboBoxTradeType4
        comboBoxTradeType4 = self.comboBoxTradeType4

        # buttonSendFutureProxyAlter
        self.buttonSendFutureProxyAlter = tk.Button(self)
        self.buttonSendFutureProxyAlter["text"] = "期貨刪改單送出"
        self.buttonSendFutureProxyAlter["command"] = self.buttonSendFutureProxyAlter_Click
        self.buttonSendFutureProxyAlter.grid(row=7, column=1)

        # buttonSendOptionProxyAlter
        self.buttonSendOptionProxyAlter = tk.Button(self)
        self.buttonSendOptionProxyAlter["text"] = "選擇權刪改單送出"
        self.buttonSendOptionProxyAlter["command"] = self.buttonSendOptionProxyAlter_Click
        self.buttonSendOptionProxyAlter.grid(row=7, column=2)
    
    def buttonSendFutureProxyAlter_Click(self):
        pFUTUREPROXYORDER = sk.FUTUREPROXYORDER()
        pFUTUREPROXYORDER.bstrFullAccount = comboBoxAccount.get()

        if (comboBoxUpdateTFOrder4.get() == "刪單"):
            pFUTUREPROXYORDER.bstrOrderType = "0"
        elif (comboBoxUpdateTFOrder4.get() == "減量"):
            pFUTUREPROXYORDER.bstrOrderType = "1"
        elif (comboBoxUpdateTFOrder4.get() == "改價"):
            pFUTUREPROXYORDER.bstrOrderType = "2"

        pFUTUREPROXYORDER.bstrPrice = textBoxPrice4.get()

        if (comboBoxFutureReserved4.get() == "盤中單"):
            pFUTUREPROXYORDER.nReserved = 0
        elif (comboBoxFutureReserved4.get() == "預約單"):
            pFUTUREPROXYORDER.nReserved = 1

        pFUTUREPROXYORDER.nQty = int(textBoxStockDecreaseQty4.get())

        if (comboBoxTradeType4.get() == "ROD"):
            pFUTUREPROXYORDER.nTradeType = 0
        elif (comboBoxTradeType4.get() == "IOC"):
            pFUTUREPROXYORDER.nTradeType = 1
        elif (comboBoxTradeType4.get() == "FOK"):
            pFUTUREPROXYORDER.nTradeType = 2

        pFUTUREPROXYORDER.bstrBookNo = textBoxBookNo4.get()
        pFUTUREPROXYORDER.bstrSeqNo = textBoxSeqNo4.get()

        # 經由proxy server送出期貨刪改單
        bstrMessage,nCode= m_pSKOrder.SendFutureProxyAlter(comboBoxUserID.get(), pFUTUREPROXYORDER)

        if bstrMessage is not None:
             msg = "【SendFutureProxyAlter】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
             msg = "【SendFutureProxyAlter】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSendOptionProxyAlter_Click(self):
        pFUTUREPROXYORDER = sk.FUTUREPROXYORDER()
        pFUTUREPROXYORDER.bstrFullAccount = comboBoxAccount.get()

        if (comboBoxUpdateTFOrder4.get() == "刪單"):
            pFUTUREPROXYORDER.bstrOrderType = "0"
        elif (comboBoxUpdateTFOrder4.get() == "減量"):
            pFUTUREPROXYORDER.bstrOrderType = "1"
        elif (comboBoxUpdateTFOrder4.get() == "改價"):
            pFUTUREPROXYORDER.bstrOrderType = "2"

        pFUTUREPROXYORDER.bstrPrice = textBoxPrice4.get()

        if (comboBoxFutureReserved4.get() == "盤中單"):
            pFUTUREPROXYORDER.nReserved = 0
        elif (comboBoxFutureReserved4.get() == "預約單"):
            pFUTUREPROXYORDER.nReserved = 1

        pFUTUREPROXYORDER.nQty = int(textBoxStockDecreaseQty4.get())

        if (comboBoxTradeType4.get() == "ROD"):
            pFUTUREPROXYORDER.nTradeType = 0
        elif (comboBoxTradeType4.get() == "IOC"):
            pFUTUREPROXYORDER.nTradeType = 1
        elif (comboBoxTradeType4.get() == "FOK"):
            pFUTUREPROXYORDER.nTradeType = 2

        pFUTUREPROXYORDER.bstrBookNo = textBoxBookNo4.get()
        pFUTUREPROXYORDER.bstrSeqNo = textBoxSeqNo4.get()

        # 經由proxy server送出選擇權刪改單
        bstrMessage,nCode= m_pSKOrder.SendOptionProxyAlter(comboBoxUserID.get(), pFUTUREPROXYORDER)

        if bstrMessage is not None:
             msg = "【SendOptionProxyAlter】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
             msg = "【SendOptionProxyAlter】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
#OffSetNewForm
class OffsetNewForm(tk.Frame):
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

        # comboBoxSendTFOffSetNewnCommodity
        tk.Label(self, text = "類別").grid(row = 0,column = 1)
        self.comboBoxSendTFOffSetNewnCommodity = ttk.Combobox(self, state='readonly')
        self.comboBoxSendTFOffSetNewnCommodity['values'] = Config.comboBoxSendTFOffSetNewnCommodity
        self.comboBoxSendTFOffSetNewnCommodity.grid(row=0, column=2)

        global comboBoxSendTFOffSetNewnCommodity
        comboBoxSendTFOffSetNewnCommodity = self.comboBoxSendTFOffSetNewnCommodity

        # textBoxSendTFOffSetNewbstrYearMonth
        tk.Label(self, text = "年月").grid(row=1, column=1)
        #輸入框
        self.textBoxSendTFOffSetNewbstrYearMonth = tk.Entry(self)
        self.textBoxSendTFOffSetNewbstrYearMonth.grid(row=1, column=2)

        global textBoxSendTFOffSetNewbstrYearMonth
        textBoxSendTFOffSetNewbstrYearMonth = self.textBoxSendTFOffSetNewbstrYearMonth

        # comboBoxSendTFOffSetNewnBuySell
        tk.Label(self, text = "買賣別").grid(row = 1,column = 3)
        self.comboBoxSendTFOffSetNewnBuySell = ttk.Combobox(self, state='readonly')
        self.comboBoxSendTFOffSetNewnBuySell['values'] = Config.comboBoxSendTFOffSetNewnBuySell
        self.comboBoxSendTFOffSetNewnBuySell.grid(row=1, column=4)

        global comboBoxSendTFOffSetNewnBuySell
        comboBoxSendTFOffSetNewnBuySell = self.comboBoxSendTFOffSetNewnBuySell

        # textBoxSendTFOffSetNewnQty
        tk.Label(self, text = "互抵口數(大台)").grid(row=2, column=1)
        #輸入框
        self.textBoxSendTFOffSetNewnQty = tk.Entry(self)
        self.textBoxSendTFOffSetNewnQty.grid(row=2, column=2)

        global textBoxSendTFOffSetNewnQty
        textBoxSendTFOffSetNewnQty = self.textBoxSendTFOffSetNewnQty
        
        # textBoxSendTFOffSetNewnQty_2
        tk.Label(self, text = "互抵口數(小台)").grid(row=2, column=3)
        #輸入框
        self.textBoxSendTFOffSetNewnQty_2 = tk.Entry(self)
        self.textBoxSendTFOffSetNewnQty_2.grid(row=2, column=4)

        global textBoxSendTFOffSetNewnQty_2
        textBoxSendTFOffSetNewnQty_2 = self.textBoxSendTFOffSetNewnQty_2
        
        # textBoxSendTFOffSetNewnQty_3
        tk.Label(self, text = "互抵口數(微台)").grid(row=2, column=5)
        #輸入框
        self.textBoxSendTFOffSetNewnQty_3 = tk.Entry(self)
        self.textBoxSendTFOffSetNewnQty_3.grid(row=2, column=6)

        global textBoxSendTFOffSetNewnQty_3
        textBoxSendTFOffSetNewnQty_3 = self.textBoxSendTFOffSetNewnQty_3

        # buttonSendTFOffSetNew
        self.buttonSendTFOffSetNew = tk.Button(self)
        self.buttonSendTFOffSetNew["text"] = "大小微台互抵"
        self.buttonSendTFOffSetNew["command"] = self.buttonSendTFOffSetNew_Click
        self.buttonSendTFOffSetNew.grid(row=3, column=1)

        global buttonSendTFOffSetNew
        buttonSendTFOffSetNew = self.buttonSendTFOffSetNew

        # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False

    def buttonSendTFOffSetNew_Click(self):
        if (comboBoxSendTFOffSetNewnCommodity.get() == "0:大抵微"):
            nCommodity = 0
        elif (comboBoxSendTFOffSetNewnCommodity.get() == "1:小抵微"):
            nCommodity = 1
        elif (comboBoxSendTFOffSetNewnCommodity.get() == "2:大小抵微"):
            nCommodity = 2
        elif (comboBoxSendTFOffSetNewnCommodity.get() == "3:大抵小微"):
            nCommodity = 3
        elif (comboBoxSendTFOffSetNewnCommodity.get() == "4:小抵大微"):
            nCommodity = 4
        elif (comboBoxSendTFOffSetNewnCommodity.get() == "5:大抵小"):
            nCommodity = 5

        if (comboBoxSendTFOffSetNewnBuySell.get() == "多方(買)"):
            nBuySell = 0
        elif (comboBoxSendTFOffSetNewnBuySell.get() == "空方(賣)"):
            nBuySell = 1

        nQty = int(textBoxSendTFOffSetNewnQty.get())
        nQty_2 = int(textBoxSendTFOffSetNewnQty_2.get())
        nQty_3 = int(textBoxSendTFOffSetNewnQty_3.get())

        bstrMessage, nCode = m_pSKOrder.SendTFOffsetNew(comboBoxUserID.get(), bAsyncOrder, comboBoxAccount.get(), nCommodity, textBoxSendTFOffSetNewbstrYearMonth.get(), nBuySell, nQty, nQty_2, nQty_3)

        msg = "【SendTFOffsetNew】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#==========================================
#定義彈出視窗
def popup_window_Read():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Read")

    # 建立 Frame 作為 ReadForm，並添加到彈出窗口
    popup_ReadForm = ReadForm(popup)
    popup_ReadForm.pack(fill=tk.BOTH, expand=True)

def popup_window_OffSet():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("OffSet")

    # 建立 Frame 作為 OffSetForm，並添加到彈出窗口
    popup_OffSetForm = OffSetForm(popup)
    popup_OffSetForm.pack(fill=tk.BOTH, expand=True)

def popup_window_Assemble():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Assemble")

    # 建立 Frame 作為 AssembleForm，並添加到彈出窗口
    popup_AssembleForm = AssembleForm(popup)
    popup_AssembleForm.pack(fill=tk.BOTH, expand=True)

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

def popup_window_OffsetNew():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("OffsetNew")

    # 建立 Frame 作為 OffSetForm，並添加到彈出窗口
    popup_OffsetNewForm = OffsetNewForm(popup)
    popup_OffsetNewForm.pack(fill=tk.BOTH, expand=True)

#開啟Tk視窗
if __name__ == '__main__':
    #建立主視窗
    root = tk.Tk()
    root.title("TFOrder")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)


    # 開啟Read視窗的按鈕
    popup_button_Read = tk.Button(root, text="查詢", command=popup_window_Read)
    popup_button_Read.grid(row = 1, column= 0)

    # 開啟OffSet視窗的按鈕
    popup_button_OffSet = tk.Button(root, text="大小台電金互抵", command=popup_window_OffSet)
    popup_button_OffSet.grid(row = 2, column= 0)

    # 開啟Assemble視窗的按鈕
    popup_button_Assemble = tk.Button(root, text="選擇權組合/複式單拆解/了結", command=popup_window_Assemble)
    popup_button_Assemble.grid(row = 3, column= 0)

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

    
    # 開啟OffsetNew視窗的按鈕
    popup_button_OffSet = tk.Button(root, text="大小微台互抵", command=popup_window_OffsetNew)
    popup_button_OffSet.grid(row = 8, column= 0)

    root.mainloop()

#==========================================
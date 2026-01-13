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

        # textBoxForeignStockID
        tk.Label(self, text = "股票代號").grid(row=1, column=1)
            #輸入框
        self.textBoxForeignStockID = tk.Entry(self)
        self.textBoxForeignStockID.grid(row=1, column=2)

        global textBoxForeignStockID
        textBoxForeignStockID = self.textBoxForeignStockID
        
        # textBoxForeignExchangeNo
        tk.Label(self, text = "交易所代碼，美股：US").grid(row=2, column=1)
            #輸入框
        self.textBoxForeignExchangeNo = tk.Entry(self)
        self.textBoxForeignExchangeNo.grid(row=2, column=2)

        global textBoxForeignExchangeNo
        textBoxForeignExchangeNo = self.textBoxForeignExchangeNo
        
        # comboBoxForeignAccountType
        tk.Label(self, text = "專戶別種類").grid(row=3, column=1)
            #輸入框
        self.comboBoxForeignAccountType = ttk.Combobox(self, state='readonly')
        self.comboBoxForeignAccountType['values'] = Config.comboBoxForeignAccountType
        self.comboBoxForeignAccountType.grid(row=3, column=2)

        global comboBoxForeignAccountType
        comboBoxForeignAccountType = self.comboBoxForeignAccountType
        
        # textBoxForeignCurrency1
        tk.Label(self, text = "扣款幣別1").grid(row=4, column=1)
            #輸入框
        self.textBoxForeignCurrency1 = tk.Entry(self)
        self.textBoxForeignCurrency1.grid(row=4, column=2)

        global textBoxForeignCurrency1
        textBoxForeignCurrency1 = self.textBoxForeignCurrency1
        
        # textBoxForeignCurrency2
        tk.Label(self, text = "扣款幣別2").grid(row=5, column=1)
            #輸入框
        self.textBoxForeignCurrency2 = tk.Entry(self)
        self.textBoxForeignCurrency2.grid(row=5, column=2)

        global textBoxForeignCurrency2
        textBoxForeignCurrency2 = self.textBoxForeignCurrency2
        
        # textBoxForeignCurrency3
        tk.Label(self, text = "扣款幣別3").grid(row=6, column=1)
            #輸入框
        self.textBoxForeignCurrency3 = tk.Entry(self)
        self.textBoxForeignCurrency3.grid(row=6, column=2)

        global textBoxForeignCurrency3
        textBoxForeignCurrency3 = self.textBoxForeignCurrency3
        
        # textBoxForeignQty
        tk.Label(self, text = "委託量").grid(row=7, column=1)
            #輸入框
        self.textBoxForeignQty = tk.Entry(self)
        self.textBoxForeignQty.grid(row=7, column=2)

        global textBoxForeignQty
        textBoxForeignQty = self.textBoxForeignQty
        
        # textBoxForeignPrice
        tk.Label(self, text = "委託價").grid(row=8, column=1)
            #輸入框
        self.textBoxForeignPrice = tk.Entry(self)
        self.textBoxForeignPrice.grid(row=8, column=2)

        global textBoxForeignPrice
        textBoxForeignPrice = self.textBoxForeignPrice
                
        # comboBoxForeignOrderType
        tk.Label(self, text = "買進/賣出").grid(row=9, column=1)
            #輸入框
        self.comboBoxForeignOrderType = ttk.Combobox(self, state='readonly')
        self.comboBoxForeignOrderType['values'] = Config.comboBoxForeignOrderType
        self.comboBoxForeignOrderType.grid(row=9, column=2)

        global comboBoxForeignOrderType
        comboBoxForeignOrderType = self.comboBoxForeignOrderType
                
        # comboBoxForeignTradeType
        tk.Label(self, text = "庫存別").grid(row=10, column=1)
            #輸入框
        self.comboBoxForeignTradeType = ttk.Combobox(self, state='readonly')
        self.comboBoxForeignTradeType['values'] = Config.comboBoxForeignTradeType
        self.comboBoxForeignTradeType.grid(row=10, column=2)

        global comboBoxForeignTradeType
        comboBoxForeignTradeType = self.comboBoxForeignTradeType
                
        # buttonSendForeignStockOrder
        self.buttonSendForeignStockOrder = tk.Button(self)
        self.buttonSendForeignStockOrder["text"] = "複委託送出"
        self.buttonSendForeignStockOrder["command"] = self.buttonSendForeignStockOrder_Click
        self.buttonSendForeignStockOrder.grid(row=11, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False

    def buttonSendForeignStockOrder_Click(self):
        
        pOrder = sk.FOREIGNORDER()
        
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxForeignStockID.get()
        pOrder.bstrExchangeNo = textBoxForeignExchangeNo.get()
        pOrder.bstrPrice = textBoxForeignPrice.get()
        pOrder.bstrCurrency1 = textBoxForeignCurrency1.get()
        pOrder.bstrCurrency2 = textBoxForeignCurrency2.get()
        pOrder.bstrCurrency3 = textBoxForeignCurrency3.get()

        if (comboBoxForeignAccountType.get() == "外幣專戶"):
            pOrder.nAccountType = 1
        elif (comboBoxForeignAccountType.get() == "台幣專戶"):
            pOrder.nAccountType = 2
        pOrder.nQty = int(textBoxForeignQty.get())

        if (comboBoxForeignOrderType.get() == "買"):
            pOrder.nOrderType = 1
        elif (comboBoxForeignOrderType.get() == "賣"):
            pOrder.nOrderType = 2

        if (comboBoxForeignTradeType.get() == "一般/定股(CITI)"):
            pOrder.nTradeType = 1
        elif (comboBoxForeignTradeType.get() == "定額(VIEWTRADE)"):
            pOrder.nTradeType = 2
        
        # 送出複委託委託
        bstrMessage,nCode= m_pSKOrder.SendForeignStockOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendForeignStockOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # textBoxCancelForeignStockOrderbstrSeqNoUpdate
        tk.Label(self, text = "請輸入委託序號").grid(row=0, column=1)
            #輸入框
        self.textBoxCancelForeignStockOrderbstrSeqNoUpdate = tk.Entry(self)
        self.textBoxCancelForeignStockOrderbstrSeqNoUpdate.grid(row=0, column=2)

        global textBoxCancelForeignStockOrderbstrSeqNoUpdate
        textBoxCancelForeignStockOrderbstrSeqNoUpdate = self.textBoxCancelForeignStockOrderbstrSeqNoUpdate
        
        # textBoxCancelForeignStockOrderbstrBookNoUpdate
        tk.Label(self, text = "請輸入委託書號").grid(row=1, column=1)
            #輸入框
        self.textBoxCancelForeignStockOrderbstrBookNoUpdate = tk.Entry(self)
        self.textBoxCancelForeignStockOrderbstrBookNoUpdate.grid(row=1, column=2)

        global textBoxCancelForeignStockOrderbstrBookNoUpdate
        textBoxCancelForeignStockOrderbstrBookNoUpdate = self.textBoxCancelForeignStockOrderbstrBookNoUpdate
        
        # textBoxForeignStockIDUpdate
        tk.Label(self, text = "股票代號").grid(row=2, column=1)
            #輸入框
        self.textBoxForeignStockIDUpdate = tk.Entry(self)
        self.textBoxForeignStockIDUpdate.grid(row=2, column=2)

        global textBoxForeignStockIDUpdate
        textBoxForeignStockIDUpdate = self.textBoxForeignStockIDUpdate
        
        # textBoxbstrExchangeNoUpdate
        tk.Label(self, text = "交易所代碼，美股：US").grid(row=3, column=1)
            #輸入框
        self.textBoxbstrExchangeNoUpdate = tk.Entry(self)
        self.textBoxbstrExchangeNoUpdate.grid(row=3, column=2)

        global textBoxbstrExchangeNoUpdate
        textBoxbstrExchangeNoUpdate = self.textBoxbstrExchangeNoUpdate

        # buttonCancelForeignStockOrder
        self.buttonCancelForeignStockOrder = tk.Button(self)
        self.buttonCancelForeignStockOrder["text"] = "刪單(序號+書號)"
        self.buttonCancelForeignStockOrder["command"] = self.buttonCancelForeignStockOrder_Click
        self.buttonCancelForeignStockOrder.grid(row=4, column=1)

        # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
            
    def buttonCancelForeignStockOrder_Click(self):

        pOrder = sk.FOREIGNORDER()
        pOrder.bstrStockNo = textBoxForeignStockIDUpdate.get()
        pOrder.bstrExchangeNo = textBoxbstrExchangeNoUpdate.get()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrSeqNo = textBoxCancelForeignStockOrderbstrSeqNoUpdate.get()
        pOrder.bstrBookNo = textBoxCancelForeignStockOrderbstrBookNoUpdate.get()
        pOrder.nOrderType = 4
        
        # 新版-複委託刪單(需同時填序號及委託書號)
        bstrMessage,nCode= m_pSKOrder.CancelForeignStockOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【CancelForeignStockOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # textBoxForeignStockIDProxy
        tk.Label(self, text = "股票代號").grid(row=0, column=1)
            #輸入框
        self.textBoxForeignStockIDProxy = tk.Entry(self)
        self.textBoxForeignStockIDProxy.grid(row=0, column=2)

        global textBoxForeignStockIDProxy
        textBoxForeignStockIDProxy = self.textBoxForeignStockIDProxy
        
        # comboBoxbstrExchangeNoProxy
        tk.Label(self, text = "交易所代碼，美股：US").grid(row=1, column=1)
            #輸入框
        self.comboBoxbstrExchangeNoProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxbstrExchangeNoProxy['values'] = Config.comboBoxbstrExchangeNoProxy
        self.comboBoxbstrExchangeNoProxy.grid(row=1, column=2)

        global comboBoxbstrExchangeNoProxy
        comboBoxbstrExchangeNoProxy = self.comboBoxbstrExchangeNoProxy
                
        # comboBoxForeignAccountTypeProxy
        tk.Label(self, text = "專戶別種類").grid(row=2, column=1)
            #輸入框
        self.comboBoxForeignAccountTypeProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxForeignAccountTypeProxy['values'] = Config.comboBoxForeignAccountTypeProxy
        self.comboBoxForeignAccountTypeProxy.grid(row=2, column=2)

        global comboBoxForeignAccountTypeProxy
        comboBoxForeignAccountTypeProxy = self.comboBoxForeignAccountTypeProxy
        
        # textBoxForeignCurrency1Proxy
        tk.Label(self, text = "扣款幣別1").grid(row=3, column=1)
            #輸入框
        self.textBoxForeignCurrency1Proxy = tk.Entry(self)
        self.textBoxForeignCurrency1Proxy.grid(row=3, column=2)

        global textBoxForeignCurrency1Proxy
        textBoxForeignCurrency1Proxy = self.textBoxForeignCurrency1Proxy
        
        # textBoxForeignCurrency2Proxy
        tk.Label(self, text = "扣款幣別2").grid(row=4, column=1)
            #輸入框
        self.textBoxForeignCurrency2Proxy = tk.Entry(self)
        self.textBoxForeignCurrency2Proxy.grid(row=4, column=2)

        global textBoxForeignCurrency2Proxy
        textBoxForeignCurrency2Proxy = self.textBoxForeignCurrency2Proxy
        
        # textBoxForeignCurrency3Proxy
        tk.Label(self, text = "扣款幣別3").grid(row=5, column=1)
            #輸入框
        self.textBoxForeignCurrency3Proxy = tk.Entry(self)
        self.textBoxForeignCurrency3Proxy.grid(row=5, column=2)

        global textBoxForeignCurrency3Proxy
        textBoxForeignCurrency3Proxy = self.textBoxForeignCurrency3Proxy
        
        # textBoxForeignQtyProxy
        tk.Label(self, text = "委託量").grid(row=6, column=1)
            #輸入框
        self.textBoxForeignQtyProxy = tk.Entry(self)
        self.textBoxForeignQtyProxy.grid(row=6, column=2)

        global textBoxForeignQtyProxy
        textBoxForeignQtyProxy = self.textBoxForeignQtyProxy
        
        # textBoxForeignPriceProxy
        tk.Label(self, text = "委託價").grid(row=7, column=1)
            #輸入框
        self.textBoxForeignPriceProxy = tk.Entry(self)
        self.textBoxForeignPriceProxy.grid(row=7, column=2)

        global textBoxForeignPriceProxy
        textBoxForeignPriceProxy = self.textBoxForeignPriceProxy
                
        # comboBoxForeignOrderTypeProxy
        tk.Label(self, text = "買進/賣出").grid(row=8, column=1)
            #輸入框
        self.comboBoxForeignOrderTypeProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxForeignOrderTypeProxy['values'] = Config.comboBoxForeignOrderTypeProxy
        self.comboBoxForeignOrderTypeProxy.grid(row=8, column=2)

        global comboBoxForeignOrderTypeProxy
        comboBoxForeignOrderTypeProxy = self.comboBoxForeignOrderTypeProxy
                
        # comboBoxForeignTradeTypeProxy
        tk.Label(self, text = "庫存別").grid(row=9, column=1)
            #輸入框
        self.comboBoxForeignTradeTypeProxy = ttk.Combobox(self, state='readonly')
        self.comboBoxForeignTradeTypeProxy['values'] = Config.comboBoxForeignTradeTypeProxy
        self.comboBoxForeignTradeTypeProxy.grid(row=9, column=2)

        global comboBoxForeignTradeTypeProxy
        comboBoxForeignTradeTypeProxy = self.comboBoxForeignTradeTypeProxy

        # buttonSendForeignStockProxyOrder
        self.buttonSendForeignStockProxyOrder = tk.Button(self)
        self.buttonSendForeignStockProxyOrder["text"] = "複委託送出"
        self.buttonSendForeignStockProxyOrder["command"] = self.buttonSendForeignStockProxyOrder_Click
        self.buttonSendForeignStockProxyOrder.grid(row=10, column=1)

    def buttonSendForeignStockProxyOrder_Click(self):

        pAsyncOrder = sk.OSSTOCKPROXYORDER()

        pAsyncOrder.bstrFullAccount = comboBoxAccount.get()
        pAsyncOrder.bstrStockNo = textBoxForeignStockIDProxy.get()

        if (comboBoxbstrExchangeNoProxy.get() == "US：美股"):
            pAsyncOrder.bstrExchangeNo = "US"
        elif (comboBoxbstrExchangeNoProxy.get() == "HK：港股"):
            pAsyncOrder.bstrExchangeNo = "HK"
        elif (comboBoxbstrExchangeNoProxy.get() == "JP：日股"):
            pAsyncOrder.bstrExchangeNo = "JP"
        elif (comboBoxbstrExchangeNoProxy.get() == "SP：新加坡"):
            pAsyncOrder.bstrExchangeNo = "SP"
        elif (comboBoxbstrExchangeNoProxy.get() == "SG：新(幣)坡股"):
            pAsyncOrder.bstrExchangeNo = "SG"
        elif (comboBoxbstrExchangeNoProxy.get() == "SA: 滬股"):
            pAsyncOrder.bstrExchangeNo = "SA"
        elif (comboBoxbstrExchangeNoProxy.get() == "HA: 深股"):
            pAsyncOrder.bstrExchangeNo = "HA"

        selectedValue = comboBoxForeignAccountTypeProxy.get()
        if (selectedValue == "外幣專戶"):
            pAsyncOrder.nAccountType = 1
        elif (selectedValue == "台幣專戶"):
            pAsyncOrder.nAccountType = 2

        pAsyncOrder.bstrCurrency1 = textBoxForeignCurrency1Proxy.get()
        pAsyncOrder.bstrCurrency2 = textBoxForeignCurrency2Proxy.get()
        pAsyncOrder.bstrCurrency3 = textBoxForeignCurrency3Proxy.get()
        pAsyncOrder.bstrProxyQty = textBoxForeignQtyProxy.get()
        pAsyncOrder.bstrPrice = textBoxForeignPriceProxy.get()

        selectedValue = comboBoxForeignOrderTypeProxy.get()
        if (selectedValue == "買"):
            pAsyncOrder.nOrderType = 1
        elif (selectedValue == "賣"):
            pAsyncOrder.nOrderType = 2

        selectedValue = comboBoxForeignTradeTypeProxy.get()
        if (selectedValue == "一般/定股(CITI)"):
            pAsyncOrder.nTradeType = 1
        elif (selectedValue == "定額(VIEWTRADE)"):
            pAsyncOrder.nTradeType = 2
    
        # 經由proxy server送出複委託下單
        bstrMessage,nCode= m_pSKOrder.SendForeignStockProxyOrder(comboBoxUserID.get(), pAsyncOrder)
        
        if bstrMessage is not None:
            msg = "【SendForeignStockProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
            msg = "【SendForeignStockProxyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"

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

        # textBoxCancelForeignStockOrderbstrSeqNo
        tk.Label(self, text = "請輸入委託序號").grid(row=0, column=1)
            #輸入框
        self.textBoxCancelForeignStockOrderbstrSeqNo = tk.Entry(self)
        self.textBoxCancelForeignStockOrderbstrSeqNo.grid(row=0, column=2)

        global textBoxCancelForeignStockOrderbstrSeqNo
        textBoxCancelForeignStockOrderbstrSeqNo = self.textBoxCancelForeignStockOrderbstrSeqNo
        
        # textBoxCancelForeignStockOrderbstrBookNo
        tk.Label(self, text = "請輸入委託書號").grid(row=1, column=1)
            #輸入框
        self.textBoxCancelForeignStockOrderbstrBookNo = tk.Entry(self)
        self.textBoxCancelForeignStockOrderbstrBookNo.grid(row=1, column=2)

        global textBoxCancelForeignStockOrderbstrBookNo
        textBoxCancelForeignStockOrderbstrBookNo = self.textBoxCancelForeignStockOrderbstrBookNo
        
        # textBoxbstrStockNo
        tk.Label(self, text = "股票代號").grid(row=2, column=1)
            #輸入框
        self.textBoxbstrStockNo = tk.Entry(self)
        self.textBoxbstrStockNo.grid(row=2, column=2)

        global textBoxbstrStockNo
        textBoxbstrStockNo = self.textBoxbstrStockNo
        
        # textBoxbstrExchangeNo
        tk.Label(self, text = "交易所代碼，美股：US").grid(row=3, column=1)
            #輸入框
        self.textBoxbstrExchangeNo = tk.Entry(self)
        self.textBoxbstrExchangeNo.grid(row=3, column=2)

        global textBoxbstrExchangeNo
        textBoxbstrExchangeNo = self.textBoxbstrExchangeNo

        # buttonSendForeignStockProxyCancel
        self.buttonSendForeignStockProxyCancel = tk.Button(self)
        self.buttonSendForeignStockProxyCancel["text"] = "刪單送出"
        self.buttonSendForeignStockProxyCancel["command"] = self.buttonSendForeignStockProxyCancel_Click
        self.buttonSendForeignStockProxyCancel.grid(row=4, column=1)
            
    def buttonSendForeignStockProxyCancel_Click(self):

        pOrder = sk.OSSTOCKPROXYORDER()
        pOrder.bstrStockNo = textBoxbstrStockNo.get()
        pOrder.bstrExchangeNo = textBoxbstrExchangeNo.get()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrSeqNo = textBoxCancelForeignStockOrderbstrSeqNo.get()
        pOrder.bstrBookNo = textBoxCancelForeignStockOrderbstrBookNo.get()
        pOrder.nOrderType = 4
        
        # 經由proxy server送出複委託刪單
        bstrMessage,nCode= m_pSKOrder.SendForeignStockProxyCancel(comboBoxUserID.get(), pOrder)
               
        if bstrMessage is not None:
            msg = "【SendForeignStockProxyCancel】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        else:
            msg = "【SendForeignStockProxyCancel】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + " No message"
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
#==========================================
#定義彈出視窗
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
    root.title("OSOrder")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)


    # 開啟Send視窗的按鈕
    popup_button_Send = tk.Button(root, text="一般下單", command=popup_window_Send)
    popup_button_Send.grid(row = 1, column= 0)

    # 開啟Update視窗的按鈕
    popup_button_Update = tk.Button(root, text="一般刪改單", command=popup_window_Update)
    popup_button_Update.grid(row = 2, column= 0)

    # 開啟SendProxy視窗的按鈕
    popup_button_SendProxy = tk.Button(root, text="Proxy下單", command=popup_window_SendProxy)
    popup_button_SendProxy.grid(row = 3, column= 0)

    # 開啟UpdateProxy視窗的按鈕
    popup_button_UpdateProxy = tk.Button(root, text="Proxy刪改單", command=popup_window_UpdateProxy)
    popup_button_UpdateProxy.grid(row = 4, column= 0)

    root.mainloop()

#==========================================
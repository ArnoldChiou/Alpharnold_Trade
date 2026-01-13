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
    # 新版期貨智慧單(包含停損單、移動停損、二擇一、觸價單)被動回報查詢。透過呼叫GetStopLossReport後，資訊由該事件回傳。
    def OnStopLossReport(self, bstrData):
        msg = "【OnStopLossReport】" + bstrData
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
#STPForm
class STPForm(tk.Frame):
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

        # textBoxbstrStockNo
        tk.Label(self, text = "期權商品代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNo = tk.Entry(self, width= 6)
        self.textBoxbstrStockNo.grid(row=0, column=2)

        global textBoxbstrStockNo
        textBoxbstrStockNo = self.textBoxbstrStockNo

        # comboBoxsNewClose
        tk.Label(self, text = "新平倉").grid(row=0, column=3)
            #輸入框
        self.comboBoxsNewClose = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsNewClose['values'] = Config.comboBoxsNewClose
        self.comboBoxsNewClose.grid(row=0, column=4)

        global comboBoxsNewClose
        comboBoxsNewClose = self.comboBoxsNewClose

        # comboBoxsBuySell
        tk.Label(self, text = "0:買進 1:賣出").grid(row=0, column=5)
            #輸入框
        self.comboBoxsBuySell = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySell['values'] = Config.comboBoxsBuySell
        self.comboBoxsBuySell.grid(row=0, column=6)

        global comboBoxsBuySell
        comboBoxsBuySell = self.comboBoxsBuySell

        # comboBoxsTradeType
        tk.Label(self, text = "0:ROD 3:IOC 4:FOK").grid(row=0, column=7)
            #輸入框
        self.comboBoxsTradeType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsTradeType['values'] = Config.comboBoxsTradeType
        self.comboBoxsTradeType.grid(row=0, column=8)

        global comboBoxsTradeType
        comboBoxsTradeType = self.comboBoxsTradeType

        # comboBoxsDayTrade
        tk.Label(self, text = "當沖").grid(row=0, column=9)
            #輸入框
        self.comboBoxsDayTrade = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsDayTrade['values'] = Config.comboBoxsDayTrade
        self.comboBoxsDayTrade.grid(row=0, column=10)

        global comboBoxsDayTrade
        comboBoxsDayTrade = self.comboBoxsDayTrade

        # textBoxbstrSettlementMonth
        tk.Label(self, text = "委託商品年月，YYYYMM共6碼(EX: 202206)").grid(row=1, column=1)
        #輸入框
        self.textBoxbstrSettlementMonth = tk.Entry(self, width= 6)
        self.textBoxbstrSettlementMonth.grid(row=1, column=2)

        global textBoxbstrSettlementMonth
        textBoxbstrSettlementMonth = self.textBoxbstrSettlementMonth

        # textBoxbstrTrigger
        tk.Label(self, text = "觸發價，觸發基準價").grid(row=2, column=1)
        #輸入框
        self.textBoxbstrTrigger = tk.Entry(self, width= 6)
        self.textBoxbstrTrigger.grid(row=2, column=2)

        global textBoxbstrTrigger
        textBoxbstrTrigger = self.textBoxbstrTrigger
        
        # textBoxnQty
        tk.Label(self, text = "交易口數").grid(row=3, column=1)
        #輸入框
        self.textBoxnQty = tk.Entry(self, width= 6)
        self.textBoxnQty.grid(row=3, column=2)

        global textBoxnQty
        textBoxnQty = self.textBoxnQty

        # comboBoxnOrderPriceType
        tk.Label(self, text = "2: 限價; 3:範圍市價 （不支援市價）").grid(row=3, column=3)
            #輸入框
        self.comboBoxnOrderPriceType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceType['values'] = Config.comboBoxnOrderPriceType
        self.comboBoxnOrderPriceType.grid(row=3, column=4)

        global comboBoxnOrderPriceType
        comboBoxnOrderPriceType = self.comboBoxnOrderPriceType

        # textBoxbstrPrice
        tk.Label(self, text = "委託價格，(限價時，需填此欄) //「P」範圍市價").grid(row=3, column=5)
        #輸入框
        self.textBoxbstrPrice = tk.Entry(self, width= 6)
        self.textBoxbstrPrice.grid(row=3, column=6)

        global textBoxbstrPrice
        textBoxbstrPrice = self.textBoxbstrPrice

        # comboBoxsReserved
        tk.Label(self, text = "盤別").grid(row=4, column=1)
            #輸入框
        self.comboBoxsReserved = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsReserved['values'] = Config.comboBoxsReserved
        self.comboBoxsReserved.grid(row=4, column=2)

        global comboBoxsReserved
        comboBoxsReserved = self.comboBoxsReserved

        # comboBoxnLongActionFlag
        tk.Label(self, text = "是否為長效單(0:否, 1:是)").grid(row=5, column=1)
            #輸入框
        self.comboBoxnLongActionFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLongActionFlag['values'] = Config.comboBoxnLongActionFlag
        self.comboBoxnLongActionFlag.grid(row=5, column=2)

        global comboBoxnLongActionFlag
        comboBoxnLongActionFlag = self.comboBoxnLongActionFlag

        # textBoxbstrLongEndDate
        tk.Label(self, text = "長效單結束日期(YYYYMMDD共8碼, EX: 20240205)").grid(row=5, column=3)
        #輸入框
        self.textBoxbstrLongEndDate = tk.Entry(self, width= 6)
        self.textBoxbstrLongEndDate.grid(row=5, column=4)

        global textBoxbstrLongEndDate
        textBoxbstrLongEndDate = self.textBoxbstrLongEndDate

        # comboBoxnLAType
        tk.Label(self, text = "觸發結束條件").grid(row=6, column=1)
            #輸入框
        self.comboBoxnLAType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLAType['values'] = Config.comboBoxnLAType
        self.comboBoxnLAType.grid(row=6, column=2)

        global comboBoxnLAType
        comboBoxnLAType = self.comboBoxnLAType

        # buttonSendFutureSTPOrderV1
        self.buttonSendFutureSTPOrderV1 = tk.Button(self)
        self.buttonSendFutureSTPOrderV1["text"] = "期貨STP送出"
        self.buttonSendFutureSTPOrderV1["command"] = self.buttonSendFutureSTPOrderV1_Click
        self.buttonSendFutureSTPOrderV1.grid(row=7, column=1)

        # buttonSendOptionStopLossOrder
        self.buttonSendOptionStopLossOrder = tk.Button(self)
        self.buttonSendOptionStopLossOrder["text"] = "選擇權STP送出"
        self.buttonSendOptionStopLossOrder["command"] = self.buttonSendOptionStopLossOrder_Click
        self.buttonSendOptionStopLossOrder.grid(row=7, column=2)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendFutureSTPOrderV1_Click(self):
        
        pOrder = sk.FUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNo.get()
        pOrder.bstrSettlementMonth = textBoxbstrSettlementMonth.get()

        if (comboBoxsNewClose.get() == "0:新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxsNewClose.get() == "1:平倉"):
            pOrder.sNewClose = 1
        else:
            pOrder.sNewClose = 2

        if (comboBoxsBuySell.get() == "0:買進"):
            pOrder.sBuySell = 0
        else:
            pOrder.sBuySell = 1

        if (comboBoxsTradeType.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxsTradeType.get() == "IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxsDayTrade.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        pOrder.bstrPrice = textBoxbstrPrice.get()
        pOrder.nQty = int(textBoxnQty.get())
        pOrder.bstrTrigger = textBoxbstrTrigger.get()

        if (comboBoxsReserved.get() == "0:盤中(T盤及T+1盤)"):
            pOrder.sReserved = 0
        else:
            pOrder.sReserved = 1
   
        if (comboBoxnOrderPriceType.get() == "2: 限價"):
            pOrder.nOrderPriceType = 2
        else:
            pOrder.nOrderPriceType = 3

        if (comboBoxnLongActionFlag.get() == "0:否"):
            pOrder.nLongActionFlag = 0
        else:
            pOrder.nLongActionFlag = 1

        pOrder.bstrLongEndDate = textBoxbstrLongEndDate.get()

        if (comboBoxnLAType.get() == "1:效期內觸發即失效"):
            pOrder.nLAType = 1
        else:
            pOrder.nLAType = 3

        # (指定月份需填商品契約年月)新版—送出期貨停損委託。
        bstrMessage,nCode= m_pSKOrder.SendFutureSTPOrderV1(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendFutureSTPOrderV1】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 
    
    def buttonSendOptionStopLossOrder_Click(self):
        
        pOrder = sk.FUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNo.get()
        pOrder.bstrSettlementMonth = textBoxbstrSettlementMonth.get()

        if (comboBoxsNewClose.get() == "0:新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxsNewClose.get() == "1:平倉"):
            pOrder.sNewClose = 1
        else:
            pOrder.sNewClose = 2

        if (comboBoxsBuySell.get() == "0:買進"):
            pOrder.sBuySell = 0
        else:
            pOrder.sBuySell = 1

        if (comboBoxsTradeType.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxsTradeType.get() == "IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxsDayTrade.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        pOrder.bstrPrice = textBoxbstrPrice.get()
        pOrder.nQty = int(textBoxnQty.get())
        pOrder.bstrTrigger = textBoxbstrTrigger.get()

        if (comboBoxsReserved.get() == "0:盤中(T盤及T+1盤)"):
            pOrder.sReserved = 0
        else:
            pOrder.sReserved = 1
   
        if (comboBoxnOrderPriceType.get() == "2: 限價"):
            pOrder.nOrderPriceType = 2
        else:
            pOrder.nOrderPriceType = 3

        if (comboBoxnLongActionFlag.get() == "0:否"):
            pOrder.nLongActionFlag = 0
        else:
            pOrder.nLongActionFlag = 1

        pOrder.bstrLongEndDate = textBoxbstrLongEndDate.get()

        if (comboBoxnLAType.get() == "1:效期內觸發即失效"):
            pOrder.nLAType = 1
        else:
            pOrder.nLAType = 3

        # 送出選擇權停損委託
        bstrMessage,nCode= m_pSKOrder.SendOptionStopLossOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendOptionStopLossOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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
        tk.Label(self, text = "期權商品代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoMST = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoMST.grid(row=0, column=2)

        global textBoxbstrStockNoMST
        textBoxbstrStockNoMST = self.textBoxbstrStockNoMST

        # comboBoxsNewCloseMST
        tk.Label(self, text = "新平倉，0:新倉 1:平倉 2:自動").grid(row=0, column=3)
            #輸入框
        self.comboBoxsNewCloseMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsNewCloseMST['values'] = Config.comboBoxsNewCloseMST
        self.comboBoxsNewCloseMST.grid(row=0, column=4)

        global comboBoxsNewCloseMST
        comboBoxsNewCloseMST = self.comboBoxsNewCloseMST
        
        # comboBoxsBuySellMST
        tk.Label(self, text = "0:買進 1:賣出").grid(row=0, column=5)
            #輸入框
        self.comboBoxsBuySellMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySellMST['values'] = Config.comboBoxsBuySellMST
        self.comboBoxsBuySellMST.grid(row=0, column=6)

        global comboBoxsBuySellMST
        comboBoxsBuySellMST = self.comboBoxsBuySellMST

        # comboBoxsTradeTypeMST
        tk.Label(self, text = "3:IOC 4:FOK").grid(row=0, column=7)
            #輸入框
        self.comboBoxsTradeTypeMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsTradeTypeMST['values'] = Config.comboBoxsTradeTypeMST
        self.comboBoxsTradeTypeMST.grid(row=0, column=8)

        global comboBoxsTradeTypeMST
        comboBoxsTradeTypeMST = self.comboBoxsTradeTypeMST

        # comboBoxsDayTradeMST
        tk.Label(self, text = "當沖0:否 1:是，可當沖商品請參考交易所規定").grid(row=0, column=9)
            #輸入框
        self.comboBoxsDayTradeMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsDayTradeMST['values'] = Config.comboBoxsDayTradeMST
        self.comboBoxsDayTradeMST.grid(row=0, column=10)

        global comboBoxsDayTradeMST
        comboBoxsDayTradeMST = self.comboBoxsDayTradeMST

        # textBoxbstrSettlementMonthMST
        tk.Label(self, text = "委託商品年月，YYYYMM共6碼(EX: 202206)").grid(row=1, column=1)
        #輸入框
        self.textBoxbstrSettlementMonthMST = tk.Entry(self, width= 6)
        self.textBoxbstrSettlementMonthMST.grid(row=1, column=2)

        global textBoxbstrSettlementMonthMST
        textBoxbstrSettlementMonthMST = self.textBoxbstrSettlementMonthMST

        # textBoxbstrMovingPoint
        tk.Label(self, text = "移動點數").grid(row=2, column=1)
        #輸入框
        self.textBoxbstrMovingPoint = tk.Entry(self, width= 6)
        self.textBoxbstrMovingPoint.grid(row=2, column=2)

        global textBoxbstrMovingPoint
        textBoxbstrMovingPoint = self.textBoxbstrMovingPoint

        # textBoxbstrTriggerMST
        tk.Label(self, text = "觸價基準").grid(row=2, column=3)
        #輸入框
        self.textBoxbstrTriggerMST = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerMST.grid(row=2, column=4)

        global textBoxbstrTriggerMST
        textBoxbstrTriggerMST = self.textBoxbstrTriggerMST

        # textBoxnQtyMST
        tk.Label(self, text = "交易口數").grid(row=3, column=1)
        #輸入框
        self.textBoxnQtyMST = tk.Entry(self, width= 6)
        self.textBoxnQtyMST.grid(row=3, column=2)

        global textBoxnQtyMST
        textBoxnQtyMST = self.textBoxnQtyMST

        # comboBoxnOrderPriceTypeMST
        tk.Label(self, text = "2: 限價; 3:範圍市價 （不支援市價）").grid(row=3, column=3)
            #輸入框
        self.comboBoxnOrderPriceTypeMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeMST['values'] = Config.comboBoxnOrderPriceTypeMST
        self.comboBoxnOrderPriceTypeMST.grid(row=3, column=4)

        global comboBoxnOrderPriceTypeMST
        comboBoxnOrderPriceTypeMST = self.comboBoxnOrderPriceTypeMST

        # comboBoxsReservedMST
        tk.Label(self, text = "盤別，0:盤中(T盤及T+1盤)；1:T盤預約").grid(row=4, column=1)
            #輸入框
        self.comboBoxsReservedMST = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsReservedMST['values'] = Config.comboBoxsReservedMST
        self.comboBoxsReservedMST.grid(row=4, column=2)

        global comboBoxsReservedMST
        comboBoxsReservedMST = self.comboBoxsReservedMST

        # buttonSendFutureMSTOrderV1
        self.buttonSendFutureMSTOrderV1 = tk.Button(self)
        self.buttonSendFutureMSTOrderV1["text"] = "MST送出"
        self.buttonSendFutureMSTOrderV1["command"] = self.buttonSendFutureMSTOrderV1_Click
        self.buttonSendFutureMSTOrderV1.grid(row=5, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendFutureMSTOrderV1_Click(self):
        
        pOrder = sk.FUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoMST.get()

        if (comboBoxsTradeTypeMST.get() == "IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxsBuySellMST.get() == "0:買進"):
            pOrder.sBuySell = 0
        else:
            pOrder.sBuySell = 1

        if (comboBoxsDayTradeMST.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        if (comboBoxsNewCloseMST.get() == "0:新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxsNewCloseMST.get() == "1:平倉"):
            pOrder.sNewClose = 1
        else:
            pOrder.sNewClose = 2

        pOrder.nQty = int(textBoxnQtyMST.get())
        pOrder.bstrTrigger = textBoxbstrTriggerMST.get()

        if (comboBoxsReservedMST.get() == "0:盤中(T盤及T+1盤)"):
            pOrder.sReserved = 0
        else:
            pOrder.sReserved = 1

        pOrder.bstrSettlementMonth = textBoxbstrSettlementMonthMST.get()

        if (comboBoxnOrderPriceTypeMST.get() == "2: 限價"):
            pOrder.nOrderPriceType = 2
        else:
            pOrder.nOrderPriceType = 3

        pOrder.bstrMovingPoint = textBoxbstrMovingPoint.get()

        # (指定月份需填商品契約年月)新版—送出移動停損委託。
        bstrMessage,nCode= m_pSKOrder.SendFutureMSTOrderV1(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendFutureMSTOrderV1】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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
        tk.Label(self, text = "期權商品代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoMIT = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoMIT.grid(row=0, column=2)

        global textBoxbstrStockNoMIT
        textBoxbstrStockNoMIT = self.textBoxbstrStockNoMIT

        # comboBoxsNewCloseMIT
        tk.Label(self, text = "新平倉，0:新倉 1:平倉 2:自動").grid(row=0, column=3)
            #輸入框
        self.comboBoxsNewCloseMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsNewCloseMIT['values'] = Config.comboBoxsNewCloseMIT
        self.comboBoxsNewCloseMIT.grid(row=0, column=4)

        global comboBoxsNewCloseMIT
        comboBoxsNewCloseMIT = self.comboBoxsNewCloseMIT
        
        # comboBoxsBuySellMIT
        tk.Label(self, text = "0:買進 1:賣出").grid(row=0, column=5)
            #輸入框
        self.comboBoxsBuySellMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySellMIT['values'] = Config.comboBoxsBuySellMIT
        self.comboBoxsBuySellMIT.grid(row=0, column=6)

        global comboBoxsBuySellMIT
        comboBoxsBuySellMIT = self.comboBoxsBuySellMIT

        # comboBoxsTradeTypeMIT
        tk.Label(self, text = "0:ROD 3:IOC 4:FOK").grid(row=0, column=7)
            #輸入框
        self.comboBoxsTradeTypeMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsTradeTypeMIT['values'] = Config.comboBoxsTradeTypeMIT
        self.comboBoxsTradeTypeMIT.grid(row=0, column=8)

        global comboBoxsTradeTypeMIT
        comboBoxsTradeTypeMIT = self.comboBoxsTradeTypeMIT

        # comboBoxsDayTradeMIT
        tk.Label(self, text = "當沖0:否 1:是，可當沖商品請參考交易所規定").grid(row=0, column=9)
            #輸入框
        self.comboBoxsDayTradeMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsDayTradeMIT['values'] = Config.comboBoxsDayTradeMIT
        self.comboBoxsDayTradeMIT.grid(row=0, column=10)

        global comboBoxsDayTradeMIT
        comboBoxsDayTradeMIT = self.comboBoxsDayTradeMIT

        # textBoxbstrSettlementMonthMIT
        tk.Label(self, text = "委託商品年月，YYYYMM共6碼(EX: 202206)").grid(row=1, column=1)
        #輸入框
        self.textBoxbstrSettlementMonthMIT = tk.Entry(self, width= 6)
        self.textBoxbstrSettlementMonthMIT.grid(row=1, column=2)

        global textBoxbstrSettlementMonthMIT
        textBoxbstrSettlementMonthMIT = self.textBoxbstrSettlementMonthMIT

        # comboBoxnTriggerDirectionMIT
        tk.Label(self, text = "觸發方向1:GTE(大於), 2:LTE(小於)").grid(row=2, column=1)
            #輸入框
        self.comboBoxnTriggerDirectionMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTriggerDirectionMIT['values'] = Config.comboBoxnTriggerDirectionMIT
        self.comboBoxnTriggerDirectionMIT.grid(row=2, column=2)

        global comboBoxnTriggerDirectionMIT
        comboBoxnTriggerDirectionMIT = self.comboBoxnTriggerDirectionMIT

        # textBoxbstrTriggerMIT
        tk.Label(self, text = "觸發價").grid(row=2, column=3)
        #輸入框
        self.textBoxbstrTriggerMIT = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerMIT.grid(row=2, column=4)

        global textBoxbstrTriggerMIT
        textBoxbstrTriggerMIT = self.textBoxbstrTriggerMIT

        # textBoxnQtyMIT
        tk.Label(self, text = "交易口數").grid(row=2, column=5)
        #輸入框
        self.textBoxnQtyMIT = tk.Entry(self, width= 6)
        self.textBoxnQtyMIT.grid(row=2, column=6)

        global textBoxnQtyMIT
        textBoxnQtyMIT = self.textBoxnQtyMIT

        # comboBoxnOrderPriceTypeMIT
        tk.Label(self, text = "2: 限價; 3:範圍市價 （不支援市價）").grid(row=2, column=7)
            #輸入框
        self.comboBoxnOrderPriceTypeMIT = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeMIT['values'] = Config.comboBoxnOrderPriceTypeMIT
        self.comboBoxnOrderPriceTypeMIT.grid(row=2, column=8)

        global comboBoxnOrderPriceTypeMIT
        comboBoxnOrderPriceTypeMIT = self.comboBoxnOrderPriceTypeMIT

        # textBoxbstrPriceMIT
        tk.Label(self, text = "委託價格，(指定限價時，需填此欄)").grid(row=2, column=9)
        #輸入框
        self.textBoxbstrPriceMIT = tk.Entry(self, width= 6)
        self.textBoxbstrPriceMIT.grid(row=2, column=10)

        global textBoxbstrPriceMIT
        textBoxbstrPriceMIT = self.textBoxbstrPriceMIT

        # textBoxbstrDealPriceMIT
        tk.Label(self, text = "成交價").grid(row=3, column=1)
        #輸入框
        self.textBoxbstrDealPriceMIT = tk.Entry(self, width= 6)
        self.textBoxbstrDealPriceMIT.grid(row=3, column=2)

        global textBoxbstrDealPriceMIT
        textBoxbstrDealPriceMIT = self.textBoxbstrDealPriceMIT

        # buttonSendFutureMITOrderV1
        self.buttonSendFutureMITOrderV1 = tk.Button(self)
        self.buttonSendFutureMITOrderV1["text"] = "期貨MIT送出"
        self.buttonSendFutureMITOrderV1["command"] = self.buttonSendFutureMITOrderV1_Click
        self.buttonSendFutureMITOrderV1.grid(row=4, column=1)

        # buttonSendOptionMITOrder
        self.buttonSendOptionMITOrder = tk.Button(self)
        self.buttonSendOptionMITOrder["text"] = "選擇權MIT送出"
        self.buttonSendOptionMITOrder["command"] = self.buttonSendOptionMITOrder_Click
        self.buttonSendOptionMITOrder.grid(row=4, column=2)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendFutureMITOrderV1_Click(self):
        
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoMIT.get()
        pOrder.bstrPrice = textBoxbstrPriceMIT.get()

        if (comboBoxsTradeTypeMIT.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxsTradeTypeMIT.get() == "IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxsBuySellMIT.get() == "0:買進"):
            pOrder.sBuySell = 0
        else:
            pOrder.sBuySell = 1

        if (comboBoxsDayTradeMIT.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        if (comboBoxsNewCloseMIT.get() == "0:新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxsNewCloseMIT.get() == "1:平倉"):
            pOrder.sNewClose = 1
        else:
            pOrder.sNewClose = 2

        pOrder.nQty = int(textBoxnQtyMIT.get())
        pOrder.bstrTrigger = textBoxbstrTriggerMIT.get()
        pOrder.bstrSettlementMonth = textBoxbstrSettlementMonthMIT.get()
  
        if (comboBoxnOrderPriceTypeMIT.get() == "2: 限價"):
            pOrder.nOrderPriceType = 2
        else:
            pOrder.nOrderPriceType = 3

        pOrder.bstrDealPrice = textBoxbstrDealPriceMIT.get()

        if (comboBoxnTriggerDirectionMIT.get() == "1:GTE大於等於"):
            pOrder.nTriggerDirection = 1
        else:
            pOrder.nTriggerDirection = 2

        # (指定月份需填商品契約年月)新版—送出期貨MIT委託。
        bstrMessage,nCode= m_pSKOrder.SendFutureMITOrderV1(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendFutureMITOrderV1】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end') 

    def buttonSendOptionMITOrder_Click(self):
        
        pOrder = sk.FUTUREORDER()
        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoMIT.get()
        pOrder.bstrPrice = textBoxbstrPriceMIT.get()

        if (comboBoxsTradeTypeMIT.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxsTradeTypeMIT.get() == "IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxsBuySellMIT.get() == "0:買進"):
            pOrder.sBuySell = 0
        else:
            pOrder.sBuySell = 1

        if (comboBoxsDayTradeMIT.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        if (comboBoxsNewCloseMIT.get() == "0:新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxsNewCloseMIT.get() == "1:平倉"):
            pOrder.sNewClose = 1
        else:
            pOrder.sNewClose = 2

        pOrder.nQty = int(textBoxnQtyMIT.get())
        pOrder.bstrTrigger = textBoxbstrTriggerMIT.get()
        pOrder.bstrSettlementMonth = textBoxbstrSettlementMonthMIT.get()
  
        if (comboBoxnOrderPriceTypeMIT.get() == "2: 限價"):
            pOrder.nOrderPriceType = 2
        else:
            pOrder.nOrderPriceType = 3

        pOrder.bstrDealPrice = textBoxbstrDealPriceMIT.get()

        if (comboBoxnTriggerDirectionMIT.get() == "1:GTE大於等於"):
            pOrder.nTriggerDirection = 1
        else:
            pOrder.nTriggerDirection = 2

        # 送出選擇權MIT委託
        bstrMessage,nCode= m_pSKOrder.SendOptionMITOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendOptionMITOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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
        tk.Label(self, text = "期權商品代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNoOCO = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoOCO.grid(row=0, column=2)

        global textBoxbstrStockNoOCO
        textBoxbstrStockNoOCO = self.textBoxbstrStockNoOCO

        # comboBoxsNewCloseOCO
        tk.Label(self, text = "新平倉，0:新倉 1:平倉 2:自動").grid(row=0, column=3)
            #輸入框
        self.comboBoxsNewCloseOCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsNewCloseOCO['values'] = Config.comboBoxsNewCloseOCO
        self.comboBoxsNewCloseOCO.grid(row=0, column=4)

        global comboBoxsNewCloseOCO
        comboBoxsNewCloseOCO = self.comboBoxsNewCloseOCO

        # textBoxbstrSettlementMonthOCO
        tk.Label(self, text = "委託商品年月，YYYYMM共6碼(EX: 202206)").grid(row=1, column=1)
        #輸入框
        self.textBoxbstrSettlementMonthOCO = tk.Entry(self, width= 6)
        self.textBoxbstrSettlementMonthOCO.grid(row=1, column=2)

        global textBoxbstrSettlementMonthOCO
        textBoxbstrSettlementMonthOCO = self.textBoxbstrSettlementMonthOCO

        # textBoxbstrTriggerOCO
        tk.Label(self, text = "第一腳觸發價(當市價大於觸發價1時觸發)").grid(row=2, column=1)
        #輸入框
        self.textBoxbstrTriggerOCO = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerOCO.grid(row=2, column=2)

        global textBoxbstrTriggerOCO
        textBoxbstrTriggerOCO = self.textBoxbstrTriggerOCO

        # comboBoxsBuySellOCO
        tk.Label(self, text = "0:買進 1:賣出").grid(row=2, column=3)
            #輸入框
        self.comboBoxsBuySellOCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySellOCO['values'] = Config.comboBoxsBuySellOCO
        self.comboBoxsBuySellOCO.grid(row=2, column=4)

        global comboBoxsBuySellOCO
        comboBoxsBuySellOCO = self.comboBoxsBuySellOCO

        # textBoxbstrTrigger2
        tk.Label(self, text = "第二腳觸發價(當市價小於觸發價2時觸發)").grid(row=3, column=1)
        #輸入框
        self.textBoxbstrTrigger2 = tk.Entry(self, width= 6)
        self.textBoxbstrTrigger2.grid(row=3, column=2)

        global textBoxbstrTrigger2
        textBoxbstrTrigger2 = self.textBoxbstrTrigger2

        # comboBoxsBuySell2OCO
        tk.Label(self, text = "0:買進 1:賣出").grid(row=3, column=3)
            #輸入框
        self.comboBoxsBuySell2OCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySell2OCO['values'] = Config.comboBoxsBuySell2OCO
        self.comboBoxsBuySell2OCO.grid(row=3, column=4)

        global comboBoxsBuySell2OCO
        comboBoxsBuySell2OCO = self.comboBoxsBuySell2OCO

         # comboBoxsTradeTypeOCO
        tk.Label(self, text = "0:ROD 3:IOC 4:FOK").grid(row=3, column=5)
            #輸入框
        self.comboBoxsTradeTypeOCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsTradeTypeOCO['values'] = Config.comboBoxsTradeTypeOCO
        self.comboBoxsTradeTypeOCO.grid(row=3, column=6)

        global comboBoxsTradeTypeOCO
        comboBoxsTradeTypeOCO = self.comboBoxsTradeTypeOCO

        # comboBoxnOrderPriceTypeOCO
        tk.Label(self, text = "第一腳及第二腳委託價格類型。2限價;3範圍市價（不支援市價）").grid(row=3, column=7)
            #輸入框
        self.comboBoxnOrderPriceTypeOCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeOCO['values'] = Config.comboBoxnOrderPriceTypeOCO
        self.comboBoxnOrderPriceTypeOCO.grid(row=3, column=8)

        global comboBoxnOrderPriceTypeOCO
        comboBoxnOrderPriceTypeOCO = self.comboBoxnOrderPriceTypeOCO

        # textBoxbstrPriceOCO
        tk.Label(self, text = "第一腳委託價格").grid(row=2, column=9)
        #輸入框
        self.textBoxbstrPriceOCO = tk.Entry(self, width= 6)
        self.textBoxbstrPriceOCO.grid(row=2, column=10)

        global textBoxbstrPriceOCO
        textBoxbstrPriceOCO = self.textBoxbstrPriceOCO
        
        # textBoxbstrPrice2
        tk.Label(self, text = "第二腳委託價格").grid(row=3, column=9)
        #輸入框
        self.textBoxbstrPrice2 = tk.Entry(self, width= 6)
        self.textBoxbstrPrice2.grid(row=3, column=10)

        global textBoxbstrPrice2
        textBoxbstrPrice2 = self.textBoxbstrPrice2
                
        # textBoxnQtyOCO
        tk.Label(self, text = "交易口數").grid(row=4, column=1)
        #輸入框
        self.textBoxnQtyOCO = tk.Entry(self, width= 6)
        self.textBoxnQtyOCO.grid(row=4, column=2)

        global textBoxnQtyOCO
        textBoxnQtyOCO = self.textBoxnQtyOCO

        # comboBoxsDayTradeOCO
        tk.Label(self, text = "當沖0:否 1:是，可當沖商品請參考交易所規定").grid(row=4, column=3)
            #輸入框
        self.comboBoxsDayTradeOCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsDayTradeOCO['values'] = Config.comboBoxsDayTradeOCO
        self.comboBoxsDayTradeOCO.grid(row=4, column=4)

        global comboBoxsDayTradeOCO
        comboBoxsDayTradeOCO = self.comboBoxsDayTradeOCO

        # comboBoxnLongActionFlagOCO
        tk.Label(self, text = "是否為長效單(0:否, 1:是)").grid(row=5, column=1)
            #輸入框
        self.comboBoxnLongActionFlagOCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLongActionFlagOCO['values'] = Config.comboBoxnLongActionFlagOCO
        self.comboBoxnLongActionFlagOCO.grid(row=5, column=2)

        global comboBoxnLongActionFlagOCO
        comboBoxnLongActionFlagOCO = self.comboBoxnLongActionFlagOCO

        # textBoxbstrLongEndDateOCO
        tk.Label(self, text = "長效單結束日期(YYYYMMDD共8碼, EX: 20240205)").grid(row=5, column=3)
        #輸入框
        self.textBoxbstrLongEndDateOCO = tk.Entry(self, width= 6)
        self.textBoxbstrLongEndDateOCO.grid(row=5, column=4)

        global textBoxbstrLongEndDateOCO
        textBoxbstrLongEndDateOCO = self.textBoxbstrLongEndDateOCO

        # comboBoxnLATypeOCO
        tk.Label(self, text = "觸發結束條件(1:效期內觸發即失效, 3:效期內完全成交即失效)").grid(row=6, column=1)
            #輸入框
        self.comboBoxnLATypeOCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLATypeOCO['values'] = Config.comboBoxnLATypeOCO
        self.comboBoxnLATypeOCO.grid(row=6, column=2)

        global comboBoxnLATypeOCO
        comboBoxnLATypeOCO = self.comboBoxnLATypeOCO

        # comboBoxsReservedOCO
        tk.Label(self, text = "盤別，0:盤中(T盤及T+1盤)；1:T盤預約/是否為預約單(0:否, 1:是)").grid(row=7, column=1)
            #輸入框
        self.comboBoxsReservedOCO = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsReservedOCO['values'] = Config.comboBoxsReservedOCO
        self.comboBoxsReservedOCO.grid(row=7, column=2)

        global comboBoxsReservedOCO
        comboBoxsReservedOCO = self.comboBoxsReservedOCO

        # buttonSendFutureOCOOrderV1
        self.buttonSendFutureOCOOrderV1 = tk.Button(self)
        self.buttonSendFutureOCOOrderV1["text"] = "OCO送出"
        self.buttonSendFutureOCOOrderV1["command"] = self.buttonSendFutureOCOOrderV1_Click
        self.buttonSendFutureOCOOrderV1.grid(row=8, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendFutureOCOOrderV1_Click(self):
        
        pOrder = sk.FUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoOCO.get()

        if (comboBoxsTradeTypeOCO.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxsTradeTypeOCO.get() == "IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxsBuySellOCO.get() == "0:買進"):
            pOrder.sBuySell = 0
        else:
            pOrder.sBuySell = 1

        if (comboBoxsBuySell2OCO.get() == "0:買進"):
            pOrder.sBuySell2 = 0
        else:
            pOrder.sBuySell2 = 1

        if (comboBoxsDayTradeOCO.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        if (comboBoxsNewCloseOCO.get() == "0:新倉"):
            pOrder.sNewClose = 0
        elif (comboBoxsNewCloseOCO.get() == "1:平倉"):
            pOrder.sNewClose = 1
        else:
            pOrder.sNewClose = 2

        pOrder.nQty = int(textBoxnQtyOCO.get())

        pOrder.bstrTrigger = textBoxbstrTriggerOCO.get()

        if (comboBoxsReservedOCO.get() == "0:盤中(T盤及T+1盤)"):
            pOrder.sReserved = 0
        else:
            pOrder.sReserved = 1

        pOrder.bstrSettlementMonth = textBoxbstrSettlementMonthOCO.get()
  
        if (comboBoxnOrderPriceTypeOCO.get() == "2: 限價"):
            pOrder.nOrderPriceType = 2
        else:
            pOrder.nOrderPriceType = 3

        if (comboBoxnLongActionFlagOCO.get() == "0:否"):
            pOrder.nLongActionFlag = 0
        else:
            pOrder.nLongActionFlag = 1

        pOrder.bstrLongEndDate = textBoxbstrLongEndDateOCO.get()

        if (comboBoxnLATypeOCO.get() == "1:效期內觸發即失效"):
            pOrder.nLAType = 1
        else:
            pOrder.nLAType = 3

        pOrder.bstrPrice = textBoxbstrPriceOCO.get()
        pOrder.bstrPrice2 = textBoxbstrPrice2.get()
        pOrder.bstrTrigger2 = textBoxbstrTrigger2.get()
        pOrder.nTimeFlag = 1

        # (指定月份需填商品契約年月)新版—送出期貨二擇一委託。
        bstrMessage,nCode= m_pSKOrder.SendFutureOCOOrderV1(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendFutureOCOOrderV1】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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
        tk.Label(self, text = "A商品代號").grid(row=0, column=1)
        #輸入框
        self.textBoxbstrStockNo2 = tk.Entry(self, width= 6)
        self.textBoxbstrStockNo2.grid(row=0, column=2)

        global textBoxbstrStockNo2
        textBoxbstrStockNo2 = self.textBoxbstrStockNo2

        # comboBoxnMarketNo
        tk.Label(self, text = "A商品市場編號(1:國內證, 2:國內期, 3:國外證, 4:國外期) ").grid(row=0, column=3)
            #輸入框
        self.comboBoxnMarketNo = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnMarketNo['values'] = Config.comboBoxnMarketNo
        self.comboBoxnMarketNo.grid(row=0, column=4)

        global comboBoxnMarketNo
        comboBoxnMarketNo = self.comboBoxnMarketNo

        # textBoxbstrCIDTandem
        tk.Label(self, text = "交易所代碼(EX: TSE、TAIFEX、CME)").grid(row=0, column=5)
        #輸入框
        self.textBoxbstrCIDTandem = tk.Entry(self, width= 6)
        self.textBoxbstrCIDTandem.grid(row=0, column=6)

        global textBoxbstrCIDTandem
        textBoxbstrCIDTandem = self.textBoxbstrCIDTandem

        # comboBoxnTimeFlag
        tk.Label(self, text = "0:非證券,1:上市, 2:上櫃").grid(row=0, column=7)
            #輸入框
        self.comboBoxnTimeFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTimeFlag['values'] = Config.comboBoxnTimeFlag
        self.comboBoxnTimeFlag.grid(row=0, column=8)

        global comboBoxnTimeFlag
        comboBoxnTimeFlag = self.comboBoxnTimeFlag

        # comboBoxnTriggerDirectionAB
        tk.Label(self, text = "觸發方向1:GTE(大於), 2:LTE(小於)").grid(row=1, column=1)
            #輸入框
        self.comboBoxnTriggerDirectionAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTriggerDirectionAB['values'] = Config.comboBoxnTriggerDirectionAB
        self.comboBoxnTriggerDirectionAB.grid(row=1, column=2)

        global comboBoxnTriggerDirectionAB
        comboBoxnTriggerDirectionAB = self.comboBoxnTriggerDirectionAB
        
        # textBoxbstrTriggerAB
        tk.Label(self, text = "觸發價").grid(row=1, column=3)
        #輸入框
        self.textBoxbstrTriggerAB = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerAB.grid(row=1, column=4)

        global textBoxbstrTriggerAB
        textBoxbstrTriggerAB = self.textBoxbstrTriggerAB
           
        # textBoxbstrDealPriceAB
        tk.Label(self, text = "成交價").grid(row=1, column=5)
        #輸入框
        self.textBoxbstrDealPriceAB = tk.Entry(self, width= 6)
        self.textBoxbstrDealPriceAB.grid(row=1, column=6)

        global textBoxbstrDealPriceAB
        textBoxbstrDealPriceAB = self.textBoxbstrDealPriceAB

        # comboBoxsBuySellAB
        tk.Label(self, text = "0:買進 1:賣出").grid(row=3, column=1)
            #輸入框
        self.comboBoxsBuySellAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySellAB['values'] = Config.comboBoxsBuySellAB
        self.comboBoxsBuySellAB.grid(row=3, column=2)

        global comboBoxsBuySellAB
        comboBoxsBuySellAB = self.comboBoxsBuySellAB

        # comboBoxsDayTradeAB
        tk.Label(self, text = "當沖0:否 1:是，可當沖商品請參考交易所規定").grid(row=3, column=3)
            #輸入框
        self.comboBoxsDayTradeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsDayTradeAB['values'] = Config.comboBoxsDayTradeAB
        self.comboBoxsDayTradeAB.grid(row=3, column=4)

        global comboBoxsDayTradeAB
        comboBoxsDayTradeAB = self.comboBoxsDayTradeAB
        
        # comboBoxsNewCloseAB
        tk.Label(self, text = "新平倉，0:新倉 1:平倉 2:自動").grid(row=3, column=5)
            #輸入框
        self.comboBoxsNewCloseAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsNewCloseAB['values'] = Config.comboBoxsNewCloseAB
        self.comboBoxsNewCloseAB.grid(row=3, column=6)

        global comboBoxsNewCloseAB
        comboBoxsNewCloseAB = self.comboBoxsNewCloseAB

        # comboBoxsTradeTypeAB
        tk.Label(self, text = "0:ROD 3:IOC 4:FOK").grid(row=3, column=7)
            #輸入框
        self.comboBoxsTradeTypeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsTradeTypeAB['values'] = Config.comboBoxsTradeTypeAB
        self.comboBoxsTradeTypeAB.grid(row=3, column=8)

        global comboBoxsTradeTypeAB
        comboBoxsTradeTypeAB = self.comboBoxsTradeTypeAB

        # comboBoxsBuySell2AB
        tk.Label(self, text = "買賣別2(0:買進, 1:賣出)，非價差商品請填0").grid(row=4, column=1)
            #輸入框
        self.comboBoxsBuySell2AB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySell2AB['values'] = Config.comboBoxsBuySell2AB
        self.comboBoxsBuySell2AB.grid(row=4, column=2)

        global comboBoxsBuySell2AB
        comboBoxsBuySell2AB = self.comboBoxsBuySell2AB

        # textBoxbstrStockNoAB
        tk.Label(self, text = "期權商品代號").grid(row=5, column=1)
        #輸入框
        self.textBoxbstrStockNoAB = tk.Entry(self, width= 6)
        self.textBoxbstrStockNoAB.grid(row=5, column=2)

        global textBoxbstrStockNoAB
        textBoxbstrStockNoAB = self.textBoxbstrStockNoAB

        # comboBoxnCallPut
        tk.Label(self, text = "是否為選擇權(0:否, 1:Call, 2:Put)").grid(row=5, column=3)
            #輸入框
        self.comboBoxnCallPut = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnCallPut['values'] = Config.comboBoxnCallPut
        self.comboBoxnCallPut.grid(row=5, column=4)

        global comboBoxnCallPut
        comboBoxnCallPut = self.comboBoxnCallPut
        
        # textBoxbstrStrikePrice
        tk.Label(self, text = "履約價(非選擇權商品請填0)").grid(row=5, column=5)
        #輸入框
        self.textBoxbstrStrikePrice = tk.Entry(self, width= 6)
        self.textBoxbstrStrikePrice.grid(row=5, column=6)

        global textBoxbstrStrikePrice
        textBoxbstrStrikePrice = self.textBoxbstrStrikePrice

        # comboBoxnFlag
        tk.Label(self, text = "是否委託價差商品(0:否, 1:是)").grid(row=5, column=7)
            #輸入框
        self.comboBoxnFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnFlag['values'] = Config.comboBoxnFlag
        self.comboBoxnFlag.grid(row=5, column=8)

        global comboBoxnFlag
        comboBoxnFlag = self.comboBoxnFlag

        # textBoxbstrSettlementMonthAB
        tk.Label(self, text = "委託商品年月，YYYYMM共6碼(EX: 202206)").grid(row=6, column=1)
        #輸入框
        self.textBoxbstrSettlementMonthAB = tk.Entry(self, width= 6)
        self.textBoxbstrSettlementMonthAB.grid(row=6, column=2)

        global textBoxbstrSettlementMonthAB
        textBoxbstrSettlementMonthAB = self.textBoxbstrSettlementMonthAB
        
        # textBoxbstrSettlementMonth2
        tk.Label(self, text = "商品契約月份2(YYYYMM共6碼, EX: 202206)，非價差商品請填0").grid(row=6, column=3)
        #輸入框
        self.textBoxbstrSettlementMonth2 = tk.Entry(self, width= 6)
        self.textBoxbstrSettlementMonth2.grid(row=6, column=4)

        global textBoxbstrSettlementMonth2
        textBoxbstrSettlementMonth2 = self.textBoxbstrSettlementMonth2
                
        # textBoxnQtyAB
        tk.Label(self, text = "交易口數").grid(row=6, column=5)
        #輸入框
        self.textBoxnQtyAB = tk.Entry(self, width= 6)
        self.textBoxnQtyAB.grid(row=6, column=6)

        global textBoxnQtyAB
        textBoxnQtyAB = self.textBoxnQtyAB

        # comboBoxnOrderPriceTypeAB
        tk.Label(self, text = "2: 限價; 3:範圍市價 （不支援市價）").grid(row=6, column=7)
            #輸入框
        self.comboBoxnOrderPriceTypeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeAB['values'] = Config.comboBoxnOrderPriceTypeAB
        self.comboBoxnOrderPriceTypeAB.grid(row=6, column=8)

        global comboBoxnOrderPriceTypeAB
        comboBoxnOrderPriceTypeAB = self.comboBoxnOrderPriceTypeAB

        # textBoxbstrPriceAB
        tk.Label(self, text = "委託價格").grid(row=6, column=9)
        #輸入框
        self.textBoxbstrPriceAB = tk.Entry(self, width= 6)
        self.textBoxbstrPriceAB.grid(row=6, column=10)

        global textBoxbstrPriceAB
        textBoxbstrPriceAB = self.textBoxbstrPriceAB
        
        # comboBoxsReservedAB
        tk.Label(self, text = "盤別，0:盤中(T盤及T+1盤)；1:T盤預約/是否為預約單(0:否, 1:是)").grid(row=7, column=1)
            #輸入框
        self.comboBoxsReservedAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsReservedAB['values'] = Config.comboBoxsReservedAB
        self.comboBoxsReservedAB.grid(row=7, column=2)

        global comboBoxsReservedAB
        comboBoxsReservedAB = self.comboBoxsReservedAB

        # buttonSendFutureABOrder
        self.buttonSendFutureABOrder = tk.Button(self)
        self.buttonSendFutureABOrder["text"] = "AB送出"
        self.buttonSendFutureABOrder["command"] = self.buttonSendFutureABOrder_Click
        self.buttonSendFutureABOrder.grid(row=8, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendFutureABOrder_Click(self):
        
        pOrder = sk.FUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxbstrStockNoAB.get()
        pOrder.bstrStockNo2 = textBoxbstrStockNo2.get()

        pOrder.bstrDealPrice = textBoxbstrDealPriceAB.get()

        if (comboBoxnTriggerDirectionAB.get() == "1:GTE大於等於"):
            pOrder.nTriggerDirection = 1
        else:
            pOrder.nTriggerDirection = 2

        if (comboBoxnMarketNo.get() == "1:國內證"):
            pOrder.nMarketNo = 1
        elif (comboBoxnMarketNo.get() == "2:國內期"):
            pOrder.nMarketNo = 2
        elif (comboBoxnMarketNo.get() == "3:國外證"):
            pOrder.nMarketNo = 3
        else:
            pOrder.nMarketNo = 4

        pOrder.bstrCIDTandem = textBoxbstrCIDTandem.get()

        if (comboBoxnTimeFlag.get() == "1:上市"):
            pOrder.nTimeFlag = 1
        elif(comboBoxnTimeFlag.get() == "2:上櫃(不開放權證、興櫃商品)"):
            pOrder.nTimeFlag = 2
        else:
            pOrder.nTimeFlag = 0

        if (comboBoxnCallPut.get() == "0:否"):
            pOrder.nCallPut = 0
        elif (comboBoxnCallPut.get() == "1:Call"):
            pOrder.nCallPut = 1
        else:
            pOrder.nCallPut = 2

        pOrder.bstrStrikePrice = textBoxbstrStrikePrice.get()

        if (comboBoxnFlag.get() == "0:否"):
            pOrder.nFlag = 0
        else:
            pOrder.nFlag = 1

        pOrder.bstrSettlementMonth2 = textBoxbstrSettlementMonth2.get()

        if (comboBoxsTradeTypeAB.get() == "ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxsTradeTypeAB.get() == "IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxsBuySellAB.get() == "0:買進"):
            pOrder.sBuySell = 0
        else:
            pOrder.sBuySell = 1

        if (comboBoxsBuySell2AB.get() == "0:買進"):
            pOrder.sBuySell2 = 0
        else:
            pOrder.sBuySell2 = 1

        if (comboBoxsDayTradeAB.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        if (comboBoxsNewCloseAB.get() == "0:新倉"):
            pOrder.sNewClose = 0
        elif(comboBoxsNewCloseAB.get() == "1:平倉"):
            pOrder.sNewClose = 1
        else:
            pOrder.sNewClose = 2

        pOrder.bstrPrice = textBoxbstrPriceAB.get()
        pOrder.nQty = int(textBoxnQtyAB.get())
        pOrder.bstrTrigger = textBoxbstrTriggerAB.get()

        if (comboBoxsReservedAB.get() == "0:盤中(T盤及T+1盤)"):
            pOrder.sReserved = 0
        else:
            pOrder.sReserved = 1

        pOrder.bstrSettlementMonth = textBoxbstrSettlementMonthAB.get()
    
        if (comboBoxnOrderPriceTypeAB.get() == "2: 限價"):
            pOrder.nOrderPriceType = 2
        else:
            pOrder.nOrderPriceType = 3

        # (指定月份需填商品契約年月)新版—送出期貨看A下B委託。
        bstrMessage,nCode= m_pSKOrder.SendFutureABOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendFutureABOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # comboBoxnTradeKind
        tk.Label(self, text = "3:OCO、5:STP、8:MIT、9:MST、10：AB").grid(row=1, column=1)
            #輸入框
        self.comboBoxnTradeKind = ttk.Combobox(self, state='readonly')
        self.comboBoxnTradeKind['values'] = Config.comboBoxnTradeKind
        self.comboBoxnTradeKind.grid(row=1, column=2)

        global comboBoxnTradeKind
        comboBoxnTradeKind = self.comboBoxnTradeKind
        
        # comboBoxnMarket
        tk.Label(self, text = "市場別(AB單需選欲刪單之A商品市場)").grid(row=2, column=1)
            #輸入框
        self.comboBoxnMarket = ttk.Combobox(self, state='readonly')
        self.comboBoxnMarket['values'] = Config.comboBoxnMarket
        self.comboBoxnMarket.grid(row=2, column=2)

        global comboBoxnMarket
        comboBoxnMarket = self.comboBoxnMarket
        
        # textBoxbstrSeqNo
        tk.Label(self, text = "委託序號 (預約單可忽略)").grid(row=3, column=1)
        #輸入框
        self.textBoxbstrSeqNo = tk.Entry(self)
        self.textBoxbstrSeqNo.grid(row=3, column=2)

        global textBoxbstrSeqNo
        textBoxbstrSeqNo = self.textBoxbstrSeqNo

        # textBoxbstrOrderNo
        tk.Label(self, text = "委託書號（若觸發，需給書號）").grid(row=4, column=1)
        #輸入框
        self.textBoxbstrOrderNo = tk.Entry(self)
        self.textBoxbstrOrderNo.grid(row=4, column=2)

        global textBoxbstrOrderNo
        textBoxbstrOrderNo = self.textBoxbstrOrderNo
        
        # textBoxbstrLongActionKey
        tk.Label(self, text = "長效單號(非長效單可忽略)").grid(row=5, column=1)
        #輸入框
        self.textBoxbstrLongActionKey = tk.Entry(self)
        self.textBoxbstrLongActionKey.grid(row=5, column=2)

        global textBoxbstrLongActionKey
        textBoxbstrLongActionKey = self.textBoxbstrLongActionKey

        # buttonCancelTFStrategyOrderV1
        self.buttonCancelTFStrategyOrderV1 = tk.Button(self)
        self.buttonCancelTFStrategyOrderV1["text"] = "新版刪單送出"
        self.buttonCancelTFStrategyOrderV1["command"] = self.buttonCancelTFStrategyOrderV1_Click
        self.buttonCancelTFStrategyOrderV1.grid(row=6, column=2)
              
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
    
    def buttonCancelTFStrategyOrderV1_Click(self):
        
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

        if (comboBoxnTradeKind.get() == "3:OCO"):
            pCancelOrder.nTradeKind = 3
        elif (comboBoxnTradeKind.get() == "5:STP"):
            pCancelOrder.nTradeKind = 5
        elif (comboBoxnTradeKind.get() == "8:MIT"):
            pCancelOrder.nTradeKind = 8
        elif (comboBoxnTradeKind.get() == "9:MST"):
            pCancelOrder.nTradeKind = 9
        else:
            pCancelOrder.nTradeKind = 10

        pCancelOrder.bstrSeqNo = textBoxbstrSeqNo.get()
        pCancelOrder.bstrOrderNo = textBoxbstrOrderNo.get()
        pCancelOrder.bstrLongActionKey = textBoxbstrLongActionKey.get()

        # 新版—取消期貨智慧單委託。已產生書號之委託，請填入書號，否則可能影響解除保證金風控。
        bstrMessage,nCode= m_pSKOrder.CancelTFStrategyOrderV1(pCancelOrder, bAsyncOrder)

        msg = "【CancelTFStrategyOrderV1】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # buttonGetOFSmartStrategyReport
        self.buttonGetOFSmartStrategyReport = tk.Button(self)
        self.buttonGetOFSmartStrategyReport["text"] = "查詢送出"
        self.buttonGetOFSmartStrategyReport["command"] = self.buttonGetOFSmartStrategyReport_Click
        self.buttonGetOFSmartStrategyReport.grid(row=1, column=3)
    
    def buttonGetOFSmartStrategyReport_Click(self):

        if (comboBoxbstrKind.get() == "STP:一般停損（含選擇權停損）(長效單)"):
            bstrKind = "STP"
        elif (comboBoxbstrKind.get() == "MST:移動停損"):
            bstrKind = "MST"
        elif (comboBoxbstrKind.get() == "OCO:二擇一(長效單)"):
            bstrKind = "OCO"
        elif (comboBoxbstrKind.get() == "MIT(含選擇權MIT)"):
            bstrKind = "MIT"
        else:
            bstrKind = "AB"

        # 新版期貨停損委託單查詢
        nCode= m_pSKOrder.GetStopLossReport(comboBoxUserID.get(), comboBoxAccount.get(), 0, bstrKind, textBoxbstrDate.get())

        msg = "【GetStopLossReport】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
#==========================================
#定義彈出視窗
def popup_window_STP():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("STP")

    # 建立 Frame 作為 STPForm，並添加到彈出窗口
    popup_STPForm = STPForm(popup)
    popup_STPForm.pack(fill=tk.BOTH, expand=True)
def popup_window_MST():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("MST")

    # 建立 Frame 作為 MSTForm，並添加到彈出窗口
    popup_MSTForm = MSTForm(popup)
    popup_MSTForm.pack(fill=tk.BOTH, expand=True)
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
def popup_window_AB():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("AB")

    # 建立 Frame 作為 ABForm，並添加到彈出窗口
    popup_ABForm = ABForm(popup)
    popup_ABForm.pack(fill=tk.BOTH, expand=True)
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
    root.title("TFStrategyOrder")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)


    # 開啟STP視窗的按鈕
    popup_button_STP = tk.Button(root, text="STP", command=popup_window_STP)
    popup_button_STP.grid(row = 1, column= 0)

    # 開啟MST視窗的按鈕
    popup_button_MST = tk.Button(root, text="MST", command=popup_window_MST)
    popup_button_MST.grid(row = 2, column= 0)

    # 開啟MIT視窗的按鈕
    popup_button_MIT = tk.Button(root, text="MIT", command=popup_window_MIT)
    popup_button_MIT.grid(row = 3, column= 0)

    # 開啟OCO視窗的按鈕
    popup_button_OCO = tk.Button(root, text="OCO", command=popup_window_OCO)
    popup_button_OCO.grid(row = 4, column= 0)

    # 開啟AB視窗的按鈕
    popup_button_AB = tk.Button(root, text="AB", command=popup_window_AB)
    popup_button_AB.grid(row = 5, column= 0)

    # 開啟Cancel視窗的按鈕
    popup_button_CB = tk.Button(root, text="刪單", command=popup_window_Cancel)
    popup_button_CB.grid(row = 6, column= 0)

    # 開啟Get視窗的按鈕
    popup_button_CB = tk.Button(root, text="查詢", command=popup_window_Get)
    popup_button_CB.grid(row = 7, column= 0)

    root.mainloop()

#==========================================

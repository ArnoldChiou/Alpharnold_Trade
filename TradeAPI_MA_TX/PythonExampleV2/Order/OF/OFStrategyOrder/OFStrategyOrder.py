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
    # 海期智慧單查詢。透過呼叫 GetOFSmartStrategyReport 後，資訊由該事件回傳。
    def OnOFSmartStrategyReport(self, bstrData):
        msg = "【OnOFSmartStrategyReport】" + bstrData
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

        # textBoxExchangeNo
        tk.Label(self, text = "交易所代碼 (EX: CME)").grid(row=0, column=1)
        #輸入框
        self.textBoxExchangeNo = tk.Entry(self, width= 6)
        self.textBoxExchangeNo.grid(row=0, column=2)

        global textBoxExchangeNo
        textBoxExchangeNo = self.textBoxExchangeNo
        
        # textBoxStockNo
        tk.Label(self, text = "商品代碼 (EX: ES)").grid(row=0, column=3)
        #輸入框
        self.textBoxStockNo = tk.Entry(self, width= 6)
        self.textBoxStockNo.grid(row=0, column=4)

        global textBoxStockNo
        textBoxStockNo = self.textBoxStockNo
                
        # textBoxbstrYearMonth
        tk.Label(self, text = "商品年月(YYYYMM, EX: 202206)").grid(row=1, column=1)
        #輸入框
        self.textBoxbstrYearMonth = tk.Entry(self, width= 6)
        self.textBoxbstrYearMonth.grid(row=1, column=2)

        global textBoxbstrYearMonth
        textBoxbstrYearMonth = self.textBoxbstrYearMonth
                        
        # textBoxbstrTrigger
        tk.Label(self, text = "第一隻腳觸發價(大於)").grid(row=2, column=1)
        #輸入框
        self.textBoxbstrTrigger = tk.Entry(self, width= 6)
        self.textBoxbstrTrigger.grid(row=2, column=2)

        global textBoxbstrTrigger
        textBoxbstrTrigger = self.textBoxbstrTrigger
                                
        # textBoxTriggerNumerator
        tk.Label(self, text = "分子").grid(row=2, column=3)
        #輸入框
        self.textBoxTriggerNumerator = tk.Entry(self, width= 6)
        self.textBoxTriggerNumerator.grid(row=2, column=4)

        global textBoxTriggerNumerator
        textBoxTriggerNumerator = self.textBoxTriggerNumerator
                                        
        # textBoxbstrTriggerDenominator
        tk.Label(self, text = "分母").grid(row=2, column=5)
        #輸入框
        self.textBoxbstrTriggerDenominator = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerDenominator.grid(row=2, column=6)

        global textBoxbstrTriggerDenominator
        textBoxbstrTriggerDenominator = self.textBoxbstrTriggerDenominator
        
        # comboBoxsBuySell
        tk.Label(self, text = "買賣別(0:買進, 1:賣出)").grid(row=2, column=7)
            #輸入框
        self.comboBoxsBuySell = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySell['values'] = Config.comboBoxsBuySell
        self.comboBoxsBuySell.grid(row=2, column=8)

        global comboBoxsBuySell
        comboBoxsBuySell = self.comboBoxsBuySell
                
        # comboBoxnOrderPriceType
        tk.Label(self, text = "委託價(1:市價,  2:限價)").grid(row=2, column=9)
            #輸入框
        self.comboBoxnOrderPriceType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceType['values'] = Config.comboBoxnOrderPriceType
        self.comboBoxnOrderPriceType.grid(row=2, column=10)

        global comboBoxnOrderPriceType
        comboBoxnOrderPriceType = self.comboBoxnOrderPriceType
                                                
        # textBoxbstrOrder
        tk.Label(self, text = "委託價").grid(row=2, column=11)
        #輸入框
        self.textBoxbstrOrder = tk.Entry(self, width= 6)
        self.textBoxbstrOrder.grid(row=2, column=12)

        global textBoxbstrOrder
        textBoxbstrOrder = self.textBoxbstrOrder
                                        
        # textBoxbstrOrderNumerator
        tk.Label(self, text = "分子").grid(row=2, column=13)
        #輸入框
        self.textBoxbstrOrderNumerator = tk.Entry(self, width= 6)
        self.textBoxbstrOrderNumerator.grid(row=2, column=14)

        global textBoxbstrOrderNumerator
        textBoxbstrOrderNumerator = self.textBoxbstrOrderNumerator
                                        
        # textBoxbstrOrderDenominator
        tk.Label(self, text = "分母").grid(row=2, column=15)
        #輸入框
        self.textBoxbstrOrderDenominator = tk.Entry(self, width= 6)
        self.textBoxbstrOrderDenominator.grid(row=2, column=16)

        global textBoxbstrOrderDenominator
        textBoxbstrOrderDenominator = self.textBoxbstrOrderDenominator
                        
        # comboBoxsTradeType
        tk.Label(self, text = "委託時效(0:ROD, 3:IOC, 4:FOK)").grid(row=2, column=17)
            #輸入框
        self.comboBoxsTradeType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsTradeType['values'] = Config.comboBoxsTradeType
        self.comboBoxsTradeType.grid(row=2, column=18)

        global comboBoxsTradeType
        comboBoxsTradeType = self.comboBoxsTradeType
                                
        # textBoxbstrTrigger2
        tk.Label(self, text = "第一隻腳觸發價(小於)").grid(row=3, column=1)
        #輸入框
        self.textBoxbstrTrigger2 = tk.Entry(self, width= 6)
        self.textBoxbstrTrigger2.grid(row=3, column=2)

        global textBoxbstrTrigger2
        textBoxbstrTrigger2 = self.textBoxbstrTrigger2
                                
        # textBoxbstrTriggerNumerator2
        tk.Label(self, text = "分子").grid(row=3, column=3)
        #輸入框
        self.textBoxbstrTriggerNumerator2 = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerNumerator2.grid(row=3, column=4)

        global textBoxbstrTriggerNumerator2
        textBoxbstrTriggerNumerator2 = self.textBoxbstrTriggerNumerator2
                                        
        # textBoxbstrTriggerDenominator2
        tk.Label(self, text = "分母").grid(row=3, column=5)
        #輸入框
        self.textBoxbstrTriggerDenominator2 = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerDenominator2.grid(row=3, column=6)

        global textBoxbstrTriggerDenominator2
        textBoxbstrTriggerDenominator2 = self.textBoxbstrTriggerDenominator2
        
        # comboBoxnBuySell2
        tk.Label(self, text = "買賣別(0:買進, 1:賣出)").grid(row=3, column=7)
            #輸入框
        self.comboBoxnBuySell2 = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySell2['values'] = Config.comboBoxnBuySell2
        self.comboBoxnBuySell2.grid(row=3, column=8)

        global comboBoxnBuySell2
        comboBoxnBuySell2 = self.comboBoxnBuySell2
                                                        
        # textBoxbstrOrder2
        tk.Label(self, text = "委託價").grid(row=3, column=11)
        #輸入框
        self.textBoxbstrOrder2 = tk.Entry(self, width= 6)
        self.textBoxbstrOrder2.grid(row=3, column=12)

        global textBoxbstrOrder2
        textBoxbstrOrder2 = self.textBoxbstrOrder2
                                        
        # textBoxbstrOrderNumerator2
        tk.Label(self, text = "分子").grid(row=3, column=13)
        #輸入框
        self.textBoxbstrOrderNumerator2 = tk.Entry(self, width= 6)
        self.textBoxbstrOrderNumerator2.grid(row=3, column=14)

        global textBoxbstrOrderNumerator2
        textBoxbstrOrderNumerator2 = self.textBoxbstrOrderNumerator2
                                        
        # textBoxbstrOrderDenominator2
        tk.Label(self, text = "分母").grid(row=3, column=15)
        #輸入框
        self.textBoxbstrOrderDenominator2 = tk.Entry(self, width= 6)
        self.textBoxbstrOrderDenominator2.grid(row=3, column=16)

        global textBoxbstrOrderDenominator2
        textBoxbstrOrderDenominator2 = self.textBoxbstrOrderDenominator2
                                                
        # textBoxnQty
        tk.Label(self, text = "委託口數").grid(row=4, column=1)
        #輸入框
        self.textBoxnQty = tk.Entry(self, width= 6)
        self.textBoxnQty.grid(row=4, column=2)

        global textBoxnQty
        textBoxnQty = self.textBoxnQty
                
        # comboBoxsDayTrade
        tk.Label(self, text = "當沖(0:否, 1:是)").grid(row=4, column=3)
            #輸入框
        self.comboBoxsDayTrade = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsDayTrade['values'] = Config.comboBoxsDayTrade
        self.comboBoxsDayTrade.grid(row=4, column=4)

        global comboBoxsDayTrade
        comboBoxsDayTrade = self.comboBoxsDayTrade
                        
        # comboBoxnReserved
        tk.Label(self, text = "預約單(0:否, 1:是)").grid(row=5, column=1)
            #輸入框
        self.comboBoxnReserved = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnReserved['values'] = Config.comboBoxnReserved
        self.comboBoxnReserved.grid(row=5, column=2)

        global comboBoxnReserved
        comboBoxnReserved = self.comboBoxnReserved
                                
        # comboBoxnTimeFlag
        tk.Label(self, text = "預約盤別(1:T盤, 2:T+1盤)").grid(row=5, column=3)
            #輸入框
        self.comboBoxnTimeFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTimeFlag['values'] = Config.comboBoxnTimeFlag
        self.comboBoxnTimeFlag.grid(row=5, column=4)

        global comboBoxnTimeFlag
        comboBoxnTimeFlag = self.comboBoxnTimeFlag
                                
        # comboBoxnLongActionFlag
        tk.Label(self, text = "是否為長效單(0:否, 1:是)").grid(row=6, column=1)
            #輸入框
        self.comboBoxnLongActionFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLongActionFlag['values'] = Config.comboBoxnLongActionFlag
        self.comboBoxnLongActionFlag.grid(row=6, column=2)

        global comboBoxnLongActionFlag
        comboBoxnLongActionFlag = self.comboBoxnLongActionFlag
                                                        
        # textBoxbstrLongEndDate
        tk.Label(self, text = "長效單結束日期(YYYYMMDD共8碼, EX: 20220630)").grid(row=7, column=1)
        #輸入框
        self.textBoxbstrLongEndDate = tk.Entry(self, width= 6)
        self.textBoxbstrLongEndDate.grid(row=7, column=2)

        global textBoxbstrLongEndDate
        textBoxbstrLongEndDate = self.textBoxbstrLongEndDate
                                        
        # comboBoxnLAType
        tk.Label(self, text = "觸發結束條件(1:效期內觸發即失效, 3:效期內完全成交即失效)").grid(row=8, column=1)
            #輸入框
        self.comboBoxnLAType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnLAType['values'] = Config.comboBoxnLAType
        self.comboBoxnLAType.grid(row=8, column=2)

        global comboBoxnLAType
        comboBoxnLAType = self.comboBoxnLAType

        # buttonSendOverSeaFutureOCOOrder
        self.buttonSendOverSeaFutureOCOOrder = tk.Button(self)
        self.buttonSendOverSeaFutureOCOOrder["text"] = "OCO送出"
        self.buttonSendOverSeaFutureOCOOrder["command"] = self.buttonSendOverSeaFutureOCOOrder_Click
        self.buttonSendOverSeaFutureOCOOrder.grid(row=9, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonSendOverSeaFutureOCOOrder_Click(self):
        
        pOrder = sk.OVERSEAFUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrExchangeNo = textBoxExchangeNo.get()
        pOrder.bstrStockNo = textBoxStockNo.get()
        pOrder.bstrYearMonth = textBoxbstrYearMonth.get()
        pOrder.bstrTrigger = textBoxbstrTrigger.get()
        pOrder.bstrTriggerNumerator = textBoxTriggerNumerator.get()
        pOrder.bstrTriggerDenominator = textBoxbstrTriggerDenominator.get()
        pOrder.bstrOrder = textBoxbstrOrder.get()
        pOrder.bstrOrderNumerator = textBoxbstrOrderNumerator.get()
        pOrder.bstrOrderDenominator = textBoxbstrOrderDenominator.get()

        if (comboBoxsBuySell.get() == "0:買進"):
            pOrder.sBuySell = 0
        elif (comboBoxsBuySell.get() == "1:賣出"):
            pOrder.sBuySell = 1

        pOrder.bstrOrder2 = textBoxbstrOrder2.get()
        pOrder.bstrOrderNumerator2 = textBoxbstrOrderNumerator2.get()
        pOrder.bstrOrderDenominator2 = textBoxbstrOrderDenominator2.get()
        pOrder.bstrTrigger2 = textBoxbstrTrigger2.get()
        pOrder.bstrTriggerNumerator2 = textBoxbstrTriggerNumerator2.get()
        pOrder.bstrTriggerDenominator2 = textBoxbstrTriggerDenominator2.get()

        if (comboBoxnBuySell2.get() == "0:買進"):
            pOrder.nBuySell2 = 0
        elif (comboBoxnBuySell2.get() == "1:賣出"):
            pOrder.nBuySell2 = 1

        if (comboBoxsTradeType.get() == "0:ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxsTradeType.get() == "3:IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxnReserved.get() == "0:否"):
            pOrder.nReserved = 0
        else:
            pOrder.nReserved = 1

        if (comboBoxnTimeFlag.get() == "1:T盤"):
            pOrder.nTimeFlag = 1
        else:
            pOrder.nTimeFlag = 2

        if (comboBoxnLongActionFlag.get() == "0:否"):
            pOrder.nLongActionFlag = 0
        else:
            pOrder.nLongActionFlag = 1

        pOrder.bstrLongEndDate = textBoxbstrLongEndDate.get()

        if (comboBoxnLAType.get() == "1:效期內觸發即失效"):
            pOrder.nLAType = 1
        else:
            pOrder.nLAType = 3

        if (comboBoxnOrderPriceType.get() == "1:市價"):
            pOrder.nOrderPriceType = 1
        else:
            pOrder.nOrderPriceType = 2

        if (comboBoxsDayTrade.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        pOrder.nQty = int(textBoxnQty.get())

        # 送出海外期貨OCO(含長效)委託
        bstrMessage,nCode= m_pSKOrder.SendOverSeaFutureOCOOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendOverSeaFutureOCOOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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

        # textBoxExchangeNoAB
        tk.Label(self, text = "A商品交易所代碼 (EX: CME)").grid(row=0, column=1)
        #輸入框
        self.textBoxExchangeNoAB = tk.Entry(self, width= 6)
        self.textBoxExchangeNoAB.grid(row=0, column=2)

        global textBoxExchangeNoAB
        textBoxExchangeNoAB = self.textBoxExchangeNoAB
        
        # textBoxbstrStockNo2
        tk.Label(self, text = "A商品商品代號").grid(row=0, column=3)
        #輸入框
        self.textBoxbstrStockNo2 = tk.Entry(self, width= 6)
        self.textBoxbstrStockNo2.grid(row=0, column=4)

        global textBoxbstrStockNo2
        textBoxbstrStockNo2 = self.textBoxbstrStockNo2

        # comboBoxnMarketNo
        tk.Label(self, text = "市場編號(1:國內證, 2:國內期, 3:國外證, 4:國外期)").grid(row=1, column=1)
            #輸入框
        self.comboBoxnMarketNo = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnMarketNo['values'] = Config.comboBoxnMarketNo
        self.comboBoxnMarketNo.grid(row=1, column=2)

        global comboBoxnMarketNo
        comboBoxnMarketNo = self.comboBoxnMarketNo
        
        # comboBoxOFSpecialTradeType
        tk.Label(self, text = "0:非證券,1:上市, 2:上櫃").grid(row=1, column=3)
            #輸入框
        self.comboBoxOFSpecialTradeType = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxOFSpecialTradeType['values'] = Config.comboBoxOFSpecialTradeType
        self.comboBoxOFSpecialTradeType.grid(row=1, column=4)

        global comboBoxOFSpecialTradeType
        comboBoxOFSpecialTradeType = self.comboBoxOFSpecialTradeType
        
        # textBoxbstrOrder2AB
        tk.Label(self, text = "A商品市價").grid(row=2, column=1)
        #輸入框
        self.textBoxbstrOrder2AB = tk.Entry(self, width= 6)
        self.textBoxbstrOrder2AB.grid(row=2, column=2)

        global textBoxbstrOrder2AB
        textBoxbstrOrder2AB = self.textBoxbstrOrder2AB
                
        # comboBoxnTriggerDirection
        tk.Label(self, text = "觸價方向(1:GTE大於等於,2:LTE小於等於)").grid(row=2, column=3)
            #輸入框
        self.comboBoxnTriggerDirection = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTriggerDirection['values'] = Config.comboBoxnTriggerDirection
        self.comboBoxnTriggerDirection.grid(row=2, column=4)

        global comboBoxnTriggerDirection
        comboBoxnTriggerDirection = self.comboBoxnTriggerDirection
                
        # textBoxbstrTriggerAB
        tk.Label(self, text = "觸發價").grid(row=2, column=5)
        #輸入框
        self.textBoxbstrTriggerAB = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerAB.grid(row=2, column=6)

        global textBoxbstrTriggerAB
        textBoxbstrTriggerAB = self.textBoxbstrTriggerAB
                        
        # textBoxTriggerNumeratorAB
        tk.Label(self, text = "分子").grid(row=2, column=7)
        #輸入框
        self.textBoxTriggerNumeratorAB = tk.Entry(self, width= 6)
        self.textBoxTriggerNumeratorAB.grid(row=2, column=8)

        global textBoxTriggerNumeratorAB
        textBoxTriggerNumeratorAB = self.textBoxTriggerNumeratorAB
                                
        # textBoxbstrTriggerDenominatorAB
        tk.Label(self, text = "分母").grid(row=2, column=9)
        #輸入框
        self.textBoxbstrTriggerDenominatorAB = tk.Entry(self, width= 6)
        self.textBoxbstrTriggerDenominatorAB.grid(row=2, column=10)

        global textBoxbstrTriggerDenominatorAB
        textBoxbstrTriggerDenominatorAB = self.textBoxbstrTriggerDenominatorAB
                        
        # comboBoxsBuySellAB
        tk.Label(self, text = "買賣別(0:買進, 1:賣出)").grid(row=3, column=1)
            #輸入框
        self.comboBoxsBuySellAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsBuySellAB['values'] = Config.comboBoxsBuySellAB
        self.comboBoxsBuySellAB.grid(row=3, column=2)

        global comboBoxsBuySellAB
        comboBoxsBuySellAB = self.comboBoxsBuySellAB
                                
        # comboBoxnBuySell2AB
        tk.Label(self, text = "買賣別2(0:買進, 1:賣出) ，非價差商品請填0").grid(row=3, column=3)
            #輸入框
        self.comboBoxnBuySell2AB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnBuySell2AB['values'] = Config.comboBoxnBuySell2AB
        self.comboBoxnBuySell2AB.grid(row=3, column=4)

        global comboBoxnBuySell2AB
        comboBoxnBuySell2AB = self.comboBoxnBuySell2AB
                                        
        # comboBoxsDayTradeAB
        tk.Label(self, text = "是否為當沖(0:否, 1:是)").grid(row=3, column=5)
            #輸入框
        self.comboBoxsDayTradeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsDayTradeAB['values'] = Config.comboBoxsDayTradeAB
        self.comboBoxsDayTradeAB.grid(row=3, column=6)

        global comboBoxsDayTradeAB
        comboBoxsDayTradeAB = self.comboBoxsDayTradeAB
                                                
        # comboBoxsTradeTypeAB
        tk.Label(self, text = "委託時效(0:ROC, 3:IOC, 4:FOK, 委託海期範圍市價、海選市限價僅有ROD)").grid(row=3, column=7)
            #輸入框
        self.comboBoxsTradeTypeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsTradeTypeAB['values'] = Config.comboBoxsTradeTypeAB
        self.comboBoxsTradeTypeAB.grid(row=3, column=8)

        global comboBoxsTradeTypeAB
        comboBoxsTradeTypeAB = self.comboBoxsTradeTypeAB
                                
        # textBoxbstrExchangeNo2
        tk.Label(self, text = "B商品交易所代碼 (EX: CME)").grid(row=4, column=1)
        #輸入框
        self.textBoxbstrExchangeNo2 = tk.Entry(self, width= 6)
        self.textBoxbstrExchangeNo2.grid(row=4, column=2)

        global textBoxbstrExchangeNo2
        textBoxbstrExchangeNo2 = self.textBoxbstrExchangeNo2
                                
        # textBoxStockNoAB
        tk.Label(self, text = "B商品商品代碼 (EX: ES)").grid(row=4, column=3)
        #輸入框
        self.textBoxStockNoAB = tk.Entry(self, width= 6)
        self.textBoxStockNoAB.grid(row=4, column=4)

        global textBoxStockNoAB
        textBoxStockNoAB = self.textBoxStockNoAB
                                        
        # textBoxbstrYearMonthAB
        tk.Label(self, text = "商品契約月份(YYYYMM共6碼, EX: 202206)").grid(row=4, column=5)
        #輸入框
        self.textBoxbstrYearMonthAB = tk.Entry(self, width= 6)
        self.textBoxbstrYearMonthAB.grid(row=4, column=6)

        global textBoxbstrYearMonthAB
        textBoxbstrYearMonthAB = self.textBoxbstrYearMonthAB
                                                
        # textBoxbstrYearMonth2
        tk.Label(self, text = "商品契約月份2(非價差商品請填0)").grid(row=4, column=7)
        #輸入框
        self.textBoxbstrYearMonth2 = tk.Entry(self, width= 6)
        self.textBoxbstrYearMonth2.grid(row=4, column=8)

        global textBoxbstrYearMonth2
        textBoxbstrYearMonth2 = self.textBoxbstrYearMonth2
                                                        
        # comboBoxnSpreadFlag
        tk.Label(self, text = "是否委託價差商品(0:否, 1:是)").grid(row=5, column=1)
            #輸入框
        self.comboBoxnSpreadFlag = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnSpreadFlag['values'] = Config.comboBoxnSpreadFlag
        self.comboBoxnSpreadFlag.grid(row=5, column=2)

        global comboBoxnSpreadFlag
        comboBoxnSpreadFlag = self.comboBoxnSpreadFlag
                                                                
        # comboBoxsCallPut
        tk.Label(self, text = "是否為選擇權(0:否, 1:Call, 2:Put)").grid(row=6, column=1)
            #輸入框
        self.comboBoxsCallPut = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsCallPut['values'] = Config.comboBoxsCallPut
        self.comboBoxsCallPut.grid(row=6, column=2)

        global comboBoxsCallPut
        comboBoxsCallPut = self.comboBoxsCallPut
                                                        
        # textBoxbstrStrikePrice
        tk.Label(self, text = "履約價格(非選擇權商品請填0)").grid(row=6, column=3)
        #輸入框
        self.textBoxbstrStrikePrice = tk.Entry(self, width= 6)
        self.textBoxbstrStrikePrice.grid(row=6, column=4)

        global textBoxbstrStrikePrice
        textBoxbstrStrikePrice = self.textBoxbstrStrikePrice
                                                                        
        # comboBoxsNewClose
        tk.Label(self, text = "新平倉(0:新倉, 1:平倉) 選擇權僅新、平倉，期貨商品僅新倉").grid(row=6, column=5)
            #輸入框
        self.comboBoxsNewClose = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxsNewClose['values'] = Config.comboBoxsNewClose
        self.comboBoxsNewClose.grid(row=6, column=6)

        global comboBoxsNewClose
        comboBoxsNewClose = self.comboBoxsNewClose
                                                                
        # textBoxnQtyAB
        tk.Label(self, text = "委託口數").grid(row=7, column=1)
        #輸入框
        self.textBoxnQtyAB = tk.Entry(self, width= 6)
        self.textBoxnQtyAB.grid(row=7, column=2)

        global textBoxnQtyAB
        textBoxnQtyAB = self.textBoxnQtyAB
                                                                                
        # comboBoxnOrderPriceTypeAB
        tk.Label(self, text = "委託價類別(1:市價,  2:限價)").grid(row=7, column=3)
            #輸入框
        self.comboBoxnOrderPriceTypeAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnOrderPriceTypeAB['values'] = Config.comboBoxnOrderPriceTypeAB
        self.comboBoxnOrderPriceTypeAB.grid(row=7, column=4)

        global comboBoxnOrderPriceTypeAB
        comboBoxnOrderPriceTypeAB = self.comboBoxnOrderPriceTypeAB
                
        # textBoxbstrOrderAB
        tk.Label(self, text = "委託價").grid(row=7, column=5)
        #輸入框
        self.textBoxbstrOrderAB = tk.Entry(self, width= 6)
        self.textBoxbstrOrderAB.grid(row=7, column=6)

        global textBoxbstrOrderAB
        textBoxbstrOrderAB = self.textBoxbstrOrderAB
                        
        # textBoxbstrOrderNumeratorAB
        tk.Label(self, text = "分子").grid(row=7, column=7)
        #輸入框
        self.textBoxbstrOrderNumeratorAB = tk.Entry(self, width= 6)
        self.textBoxbstrOrderNumeratorAB.grid(row=7, column=8)

        global textBoxbstrOrderNumeratorAB
        textBoxbstrOrderNumeratorAB = self.textBoxbstrOrderNumeratorAB
                                
        # textBoxbstrOrderDenominatorAB
        tk.Label(self, text = "分母").grid(row=7, column=9)
        #輸入框
        self.textBoxbstrOrderDenominatorAB = tk.Entry(self, width= 6)
        self.textBoxbstrOrderDenominatorAB.grid(row=7, column=10)

        global textBoxbstrOrderDenominatorAB
        textBoxbstrOrderDenominatorAB = self.textBoxbstrOrderDenominatorAB
                                                                                     
        # comboBoxnTimeFlagAB
        tk.Label(self, text = "是否為預約單(0:否, 1:是)A商品為國內期選市場時可選擇預約單").grid(row=8, column=1)
            #輸入框
        self.comboBoxnTimeFlagAB = ttk.Combobox(self, state='readonly', width= 6)
        self.comboBoxnTimeFlagAB['values'] = Config.comboBoxnTimeFlagAB
        self.comboBoxnTimeFlagAB.grid(row=8, column=2)

        global comboBoxnTimeFlagAB
        comboBoxnTimeFlagAB = self.comboBoxnTimeFlagAB

        # buttonendOverSeaFutureABOrder
        self.buttonendOverSeaFutureABOrder = tk.Button(self)
        self.buttonendOverSeaFutureABOrder["text"] = "AB送出"
        self.buttonendOverSeaFutureABOrder["command"] = self.buttonendOverSeaFutureABOrder_Click
        self.buttonendOverSeaFutureABOrder.grid(row=9, column=1)

    # checkBoxAsyncOrder
    def checkBoxAsyncOrder_CheckedChanged(self):
        global bAsyncOrder
        if self.var1.get() == True:
            bAsyncOrder = True
        else:
            bAsyncOrder = False
    
    def buttonendOverSeaFutureABOrder_Click(self):
        pOrder = sk.OVERSEAFUTUREORDER()

        pOrder.bstrFullAccount = comboBoxAccount.get()
        pOrder.bstrStockNo = textBoxStockNoAB.get()
        pOrder.bstrExchangeNo = textBoxExchangeNoAB.get()
        pOrder.bstrYearMonth = textBoxbstrYearMonthAB.get()
        pOrder.bstrYearMonth2 = textBoxbstrYearMonth2.get()
        pOrder.bstrOrder = textBoxbstrOrderAB.get()
        pOrder.bstrOrderNumerator = textBoxbstrOrderNumeratorAB.get()
        pOrder.bstrOrderDenominator = textBoxbstrOrderDenominatorAB.get()
        pOrder.bstrTrigger = textBoxbstrTriggerAB.get()
        pOrder.bstrTriggerNumerator = textBoxTriggerNumeratorAB.get()
        pOrder.bstrTriggerDenominator = textBoxbstrTriggerDenominatorAB.get()

        if (comboBoxsBuySellAB.get() == "0:買進"):
            pOrder.sBuySell = 0
        elif (comboBoxsBuySellAB.get() == "1:賣出"):
            pOrder.sBuySell = 1

        pOrder.bstrOrder2 = textBoxbstrOrder2AB.get()
  
        if (comboBoxnBuySell2AB.get() == "0:買進"):
            pOrder.nBuySell2 = 0
        elif (comboBoxnBuySell2AB.get() == "1:賣出"):
            pOrder.nBuySell2 = 1

        if (comboBoxsTradeTypeAB.get() == "0:ROD"):
            pOrder.sTradeType = 0
        elif (comboBoxsTradeTypeAB.get() == "3:IOC"):
            pOrder.sTradeType = 3
        else:
            pOrder.sTradeType = 4

        if (comboBoxnTriggerDirection.get() == "1:GTE大於等於"):
            pOrder.nTriggerDirection = 1
        else:
            pOrder.nTriggerDirection = 2

        if (comboBoxnTimeFlagAB.get() == "0:否"):
            pOrder.nTimeFlag = 0
        else :
            pOrder.nTimeFlag = 1

        if (comboBoxnOrderPriceTypeAB.get() == "1:市價"):
            pOrder.nOrderPriceType = 1
        else:
            pOrder.nOrderPriceType = 2

        if (comboBoxsDayTradeAB.get() == "0:否"):
            pOrder.sDayTrade = 0
        else:
            pOrder.sDayTrade = 1

        pOrder.nQty = int(textBoxnQtyAB.get())

        pOrder.bstrStockNo2 = textBoxbstrStockNo2.get()

        if (comboBoxnMarketNo.get() == "1:國內證"):
            pOrder.nMarketNo = 1
        elif (comboBoxnMarketNo.get() == "2:國內期"):
            pOrder.nMarketNo = 2
        elif (comboBoxnMarketNo.get() == "3:國外證"):
            pOrder.nMarketNo = 3
        else:
            pOrder.nMarketNo = 4

        if (comboBoxOFSpecialTradeType.get() == "0:非證券"):
            pOrder.sSpecialTradeType = 0
        elif (comboBoxOFSpecialTradeType.get() == "1:上市"):
            pOrder.sSpecialTradeType = 1
        else:
            pOrder.sSpecialTradeType = 2


        if (comboBoxsCallPut.get() == "0:否"):
            pOrder.sCallPut = 0
        elif (comboBoxsCallPut.get() == "1:Call"):
            pOrder.sCallPut = 1
        else:
            pOrder.sCallPut = 2

        pOrder.bstrStrikePrice = textBoxbstrStrikePrice.get()

        if (comboBoxnSpreadFlag.get() == "0:否"):
            pOrder.nSpreadFlag = 0
        else:
            pOrder.nSpreadFlag = 1

        pOrder.bstrYearMonth2 = textBoxbstrYearMonth2.get()

        if (comboBoxsNewClose.get() == "0:新倉"):
            pOrder.sNewClose = 0
        else:
            pOrder.sNewClose = 1

        # 送出海外期貨AB單委託
        bstrMessage,nCode= m_pSKOrder.SendOverSeaFutureABOrder(comboBoxUserID.get(), bAsyncOrder, pOrder)

        msg = "【SendOverSeaFutureABOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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
        tk.Label(self, text = "3：OCO、10：AB").grid(row=1, column=1)
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

        # buttonCancelOFStrategyOrder
        self.buttonCancelOFStrategyOrder = tk.Button(self)
        self.buttonCancelOFStrategyOrder["text"] = "刪單送出"
        self.buttonCancelOFStrategyOrder["command"] = self.buttonCancelOFStrategyOrder_Click
        self.buttonCancelOFStrategyOrder.grid(row=6, column=2)
              
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
    
    def buttonCancelOFStrategyOrder_Click(self):
        
        pCancelOrder = sk.CANCELSTRATEGYORDER()

        pCancelOrder.bstrFullAccount = comboBoxAccount.get()
        pCancelOrder.bstrSmartKey = textBoxbstrSmartKey.get()

        if (comboBoxnMarket.get() == "1：國內證"):
            pCancelOrder.nMarket = 1
        elif (comboBoxnMarket.get() == "2：國內期"):
            pCancelOrder.nMarket = 2
        elif (comboBoxnMarket.get() == "3：國外證"):
            pCancelOrder.nMarket = 3
        elif (comboBoxnMarket.get() == "4：國外期"):
            pCancelOrder.nMarket = 4

        if (comboBoxnTradeKind.get() == "3:OCO"):
            pCancelOrder.nTradeKind = 3
        else:
            pCancelOrder.nTradeKind = 10

        pCancelOrder.bstrSeqNo = textBoxbstrSeqNo.get()
        pCancelOrder.bstrOrderNo = textBoxbstrOrderNo.get()
        pCancelOrder.bstrLongActionKey = textBoxbstrLongActionKey.get()

        # 取消海期智慧單委託。刪單欄位請參考GetOFStrategyOrder 回傳的內容
        bstrMessage,nCode= m_pSKOrder.CancelOFStrategyOrder(comboBoxUserID.get(), pCancelOrder)

        msg = "【CancelOFStrategyOrder】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
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
        tk.Label(self, text = "智慧單類型(OCO：二擇一、AB：AB單)").grid(row=0, column=1)
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

        if (comboBoxbstrKind.get() == "OCO:二擇一(長效單)"):
            bstrKind = "OCO"
        else:
            bstrKind = "AB"

        # 查詢海期智慧單
        nCode= m_pSKOrder.GetOFSmartStrategyReport(comboBoxUserID.get(), comboBoxAccount.get(),"OF",  0, bstrKind, textBoxbstrDate.get())

        msg = "【GetOFSmartStrategyReport】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
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
#==========================================
#定義彈出視窗
def popup_window_Load():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Load")

    # 建立 Frame 作為 LoadForm，並添加到彈出窗口
    popup_LoadForm = LoadForm(popup)
    popup_LoadForm.pack(fill=tk.BOTH, expand=True)
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
    root.title("OFtrategyOrder")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)

    
    # 開啟Load視窗的按鈕
    popup_button_Load = tk.Button(root, text="下載商品檔", command=popup_window_Load)
    popup_button_Load.grid(row = 1, column= 0)

    # 開啟OCO視窗的按鈕
    popup_button_OCO = tk.Button(root, text="OCO", command=popup_window_OCO)
    popup_button_OCO.grid(row = 2, column= 0)

    # 開啟AB視窗的按鈕
    popup_button_AB = tk.Button(root, text="AB", command=popup_window_AB)
    popup_button_AB.grid(row = 3, column= 0)

    # 開啟Cancel視窗的按鈕
    popup_button_CB = tk.Button(root, text="刪單", command=popup_window_Cancel)
    popup_button_CB.grid(row = 4, column= 0)

    # 開啟Get視窗的按鈕
    popup_button_CB = tk.Button(root, text="查詢", command=popup_window_Get)
    popup_button_CB.grid(row = 5, column= 0)

    root.mainloop()

#==========================================
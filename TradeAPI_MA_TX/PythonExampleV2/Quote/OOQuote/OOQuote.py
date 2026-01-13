# API com元件初始化
import comtypes.client
comtypes.client.GetModule(r'SKCOM.dll')
import comtypes.gen.SKCOMLib as sk

# 群益API元件導入Python code內用的物件宣告
m_pSKCenter = comtypes.client.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
m_pSKQuote = comtypes.client.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)
m_pSKOSQuote = comtypes.client.CreateObject(sk.SKOSQuoteLib,interface=sk.ISKOSQuoteLib)
m_pSKOOQuote = comtypes.client.CreateObject(sk.SKOOQuoteLib,interface=sk.ISKOOQuoteLib)
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

# 海期報價伺服器 0：預設  1：備援
sServer = 0
######################################################################################################################################
# ReplyLib事件
class SKReplyLibEvent():
    def OnReplyMessage(self, bstrUserID, bstrMessages):
        nConfirmCode = -1
        msg = "【註冊公告OnReplyMessage】" + bstrUserID + "_" + bstrMessages
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
        return nConfirmCode
SKReplyEvent = SKReplyLibEvent()
SKReplyLibEventHandler = comtypes.client.GetEvents(m_pSKReply, SKReplyEvent)

# OOQuoteLib事件
class SKOOQuoteLibEvent():
    def OnConnect(self, nCode, nSocketCode):
        msg = "【OnConnect】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + "_" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nSocketCode)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnProducts(self, bstrValue):
        msg = "【OnProducts】" + bstrValue
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnNotifyQuoteLONG(self, nIndex):
        pSKStock = sk.SKFOREIGNLONG()
        pSKStock, nCode = m_pSKOOQuote.SKOOQuoteLib_GetStockByIndexLONG(nIndex, pSKStock)
        msg = "【OnNotifyQuoteLONG】" + " 報價小數位數" + str(pSKStock.sDecimal) + " 分母" + str(pSKStock.nDenominator) + " 市場代碼" + str(pSKStock.bstrMarketNo) + " 交易所代號" + str(pSKStock.bstrExchangeNo) + " 交易所名稱" + str(pSKStock.bstrExchangeName) + " 商品代號" + str(pSKStock.bstrStockNo) + " 商品名稱" + str(pSKStock.bstrStockName) + " CallPut" + str(pSKStock.bstrCallPut) + " 開盤價" + str(pSKStock.nOpen) + " 最高價" + str(pSKStock.nHigh) + " 最低價" + str(pSKStock.nLow) + " 成交價" + str(pSKStock.nClose) + " 結算價" + str(pSKStock.nSettlePrice) + " 單量" + str(pSKStock.nTickQty) + " 昨收、參考價" + str(pSKStock.nRef) + " 買價" + str(pSKStock.nBid) + " 買量" + str(pSKStock.nBc) + " 賣價" + str(pSKStock.nAsk) + " 賣量" + str(pSKStock.nAc) + " 成交量" + str(pSKStock.nTQty) + " 履約價" + str(pSKStock.nStrikePrice) + " 交易日(YYYYMMDD)" + str(pSKStock.nTradingDay)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')

        strPriceInf = (str(pSKStock.sDecimal)  + "," + 
            str(pSKStock.nDenominator) + "," + 
            str(pSKStock.bstrMarketNo) + "," + 
            str(pSKStock.bstrExchangeNo) + "," + 
            str(pSKStock.bstrExchangeName) + "," +
            str(pSKStock.bstrStockNo) + ","  +
            str(pSKStock.bstrCallPut) + ","  +
            str(pSKStock.nOpen) + ","  +
            str(pSKStock.nHigh) + ","  +
            str(pSKStock.nLow) + ","  +
            str(pSKStock.nClose) + ","  +
            str(pSKStock.nSettlePrice) + ","  +
            str(pSKStock.nTickQty) + ","  +
            str(pSKStock.nRef) + ","  +
            str(pSKStock.nBid) + ","  +
            str(pSKStock.nBc) + ","  +
            str(pSKStock.nAsk) + ","  +
            str(pSKStock.nAc) + ","  +
            str(pSKStock.nTQty) + ","  +
            str(pSKStock.nStrikePrice) + ","  +
            str(pSKStock.nTradingDay))
        #global treeviewStocks
        self.insert_item(str(pSKStock.bstrStockNo), (str(pSKStock.bstrStockName), strPriceInf))

    def insert_item(self, text, values):
        #global treeviewStocks
        #檢查相同股票代號時，就更換價格資訊
        existing_items = treeviewStocks.get_children()
        for item in existing_items:
            item_text = treeviewStocks.item(item, "text")
            if item_text == text:
                treeviewStocks.item(item, values=values)
                return

        # 插入新的項
        treeviewStocks.insert("", index="end", text=text, values=values)
    
    def OnNotifyTicksLONG(self, nIndex, nPtr, nDate, nTime, nClose, nQty):
        pSKTick = sk.SKFOREIGNTICK()
        pSKTick, nCode = m_pSKOOQuote.SKOOQuoteLib_GetTickLONG(nIndex, nPtr, pSKTick)
        msg = "【OnNotifyTicksLONG】" + " 成交時間" + str(pSKTick.nTime) + " 成交價" + str(pSKTick.nClose) + " 成交量" + str(pSKTick.nQty) + " 成交日期YYYYMMDD" + str(pSKTick.nDate) 
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
        
        hour = str(nTime)[:2]
        min = str(nTime)[2:4]
        sec = str(nTime)[4:6]

        richTextBoxTickMessage.insert('end', hour + ":" + min + ":" + sec + "     " + str(nClose / 100.0) + "     " + str(nQty) + "\n")
        richTextBoxTickMessage.see('end')

    def OnNotifyBest5LONG(self, nStockidx, nBestBid1, nBestBidQty1, nBestBid2, nBestBidQty2, nBestBid3, nBestBidQty3, nBestBid4, nBestBidQty4, nBestBid5, nBestBidQty5, nBestAsk1, nBestAskQty1, nBestAsk2, nBestAskQty2, nBestAsk3, nBestAskQty3, nBestAsk4, nBestAskQty4, nBestAsk5, nBestAskQty5):
        pSKBest5 = sk.SKBEST5()
        pSKBest5, nCode = m_pSKOOQuote.SKOOQuoteLib_GetBest5LONG(nStockidx, pSKBest5)
        msg = "【OnNotifyBest5LONG】" + " 1買量" + str(pSKBest5.nBidQty1) + " 1買價" + str(pSKBest5.nBid1 / 100) + " 1賣價" + str(pSKBest5.nAsk1 / 100) + " 1賣量" + str(pSKBest5.nAskQty1) + " 2買量" + str(pSKBest5.nBidQty2) + " 2買價" + str(pSKBest5.nBid2 / 100) + " 2賣價" + str(pSKBest5.nAsk2 / 100) + " 2賣量" + str(pSKBest5.nAskQty2)  + " 3買量" + str(pSKBest5.nBidQty3) + " 3買價" + str(pSKBest5.nBid3 / 100) + " 3賣價" + str(pSKBest5.nAsk3 / 100) + " 3賣量" + str(pSKBest5.nAskQty3)  + " 4買量" + str(pSKBest5.nBidQty4) + " 4買價" + str(pSKBest5.nBid4 / 100) + " 4賣價" + str(pSKBest5.nAsk4 / 100) + " 4賣量" + str(pSKBest5.nAskQty4)  + " 5買量" + str(pSKBest5.nBidQty5) + " 5買價" + str(pSKBest5.nBid5 / 100) + " 5賣價" + str(pSKBest5.nAsk5 / 100) + " 5賣量" + str(pSKBest5.nAskQty5)  
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
        
        labelnBestBidQty1.config(text = str(nBestBidQty1))
        labelnBestBidQty2.config(text = str(nBestBidQty2))
        labelnBestBidQty3.config(text = str(nBestBidQty3))
        labelnBestBidQty4.config(text = str(nBestBidQty4))
        labelnBestBidQty5.config(text = str(nBestBidQty5))

        labelnBestBid1.config(text = str(nBestBid1 / 100.0))        
        labelnBestBid2.config(text = str(nBestBid2 / 100.0))  
        labelnBestBid3.config(text = str(nBestBid3 / 100.0))  
        labelnBestBid4.config(text = str(nBestBid4 / 100.0))  
        labelnBestBid5.config(text = str(nBestBid5 / 100.0))

        labelnBestAsk1.config(text = str(nBestAsk1 / 100.0))
        labelnBestAsk2.config(text = str(nBestAsk2 / 100.0))
        labelnBestAsk3.config(text = str(nBestAsk3 / 100.0))
        labelnBestAsk4.config(text = str(nBestAsk4 / 100.0))
        labelnBestAsk5.config(text = str(nBestAsk5 / 100.0))  

        labelnBestAskQty1.config(text = str(nBestAskQty1))
        labelnBestAskQty2.config(text = str(nBestAskQty2))
        labelnBestAskQty3.config(text = str(nBestAskQty3))
        labelnBestAskQty4.config(text = str(nBestAskQty4))
        labelnBestAskQty5.config(text = str(nBestAskQty5))
        
    def OnNotifyBest10LONG(self, nStockidx, nBestBid1, nBestBidQty1, nBestBid2, nBestBidQty2, nBestBid3, nBestBidQty3, nBestBid4, nBestBidQty4, nBestBid5, nBestBidQty5, nBestBid6, nBestBidQty6, nBestBid7, nBestBidQty7, nBestBid8, nBestBidQty8, nBestBid9, nBestBidQty9, nBestBid10, nBestBidQty10, nBestAsk1, nBestAskQty1, nBestAsk2, nBestAskQty2, nBestAsk3, nBestAskQty3, nBestAsk4, nBestAskQty4, nBestAsk5, nBestAskQty5, nBestAsk6, nBestAskQty6, nBestAsk7, nBestAskQty7, nBestAsk8, nBestAskQty8, nBestAsk9, nBestAskQty9, nBestAsk10, nBestAskQty10):

        msg = "【OnNotifyBest10LONG】" + " 1買量" + str(nBestBidQty1) + " 1買價" + str(nBestBid1 / 100) + " 1賣價" + str(nBestAsk1 / 100) + " 1賣量" + str(nBestAskQty1) + " 2買量" + str(nBestBidQty2) + " 2買價" + str(nBestBid2 / 100) + " 2賣價" + str(nBestAsk2 / 100) + " 2賣量" + str(nBestAskQty2) + " 3買量" + str(nBestBidQty3) + " 3買價" + str(nBestBid3 / 100) + " 3賣價" + str(nBestAsk3 / 100) + " 3賣量" + str(nBestAskQty3) + " 4買量" + str(nBestBidQty4) + " 4買價" + str(nBestBid4 / 100) + " 4賣價" + str(nBestAsk4 / 100) + " 4賣量" + str(nBestAskQty4) + " 5買量" + str(nBestBidQty5) + " 5買價" + str(nBestBid5 / 100) + " 5賣價" + str(nBestAsk5 / 100) + " 5賣量" + str(nBestAskQty5)  + " 6買量" + str(nBestBidQty6) + " 6買價" + str(nBestBid6 / 100) + " 6賣價" + str(nBestAsk6 / 100) + " 6賣量" + str(nBestAskQty6) + " 7買量" + str(nBestBidQty7) + " 7買價" + str(nBestBid7 / 100) + " 7賣價" + str(nBestAsk7 / 100) + " 7賣量" + str(nBestAskQty7) + " 8買量" + str(nBestBidQty8) + " 8買價" + str(nBestBid8 / 100) + " 8賣價" + str(nBestAsk8 / 100) + " 8賣量" + str(nBestAskQty8) + " 9買量" + str(nBestBidQty9) + " 9買價" + str(nBestBid9 / 100) + " 9賣價" + str(nBestAsk9 / 100) + " 9賣量" + str(nBestAskQty9) + " 10買量" + str(nBestBidQty10) + " 10買價" + str(nBestBid10 / 100) + " 10賣價" + str(nBestAsk10 / 100) + " 10賣量" + str(nBestAskQty10)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
        
        labelnBestBidQty11.config(text = str(nBestBidQty1))
        labelnBestBidQty12.config(text = str(nBestBidQty2))
        labelnBestBidQty13.config(text = str(nBestBidQty3))
        labelnBestBidQty14.config(text = str(nBestBidQty4))
        labelnBestBidQty15.config(text = str(nBestBidQty5))

        labelnBestBid11.config(text = str(nBestBid1 / 100.0))        
        labelnBestBid12.config(text = str(nBestBid2 / 100.0))  
        labelnBestBid13.config(text = str(nBestBid3 / 100.0))  
        labelnBestBid14.config(text = str(nBestBid4 / 100.0))  
        labelnBestBid15.config(text = str(nBestBid5 / 100.0))

        labelnBestAsk11.config(text = str(nBestAsk1 / 100.0))
        labelnBestAsk12.config(text = str(nBestAsk2 / 100.0))
        labelnBestAsk13.config(text = str(nBestAsk3 / 100.0))
        labelnBestAsk14.config(text = str(nBestAsk4 / 100.0))
        labelnBestAsk15.config(text = str(nBestAsk5 / 100.0))  

        labelnBestAskQty11.config(text = str(nBestAskQty1))
        labelnBestAskQty12.config(text = str(nBestAskQty2))
        labelnBestAskQty13.config(text = str(nBestAskQty3))
        labelnBestAskQty14.config(text = str(nBestAskQty4))
        labelnBestAskQty15.config(text = str(nBestAskQty5))
        
        labelnBestBidQty16.config(text = str(nBestBidQty6))
        labelnBestBidQty17.config(text = str(nBestBidQty7))
        labelnBestBidQty18.config(text = str(nBestBidQty8))
        labelnBestBidQty19.config(text = str(nBestBidQty9))
        labelnBestBidQty20.config(text = str(nBestBidQty10))

        labelnBestBid16.config(text = str(nBestBid6 / 100.0))        
        labelnBestBid17.config(text = str(nBestBid7 / 100.0))  
        labelnBestBid18.config(text = str(nBestBid8 / 100.0))  
        labelnBestBid19.config(text = str(nBestBid9 / 100.0))  
        labelnBestBid20.config(text = str(nBestBid10 / 100.0))

        labelnBestAsk16.config(text = str(nBestAsk6 / 100.0))
        labelnBestAsk17.config(text = str(nBestAsk7 / 100.0))
        labelnBestAsk18.config(text = str(nBestAsk8 / 100.0))
        labelnBestAsk19.config(text = str(nBestAsk9 / 100.0))
        labelnBestAsk20.config(text = str(nBestAsk10 / 100.0))  

        labelnBestAskQty16.config(text = str(nBestAskQty6))
        labelnBestAskQty17.config(text = str(nBestAskQty7))
        labelnBestAskQty18.config(text = str(nBestAskQty8))
        labelnBestAskQty19.config(text = str(nBestAskQty9))
        labelnBestAskQty20.config(text = str(nBestAskQty10))

SKOOQuoteEvent = SKOOQuoteLibEvent()
SKOOQuoteLibEventHandler = comtypes.client.GetEvents(m_pSKOOQuote, SKOOQuoteEvent)

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
#ConnectForm
class ConnectForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):
        
        # buttonSKOOQuoteLib_EnterMonitorLONG
        self.buttonSKOOQuoteLib_EnterMonitorLONG = tk.Button(self)
        self.buttonSKOOQuoteLib_EnterMonitorLONG["text"] = "連線報價主機"
        self.buttonSKOOQuoteLib_EnterMonitorLONG["command"] = self.buttonSKOOQuoteLib_EnterMonitorLONG_Click
        self.buttonSKOOQuoteLib_EnterMonitorLONG.grid(row=0, column=1)
                
        # buttonSKOOQuoteLib_LeaveMonitor
        self.buttonSKOOQuoteLib_LeaveMonitor = tk.Button(self)
        self.buttonSKOOQuoteLib_LeaveMonitor["text"] = "斷線報價主機"
        self.buttonSKOOQuoteLib_LeaveMonitor["command"] = self.buttonSKOOQuoteLib_LeaveMonitor_Click
        self.buttonSKOOQuoteLib_LeaveMonitor.grid(row=1, column=1)
                        
        # buttonSKOOQuoteLib_IsConnected
        self.buttonSKOOQuoteLib_IsConnected = tk.Button(self)
        self.buttonSKOOQuoteLib_IsConnected["text"] = "檢查連線狀態"
        self.buttonSKOOQuoteLib_IsConnected["command"] = self.buttonSKOOQuoteLib_IsConnected_Click
        self.buttonSKOOQuoteLib_IsConnected.grid(row=2, column=1)

    def buttonSKOOQuoteLib_EnterMonitorLONG_Click(self):
        # 與報價伺服器連線
        nCode= m_pSKOOQuote.SKOOQuoteLib_EnterMonitorLONG()

        msg = "【SKOOQuoteLib_EnterMonitorLONG】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    def buttonSKOOQuoteLib_LeaveMonitor_Click(self):
        
        # 中斷報價伺服器連線
        nCode= m_pSKOOQuote.SKOOQuoteLib_LeaveMonitor()

        msg = "【SKOOQuoteLib_LeaveMonitor】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    def buttonSKOOQuoteLib_IsConnected_Click(self):
        
        # 檢查目前報價的連線狀態
        nCode= m_pSKOOQuote.SKOOQuoteLib_IsConnected()
        
        if nCode == 1:
            msg = "連線中"
        else:
            msg = "失敗"

        msg = "【SKOOQuoteLib_IsConnected】" + msg
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#ProductForm
class ProductForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):
        
        # buttonSKOOQuoteLib_RequestProducts
        self.buttonSKOOQuoteLib_RequestProducts = tk.Button(self)
        self.buttonSKOOQuoteLib_RequestProducts["text"] = "取得海選商品檔"
        self.buttonSKOOQuoteLib_RequestProducts["command"] = self.buttonSKOOQuoteLib_RequestProducts_Click
        self.buttonSKOOQuoteLib_RequestProducts.grid(row=0, column=1)


        # textBoxSKOOQuoteLib_GetStockByNoLONG
        tk.Label(self, text = "商品代碼").grid(row=1, column=1)
            #輸入框
        self.textBoxSKOOQuoteLib_GetStockByNoLONG = tk.Entry(self)
        self.textBoxSKOOQuoteLib_GetStockByNoLONG.grid(row=1, column=2)

        global textBoxSKOOQuoteLib_GetStockByNoLONG
        textBoxSKOOQuoteLib_GetStockByNoLONG = self.textBoxSKOOQuoteLib_GetStockByNoLONG
                        
        # buttonSKOOQuoteLib_GetStockByNoLONG
        self.buttonSKOOQuoteLib_GetStockByNoLONG = tk.Button(self)
        self.buttonSKOOQuoteLib_GetStockByNoLONG["text"] = "個選資訊"
        self.buttonSKOOQuoteLib_GetStockByNoLONG["command"] = self.buttonSKOOQuoteLib_GetStockByNoLONG_Click
        self.buttonSKOOQuoteLib_GetStockByNoLONG.grid(row=1, column=3)
 

    def buttonSKOOQuoteLib_RequestProducts_Click(self):
        # 取得海外商品檔
        nCode= m_pSKOOQuote.SKOOQuoteLib_RequestProducts()

        msg = "【SKOOQuoteLib_RequestProducts】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        

    def buttonSKOOQuoteLib_GetStockByNoLONG_Click(self):
        
        pSKStock = sk.SKFOREIGNLONG()

        # (LONG index)根據商品代號，取回海選報價的相關資訊。
        pSKStock, nCode= m_pSKOOQuote.SKOOQuoteLib_GetStockByNoLONG(textBoxSKOOQuoteLib_GetStockByNoLONG.get(), pSKStock)

        msg = "【SKOOQuoteLib_GetStockByNoLONG】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

        msg = "【SKOOQuoteLib_GetStockByNoLONG】" + "商品代號:" + str(pSKStock.bstrStockNo) + " 商品名稱:" + str(pSKStock.bstrStockName) + " 報價小數位數:" + str(pSKStock.sDecimal) + " 分母:" + str(pSKStock.nDenominator) + " 市場代碼:" + str(pSKStock.bstrMarketNo) + " 交易所代號:" + str(pSKStock.bstrExchangeNo) + " 交易所名稱:" + str(pSKStock.bstrExchangeName) + " CallPut:" + str(pSKStock.bstrCallPut) + " 開盤價:" +  str(pSKStock.nOpen) + " 最高:" + str(pSKStock.nHigh) + " 最低:" + str(pSKStock.nLow) + " 成交價:" +  str(pSKStock.nClose) + " 結算價:" + str(pSKStock.nSettlePrice) + " 單量:" + str(pSKStock.nTickQty) + " 昨收(參考價):" +  str(pSKStock.nRef) + " 買價:" +  str(pSKStock.nBid) + " 買量:" + str(pSKStock.nBc) + " 賣價:" + str(pSKStock.nAsk) + " 賣量:" + str(pSKStock.nAc) + " 交易日:" + str(pSKStock.nTradingDay)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
######################################################################################################################################
#RequestForm
class RequestForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # textBoxpsPageNo2
        tk.Label(self, text = "Page").grid(row=0, column=1)
            #輸入框
        self.textBoxpsPageNo2 = tk.Entry(self)
        self.textBoxpsPageNo2.grid(row=0, column=2)

        global textBoxpsPageNo2
        textBoxpsPageNo2 = self.textBoxpsPageNo2
        
        # textBoxStockNos
        tk.Label(self, text = "請輸入商品代號(每檔以,做區隔)").grid(row=0, column=3)
            #輸入框
        self.textBoxStockNos = tk.Entry(self)
        self.textBoxStockNos.grid(row=0, column=4)

        global textBoxStockNos
        textBoxStockNos = self.textBoxStockNos
                        
        # buttonSKOOQuoteLib_RequestStocks
        self.buttonSKOOQuoteLib_RequestStocks = tk.Button(self)
        self.buttonSKOOQuoteLib_RequestStocks["text"] = "訂閱"
        self.buttonSKOOQuoteLib_RequestStocks["command"] = self.buttonSKOOQuoteLib_RequestStocks_Click
        self.buttonSKOOQuoteLib_RequestStocks.grid(row=0, column=5)
        
        # 讓treeview更寬
        tk.Label(self, text = "                                                                                                                                                             ").grid(row=0, column=6)
                
        # treeviewStocks
        self.treeviewStocks = ttk.Treeview(self, columns=("名稱", "價格資訊(報價小數位數,分母,市場代碼,交易所代號,交易所名稱,CallPut,開盤價,最高,最低,成交價,結算價,單量,昨收(參考價),買價,買量,賣價,賣量,交易日)"))
        self.treeviewStocks.heading("#0", text="代碼")
        self.treeviewStocks.heading("#1", text="名稱")
        self.treeviewStocks.heading("#2", text="價格資訊(報價小數位數,分母,市場代碼,交易所代號,交易所名稱,CallPut,開盤價,最高,最低,成交價,結算價,單量,昨收(參考價),買價,買量,賣價,賣量,交易日)")
        self.treeviewStocks.grid(row=2, column=1, columnspan=100, sticky="nsew")

        global treeviewStocks
        treeviewStocks = self.treeviewStocks

        # Remove button
        self.btn_remove = tk.Button(self, text="清除資料", command=self.remove)
        self.btn_remove.grid(row=3, column=1)

    def remove(self):
        # 删除所有项
        self.treeviewStocks.delete(*self.treeviewStocks.get_children())

    def buttonSKOOQuoteLib_RequestStocks_Click(self):
        psPageNo = int(textBoxpsPageNo2.get())
        # 訂閱指定商品即時報價，要求伺服器針對 bstrStockNos 內的商品代號做報價通知動作。報價更新由OnNotifyQuote事件取得更通知。
        psPageNo, nCode= m_pSKOOQuote.SKOOQuoteLib_RequestStocks(psPageNo, textBoxStockNos.get())

        msg = "【SKOOQuoteLib_RequestStocks】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#TicksForm
class TicksForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # textBoxpsPageNo
        tk.Label(self, text = "Page").grid(row=0, column=1)
            #輸入框
        self.textBoxpsPageNo = tk.Entry(self)
        self.textBoxpsPageNo.grid(row=0, column=2)

        global textBoxpsPageNo
        textBoxpsPageNo = self.textBoxpsPageNo
        
        # textBoxTicks
        tk.Label(self, text = "輸入商品代碼(僅1檔)").grid(row=0, column=3)
            #輸入框
        self.textBoxTicks = tk.Entry(self)
        self.textBoxTicks.grid(row=0, column=4)

        global textBoxTicks
        textBoxTicks = self.textBoxTicks
                        
        # buttonSKOOQuoteLib_RequestTicks
        self.buttonSKOOQuoteLib_RequestTicks = tk.Button(self)
        self.buttonSKOOQuoteLib_RequestTicks["text"] = "訂閱"
        self.buttonSKOOQuoteLib_RequestTicks["command"] = self.buttonSKOOQuoteLib_RequestTicks_Click
        self.buttonSKOOQuoteLib_RequestTicks.grid(row=0, column=5)


        


        tk.Label(self, text = "買量").grid(row=1, column=1)
        
        # 買量1
        self.labelnBestBidQty1 = tk.Label(self, text = "")
        self.labelnBestBidQty1.grid(row=2, column=1)

        global labelnBestBidQty1
        labelnBestBidQty1 = self.labelnBestBidQty1
        
        # 買量2
        self.labelnBestBidQty2 = tk.Label(self, text = "")
        self.labelnBestBidQty2.grid(row=3, column=1)

        global labelnBestBidQty2
        labelnBestBidQty2 = self.labelnBestBidQty2
        
        # 買量3
        self.labelnBestBidQty3 = tk.Label(self, text = "")
        self.labelnBestBidQty3.grid(row=4, column=1)

        global labelnBestBidQty3
        labelnBestBidQty3 = self.labelnBestBidQty3
        
        # 買量4
        self.labelnBestBidQty4 = tk.Label(self, text = "")
        self.labelnBestBidQty4.grid(row=5, column=1)

        global labelnBestBidQty4
        labelnBestBidQty4 = self.labelnBestBidQty4
        
        # 買量5
        self.labelnBestBidQty5 = tk.Label(self, text = "")
        self.labelnBestBidQty5.grid(row=6, column=1)

        global labelnBestBidQty5
        labelnBestBidQty5 = self.labelnBestBidQty5        


        tk.Label(self, text = "買價").grid(row=1, column=2)
        
        # 買價1
        self.labelnBestBid1 = tk.Label(self, text = "")
        self.labelnBestBid1.grid(row=2, column=2)

        global labelnBestBid1
        labelnBestBid1 = self.labelnBestBid1
        
        # 買價2
        self.labelnBestBid2 = tk.Label(self, text = "")
        self.labelnBestBid2.grid(row=3, column=2)

        global labelnBestBid2
        labelnBestBid2 = self.labelnBestBid2
        
        # 買價3
        self.labelnBestBid3 = tk.Label(self, text = "")
        self.labelnBestBid3.grid(row=4, column=2)

        global labelnBestBid3
        labelnBestBid3 = self.labelnBestBid3
        
        # 買價4
        self.labelnBestBid4 = tk.Label(self, text = "")
        self.labelnBestBid4.grid(row=5, column=2)

        global labelnBestBid4
        labelnBestBid4 = self.labelnBestBid4
        
        # 買價5
        self.labelnBestBid5 = tk.Label(self, text = "")
        self.labelnBestBid5.grid(row=6, column=2)

        global labelnBestBid5
        labelnBestBid5 = self.labelnBestBid5


        tk.Label(self, text = "賣價").grid(row=1, column=3)
        
        # 賣價1
        self.labelnBestAsk1 = tk.Label(self, text = "")
        self.labelnBestAsk1.grid(row=2, column=3)

        global labelnBestAsk1
        labelnBestAsk1 = self.labelnBestAsk1
        
        # 賣價2
        self.labelnBestAsk2 = tk.Label(self, text = "")
        self.labelnBestAsk2.grid(row=3, column=3)

        global labelnBestAsk2
        labelnBestAsk2 = self.labelnBestAsk2
        
        # 賣價3
        self.labelnBestAsk3 = tk.Label(self, text = "")
        self.labelnBestAsk3.grid(row=4, column=3)

        global labelnBestAsk3
        labelnBestAsk3 = self.labelnBestAsk3
        
        # 賣價4
        self.labelnBestAsk4 = tk.Label(self, text = "")
        self.labelnBestAsk4.grid(row=5, column=3)

        global labelnBestAsk4
        labelnBestAsk4 = self.labelnBestAsk4
        
        # 賣價5
        self.labelnBestAsk5 = tk.Label(self, text = "")
        self.labelnBestAsk5.grid(row=6, column=3)

        global labelnBestAsk5
        labelnBestAsk5 = self.labelnBestAsk5


        tk.Label(self, text = "賣量").grid(row=1, column=4)
        
        # 賣量1
        self.labelnBestAskQty1 = tk.Label(self, text = "")
        self.labelnBestAskQty1.grid(row=2, column=4)

        global labelnBestAskQty1
        labelnBestAskQty1 = self.labelnBestAskQty1
        
        # 賣量2
        self.labelnBestAskQty2 = tk.Label(self, text = "")
        self.labelnBestAskQty2.grid(row=3, column=4)

        global labelnBestAskQty2
        labelnBestAskQty2 = self.labelnBestAskQty2
        
        # 賣量3
        self.labelnBestAskQty3 = tk.Label(self, text = "")
        self.labelnBestAskQty3.grid(row=4, column=4)

        global labelnBestAskQty3
        labelnBestAskQty3 = self.labelnBestAskQty3
        
        # 賣量4
        self.labelnBestAskQty4 = tk.Label(self, text = "")
        self.labelnBestAskQty4.grid(row=5, column=4)

        global labelnBestAskQty4
        labelnBestAskQty4 = self.labelnBestAskQty4
        
        # 賣量5
        self.labelnBestAskQty5 = tk.Label(self, text = "")
        self.labelnBestAskQty5.grid(row=6, column=4)

        global labelnBestAskQty5
        labelnBestAskQty5 = self.labelnBestAskQty5

        tk.Label(self, text = "成交彙總(時間/成交價/成交量)").grid(row=7, column=1)
        # richTextBoxTickMessage
        self.richTextBoxTickMessage = tk.Listbox(self, height=5, width=20)
        self.richTextBoxTickMessage.grid(row = 8, column = 1)

        global richTextBoxTickMessage
        richTextBoxTickMessage = self.richTextBoxTickMessage

        #十檔
        tk.Label(self, text = "買量").grid(row=1, column=5)
        
        # 買量11
        self.labelnBestBidQty11 = tk.Label(self, text = "")
        self.labelnBestBidQty11.grid(row=2, column=5)

        global labelnBestBidQty11
        labelnBestBidQty11 = self.labelnBestBidQty11
        
        # 買量12
        self.labelnBestBidQty12 = tk.Label(self, text = "")
        self.labelnBestBidQty12.grid(row=3, column=5)

        global labelnBestBidQty12
        labelnBestBidQty12 = self.labelnBestBidQty12
        
        # 買量13
        self.labelnBestBidQty13 = tk.Label(self, text = "")
        self.labelnBestBidQty13.grid(row=4, column=5)

        global labelnBestBidQty13
        labelnBestBidQty13 = self.labelnBestBidQty13
        
        # 買量14
        self.labelnBestBidQty14 = tk.Label(self, text = "")
        self.labelnBestBidQty14.grid(row=5, column=5)

        global labelnBestBidQty14
        labelnBestBidQty14 = self.labelnBestBidQty14
        
        # 買量15
        self.labelnBestBidQty15 = tk.Label(self, text = "")
        self.labelnBestBidQty15.grid(row=6, column=5)

        global labelnBestBidQty15
        labelnBestBidQty15 = self.labelnBestBidQty15        


        tk.Label(self, text = "買價").grid(row=1, column=6)
        
        # 買價11
        self.labelnBestBid11 = tk.Label(self, text = "")
        self.labelnBestBid11.grid(row=2, column=6)

        global labelnBestBid11
        labelnBestBid11 = self.labelnBestBid11
        
        # 買價12
        self.labelnBestBid12 = tk.Label(self, text = "")
        self.labelnBestBid12.grid(row=3, column=6)

        global labelnBestBid12
        labelnBestBid12 = self.labelnBestBid12
        
        # 買價13
        self.labelnBestBid13 = tk.Label(self, text = "")
        self.labelnBestBid13.grid(row=4, column=6)

        global labelnBestBid13
        labelnBestBid13 = self.labelnBestBid13
        
        # 買價14
        self.labelnBestBid14 = tk.Label(self, text = "")
        self.labelnBestBid14.grid(row=5, column=6)

        global labelnBestBid14
        labelnBestBid14 = self.labelnBestBid14
        
        # 買價15
        self.labelnBestBid15 = tk.Label(self, text = "")
        self.labelnBestBid15.grid(row=6, column=6)

        global labelnBestBid15
        labelnBestBid15 = self.labelnBestBid15


        tk.Label(self, text = "賣價").grid(row=1, column=7)
        
        # 賣價11
        self.labelnBestAsk11 = tk.Label(self, text = "")
        self.labelnBestAsk11.grid(row=2, column=7)

        global labelnBestAsk11
        labelnBestAsk11 = self.labelnBestAsk11
        
        # 賣價12
        self.labelnBestAsk12 = tk.Label(self, text = "")
        self.labelnBestAsk12.grid(row=3, column=7)

        global labelnBestAsk12
        labelnBestAsk12 = self.labelnBestAsk12
        
        # 賣價13
        self.labelnBestAsk13 = tk.Label(self, text = "")
        self.labelnBestAsk13.grid(row=4, column=7)

        global labelnBestAsk13
        labelnBestAsk13 = self.labelnBestAsk13
        
        # 賣價14
        self.labelnBestAsk14 = tk.Label(self, text = "")
        self.labelnBestAsk14.grid(row=5, column=7)

        global labelnBestAsk14
        labelnBestAsk14 = self.labelnBestAsk14
        
        # 賣價15
        self.labelnBestAsk15 = tk.Label(self, text = "")
        self.labelnBestAsk15.grid(row=6, column=7)

        global labelnBestAsk15
        labelnBestAsk15 = self.labelnBestAsk15


        tk.Label(self, text = "賣量").grid(row=1, column=8)
        
        # 賣量11
        self.labelnBestAskQty11 = tk.Label(self, text = "")
        self.labelnBestAskQty11.grid(row=2, column=8)

        global labelnBestAskQty11
        labelnBestAskQty11 = self.labelnBestAskQty11
        
        # 賣量12
        self.labelnBestAskQty12 = tk.Label(self, text = "")
        self.labelnBestAskQty12.grid(row=3, column=8)

        global labelnBestAskQty12
        labelnBestAskQty12 = self.labelnBestAskQty12
        
        # 賣量13
        self.labelnBestAskQty13 = tk.Label(self, text = "")
        self.labelnBestAskQty13.grid(row=4, column=8)

        global labelnBestAskQty13
        labelnBestAskQty13 = self.labelnBestAskQty13
        
        # 賣量14
        self.labelnBestAskQty14 = tk.Label(self, text = "")
        self.labelnBestAskQty14.grid(row=5, column=8)

        global labelnBestAskQty14
        labelnBestAskQty14 = self.labelnBestAskQty14
        
        # 賣量15
        self.labelnBestAskQty15 = tk.Label(self, text = "")
        self.labelnBestAskQty15.grid(row=6, column=8)

        global labelnBestAskQty15
        labelnBestAskQty15 = self.labelnBestAskQty15

        #tk.Label(self, text = "買量").grid(row=1, column=1)
        
        # 買量16
        self.labelnBestBidQty16 = tk.Label(self, text = "")
        self.labelnBestBidQty16.grid(row=7, column=5)

        global labelnBestBidQty16
        labelnBestBidQty16 = self.labelnBestBidQty16
        
        # 買量17
        self.labelnBestBidQty17 = tk.Label(self, text = "")
        self.labelnBestBidQty17.grid(row=8, column=5)

        global labelnBestBidQty17
        labelnBestBidQty17 = self.labelnBestBidQty17
        
        # 買量18
        self.labelnBestBidQty18 = tk.Label(self, text = "")
        self.labelnBestBidQty18.grid(row=9, column=5)

        global labelnBestBidQty18
        labelnBestBidQty18 = self.labelnBestBidQty18
        
        # 買量19
        self.labelnBestBidQty19 = tk.Label(self, text = "")
        self.labelnBestBidQty19.grid(row=10, column=5)

        global labelnBestBidQty19
        labelnBestBidQty19 = self.labelnBestBidQty19
        
        # 買量20
        self.labelnBestBidQty20 = tk.Label(self, text = "")
        self.labelnBestBidQty20.grid(row=11, column=5)

        global labelnBestBidQty20
        labelnBestBidQty20 = self.labelnBestBidQty20        


        #tk.Label(self, text = "買價").grid(row=1, column=6)
        
        # 買價16
        self.labelnBestBid16 = tk.Label(self, text = "")
        self.labelnBestBid16.grid(row=7, column=6)

        global labelnBestBid16
        labelnBestBid16 = self.labelnBestBid16
        
        # 買價17
        self.labelnBestBid17 = tk.Label(self, text = "")
        self.labelnBestBid17.grid(row=8, column=6)

        global labelnBestBid17
        labelnBestBid17 = self.labelnBestBid17
        
        # 買價18
        self.labelnBestBid18 = tk.Label(self, text = "")
        self.labelnBestBid18.grid(row=9, column=6)

        global labelnBestBid18
        labelnBestBid18 = self.labelnBestBid18
        
        # 買價19
        self.labelnBestBid19 = tk.Label(self, text = "")
        self.labelnBestBid19.grid(row=10, column=6)

        global labelnBestBid19
        labelnBestBid19 = self.labelnBestBid19
        
        # 買價20
        self.labelnBestBid20 = tk.Label(self, text = "")
        self.labelnBestBid20.grid(row=11, column=6)

        global labelnBestBid20
        labelnBestBid20 = self.labelnBestBid20


        #tk.Label(self, text = "賣價").grid(row=1, column=7)
        
        # 賣價16
        self.labelnBestAsk16 = tk.Label(self, text = "")
        self.labelnBestAsk16.grid(row=7, column=7)

        global labelnBestAsk16
        labelnBestAsk16 = self.labelnBestAsk16
        
        # 賣價17
        self.labelnBestAsk17 = tk.Label(self, text = "")
        self.labelnBestAsk17.grid(row=8, column=7)

        global labelnBestAsk17
        labelnBestAsk17 = self.labelnBestAsk17
        
        # 賣價18
        self.labelnBestAsk18 = tk.Label(self, text = "")
        self.labelnBestAsk18.grid(row=9, column=7)

        global labelnBestAsk18
        labelnBestAsk18 = self.labelnBestAsk18
        
        # 賣價19
        self.labelnBestAsk19 = tk.Label(self, text = "")
        self.labelnBestAsk19.grid(row=10, column=7)

        global labelnBestAsk19
        labelnBestAsk19 = self.labelnBestAsk19
        
        # 賣價20
        self.labelnBestAsk20 = tk.Label(self, text = "")
        self.labelnBestAsk20.grid(row=11, column=7)

        global labelnBestAsk20
        labelnBestAsk20 = self.labelnBestAsk20


        #tk.Label(self, text = "賣量").grid(row=1, column=8)
        
        # 賣量16
        self.labelnBestAskQty16 = tk.Label(self, text = "")
        self.labelnBestAskQty16.grid(row=7, column=8)

        global labelnBestAskQty16
        labelnBestAskQty16 = self.labelnBestAskQty16
        
        # 賣量17
        self.labelnBestAskQty17 = tk.Label(self, text = "")
        self.labelnBestAskQty17.grid(row=8, column=8)

        global labelnBestAskQty17
        labelnBestAskQty17 = self.labelnBestAskQty17
        
        # 賣量18
        self.labelnBestAskQty18 = tk.Label(self, text = "")
        self.labelnBestAskQty18.grid(row=9, column=8)

        global labelnBestAskQty18
        labelnBestAskQty18 = self.labelnBestAskQty18
        
        # 賣量19
        self.labelnBestAskQty19 = tk.Label(self, text = "")
        self.labelnBestAskQty19.grid(row=10, column=8)

        global labelnBestAskQty19
        labelnBestAskQty19 = self.labelnBestAskQty19
        
        # 賣量20
        self.labelnBestAskQty20 = tk.Label(self, text = "")
        self.labelnBestAskQty20.grid(row=11, column=8)

        global labelnBestAskQty20
        labelnBestAskQty20 = self.labelnBestAskQty20


    def buttonSKOOQuoteLib_RequestTicks_Click(self):
        psPageNo = int(textBoxpsPageNo.get())
        # 訂閱與要求傳送成交明細以及五檔
        psPageNo, nCode= m_pSKOOQuote.SKOOQuoteLib_RequestTicks(psPageNo, textBoxTicks.get())

        msg = "【SKOOQuoteLib_RequestTicks】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
#==========================================
#定義彈出視窗
def popup_window_Connect():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Connect")

    # 建立 Frame 作為 ConnectForm，並添加到彈出窗口
    popup_ConnectForm = ConnectForm(popup)
    popup_ConnectForm.pack(fill=tk.BOTH, expand=True)
def popup_window_Product():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Product")

    # 建立 Frame 作為 ProductForm，並添加到彈出窗口
    popup_ProductForm = ProductForm(popup)
    popup_ProductForm.pack(fill=tk.BOTH, expand=True)
def popup_window_Request():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Request")

    # 建立 Frame 作為 RequestForm，並添加到彈出窗口
    popup_RequestForm = RequestForm(popup)
    popup_RequestForm.pack(fill=tk.BOTH, expand=True)
def popup_window_Ticks():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Ticks")

    # 建立 Frame 作為 TicksForm，並添加到彈出窗口
    popup_TicksForm = TicksForm(popup)
    popup_TicksForm.pack(fill=tk.BOTH, expand=True)
#開啟Tk視窗
if __name__ == '__main__':
    #建立主視窗
    root = tk.Tk()
    root.title("OOQuote")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)

    # 開啟Connect視窗的按鈕
    popup_button_Connect = tk.Button(root, text="連線", command=popup_window_Connect)
    popup_button_Connect.grid(row = 1, column= 0)
    
    # 開啟Product視窗的按鈕
    popup_button_Product = tk.Button(root, text="商品清單&個選資訊", command=popup_window_Product)
    popup_button_Product.grid(row = 2, column= 0)
        
    # 開啟Request視窗的按鈕
    popup_button_Request = tk.Button(root, text="即時報價", command=popup_window_Request)
    popup_button_Request.grid(row = 3, column= 0)
            
    # 開啟Ticks視窗的按鈕
    popup_button_Ticks = tk.Button(root, text="十檔&五檔&成交明細", command=popup_window_Ticks)
    popup_button_Ticks.grid(row = 4, column= 0)

    root.mainloop()
#==========================================
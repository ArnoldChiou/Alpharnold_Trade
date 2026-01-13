# API com元件初始化
import comtypes.client
comtypes.client.GetModule(r'C:\Trading\TradeAPI_MA_TX\units\SKCOM.dll')
import comtypes.gen.SKCOMLib as sk
import ctypes

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
######################################################################################################################################
# CenterLib 事件
class SKCenterLibEvent:
    # 同意書狀態通知
    def OnShowAgreement(self, bstrData):
        msg = "【OnShowAgreement】" + bstrData;
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
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

# QuoteLib事件
class SKQuoteLibEvent():
    def OnConnection(self, nKind, nCode):
        msg = "【OnConnection】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nKind) + "_" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnNotifyServerTime(self, sHour, sMinute, sSecond, nTotal):
        msg = "【OnNotifyServerTime】" + str(sHour) + ":" + str(sMinute) + ":" + str(sSecond) + "總秒數:" + str(nTotal)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')

    def OnNotifyMarketTot(self, sMarketNo, sPtr, nTime, nTotv, nTots, nTotc):
        if (sMarketNo == 0): #上市
            labelMarketTotPtr.config(text = str(sPtr))
            labelMarketTotTime.config(text = str(nTime))
            labelnTotv.config(text = str(nTotv / 100.00))
            labelnTots.config(text = str(nTots))
            labelnTotc.config(text = str(nTotc))
        else: #上櫃
            labelMarketTotPtr2.config(text = str(sPtr))
            labelMarketTotTime2.config(text = str(nTime))
            labelnTotv2.config(text = str(nTotv / 100.00))
            labelnTots2.config(text = str(nTots))
            labelnTotc2.config(text = str(nTotc))
    def OnNotifyMarketBuySell(self, sMarketNo, sPtr, nTime, nBc, nSc, nBs, nSs):
        if (sMarketNo == 0): #上市
            labelnBs.config(text = str(nBs))
            labelnSs.config(text = str(nSs))
            labelnBc.config(text = str(nBc))
            labelnSc.config(text = str(nSc))
        else: #上櫃
            labelnBs2.config(text = str(nBs))
            labelnSs2.config(text = str(nSs))
            labelnBc2.config(text = str(nBc))
            labelnSc2.config(text = str(nSc))
    def OnNotifyMarketHighLowNoWarrant(self, sMarketNo, sPtr, nTime, nUp, nDown, nHigh, nLow, nNoChange, nUpNoW, nDownNoW, nHighNoW, nLowNoW, nNoChangeNoW):
        if (sMarketNo == 0): #上市
            labelnUp.config(text = str(nUp))
            labelnDown.config(text = str(nDown))
            labelnHigh.config(text = str(nHigh))
            labelnLow.config(text = str(nLow))
            labelnNoChange.config(text = str(nNoChange))

            labelnUpNoW.config(text = str(nUpNoW))
            labelnDownNoW.config(text = str(nDownNoW))
            labelnHighNoW.config(text = str(nHighNoW))
            labelnLowNoW.config(text = str(nLowNoW))
            labelnNoChangeNoW.config(text = str(nNoChangeNoW))
        else: #上櫃
            labelnUp2.config(text = str(nUp))
            labelnDown2.config(text = str(nDown))
            labelnHigh2.config(text = str(nHigh))
            labelnLow2.config(text = str(nLow))
            labelnNoChange2.config(text = str(nNoChange))

            labelnUpNoW2.config(text = str(nUpNoW))
            labelnDownNoW2.config(text = str(nDownNoW))
            labelnHighNoW2.config(text = str(nHighNoW))
            labelnLowNoW2.config(text = str(nLowNoW))
            labelnNoChangeNoW2.config(text = str(nNoChangeNoW))
    def OnNotifyCommodityListWithTypeNo(self, sMarketNo, bstrCommodityData):
        msg = "【OnNotifyCommodityListWithTypeNo】" + str(sMarketNo) + "_" + bstrCommodityData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnNotifyQuoteLONG(self, sMarketNo, nIndex):
        pSKStock = sk.SKSTOCKLONG()
        pSKStock, nCode= m_pSKQuote.SKQuoteLib_GetStockByIndexLONG(sMarketNo, nIndex, pSKStock)

        if (pSKStock.nBid == m_pSKQuote.SKQuoteLib_GetMarketPriceTS()):
            nBidValue = "市價"
        else:
            nBidValue = pSKStock.nBid / 100.0

        if (pSKStock.nBid == m_pSKQuote.SKQuoteLib_GetMarketPriceTS()):
            nAskValue = "市價"
        else:
            nAskValue = pSKStock.nAsk / 100.0

        msg = ("【OnNotifyQuoteLONG】" + " 商品代碼" + str(pSKStock.bstrStockNo) + 
        " 名稱" + str(pSKStock.bstrStockName) +
        " 開盤價" + str(pSKStock.nOpen / 100.0) +
        " 成交價" + str(pSKStock.nClose / 100.0) +
        " 最高" + str(pSKStock.nHigh / 100.0) +
        " 最低" + str(pSKStock.nLow / 100.0) +
        " 漲停價" + str(pSKStock.nUp / 100.0) +
        " 跌停價" + str(pSKStock.nDown / 100.0) +
        " 買盤量(外盤)" + str(pSKStock.nTBc) +
        " 賣盤量(內盤)" + str(pSKStock.nTAc) +
        " 總量" + str(pSKStock.nTQty) +
        " 昨收(參考價)" + str(pSKStock.nRef / 100.0) +
        " 昨量" + str(pSKStock.nYQty) +
        " 買價" + str(nBidValue) +
        " 買量" + str(pSKStock.nBc) +
        " 賣價" + str(nAskValue) +
        " 賣量" + str(pSKStock.nAc) )
        
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
        
        strPriceInf = (str(pSKStock.nOpen / 100.0) + "," + 
                       str(pSKStock.nClose / 100.0) + "," + 
                       str(pSKStock.nHigh / 100.0) + "," + 
                       str(pSKStock.nLow / 100.0) + "," + 
                       str(pSKStock.nUp / 100.0) + "," +
                       str(pSKStock.nDown / 100.0) + ","  +
                       str(pSKStock.nTBc) + ","  +
                       str(pSKStock.nTAc) + ","  +
                       str(pSKStock.nTQty) + ","  +
                       str(pSKStock.nRef / 100.0) + ","  +
                       str(pSKStock.nYQty) + ","  +
                       str(nBidValue) + ","  +
                       str(pSKStock.nBc) + ","  +
                       str(nAskValue) + ","  +
                       str(pSKStock.nAc) )
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

    def OnNotifyOddLotSpreadDeal(self, sMarketNo, bstrStockNo, nDealPrice, sDigit):
        while sDigit != 0:
            sDigit -=1
            nDealPrice /= 10
        msg = "【OnNotifyOddLotSpreadDeal】" + " 市場別代號" + str(sMarketNo)+ " 商品代碼" + str(bstrStockNo)+ " 整零成交價差(負數則含-負號)" + str(nDealPrice)
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    
    def OnNotifyBest5LONG(self, sMarketNo, nStockidx, nBestBid1, nBestBidQty1, nBestBid2,  nBestBidQty2, nBestBid3, nBestBidQty3, nBestBid4, nBestBidQty4, nBestBid5, nBestBidQty5, nExtendBid, nExtendBidQty, nBestAsk1, nBestAskQty1, nBestAsk2, nBestAskQty2, nBestAsk3, nBestAskQty3, nBestAsk4, nBestAskQty4, nBestAsk5, nBestAskQty5, nExtendAsk, nExtendAskQty, nSimulate):
        if (nSimulate == 0):
            labelnSimulate = "一般揭示"
        elif (nSimulate == 1):
            labelnSimulate = "試算揭示"
        msg = ("【OnNotifyBest5LONG】" + " 揭示" + labelnSimulate + 
               " 買量一檔" + str(nBestBidQty1)+ 
               " 買價一檔" + str(nBestBid1 / 100.0)+ 
                " 賣價一檔" + str(nBestAsk1 / 100.0)+ 
               " 賣量一檔" + str(nBestAskQty1)+ 

                " 買量二檔" + str(nBestBidQty2)+ 
               " 買價二檔" + str(nBestBid2 / 100.0)+ 
                " 賣價二檔" + str(nBestAsk2 / 100.0)+ 
               " 賣量二檔" + str(nBestAskQty2)+ 

                " 買量三檔" + str(nBestBidQty3)+ 
               " 買價三檔" + str(nBestBid3 / 100.0)+ 
                " 賣價三檔" + str(nBestAsk3 / 100.0)+ 
               " 賣量三檔" + str(nBestAskQty3)+ 

                " 買量四檔" + str(nBestBidQty4)+ 
               " 買價四檔" + str(nBestBid4 / 100.0)+ 
                " 賣價四檔" + str(nBestAsk4 / 100.0)+ 
               " 賣量四檔" + str(nBestAskQty4)+ 

                " 買量五檔" + str(nBestBidQty5)+ 
               " 買價五檔" + str(nBestBid5 / 100.0)+ 
                " 賣價五檔" + str(nBestAsk5 / 100.0)+ 
               " 賣量五檔" + str(nBestAskQty5) )

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


    def OnNotifyTicksLONG(self, sMarketNo, nIndex, nPtr, nDate, nTimehms,  nTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
        msg = ("【OnNotifyTicksLONG】" + " 交易日期。(YYYYMMDD)" + str(nDate) + 
               " 時間1。(時：分：秒)" + str(nTimehms)+ 
               " 時間2。(毫秒微秒)" + str(nTimemillismicros)+ 
                " 買價" + str(nBid / 100.0)+ 
               " 賣價" + str(nAsk / 100.0)+ 

                " 成交價" + str(nClose / 100.0)+ 
               " 成交量" + str(nQty))

        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')

        hour = str(nTimehms)[:2]
        min = str(nTimehms)[2:4]
        sec = str(nTimehms)[4:6]

        richTextBoxTickMessage.insert('end', hour + ":" + min + ":" + sec + "     " + str(nClose / 100.0) + "     " + str(nQty) + "\n")
        richTextBoxTickMessage.see('end')

    def OnNotifyMACDLONG(self, sMarketNo, nStockidx, bstrMACD, bstrDIF, bstrOSC):
        pSKMACD = sk.SKMACD()
        pSKMACD.bstrStockNo = textBoxbstrStockNo.get()
        pSKMACD.bstrMACD = bstrMACD
        pSKMACD.bstrDIF = bstrDIF
        pSKMACD.bstrOSC = bstrOSC
        pSKMACD, nCode = m_pSKQuote.SKQuoteLib_GetMACDLONG(sMarketNo, nStockidx, pSKMACD)

        msg = ("【OnNotifyMACDLONG】" + "市場別代號:" + str(sMarketNo) + 
        "系統所編的索引代碼" + str(nStockidx) + 
        "MACD平滑異同平均線:" + str(pSKMACD.bstrMACD) + 
        "DIF:" + str(pSKMACD.bstrDIF) + 
        "OSC:" + str(pSKMACD.bstrOSC))
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnNotifyBoolTunelLONG(self, sMarketNo, nStockidx, bstrAVG, bstrUBT, bstrLBT):
        pBoolTunel = sk.SKBoolTunel()
        pBoolTunel.bstrStockNo = textBoxbstrStockNo.get()
        pBoolTunel.bstrAVG = bstrAVG
        pBoolTunel.bstrUBT = bstrUBT
        pBoolTunel.bstrLBT = bstrLBT
        pBoolTunel, nCode = m_pSKQuote.SKQuoteLib_GetBoolTunelLONG(sMarketNo, nStockidx, pBoolTunel)

        msg = ("【OnNotifyBoolTunelLONG】" + "市場別代號:" + str(sMarketNo) + 
        "系統所編的索引代碼" + str(nStockidx) + 
        "均線:" + str(pBoolTunel.bstrAVG) + 
        "通道上端:" + str(pBoolTunel.bstrUBT) + 
        "通道下端:" + str(pBoolTunel.bstrLBT))
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnNotifyKLineData(self, bstrStockNo, bstrData):
        msg = "【OnNotifyKLineData】" + bstrStockNo + "_" + bstrData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')

    def OnNotifyFutureTradeInfoLONG(self, bstrStockNo, sMarketNo, nStockidx, nBuyTotalCount, nSellTotalCount, nBuyTotalQty, nSellTotalQty, nBuyDealTotalCount, nSellDealTotalCount):

        msg = ("【OnNotifyFutureTradeInfoLONG】" + " 總委託買進筆數" + str(nBuyTotalCount)+ 
        " 總委託賣出筆數" + str(nSellTotalCount)+ 
        " 總委託買進口數" + str(nBuyTotalQty)+ 
        " 總委託賣出口數" + str(nSellTotalQty)+ 
        " 總成交買進筆數" + str(nBuyDealTotalCount) +
        " 總成交賣出筆數" + str(nSellDealTotalCount))
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
    def OnNotifyStrikePrices(self, bstrOptionData):
        msg = "【OnNotifyStrikePrices】" + bstrOptionData
        richTextBoxMessage.insert('end', msg + "\n")
        richTextBoxMessage.see('end')
SKQuoteEvent = SKQuoteLibEvent()
SKQuoteLibEventHandler = comtypes.client.GetEvents(m_pSKQuote, SKQuoteEvent)

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
        
        # buttonSKQuoteLib_RequestServerTime
        self.buttonSKQuoteLib_RequestServerTime = tk.Button(self)
        self.buttonSKQuoteLib_RequestServerTime["text"] = "報價主機現在時間"
        self.buttonSKQuoteLib_RequestServerTime["command"] = self.buttonSKQuoteLib_RequestServerTime_Click
        self.buttonSKQuoteLib_RequestServerTime.grid(row=0, column=1)

        # buttonSKQuoteLib_EnterMonitorLONG
        self.buttonSKQuoteLib_EnterMonitorLONG = tk.Button(self)
        self.buttonSKQuoteLib_EnterMonitorLONG["text"] = "連線報價主機"
        self.buttonSKQuoteLib_EnterMonitorLONG["command"] = self.buttonSKQuoteLib_EnterMonitorLONG_Click
        self.buttonSKQuoteLib_EnterMonitorLONG.grid(row=1, column=1)
                
        # buttonSKQuoteLib_LeaveMonitor
        self.buttonSKQuoteLib_LeaveMonitor = tk.Button(self)
        self.buttonSKQuoteLib_LeaveMonitor["text"] = "斷線報價主機(ALL)"
        self.buttonSKQuoteLib_LeaveMonitor["command"] = self.buttonSKQuoteLib_LeaveMonitor_Click
        self.buttonSKQuoteLib_LeaveMonitor.grid(row=2, column=1)
                
        # buttonSKQuoteLib_IsConnected
        self.buttonSKQuoteLib_IsConnected = tk.Button(self)
        self.buttonSKQuoteLib_IsConnected["text"] = "檢查連線狀態"
        self.buttonSKQuoteLib_IsConnected["command"] = self.buttonSKQuoteLib_IsConnected_Click
        self.buttonSKQuoteLib_IsConnected.grid(row=3, column=1)
                
        # buttonSKQuoteLib_GetQuoteStatus
        self.buttonSKQuoteLib_GetQuoteStatus = tk.Button(self)
        self.buttonSKQuoteLib_GetQuoteStatus["text"] = "連線數資訊/限制"
        self.buttonSKQuoteLib_GetQuoteStatus["command"] = self.buttonSKQuoteLib_GetQuoteStatus_Click
        self.buttonSKQuoteLib_GetQuoteStatus.grid(row=4, column=1)

    def buttonSKQuoteLib_RequestServerTime_Click(self):
        # 要求報價主機傳送目前時間。
        nCode= m_pSKQuote.SKQuoteLib_RequestServerTime()

        msg = "【SKQuoteLib_RequestServerTime】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKQuoteLib_EnterMonitorLONG_Click(self):
        # 與報價伺服器連線
        nCode= m_pSKQuote.SKQuoteLib_EnterMonitorLONG()

        msg = "【SKQuoteLib_EnterMonitorLONG】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    def buttonSKQuoteLib_LeaveMonitor_Click(self):
        # 中斷所有Solace伺服器連線
        nCode= m_pSKQuote.SKQuoteLib_LeaveMonitor()

        msg = "【SKQuoteLib_LeaveMonitor】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
                
    def buttonSKQuoteLib_IsConnected_Click(self):
        # 檢查目前報價的連線狀態
        nCode= m_pSKQuote.SKQuoteLib_IsConnected()

        if nCode == 0:
            msg = "斷線"
        elif nCode == 1:
            msg = "連線中"
        elif nCode == 2:
            msg = "下載中"
        else:
            msg = "出錯啦"

        msg = "【SKQuoteLib_IsConnected】" + msg
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKQuoteLib_GetQuoteStatus_Click(self):
        pnConnectionCount = 0
        pbIsOutLimit = False

        # 查詢報價連線狀態(是否超過報價連線限制,連線數資訊)
        pnConnectionCount, pbIsOutLimit, nCode= m_pSKQuote.SKQuoteLib_GetQuoteStatus(pnConnectionCount, pbIsOutLimit)

        msg = "【SKQuoteLib_GetQuoteStatus】"  + "連線數:" + str(pnConnectionCount) + "超過限制:" + str(pbIsOutLimit)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#MarketForm
class MarketForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):
        
        # buttonSKQuoteLib_GetMarketBuySellUpDown
        self.buttonSKQuoteLib_GetMarketBuySellUpDown = tk.Button(self)
        self.buttonSKQuoteLib_GetMarketBuySellUpDown["text"] = "取得大盤資訊 (左)上市 (右)上櫃"
        self.buttonSKQuoteLib_GetMarketBuySellUpDown["command"] = self.buttonSKQuoteLib_GetMarketBuySellUpDown_Click
        self.buttonSKQuoteLib_GetMarketBuySellUpDown.grid(row=0, column=1)

        # labelMarketTotPtr
        tk.Label(self, text = "目前第x筆資料").grid(row=1, column=1)
        # labelMarketTotPtr
        self.labelMarketTotPtr = tk.Label(self, text = "")
        self.labelMarketTotPtr.grid(row=1, column=2)

        global labelMarketTotPtr
        labelMarketTotPtr = self.labelMarketTotPtr
        
        # labelnTotv
        tk.Label(self, text = "成交值(億)").grid(row=2, column=1)
        # labelnTotv
        self.labelnTotv = tk.Label(self, text = "")
        self.labelnTotv.grid(row=2, column=2)

        global labelnTotv
        labelnTotv = self.labelnTotv
        
        # labelnTots
        tk.Label(self, text = "成交張數").grid(row=3, column=1)
        # labelnTots
        self.labelnTots = tk.Label(self, text = "")
        self.labelnTots.grid(row=3, column=2)

        global labelnTots
        labelnTots = self.labelnTots
        
        # labelnTotc
        tk.Label(self, text = "成交筆數").grid(row=4, column=1)
        # labelnTotc
        self.labelnTotc = tk.Label(self, text = "")
        self.labelnTotc.grid(row=4, column=2)

        global labelnTotc
        labelnTotc = self.labelnTotc
        
        # labelnUp
        tk.Label(self, text = "成交上漲家數").grid(row=5, column=1)
        # labelnUp
        self.labelnUp = tk.Label(self, text = "")
        self.labelnUp.grid(row=5, column=2)

        global labelnUp
        labelnUp = self.labelnUp
        
        # labelnDown
        tk.Label(self, text = "成交下跌家數").grid(row=6, column=1)
        # labelnDown
        self.labelnDown = tk.Label(self, text = "")
        self.labelnDown.grid(row=6, column=2)

        global labelnDown
        labelnDown = self.labelnDown
        
        # labelnHigh
        tk.Label(self, text = "成交漲停家數").grid(row=7, column=1)
        # labelnHigh
        self.labelnHigh = tk.Label(self, text = "")
        self.labelnHigh.grid(row=7, column=2)

        global labelnHigh
        labelnHigh = self.labelnHigh
        
        # labelnLow
        tk.Label(self, text = "成交跌停家數").grid(row=8, column=1)
        # labelnLow
        self.labelnLow = tk.Label(self, text = "")
        self.labelnLow.grid(row=8, column=2)

        global labelnLow
        labelnLow = self.labelnLow
        
        # labelnNoChange
        tk.Label(self, text = "平盤家數").grid(row=9, column=1)
        # labelnNoChange
        self.labelnNoChange = tk.Label(self, text = "")
        self.labelnNoChange.grid(row=9, column=2)

        global labelnNoChange
        labelnNoChange = self.labelnNoChange

        
        # labelMarketTotTime
        tk.Label(self, text = "大盤成交時間").grid(row=1, column=3)
        # labelMarketTotTime
        self.labelMarketTotTime = tk.Label(self, text = "")
        self.labelMarketTotTime.grid(row=1, column=4)

        global labelMarketTotTime
        labelMarketTotTime = self.labelMarketTotTime
        
        # labelnBs
        tk.Label(self, text = "成交買進張數").grid(row=2, column=3)
        # labelnBs
        self.labelnBs = tk.Label(self, text = "")
        self.labelnBs.grid(row=2, column=4)

        global labelnBs
        labelnBs = self.labelnBs
        
        # labelnSs
        tk.Label(self, text = "成交賣出張數").grid(row=3, column=3)
        # labelnSs
        self.labelnSs = tk.Label(self, text = "")
        self.labelnSs.grid(row=3, column=4)

        global labelnSs
        labelnSs = self.labelnSs
        
        # labelnBc
        tk.Label(self, text = "成交買進筆數").grid(row=4, column=3)
        # labelnBc
        self.labelnBc = tk.Label(self, text = "")
        self.labelnBc.grid(row=4, column=4)

        global labelnBc
        labelnBc = self.labelnBc
        
        # labelnSc
        tk.Label(self, text = "成交賣出筆數").grid(row=5, column=3)
        # labelnSc
        self.labelnSc = tk.Label(self, text = "")
        self.labelnSc.grid(row=5, column=4)

        global labelnSc
        labelnSc = self.labelnSc
        
        # labelnUpNoW
        tk.Label(self, text = "(不含權證)成交上漲家數").grid(row=6, column=3)
        # labelnUpNoW
        self.labelnUpNoW = tk.Label(self, text = "")
        self.labelnUpNoW.grid(row=6, column=4)

        global labelnUpNoW
        labelnUpNoW = self.labelnUpNoW
        
        # labelnDownNoW
        tk.Label(self, text = "(不含權證)成交下跌家數").grid(row=7, column=3)
        # labelnDownNoW
        self.labelnDownNoW = tk.Label(self, text = "")
        self.labelnDownNoW.grid(row=7, column=4)

        global labelnDownNoW
        labelnDownNoW = self.labelnDownNoW
        
        # labelnHighNoW
        tk.Label(self, text = "(不含權證)成交漲停家數").grid(row=8, column=3)
        # labelnHighNoW
        self.labelnHighNoW = tk.Label(self, text = "")
        self.labelnHighNoW.grid(row=8, column=4)

        global labelnHighNoW
        labelnHighNoW = self.labelnHighNoW
        
        # labelnLowNoW
        tk.Label(self, text = "(不含權證)成交跌停家數").grid(row=9, column=3)
        # labelnLowNoW
        self.labelnLowNoW = tk.Label(self, text = "")
        self.labelnLowNoW.grid(row=9, column=4)

        global labelnLowNoW
        labelnLowNoW = self.labelnLowNoW
                
        # labelnNoChangeNoW
        tk.Label(self, text = "(不含權證)平盤家數").grid(row=10, column=3)
        # labelnNoChangeNoW
        self.labelnNoChangeNoW = tk.Label(self, text = "")
        self.labelnNoChangeNoW.grid(row=10, column=4)

        global labelnNoChangeNoW
        labelnNoChangeNoW = self.labelnNoChangeNoW

        












        
        # labelMarketTotPtr2
        tk.Label(self, text = "目前第x筆資料").grid(row=1, column=5)
        # labelMarketTotPtr2
        self.labelMarketTotPtr2 = tk.Label(self, text = "")
        self.labelMarketTotPtr2.grid(row=1, column=6)

        global labelMarketTotPtr2
        labelMarketTotPtr2 = self.labelMarketTotPtr2
        
        # labelnTotv2
        tk.Label(self, text = "成交值(億)").grid(row=2, column=5)
        # labelnTotv2
        self.labelnTotv2 = tk.Label(self, text = "")
        self.labelnTotv2.grid(row=2, column=6)

        global labelnTotv2
        labelnTotv2 = self.labelnTotv2
        
        # labelnTots2
        tk.Label(self, text = "成交張數").grid(row=3, column=5)
        # labelnTots2
        self.labelnTots2 = tk.Label(self, text = "")
        self.labelnTots2.grid(row=3, column=6)

        global labelnTots2
        labelnTots2 = self.labelnTots2
        
        # labelnTotc2
        tk.Label(self, text = "成交筆數").grid(row=4, column=5)
        # labelnTotc2
        self.labelnTotc2 = tk.Label(self, text = "")
        self.labelnTotc2.grid(row=4, column=6)

        global labelnTotc2
        labelnTotc2 = self.labelnTotc2
        
        # labelnUp2
        tk.Label(self, text = "成交上漲家數").grid(row=5, column=5)
        # labelnUp2
        self.labelnUp2 = tk.Label(self, text = "")
        self.labelnUp2.grid(row=5, column=6)

        global labelnUp2
        labelnUp2 = self.labelnUp2
        
        # labelnDown2
        tk.Label(self, text = "成交下跌家數").grid(row=6, column=5)
        # labelnDown2
        self.labelnDown2 = tk.Label(self, text = "")
        self.labelnDown2.grid(row=6, column=6)

        global labelnDown2
        labelnDown2 = self.labelnDown2
        
        # labelnHigh2
        tk.Label(self, text = "成交漲停家數").grid(row=7, column=5)
        # labelnHigh2
        self.labelnHigh2 = tk.Label(self, text = "")
        self.labelnHigh2.grid(row=7, column=6)

        global labelnHigh2
        labelnHigh2 = self.labelnHigh2
        
        # labelnLow2
        tk.Label(self, text = "成交跌停家數").grid(row=8, column=5)
        # labelnLow2
        self.labelnLow2 = tk.Label(self, text = "")
        self.labelnLow2.grid(row=8, column=6)

        global labelnLow2
        labelnLow2 = self.labelnLow2
        
        # labelnNoChange2
        tk.Label(self, text = "平盤家數").grid(row=9, column=5)
        # labelnNoChange2
        self.labelnNoChange2 = tk.Label(self, text = "")
        self.labelnNoChange2.grid(row=9, column=6)

        global labelnNoChange2
        labelnNoChange2 = self.labelnNoChange2

        
        # labelMarketTotTime2
        tk.Label(self, text = "大盤成交時間").grid(row=1, column=7)
        # labelMarketTotTime2
        self.labelMarketTotTime2 = tk.Label(self, text = "")
        self.labelMarketTotTime2.grid(row=1, column=8)

        global labelMarketTotTime2
        labelMarketTotTime2 = self.labelMarketTotTime2
        
        # labelnBs2
        tk.Label(self, text = "成交買進張數").grid(row=2, column=7)
        # labelnBs2
        self.labelnBs2 = tk.Label(self, text = "")
        self.labelnBs2.grid(row=2, column=8)

        global labelnBs2
        labelnBs2 = self.labelnBs2
        
        # labelnSs2
        tk.Label(self, text = "成交賣出張數").grid(row=3, column=7)
        # labelnSs2
        self.labelnSs2 = tk.Label(self, text = "")
        self.labelnSs2.grid(row=3, column=8)

        global labelnSs2
        labelnSs2 = self.labelnSs2
        
        # labelnBc2
        tk.Label(self, text = "成交買進筆數").grid(row=4, column=7)
        # labelnBc2
        self.labelnBc2 = tk.Label(self, text = "")
        self.labelnBc2.grid(row=4, column=8)

        global labelnBc2
        labelnBc2 = self.labelnBc2
        
        # labelnSc2
        tk.Label(self, text = "成交賣出筆數").grid(row=5, column=7)
        # labelnSc2
        self.labelnSc2 = tk.Label(self, text = "")
        self.labelnSc2.grid(row=5, column=8)

        global labelnSc2
        labelnSc2 = self.labelnSc2
        
        # labelnUpNoW2
        tk.Label(self, text = "(不含權證)成交上漲家數").grid(row=6, column=7)
        # labelnUpNoW2
        self.labelnUpNoW2 = tk.Label(self, text = "")
        self.labelnUpNoW2.grid(row=6, column=8)

        global labelnUpNoW2
        labelnUpNoW2 = self.labelnUpNoW2
        
        # labelnDownNoW2
        tk.Label(self, text = "(不含權證)成交下跌家數").grid(row=7, column=7)
        # labelnDownNoW2
        self.labelnDownNoW2 = tk.Label(self, text = "")
        self.labelnDownNoW2.grid(row=7, column=8)

        global labelnDownNoW2
        labelnDownNoW2 = self.labelnDownNoW2
        
        # labelnHighNoW2
        tk.Label(self, text = "(不含權證)成交漲停家數").grid(row=8, column=7)
        # labelnHighNoW2
        self.labelnHighNoW2 = tk.Label(self, text = "")
        self.labelnHighNoW2.grid(row=8, column=8)

        global labelnHighNoW2
        labelnHighNoW2 = self.labelnHighNoW2
        
        # labelnLowNoW2
        tk.Label(self, text = "(不含權證)成交跌停家數").grid(row=9, column=7)
        # labelnLowNoW2
        self.labelnLowNoW2 = tk.Label(self, text = "")
        self.labelnLowNoW2.grid(row=9, column=8)

        global labelnLowNoW2
        labelnLowNoW2 = self.labelnLowNoW2
                
        # labelnNoChangeNoW2
        tk.Label(self, text = "(不含權證)平盤家數").grid(row=10, column=7)
        # labelnNoChangeNoW2
        self.labelnNoChangeNoW2 = tk.Label(self, text = "")
        self.labelnNoChangeNoW2.grid(row=10, column=8)

        global labelnNoChangeNoW2
        labelnNoChangeNoW2 = self.labelnNoChangeNoW2
       
    def buttonSKQuoteLib_GetMarketBuySellUpDown_Click(self):
        # 要求傳送上市與上櫃大盤資訊(成交數,買賣數,漲跌家數)
        nCode= m_pSKQuote.SKQuoteLib_GetMarketBuySellUpDown()

        msg = "【SKQuoteLib_GetMarketBuySellUpDown】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
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
        
        # comboBoxSKQuoteLib_RequestStockList
        tk.Label(self, text = "請選擇市場別").grid(row=1, column=1)
            #輸入框
        self.comboBoxSKQuoteLib_RequestStockList = ttk.Combobox(self, state='readonly')
        self.comboBoxSKQuoteLib_RequestStockList['values'] = Config.comboBoxSKQuoteLib_RequestStockList
        self.comboBoxSKQuoteLib_RequestStockList.grid(row=1, column=2)

        global comboBoxSKQuoteLib_RequestStockList
        comboBoxSKQuoteLib_RequestStockList = self.comboBoxSKQuoteLib_RequestStockList   

        # buttonSKQuoteLib_RequestStockList
        self.buttonSKQuoteLib_RequestStockList = tk.Button(self)
        self.buttonSKQuoteLib_RequestStockList["text"] = "商品清單送出"
        self.buttonSKQuoteLib_RequestStockList["command"] = self.buttonSKQuoteLib_RequestStockList_Click
        self.buttonSKQuoteLib_RequestStockList.grid(row=1, column=3)



        # textBoxSKQuoteLib_GetStockByNoLONG
        tk.Label(self, text = "商品代碼").grid(row=2, column=1)
            #輸入框
        self.textBoxSKQuoteLib_GetStockByNoLONG = tk.Entry(self)
        self.textBoxSKQuoteLib_GetStockByNoLONG.grid(row=2, column=2)

        global textBoxSKQuoteLib_GetStockByNoLONG
        textBoxSKQuoteLib_GetStockByNoLONG = self.textBoxSKQuoteLib_GetStockByNoLONG
                        
        # buttonSKQuoteLib_GetStockByNoLONG
        self.buttonSKQuoteLib_GetStockByNoLONG = tk.Button(self)
        self.buttonSKQuoteLib_GetStockByNoLONG["text"] = "個股資訊"
        self.buttonSKQuoteLib_GetStockByNoLONG["command"] = self.buttonSKQuoteLib_GetStockByNoLONG_Click
        self.buttonSKQuoteLib_GetStockByNoLONG.grid(row=2, column=3)

    def buttonSKQuoteLib_RequestStockList_Click(self):

        selectValue = comboBoxSKQuoteLib_RequestStockList.get()
        if (selectValue == "上市"):
            sMarketNo = 0
        elif (selectValue == "上櫃"):
            sMarketNo = 1
        elif (selectValue == "期貨"):
            sMarketNo = 2
        elif (selectValue == "選擇權"):
            sMarketNo = 3
        elif (selectValue == "興櫃"):
            sMarketNo = 4
        elif (selectValue == "盤中零股-上市"):
            sMarketNo = 5
        elif (selectValue == "盤中零股-上櫃"):
            sMarketNo = 6
        elif (selectValue == "客製化期貨"):
            sMarketNo = 9
        elif (selectValue == "客製化選擇權"):
            sMarketNo = 10

        # 根據市場別編號，取得國內各市場代碼所包含的商品基本資料相關資訊
        nCode= m_pSKQuote.SKQuoteLib_RequestStockList(sMarketNo)

        msg = "【SKQuoteLib_RequestStockList】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    def buttonSKQuoteLib_GetStockByNoLONG_Click(self):
        
        pSKStock = sk.SKSTOCKLONG()

        # (LONG index)根據商品代號，取回商品報價的相關資訊
        pSKStock, nCode= m_pSKQuote.SKQuoteLib_GetStockByNoLONG(textBoxSKQuoteLib_GetStockByNoLONG.get(), pSKStock)

        msg = "【SKQuoteLib_GetStockByNoLONG】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

        msg = ("類股別" + str(pSKStock.sTypeNo) + 
        "市埸代碼" + str(pSKStock.bstrMarketNo) + 
        "商品代碼" + str(pSKStock.bstrStockNo) + 
        "商品名稱" + str(pSKStock.bstrStockName) + 
        "最高價" + str(pSKStock.nHigh / 100.0) + 
        "開盤價" + str(pSKStock.nOpen / 100.0) + 
        "最低價" + str(pSKStock.nLow / 100.0) + 
        "成交價" + str(pSKStock.nClose / 100.0) + 
        "單量" + str(pSKStock.nTickQty) + 
        "昨收、參考價" + str(pSKStock.nRef / 100.0) + 
        "買價" + str(pSKStock.nBid / 100.0) + 
        "買量" + str(pSKStock.nBc) + 
        "賣價" + str(pSKStock.nAsk / 100.0) + 
        "賣量" +  str(pSKStock.nAc) + 
        "買盤量(即外盤量)" +  str(pSKStock.nTBc) + 
        "賣盤量(即內盤量)" +  str(pSKStock.nTAc) + 
        "總量" +  str(pSKStock.nTQty) + 
        "昨量" + str(pSKStock.nYQty) + 
        "漲停價" +  str(pSKStock.nUp / 100.0) + 
        "跌停價" +  str(pSKStock.nDown / 100.0) + 
        "揭示 0:一般 1:試算(試撮)" +  str(pSKStock.nSimulate) + 
        "[限證券整股商品]可否當沖 0:一般 1:可先買後賣現股當沖2:可先買後賣和先賣後買現股當沖" + str(pSKStock.nDayTrade) + 
        "交易日(YYYYMMDD)" +  str(pSKStock.nTradingDay) + 
        "[證券] 整股、盤中零股揭示註記   0:現股 ; 1:盤中零股" +  str(pSKStock.nTradingLotFlag))
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
        
        # textBoxStockNos
        tk.Label(self, text = "(不含盤中零股)").grid(row=0, column=5)

        # buttonSKQuoteLib_CancelRequestStocks
        self.buttonSKQuoteLib_CancelRequestStocks = tk.Button(self)
        self.buttonSKQuoteLib_CancelRequestStocks["text"] = "取消訂閱"
        self.buttonSKQuoteLib_CancelRequestStocks["command"] = self.buttonSKQuoteLib_CancelRequestStocks_Click
        self.buttonSKQuoteLib_CancelRequestStocks.grid(row=0, column=6)

        # buttonSKQuoteLib_RequestStocks
        self.buttonSKQuoteLib_RequestStocks = tk.Button(self)
        self.buttonSKQuoteLib_RequestStocks["text"] = "訂閱"
        self.buttonSKQuoteLib_RequestStocks["command"] = self.buttonSKQuoteLib_RequestStocks_Click
        self.buttonSKQuoteLib_RequestStocks.grid(row=0, column=7)

                
        # comboBoxSKQuoteLib_RequestStocksWithMarketNo
        tk.Label(self, text = "請選擇市場別").grid(row=0, column=8)
            #輸入框
        self.comboBoxSKQuoteLib_RequestStocksWithMarketNo = ttk.Combobox(self, state='readonly')
        self.comboBoxSKQuoteLib_RequestStocksWithMarketNo['values'] = Config.comboBoxSKQuoteLib_RequestStocksWithMarketNo
        self.comboBoxSKQuoteLib_RequestStocksWithMarketNo.grid(row=0, column=9)

        global comboBoxSKQuoteLib_RequestStocksWithMarketNo
        comboBoxSKQuoteLib_RequestStocksWithMarketNo = self.comboBoxSKQuoteLib_RequestStocksWithMarketNo
        
        # buttonSKQuoteLib_RequestStocksWithMarketNo
        self.buttonSKQuoteLib_RequestStocksWithMarketNo = tk.Button(self)
        self.buttonSKQuoteLib_RequestStocksWithMarketNo["text"] = "盤中零股訂閱"
        self.buttonSKQuoteLib_RequestStocksWithMarketNo["command"] = self.buttonSKQuoteLib_RequestStocksWithMarketNo_Click
        self.buttonSKQuoteLib_RequestStocksWithMarketNo.grid(row=0, column=10)

        # treeviewStocks
        self.treeviewStocks = ttk.Treeview(self, columns=("名稱", "價格資訊(開盤價,成交價,最高,最低,漲停價,跌停價,買盤量(外盤),賣盤量(內盤),總量,昨收(參考價),昨量,買價,賣價)"))
        self.treeviewStocks.heading("#0", text="代碼")
        self.treeviewStocks.heading("#1", text="名稱")
        self.treeviewStocks.heading("#2", text="價格資訊(開盤價,成交價,最高,最低,漲停價,跌停價,買盤量(外盤),賣盤量(內盤),總量,昨收(參考價),昨量,買價,賣價)")
        self.treeviewStocks.grid(row=2, column=1, columnspan=100, sticky="nsew")

        global treeviewStocks
        treeviewStocks = self.treeviewStocks

        # Remove button
        self.btn_remove = tk.Button(self, text="清除資料", command=self.remove)
        self.btn_remove.grid(row=3, column=1)

    def remove(self):
        # 删除所有项
        self.treeviewStocks.delete(*self.treeviewStocks.get_children())


    def buttonSKQuoteLib_CancelRequestStocks_Click(self):
    
        # 取消訂閱SKQuoteLib_RequestStocks的報價通知，並停止更新商品報價
        nCode= m_pSKQuote.SKQuoteLib_CancelRequestStocks(textBoxStockNos.get())

        msg = "【SKQuoteLib_CancelRequestStocks】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    def buttonSKQuoteLib_RequestStocks_Click(self):
        psPageNo = int(textBoxpsPageNo2.get())
        # 訂閱指定商品即時報價(註冊)
        psPageNo, nCode= m_pSKQuote.SKQuoteLib_RequestStocks(psPageNo, textBoxStockNos.get())

        msg = "【SKQuoteLib_RequestStocks】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
                
    def buttonSKQuoteLib_RequestStocksWithMarketNo_Click(self):
        psPageNo = int(textBoxpsPageNo2.get())
        selectedValue = comboBoxSKQuoteLib_RequestStocksWithMarketNo.get()
        if (selectedValue == "盤中零股-上市(5)"):
            sMarketNo = 5
        elif (selectedValue == "盤中零股-上櫃(6)"):
            sMarketNo = 6
        elif (selectedValue == "客製化期貨-9"):
            sMarketNo = 9
        elif (selectedValue == "客製化選擇權-10"):
            sMarketNo = 10
        # 訂閱指定市場別及指定商品即時報價
        # 要求伺服器針對sMarketNo市場別、 bstrStockNos 內的商品代號訂閱商品報價通知動作
        psPageNo, nCode= m_pSKQuote.SKQuoteLib_RequestStocksWithMarketNo(psPageNo, sMarketNo, textBoxStockNos.get())

        msg = "【SKQuoteLib_RequestStocksWithMarketNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
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
                        
        # buttonSKQuoteLib_CancelRequestTicks
        self.buttonSKQuoteLib_CancelRequestTicks = tk.Button(self)
        self.buttonSKQuoteLib_CancelRequestTicks["text"] = "取消訂閱"
        self.buttonSKQuoteLib_CancelRequestTicks["command"] = self.buttonSKQuoteLib_CancelRequestTicks_Click
        self.buttonSKQuoteLib_CancelRequestTicks.grid(row=0, column=5)
                                
        # buttonSKQuoteLib_RequestTicks
        self.buttonSKQuoteLib_RequestTicks = tk.Button(self)
        self.buttonSKQuoteLib_RequestTicks["text"] = "訂閱"
        self.buttonSKQuoteLib_RequestTicks["command"] = self.buttonSKQuoteLib_RequestTicks_Click
        self.buttonSKQuoteLib_RequestTicks.grid(row=0, column=6)
                
        # comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo
        tk.Label(self, text = "請選擇市場別").grid(row=0, column=7)
            #輸入框
        self.comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo = ttk.Combobox(self, state='readonly')
        self.comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo['values'] = Config.comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo
        self.comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo.grid(row=0, column=8)

        global comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo
        comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo = self.comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo
                                        
        # buttonSKQuoteLib_RequestTicksWithMarketNo
        self.buttonSKQuoteLib_RequestTicksWithMarketNo = tk.Button(self)
        self.buttonSKQuoteLib_RequestTicksWithMarketNo["text"] = "盤中零股訂閱"
        self.buttonSKQuoteLib_RequestTicksWithMarketNo["command"] = self.buttonSKQuoteLib_RequestTicksWithMarketNo_Click
        self.buttonSKQuoteLib_RequestTicksWithMarketNo.grid(row=0, column=9)



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

    def buttonSKQuoteLib_CancelRequestTicks_Click(self):
        # 取消訂閱RequestTicks的成交明細及五檔
        nCode= m_pSKQuote.SKQuoteLib_CancelRequestTicks(textBoxTicks.get())

        msg = "【SKQuoteLib_CancelRequestTicks】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')

    def buttonSKQuoteLib_RequestTicks_Click(self):
        psPageNo = int(textBoxpsPageNo.get())
        # 此功能不支援盤中零股。訂閱要求傳送成交明細以及五檔
        psPageNo, nCode= m_pSKQuote.SKQuoteLib_RequestTicks(psPageNo, textBoxTicks.get())

        msg = "【SKQuoteLib_RequestTicks】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    def buttonSKQuoteLib_RequestTicksWithMarketNo_Click(self):
        psPageNo = int(textBoxpsPageNo.get())
        selectedValue = comboBoxSKQuoteLib_RequestTicksWithMarketNosMarketNo.get()
        if (selectedValue == "盤中零股-上市(5)"):
            sMarketNo = 5
        elif (selectedValue == "盤中零股-上櫃(6)"):
            sMarketNo = 6
        elif (selectedValue == "客製化期貨-9"):
            sMarketNo = 9
        elif (selectedValue == "客製化選擇權-10"):
            sMarketNo = 10
        # 適用盤中零股，訂閱要求傳送成交明細以及五檔
        psPageNo, nCode= m_pSKQuote.SKQuoteLib_RequestTicksWithMarketNo(psPageNo, sMarketNo, textBoxTicks.get())

        msg = "【SKQuoteLib_RequestTicksWithMarketNo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#KLineForm
class KLineForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # textBoxSKQuoteLib_RequestMACDpsPageNo
        tk.Label(self, text = "Page").grid(row=0, column=1)
            #輸入框
        self.textBoxSKQuoteLib_RequestMACDpsPageNo = tk.Entry(self)
        self.textBoxSKQuoteLib_RequestMACDpsPageNo.grid(row=0, column=2)

        global textBoxSKQuoteLib_RequestMACDpsPageNo
        textBoxSKQuoteLib_RequestMACDpsPageNo = self.textBoxSKQuoteLib_RequestMACDpsPageNo
        
        # textBoxbstrStockNo
        tk.Label(self, text = "商品代碼").grid(row=0, column=3)
            #輸入框
        self.textBoxbstrStockNo = tk.Entry(self)
        self.textBoxbstrStockNo.grid(row=0, column=4)

        global textBoxbstrStockNo
        textBoxbstrStockNo = self.textBoxbstrStockNo
                        
        # buttonSKQuoteLib_RequestMACD
        self.buttonSKQuoteLib_RequestMACD = tk.Button(self)
        self.buttonSKQuoteLib_RequestMACD["text"] = "MACD"
        self.buttonSKQuoteLib_RequestMACD["command"] = self.buttonSKQuoteLib_RequestMACD_Click
        self.buttonSKQuoteLib_RequestMACD.grid(row=1, column=1)
                        
        # buttonSKQuoteLib_RequestBoolTunel
        self.buttonSKQuoteLib_RequestBoolTunel = tk.Button(self)
        self.buttonSKQuoteLib_RequestBoolTunel["text"] = "BoolTunel"
        self.buttonSKQuoteLib_RequestBoolTunel["command"] = self.buttonSKQuoteLib_RequestBoolTunel_Click
        self.buttonSKQuoteLib_RequestBoolTunel.grid(row=2, column=1)
                
        # comboBoxsKLineType
        tk.Label(self, text = "K線種類").grid(row=3, column=1)
            #輸入框
        self.comboBoxsKLineType = ttk.Combobox(self, state='readonly')
        self.comboBoxsKLineType['values'] = Config.comboBoxsKLineType
        self.comboBoxsKLineType.grid(row=3, column=2)

        global comboBoxsKLineType
        comboBoxsKLineType = self.comboBoxsKLineType
                        
        # comboBoxsOutType
        tk.Label(self, text = "輸出格式").grid(row=3, column=3)
            #輸入框
        self.comboBoxsOutType = ttk.Combobox(self, state='readonly')
        self.comboBoxsOutType['values'] = Config.comboBoxsOutType
        self.comboBoxsOutType.grid(row=3, column=4)

        global comboBoxsOutType
        comboBoxsOutType = self.comboBoxsOutType
                        
        # comboBoxsTradeSession
        tk.Label(self, text = "全盤/AM盤").grid(row=3, column=5)
            #輸入框
        self.comboBoxsTradeSession = ttk.Combobox(self, state='readonly')
        self.comboBoxsTradeSession['values'] = Config.comboBoxsTradeSession
        self.comboBoxsTradeSession.grid(row=3, column=6)

        global comboBoxsTradeSession
        comboBoxsTradeSession = self.comboBoxsTradeSession

        # textBoxbstrStartDate
        tk.Label(self, text = "起始日期").grid(row=3, column=7)
            #輸入框
        self.textBoxbstrStartDate = tk.Entry(self)
        self.textBoxbstrStartDate.grid(row=3, column=8)

        global textBoxbstrStartDate
        textBoxbstrStartDate = self.textBoxbstrStartDate
                       
        # textBoxbstrEndDate
        tk.Label(self, text = "結束日期").grid(row=3, column=9)
            #輸入框
        self.textBoxbstrEndDate = tk.Entry(self)
        self.textBoxbstrEndDate.grid(row=3, column=10)

        global textBoxbstrEndDate
        textBoxbstrEndDate = self.textBoxbstrEndDate
                       
        # textBoxsMinuteNumber
        tk.Label(self, text = "幾分K(分線)").grid(row=3, column=11)
            #輸入框
        self.textBoxsMinuteNumber = tk.Entry(self)
        self.textBoxsMinuteNumber.grid(row=3, column=12)

        global textBoxsMinuteNumber
        textBoxsMinuteNumber = self.textBoxsMinuteNumber
                        
        # buttonSKQuoteLib_RequestKLineAMByDate
        self.buttonSKQuoteLib_RequestKLineAMByDate = tk.Button(self)
        self.buttonSKQuoteLib_RequestKLineAMByDate["text"] = "KLine"
        self.buttonSKQuoteLib_RequestKLineAMByDate["command"] = self.buttonSKQuoteLib_RequestKLineAMByDate_Click
        self.buttonSKQuoteLib_RequestKLineAMByDate.grid(row=3, column=13)

    def buttonSKQuoteLib_RequestMACD_Click(self):
        psPageNo = int(textBoxSKQuoteLib_RequestMACDpsPageNo.get())
        # 要求傳送商品技術指標MACD。(平滑異同平均線)
        psPageNo, nCode= m_pSKQuote.SKQuoteLib_RequestMACD(psPageNo, textBoxbstrStockNo.get())

        msg = "【SKQuoteLib_RequestMACD】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    def buttonSKQuoteLib_RequestBoolTunel_Click(self):
        psPageNo = int(textBoxSKQuoteLib_RequestMACDpsPageNo.get())
        # 要求傳送商品布林通道BoolTunel
        psPageNo, nCode= m_pSKQuote.SKQuoteLib_RequestBoolTunel(psPageNo, textBoxbstrStockNo.get())

        msg = "【SKQuoteLib_RequestBoolTunel】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
    
    def buttonSKQuoteLib_RequestKLineAMByDate_Click(self):

        if (comboBoxsKLineType.get() == "分線"):
            sKLineType = 0
        elif (comboBoxsKLineType.get() == "日線"):
            sKLineType = 4
        elif (comboBoxsKLineType.get() == "週線"):
            sKLineType = 5
        elif (comboBoxsKLineType.get() == "月線"):
            sKLineType = 6

        if (comboBoxsOutType.get() == "舊版"):
            sOutType = 0
        elif (comboBoxsOutType.get() == "新版"):
            sOutType = 1
            
        if (comboBoxsTradeSession.get() == "全盤"):
            sTradeSession = 0
        elif (comboBoxsTradeSession.get() == "AM盤"):
            sTradeSession = 1

        # （僅提供歷史資料）向報價伺服器提出，取得單一商品技術分析資訊需求，可選AM盤或全盤，可指定日期區間，分K時可指定幾分K
        nCode= m_pSKQuote.SKQuoteLib_RequestKLineAMByDate(textBoxbstrStockNo.get(), sKLineType, sOutType, sTradeSession, textBoxbstrStartDate.get(), textBoxbstrEndDate.get(), int(textBoxsMinuteNumber.get()))

        msg = "【SKQuoteLib_RequestKLineAMByDate】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#DeltaForm
class DeltaForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # textBoxS
        tk.Label(self, text = "指數").grid(row=0, column=1)
            #輸入框
        self.textBoxS = tk.Entry(self)
        self.textBoxS.grid(row=0, column=2)

        global textBoxS
        textBoxS = self.textBoxS
        
        # textBoxK
        tk.Label(self, text = "履約價").grid(row=0, column=3)
            #輸入框
        self.textBoxK = tk.Entry(self)
        self.textBoxK.grid(row=0, column=4)

        global textBoxK
        textBoxK = self.textBoxK
        
        # textBoxR
        tk.Label(self, text = "無風險利率").grid(row=1, column=1)
            #輸入框
        self.textBoxR = tk.Entry(self)
        self.textBoxR.grid(row=1, column=2)

        global textBoxR
        textBoxR = self.textBoxR
        
        # textBoxT
        tk.Label(self, text = "剩餘天數").grid(row=1, column=3)
            #輸入框
        self.textBoxT = tk.Entry(self)
        self.textBoxT.grid(row=1, column=4)

        global textBoxT
        textBoxT = self.textBoxT
        
        # textBoxsigma
        tk.Label(self, text = "sigma").grid(row=2, column=1)
            #輸入框
        self.textBoxsigma = tk.Entry(self)
        self.textBoxsigma.grid(row=2, column=2)

        global textBoxsigma
        textBoxsigma = self.textBoxsigma
            
        # comboBoxnCallPut
        tk.Label(self, text = "買賣權別").grid(row=2, column=3)
            #輸入框
        self.comboBoxnCallPut = ttk.Combobox(self, state='readonly')
        self.comboBoxnCallPut['values'] = Config.comboBoxnCallPut
        self.comboBoxnCallPut.grid(row=2, column=4)

        global comboBoxnCallPut
        comboBoxnCallPut = self.comboBoxnCallPut

        # buttonSKQuoteLib_Gamma
        self.buttonSKQuoteLib_Gamma = tk.Button(self)
        self.buttonSKQuoteLib_Gamma["text"] = "計算"
        self.buttonSKQuoteLib_Gamma["command"] = self.buttonSKQuoteLib_Gamma_Click
        self.buttonSKQuoteLib_Gamma.grid(row=3, column=1)

        # labelDelta
        tk.Label(self, text = "Delta:").grid(row=0, column=5)
        # labelDelta
        self.labelDelta = tk.Label(self, text = "")
        self.labelDelta.grid(row=0, column=6)

        global labelDelta
        labelDelta = self.labelDelta

        # labelGamma
        tk.Label(self, text = "Gamma:").grid(row=1, column=5)
        # labelGamma
        self.labelGamma = tk.Label(self, text = "")
        self.labelGamma.grid(row=1, column=6)

        global labelGamma
        labelGamma = self.labelGamma
        
        # labelVega
        tk.Label(self, text = "Vega:").grid(row=2, column=5)
        # labelVega
        self.labelVega = tk.Label(self, text = "")
        self.labelVega.grid(row=2, column=6)

        global labelVega
        labelVega = self.labelVega
        
        # labelTheta
        tk.Label(self, text = "Theta:").grid(row=3, column=5)
        # labelTheta
        self.labelTheta = tk.Label(self, text = "")
        self.labelTheta.grid(row=3, column=6)

        global labelTheta
        labelTheta = self.labelTheta
        
        # labelRho
        tk.Label(self, text = "Rho:").grid(row=4, column=5)
        # labelRho
        self.labelRho = tk.Label(self, text = "")
        self.labelRho.grid(row=4, column=6)

        global labelRho
        labelRho = self.labelRho
               
    def buttonSKQuoteLib_Gamma_Click(self):
        # 輸入1~5得到 Gamma值
        Gamma, nCode= m_pSKQuote.SKQuoteLib_Gamma(int(textBoxS.get()), int(textBoxK.get()), int(textBoxR.get()), int(textBoxT.get()), int(textBoxsigma.get()))
        labelGamma.config(text = Gamma)
        msg = "【SKQuoteLib_Gamma】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        # 輸入1~5得到 Vega值
        Vega, nCode= m_pSKQuote.SKQuoteLib_Vega(int(textBoxS.get()), int(textBoxK.get()), int(textBoxR.get()), int(textBoxT.get()), int(textBoxsigma.get()))
        labelVega.config(text = Vega)
        msg = "【SKQuoteLib_Vega】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)

        if (comboBoxnCallPut.get() == "Call"):
            nCallPut = 0
        elif (comboBoxnCallPut.get() == "Put"):
            nCallPut = 1
        # 輸入1~6得到 Delta值
        Delta, nCode= m_pSKQuote.SKQuoteLib_Delta(nCallPut, int(textBoxS.get()), int(textBoxK.get()), int(textBoxR.get()), int(textBoxT.get()), int(textBoxsigma.get()))
        labelDelta.config(text = Delta)
        msg = "【SKQuoteLib_Delta】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        # 輸入1~6得到 Theta值
        Theta, nCode= m_pSKQuote.SKQuoteLib_Theta(nCallPut, int(textBoxS.get()), int(textBoxK.get()), int(textBoxR.get()), int(textBoxT.get()), int(textBoxsigma.get()))
        labelTheta.config(text = Theta)
        msg = "【SKQuoteLib_Theta】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        # 輸入1~6得到 Rho值
        Rho, nCode= m_pSKQuote.SKQuoteLib_Rho(nCallPut, int(textBoxS.get()), int(textBoxK.get()), int(textBoxR.get()), int(textBoxT.get()), int(textBoxsigma.get()))
        labelRho.config(text = Rho)
        msg = "【SKQuoteLib_Rho】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
######################################################################################################################################
#TradeForm
class TradeForm(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.createWidgets()
    def createWidgets(self):

        # textBoxSKQuoteLib_RequestFutureTradeInfopsPageNo
        tk.Label(self, text = "Page").grid(row=0, column=1)
            #輸入框
        self.textBoxSKQuoteLib_RequestFutureTradeInfopsPageNo = tk.Entry(self)
        self.textBoxSKQuoteLib_RequestFutureTradeInfopsPageNo.grid(row=0, column=2)

        global textBoxSKQuoteLib_RequestFutureTradeInfopsPageNo
        textBoxSKQuoteLib_RequestFutureTradeInfopsPageNo = self.textBoxSKQuoteLib_RequestFutureTradeInfopsPageNo
        
        # textBoxSKQuoteLib_RequestFutureTradeInfobstrStockNo
        tk.Label(self, text = "請輸入商品代號(僅1檔)").grid(row=0, column=3)
            #輸入框
        self.textBoxSKQuoteLib_RequestFutureTradeInfobstrStockNo = tk.Entry(self)
        self.textBoxSKQuoteLib_RequestFutureTradeInfobstrStockNo.grid(row=0, column=4)

        global textBoxSKQuoteLib_RequestFutureTradeInfobstrStockNo
        textBoxSKQuoteLib_RequestFutureTradeInfobstrStockNo = self.textBoxSKQuoteLib_RequestFutureTradeInfobstrStockNo
                        
        # buttonSKQuoteLib_RequestFutureTradeInfo
        self.buttonSKQuoteLib_RequestFutureTradeInfo = tk.Button(self)
        self.buttonSKQuoteLib_RequestFutureTradeInfo["text"] = "期貨"
        self.buttonSKQuoteLib_RequestFutureTradeInfo["command"] = self.buttonSKQuoteLib_RequestFutureTradeInfo_Click
        self.buttonSKQuoteLib_RequestFutureTradeInfo.grid(row=1, column=1)
                        
        # buttonSKQuoteLib_GetStrikePrices
        self.buttonSKQuoteLib_GetStrikePrices = tk.Button(self)
        self.buttonSKQuoteLib_GetStrikePrices["text"] = "選擇權"
        self.buttonSKQuoteLib_GetStrikePrices["command"] = self.buttonSKQuoteLib_GetStrikePrices_Click
        self.buttonSKQuoteLib_GetStrikePrices.grid(row=2, column=1)

    def buttonSKQuoteLib_RequestFutureTradeInfo_Click(self):
        psPageNo = ctypes.c_short(int(textBoxSKQuoteLib_RequestFutureTradeInfopsPageNo.get()))
        # 取得報價函式庫註冊接收期貨商品的交易資訊
        nCode= m_pSKQuote.SKQuoteLib_RequestFutureTradeInfo(psPageNo, textBoxSKQuoteLib_RequestFutureTradeInfobstrStockNo.get())

        msg = "【SKQuoteLib_RequestFutureTradeInfo】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        richTextBoxMethodMessage.insert('end',  msg + "\n")
        richTextBoxMethodMessage.see('end')
        
    def buttonSKQuoteLib_GetStrikePrices_Click(self):
        # 取得報價函式庫選擇權交易商品資訊
        nCode= m_pSKQuote.SKQuoteLib_GetStrikePrices()

        msg = "【SKQuoteLib_GetStrikePrices】" + m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
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
def popup_window_Market():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Market")

    # 建立 Frame 作為 MarketForm，並添加到彈出窗口
    popup_MarketForm = MarketForm(popup)
    popup_MarketForm.pack(fill=tk.BOTH, expand=True)
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
def popup_window_KLine():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("KLine")

    # 建立 Frame 作為 KLineForm，並添加到彈出窗口
    popup_KLineForm = KLineForm(popup)
    popup_KLineForm.pack(fill=tk.BOTH, expand=True)
def popup_window_Delta():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Delta")

    # 建立 Frame 作為 DeltaForm，並添加到彈出窗口
    popup_DeltaForm = DeltaForm(popup)
    popup_DeltaForm.pack(fill=tk.BOTH, expand=True)
def popup_window_Trade():
    # 建立Toplevel
    popup = tk.Toplevel()
    popup.title("Trade")

    # 建立 Frame 作為 TradeForm，並添加到彈出窗口
    popup_TradeForm = TradeForm(popup)
    popup_TradeForm.pack(fill=tk.BOTH, expand=True)
#開啟Tk視窗
if __name__ == '__main__':
    #建立主視窗
    root = tk.Tk()
    root.title("Quote")
    
    #建立Frame (訊息框)
    frame_A = MessageForm(root)
    frame_A.grid(row = 0, column= 0)

    # 開啟Connect視窗的按鈕
    popup_button_Connect = tk.Button(root, text="連線", command=popup_window_Connect)
    popup_button_Connect.grid(row = 1, column= 0)
    
    # 開啟Market視窗的按鈕
    popup_button_Market = tk.Button(root, text="大盤資訊", command=popup_window_Market)
    popup_button_Market.grid(row = 2, column= 0)
        
    # 開啟Product視窗的按鈕
    popup_button_Product = tk.Button(root, text="商品清單&個股資訊", command=popup_window_Product)
    popup_button_Product.grid(row = 3, column= 0)
            
    # 開啟Request視窗的按鈕
    popup_button_Request = tk.Button(root, text="即時報價", command=popup_window_Request)
    popup_button_Request.grid(row = 4, column= 0)
                
    # 開啟Ticks視窗的按鈕
    popup_button_Ticks = tk.Button(root, text="五檔&成交明細", command=popup_window_Ticks)
    popup_button_Ticks.grid(row = 5, column= 0)
                
    # 開啟KLine視窗的按鈕
    popup_button_KLine = tk.Button(root, text="技術分析", command=popup_window_KLine)
    popup_button_KLine.grid(row = 6, column= 0)
                    
    # 開啟Delta視窗的按鈕
    popup_button_Delta = tk.Button(root, text="風險計算(選擇權)", command=popup_window_Delta)
    popup_button_Delta.grid(row = 7, column= 0)
                        
    # 開啟Trade視窗的按鈕
    popup_button_Trade = tk.Button(root, text="交易資訊(期選)", command=popup_window_Trade)
    popup_button_Trade.grid(row = 8, column= 0)

    root.mainloop()

#==========================================
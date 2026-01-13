# 先把API com元件初始化
import os
from ctypes import wintypes
# 第一種讓群益API元件可導入讓Python code使用的方法
#import win32com.client
#from ctypes import WinDLL,byref
#from ctypes.wintypes import MSG
#SKCenterLib = win32com.client.Dispatch("{AC30BAB5-194A-4515-A8D3-6260749F8577}")
#SKReplyLib = win32com.client.Dispatch("{72D98963-03E9-42AB-B997-BB2E5CCE78DD}")

# 第二種讓群益API元件可導入Python code內用的物件宣告
import comtypes.client
comtypes.client.GetModule(os.path.split(os.path.realpath(__file__))[0] + r"/SKCOM.dll")
import comtypes.gen.SKCOMLib as sk
skC = comtypes.client.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
skOOQ = comtypes.client.CreateObject(sk.SKOOQuoteLib,interface=sk.ISKOOQuoteLib)
skO = comtypes.client.CreateObject(sk.SKOrderLib,interface=sk.ISKOrderLib)
skOSQ = comtypes.client.CreateObject(sk.SKOSQuoteLib,interface=sk.ISKOSQuoteLib)
skQ = comtypes.client.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)
skR = comtypes.client.CreateObject(sk.SKReplyLib,interface=sk.ISKReplyLib)

# 畫視窗用物件
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox,colorchooser,font,Button,Frame,Label

# 數學計算用物件
import math

# 顯示各功能狀態用的function
def WriteMessage(strMsg,listInformation):
    listInformation.insert('end', strMsg)
    listInformation.see('end')
def SendReturnMessage(strType, nCode, strMessage,listInformation):
    GetMessage(strType, nCode, strMessage,listInformation)
def GetMessage(strType,nCode,strMessage,listInformation):
    strInfo = ""
    if (nCode != 0):
        strInfo ="【"+ skC.SKCenterLib_GetLastLogInfo()+ "】"
    WriteMessage("【" + strType + "】【" + strMessage + "】【" + skC.SKCenterLib_GetReturnCodeMessage(nCode) + "】" + strInfo,listInformation)

#----------------------------------------------------------------------------------------------------------------------------------------------------
#上半部登入框
class FrameLogin(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.grid()
        #self.pack()
        self.place()
        self.FrameLogin = Frame(self)
        self.master["background"] = "#F5F5F5"
        self.FrameLogin.master["background"] = "#F5F5F5"
        self.createWidgets()

    def createWidgets(self):
        #帳號
        self.labelID = Label(self)
        self.labelID["text"] = "帳號："
        self.labelID["background"] = "#F5F5F5"
        self.labelID["font"] = 20
        self.labelID.grid(column=0,row=0)
            #輸入框
        self.textID = Entry(self)
        self.textID["width"] = 50
        self.textID.grid(column = 1, row = 0)

        #密碼
        self.labelPassword = Label(self)
        self.labelPassword["text"] = "密碼："
        self.labelPassword["background"] = "#F5F5F5"
        self.labelPassword["font"] = 20
        self.labelPassword.grid(column = 2, row = 0)
            #輸入框
        self.textPassword = Entry(self)
        self.textPassword["width"] = 50
        self.textPassword['show'] = '*'
        self.textPassword.grid(column = 3, row = 0)

        #按鈕
        self.buttonLogin = Button(self)
        self.buttonLogin["text"] = "登入"
        self.buttonLogin["background"] = "#4169E1"
        self.buttonLogin["foreground"] = "#ffffff"
        self.buttonLogin["font"] = 20
        self.buttonLogin["command"] = self.buttonLogin_Click
        self.buttonLogin.grid(column = 4, row = 0)

        #ID
        self.labelID = Label(self)
        self.labelID["text"] = "<<ID>>"
        self.labelID["background"] = "#F5F5F5"
        self.labelID["font"] = 20
        self.labelID.grid(column = 5, row = 0)

        #訊息欄
        self.listInformation = Listbox(root, height=5)
        self.listInformation.grid(column = 0, row = 1, sticky = E + W)

        global GlobalListInformation,Global_ID
        GlobalListInformation = self.listInformation
        Global_ID = self.labelID

    def buttonLogin_Click(self):
        try:
            m_nCode = skC.SKCenterLib_SetLogPath(os.path.split(os.path.realpath(__file__))[0] + "\\CapitalLog_Reply")
            m_nCode = skC.SKCenterLib_Login(self.textID.get().replace(' ',''),self.textPassword.get().replace(' ',''))
            m_nCode = skC.SKCenterLib_Debug(os.path.split(os.path.realpath(__file__))[0] + "\\CapitalLog_Reply")
            if(m_nCode==0):
                Global_ID["text"] =  self.textID.get().replace(' ','')
                WriteMessage("登入成功",self.listInformation)
            elif m_nCode == 151:
                WriteMessage("密碼錯誤",self.listInformation)
            else:
                WriteMessage(m_nCode,self.listInformation)
        except Exception as e:
            messagebox.showerror("error！",e)

    def GetID(self):
        return self.textID.get().replace(' ','')

#下半部-回報
class FrameReply(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.grid()
        self.FrameReply = Frame(self)
        self.FrameReply.master["background"] = "#F5F5F5"
        self.createWidgets()

    def createWidgets(self):
        #ID
        # self.labelID = Label(self)
        # self.labelID["text"] = "ID："
        # self.labelID.grid(column = 0, row = 0)

        #Connect
        self.btnConnect = Button(self)
        self.btnConnect["text"] = " 連線 "
        self.btnConnect["background"] = "#d0d0d0"
        self.btnConnect["font"] = "20"
        self.btnConnect.grid(column = 0, row = 1)
        self.btnConnect["command"] = self.btnConnect_Click

        #Disconnect
        self.btnDisconnect = Button(self)
        self.btnDisconnect["text"] = " 斷線 "
        self.btnDisconnect["background"] = "#d0d0d0"
        self.btnDisconnect["font"] = "20"
        self.btnDisconnect.grid(column = 1, row = 1)
        self.btnDisconnect["command"] = self.btnDisconnect_Click

        #ConnectStatus
        self.ConnectStatus = Button(self)
        self.ConnectStatus["text"] = "連線狀態"
        self.btnDisconnect["background"] = "#d0d0d0"
        self.ConnectStatus["font"] = "20"
        self.ConnectStatus.grid(column = 2, row = 1)
        self.ConnectStatus["command"] = self.ConnectStatus_Click

        #SolaceClose
        self.SolaceClose = Button(self)
        self.SolaceClose["text"] = "中斷Solace連線"
        self.SolaceClose["background"] = "#d0d0d0"
        self.SolaceClose["font"] = "20"
        self.SolaceClose.grid(column = 3, row = 1)
        self.SolaceClose["command"] = self.SolaceClose_Click

        #訊息欄
        self.listInformation = Listbox(self, height = 25, width = 100)
        self.listInformation.grid(column = 0, row = 2, sticky = E + W, columnspan = 4)

        sb = Scrollbar(self,orient='horizontal',command = self.listInformation.xview)
        sb.grid(row = 3, column = 0,columnspan = 4,sticky = 'ew')
        #self.listInformation.config(xscrollcommand = sb.set)


        global ReplyInformation
        ReplyInformation = self.listInformation

    def btnConnect_Click(self):
        try:
            nErrorCode = skR.SKReplyLib_ConnectByID(frLogin.GetID())
            SendReturnMessage("Reply", nErrorCode, "SKReplyLib_Connect",GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！",e)

    def btnDisconnect_Click(self):
        try:
            nErrorCode = skR.SKReplyLib_CloseByID(frLogin.GetID())
            SendReturnMessage("Reply", nErrorCode, "SKReplyLib_DisConnect",GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！",e)

    def ConnectStatus_Click(self):
        try:
            nErrorCode = skR.SKReplyLib_IsConnectedByID(frLogin.GetID())
            if nErrorCode == 1:
                strMsg = "SKReplyLib_ConnectStatus 連線成功"
            elif nErrorCode == 0:
                strMsg = "SKReplyLib_ConnectStatus 斷線中"
            WriteMessage(strMsg,GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！",e)

    def SolaceClose_Click(self):
        try:
            nErrorCode = skR.SKReplyLib_SolaceCloseByID(frLogin.GetID())
            SendReturnMessage("Reply", nErrorCode, "SKReplyLib_ConnectClose",GlobalListInformation)
        except Exception as e:
            messagebox.showerror("error！",e)

class SKReplyLibEvent:
    def OnConnect(self, btrUserID, nErrorCode):
        if nErrorCode == 0:
            strMsg = btrUserID,"Connected!"
        else :
            strMsg = btrUserID,"Connect Error!"
        WriteMessage(strMsg,ReplyInformation)

    def OnDisconnect(self,btrUserID, nErrorCode):
        if nErrorCode == 3002:
            strMsg = "OnDisconnect 您已經斷線囉~~~"
        else:
            strMsg = nErrorCode
        WriteMessage(strMsg,ReplyInformation)

    def OnComplete(self,btrUserID):
        WriteMessage("OnComplete",ReplyInformation)

    def OnData(self,btrUserID,bstrData):
        cutData = bstrData.split(',')
        print(cutData[0])
        print(cutData[10])
        WriteMessage("OnData"+"\n"+bstrData,ReplyInformation)

    def OnNewData(self,btrUserID,bstrData):
        cutData = bstrData.split(',')
        #strMsg = {" 委託序號 ": cutData[0] , " 委託種類 " : cutData[2] , " 委託狀態 " : cutData[3] ," 商品代碼 " : cutData[8] ,
        # " 委託書號 " : cutData[10]," 價格 " : cutData[11] , " 數量 " : cutData[20] ,
        #" 日期&時間 " : cutData[23] + " " +cutData[24] , "錯誤訊息" : cutData[-4] + " " + cutData[-3]}
        #WriteMessage( strMsg,ReplyInformation)
        WriteMessage("OnNewData"+"\n"+cutData ,ReplyInformation)

    def OnReplyMessage(self,bstrUserID, bstrMessages):
        sConfirmCode = -1
        WriteMessage(bstrMessages,ReplyInformation)
        return sConfirmCode

    def OnReplyClearMessage(self,bstrUserID):
        WriteMessage("OnReplyClearMessage",ReplyInformation)

    def OnSolaceReplyDisconnect(self,btrUserID, nErrorCode):
        if nErrorCode == 3002:
            strMsg = "OnSolaceReplyDisconnect SK_SUBJECT_CONNECTION_DISCONNECT"
        else:
            strMsg = nErrorCode
        WriteMessage(strMsg,ReplyInformation)

    def OnSmartData(self,btrUserID,bstrData):
        cutData = bstrData.split(',')
        WriteMessage("OnSmartData"+"\n"+bstrData ,ReplyInformation)

    def OnReplyClear(self,bstrMarket):
        strMsg = "Clear Market: " + bstrMarket
        WriteMessage(strMsg,ReplyInformation)

SKReplyEvent = SKReplyLibEvent()
SKReplyLibEventHandler = comtypes.client.GetEvents(skR, SKReplyEvent)

if __name__ == '__main__':
    root = Tk()
    root.title("PythonExampleReply")
    root["background"] = "#ffdbdb"

    frLogin = FrameLogin(master = root)

    #TabControl
    root.TabControl = Notebook(root)
    root.TabControl.add(FrameReply(master = root),text="Reply")
    root.TabControl.grid(column = 0, row = 2, sticky = E + W)
    root.mainloop()

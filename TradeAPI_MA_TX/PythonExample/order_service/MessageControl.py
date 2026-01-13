# 先把API com元件初始化
import os
import Global
# 第二種讓群益API元件可導入Python code內用的物件宣告
import comtypes.client
#comtypes.client.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\SKCOM.dll')
import comtypes.gen.SKCOMLib as sk
skC = Global.skC

class MessageControl():
    def __init__(self):
        return

    # 顯示各功能狀態用的function
    def WriteMessage(self, strMsg, listInformation):
        listInformation.insert('end', strMsg)
        listInformation.see('end')

    def SendReturnMessage(self, strType, nCode, strMessage, listInformation):
        strInfo = ""
        if (nCode != 0):
            strInfo = "【" + skC.SKCenterLib_GetLastLogInfo() + "】"
        self.WriteMessage("【" + strType + "】【" + strMessage + "】【" + skC.SKCenterLib_GetReturnCodeMessage(nCode) + "】" + strInfo, listInformation)

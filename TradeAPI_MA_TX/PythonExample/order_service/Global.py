# 第二種讓群益API元件可導入Python code內用的物件宣告
import comtypes.client
#comtypes.client.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\SKCOM.dll')
import comtypes.gen.SKCOMLib as sk

def SetID(id):
    iid = id
    global Global_IID
    Global_IID = iid

global skO, skC, skQ, skR, skOSQ, skOOQ

skO = comtypes.client.CreateObject(sk.SKOrderLib,interface=sk.ISKOrderLib)

skC = comtypes.client.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)

skQ = comtypes.client.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)

skR = comtypes.client.CreateObject(sk.SKReplyLib,interface=sk.ISKReplyLib)

skOSQ = comtypes.client.CreateObject(sk.SKOSQuoteLib,interface=sk.ISKOSQuoteLib)

skOOQ = comtypes.client.CreateObject(sk.SKOOQuoteLib,interface=sk.ISKOOQuoteLib)

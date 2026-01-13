# setting about combobox
PRIMESET = (
    "上市櫃", "興櫃",
)

BUYSELLSET = (
    "買進", "賣出",
)

PERIODSET = dict(
    stock = ("盤中", "盤後", "零股", "盤中零股"),
    stock_tradetype = ("ROD", "IOC", "FOK"),
    future = ("ROD", "IOC", "FOK"),
    sea_future = ("ROD"),
    moving_stop_loss = ("IOC", "FOK"),
)

STRADETYPE = dict(
    stock = ("市價", "限價"),
    sea_future = ("LMT（限價）", "MKT（市價）", "STL（停損限價）", "STP（停損市價）"),
    sea_option = ("LMT（限價）"),
    strategy = ("範圍市價", "限價"),
)

FLAGSET = dict(
    stock = ("現股", "融資", "融券", "無券"),
    future = ("非當沖", "當沖"),
)

NEWCLOSESET = dict(
    future = ("新倉", "平倉", "自動"),
    sea_future = ("新倉"),
    option_future = ("新倉", "平倉")
)

RESERVEDSET = (
    "盤中", "T盤預約",
)

CALLPUTSET = (
    "CALL", "PUT",
)

ACCOUNTTYPESET = (
    "外幣專戶", "台幣專戶",
)

CURRENCYSET = (
    "HKD", "NTD", "USD", "JPY", "SGD", "EUR", "AUD",
)

EXCHANGENOSET = (
    "美股",
)

MARKETTYPE = (
    "TS (證券)","TF(期貨)","TO(選擇權)","OS(複委託)","OF(海外期貨)","OO(海外選擇權)",
)

OPENINTERSETFORMAT = (
    "1.完整","2.格式一","3.格式二-含損益"
)

COINTYPE = (
    "ALL","新台幣(TWD)","人民幣(RMB)"
)

REPORTSTATUS = (
    "0:全部的委託單"
)

STOPLOSSKIND = dict(
    delete = ("STP","MST","OCO"),
    report = ("STP","MST","OCO","MIT"),
)

ASYNC = (
    "同步","非同步"
)

WITHDRAWTYPE = (
    "國內","國外"
)

WITHDRAWCURRENCY = (
    "0:澳幣 AUD","1:歐元 EUR","2:英鎊 GBP","3:港幣 HKD","4:日元 JPY","5:台幣 NTD","6:紐幣 NZD","7:人民幣 RMB","8:美元 USD","9:南非幣 ZAR"
)

STOCKSMARTDAYTRADE = (
    "現股買","無券賣出"
)

STOCKSTRATEGYORDERTYPE = (
    "現股","融資","融券"
)

STOCKSMARTSTRATEGYKIND = (
    "當沖","出清"
)

STCOKSTRATEGYTRADEKIND = (
    "當沖母單","當沖未成交入場單","當沖已進場單","出清"
)

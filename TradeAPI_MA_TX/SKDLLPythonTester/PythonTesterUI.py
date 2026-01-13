import tkinter as tk
from tkinter import ttk

class Login(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="登入")

        # ===== groupBox2: 帳號管理 =====
        self.groupBoxLogin = ttk.LabelFrame(self, text="Login")
        self.groupBoxLogin.grid(row=0, column=0, columnspan=4, padx=5, pady=10, sticky="ew")

        # ===== UserID =====
        ttk.Label(self.groupBoxLogin, text="UserID").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.textBoxUserID = ttk.Entry(self.groupBoxLogin)
        self.textBoxUserID.grid(row=1, column=0, padx=5, pady=2)

        # ===== Password =====
        ttk.Label(self.groupBoxLogin, text="Password").grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.textBoxPassword = ttk.Entry(self.groupBoxLogin, show="*")
        self.textBoxPassword.grid(row=1, column=1, padx=5, pady=2)

        # ===== SKCenterLib_Login Button =====
        self.buttonSKCenterLib_Login = ttk.Button(self.groupBoxLogin, text="SKCenterLib_Login")
        self.buttonSKCenterLib_Login.grid(row=1, column=2, padx=5, pady=2)

        # ===== comboBoxAuthorityFlag =====
        ttk.Label(self.groupBoxLogin, text="Authority").grid(row=0, column=3, sticky="w", padx=5, pady=2)
        self.comboBoxAuthorityFlag = ttk.Combobox(self.groupBoxLogin, state="readonly")
        self.comboBoxAuthorityFlag['values'] = [
            "0:正式",
            "1:正式SGX",
            "2:測試",
            "3:測試SGX"
        ]
        self.comboBoxAuthorityFlag.current(0)
        self.comboBoxAuthorityFlag.grid(row=1, column=3, padx=5, pady=2)

        # ===== groupBox2: 帳號管理 =====
        self.groupBox2 = ttk.LabelFrame(self, text="帳號管理")
        self.groupBox2.grid(row=1, column=0, columnspan=4, padx=5, pady=10, sticky="ew")

        # ===== 證券 =====
        ttk.Label(self.groupBox2, text="證券").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.comboBoxTS = ttk.Combobox(self.groupBox2, state="readonly")
        self.comboBoxTS.grid(row=1, column=0, padx=5, pady=2)

        # ===== 複委託 =====
        ttk.Label(self.groupBox2, text="複委託").grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.comboBoxOS = ttk.Combobox(self.groupBox2, state="readonly")
        self.comboBoxOS.grid(row=1, column=1, padx=5, pady=2)

        # ===== 內期 =====
        ttk.Label(self.groupBox2, text="內期").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.comboBoxTF = ttk.Combobox(self.groupBox2, state="readonly")
        self.comboBoxTF.grid(row=1, column=2, padx=5, pady=2)

        # ===== 海期 =====
        ttk.Label(self.groupBox2, text="海期").grid(row=0, column=3, sticky="w", padx=5, pady=2)
        self.comboBoxOF = ttk.Combobox(self.groupBox2, state="readonly")
        self.comboBoxOF.grid(row=1, column=3, padx=5, pady=2)


        # ===== groupBox7: 與主機建立連線 =====
        self.groupBox7 = ttk.LabelFrame(self, text="與主機建立連線")
        self.groupBox7.grid(row=0, column=4, columnspan=4, padx=5, pady=10, sticky="ew")

        # ===== comboBoxStatus =====
        self.comboBoxStatus = ttk.Combobox(self.groupBox7, state="readonly")
        self.comboBoxStatus['values'] = [
            "0:連線",
            "1:斷線",
            "2:重連(僅Proxy連線有重連)",
            "3:連線(不下載商品檔)",
            "4:連線(備援(僅海期選))"
        ]
        self.comboBoxStatus.current(0)
        self.comboBoxStatus.grid(row=0, column=0, padx=5, pady=2)

        # ===== comboBoxTargetType =====
        self.comboBoxTargetType = ttk.Combobox(self.groupBox7, state="readonly")
        self.comboBoxTargetType['values'] = [
            "0:回報",
            "1:國內行情",
            "2:海期行情",
            "3:海選行情",
            "4:Proxy下單"
        ]
        self.comboBoxTargetType.current(0)
        self.comboBoxTargetType.grid(row=1, column=0, padx=5, pady=2)

        # ===== buttonManageServerConnection =====
        self.buttonManageServerConnection = ttk.Button(self.groupBox7, text="ManageServerConnection")
        self.buttonManageServerConnection.grid(row=2, column=0, padx=5, pady=5)

        # ===== comboBoxnMarketNo =====
        ttk.Label(self.groupBox7, text="下載指定市場別商品檔").grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.comboBoxnMarketNo = ttk.Combobox(self.groupBox7, state="readonly")
        self.comboBoxnMarketNo['values'] = [
            "0: 上市",
            "1: 上櫃",
            "2: 期貨T盤行情",
            "3: 選擇權T盤行情",
            "4: 興櫃",
            "5: 零股-上市",
            "6: 零股-上櫃",
            "7: 期貨全盤行情",
            "8: 選擇權全盤行情",
            "9: 客製化期貨",
            "10: 客製化選擇權",
            "11: 全市場",
            "12: 股票市場",
            "13: 期貨市場",
            "14: 海期市場",
            "15: 海選市場"
        ]
        self.comboBoxnMarketNo.current(0)
        self.comboBoxnMarketNo.grid(row=1, column=1, padx=5, pady=2)
        
        # ===== buttonLoadCommodity =====
        self.buttonLoadCommodity = ttk.Button(self.groupBox7, text="LoadCommodity")
        self.buttonLoadCommodity.grid(row=2, column=1, padx=5, pady=5)

        # ===== groupBox6: 回傳值 =====
        self.groupBox6 = ttk.LabelFrame(self, text="回傳值")
        self.groupBox6.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky="ew")
        # 讓內部 column 0 可以伸展
        self.groupBox6.columnconfigure(0, weight=1)

        self.listOnReplyMessage = tk.Listbox(self.groupBox6, height=6)
        self.listOnReplyMessage.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

class Order(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="新單(需先連上Proxy)")

        # 建立 Canvas 和 Scrollbars
        canvas = tk.Canvas(self)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)

        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # 放置 Scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # 可滾動 Frame
        self.inner_frame = ttk.Frame(canvas)
        self.inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # 可滾動 Frame 自身也要可伸縮
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.tabControl1 = ttk.Notebook(self.inner_frame)
        self.tabControl1.grid(row=0, column=0, sticky="nsew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # 建立六個 TabPage
        self.TabPage1 = ttk.Frame(self.tabControl1)
        self.TabPage2 = ttk.Frame(self.tabControl1)
        self.TabPage3 = ttk.Frame(self.tabControl1)
        self.TabPage4 = ttk.Frame(self.tabControl1)
        self.TabPage5 = ttk.Frame(self.tabControl1)
        self.TabPage6 = ttk.Frame(self.tabControl1)
        self.TabPage18 = ttk.Frame(self.tabControl1)

        self.tabControl1.add(self.TabPage1, text="證券")
        self.tabControl1.add(self.TabPage2, text="期貨")
        self.tabControl1.add(self.TabPage3, text="選擇權")
        self.tabControl1.add(self.TabPage4, text="海期")
        self.tabControl1.add(self.TabPage5, text="海選")
        self.tabControl1.add(self.TabPage6, text="複委託")
        self.tabControl1.add(self.TabPage18, text="帳務")

        # 建立 tabControl7
        self.tabControl7 = ttk.Notebook(self.TabPage18)
        self.tabControl7.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.TabPage22 = ttk.Frame(self.tabControl7)
        self.TabPage23 = ttk.Frame(self.tabControl7)
        self.TabPage24 = ttk.Frame(self.tabControl7)
        self.TabPage25 = ttk.Frame(self.tabControl7)

        self.tabControl7.add(self.TabPage22, text="證券")
        self.tabControl7.add(self.TabPage23, text="內期")
        self.tabControl7.add(self.TabPage24, text="外期")
        self.tabControl7.add(self.TabPage25, text="複委託")

        # === 證券Proxy委託 groupBox10 放入 TabPage1 ===
        self.groupBox10 = ttk.LabelFrame(self.TabPage1, text="證券 Proxy 委託")
        self.groupBox10.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(9):
            self.groupBox10.columnconfigure(i, weight=1)

        # 商品代碼
        ttk.Label(self.groupBox10, text="商品代碼").grid(row=0, column=0, padx=2, pady=2)
        self.txtProxyStockNo = ttk.Entry(self.groupBox10)
        self.txtProxyStockNo.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        # 下單類別
        ttk.Label(self.groupBox10, text="下單類別").grid(row=0, column=1, padx=2, pady=2)
        self.ProxyOrderTypeBox = ttk.Combobox(self.groupBox10, values=[
            "現股買進", "現股賣出", "融資買進", "融資賣出", "融券買進", "融券賣出", "無券賣出"
        ])
        self.ProxyOrderTypeBox.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # 價格類別
        ttk.Label(self.groupBox10, text="價格類別").grid(row=0, column=2, padx=2, pady=2)
        self.ProxyPriceTypeBox = ttk.Combobox(self.groupBox10, values=["市價", "限價"])
        self.ProxyPriceTypeBox.grid(row=1, column=2, sticky="ew", padx=2, pady=2)

        # 委託時效
        ttk.Label(self.groupBox10, text="委託時效").grid(row=0, column=3, padx=2, pady=2)
        self.ProxyTimeBox = ttk.Combobox(self.groupBox10, values=["ROD", "IOC", "FOK"])
        self.ProxyTimeBox.grid(row=1, column=3, sticky="ew", padx=2, pady=2)

        # 盤別
        ttk.Label(self.groupBox10, text="盤別").grid(row=0, column=4, padx=2, pady=2)
        self.ProxyMarketBox = ttk.Combobox(self.groupBox10, values=["盤中", "零股", "盤後交易", "盤中零股"])
        self.ProxyMarketBox.grid(row=1, column=4, sticky="ew", padx=2, pady=2)

        # 委託價
        ttk.Label(self.groupBox10, text="委託價").grid(row=0, column=5, padx=2, pady=2)
        self.txtProxyStockPrice = ttk.Entry(self.groupBox10)
        self.txtProxyStockPrice.grid(row=1, column=5, sticky="ew", padx=2, pady=2)

        # 委託量
        ttk.Label(self.groupBox10, text="委託量").grid(row=0, column=6, padx=2, pady=2)
        self.txtStockQty = ttk.Entry(self.groupBox10)
        self.txtStockQty.grid(row=1, column=6, sticky="ew", padx=2, pady=2)

        # 價格旗標
        ttk.Label(self.groupBox10, text="價格旗標").grid(row=0, column=7, padx=2, pady=2)
        self.ProxyPriceMarkBox = ttk.Combobox(self.groupBox10, values=["一般定價", "前日收盤價", "漲停", "跌停"])
        self.ProxyPriceMarkBox.grid(row=1, column=7, sticky="ew", padx=2, pady=2)

        # 按鈕：SendStockProxyOrder
        self.btnSendStockProxyOrder = ttk.Button(self.groupBox10, text="SendStockProxyOrder")
        self.btnSendStockProxyOrder.grid(row=1, column=8, padx=2, pady=2)

        # === 刪改單 groupBox5 ===
        self.groupBox5 = ttk.LabelFrame(self.TabPage1, text="刪改單")
        self.groupBox5.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox5.columnconfigure(tuple(range(9)), weight=1)

        # Row 0: Label
        ttk.Label(self.groupBox5, text="商品代碼").grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(self.groupBox5, text="下單類別").grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(self.groupBox5, text="價格類別").grid(row=0, column=2, padx=2, pady=2)
        ttk.Label(self.groupBox5, text="委託時效").grid(row=0, column=3, padx=2, pady=2)
        ttk.Label(self.groupBox5, text="盤別").grid(row=0, column=4, padx=2, pady=2)
        ttk.Label(self.groupBox5, text="委託價").grid(row=0, column=5, padx=2, pady=2)
        ttk.Label(self.groupBox5, text="委託量").grid(row=0, column=6, padx=2, pady=2)
        ttk.Label(self.groupBox5, text="價格旗標").grid(row=0, column=7, padx=2, pady=2)

        # Row 1: Entry / Combobox / Button
        self.txtProxyStockNo2 = ttk.Entry(self.groupBox5)
        self.txtProxyStockNo2.grid(row=1, column=0, padx=2, pady=2)

        self.ProxyOrderTypeBox2 = ttk.Combobox(self.groupBox5, values=[
            "刪單", "改量", "改價"
        ])
        self.ProxyOrderTypeBox2.grid(row=1, column=1, padx=2, pady=2)

        self.ProxyPriceTypeBox2 = ttk.Combobox(self.groupBox5, values=[
            "市價", "限價"
        ])
        self.ProxyPriceTypeBox2.grid(row=1, column=2, padx=2, pady=2)

        self.ProxyTimeBox2 = ttk.Combobox(self.groupBox5, values=[
            "ROD", "IOC", "FOK"
        ])
        self.ProxyTimeBox2.grid(row=1, column=3, padx=2, pady=2)

        self.ProxyMarketBox2 = ttk.Combobox(self.groupBox5, values=[
            "盤中", "零股", "盤後交易", "盤中零股"
        ])
        self.ProxyMarketBox2.grid(row=1, column=4, padx=2, pady=2)

        self.txtProxyStockPrice2 = ttk.Entry(self.groupBox5)
        self.txtProxyStockPrice2.grid(row=1, column=5, padx=2, pady=2)

        self.txtStockQty2 = ttk.Entry(self.groupBox5)
        self.txtStockQty2.grid(row=1, column=6, padx=2, pady=2)

        self.ProxyPriceMarkBox2 = ttk.Combobox(self.groupBox5, values=[
            "一般定價", "前日收盤價", "漲停", "跌停"
        ])
        self.ProxyPriceMarkBox2.grid(row=1, column=7, padx=2, pady=2)

        self.btnSendStockProxyAlter = ttk.Button(self.groupBox5, text="SendStockProxyAlter")
        self.btnSendStockProxyAlter.grid(row=1, column=8, padx=2, pady=2)

        # Row 2: Label for 書號與序號
        ttk.Label(self.groupBox5, text="委託書號").grid(row=2, column=4, padx=2, pady=2)
        ttk.Label(self.groupBox5, text="委託序號").grid(row=2, column=5, padx=2, pady=2)

        # Row 3: Entry for 書號與序號
        self.txtStockBookNo = ttk.Entry(self.groupBox5)
        self.txtStockBookNo.grid(row=3, column=4, padx=2, pady=2)

        self.txtStockSeqNo = ttk.Entry(self.groupBox5)
        self.txtStockSeqNo.grid(row=3, column=5, padx=2, pady=2)

        # === 期貨 Proxy 委託 groupBox9 ===
        self.groupBox9 = ttk.LabelFrame(self.TabPage2, text="期貨Proxy委託")
        self.groupBox9.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox9.columnconfigure(tuple(range(8)), weight=1)

        # Row 0: Labels
        ttk.Label(self.groupBox9, text="商品代碼").grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(self.groupBox9, text="買賣別").grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(self.groupBox9, text="委託條件").grid(row=0, column=2, padx=2, pady=2)
        ttk.Label(self.groupBox9, text="當沖與否").grid(row=0, column=3, padx=2, pady=2)
        ttk.Label(self.groupBox9, text="委託價").grid(row=0, column=4, padx=2, pady=2)
        ttk.Label(self.groupBox9, text="委託量").grid(row=0, column=5, padx=2, pady=2)
        ttk.Label(self.groupBox9, text="委價類別").grid(row=0, column=6, padx=2, pady=2)

        # Row 1: Inputs
        self.txtFutureNo = ttk.Entry(self.groupBox9)
        self.txtFutureNo.grid(row=1, column=0, padx=2, pady=2)

        self.boxProxyBS = ttk.Combobox(self.groupBox9, values=["買", "賣"])
        self.boxProxyBS.grid(row=1, column=1, padx=2, pady=2)

        self.boxProxyCOND = ttk.Combobox(self.groupBox9, values=["ROD", "IOC", "FOK"])
        self.boxProxyCOND.grid(row=1, column=2, padx=2, pady=2)

        self.boxDayTrade = ttk.Combobox(self.groupBox9, values=["非當沖", "當沖"])
        self.boxDayTrade.grid(row=1, column=3, padx=2, pady=2)

        self.txtFuturePrice = ttk.Entry(self.groupBox9)
        self.txtFuturePrice.grid(row=1, column=4, padx=2, pady=2)

        self.txtFutureQty = ttk.Entry(self.groupBox9)
        self.txtFutureQty.grid(row=1, column=5, padx=2, pady=2)

        self.boxProxyPriceFlag = ttk.Combobox(self.groupBox9, values=["市價單", "限價單", "範圍市價"])
        self.boxProxyPriceFlag.grid(row=1, column=6, padx=2, pady=2)

        # Row 2: Labels
        ttk.Label(self.groupBox9, text="商品年月").grid(row=2, column=0, padx=2, pady=2)
        ttk.Label(self.groupBox9, text="倉別").grid(row=2, column=5, padx=2, pady=2)
        ttk.Label(self.groupBox9, text="盤別").grid(row=2, column=6, padx=2, pady=2)

        # Row 3: Inputs + Button
        self.txtProxyYM = ttk.Entry(self.groupBox9)
        self.txtProxyYM.grid(row=3, column=0, padx=2, pady=2)

        self.boxProxyORDERType = ttk.Combobox(self.groupBox9, values=["新倉", "平倉", "自動"])
        self.boxProxyORDERType.grid(row=3, column=5, padx=2, pady=2)

        self.boxProxyPreOrder = ttk.Combobox(self.groupBox9, values=["盤中", "T盤預約"])
        self.boxProxyPreOrder.grid(row=3, column=6, padx=2, pady=2)

        self.btnSendProxyFutureOrderCLR = ttk.Button(self.groupBox9, text="SendProxyFutureOrder")
        self.btnSendProxyFutureOrderCLR.grid(row=3, column=7, padx=2, pady=2)

        # === 期貨 Proxy 刪改單 groupBox11 ===
        self.groupBox11 = ttk.LabelFrame(self.TabPage2, text="期貨Proxy刪改單")
        self.groupBox11.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox11.columnconfigure(tuple(range(5)), weight=1)

        # Row 0: Labels
        ttk.Label(self.groupBox11, text="委託類別").grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(self.groupBox11, text="委託條件").grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(self.groupBox11, text="盤別").grid(row=0, column=2, padx=2, pady=2)
        ttk.Label(self.groupBox11, text="改價:委託價").grid(row=0, column=3, padx=2, pady=2)

        # Row 1: Inputs
        self.boxProxyORDERType2 = ttk.Combobox(self.groupBox11, values=["刪單", "減量", "改價"])
        self.boxProxyORDERType2.grid(row=1, column=0, padx=2, pady=2)

        self.boxProxyCOND2 = ttk.Combobox(self.groupBox11, values=["ROD", "IOC", "FOK"])
        self.boxProxyCOND2.grid(row=1, column=1, padx=2, pady=2)

        self.boxProxyPreOrder2 = ttk.Combobox(self.groupBox11, values=["盤中", "T盤預約"])
        self.boxProxyPreOrder2.grid(row=1, column=2, padx=2, pady=2)

        self.txtProxyPrice2 = ttk.Entry(self.groupBox11)
        self.txtProxyPrice2.grid(row=1, column=3, padx=2, pady=2)

        # Row 2: Labels
        ttk.Label(self.groupBox11, text="委託書號").grid(row=2, column=0, padx=2, pady=2)
        ttk.Label(self.groupBox11, text="委託序號").grid(row=2, column=1, padx=2, pady=2)
        ttk.Label(self.groupBox11, text="減量:填要減的量").grid(row=2, column=2, padx=2, pady=2)

        # Row 3: Inputs
        self.txtProxyOrderNo = ttk.Entry(self.groupBox11)
        self.txtProxyOrderNo.grid(row=3, column=0, padx=2, pady=2)

        self.txtProxySeqNo = ttk.Entry(self.groupBox11)
        self.txtProxySeqNo.grid(row=3, column=1, padx=2, pady=2)

        self.txtProxyQty2 = ttk.Entry(self.groupBox11)
        self.txtProxyQty2.grid(row=3, column=2, padx=2, pady=2)

        # Row 1, Col 4: Button
        self.btnProxyFutureAlter = ttk.Button(self.groupBox11, text="ProxyFutureAlter")
        self.btnProxyFutureAlter.grid(row=1, column=4, padx=2, pady=2)

        # === 選擇權proxy委託 groupBox12 ===
        self.groupBox12 = ttk.LabelFrame(self.TabPage3, text="選擇權proxy委託")
        self.groupBox12.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox12.columnconfigure(tuple(range(8)), weight=1)

        # Row 0: Labels
        ttk.Label(self.groupBox12, text="商品代碼").grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="商品年月").grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="履約價").grid(row=0, column=2, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="買/賣權").grid(row=0, column=3, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="買賣別").grid(row=0, column=4, padx=2, pady=2)

        # Row 1: Inputs
        self.txtOptionNo = ttk.Entry(self.groupBox12)
        self.txtOptionNo.grid(row=1, column=0, padx=2, pady=2)

        self.txtOptionYM = ttk.Entry(self.groupBox12)
        self.txtOptionYM.grid(row=1, column=1, padx=2, pady=2)

        self.txtProxyStrike = ttk.Entry(self.groupBox12)
        self.txtProxyStrike.grid(row=1, column=2, padx=2, pady=2)

        self.boxProxyCP = ttk.Combobox(self.groupBox12, values=["Call", "Put"])
        self.boxProxyCP.grid(row=1, column=3, padx=2, pady=2)

        self.boxOptionBS = ttk.Combobox(self.groupBox12, values=["買", "賣"])
        self.boxOptionBS.grid(row=1, column=4, padx=2, pady=2)

        # Row 2: Labels
        ttk.Label(self.groupBox12, text="委託條件").grid(row=2, column=0, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="倉別").grid(row=2, column=1, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="委託價").grid(row=2, column=2, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="委託量").grid(row=2, column=3, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="當沖與否").grid(row=2, column=4, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="盤別").grid(row=2, column=5, padx=2, pady=2)
        ttk.Label(self.groupBox12, text="委價類別").grid(row=2, column=6, padx=2, pady=2)

        # Row 3: Inputs
        self.boxOptionCOND = ttk.Combobox(self.groupBox12, values=["ROD", "IOC", "FOK"])
        self.boxOptionCOND.grid(row=3, column=0, padx=2, pady=2)

        self.boxORDERType = ttk.Combobox(self.groupBox12, values=["新倉", "平倉", "自動"])
        self.boxORDERType.grid(row=3, column=1, padx=2, pady=2)

        self.txtOptionPrice = ttk.Entry(self.groupBox12)
        self.txtOptionPrice.grid(row=3, column=2, padx=2, pady=2)

        self.txtOptionQty = ttk.Entry(self.groupBox12)
        self.txtOptionQty.grid(row=3, column=3, padx=2, pady=2)

        self.boxOptionDayTrade = ttk.Combobox(self.groupBox12, values=["非當沖", "當沖"])
        self.boxOptionDayTrade.grid(row=3, column=4, padx=2, pady=2)

        self.boxPreOrder = ttk.Combobox(self.groupBox12, values=["盤中", "T盤預約"])
        self.boxPreOrder.grid(row=3, column=5, padx=2, pady=2)

        self.boxPriceFlag = ttk.Combobox(self.groupBox12, values=["市價單", "限價單", "範圍市價"])
        self.boxPriceFlag.grid(row=3, column=6, padx=2, pady=2)

        # Row 3, Col 7: Button
        self.btnSendProxyOptionOrder = ttk.Button(self.groupBox12, text="SendProxyOptionOrder")
        self.btnSendProxyOptionOrder.grid(row=3, column=7, padx=2, pady=2)

        # === 選擇權proxy複式單 groupBox13 ===
        self.groupBox13 = ttk.LabelFrame(self.TabPage3, text="選擇權proxy複式單")
        self.groupBox13.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox13.columnconfigure(tuple(range(8)), weight=1)

        # Row 0
        tk.Label(self.groupBox13, text="商品代碼1").grid(row=0, column=0)
        tk.Label(self.groupBox13, text="商品年月1").grid(row=0, column=1)
        tk.Label(self.groupBox13, text="履約價1").grid(row=0, column=2)
        tk.Label(self.groupBox13, text="買/賣權1").grid(row=0, column=3)
        tk.Label(self.groupBox13, text="買賣別1").grid(row=0, column=4)

        # Row 1
        self.txtOptionNo1 = tk.Entry(self.groupBox13)
        self.txtOptionNo1.grid(row=1, column=0)

        self.txtProxyYM1 = tk.Entry(self.groupBox13)
        self.txtProxyYM1.grid(row=1, column=1)

        self.txtProxyStrike1 = tk.Entry(self.groupBox13)
        self.txtProxyStrike1.grid(row=1, column=2)

        self.boxProxyCP1 = ttk.Combobox(self.groupBox13, values=["Call", "Put"], state="readonly")
        self.boxProxyCP1.grid(row=1, column=3)

        self.boxProxyBS1 = ttk.Combobox(self.groupBox13, values=["買", "賣"], state="readonly")
        self.boxProxyBS1.grid(row=1, column=4)

        # Row 2
        tk.Label(self.groupBox13, text="商品代碼2").grid(row=2, column=0)
        tk.Label(self.groupBox13, text="商品年月2").grid(row=2, column=1)
        tk.Label(self.groupBox13, text="履約價2").grid(row=2, column=2)
        tk.Label(self.groupBox13, text="買/賣權2").grid(row=2, column=3)
        tk.Label(self.groupBox13, text="買賣別2").grid(row=2, column=4)

        # Row 3
        self.txtOptionNo2 = tk.Entry(self.groupBox13)
        self.txtOptionNo2.grid(row=3, column=0)

        self.txtProxyYM2 = tk.Entry(self.groupBox13)
        self.txtProxyYM2.grid(row=3, column=1)

        self.txtProxyStrike2 = tk.Entry(self.groupBox13)
        self.txtProxyStrike2.grid(row=3, column=2)

        self.boxProxyCP2 = ttk.Combobox(self.groupBox13, values=["Call", "Put"], state="readonly")
        self.boxProxyCP2.grid(row=3, column=3)

        self.boxProxyBS2 = ttk.Combobox(self.groupBox13, values=["買", "賣"], state="readonly")
        self.boxProxyBS2.grid(row=3, column=4)

        # Row 4
        tk.Label(self.groupBox13, text="委託條件").grid(row=4, column=0)
        tk.Label(self.groupBox13, text="倉別").grid(row=4, column=1)
        tk.Label(self.groupBox13, text="委託價").grid(row=4, column=2)
        tk.Label(self.groupBox13, text="委託量").grid(row=4, column=3)
        tk.Label(self.groupBox13, text="當沖與否").grid(row=4, column=4)
        tk.Label(self.groupBox13, text="盤別").grid(row=4, column=5)
        tk.Label(self.groupBox13, text="委價類別").grid(row=4, column=6)

        # Row 5
        self.boxOptionCOND2 = ttk.Combobox(self.groupBox13, values=["", "IOC", "FOK"], state="readonly")
        self.boxOptionCOND2.grid(row=5, column=0)

        self.boxORDERType2 = ttk.Combobox(self.groupBox13, values=["新倉", "平倉", "自動"], state="readonly")
        self.boxORDERType2.grid(row=5, column=1)

        self.txtOptionPrice2 = tk.Entry(self.groupBox13)
        self.txtOptionPrice2.grid(row=5, column=2)

        self.txtOptionQty2 = tk.Entry(self.groupBox13)
        self.txtOptionQty2.grid(row=5, column=3)

        self.boxDayTrade2 = ttk.Combobox(self.groupBox13, values=["非當沖", "當沖"], state="readonly")
        self.boxDayTrade2.grid(row=5, column=4)

        self.boxPreOrder2 = ttk.Combobox(self.groupBox13, values=["盤中", "T盤預約"], state="readonly")
        self.boxPreOrder2.grid(row=5, column=5)

        self.boxPriceFlag2 = ttk.Combobox(self.groupBox13, values=["市價單", "限價單", "範圍市價"], state="readonly")
        self.boxPriceFlag2.grid(row=5, column=6)

        self.btnSendProxyDuplexOrder = ttk.Button(self.groupBox13, text="SendProxyDuplexOrder")
        self.btnSendProxyDuplexOrder.grid(row=5, column=7)
        
        # groupBox14: 選擇權Proxy刪改單
        self.groupBox14 = ttk.LabelFrame(self.TabPage3, text="選擇權Proxy刪改單")
        self.groupBox14.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox14.columnconfigure(tuple(range(4)), weight=1)

        # Row 0 - Labels for row 1
        ttk.Label(self.groupBox14, text="委託類別").grid(row=0, column=0)
        ttk.Label(self.groupBox14, text="委託條件").grid(row=0, column=1)
        ttk.Label(self.groupBox14, text="盤別").grid(row=0, column=2)
        ttk.Label(self.groupBox14, text="改價:委託價").grid(row=0, column=3)

        # Row 1 - Inputs
        self.boxProxyORDERType3 = ttk.Combobox(self.groupBox14, values=["刪單", "減量", "改價"])
        self.boxProxyORDERType3.grid(row=1, column=0, padx=5, pady=5)

        self.boxProxyCOND3 = ttk.Combobox(self.groupBox14, values=["ROD", "IOC", "FOK"])
        self.boxProxyCOND3.grid(row=1, column=1, padx=5, pady=5)

        self.boxProxyPreOrder3 = ttk.Combobox(self.groupBox14, values=["盤中", "T盤預約"])
        self.boxProxyPreOrder3.grid(row=1, column=2, padx=5, pady=5)

        self.txtProxyPrice3 = ttk.Entry(self.groupBox14)
        self.txtProxyPrice3.grid(row=1, column=3, padx=5, pady=5)

        # Row 2 - Labels for row 3
        ttk.Label(self.groupBox14, text="委託書號").grid(row=2, column=0)
        ttk.Label(self.groupBox14, text="委託序號").grid(row=2, column=1)
        ttk.Label(self.groupBox14, text="減量:填要減的量").grid(row=2, column=2)

        # Row 3 - Inputs and button
        self.txtProxyOrderNo3 = ttk.Entry(self.groupBox14)
        self.txtProxyOrderNo3.grid(row=3, column=0, padx=5, pady=5)

        self.txtProxySeqNo3 = ttk.Entry(self.groupBox14)
        self.txtProxySeqNo3.grid(row=3, column=1, padx=5, pady=5)

        self.txtProxyQty3 = ttk.Entry(self.groupBox14)
        self.txtProxyQty3.grid(row=3, column=2, padx=5, pady=5)

        self.btnProxyOptionAlter = ttk.Button(self.groupBox14, text="ProxyOptionAlter")
        self.btnProxyOptionAlter.grid(row=3, column=3, padx=5, pady=5)

        # groupBox15: 海期proxy委託
        self.groupBox15 = ttk.LabelFrame(self.TabPage4, text="海期proxy委託")
        self.groupBox15.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox15.columnconfigure(tuple(range(10)), weight=1)

        # Row 0 - Labels for Row 1
        ttk.Label(self.groupBox15, text="交易所代號").grid(row=0, column=0)
        ttk.Label(self.groupBox15, text="商品代號").grid(row=0, column=1)
        ttk.Label(self.groupBox15, text="商品年月").grid(row=0, column=2)
        ttk.Label(self.groupBox15, text="委託價").grid(row=0, column=3)
        ttk.Label(self.groupBox15, text="委託價分子").grid(row=0, column=4)
        ttk.Label(self.groupBox15, text="委託價分母").grid(row=0, column=5)
        ttk.Label(self.groupBox15, text="觸發價").grid(row=0, column=6)
        ttk.Label(self.groupBox15, text="觸發價分子").grid(row=0, column=7)
        ttk.Label(self.groupBox15, text="委託量").grid(row=0, column=8)

        # Row 1 - Text entries + button
        self.txtProxyTradeNo = ttk.Entry(self.groupBox15)
        self.txtProxyTradeNo.grid(row=1, column=0, padx=5, pady=5)

        self.txtOFutureNo = ttk.Entry(self.groupBox15)
        self.txtOFutureNo.grid(row=1, column=1, padx=5, pady=5)

        self.txtProxyYearMonth = ttk.Entry(self.groupBox15)
        self.txtProxyYearMonth.grid(row=1, column=2, padx=5, pady=5)

        self.txtProxyOrder = ttk.Entry(self.groupBox15)
        self.txtProxyOrder.grid(row=1, column=3, padx=5, pady=5)

        self.txtProxyOrderNumerator = ttk.Entry(self.groupBox15)
        self.txtProxyOrderNumerator.grid(row=1, column=4, padx=5, pady=5)

        self.txtProxyOrderDeno = ttk.Entry(self.groupBox15)
        self.txtProxyOrderDeno.grid(row=1, column=5, padx=5, pady=5)

        self.txtProxyTrigger = ttk.Entry(self.groupBox15)
        self.txtProxyTrigger.grid(row=1, column=6, padx=5, pady=5)

        self.txtProxyTriggerNumerator = ttk.Entry(self.groupBox15)
        self.txtProxyTriggerNumerator.grid(row=1, column=7, padx=5, pady=5)

        self.txtOFQty = ttk.Entry(self.groupBox15)
        self.txtOFQty.grid(row=1, column=8, padx=5, pady=5)

        self.btnSendOverseaFutureProxyOrder = ttk.Button(self.groupBox15, text="SendOverseaFutureProxyOrder")
        self.btnSendOverseaFutureProxyOrder.grid(row=1, column=9, padx=5, pady=5)

        # Row 2 - Labels for Row 3
        ttk.Label(self.groupBox15, text="買賣別").grid(row=2, column=0)
        ttk.Label(self.groupBox15, text="倉別").grid(row=2, column=1)
        ttk.Label(self.groupBox15, text="當沖與否").grid(row=2, column=2)
        ttk.Label(self.groupBox15, text="委託類型").grid(row=2, column=3)
        ttk.Label(self.groupBox15, text="委託條件").grid(row=2, column=4)
        ttk.Label(self.groupBox15, text="商品年月( 遠月)").grid(row=2, column=5)

        # Row 3 - Comboboxes + second button
        self.boxOFBS = ttk.Combobox(self.groupBox15, values=["買", "賣"])
        self.boxOFBS.grid(row=3, column=0, padx=5, pady=5)

        self.boxProxyNewClose = ttk.Combobox(self.groupBox15, values=["新倉"])
        self.boxProxyNewClose.grid(row=3, column=1, padx=5, pady=5)

        self.boxProxyFlag = ttk.Combobox(self.groupBox15, values=["非當沖", "當沖"])
        self.boxProxyFlag.grid(row=3, column=2, padx=5, pady=5)

        self.boxProxySpecialTradeType = ttk.Combobox(
            self.groupBox15,
            values=["LMT  ( 限價 )", "MKT ( 市價 )", "STL   ( 停損限價 )", "STP  ( 停損市價 )"]
        )
        self.boxProxySpecialTradeType.grid(row=3, column=3, padx=5, pady=5)

        self.boxProxyPeriod = ttk.Combobox(self.groupBox15, values=["ROD", "FOK", "IOC"])
        self.boxProxyPeriod.grid(row=3, column=4, padx=5, pady=5)

        self.txtProxyYearMonth2 = ttk.Entry(self.groupBox15)
        self.txtProxyYearMonth2.grid(row=3, column=5, padx=5, pady=5)

        self.btnSendOverseaFutureSpreadProxyOrder = ttk.Button(self.groupBox15, text="SendOverseaFutureSpreadProxyOrder")
        self.btnSendOverseaFutureSpreadProxyOrder.grid(row=3, column=6, padx=5, pady=5)

        # === 海期選proxy刪改單 groupBox17 ===
        self.groupBox17 = ttk.LabelFrame(self.TabPage4, text="海期選proxy刪改單")
        self.groupBox17.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox17.columnconfigure(tuple(range(8)), weight=1)

        # 第一行 label
        labels1 = ["交易所代號", "商品代號", "商品年月", "倉別", "委託類型", "委託條件", "異動項目", "價差單商品年月(遠月)"]
        for i, text in enumerate(labels1):
            ttk.Label(self.groupBox17, text=text).grid(row=0, column=i)

        # 第一行 entries/comboboxes
        self.txtProxyTradeNo2 = ttk.Entry(self.groupBox17)
        self.txtProxyTradeNo2.grid(row=1, column=0)
        self.txtOFutureNo2 = ttk.Entry(self.groupBox17)
        self.txtOFutureNo2.grid(row=1, column=1)
        self.txtProxyYearMonth3 = ttk.Entry(self.groupBox17)
        self.txtProxyYearMonth3.grid(row=1, column=2)

        self.boxProxyNewClose2 = ttk.Combobox(self.groupBox17, values=["新倉"])
        self.boxProxyNewClose2.grid(row=1, column=3)

        self.boxProxySpecialTradeType2 = ttk.Combobox(self.groupBox17, values=["LMT ( 限價 )"])
        self.boxProxySpecialTradeType2.grid(row=1, column=4)

        self.boxProxyPeriod2 = ttk.Combobox(self.groupBox17, values=["ROD"])
        self.boxProxyPeriod2.grid(row=1, column=5)

        self.boxFunCode = ttk.Combobox(self.groupBox17, values=["刪單", "減量", "改價"])
        self.boxFunCode.grid(row=1, column=6)

        self.txtProxyYearMonth4 = ttk.Entry(self.groupBox17)
        self.txtProxyYearMonth4.grid(row=1, column=7)

        # 第二行 label
        labels2 = ["委託書號", "委託序號", "改價:委託價", "委託價分子", "委託價分母", "改量：輸入欲減少的數量", "市場別(OF/OO)"]
        for i, text in enumerate(labels2):
            ttk.Label(self.groupBox17, text=text).grid(row=2, column=i)

        # 第二行 entries/comboboxes
        self.txtOFBookNo = ttk.Entry(self.groupBox17)
        self.txtOFBookNo.grid(row=3, column=0)
        self.txtSeqNo4 = ttk.Entry(self.groupBox17)
        self.txtSeqNo4.grid(row=3, column=1)
        self.txtProxyOrder2 = ttk.Entry(self.groupBox17)
        self.txtProxyOrder2.grid(row=3, column=2)
        self.txtProxyOrderNumerator2 = ttk.Entry(self.groupBox17)
        self.txtProxyOrderNumerator2.grid(row=3, column=3)
        self.txtProxyPriceD = ttk.Entry(self.groupBox17)
        self.txtProxyPriceD.grid(row=3, column=4)
        self.txtOFQty2 = ttk.Entry(self.groupBox17)
        self.txtOFQty2.grid(row=3, column=5)

        self.BoxAlterSpread = ttk.Combobox(self.groupBox17, values=["0海期", "1海期價差", "2海選"])
        self.BoxAlterSpread.grid(row=3, column=6)

        # 第三行 label
        ttk.Label(self.groupBox17, text="履約價").grid(row=4, column=0)
        ttk.Label(self.groupBox17, text="CALLPUT").grid(row=4, column=1)

        # 第三行 entries/combobox + button
        self.txt_Strike_proxy = ttk.Entry(self.groupBox17)
        self.txt_Strike_proxy.grid(row=5, column=0)

        self.boxCallPutAlter = ttk.Combobox(self.groupBox17, values=["CALL", "PUT"])
        self.boxCallPutAlter.grid(row=5, column=1)

        self.btnSendOverseaFutureProxyAlter = ttk.Button(
            self.groupBox17, text="SendOverseaFutureProxyAlter")
        self.btnSendOverseaFutureProxyAlter.grid(row=5, column=2)

        # === 海選proxy委託 groupBox18 ===
        self.groupBox18 = ttk.LabelFrame(self.TabPage5, text="海選proxy委託")
        self.groupBox18.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox18.columnconfigure(tuple(range(9)), weight=1)

        # 第一列 label
        labels = [
            "交易所代號", "商品代號", "商品年月", "履約價", "CALLPUT",
            "委託量", "委託價", "委託價分子", "委託價分母"
        ]
        for i, text in enumerate(labels):
            ttk.Label(self.groupBox18, text=text).grid(row=0, column=i)

        # 第一列輸入欄位
        self.txtOOTradeNo = ttk.Entry(self.groupBox18)
        self.txtOOTradeNo.grid(row=1, column=0)

        self.txtOONo = ttk.Entry(self.groupBox18)
        self.txtOONo.grid(row=1, column=1)

        self.txtOOYM = ttk.Entry(self.groupBox18)
        self.txtOOYM.grid(row=1, column=2)

        self.txtProxyStrikePrice = ttk.Entry(self.groupBox18)
        self.txtProxyStrikePrice.grid(row=1, column=3)

        self.boxProxyCallPut = ttk.Combobox(self.groupBox18, values=["CALL", "PUT"])
        self.boxProxyCallPut.grid(row=1, column=4)

        self.txtOOQty = ttk.Entry(self.groupBox18)
        self.txtOOQty.grid(row=1, column=5)

        self.txtOOPrice = ttk.Entry(self.groupBox18)
        self.txtOOPrice.grid(row=1, column=6)

        self.txtOONumerator = ttk.Entry(self.groupBox18)
        self.txtOONumerator.grid(row=1, column=7)

        self.txtOODeno = ttk.Entry(self.groupBox18)
        self.txtOODeno.grid(row=1, column=8)

        # 第二列 label
        labels2 = [
            "買賣別", "倉別", "當沖與否", "委託條件", "委託類型",
            "觸發價", "觸發價分子", ""
        ]
        for i, text in enumerate(labels2):
            ttk.Label(self.groupBox18, text=text).grid(row=2, column=i)

        # 第二列輸入欄位
        self.boxOOBS = ttk.Combobox(self.groupBox18, values=["買", "賣"])
        self.boxOOBS.grid(row=3, column=0)

        self.boxOONewClose = ttk.Combobox(self.groupBox18, values=["新倉", "平倉"])
        self.boxOONewClose.grid(row=3, column=1)

        self.boxOOFlag = ttk.Combobox(self.groupBox18, values=["非當沖", "當沖"])
        self.boxOOFlag.grid(row=3, column=2)

        self.boxOOPeriod = ttk.Combobox(self.groupBox18, values=["ROD"])
        self.boxOOPeriod.grid(row=3, column=3)

        self.boxOOSpecialTradeType = ttk.Combobox(self.groupBox18, values=["LMT (限價)"])
        self.boxOOSpecialTradeType.grid(row=3, column=4)

        self.txtOOTrigger = ttk.Entry(self.groupBox18)
        self.txtOOTrigger.grid(row=3, column=5)

        self.txtOOTriggerNumerator = ttk.Entry(self.groupBox18)
        self.txtOOTriggerNumerator.grid(row=3, column=6)

        self.btnSendOverseaOptionProxyOrder = ttk.Button(
            self.groupBox18, text="SendOverseaOptionProxyOrder"
        )
        self.btnSendOverseaOptionProxyOrder.grid(row=3, column=7, padx=5, pady=5)


        # === proxy複委託 groupBox19 ===
        self.groupBox19 = ttk.LabelFrame(self.TabPage6, text="proxy複委託")
        self.groupBox19.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox19.columnconfigure(tuple(range(7)), weight=1)

        # 第一列 labels（專戶別與扣款幣別）
        labels1 = ["專戶別", "扣款幣別順序：1.", "2.", "3."]
        for i, text in enumerate(labels1):
            ttk.Label(self.groupBox19, text=text).grid(row=0, column=i)

        # 第一列 widgets
        self.boxProxyAccountType = ttk.Combobox(self.groupBox19, values=["外幣專戶", "台幣專戶"])
        self.boxProxyAccountType.grid(row=1, column=0)

        currency_options = ["HKD", "NTD", "USD", "JPY", "SGD", "EUR", "AUD", "CNY", "GBP"]

        self.boxProxyCurrency1 = ttk.Combobox(self.groupBox19, values=currency_options)
        self.boxProxyCurrency1.grid(row=1, column=1)

        self.boxProxyCurrency2 = ttk.Combobox(self.groupBox19, values=currency_options)
        self.boxProxyCurrency2.grid(row=1, column=2)

        self.boxProxyCurrency3 = ttk.Combobox(self.groupBox19, values=currency_options)
        self.boxProxyCurrency3.grid(row=1, column=3)

        # 第二列 labels（市場別到庫存別）
        labels2 = ["市場別", "商品代碼", "買賣別", "委託價", "委託量", "庫存別"]
        for i, text in enumerate(labels2):
            ttk.Label(self.groupBox19, text=text).grid(row=2, column=i)

        # 第二列 widgets
        exchange_options = ["美股", "港股", "日股", "新加坡", "新(幣)加坡", "滬股", "深股"]
        self.boxProxyExchange = ttk.Combobox(self.groupBox19, values=exchange_options)
        self.boxProxyExchange.grid(row=3, column=0)

        self.txtProxyOStockNo = ttk.Entry(self.groupBox19)
        self.txtProxyOStockNo.grid(row=3, column=1)

        self.boxProxyBidAsk = ttk.Combobox(self.groupBox19, values=["買", "賣"])
        self.boxProxyBidAsk.grid(row=3, column=2)

        self.txtProxyPrice = ttk.Entry(self.groupBox19)
        self.txtProxyPrice.grid(row=3, column=3)

        self.txtProxyQty = ttk.Entry(self.groupBox19)
        self.txtProxyQty.grid(row=3, column=4)

        trade_type_options = ["美股:一般定股", "美股:定額", "其他股市:一般"]
        self.boxProxyTradeType = ttk.Combobox(self.groupBox19, values=trade_type_options)
        self.boxProxyTradeType.grid(row=3, column=5)

        self.btnSendForeignStockProxyOrder = ttk.Button(
            self.groupBox19, text="SendForeignStockProxyOrder"
        )
        self.btnSendForeignStockProxyOrder.grid(row=3, column=6, padx=5, pady=5)

        # === 複委託proxy取消委託 groupBox20 ===
        self.groupBox20 = ttk.LabelFrame(self.TabPage6, text="複委託proxy取消委託")
        self.groupBox20.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox20.columnconfigure(tuple(range(5)), weight=1)

        # 標籤列（第0列）
        labels = ["市場別", "商品代碼", "委託書號刪單", "委託序號刪單"]
        for i, text in enumerate(labels):
            ttk.Label(self.groupBox20, text=text).grid(row=0, column=i, padx=5, pady=2)

        # 控制元件列（第1列）
        exchange_options = ["美股", "港股", "日股", "新加坡", "新(幣)加坡", "滬股", "深股"]
        self.boxProxyCancelExchange = ttk.Combobox(self.groupBox20, values=exchange_options)
        self.boxProxyCancelExchange.grid(row=1, column=0, padx=5, pady=2)

        self.txtProxyOStockNo2 = ttk.Entry(self.groupBox20)
        self.txtProxyOStockNo2.grid(row=1, column=1, padx=5, pady=2)

        self.txtProxyCancelBookNo = ttk.Entry(self.groupBox20)
        self.txtProxyCancelBookNo.grid(row=1, column=2, padx=5, pady=2)

        self.txtProxyCancelSeqNo = ttk.Entry(self.groupBox20)
        self.txtProxyCancelSeqNo.grid(row=1, column=3, padx=5, pady=2)

        self.btnProxyCancelForeignOrderBySeqNo = ttk.Button(
            self.groupBox20, text="Cancel ProxyForeignOrder"
        )
        self.btnProxyCancelForeignOrderBySeqNo.grid(row=1, column=4, padx=5, pady=2)

        # === 圈存查詢 groupBox28 ===
        self.groupBox28 = ttk.LabelFrame(self.TabPage25, text="圈存查詢")
        self.groupBox28.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox28.columnconfigure(tuple(range(7)), weight=1)

        ForeignBlocknFunc = ["0:台幣", "1:外幣"]
        self.comboBoxGetForeignBlocknFunc = ttk.Combobox(self.groupBox28, values=ForeignBlocknFunc)
        self.comboBoxGetForeignBlocknFunc.grid(row=0, column=0, padx=5, pady=2)

        self.buttonGetForeignBlock = ttk.Button(self.groupBox28, text="GetForeignBlock")
        self.buttonGetForeignBlock.grid(row=0, column=1, padx=5, pady=2)

        # === 國內外保證金互轉申請 groupBox29 ===
        self.groupBox29 = ttk.LabelFrame(self.TabPage24, text="國內外保證金互轉申請")
        self.groupBox29.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox29.columnconfigure(tuple(range(7)), weight=1)

        ttk.Label(self.groupBox29, text='轉出帳號：').grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.groupBox29, text='轉入帳號：').grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(self.groupBox29, text='幣別：').grid(row=0, column=4, padx=5, pady=5)
        ttk.Label(self.groupBox29, text='轉帳金額').grid(row=0, column=5, padx=5, pady=5)
        ttk.Label(self.groupBox29, text='出金密碼檢核：').grid(row=0, column=6, padx=5, pady=5)

        boxTypeOutWithDraw = ["0:國內", "1:國外"]
        self.boxTypeOut = ttk.Combobox(self.groupBox29, values=boxTypeOutWithDraw)
        self.boxTypeOut.grid(row=1, column=0, padx=5, pady=2)

        self.textBoxAccountOut = ttk.Entry(self.groupBox29)
        self.textBoxAccountOut.grid(row=1, column=1, padx=5, pady=2)

        boxTypeInWithDraw = ["0:國內", "1:國外"]
        self.boxTypeIn = ttk.Combobox(self.groupBox29, values=boxTypeInWithDraw)
        self.boxTypeIn.grid(row=1, column=2, padx=5, pady=2)

        self.textBoxAccountIn = ttk.Entry(self.groupBox29)
        self.textBoxAccountIn.grid(row=1, column=3, padx=5, pady=2)

        boxCurrencyWithDraw = ["AUD", "EUR", "GBP", "HKD", "JPY", "NTD", "NZD", "RMB", "USD", "ZAR"]
        self.boxCurrency = ttk.Combobox(self.groupBox29, values=boxCurrencyWithDraw)
        self.boxCurrency.grid(row=1, column=4, padx=5, pady=2)
     
        self.txtDollars = ttk.Entry(self.groupBox29)
        self.txtDollars.grid(row=1, column=5, padx=5, pady=2)

        self.txtPWD = ttk.Entry(self.groupBox29)
        self.txtPWD.grid(row=1, column=6, padx=5, pady=2)

        self.btnSend = ttk.Button(self.groupBox29, text="執行互轉")
        self.btnSend.grid(row=1, column=7, padx=5, pady=2)

        # === 部位互抵(大小微台、大小電金) groupBox30 ===
        self.groupBox30 = ttk.LabelFrame(self.TabPage23, text="部位互抵(大小微台、大小電金)")
        self.groupBox30.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.groupBox30.columnconfigure(tuple(range(7)), weight=1)

        ttk.Label(self.groupBox30, text='商品').grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.groupBox30, text='年月').grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.groupBox30, text='買賣別').grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(self.groupBox30, text='大台電金委託量').grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(self.groupBox30, text='小台委託量').grid(row=0, column=4, padx=5, pady=5)
        ttk.Label(self.groupBox30, text='微型委託量').grid(row=0, column=5, padx=5, pady=5)

        boxTypeCommodityBoxNew = ["0:大抵微", "1:小抵微", "2:大小抵微", "3:大抵小微", "4:小抵大微", "5:大抵小", "6:大小電", "7:大小金"]
        self.CommodityBoxNew = ttk.Combobox(self.groupBox30, values=boxTypeCommodityBoxNew)
        self.CommodityBoxNew.grid(row=1, column=0, padx=5, pady=2)

        self.txtOffsetNewYearMonth = ttk.Entry(self.groupBox30)
        self.txtOffsetNewYearMonth.grid(row=1, column=1, padx=5, pady=2)

        boxTypeboxOffsetNewBuySell = ["買", "賣"]
        self.boxOffsetNewBuySell = ttk.Combobox(self.groupBox30, values=boxTypeboxOffsetNewBuySell)
        self.boxOffsetNewBuySell.grid(row=1, column=2, padx=5, pady=2)

        self.txtOffsetNewQty = ttk.Entry(self.groupBox30)
        self.txtOffsetNewQty.grid(row=1, column=3, padx=5, pady=2)
        
        self.txtOffsetNewQty_2 = ttk.Entry(self.groupBox30)
        self.txtOffsetNewQty_2.grid(row=1, column=4, padx=5, pady=2)
        
        self.txtOffsetNewQty_3 = ttk.Entry(self.groupBox30)
        self.txtOffsetNewQty_3.grid(row=1, column=5, padx=5, pady=2)

        self.btnSendTFOffset = ttk.Button(self.groupBox30, text="btnSendTFOffset")
        self.btnSendTFOffset.grid(row=1, column=6, padx=5, pady=2)

class Reply(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, text="回報查詢", *args, **kwargs)
        
        # 建立 tabControl2
        self.tabControl2 = ttk.Notebook(self)
        self.tabControl2.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 第一頁：委託回報
        self.tabPage7 = ttk.Frame(self.tabControl2)
        self.tabControl2.add(self.tabPage7, text="委託回報")

        self.listOnNewOrderData = tk.Listbox(self.tabPage7, width=120, height=20)
        self.listOnNewOrderData.pack(padx=10, pady=10, fill="both", expand=True)

        # 第二頁：成交回報
        self.tabPage8 = ttk.Frame(self.tabControl2)
        self.tabControl2.add(self.tabPage8, text="成交回報")

        self.listOnNewFulfillData = tk.Listbox(self.tabPage8, width=120, height=20)
        self.listOnNewFulfillData.pack(padx=10, pady=10, fill="both", expand=True)

        # 讓 tabControl2 可以隨視窗調整大小
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

class Quote(ttk.LabelFrame):
    def UpdateBest5Grid(self, marketNo, bids, bidQtys, asks, askQtys,
                    extendBid, extendBidQty, extendAsk, extendAskQty, simulate):
        kMarketPrice = 0
        dDigitNum = 100.00  # 預設價格除數（兩位小數）

        # 文字顏色區分：一般 or 試算揭示
        tag = "simulate" if simulate == 1 else "normal"
        self.GridBest5Ask.tag_configure("simulate", foreground="gray")
        self.GridBest5Bid.tag_configure("simulate", foreground="gray")
        self.GridBest5Ask.tag_configure("normal", foreground="black")
        self.GridBest5Bid.tag_configure("normal", foreground="black")

        # 清空內部資料結構
        self.m_dtBest5Ask = []
        self.m_dtBest5Bid = []

        # 填入 Ask（賣）
        for i in range(5):
            price = "M" if asks[i] == kMarketPrice else f"{asks[i] / dDigitNum:.2f}"
            qty = askQtys[i]
            self.m_dtBest5Ask.append({
                "m_nAskQty": qty,
                "m_nAsk": price
            })

        # 填入 Bid（買）
        for i in range(5):
            price = "M" if bids[i] == kMarketPrice else f"{bids[i] / dDigitNum:.2f}"
            qty = bidQtys[i]
            self.m_dtBest5Bid.append({
                "m_nBidQty": qty,
                "m_nBid": price
            })

        # 更新 UI
        self.BindDataGrids()
    
    def UpdateBest10Grid(self, bids, bidQtys, asks, askQtys):
        # 清空內部資料結構
        self.m_dtBest10Ask = []
        self.m_dtBest10Bid = []

        # 填入 Ask（賣）
        for i in range(10):
            price = f"{asks[i]}"
            qty = askQtys[i]
            self.m_dtBest10Ask.append({
                "m_nAskQty": qty,
                "m_nAsk": price
            })

        # 填入 Bid（買）
        for i in range(10):
            price = f"{bids[i]}"
            qty = bidQtys[i]
            self.m_dtBest10Bid.append({
                "m_nBidQty": qty,
                "m_nBid": price
            })

        # 更新 UI
        self.BindDataGrids10OS()
    
    def UpdateBest10Grid2(self, bids, bidQtys, asks, askQtys):
        # 清空內部資料結構
        self.m_dtBest10Ask2 = []
        self.m_dtBest10Bid2 = []

        # 填入 Ask（賣）
        for i in range(10):
            price = f"{asks[i]}"
            qty = askQtys[i]
            self.m_dtBest10Ask2.append({
                "m_nAskQty": qty,
                "m_nAsk": price
            })

        # 填入 Bid（買）
        for i in range(10):
            price = f"{bids[i]}"
            qty = bidQtys[i]
            self.m_dtBest10Bid2.append({
                "m_nBidQty": qty,
                "m_nBid": price
            })

        # 更新 UI
        self.BindDataGrids10OO()

    def CreateBest5Table(self):
        self.best5_ask_columns = ["m_nAskQty", "m_nAsk"]
        self.best5_bid_columns = ["m_nBidQty", "m_nBid"]
        return []
    
    def CreateBest10Table(self):
        self.best10_ask_columns = ["m_nAskQty", "m_nAsk"]
        self.best10_bid_columns = ["m_nBidQty", "m_nBid"]
        return []

    def BindDataGrids(self):
        # 清除舊資料
        for row in self.GridBest5Ask.get_children():
            self.GridBest5Ask.delete(row)
        for row in self.GridBest5Bid.get_children():
            self.GridBest5Bid.delete(row)

        # 加入新資料：Ask
        for row in self.m_dtBest5Ask:
            self.GridBest5Ask.insert("", "end", values=(row["m_nAskQty"], row["m_nAsk"]))

        # 加入新資料：Bid
        for row in self.m_dtBest5Bid:
            self.GridBest5Bid.insert("", "end", values=(row["m_nBidQty"], row["m_nBid"]))
    
    def BindDataGrids10OS(self):
        # 清除舊資料
        for row in self.GridBest10Ask.get_children():
            self.GridBest10Ask.delete(row)
        for row in self.GridBest10Bid.get_children():
            self.GridBest10Bid.delete(row)

        # 加入新資料：Ask
        for row in self.m_dtBest10Ask:
            self.GridBest10Ask.insert("", "end", values=(row["m_nAskQty"], row["m_nAsk"]))

        # 加入新資料：Bid
        for row in self.m_dtBest10Bid:
            self.GridBest10Bid.insert("", "end", values=(row["m_nBidQty"], row["m_nBid"]))
    
    def BindDataGrids10OO(self):
        # 清除舊資料
        for row in self.GridBest10Ask2.get_children():
            self.GridBest10Ask2.delete(row)
        for row in self.GridBest10Bid2.get_children():
            self.GridBest10Bid2.delete(row)

        # 加入新資料：Ask
        for row in self.m_dtBest10Ask2:
            self.GridBest10Ask2.insert("", "end", values=(row["m_nAskQty"], row["m_nAsk"]))

        # 加入新資料：Bid
        for row in self.m_dtBest10Bid2:
            self.GridBest10Bid2.insert("", "end", values=(row["m_nBidQty"], row["m_nBid"]))

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, text="報價", *args, **kwargs)

        # 對應 C# 的欄位結構
        self.stock_columns = [
            "商品代碼", "名稱",
            "開盤價", "最高", "最低", "成交價", "單量", "昨收價",
            "買價", "買量", "賣價", "賣量", "買盤量", "賣盤量",
            "m_nFutureOI", "總量", "昨量", "漲停", "跌停",
            "m_nCloseS", "m_nTickQtyS", "m_nBidS", "m_nAskS", "m_nOddLotPer",
            "成交時間", "m_sDecimal", "m_sTypeNo","m_cMarketNo"
        ]
        
        # 對應 C# 的欄位結構
        self.stock_columnsOS = [
            "交易所代碼", "交易所名稱",
            "商品代碼", "商品名稱", "開盤價", "最高價", "最低價", "成交價",
            "結算價", "單量", "昨收價", "買價", "買量", "賣價",
            "賣量", "成交量"
        ]

        # 對應 C# 的欄位結構
        self.stock_columnsOO = [
            "交易所代碼", "交易所名稱",
            "商品代碼", "商品名稱", "開盤價", "最高價", "最低價", "成交價",
            "結算價", "單量", "昨收價", "買價", "買量", "賣價",
            "賣量", "成交量"
        ]

        self.best5_ask_columns = ["m_nAskQty", "m_nAsk"]
        self.best5_bid_columns = ["m_nBidQty", "m_nBid"]
        self.best10_ask_columns = ["m_nAskQty", "m_nAsk"]
        self.best10_bid_columns = ["m_nBidQty", "m_nBid"]

        # 建立 TabControl3
        self.tabControl3 = ttk.Notebook(self)
        self.tabControl3.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # TabPage9: 國內行情
        self.tabPage9 = ttk.Frame(self.tabControl3)
        self.tabControl3.add(self.tabPage9, text="國內行情")

        # TabPage10: 海期行情
        self.tabPage10 = ttk.Frame(self.tabControl3)
        self.tabControl3.add(self.tabPage10, text="海期行情")

        # TabPage11: 海選行情
        self.tabPage11 = ttk.Frame(self.tabControl3)
        self.tabControl3.add(self.tabPage11, text="海選行情")

        # 讓 tabControl3 可隨容器拉伸
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # 在 tabPage9 裡建立內嵌的 tabControl4
        self.tabControl4 = ttk.Notebook(self.tabPage9)
        self.tabControl4.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # tabPage12: 即時報價
        self.tabPage12 = ttk.Frame(self.tabControl4)
        self.tabControl4.add(self.tabPage12, text="即時報價")

        # tabPage13: TICKS & BEST5
        self.tabPage13 = ttk.Frame(self.tabControl4)
        self.tabControl4.add(self.tabPage13, text="TICKS & BEST5")

        # 讓 tabPage9 內部的 tabControl4 可以撐開
        self.tabPage9.rowconfigure(0, weight=1)
        self.tabPage9.columnconfigure(0, weight=1)

        # 在 tabPage10 裡建立內嵌的 tabControl5
        self.tabControl5 = ttk.Notebook(self.tabPage10)
        self.tabControl5.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # tabPage15: 即時報價
        self.tabPage15 = ttk.Frame(self.tabControl5)
        self.tabControl5.add(self.tabPage15, text="即時報價")

        # tabPage16: TICKS & BEST10
        self.tabPage16 = ttk.Frame(self.tabControl5)
        self.tabControl5.add(self.tabPage16, text="TICKS & BEST10")

        # 讓 tabPage10 內部的 tabControl5 可以撐開
        self.tabPage10.rowconfigure(0, weight=1)
        self.tabPage10.columnconfigure(0, weight=1)

        # 在 tabPage11 裡建立內嵌的 tabControl6
        self.tabControl6 = ttk.Notebook(self.tabPage11)
        self.tabControl6.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # tabPage19: 即時報價
        self.tabPage19 = ttk.Frame(self.tabControl6)
        self.tabControl6.add(self.tabPage19, text="即時報價")

        # tabPage20: TICKS & BEST10
        self.tabPage20 = ttk.Frame(self.tabControl6)
        self.tabControl6.add(self.tabPage20, text="TICKS & BEST10")

        # 讓 tabPage11 內部的 tabControl6 可以撐開
        self.tabPage11.rowconfigure(0, weight=1)
        self.tabPage11.columnconfigure(0, weight=1)

        # 在 tabPage12 中建立 groupBox21（左上角）
        self.groupBox21 = ttk.LabelFrame(self.tabPage12, text="商品代碼(不支援盤中零股)( 多筆以逗號{,}區隔 )")
        self.groupBox21.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # groupBox21 中的元件
        self.txtStocks = ttk.Entry(self.groupBox21)
        self.txtStocks.insert(0, "TX00,MTX00,6005")
        self.txtStocks.grid(row=0, column=0, padx=5, pady=5)

        self.btnCancelStocks = ttk.Button(self.groupBox21, text="取消")
        self.btnCancelStocks.grid(row=0, column=1, padx=5, pady=5)

        self.btnQueryStocks = ttk.Button(self.groupBox21, text="查詢")
        self.btnQueryStocks.grid(row=0, column=2, padx=5, pady=5)

        # 在 groupBox21 中建立 groupBox3
        self.groupBox3 = ttk.LabelFrame(self.groupBox21, text="商品代碼(支援盤中零股)( 多筆以逗號{,}區隔 )")
        self.groupBox3.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)

        # groupBox3 中的元件

        self.txtStocks2 = ttk.Entry(self.groupBox3)
        self.txtStocks2.insert(0, "6005,2330")
        self.txtStocks2.grid(row=0, column=0, padx=5, pady=5)

        self.btnQueryOddLot = ttk.Button(self.groupBox3, text="零股查詢")
        self.btnQueryOddLot.grid(row=0, column=1, padx=5, pady=5)

        # 可選：設定 tabPage12 的 grid 結構使其能撐開
        self.tabPage12.columnconfigure(0, weight=1)
        self.tabPage12.columnconfigure(1, weight=1)
        self.tabPage12.rowconfigure(0, weight=0)
        
        # ➤ 放入一個固定大小的 Frame
        self.gridStocksFrame = ttk.Frame(self.tabPage12, width=850, height=400)
        self.gridStocksFrame.grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.gridStocksFrame.grid_propagate(False)  # 阻止內部元件撐大 frame

        # ➤ 建立 Treeview（可視欄位總數調整寬度）
        self.gridStocks = ttk.Treeview(self.gridStocksFrame, columns=self.stock_columns, show="headings")

        # ➤ 每欄固定 80 寬
        for col in self.stock_columns:
            self.gridStocks.heading(col, text=col)
            self.gridStocks.column(col, width=80, anchor="center", stretch=False)  # stretch=False 是關鍵！

        # ➤ 水平捲動條
        xscroll = ttk.Scrollbar(self.gridStocksFrame, orient="horizontal", command=self.gridStocks.xview)
        self.gridStocks.configure(xscrollcommand=xscroll.set)

        # ➤ 垂直捲動條
        yscroll = ttk.Scrollbar(self.gridStocksFrame, orient="vertical", command=self.gridStocks.yview)
        self.gridStocks.configure(yscrollcommand=yscroll.set)

        # ➤ 擺進去（不設 sticky 擴張）
        self.gridStocks.grid(row=0, column=0, sticky="nsew")
        xscroll.grid(row=1, column=0, sticky="ew")
        yscroll.grid(row=0, column=1, sticky="ns")

        # ➤ 設定 gridStocksFrame 裡面的排版邏輯
        self.gridStocksFrame.rowconfigure(0, weight=1)
        self.gridStocksFrame.columnconfigure(0, weight=1)

        # ------------------------------
        # (0,0) groupBox22 - LabelFrame
        # ------------------------------
        self.groupBox22 = ttk.LabelFrame(self.tabPage13, text='TICKS & BEST5')
        self.groupBox22.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # → row=0, column=0~5
        ttk.Label(self.groupBox22, text='第幾檔').grid(row=0, column=0, padx=5, pady=5)

        self.txtItemNoQuote = ttk.Entry(self.groupBox22)
        self.txtItemNoQuote.insert(0, "1")
        self.txtItemNoQuote.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.groupBox22, text='商品代碼(僅一檔)').grid(row=0, column=2, padx=2, pady=2)
        self.txtTick = tk.Entry(self.groupBox22, width=10)
        self.txtTick.insert(0, "6005")
        self.txtTick.grid(row=0, column=3, padx=2, pady=2)

        self.btnTicks = ttk.Button(self.groupBox22, text='Request Tick')
        self.btnTicks.grid(row=0, column=4, padx=2, pady=2)

        self.btnTicks_OddLot = ttk.Button(self.groupBox22, text='Request Tick_OddLot')
        self.btnTicks_OddLot.grid(row=0, column=5, padx=2, pady=2)

        self.btnTickStop = ttk.Button(self.groupBox22, text='Stop')
        self.btnTickStop.grid(row=0, column=6, padx=2, pady=2)

        # (0,6) 不含毫秒微秒
        self.chkbox_msms_var = tk.BooleanVar()
        self.chkbox_msms = ttk.Checkbutton(self.groupBox22, text="不含毫秒微秒", variable=self.chkbox_msms_var, command=self.on_chkbox_msms_changed)
        self.chkbox_msms.grid(row=0, column=7, padx=5, pady=5, sticky="w")

        # (0,7) 含試算揭示
        self.chkBoxSimulate_var = tk.BooleanVar()
        self.chkBoxSimulate = ttk.Checkbutton(self.groupBox22, text="含試算揭示", variable=self.chkBoxSimulate_var)
        self.chkBoxSimulate.grid(row=0, column=8, padx=5, pady=5, sticky="w")

        # (0,8) 含市價揭示轉換
        self.Box_M_var = tk.BooleanVar()
        self.Box_M = ttk.Checkbutton(self.groupBox22, text="含市價揭示轉換", variable=self.Box_M_var, command=self.on_Box_M_changed)
        self.Box_M.grid(row=0, column=9, padx=5, pady=5, sticky="w")

        # ------------------------------
        # (1,0) listTicks - Listbox
        # ------------------------------
        self.listTicks = tk.Listbox(self.tabPage13, height=15, width=30)
        self.listTicks.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # ------------------------------
        # (1,1) GridBest5Bid - Treeview
        # ------------------------------
        self.GridBest5Bid = ttk.Treeview(self.tabPage13, columns=self.best5_bid_columns, show="headings", height=10)
        for col in self.best5_bid_columns:
            self.GridBest5Bid.heading(col, text=col)
            self.GridBest5Bid.column(col, width=80, anchor="center")
        self.GridBest5Bid.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # ------------------------------
        # (1,2) GridBest5Ask - Treeview
        # ------------------------------
        self.GridBest5Ask = ttk.Treeview(self.tabPage13, columns=self.best5_ask_columns, show="headings", height=10)
        for col in self.best5_ask_columns:
            self.GridBest5Ask.heading(col, text=col)
            self.GridBest5Ask.column(col, width=80, anchor="center")
        self.GridBest5Ask.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        # 模擬資料綁定
        self.m_dtBest5Bid = self.CreateBest5Table()
        self.m_dtBest5Ask = self.CreateBest5Table()
        self.BindDataGrids()
        
        # 設定 grid 權重
        self.tabPage13.rowconfigure(1, weight=1)
        self.tabPage13.columnconfigure(0, weight=1)
        self.tabPage13.columnconfigure(1, weight=1)
        self.tabPage13.columnconfigure(2, weight=1)

        # tabPage14: StockList
        self.tabPage14 = ttk.Frame(self.tabControl4)
        self.tabControl4.add(self.tabPage14, text="StockList")

        # ------------------------------
        # (0,0) groupBox23 - LabelFrame
        # ------------------------------
        self.groupBox23 = ttk.LabelFrame(self.tabPage14, text='StockList')
        self.groupBox23.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        # → row=0, column=0~4
        ttk.Label(self.groupBox23, text='MarketNo').grid(row=0, column=0, padx=2, pady=2)
        self.MarketNo_txt = tk.Entry(self.groupBox23, width=10)
        self.MarketNo_txt.insert(0, "0") # 0:上市
        self.MarketNo_txt.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(self.groupBox23, text='TypeNo').grid(row=0, column=2, padx=2, pady=2)
        self.TypeNo_txt = tk.Entry(self.groupBox23, width=10)
        self.TypeNo_txt.insert(0, "1") # 1:水泥產業
        self.TypeNo_txt.grid(row=0, column=3, padx=2, pady=2)

        self.RequestStockListBtn = ttk.Button(self.groupBox23, text='RequestStockList')
        self.RequestStockListBtn.grid(row=0, column=4, padx=2, pady=2)

        # → row=1, column=0
        self.StockList = tk.Listbox(self.tabPage14, width=100, height=50)
        self.StockList.grid(row=1, column=0, columnspan=5, padx=2, pady=2, sticky="we")

        # 在 tabPage15 中建立 groupBox24（左上角）
        self.groupBox24 = ttk.LabelFrame(self.tabPage15, text="格式 [ 交易代碼,商品報價代碼 ] ( 多筆以 井號{#}區隔 )")
        self.groupBox24.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # groupBox24 中的元件
        self.txtStocksOS = ttk.Entry(self.groupBox24)
        self.txtStocksOS.insert(0, "NYM,NG2509#NYM,NG2510#CME,ES2512#CBOT,US2509")
        self.txtStocksOS.grid(row=0, column=0, padx=5, pady=5)

        self.btnQueryStocksOS = ttk.Button(self.groupBox24, text="查詢")
        self.btnQueryStocksOS.grid(row=0, column=1, padx=5, pady=5)

        # ➤ 放入一個固定大小的 Frame
        self.gridStocksOSFrame = ttk.Frame(self.tabPage15, width=850, height=400)
        self.gridStocksOSFrame.grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.gridStocksOSFrame.grid_propagate(False)  # 阻止內部元件撐大 frame

        # ➤ 建立 Treeview（可視欄位總數調整寬度）
        self.gridStocksOS = ttk.Treeview(self.gridStocksOSFrame, columns=self.stock_columnsOS, show="headings")

        # ➤ 每欄固定 80 寬
        for col in self.stock_columnsOS:
            self.gridStocksOS.heading(col, text=col)
            self.gridStocksOS.column(col, width=80, anchor="center", stretch=False)  # stretch=False 是關鍵！

        # ➤ 水平捲動條
        xscroll2 = ttk.Scrollbar(self.gridStocksOSFrame, orient="horizontal", command=self.gridStocksOS.xview)
        self.gridStocksOS.configure(xscrollcommand=xscroll2.set)

        # ➤ 垂直捲動條
        yscroll2 = ttk.Scrollbar(self.gridStocksOSFrame, orient="vertical", command=self.gridStocksOS.yview)
        self.gridStocksOS.configure(yscrollcommand=yscroll2.set)

        # ➤ 擺進去（不設 sticky 擴張）
        self.gridStocksOS.grid(row=0, column=0, sticky="nsew")
        xscroll2.grid(row=1, column=0, sticky="ew")
        yscroll2.grid(row=0, column=1, sticky="ns")

        # ➤ 設定 gridStocksOSFrame 裡面的排版邏輯
        self.gridStocksOSFrame.rowconfigure(0, weight=1)
        self.gridStocksOSFrame.columnconfigure(0, weight=1)

        # ------------------------------
        # (0,0) groupBox26 - LabelFrame
        # ------------------------------
        self.groupBox26 = ttk.LabelFrame(self.tabPage16, text='TICKS & BEST10')
        self.groupBox26.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # → row=0, column=0~5
        ttk.Label(self.groupBox26, text='第幾檔').grid(row=0, column=0, padx=5, pady=5)

        self.txtItemQuoteOS = ttk.Entry(self.groupBox26)
        self.txtItemQuoteOS.insert(0, "1")
        self.txtItemQuoteOS.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.groupBox26, text='商品代碼(僅一檔)').grid(row=0, column=2, padx=2, pady=2)
        self.txtTickOS = tk.Entry(self.groupBox26, width=10)
        self.txtTickOS.insert(0, "CME,ES2512")
        self.txtTickOS.grid(row=0, column=3, padx=2, pady=2)

        self.btnTicksOS = ttk.Button(self.groupBox26, text='Request Tick')
        self.btnTicksOS.grid(row=0, column=4, padx=2, pady=2)

        # ------------------------------
        # (1,0) listTicksOS - Listbox
        # ------------------------------
        self.listTicksOS = tk.Listbox(self.tabPage16, height=15, width=30)
        self.listTicksOS.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # ------------------------------
        # (1,1) GridBest10Bid - Treeview
        # ------------------------------
        self.GridBest10Bid = ttk.Treeview(self.tabPage16, columns=self.best10_bid_columns, show="headings", height=10)
        for col in self.best10_bid_columns:
            self.GridBest10Bid.heading(col, text=col)
            self.GridBest10Bid.column(col, width=80, anchor="center")
        self.GridBest10Bid.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # ------------------------------
        # (1,2) GridBest10Ask - Treeview
        # ------------------------------
        self.GridBest10Ask = ttk.Treeview(self.tabPage16, columns=self.best10_ask_columns, show="headings", height=10)
        for col in self.best10_ask_columns:
            self.GridBest10Ask.heading(col, text=col)
            self.GridBest10Ask.column(col, width=80, anchor="center")
        self.GridBest10Ask.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        # 模擬資料綁定
        self.m_dtBest10Bid = self.CreateBest10Table()
        self.m_dtBest10Ask = self.CreateBest10Table()
        self.BindDataGrids10OS()    
        
        # 在 tabPage19 中建立 groupBox25（左上角）
        self.groupBox25 = ttk.LabelFrame(self.tabPage19, text="格式 [ 交易代碼,商品報價代碼 ] ( 多筆以 井號{#}區隔 )")
        self.groupBox25.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # groupBox25 中的元件
        self.txtStocksOO = ttk.Entry(self.groupBox25)
        self.txtStocksOO.insert(0, "CME,E1A06130H5#HKEx,HSI29600T5")
        self.txtStocksOO.grid(row=0, column=0, padx=5, pady=5)

        self.btnQueryStocksOO = ttk.Button(self.groupBox25, text="查詢")
        self.btnQueryStocksOO.grid(row=0, column=1, padx=5, pady=5)

        # ➤ 放入一個固定大小的 Frame
        self.gridStocksOOFrame = ttk.Frame(self.tabPage19, width=850, height=400)
        self.gridStocksOOFrame.grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.gridStocksOOFrame.grid_propagate(False)  # 阻止內部元件撐大 frame

        # ➤ 建立 Treeview（可視欄位總數調整寬度）
        self.gridStocksOO = ttk.Treeview(self.gridStocksOOFrame, columns=self.stock_columnsOO, show="headings")

        # ➤ 每欄固定 80 寬
        for col in self.stock_columnsOO:
            self.gridStocksOO.heading(col, text=col)
            self.gridStocksOO.column(col, width=80, anchor="center", stretch=False)

        # ➤ 水平捲動條
        xscroll2 = ttk.Scrollbar(self.gridStocksOOFrame, orient="horizontal", command=self.gridStocksOO.xview)
        self.gridStocksOO.configure(xscrollcommand=xscroll2.set)

        # ➤ 垂直捲動條
        yscroll2 = ttk.Scrollbar(self.gridStocksOOFrame, orient="vertical", command=self.gridStocksOO.yview)
        self.gridStocksOO.configure(yscrollcommand=yscroll2.set)

        # ➤ 擺進去（不設 sticky 擴張）
        self.gridStocksOO.grid(row=0, column=0, sticky="nsew")
        xscroll2.grid(row=1, column=0, sticky="ew")
        yscroll2.grid(row=0, column=1, sticky="ns")

        # ➤ 設定 gridStocksOOFrame 裡面的排版邏輯
        self.gridStocksOOFrame.rowconfigure(0, weight=1)
        self.gridStocksOOFrame.columnconfigure(0, weight=1)

        # ------------------------------
        # (0,0) groupBox27 - LabelFrame
        # ------------------------------
        self.groupBox27 = ttk.LabelFrame(self.tabPage20, text='TICKS & BEST10')
        self.groupBox27.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # → row=0, column=0~5
        ttk.Label(self.groupBox27, text='第幾檔').grid(row=0, column=0, padx=5, pady=5)

        self.txtItemQuoteOO = ttk.Entry(self.groupBox27)
        self.txtItemQuoteOO.insert(0, "1")
        self.txtItemQuoteOO.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.groupBox27, text='商品代碼(僅一檔)').grid(row=0, column=2, padx=2, pady=2)
        self.txtTickOO = tk.Entry(self.groupBox27, width=10)
        self.txtTickOO.insert(0, "CME,E1A06130H5")
        self.txtTickOO.grid(row=0, column=3, padx=2, pady=2)

        self.btnTicksOO = ttk.Button(self.groupBox27, text='Request Tick')
        self.btnTicksOO.grid(row=0, column=4, padx=2, pady=2)

        # ------------------------------
        # (1,0) listTicksOO - Listbox
        # ------------------------------
        self.listTicksOO = tk.Listbox(self.tabPage20, height=15, width=30)
        self.listTicksOO.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # ------------------------------
        # (1,1) GridBest10Bid2 - Treeview
        # ------------------------------
        self.GridBest10Bid2 = ttk.Treeview(self.tabPage20, columns=self.best10_bid_columns, show="headings", height=10)
        for col in self.best10_bid_columns:
            self.GridBest10Bid2.heading(col, text=col)
            self.GridBest10Bid2.column(col, width=80, anchor="center")
        self.GridBest10Bid2.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # ------------------------------
        # (1,2) GridBest10Ask2 - Treeview
        # ------------------------------
        self.GridBest10Ask2 = ttk.Treeview(self.tabPage20, columns=self.best10_ask_columns, show="headings", height=10)
        for col in self.best10_ask_columns:
            self.GridBest10Ask2.heading(col, text=col)
            self.GridBest10Ask2.column(col, width=80, anchor="center")
        self.GridBest10Ask2.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        # 模擬資料綁定
        self.m_dtBest10Bid2 = self.CreateBest10Table()
        self.m_dtBest10Ask2 = self.CreateBest10Table()
        self.BindDataGrids10OO()

    def OnUpDateDataRow(self, stock_data):
        stock_no = stock_data.strStockNo
        grid = self.gridStocks
        found = False

        # 檢查是否已存在資料列（以股票代碼判斷）
        for row_id in grid.get_children():
            row_values = grid.item(row_id)["values"]
            if str(row_values[self.stock_columns.index("商品代碼")]) == stock_no:
                # 更新該筆 row 資料
                grid.item(row_id, values=self._build_row_values(stock_data))
                found = True
                break

        if not found:
            # 新增一筆資料
            grid.insert("", "end", values=self._build_row_values(stock_data))

    def OnUpDateDataQuote(self, stock_data):
        stock_no = stock_data.strStockNo
        grid = self.gridStocksOS
        found = False

        # 檢查是否已存在資料列（以股票代碼判斷）
        for row_id in grid.get_children():
            row_values = grid.item(row_id)["values"]
            if str(row_values[self.stock_columnsOS.index("商品代碼")]) == stock_no:
                # 更新該筆 row 資料
                grid.item(row_id, values=self._build_row_valuesOS(stock_data))
                found = True
                break

        if not found:
            # 新增一筆資料
            grid.insert("", "end", values=self._build_row_valuesOS(stock_data))
    
    def OnUpDateDataQuote2(self, stock_data):
        stock_no = stock_data.strStockNo
        grid = self.gridStocksOO
        found = False

        # 檢查是否已存在資料列（以股票代碼判斷）
        for row_id in grid.get_children():
            row_values = grid.item(row_id)["values"]
            if str(row_values[self.stock_columnsOO.index("商品代碼")]) == stock_no:
                # 更新該筆 row 資料
                grid.item(row_id, values=self._build_row_valuesOS(stock_data))
                found = True
                break

        if not found:
            # 新增一筆資料
            grid.insert("", "end", values=self._build_row_valuesOS(stock_data))
    
    def _build_row_values(self, s):
        d = s.nDecimal
        pow10 = 10 ** d
        market_price = 2147483647  # kMarketPrice 的對應值

        def format_price(x):
            return "市價" if x == market_price else round(x / pow10, d)

        is_simulated = s.nSimulate == 1 and s.nMarketNo in (5, 6)

        return [
            s.strStockNo,                             # m_caStockNo 代碼
            s.strStockName,                           # m_caName
            round(s.nOpen / pow10, d),                # m_nOpen
            round(s.nHigh / pow10, d),                # m_nHigh
            round(s.nLow / pow10, d),                 # m_nLow
            round(s.nClose / pow10, d),               # m_nClose
            s.nTickQty,                               # m_nTickQty
            round(s.nRef / pow10, d),                 # m_nRef
            format_price(s.nBid),                     # m_nBid
            s.nBc,                                    # m_nBc
            format_price(s.nAsk),                     # m_nAsk
            s.nAc,                                    # m_nAc
            s.nTBc,                                   # m_nTBc
            s.nTAc,                                   # m_nTAc
            s.nFutureOI,                              # m_nFutureOI
            s.nTQty,                                  # m_nTQty
            s.nYQty,                                  # m_nYQty
            round(s.nUp / pow10, d),                  # m_nUp
            round(s.nDown / pow10, d),                # m_nDown
            round(s.nClose / pow10, d) if is_simulated else "",  # m_nCloseS
            s.nTickQty if is_simulated else "",       # m_nTickQtyS
            format_price(s.nBid) if is_simulated else "",  # m_nBidS
            format_price(s.nAsk) if is_simulated else "",  # m_nAskS
            "",                                       # m_nOddLotPer（暫無資料來源）
            s.nDealTime,                              # m_nDealTime
            d,                                        # m_sDecimal
            s.nTypeNo,                                # m_sTypeNo
            s.nMarketNo                               # m_cMarketNo
        ]
    
    def _build_row_valuesOS(self, s):
        d = s.nDecimal
        pow10 = 10 ** d

        return [
            #s.nStockidx,                        # m_nStockidx
            #s.nDecimal,                         # m_sDecimal
            #s.nDenominator,                     # m_nDenominator
            #s.strMarketNo,                      # m_cMarketNo
            s.strExchangeNo,                    # m_caExchangeNo
            s.strExchangeName,                  # m_caExchangeName
            s.strStockNo,                       # m_caStockNo
            s.strStockName,                     # m_caStockName
            round(s.nOpen / pow10, d),          # m_nOpen
            round(s.nHigh / pow10, d),          # m_nHigh
            round(s.nLow / pow10, d),           # m_nLow
            round(s.nClose / pow10, d),         # m_nClose
            round(s.nSettlePrice / pow10, d),   # m_dSettlePrice
            s.nTickQty,                         # m_nTickQty
            round(s.nRef / pow10, d),           # m_nRef
            round(s.nBid / pow10, d),           # m_nBid
            s.nBc,                              # m_nBc
            round(s.nAsk / pow10, d),           # m_nAsk
            s.nAc,                                # m_nAc
            s.nTQty                             # m_nTQty
        ]

    def on_chkbox_msms_changed(self):
        # 勾選/取消「不含毫秒微秒」時，同步「含市價揭示轉換」
        self.Box_M_var.set(self.chkbox_msms_var.get())

    def on_Box_M_changed(self):
        # 勾選/取消「含市價揭示轉換」時，同步「不含毫秒微秒」
        self.chkbox_msms_var.set(self.Box_M_var.get())

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PythonTester")
        self.geometry("1200x600")

        # 方便跨檔案存取 Login UI 實例（可選）
        MainApp.instance = self

        # 建立 Canvas + Scrollbar 結構
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # 建立 Canvas
        self.canvas = tk.Canvas(container)
        self.canvas.pack(side="left", fill="both", expand=True)

        # 加入垂直 Scrollbar
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        v_scroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=v_scroll.set)

        # 加入水平 Scrollbar（可選）
        h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        h_scroll.pack(side="bottom", fill="x")
        self.canvas.configure(xscrollcommand=h_scroll.set)

        # 建立內部 Frame 裝元件，並放入 Canvas 中
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # 滾動滑鼠滾輪也能滾動（僅限垂直）
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        # 設定 grid 結構（放在 scrollable_frame 上）
        self.scrollable_frame.rowconfigure(2, weight=1)
        for i in range(3):
            self.scrollable_frame.columnconfigure(i, weight=1)

        # 放入原本的 Frame
        self.login_frame = Login(self.scrollable_frame)
        self.login_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        self.reply_frame = Reply(self.scrollable_frame)
        self.reply_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

        self.order_frame = Order(self.scrollable_frame)
        self.order_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.quote_frame = Quote(self.scrollable_frame)
        self.quote_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

# 啟動函式(由 PythonTester 啟動)
#if __name__ == "__main__":
#    app = MainApp()
#   app.mainloop()
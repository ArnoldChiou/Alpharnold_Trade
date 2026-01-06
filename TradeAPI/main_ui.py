import sys
import threading
import time
import json
import os
import hashlib
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from binance.client import Client
import config
from crypto_utils import encrypt_text, decrypt_text
from trading_strategy import TradingWorker, STATE_FOLDER

ACCOUNTS_FILE = "user_accounts.json"

# 按鈕與介面 QSS 樣式
GLOBAL_BTN_STYLE = """
    QPushButton { font-weight: bold; border-radius: 4px; padding: 5px; border: 1px solid #555; background-color: #333; color: white; }
    QPushButton:hover { background-color: #444; border: 1px solid #00ff00; }
    QPushButton:pressed { background-color: #111; padding-left: 8px; padding-top: 8px; }
    QPushButton#GreenBtn { background-color: #27ae60; }
    QPushButton#GreenBtn:hover { background-color: #2ecc71; border: 1px solid #fff; }
    QPushButton#RedBtn { background-color: #c0392b; }
    QPushButton#RedBtn:hover { background-color: #e74c3c; border: 1px solid #fff; }
    QPushButton#BlueBtn { background-color: #2980b9; }
    QPushButton#BlueBtn:hover { background-color: #3498db; border: 1px solid #fff; }
    QCheckBox { color: #00ff00; font-weight: bold; }
    QCheckBox::indicator { width: 18px; height: 18px; }
"""

class AccountManager(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AlphaTrader - 帳戶管理中心")
        self.setMinimumSize(600, 650)
        self.accounts = self.load_accounts()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet("QDialog { background: #222; color: white; } QLineEdit, QComboBox { background: #333; color: white; border: 1px solid #555; padding: 8px; } " + GLOBAL_BTN_STYLE)
        
        self.env_label = QLabel()
        self.env_label.setAlignment(Qt.AlignCenter)
        self.env_label.setFixedHeight(40)
        layout.addWidget(self.env_label)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: #1a1a1a; color: #00ff00; border: 1px solid #444; font-family: Consolas;")
        self.refresh_list()
        layout.addWidget(QLabel("已儲存帳號列表 (格式: [幣種-方向] 暱稱):"))
        layout.addWidget(self.list_widget)
        
        # --- 新增帳號區域 ---
        box = QGroupBox("新增/編輯帳號設定")
        gl = QFormLayout(box)
        
        self.nick_in = QLineEdit()
        self.api_in = QLineEdit()
        self.sec_in = QLineEdit()
        self.sec_in.setEchoMode(QLineEdit.Password)
        
        # [修改] 新增幣種與方向選擇
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"])
        
        self.dir_combo = QComboBox()
        self.dir_combo.addItems(["LONG (只做多)", "SHORT (只做空)"])
        
        gl.addRow("暱稱 (Nickname):", self.nick_in)
        gl.addRow("API Key:", self.api_in)
        gl.addRow("Secret Key:", self.sec_in)
        gl.addRow("綁定幣種 (Symbol):", self.symbol_combo)
        gl.addRow("策略方向 (Side):", self.dir_combo)
        
        layout.addWidget(box)
        
        bl = QHBoxLayout()
        add_b = QPushButton("加密新增")
        add_b.setObjectName("GreenBtn")
        add_b.clicked.connect(self.add_acc)
        
        del_b = QPushButton("刪除選中")
        del_b.setObjectName("RedBtn")
        del_b.clicked.connect(self.del_acc)
        
        bl.addWidget(add_b)
        bl.addWidget(del_b)
        layout.addLayout(bl)
        
        self.testnet_chk = QCheckBox("使用幣安測試網 (Testnet Mode)")
        self.testnet_chk.setChecked(config.IS_TESTNET)
        self.testnet_chk.stateChanged.connect(self.update_env_indicator)
        layout.addWidget(self.testnet_chk)
        
        sb = QPushButton("進入下單控制台")
        sb.setObjectName("GreenBtn")
        sb.setFixedHeight(45)
        sb.clicked.connect(self.accept)
        layout.addWidget(sb)
        
        self.update_env_indicator()

    def update_env_indicator(self):
        if self.testnet_chk.isChecked():
            self.env_label.setText("⚠️ 當前設定：測試網 (Testnet)")
            self.env_label.setStyleSheet("background-color: #f39c12; color: black; font-weight: bold;")
        else:
            self.env_label.setText("🛡️ 當前設定：正式網 (Mainnet)")
            self.env_label.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

    def load_accounts(self):
        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def refresh_list(self):
        self.list_widget.clear()
        for a in self.accounts:
            nick = a.get('nickname', '未命名')
            # 讀取設定，若無則預設
            conf = a.get('config', {})
            sym = conf.get('symbol', 'BTCUSDT')
            dire = conf.get('direction', 'BOTH').split(' ')[0]
            
            self.list_widget.addItem(f"[{sym}-{dire}] {nick}")

    def add_acc(self):
        n = self.nick_in.text().strip()
        a = self.api_in.text().strip()
        s = self.sec_in.text().strip()
        sym = self.symbol_combo.currentText()
        dire = self.dir_combo.currentText().split(' ')[0] # 只取 LONG/SHORT/BOTH
        
        if n and a and s:
            new_data = {
                "nickname": n, 
                "api_key": encrypt_text(a), 
                "secret_key": encrypt_text(s),
                # [修改] 儲存專屬設定
                "config": {
                    "symbol": sym,
                    "direction": dire
                }
            }
            self.accounts.append(new_data)
            self.save_acc()
            self.refresh_list()
            # 清空輸入框
            self.nick_in.clear()
            self.api_in.clear()
            self.sec_in.clear()

    def del_acc(self):
        r = self.list_widget.currentRow()
        if r >= 0:
            self.accounts.pop(r)
            self.save_acc()
            self.refresh_list()

    def save_acc(self):
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump(self.accounts, f)

class MainWindow(QMainWindow):
    def __init__(self, account_data, is_testnet):
        super().__init__()
        self.account_data = account_data
        self.is_testnet = is_testnet
        
        # [修改] 不再有單一的 self.symbol，而是收集所有帳戶用到的幣種
        self.active_symbols = set()
        for acc in self.account_data:
            conf = acc.get('config', {})
            self.active_symbols.add(conf.get('symbol', 'BTCUSDT'))
        
        # 轉為列表並排序
        self.active_symbols = sorted(list(self.active_symbols))
        symbols_str = ",".join([s.replace("USDT", "") for s in self.active_symbols])
        
        env_str = "測試網" if is_testnet else "正式網"
        self.setWindowTitle(f"AlphaTrader Pro - 多幣種管理 [{symbols_str}] - {env_str}")
        self.setMinimumSize(1400, 900)
        
        self.prices = {s: 0.0 for s in self.active_symbols}
        self.workers = [None] * len(account_data)
        self.manual_workers = []

        self.main_client = None
        self.init_ui()
        QTimer.singleShot(100, self.connect_market_data)

    def connect_market_data(self):
        try:
            # 建立一個只用來看行情的 Client (使用第一個帳戶的 API)
            if self.account_data:
                self.main_client = Client(decrypt_text(self.account_data[0]['api_key']), 
                                        decrypt_text(self.account_data[0]['secret_key']), 
                                        testnet=self.is_testnet)
                self.start_price_monitor()
                self.append_log(f"✅ 成功連線，監控幣種: {self.active_symbols}")
            else:
                self.price_label.setText("無帳戶")
        except Exception as e:
            QMessageBox.critical(self, "API 連線失敗", f"連線出錯: {e}")
            self.price_label.setText("連線失敗")

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        ml = QVBoxLayout(cw)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #444; background: #222; } QTabBar::tab { background: #333; color: #888; padding: 12px 25px; border: 1px solid #444; } QTabBar::tab:selected { background: #222; color: #00ff00; font-weight: bold; }")
        
        self.tab_strat = QWidget()
        self.setup_strat_tab(QVBoxLayout(self.tab_strat))
        self.tab_stat = QWidget()
        self.setup_stat_tab(QVBoxLayout(self.tab_stat))
        
        self.tabs.addTab(self.tab_strat, "策略控制中心")
        self.tabs.addTab(self.tab_stat, "帳戶監控面板")
        
        # [修改] 價格標籤
        self.price_label = QLabel("讀取中...")
        self.price_label.setAlignment(Qt.AlignCenter)
        self.price_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00; background: #111; padding: 15px; border: 1px solid #333;")
        ml.addWidget(self.price_label)
        ml.addWidget(self.tabs)
        self.setStyleSheet("QMainWindow { background: #222; } QLabel { color: #ddd; } QGroupBox { color: #fff; font-weight: bold; border: 1px solid #444; margin-top: 10px; padding-top: 15px; } QTextEdit { background: #1a1a1a; color: #00ff00; font-family: Consolas; } QLineEdit { background: #333; color: white; border: 1px solid #555; } " + GLOBAL_BTN_STYLE)

    def setup_strat_tab(self, layout):
        self.banner = QLabel()
        self.banner.setAlignment(Qt.AlignCenter)
        self.banner.setFixedHeight(30)
        if self.is_testnet:
            self.banner.setText("● 當前運行模式：測試網 (SANDBOX)")
            self.banner.setStyleSheet("background-color: #f39c12; color: black; font-weight: bold; border-radius: 4px;")
        else:
            self.banner.setText("● 當前運行模式：正式網 (LIVE)")
            self.banner.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; border-radius: 4px;")
        layout.addWidget(self.banner)
        
        # --- 策略參數 (全域共用) ---
        hl = QHBoxLayout()
        self.inputs = {}
        p_list = [("突破天數", "lookback", "20"), ("進場緩衝 %", "buffer", "0.2"), ("停損 %", "sl", "1.5"), ("移停觸發 %", "ttp_trig", "3.0"), ("移停回撤 %", "ttp_call", "0.5")]
        for p in ["long", "short"]:
            box = QGroupBox(f" {p.upper()} 參數設定 ")
            gl = QGridLayout(box)
            for i, (l, k, v) in enumerate(p_list):
                gl.addWidget(QLabel(l), i, 0)
                e = QLineEdit(v)
                e.setValidator(QIntValidator(1, 999) if k=="lookback" else QDoubleValidator(0, 99, 2))
                gl.addWidget(e, i, 1)
                self.inputs[f"{p}_{k}"] = e
            hl.addWidget(box)
        layout.addLayout(hl)
        
        mode_container = QHBoxLayout()
        self.mode_group = QGroupBox("下單模式 (套用於所有帳戶)")
        self.mode_group.setStyleSheet("QGroupBox { border: 1px solid #444; border-radius: 6px; margin-top: 10px; }")
        mode_grid = QGridLayout(self.mode_group)
        self.radio_pct = QRadioButton("比例下單")
        self.radio_pct.setChecked(True)
        self.spin_pct = QDoubleSpinBox()
        self.spin_pct.setRange(1, 100)
        self.spin_pct.setValue(10)
        self.spin_pct.setSuffix(" %")
        self.radio_fixed = QRadioButton("固定下單")
        self.spin_fixed = QDoubleSpinBox()
        self.spin_fixed.setRange(0, 999)
        self.spin_fixed.setDecimals(3)
        self.spin_fixed.setValue(0.005) 
        self.spin_fixed.setSuffix(" 顆") # 通用單位
        mode_grid.addWidget(self.radio_pct, 0, 0)
        mode_grid.addWidget(self.spin_pct, 0, 1)
        mode_grid.addWidget(self.radio_fixed, 1, 0)
        mode_grid.addWidget(self.spin_fixed, 1, 1)
        
        mode_container.addWidget(self.mode_group, 1)
        layout.addLayout(mode_container)

        bl = QHBoxLayout()
        self.start_btn = QPushButton("啟動全體策略")
        self.start_btn.setObjectName("GreenBtn")
        self.start_btn.setFixedHeight(50)
        self.start_btn.clicked.connect(self.start_strategy)
        
        self.buy_t = QPushButton("多帳戶買入測試")
        self.buy_t.setFixedHeight(50)
        self.buy_t.clicked.connect(self.manual_buy)
        
        self.sell_t = QPushButton("多帳戶賣出測試")
        self.sell_t.setFixedHeight(50)
        self.sell_t.clicked.connect(self.manual_sell)
        
        bl.addWidget(self.start_btn, 1)
        bl.addWidget(self.buy_t, 1)
        bl.addWidget(self.sell_t, 1)
        layout.addLayout(bl)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

    def setup_stat_tab(self, layout):
        # --- 新增篩選控制區域 ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("方向篩選："))
        self.side_filter = QComboBox()
        self.side_filter.addItems(["全部", "LONG", "SHORT"])
        self.side_filter.currentTextChanged.connect(self.apply_account_filter)
        filter_layout.addWidget(self.side_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.status_table = QTableWidget()
        self.status_table.setColumnCount(12)
        self.status_table.setHorizontalHeaderLabels(["設定", "今日單", "總單", "餘額", "倉位", "均價", "PNL", "預計止損", "狀態", "開關", "平倉", "移除"])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.setStyleSheet("QTableWidget { background: #1a1a1a; color: #eee; border: none; } QHeaderView::section { background: #333; color: #00ff00; }")
        self.status_table.setRowCount(len(self.account_data))
        for i, acc in enumerate(self.account_data):
            self.add_row_to_table(i, acc)
        layout.addWidget(self.status_table)
        
        ctrl_l = QHBoxLayout()
        self.dyn_add_btn = QPushButton("✨ 動態新增帳戶")
        self.dyn_add_btn.setObjectName("BlueBtn")
        self.dyn_add_btn.setFixedHeight(40)
        self.dyn_add_btn.clicked.connect(self.dynamic_add_account)
        
        refresh_btn = QPushButton("手動刷新狀態")
        refresh_btn.setFixedHeight(40)
        refresh_btn.clicked.connect(self.update_all_account_status)
        
        ctrl_l.addStretch()
        ctrl_l.addWidget(self.dyn_add_btn)
        ctrl_l.addWidget(refresh_btn)
        layout.addLayout(ctrl_l)

    def add_row_to_table(self, i, acc):
        nick = acc.get('nickname', '未命名')
        conf = acc.get('config', {})
        sym = conf.get('symbol', 'BTCUSDT')
        dire = conf.get('direction', 'BOTH')
        
        display_name = f"{nick}\n[{sym}]\n({dire})"
        
        self.status_table.setItem(i, 0, QTableWidgetItem(display_name))
        for j in range(1, 8):
            self.status_table.setItem(i, j, QTableWidgetItem("---"))
        self.status_table.setItem(i, 8, QTableWidgetItem("⏹️ 停止"))
        
        tb = QPushButton("啟動")
        tb.setObjectName("GreenBtn")
        tb.clicked.connect(lambda c=False, idx=i: self.toggle_individual_account(idx))
        self.status_table.setCellWidget(i, 9, tb)
        
        cb = QPushButton("平倉")
        cb.setObjectName("RedBtn")
        cb.setEnabled(False)
        cb.clicked.connect(lambda c=False, idx=i: self.manual_close_account(idx))
        self.status_table.setCellWidget(i, 10, cb)
        
        db = QPushButton("移除")
        db.setObjectName("RedBtn")
        db.clicked.connect(lambda c=False, idx=i: self.delete_account_from_panel(idx))
        self.status_table.setCellWidget(i, 11, db)
        
        # 調整行高以顯示多行資訊
        self.status_table.setRowHeight(i, 60)

    def dynamic_add_account(self):
        # 這裡簡單呼叫 AccountManager 視窗
        mgr = AccountManager()
        if mgr.exec() == QDialog.Accepted:
            # 重新載入
            self.account_data = mgr.accounts
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(self.account_data, f)
            # 重繪表格
            self.status_table.setRowCount(0)
            self.status_table.setRowCount(len(self.account_data))
            self.workers = [None] * len(self.account_data)
            for i, acc in enumerate(self.account_data):
                self.add_row_to_table(i, acc)
            self.refresh_table_indices()
            # 重新掃描幣種
            self.active_symbols = set()
            for acc in self.account_data:
                conf = acc.get('config', {})
                self.active_symbols.add(conf.get('symbol', 'BTCUSDT'))
            self.active_symbols = sorted(list(self.active_symbols))
            self.apply_account_filter()

    def update_all_account_status(self):
        for i, acc in enumerate(self.account_data):
            try:
                # [修正] 讀取該帳戶設定的 Symbol
                conf = acc.get('config', {})
                symbol = conf.get('symbol', 'BTCUSDT')
                
                api = decrypt_text(acc['api_key'])
                sec = decrypt_text(acc['secret_key'])
                c = Client(api, sec, testnet=self.is_testnet)
                ai = c.futures_account()
                h = hashlib.md5(api.encode()).hexdigest()[:8]
                
                # [修正] 讀取對應 Symbol 的狀態檔
                sf = os.path.join(STATE_FOLDER, f"state_{h}_{symbol}.json")
                if os.path.exists(sf):
                    with open(sf, "r") as f:
                        d = json.load(f)
                        self.status_table.setItem(i, 1, QTableWidgetItem(str(d.get("daily_trades", 0))))
                        self.status_table.setItem(i, 2, QTableWidgetItem(str(d.get("total_trades", 0))))
                        sli = QTableWidgetItem(f"{d.get('sl_price', 0.0):,.2f}")
                        sli.setForeground(QColor("#ff9f43"))
                        self.status_table.setItem(i, 7, sli)
                
                bal = next(float(a['walletBalance']) for a in ai['assets'] if a['asset'] == 'USDT')
                self.status_table.setItem(i, 3, QTableWidgetItem(f"{bal:,.2f}"))
                
                # [修正] 檢查該帳戶 Symbol 的倉位
                pos = next((p for p in ai['positions'] if p['symbol'] == symbol), None)
                cb = self.status_table.cellWidget(i, 10)
                if pos and float(pos['positionAmt']) != 0:
                    side = "多" if float(pos['positionAmt']) > 0 else "空"
                    self.status_table.setItem(i, 4, QTableWidgetItem(f"{side} ({abs(float(pos['positionAmt']))})"))
                    self.status_table.setItem(i, 5, QTableWidgetItem(f"{float(pos['entryPrice']):.2f}"))
                    pnl = float(pos['unrealizedProfit'])
                    pi = QTableWidgetItem(f"{pnl:+.2f}")
                    pi.setForeground(QColor("#00ff00" if pnl > 0 else "#ff4d4d"))
                    self.status_table.setItem(i, 6, pi)
                    if cb:
                        cb.setEnabled(True)
                        cb.setStyleSheet("background: #d35400; color: white;")
                else:
                    self.status_table.setItem(i, 4, QTableWidgetItem("---"))
                    self.status_table.setItem(i, 5, QTableWidgetItem("---"))
                    self.status_table.setItem(i, 6, QTableWidgetItem("0.00"))
                    if cb:
                        cb.setEnabled(False)
                        cb.setStyleSheet("background: #555; color: #aaa;")
            except Exception as e:
                pass

    def manual_close_account(self, idx):
        acc = self.account_data[idx]
        conf = acc.get('config', {})
        symbol = conf.get('symbol', 'BTCUSDT')
        nick = acc.get('nickname', '未命名')
        
        if QMessageBox.question(self, "確認", f"確定要平掉「{nick}」的 {symbol} 倉位嗎？") == QMessageBox.No:
            return
        
        if self.status_table.cellWidget(idx, 9).text() == "停止":
            self.toggle_individual_account(idx)
        try:
            raw_api = decrypt_text(acc['api_key'])
            c = Client(raw_api, decrypt_text(acc['secret_key']), testnet=self.is_testnet)
            ai = c.futures_account()
            pos = next((p for p in ai['positions'] if p['symbol'] == symbol), None)
            if pos and float(pos['positionAmt']) != 0:
                side = "SELL" if float(pos['positionAmt']) > 0 else "BUY"
                c.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=abs(float(pos['positionAmt'])), reduceOnly=True)
                if self.workers[idx]:
                    self.workers[idx].clear_state()
                QTimer.singleShot(1000, self.update_all_account_status)
        except Exception as e:
            QMessageBox.critical(self, "失敗", str(e))

    def delete_account_from_panel(self, idx):
        nick = self.account_data[idx].get('nickname', '未命名')
        if QMessageBox.warning(self, "移除", f"確定移除「{nick}」？", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        if self.workers[idx]:
            self.workers[idx].stop()
        self.account_data.pop(idx)
        self.workers.pop(idx)
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump(self.account_data, f)
        self.status_table.removeRow(idx)
        self.refresh_table_indices()

    def refresh_table_indices(self):
        for i in range(self.status_table.rowCount()):
            for col, func in [(9, self.toggle_individual_account), (10, self.manual_close_account), (11, self.delete_account_from_panel)]:
                w = self.status_table.cellWidget(i, col)
                if w:
                    try:
                        w.clicked.disconnect()
                    except:
                        pass
                    w.clicked.connect(lambda c=False, idx=i, f=func: f(idx))

    def toggle_individual_account(self, idx, wait_for_reset=False):
        btn = self.status_table.cellWidget(idx, 9)
        nick = self.account_data[idx].get('nickname', '未命名')
        
        # [核心修改] 讀取該帳戶的專屬設定
        acc_config = self.account_data[idx].get('config', {})
        target_symbol = acc_config.get('symbol', 'BTCUSDT')
        target_direction = acc_config.get('direction', 'BOTH')
        
        ps = self.get_params()
        # [覆寫] 強制使用帳戶設定的方向
        ps['direction'] = target_direction
        
        if btn.text() == "啟動":
            api = decrypt_text(self.account_data[idx]['api_key'])
            sec = decrypt_text(self.account_data[idx]['secret_key'])
            c = Client(api, sec, testnet=self.is_testnet)
            
            # [傳遞] 將 symbol 傳給 Worker
            w = TradingWorker(c, ps, target_symbol, wait_for_reset)
            w.price_update.connect(lambda p, s=target_symbol: self.update_price_cache(s, p)) # 用於更新快取
            w.log_update.connect(lambda m, n=nick: self.append_log(f"【{n}】 {m}"))
            
            self.workers[idx] = w
            threading.Thread(target=w.run, daemon=True).start()
            
            self.status_table.setItem(idx, 8, QTableWidgetItem("⚡ 運行" if not wait_for_reset else "⏳ 等待同步"))
            btn.setText("停止")
            btn.setObjectName("RedBtn")
            btn.setStyle(btn.style())
        else:
            if self.workers[idx]:
                self.workers[idx].stop()
            self.status_table.setItem(idx, 8, QTableWidgetItem("⏹️ 停止"))
            btn.setText("啟動")
            btn.setObjectName("GreenBtn")
            btn.setStyle(btn.style())

    def update_price_cache(self, symbol, price):
        self.prices[symbol] = price
        # 更新顯示文字
        display_str = " | ".join([f"{s.replace('USDT','')}: {p:,.2f}" for s, p in self.prices.items() if p > 0])
        self.price_label.setText(display_str)

    def start_price_monitor(self):
        # 這裡改成多幣種輪詢
        def monitor():
            while True:
                if self.main_client:
                    for sym in self.active_symbols:
                        try:
                            p = float(self.main_client.futures_symbol_ticker(symbol=sym)['price'])
                            # 使用信號傳回主線程比較安全，這裡簡化直接更新字典
                            # 為了 UI 安全，我們發射一個自定義信號或利用現有機制
                            # 但這裡因為是在 Thread 中，最安全是透過 Worker 的信號
                            # 由於我們沒有全局 Worker，這裡簡單更新價格緩存，讓個別 Worker 的信號去更新 UI
                            # 或者：
                            self.prices[sym] = p
                        except:
                            pass
                    
                    # 組合顯示字串
                    display_str = " | ".join([f"{s.replace('USDT','')}: {p:,.2f}" for s, p in self.prices.items() if p > 0])
                    # 使用 QMetaObject 跨線程更新 UI
                    QMetaObject.invokeMethod(self.price_label, "setText", Qt.QueuedConnection, Q_ARG(str, display_str))
                    
                time.sleep(1) # 每秒更新所有幣種
        threading.Thread(target=monitor, daemon=True).start()

    def append_log(self, m):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{now}] {m}")
        self.log_display.ensureCursorVisible()

    def start_strategy(self):
        if self.start_btn.text().startswith("啟動"):
            for i in range(len(self.account_data)):
                if self.status_table.cellWidget(i, 9).text() == "啟動":
                    self.toggle_individual_account(i)
            self.start_btn.setText("停止全體策略")
            self.start_btn.setObjectName("RedBtn")
            self.set_enabled(False)
        else:
            for i in range(len(self.account_data)):
                if self.status_table.cellWidget(i, 9).text() == "停止":
                    self.toggle_individual_account(i)
            self.start_btn.setText("啟動全體策略")
            self.start_btn.setObjectName("GreenBtn")
            self.set_enabled(True)
        self.start_btn.setStyle(self.start_btn.style())

    def set_enabled(self, e):
        for i in self.inputs.values():
            i.setEnabled(e)
        self.radio_pct.setEnabled(e)
        self.radio_fixed.setEnabled(e)
        self.spin_pct.setEnabled(e)
        self.spin_fixed.setEnabled(e)
        self.dyn_add_btn.setEnabled(True)

    def manual_buy(self):
        self.manual_trade("BUY")
    
    def manual_sell(self):
        self.manual_trade("SELL")

    def manual_trade(self, side):
        params = self.get_params()
        self.append_log(f"🚀 開始執行多帳戶手動 {side} 測試...")
        
        self.manual_workers = [w for w in self.manual_workers if w.is_running]

        for acc in self.account_data:
            nick = acc.get('nickname', '未命名')
            # [修正] 讀取該帳戶設定
            conf = acc.get('config', {})
            symbol = conf.get('symbol', 'BTCUSDT')
            
            try:
                client = Client(decrypt_text(acc['api_key']), decrypt_text(acc['secret_key']), testnet=self.is_testnet)
                # [修正] 傳入正確的 Symbol
                w = TradingWorker(client, params, symbol)
                w.log_update.connect(lambda m, n=nick: self.append_log(f"【{n}】 {m}"))
                self.manual_workers.append(w)
                
                # 取得當前價格 (若緩存有則用緩存，否則即時抓)
                price = self.prices.get(symbol, 0.0)
                if price <= 0:
                     ticker = client.futures_symbol_ticker(symbol=symbol)
                     price = float(ticker['price'])

                w.is_running = True 
                threading.Thread(target=self._run_manual_task, args=(w, price, side), daemon=True).start()
            except Exception as e:
                self.append_log(f"❌ 【{nick}】初始化失敗: {e}")

    def _run_manual_task(self, worker, price, side):
        worker.execute_entry(price, side, True)
        worker.is_running = False

    def get_params(self):
        p = {k: float(v.text()) for k, v in self.inputs.items()}
        p['order_mode'] = "FIXED" if self.radio_fixed.isChecked() else "PERCENT"
        p['fixed_qty'] = self.spin_fixed.value()
        p['trade_pct'] = self.spin_pct.value()
        # [修改] 這裡的方向將被個別帳戶設定覆蓋
        p['direction'] = "BOTH" 
        return p
    
    def apply_account_filter(self):
        filter_text = self.side_filter.currentText()
        for i in range(self.status_table.rowCount()):
            acc = self.account_data[i]
            direction = acc.get('config', {}).get('direction', '')
            
            if filter_text == "全部" or direction == filter_text:
                self.status_table.setRowHidden(i, False)
            else:
                self.status_table.setRowHidden(i, True)

    
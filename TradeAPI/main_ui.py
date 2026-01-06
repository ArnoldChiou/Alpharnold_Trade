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
# [修改] 從外部匯入優化後的 Worker
from trading_strategy import TradingWorker, STATE_FOLDER

ACCOUNTS_FILE = "user_accounts.json"

# 按鈕與介面 QSS 樣式 (保持不變)
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
    # (AccountManager 類別代碼保持原樣，無需修改，為了簡潔這裡省略，請保留原有的 AccountManager 程式碼)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AlphaTrader - 帳戶管理中心")
        self.setMinimumSize(500, 600)
        self.accounts = self.load_accounts()
        self.setup_ui()
    
    # ... (請將原有的 setup_ui, update_env_indicator, load_accounts, refresh_list, add_acc, del_acc, save_acc 貼在這裡) ...
    # 為了完整性，若你需要可直接複製舊檔的這部分，這部分邏輯是共用的。
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet("QDialog { background: #222; color: white; } QLineEdit { background: #333; color: white; border: 1px solid #555; padding: 8px; } " + GLOBAL_BTN_STYLE)
        self.env_label = QLabel()
        self.env_label.setAlignment(Qt.AlignCenter)
        self.env_label.setFixedHeight(40)
        layout.addWidget(self.env_label)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: #1a1a1a; color: #00ff00; border: 1px solid #444;")
        self.refresh_list()
        layout.addWidget(QLabel("已儲存帳號列表:"))
        layout.addWidget(self.list_widget)
        box = QGroupBox("新增帳號")
        gl = QFormLayout(box)
        self.nick_in = QLineEdit()
        self.api_in = QLineEdit()
        self.sec_in = QLineEdit()
        self.sec_in.setEchoMode(QLineEdit.Password)
        gl.addRow("暱稱:", self.nick_in)
        gl.addRow("API Key:", self.api_in)
        gl.addRow("Secret:", self.sec_in)
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
            self.list_widget.addItem(f"【{nick}】 API: {a['api_key'][:10]}...")

    def add_acc(self):
        n = self.nick_in.text().strip()
        a = self.api_in.text().strip()
        s = self.sec_in.text().strip()
        if n and a and s:
            new_data = {"nickname": n, "api_key": encrypt_text(a), "secret_key": encrypt_text(s)}
            self.accounts.append(new_data)
            self.save_acc()
            self.refresh_list()
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
    def __init__(self, account_data, is_testnet, symbol): # [修改] 增加 symbol 參數
        super().__init__()
        self.account_data = account_data
        self.is_testnet = is_testnet
        self.symbol = symbol # [修改] 儲存 symbol
        
        env_str = "測試網" if is_testnet else "正式網"
        self.setWindowTitle(f"AlphaTrader Pro - {self.symbol} 管理 [{env_str}]")
        self.setMinimumSize(1300, 900)
        self.last_price = 0.0
        self.workers = [None] * len(account_data)
        self.manual_workers = [] # 防止閃退用

        # [優化] 延遲連線，避免介面卡死
        self.main_client = None
        self.init_ui()
        QTimer.singleShot(100, self.connect_market_data)

    def connect_market_data(self):
        try:
            # 建立一個只用來看行情的 Client
            self.main_client = Client(decrypt_text(self.account_data[0]['api_key']), 
                                    decrypt_text(self.account_data[0]['secret_key']), 
                                    testnet=self.is_testnet)
            self.start_price_monitor()
            self.append_log(f"✅ 成功連線至 {self.symbol} 行情")
        except Exception as e:
            QMessageBox.critical(self, "API 連線失敗", f"連線出錯: {e}")
            self.price_label.setText(f"{self.symbol}: 連線失敗")

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
        
        self.price_label = QLabel(f"{self.symbol}: 讀取中...")
        self.price_label.setAlignment(Qt.AlignCenter)
        self.price_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #00ff00; background: #111; padding: 15px; border: 1px solid #333;")
        ml.addWidget(self.price_label)
        ml.addWidget(self.tabs)
        self.setStyleSheet("QMainWindow { background: #222; } QLabel { color: #ddd; } QGroupBox { color: #fff; font-weight: bold; border: 1px solid #444; margin-top: 10px; padding-top: 15px; } QTextEdit { background: #1a1a1a; color: #00ff00; font-family: Consolas; } QLineEdit { background: #333; color: white; border: 1px solid #555; } " + GLOBAL_BTN_STYLE)

    def setup_strat_tab(self, layout):
        # ... (這部分 UI 佈局代碼與原版幾乎相同，保持不變) ...
        # 為了完整性，這裡簡略帶過重點：
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
        hl = QHBoxLayout()
        self.inputs = {}
        p_list = [("突破天數", "lookback", "20"), ("進場緩衝 %", "buffer", "0.2"), ("停損 %", "sl", "1.5"), ("移停觸發 %", "ttp_trig", "3.0"), ("移停回撤 %", "ttp_call", "0.5")]
        for p in ["long", "short"]:
            box = QGroupBox(f" {p.upper()} 條件 ")
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
        self.mode_group = QGroupBox("下單模式設定")
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
        self.spin_fixed.setValue(0.007 if "ETH" in self.symbol else 0.001) # [修改] 根據幣種調整預設值
        self.spin_fixed.setSuffix(f" {self.symbol[:3]}")
        mode_grid.addWidget(self.radio_pct, 0, 0)
        mode_grid.addWidget(self.spin_pct, 0, 1)
        mode_grid.addWidget(self.radio_fixed, 1, 0)
        mode_grid.addWidget(self.spin_fixed, 1, 1)
        
        self.dir_group = QGroupBox("進場方向限制")
        self.dir_group.setStyleSheet(self.mode_group.styleSheet())
        dir_grid = QGridLayout(self.dir_group)
        self.radio_both = QRadioButton("多空皆做")
        self.radio_both.setChecked(True)
        self.radio_long_only = QRadioButton("只做多")
        self.radio_short_only = QRadioButton("只做空")
        dir_grid.addWidget(self.radio_both, 0, 0)
        dir_grid.addWidget(self.radio_long_only, 1, 0)
        dir_grid.addWidget(self.radio_short_only, 1, 1)
        
        mode_container.addWidget(self.mode_group, 1)
        mode_container.addWidget(self.dir_group, 1)
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
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(12)
        self.status_table.setHorizontalHeaderLabels(["暱稱", "今日單", "總單", "餘額", "倉位", "均價", "PNL", "預計止損", "狀態", "開關", "平倉", "移除"])
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
        # (同原版)
        self.status_table.setItem(i, 0, QTableWidgetItem(acc.get('nickname', '未命名')))
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

    def dynamic_add_account(self):
        # (同原版)
        d = QDialog(self)
        d.setWindowTitle("動態新增帳戶")
        d.setMinimumSize(400, 300)
        dl = QFormLayout(d)
        n_in, a_in, s_in = QLineEdit(), QLineEdit(), QLineEdit()
        s_in.setEchoMode(QLineEdit.Password)
        dl.addRow("暱稱:", n_in)
        dl.addRow("API:", a_in)
        dl.addRow("Secret:", s_in)
        btn = QPushButton("確認新增")
        btn.setObjectName("GreenBtn")
        dl.addWidget(btn)
        def do_add():
            nick, api, sec = n_in.text().strip(), a_in.text().strip(), s_in.text().strip()
            if nick and api and sec:
                new_acc = {"nickname": nick, "api_key": encrypt_text(api), "secret_key": encrypt_text(sec)}
                self.account_data.append(new_acc)
                with open(ACCOUNTS_FILE, "w") as f:
                    json.dump(self.account_data, f)
                idx = self.status_table.rowCount()
                self.status_table.insertRow(idx)
                self.add_row_to_table(idx, new_acc)
                self.workers.append(None)
                if self.start_btn.text().startswith("停止"):
                    self.toggle_individual_account(idx, wait_for_reset=True)
                d.accept()
        btn.clicked.connect(do_add)
        d.exec()

    def update_all_account_status(self):
        # [修改] 使用 STATE_FOLDER 和 Symbol 來讀取正確的檔案
        for i, acc in enumerate(self.account_data):
            try:
                api = decrypt_text(acc['api_key'])
                sec = decrypt_text(acc['secret_key'])
                c = Client(api, sec, testnet=self.is_testnet)
                ai = c.futures_account()
                h = hashlib.md5(api.encode()).hexdigest()[:8]
                # [修正] 讀取對應 Symbol 的狀態檔
                sf = os.path.join(STATE_FOLDER, f"state_{h}_{self.symbol}.json")
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
                pos = next((p for p in ai['positions'] if p['symbol'] == self.symbol), None)
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
                # print(e) 
                pass

    def manual_close_account(self, idx):
        # (同原版)
        acc = self.account_data[idx]
        nick = acc.get('nickname', '未命名')
        if QMessageBox.question(self, "確認", f"確定要平掉「{nick}」倉位嗎？") == QMessageBox.No:
            return
        if self.status_table.cellWidget(idx, 9).text() == "停止":
            self.toggle_individual_account(idx)
        try:
            raw_api = decrypt_text(acc['api_key'])
            c = Client(raw_api, decrypt_text(acc['secret_key']), testnet=self.is_testnet)
            ai = c.futures_account()
            pos = next((p for p in ai['positions'] if p['symbol'] == self.symbol), None)
            if pos and float(pos['positionAmt']) != 0:
                side = "SELL" if float(pos['positionAmt']) > 0 else "BUY"
                c.futures_create_order(symbol=self.symbol, side=side, type='MARKET', quantity=abs(float(pos['positionAmt'])), reduceOnly=True)
                if self.workers[idx]:
                    self.workers[idx].clear_state()
                QTimer.singleShot(1000, self.update_all_account_status)
        except Exception as e:
            QMessageBox.critical(self, "失敗", str(e))

    def delete_account_from_panel(self, idx):
        # (同原版)
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
        # (同原版)
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
        ps = self.get_params()
        if btn.text() == "啟動":
            api = decrypt_text(self.account_data[idx]['api_key'])
            sec = decrypt_text(self.account_data[idx]['secret_key'])
            c = Client(api, sec, testnet=self.is_testnet)
            # [修改] 傳入 self.symbol
            w = TradingWorker(c, ps, self.symbol, wait_for_reset)
            w.price_update.connect(self.price_update)
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

    def start_price_monitor(self):
        def monitor():
            while True:
                try: 
                    if self.main_client:
                        p = float(self.main_client.futures_symbol_ticker(symbol=self.symbol)['price'])
                        self.price_update(p)
                    time.sleep(1)
                except:
                    time.sleep(5)
        threading.Thread(target=monitor, daemon=True).start()

    @Slot(float)
    def price_update(self, p):
        self.last_price = p
        self.price_label.setText(f"{self.symbol}: {p:,.2f}")

    def append_log(self, m):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{now}] {m}")
        self.log_display.ensureCursorVisible()

    def start_strategy(self):
        # (同原版)
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
        self.radio_both.setEnabled(e)
        self.radio_long_only.setEnabled(e)
        self.radio_short_only.setEnabled(e)
        self.dyn_add_btn.setEnabled(True)

    def manual_buy(self):
        self.manual_trade("BUY")
    
    def manual_sell(self):
        self.manual_trade("SELL")

    def manual_trade(self, side):
        if self.last_price <= 0:
            self.append_log("❌ [錯誤] 無法取得當前價格，請確認左上角價格是否在跳動。")
            return
        params = self.get_params()
        self.append_log(f"🚀 開始執行手動 {side} 測試...")
        
        # [優化] 清理已完成的 worker
        self.manual_workers = [w for w in self.manual_workers if w.is_running]

        for acc in self.account_data:
            nick = acc.get('nickname', '未命名')
            try:
                client = Client(decrypt_text(acc['api_key']), decrypt_text(acc['secret_key']), testnet=self.is_testnet)
                # [修改] 傳入 Symbol
                w = TradingWorker(client, params, self.symbol)
                w.log_update.connect(lambda m, n=nick: self.append_log(f"【{n}】 {m}"))
                self.manual_workers.append(w)
                # 設定偽狀態讓 Worker 不會被回收 (這裡簡單用 is_running 標記)
                w.is_running = True 
                threading.Thread(target=self._run_manual_task, args=(w, self.last_price, side), daemon=True).start()
            except Exception as e:
                self.append_log(f"❌ 【{nick}】初始化失敗: {e}")

    def _run_manual_task(self, worker, price, side):
        worker.execute_entry(price, side, True)
        worker.is_running = False # 任務結束

    def get_params(self):
        # (同原版)
        p = {k: float(v.text()) for k, v in self.inputs.items()}
        p['order_mode'] = "FIXED" if self.radio_fixed.isChecked() else "PERCENT"
        p['fixed_qty'] = self.spin_fixed.value()
        p['trade_pct'] = self.spin_pct.value()
        if self.radio_long_only.isChecked():
            p['direction'] = "LONG"
        elif self.radio_short_only.isChecked():
            p['direction'] = "SHORT"
        else:
            p['direction'] = "BOTH"
        return p
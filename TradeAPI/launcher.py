import sys
from PySide6.QtWidgets import QApplication, QDialog, QInputDialog
from main_ui import AccountManager, MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 1. 先登入/管理帳號
    mgr = AccountManager()
    if mgr.exec() == QDialog.Accepted and mgr.accounts:
        
        # 2. 詢問要交易的幣種
        items = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
        symbol, ok = QInputDialog.getItem(None, "選擇幣種", "請選擇要交易的合約:", items, 0, False)
        
        if ok and symbol:
            # 3. 啟動主視窗
            window = MainWindow(mgr.accounts, mgr.testnet_chk.isChecked(), symbol)
            window.show()
            sys.exit(app.exec())
import sys
from PySide6.QtWidgets import QApplication, QDialog
from main_ui import AccountManager, MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 1. 開啟帳戶管理器
    mgr = AccountManager()
    
    # 無論是按「進入控制台」還是直接關閉，只要有帳號就嘗試開啟主視窗
    if mgr.exec() == QDialog.Accepted or mgr.accounts:
        if mgr.accounts:
            # 2. 直接啟動主視窗，不需要再選擇幣種
            window = MainWindow(mgr.accounts, mgr.testnet_chk.isChecked())
            window.show()
            sys.exit(app.exec())
        else:
            sys.exit()
    else:
        sys.exit()
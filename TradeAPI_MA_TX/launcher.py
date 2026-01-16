import sys
import comtypes.client
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QTimer
from main_ui import MainWindow, LoginDialog # 記得匯入 LoginDialog
import tkinter as tk

if __name__ == "__main__":
    # 1. 建立隱藏的 Tkinter 視窗跑訊息泵
    temp_root = tk.Tk()
    temp_root.withdraw()

    # 2. 啟動 PySide6
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # --- [新增] 先跳出登入視窗 ---
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        # 登入成功才開啟主視窗
        window = MainWindow()
        window.show()

        # 3. 定時器：驅動群益 API 事件
        timer = QTimer()
        timer.timeout.connect(lambda: comtypes.client.PumpEvents(0.005))
        timer.start(10)

        sys.exit(app.exec())
    else:
        # 取消登入則直接結束
        sys.exit()
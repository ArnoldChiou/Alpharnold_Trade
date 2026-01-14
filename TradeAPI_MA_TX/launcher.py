import sys
import comtypes.client
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from main_ui import MainWindow
import tkinter as tk

if __name__ == "__main__":
    # 1. 建立隱藏的 Tkinter 視窗跑訊息泵 (與獨立腳本環境一致)
    temp_root = tk.Tk()
    temp_root.withdraw()

    # 2. 啟動 PySide6
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()

    # 3. 定時器：頻繁呼叫 PumpEvents 來驅動群益 API 的回傳事件
    timer = QTimer()
    # 增加頻率到 10ms，確保報價不延遲
    timer.timeout.connect(lambda: comtypes.client.PumpEvents(0.005))
    timer.start(10)

    sys.exit(app.exec())
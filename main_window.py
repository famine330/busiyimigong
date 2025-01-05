import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("运行脚本")
        self.setGeometry(100, 100, 300, 150)

        # 创建按钮并绑定点击事件
        self.run_button = QPushButton("SL永恒套装", self)
        self.run_button.clicked.connect(self.run_script)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.run_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_script(self):
        try:
            # 获取当前脚本所在的目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建要运行的脚本的完整路径
            script_path = os.path.join(script_dir, 'sl_equip.py')
            # 使用subprocess运行脚本
            subprocess.run(['python', script_path], check=True)
            QMessageBox.information(self, "成功", "脚本已成功运行")
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "错误", "脚本运行失败")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
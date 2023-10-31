from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.label1 = QLabel('Label 1', self)
        self.label2 = QLabel('Label 2', self)
        self.label3 = QLabel('Label 3', self)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label1, stretch=1)  # 占1份空间
        self.layout.addWidget(self.label2, stretch=2)  # 占2份空间
        self.layout.addWidget(self.label3, stretch=1)  # 占1份空间

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

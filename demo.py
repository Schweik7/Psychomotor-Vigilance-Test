from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class BaseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel('Common Label', self)
        self.button = QPushButton('Common Button', self)
        self.button.clicked.connect(self.on_button_clicked)
        self.init_ui()
        self.cnt=0

    def init_ui(self):
        pass

    def on_button_clicked(self):
        self.cnt+=1
        print('Button clicked',self.cnt)
class Layout1(BaseWidget):
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

class Layout2(BaseWidget):
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.addWidget(self.label)
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)

        self.layout1 = Layout1()
        self.layout2 = Layout2()

        self.stackedWidget.addWidget(self.layout1)
        self.stackedWidget.addWidget(self.layout2)

        self.toolbar = self.addToolBar('Switch Layout')
        self.switch_button = QPushButton('Switch Layout')
        self.toolbar.addWidget(self.switch_button)
        self.switch_button.clicked.connect(self.switch_layout)

    def switch_layout(self):
        current_index = self.stackedWidget.currentIndex()
        self.stackedWidget.setCurrentIndex(1 - current_index)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

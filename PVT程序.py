import sys
import random
import time
import shelve
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QDesktopWidget,
    QTableWidgetItem,
    QTableWidget,
    QComboBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QFont
import numpy as np

TEST_CNT = 3  # 测试次数

RAND_MIN_TIME = 1000
RAND_MAX_TIME = 4000
font = QFont("LXGW WenKai", 16)
DEBUG = True
# TODO：1.框要大；2.不能有字；3.

class PVT(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.response_times = []  # 存储反应时间的列表
        self.combo_count = 0  # 连续小于300ms的反应次数
        self.max_combo = 0  # 最大连续反应次数
        self.timer = QTimer()  # 计时器，用于控制红色方块的显示
        self.timer.timeout.connect(self.displayRed)  #
        self.start_time = None  # 开始计时的时间
        self.is_red_displayed = False  # 红色方块是否正在显示
        self.is_test_started = False  # 测试是否已经开始
        self.mistakes = 0
        self.fastest_10_percent = []
        self.slowest_10_percent = []
        self.median_response_time = 0
        self.false_clicks = 0
        self.first_response_false = None

    def analyzeResults(self):
        # "编号",  "测试次数",  "平均反应时间", "中位数反应时间", "最大Combo数",  "失误（慢于500ms）次数",
        #  "错误点击次数",    "最快时间",       "最慢时间",            ]
        with shelve.open("pvt_results") as db:
            self.results_table.setRowCount(len(db))
            for i, (key, results) in enumerate(db.items()):
                self.results_table.setItem(i, 0, QTableWidgetItem(key))
                self.results_table.setItem(
                    i, 1, QTableWidgetItem(str(len(results["反应时间列表"])))
                )
                self.results_table.setItem(
                    i, 2, QTableWidgetItem(f'{results["平均反应时间"]:.2f}')
                )
                self.results_table.setItem(
                    i, 3, QTableWidgetItem(f'{results["中位数反应时间"]:.2f}')
                )
                self.results_table.setItem(
                    i, 4, QTableWidgetItem(str(results["最大Combo数"]))
                )
                self.results_table.setItem(
                    i, 5, QTableWidgetItem(str(results["失误（慢于500ms）次数"]))
                )
                self.results_table.setItem(
                    i, 6, QTableWidgetItem(str(results["错误点击次数"]))
                )
                self.results_table.setItem(i, 7, QTableWidgetItem(str(results["最快时间"])))
                self.results_table.setItem(i, 8, QTableWidgetItem(str(results["最慢时间"])))
                self.results_table.setItem(
                    i, 9, QTableWidgetItem(str(results["初次点击是否错误"]))
                )

    def initUI(self):
        # 设置布局和界面元素
        self.layout = QVBoxLayout()

        self.name_label = QLabel("请输入你的编号:")
        self.layout.addWidget(self.name_label)

        self.name_edit = QLineEdit(self)
        self.layout.addWidget(self.name_edit)

        self.start_button = QPushButton("开始测试", self)
        self.start_button.clicked.connect(self.startTest)
        self.start_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; }"
        )
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("终止测试", self)
        self.stop_button.clicked.connect(self.stopTest)
        self.stop_button.setDisabled(True)  # 初始状态下“终止测试”按钮不可用
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; }"
        )
        self.layout.addWidget(self.stop_button)

        self.stop_and_show_button = QPushButton("终止测试并展示结果", self)
        self.stop_and_show_button.clicked.connect(self.stopTestAndShowResults)
        self.stop_and_show_button.setDisabled(True)  # 初始状态下“终止测试并展示结果”按钮不可用
        self.stop_and_show_button.setStyleSheet(
            "QPushButton { background-color: #ffeb3b; color: green; }"
        )
        self.layout.addWidget(self.stop_and_show_button)

        self.red_label = QLabel(self)
        self.red_label.setFixedSize(200, 200)
        self.red_label.setStyleSheet("background-color: red; border-radius: 100px;")
        self.red_label.setAlignment(Qt.AlignCenter)
        self.red_label.hide()
        self.layout.addWidget(self.red_label)

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setFixedHeight(150)  # 设置文本框的高度
        self.layout.addWidget(self.result_text)

        self.setLayout(self.layout)
        screen_size = QApplication.primaryScreen().size()
        width = screen_size.width() * 1.5 / 2
        height = screen_size.height() * 1.5 / 2
        self.setGeometry(
            int((screen_size.width() - width) / 2),
            int((screen_size.height() - height) / 2),
            int(width),
            int(height),
        )
        self.setWindowTitle("Psychomotor Vigilance Test V2023.10——by Meng")
        self.show()

        # self.copy_button = QPushButton("复制选中成绩", self)
        # self.copy_button.clicked.connect(self.copyResults)
        # self.layout.addWidget(self.copy_button)
        self.analysis_button = QPushButton("成绩分析", self)
        self.analysis_button.clicked.connect(self.analyzeResults)
        self.analysis_button.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; }"
        )
        self.layout.addWidget(self.analysis_button)

        self.results_table = QTableWidget(self)
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels(
            [
                "编号",
                "测试次数",
                "平均反应时间",
                "中位数反应时间",
                "最大Combo数",
                "失误（慢于500ms）次数",
                "错误点击次数",
                "最快时间",
                "最慢时间",
                "初次点击是否错误",
            ]
        )
        self.results_table.setSortingEnabled(True)  # 启用排序
        self.layout.addWidget(self.results_table)  # 添加到布局中

        self.test_type_combo = QComboBox(self)
        self.test_type_combo.addItems(["按次数测试", "按时间测试（分钟）"])
        self.test_type_combo.setFont(font)
        self.test_type_combo.currentIndexChanged.connect(self.updateTestType)
        self.layout.addWidget(self.test_type_combo)

        self.test_input = QLineEdit(self)
        self.test_input.setPlaceholderText("输入次数或时间")
        self.layout.addWidget(self.test_input)

        self.status_label = QLabel("等待开始...", self)
        self.layout.addWidget(self.status_label)

        self.widgets = [
            self.start_button,
            self.stop_button,
            self.stop_and_show_button,
            self.result_text,
            self.test_input,
            self.name_edit,
            self.name_label,
            self.analysis_button,
            self.status_label,
        ]
        for widget in self.widgets:
            widget.setFont(font)

        self.start_button.setMinimumSize(150, 30)  # 150 是宽度, 50 是高度。你可以根据需要进行调整
        self.stop_button.setMinimumSize(150, 30)
        self.stop_and_show_button.setMinimumSize(150, 30)

    def copyResults(self):
        selected_range = self.results_table.selectedRanges()[0]  # 获取选中的区域
        copied_text = ""
        for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
            row_text = ""
            for col in range(
                selected_range.leftColumn(), selected_range.rightColumn() + 1
            ):
                item = self.results_table.item(row, col)
                if item and item.text():
                    row_text += item.text() + "\t"  # 制表符分隔每列
            row_text = row_text.rstrip("\t")  # 删除最后一个制表符
            copied_text += row_text + "\n"  # 换行符分隔每行
        copied_text = copied_text.rstrip("\n")  # 删除最后一个换行符
        QApplication.clipboard().setText(copied_text)  # 将文本复制到剪贴板

    def updateTestType(self):
        if self.test_type_combo.currentText() == "按次数测试":
            self.test_input.setPlaceholderText("输入测试次数")
            self.test_input.setText("20")
        else:
            self.test_input.setPlaceholderText("按时间测试（分钟）")
            self.test_input.setText("3")

    def mousePressEvent(self, event):
        # 捕捉鼠标点击事件
        if self.is_red_displayed and self.red_label.geometry().contains(event.pos()):
            self.captureResponse()
        if not self.is_red_displayed and self.is_test_started:
            self.false_clicks += 1
            if self.first_response_false is None:
                self.first_response_false = True
            else:
                self.first_response_false = False

    def keyPressEvent(self, event):
        # 捕捉键盘事件
        if event.key() == Qt.Key_Space and self.is_red_displayed:
            self.captureResponse()
            self.name_edit.setFocus()  # 将焦点设置到其他控件上，防止“开始测试”按钮被触发

    def startTest(self):
        self.is_test_started = True
        self.response_times = []
        self.combo_count = 0
        self.max_combo = 0
        self.result_text.clear()
        self.result_text.append("测试开始，请准备...")

        test_type = self.test_type_combo.currentText()
        test_input = float(self.test_input.text())

        if test_type == "按次数测试":
            try:
                self.target_count = int(test_input)
                self.result_text.append(f"目标测试次数：{self.target_count}")
            except ValueError:
                self.result_text.append("请输入有效的测试次数")
                self.is_test_started = False
                return
            # self.timer.timeout.connect(self.updateTimeTest) # 按次数不需要更新剩余时间
            self.timer.start(random.randint(RAND_MIN_TIME, RAND_MAX_TIME))

        elif test_type == "按时间测试（分钟）":
            try:
                self.target_time = float(test_input * 60)  # 转换为秒
                self.result_text.append(f"目标测试时间：{self.target_time}")
            except ValueError:
                self.result_text.append("请输入有效的测试时间")
                self.is_test_started = False
                return
            self.test_start_time = time.time()  # 如果按时间测试，需要记录下最开始的测试时间
            self.timer.timeout.connect(self.updateTimeTest)
            self.timer.start(random.randint(RAND_MIN_TIME, RAND_MAX_TIME))
        # self.displayRed() # 第一次呈现
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(False)
        self.stop_and_show_button.setDisabled(False)

    def updateTimeTest(self):
        elapsed_time = time.time() - self.test_start_time  # 所有流逝的时间
        if elapsed_time >= self.target_time:
            self.finishTest()
        else:
            self.status_label.setText(
                "剩余时间: {:.0f}s".format(self.target_time - elapsed_time)
            )

    def stopTest(self):
        # 终止测试
        if self.is_test_started:
            self.is_test_started = False
            self.is_red_displayed = False
            self.red_label.hide()
            self.timer.stop()
            self.result_text.append("\n测试被终止。")
            self.start_button.setDisabled(False)  # 使“开始测试”按钮可用
            self.stop_button.setDisabled(True)  # 使“终止测试”按钮不可用
            self.stop_and_show_button.setDisabled(True)  # 使“终止测试并展示结果”按钮不可用

    def stopTestAndShowResults(self):
        # 终止测试并展示结果
        self.stopTest()
        if len(self.response_times) > 0:
            self.finishTest()

    def displayRed(self):
        # 显示红色方块
        self.red_label.show()
        self.start_time = time.time()
        self.is_red_displayed = True

    def captureResponse(self):
        # 捕捉反应
        self.red_label.hide()
        self.is_red_displayed = False
        response_time = (time.time() - self.start_time) * 1000  # 将反应时间转换为毫秒
        self.response_times.append(response_time)
        if DEBUG:
            self.result_text.append("反应时间: {:.2f} ms".format(response_time))

        if response_time < 300:
            self.combo_count += 1
        else:
            self.max_combo = max(self.combo_count, self.max_combo)
            self.combo_count = 0

        if (
            self.test_type_combo.currentText() == "按次数测试"
            and len(self.response_times) == self.target_count
        ):
            self.finishTest()

    def finishTest(self):
        # 完成测试
        self.is_test_started = False
        self.timer.stop()
        self.stop_button.setDisabled(True)  # 测试结束后，使“终止测试”按钮不可用
        self.stop_and_show_button.setDisabled(True)  # 测试结束后，使“终止测试并展示结果”按钮不可用
        self.max_combo = max(self.combo_count, self.max_combo)
        if DEBUG:
            self.result_text.append("\n所有反应时间: {}".format(self.response_times))

        with shelve.open("pvt_results") as db:
            db[self.name_edit.text()] = {
                "反应时间列表": self.response_times,
                "平均反应时间": np.mean(self.response_times),
                "最大Combo数": self.max_combo,
                "错误点击次数": self.false_clicks,
                "中位数反应时间": np.median(self.response_times),
                "最快时间": min(self.response_times),
                "最慢时间": max(self.response_times),
                "失误（慢于500ms）次数": len(
                    list(filter(lambda x: x >= 500, self.response_times))
                ),
                "初次点击是否错误": self.first_response_false,
            }
        self.start_button.setDisabled(False)
        self.status_label.setText("测试完成")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pvt = PVT()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QHBoxLayout, QLabel,QSpacerItem,QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layoutMain = QVBoxLayout()

        #위쪽 레이아웃
        layout1 = QHBoxLayout()
        spacerTop = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        labelTitle = QLabel('제목', self)
        labelTitle.setFixedSize(50 ,30)
        font = QFont()
        font.setPointSize(15)  # 폰트 크기를 15포인트로 설정
        labelTitle.setFont(font)  # 폰트 설정 적용
        spacerBottom = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout1.addItem(spacerTop)
        layout1.addWidget(labelTitle)
        layout1.addItem(spacerBottom)

        #아래쪽 레이아웃
        layout2= QVBoxLayout()
        labelContent = QLabel('이곳에 내용을 입력하세요.', self)
        labelContent2 = QLabel('1+1=2',self)
        layout2.addWidget(labelContent)
        layout2.addWidget(labelContent2)

        #두 레이아웃을 메인 레이아웃에 추가
        layoutMain.addLayout(layout1)
        layoutMain.addLayout(layout2)

        self.setLayout(layoutMain)

        self.setWindowTitle('My App')
        self.setGeometry(300, 300, 300, 200)
        self.show()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
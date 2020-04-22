import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLabel

def window():
    app = QApplication(sys.argv)
    widget = QWidget()
    label = QLabel(widget)
    label.setText('Hello world!')
    widget.setGeometry(100, 100, 200, 50)
    label.move(50, 20)
    widget.setWindowTitle('PyQt')
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    window()
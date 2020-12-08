from PySide2 import QtWidgets

VERSION = "0.1"

ABOUT = f"""CsvTable v{VERSION}

Logiciel sous licence GPL

Developpé par David C

Librairies :
Qt
PySide2
fbs
Numpy
Pandas


Icons made by Freepik from www.flaticon.com"""


def show_about(logo):
    """Show the about dialog"""
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle("A propos")
    msg_box.setText(ABOUT)
    msg_box.setIconPixmap(logo)
    msg_box.exec_()

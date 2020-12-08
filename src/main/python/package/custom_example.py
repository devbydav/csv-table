"""This is an example for custom.py. It is used if custom.py file doesn't exist"""
from PySide2 import QtWidgets

from package.api.exceptions import CustomError


class Custom:
    def __init__(self, config):
        self._config = config

    def table_view_double_clicked(self, item, row_index, df, extension):
        print(f"Copied {item.data()} to clipboard")
        QtWidgets.QApplication.clipboard().setText(item.data())

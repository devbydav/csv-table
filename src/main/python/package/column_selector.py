import logging

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

logger = logging.getLogger(__name__)

COLOR_INDEX = QtGui.QColor(153, 38, 0)
COLOR_COMPARE = QtGui.QColor(65, 0, 128)
COLOR_DISPLAY = QtGui.QColor(27, 126, 77)
COLOR_IGNORE = QtGui.QColor(59, 59, 59)

STR_TITLE = "Sélection des colonnes à masquer"
STR_VALIDATE = "Valider"
STR_TOGGLE = ["Tout sélectionner", "Tout désélectionner"]


class ColumnSelector(QtWidgets.QWidget):
    validated = Signal()

    def __init__(self, csv_set, config, ctx):
        super().__init__()
        self._csv_set = csv_set
        self._config = config
        self._ctx = ctx
        self._available_columns = csv_set.available_columns  # list
        self._undesired_columns = config.undesired_columns  # set

        self.resize(1000, 800)
        self.setWindowTitle(STR_TITLE)

        self._toggle_status = False  # status of the toggle btn and index of its STR

        # create widgets
        self._toggle_selection_btn = QtWidgets.QPushButton(STR_TOGGLE[0])
        self._list_widget = QtWidgets.QListWidget()
        self._validate_btn = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(self._ctx.get_resource("tick.svg"))),
                                                   STR_VALIDATE)

        # create layouts
        self._main_layout = QtWidgets.QVBoxLayout(self)

        # modify widgets
        self._toggle_selection_btn.setFixedWidth(200)
        self._validate_btn.setMaximumWidth(100)

        # add widgets to layouts
        self._main_layout.addWidget(self._toggle_selection_btn, alignment=QtCore.Qt.AlignCenter)
        self._main_layout.addWidget(self._list_widget)
        self._main_layout.addWidget(self._validate_btn, alignment=QtCore.Qt.AlignCenter)

        # populate list widget
        for column in self._available_columns:
            item = QtWidgets.QListWidgetItem(column)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked if column in self._undesired_columns else QtCore.Qt.Unchecked)
            self._list_widget.addItem(item)

        # set connections
        self._list_widget.itemPressed.connect(lambda i: i.setCheckState(
            QtCore.Qt.Checked if i.checkState() == QtCore.Qt.Unchecked else QtCore.Qt.Unchecked))
        self._toggle_selection_btn.clicked.connect(self._toggle_selection)
        self._validate_btn.clicked.connect(self._validate)

    def _toggle_selection(self):
        self._toggle_status = not self._toggle_status
        new_status = QtCore.Qt.Checked if self._toggle_status else QtCore.Qt.Unchecked
        self._toggle_selection_btn.setText(STR_TOGGLE[self._toggle_status])
        self._toggle_selection_btn.adjustSize()
        for i in range(self._list_widget.count()):
            self._list_widget.item(i).setCheckState(new_status)

    def _validate(self):
        selected_columns = [self._list_widget.item(index).text() for index in range(self._list_widget.count())
                            if self._list_widget.item(index).checkState() == QtCore.Qt.Checked]

        self._config.undesired_columns = selected_columns
        self._config.hide_undesired = True if selected_columns else False

        self.hide()
        self.validated.emit()

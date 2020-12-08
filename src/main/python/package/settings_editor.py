from PySide2 import QtWidgets, QtCore, QtGui

from package.api.exceptions import ConfigSettingError

STR_CANCEL = "Annuler"
STR_VALIDATE = "Valider"
STR_WINDOW_TITLE = "Paramètres CSV"


STR_ENCODING = "Encodage"
STR_COMMENT = "Commentaire"
STR_HEADER = "Nb lignes avant en-tête"
STR_SEPARATOR = "Séparateur"
STR_MAX_LINES = "Nb max de lignes"
STR_SKIP_BLANK_LINES = "Ignorer les lignes vides"
STR_HIDE_EMPTY = "Masquer les colonnes vides"
STR_HIDE_UNDESIRED = "Masquer les colonnes indésirables"


class SettingsEditor(QtWidgets.QWidget):
    validated = QtCore.Signal()
    reload_csv = QtCore.Signal()

    def __init__(self, ctx, config, csv_set):
        super().__init__()

        self._csv_set = csv_set
        self._config = config
        self.setWindowTitle(STR_WINDOW_TITLE + " " + config.csv_extension)

        # create labels
        self._info_lbl = QtWidgets.QLabel()

        # create lineedits
        self._encoding_le = QtWidgets.QLineEdit(self._config.encoding)
        self._comment_le = QtWidgets.QLineEdit(self._config.comment)
        self._header_le = QtWidgets.QLineEdit(str(self._config.header))
        self._separator_le = QtWidgets.QLineEdit(self._config.separator)
        self._max_lines_le = QtWidgets.QLineEdit(str(self._config.max_lines))
        self._skip_blank__lines_le = QtWidgets.QCheckBox()
        self._hide_empty_le = QtWidgets.QCheckBox()
        self._hide_undesired_le = QtWidgets.QCheckBox()

        # create buttons
        self._cancel_btn = QtWidgets.QPushButton(STR_CANCEL)
        self._validate_btn = QtWidgets.QPushButton(STR_VALIDATE)

        # create layouts
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._form_layout = QtWidgets.QFormLayout()
        self._buttons_layout = QtWidgets.QHBoxLayout()

        # modify widgets
        self._skip_blank__lines_le.setChecked(self._config.skip_blank_lines)
        self._hide_empty_le.setChecked(self._config.hide_empty)
        self._hide_undesired_le.setChecked(self._config.hide_undesired)
        self._cancel_btn.setIcon(QtGui.QIcon(QtGui.QPixmap(ctx.get_resource("cross.svg"))))
        self._cancel_btn.setMaximumWidth(100)
        self._validate_btn.setIcon(QtGui.QIcon(QtGui.QPixmap(ctx.get_resource("tick.svg"))))
        self._validate_btn.setMaximumWidth(100)

        self._encoding_le.setMaximumWidth(80)
        self._max_lines_le.setMaximumWidth(80)
        self._comment_le.setMaximumWidth(50)
        self._header_le.setMaximumWidth(50)
        self._separator_le.setMaximumWidth(50)

        # add widgets to form layout
        self._form_layout.addRow(STR_ENCODING, self._encoding_le)
        self._form_layout.addRow(STR_MAX_LINES, self._max_lines_le)
        self._form_layout.addRow(STR_COMMENT, self._comment_le)
        self._form_layout.addRow(STR_HEADER, self._header_le)
        self._form_layout.addRow(STR_SEPARATOR, self._separator_le)
        self._form_layout.addRow(STR_SKIP_BLANK_LINES, self._skip_blank__lines_le)
        self._form_layout.addRow(STR_HIDE_EMPTY, self._hide_empty_le)
        self._form_layout.addRow(STR_HIDE_UNDESIRED, self._hide_undesired_le)

        # add widgets to main layout
        self._main_layout.addWidget(self._info_lbl)
        self._main_layout.addLayout(self._form_layout)
        self._main_layout.addLayout(self._buttons_layout)

        self._buttons_layout.addWidget(self._cancel_btn)
        self._buttons_layout.addWidget(self._validate_btn)

        self.setup_connections()

    def setup_connections(self):
        self._cancel_btn.clicked.connect(self.cancel)
        self._validate_btn.clicked.connect(self.validate)

    def cancel(self):
        self.close()

    def validate(self):
        try:
            self._config.encoding = self._encoding_le.text()
            self._config.comment = self._comment_le.text()
            self._config.header = self._header_le.text()
            self._config.separator = self._separator_le.text()
            self._config.max_lines = self._max_lines_le.text()
            self._config.skip_blank_lines = self._skip_blank__lines_le.isChecked()
            self._config.hide_empty = self._hide_empty_le.isChecked()
            self._config.hide_undesired = self._hide_undesired_le.isChecked()

        except ConfigSettingError as e:
            self._info_lbl.setText(str(e))
            self._info_lbl.adjustSize()
        else:
            self.hide()
            self.validated.emit()

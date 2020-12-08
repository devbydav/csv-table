import pathlib
import logging

from PySide2 import QtWidgets, QtCore, QtGui, QtSvg
from PySide2.QtCore import Slot

import package.api.logger
from package.about import show_about
from package.settings_editor import SettingsEditor
from package.column_selector import ColumnSelector
from package.main_table import MainTableModel
from package.api.csv_set import CsvSet
from package.api.config import Config
from package.api.filtering import FilterManager
from package.api.exceptions import FilterInvalidError, CustomError

try:
    from package.custom import Custom
except ModuleNotFoundError:
    from package.custom_example import Custom

logger = logging.getLogger(__name__)


STR_WINDOW_TITLE = "CSV Table"
STR_TB_ACTION_OPEN = "Ouvrir un fichier"
STR_TB_ACTION_EDIT_SETTINGS = "Paramètres"
STR_TB_ACTION_SHOW_ABOUT = "Legal"


class LogoWidget(QtSvg.QSvgWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)

    def heightForWidth(self, w):
        return w*2

    def hasHeightForWidth(self):
        return True


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ctx, file_path_strs):
        super().__init__()

        self.setWindowTitle(STR_WINDOW_TITLE)

        self.ctx = ctx

        self._ICON_OPEN = QtGui.QIcon(QtGui.QPixmap(ctx.get_resource("document.svg")))
        self._ICON_SAVE = QtGui.QIcon(QtGui.QPixmap(ctx.get_resource("save.svg")))
        self._ICON_ABOUT = QtGui.QIcon(QtGui.QPixmap(ctx.get_resource("question.svg")))

        self._config = Config()
        self._csv_set = CsvSet(config=self._config)
        self._filter_manager = FilterManager(icon_on=QtGui.QIcon(QtGui.QPixmap(self.ctx.get_resource("dot_on.svg"))),
                                             icon_off=QtGui.QIcon(QtGui.QPixmap(self.ctx.get_resource("dot_off.svg"))))
        self._table_model = None
        self._completer = None
        self._timer = QtCore.QTimer()

        # create widgets
        self._main_menu = self.menuBar()
        self._main_widget = QtWidgets.QWidget()
        self._info_lbl = QtWidgets.QLabel("Déposer le fichier dans l'interface")
        self._filter_le = QtWidgets.QLineEdit()
        self._logo_widget = LogoWidget(ctx.get_resource("images/stork.svg"))
        self._csv_widget = QtWidgets.QWidget()
        self._table_view = QtWidgets.QTableView()
        self._raz_btn = QtWidgets.QPushButton("RAZ")
        self._pop_menu = QtWidgets.QMenu(self)
        self._neg_cb = QtWidgets.QCheckBox("Neg")
        self._action_remove_btn = QtWidgets.QAction("Supprimer", self)

        # create layouts
        self._main_layout = QtWidgets.QVBoxLayout(self._main_widget)
        self._csv_layout = QtWidgets.QVBoxLayout()
        self._filtering_layout = QtWidgets.QHBoxLayout()

        # modify menu
        self._file_menu = self._main_menu.addMenu("&Fichier")
        self._open_file_action = self._file_menu.addAction(self._ICON_OPEN, "&Ouvrir un fichier")
        self._edit_settings_action = self._file_menu.addAction(self._ICON_SAVE, "&Modifier les paramètres")
        self._columns_menu = self._main_menu.addMenu("&Colonnes")
        self._columns_edit_undesired_action = self._columns_menu.addAction("&Editer les colonnes à masquer")
        self._help_menu = self._main_menu.addMenu('&Aide')
        self._show_about_action = self._help_menu.addAction(self._ICON_ABOUT, "&A propos ...")

        # modify other widgets
        self._csv_widget.setLayout(self._csv_layout)
        self._logo_widget.setMaximumSize(400, 500)
        self._csv_widget.hide()
        self._table_view.setSortingEnabled(True)
        self._pop_menu.addAction(self._action_remove_btn)
        self.setAcceptDrops(True)

        # add widgets to layouts
        self.setCentralWidget(self._main_widget)
        self._main_layout.setAlignment(QtCore.Qt.AlignCenter)
        self._main_layout.addWidget(self._info_lbl)
        self._main_layout.addWidget(self._logo_widget)
        self._filtering_layout.addWidget(self._neg_cb)
        self._filtering_layout.addWidget(self._filter_le)
        self._filtering_layout.addWidget(self._raz_btn)
        self._csv_layout.addLayout(self._filtering_layout)
        self._csv_layout.addWidget(self._table_view)
        self._main_layout.addWidget(self._csv_widget)

        self._info_lbl.hide()

        # setup connections
        self._open_file_action.triggered.connect(self._open_file_clicked)
        self._edit_settings_action.triggered.connect(self._show_settings)
        self._columns_edit_undesired_action.triggered.connect(self._edit_undesired_columns)
        self._show_about_action.triggered.connect(self._show_about)
        self._filter_le.returnPressed.connect(self._filter_entered)
        self._raz_btn.clicked.connect(self._filter_raz)
        self._action_remove_btn.triggered.connect(self._filter_remove_btn)
        self._table_view.doubleClicked.connect(self._table_view_double_clicked)

        self._config.load_gen_config()
        self._custom = Custom(self._config.custom)

        if file_path_strs:
            self._read_files(file_path_strs)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self._info_lbl.show()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._info_lbl.hide()

    def dropEvent(self, event):
        self._info_lbl.hide()
        if event.mimeData().hasUrls():
            event.accept()
            self._read_files([str(url.toLocalFile()) for url in event.mimeData().urls()])

    # def _close_files(self):
    #     """Closes all opened files"""
    #     self._csv_set = None
    #     self._table_model.clear()
    #     self._completer = None

    def _edit_undesired_columns(self):
        """Actions when edit undesirable columns in menu has been clicked"""
        if not self._csv_set.extension:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Aucun fichier ouvert")
            return
        self._columns_selector = ColumnSelector(csv_set=self._csv_set, config=self._config, ctx=self.ctx)
        self._columns_selector.validated.connect(self._save_columns_preferences)
        self._columns_selector.show()

    def _filter_btn_clicked(self):
        """Actions when filter button has been left-clicked"""
        self._filter_manager.toggle_filter(self.sender().text())
        self.statusBar().showMessage(self._table_model.hits)

    def _filter_btn_right_clicked(self, point):
        """Actions when filter button has been right-clicked"""
        sender_btn = self.sender()
        self._last_right_clicked_btn = sender_btn
        self._pop_menu.exec_(sender_btn.mapToGlobal(point))

    def _filter_entered(self):
        """Actions when Enter key pressed in filter lineedit"""
        text = self._filter_le.text()

        nb_operators = text.count(":") + text.count(">") + text.count("<")

        if nb_operators == 0:
            if self._completer and self._completer.currentRow() > -1:
                column = self._completer.currentCompletion()

                if column in self._table_model.string_columns:
                    self._filter_le.setText(column + " : ")
                elif column in self._table_model.numeric_columns:
                    self._filter_le.setText(column + " > ")
        else:
            try:
                new_btn = self._filter_manager.add(text, neg=self._neg_cb.isChecked())
            except FilterInvalidError as e:
                QtWidgets.QMessageBox.warning(self, "Erreur", str(e))
            else:
                new_btn.clicked.connect(self._filter_btn_clicked)
                new_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                new_btn.customContextMenuRequested.connect(self._filter_btn_right_clicked)
                self._filtering_layout.insertWidget(2, new_btn)
                self._filter_le.setText("")
                self._neg_cb.setChecked(False)
                self._update_hits()

    def _filter_raz(self):
        """Removes all filters and their buttons"""
        self._filter_manager.raz()
        self._update_hits()

    def _filter_remove_btn(self):
        """Removes the filter button that was right-clicked"""
        text = self._last_right_clicked_btn.text()
        self._filter_manager.delete(text)
        self._update_hits()

    def _open_file_clicked(self):
        """Actions when open files in menu has been clicked"""
        path_strs, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Ouvrir un fichier",
                                                              self._config.open_file_dir,
                                                              self._config.open_file_filters)
        if not path_strs:
            return

        path = pathlib.Path(path_strs[0])
        self._config.open_file_dir = str(path.resolve().parent)
        self._read_files(path_strs)

    def _read_files(self, files=None):
        """Reads csv files : new ones if arg files is provided, otherwise re-reads current ones"""
        try:
            self._csv_set.read_files(files=files)

        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Erreur", str(e))
            logger.error(e)
            logger.exception("Value error")
            # display
            self._csv_widget.hide()
            self._logo_widget.show()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erreur", str(e))
            logger.error(e)
            logger.exception("unexpected exception")
            # display
            self._csv_widget.hide()
            self._logo_widget.show()

        else:
            self._read_success()

    def _read_success(self):
        """Actions when _read_files has run without error"""
        self._table_model = MainTableModel(self._csv_set.df, self._filter_manager)
        self._filter_manager.set_model(self._table_model)
        self._filter_manager.file_opened()
        self._table_view.setModel(self._table_model)

        # self._table_view.resizeColumnsToContents()  # too slow

        self._completer = QtWidgets.QCompleter(self._table_model.df_columns)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._filter_le.setCompleter(self._completer)
        self.setWindowTitle(self._csv_set.title)

        # display
        self._logo_widget.hide()
        self._csv_widget.show()
        self._update_hits()

    def _save_columns_preferences(self):
        """Saves the column preferences"""
        self._columns_selector = None
        self._config.save_csv_config()
        self._read_files()

    def _save_settings(self):
        """Saves the settings"""
        self._settings_editor = None
        self._config.save_csv_config()
        self._read_files()

    def _show_about(self):
        """Show the about dialog"""
        show_about(logo=QtGui.QPixmap(self.ctx.get_resource("images/stork.svg")).scaledToWidth(100))

    def _show_settings(self):
        """Actions when edit settings in menu has been clicked"""
        self._settings_editor = SettingsEditor(csv_set=self._csv_set, config=self._config, ctx=self.ctx)
        self._settings_editor.validated.connect(self._save_settings)
        self._settings_editor.show()

    def _table_view_double_clicked(self, item: QtCore.QModelIndex):
        """Actions when table view is double-clicked"""
        try:
            self._custom.table_view_double_clicked(item=item,
                                                   row_index=item.model().headerData(item.row(), QtCore.Qt.Vertical),
                                                   df=self._table_model.df,
                                                   extension=self._csv_set.extension)
        except CustomError as e:
            QtWidgets.QMessageBox.warning(self, "Erreur", str(e))

    def _update_hits(self):
        self.statusBar().showMessage(self._table_model.hits)

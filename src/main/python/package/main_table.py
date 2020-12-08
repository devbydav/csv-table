from PySide2 import QtCore, QtGui

from pandas.api.types import is_numeric_dtype, is_string_dtype

from package.api.utils import log_time_it

COLOR_HIGHLIGHT = QtGui.QColor(245, 217, 188)


class MainTableModel(QtCore.QAbstractTableModel):

    @property
    def df(self):
        return self._df

    @property
    def df_columns(self):
        return self.columns

    @property
    def hits(self):
        return self._hits

    def __init__(self, df, filter_manager, parent=None):
        super().__init__(parent)

        self._filter_manager = filter_manager

        self._original_df = df
        self._df = df

        self._nb_total_lines = df.shape[0]
        self._update_hits()

        self.columns = list(df.columns)
        self.column_highlights = None

        self.numeric_columns = {col for col, dtype in zip(self.columns, df.dtypes) if is_numeric_dtype(dtype)}
        self.string_columns = {col for col, dtype in zip(self.columns, df.dtypes) if is_string_dtype(dtype)}

        # Filter details. Dict "btn text": ("enabled", "field", "query)
        self._filters = {}

        # self._np = np.array(df.values)

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._df.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._df.index[section])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            # value = self._np[index.row(), index.column()]
            return str(value)

        if role == QtCore.Qt.BackgroundRole:
            if self.column_highlights[index.column()]:
                return QtGui.QBrush(COLOR_HIGHLIGHT)

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def sort(self, column, order=QtCore.Qt.SortOrder.AscendingOrder):
        if not self._df.empty:
            colname = self._df.columns.tolist()[column]
            self.layoutAboutToBeChanged.emit()
            self._df.sort_values(colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True)
            # self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

    def add_query(self, query):
        """Add a query to the current filtered df"""
        self.layoutAboutToBeChanged.emit()
        self._df = self._df.query(query).copy()
        self.layoutChanged.emit()
        self._update_hits()

    def reset_filtering(self):
        """Refilters the data with the current active filters"""
        self.layoutAboutToBeChanged.emit()
        self._df = self._original_df
        queries_list = self._filter_manager.enabled_queries
        if queries_list:
            self._df = self._df.query(" & ".join(queries_list)).copy()
        self.layoutChanged.emit()
        self._update_hits()

    def update_highlights(self, added_col=False):
        if added_col:
            self.column_highlights[self.columns.index(added_col)] = True
        else:
            filtered = self._filter_manager.filtered_columns
            self.column_highlights = [col in filtered for col in self.columns]

    def _update_hits(self):
        """Updates the number of hits with the current active filters"""
        nb_filtered = self._df.shape[0]
        if nb_filtered == self._nb_total_lines:
            self._hits = f"{nb_filtered} lignes"
        else:
            self._hits = f"{nb_filtered} / {self._nb_total_lines} lignes"

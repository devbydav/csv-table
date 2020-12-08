import re
import logging

from PySide2 import QtCore, QtWidgets

from package.api.exceptions import FilterInvalidError

logger = logging.getLogger(__name__)


class FilterManager:

    def __init__(self, icon_on, icon_off):

        self._icon_on = icon_on
        self._icon_off = icon_off

        self._table_model = None
        self._filters = {}

    @property
    def enabled_queries(self):
        if not self._filters:
            return []
        return [filter_.query for filter_ in self._filters.values() if filter_.enabled]

    @property
    def filtered_columns(self):
        if not self._filters:
            return {}
        return {filter_.column for filter_ in self._filters.values() if filter_.enabled}

    @staticmethod
    def _parse_text(text, operator):
        """returns column and value from the raw (button) text"""
        return [v.strip() for v in text.split(operator, maxsplit=1)]

    @staticmethod
    def _prepare_numeric_query(column, value, operator):
        """Returns the number query"""
        if value == "*":
            return f"{column}.notnull()"
        try:
            value = float(value.replace(",", "."))
        except ValueError:
            raise FilterInvalidError(f"La valeur doit filtre doit être un nombre")
        return f"{column} {operator} {value}"

    @staticmethod
    def _prepare_string_query(column, value):
        """Returns the string query"""
        if value == "*":
            return f"{column}.str.match(r'^.+$')"
        value = value.replace("*", ".*").replace("?", ".?")
        return f"{column}.str.match('{value}$', case=False)"

    def add(self, text, neg):
        """Adds a new filter and returns the associated button for the UI"""
        operator = re.search(r"[<>]=?|[:=]", text).group(0)

        column, value = [v.strip() for v in text.split(operator, maxsplit=1)]

        if column not in self._table_model.df_columns:
            raise FilterInvalidError(f"{column} n'est pas une colonne de ce fichier")

        if not re.match(r"^[\w?*:,.% ]+$", value):
            raise FilterInvalidError(f"La valeur du filtre est incorrecte")

        if column in self._table_model.string_columns:
            if not re.match(r"[:=]", operator):
                raise FilterInvalidError(f"Opérateurs autorisés pour une colonne texte : ':' ou '='")
            query = self._prepare_string_query(column, value)

        elif column in self._table_model.numeric_columns:
            if not re.match(r"[<>=]", operator):
                raise FilterInvalidError(
                    f"Opérateurs autorisés pour une colonne numérique : '>', '>=', '<' ou '<='")
            query = self._prepare_numeric_query(column, value, operator)

        else:
            raise FilterInvalidError("Le filtre n'est pas valide")

        text = f"{column}{operator} {value}"

        # negate the query
        if neg:
            text = "not " + text
            query = "not " + query

        if text in self._filters:
            raise FilterInvalidError("Ce filtre existe déjà")

        filter_ = Filter(enabled=True,
                         column=column,
                         text=text,
                         query=query,
                         btn=QtWidgets.QPushButton(self._icon_on, text))

        self._filters[text] = filter_
        self._table_model.update_highlights(added_col=column)
        self._table_model.add_query(query)

        return filter_.btn

    def delete(self, text):
        """Deletes a filter"""
        if text in self._filters:
            self._filters[text].btn.deleteLater()
            del self._filters[text]
            self._table_model.update_highlights()
        self._table_model.reset_filtering()

    def file_opened(self):
        """Updates filtering when a new file is opened"""
        if self._filters:
            remove_list = []
            for filter_ in self._filters.values():
                if filter_.column in self._table_model.columns:
                    if filter_.enabled:
                        filter_.enabled = False
                        filter_.btn.setIcon(self._icon_off)
                        filter_.btn.repaint()
                else:
                    filter_.btn.deleteLater()
                    remove_list.append(filter_.text)
            for text in remove_list:
                del self._filters[text]
        self._table_model.update_highlights()

    def raz(self):
        """Deletes all filters"""
        for filter_ in self._filters.values():
            filter_.btn.deleteLater()
        self._filters = {}
        self._table_model.column_highlights = [False] * len(self._table_model.columns)
        self._table_model.reset_filtering()

    def set_model(self, model):
        """Updates the model"""
        self._table_model = model

    def toggle_filter(self, text):
        """Toggles """
        filter_ = self._filters[text]

        if filter_.enabled:
            filter_.enabled = False
            filter_.btn.setIcon(self._icon_off)
            filter_.btn.repaint()
            self._table_model.reset_filtering()
        else:
            filter_.enabled = True
            filter_.btn.setIcon(self._icon_on)
            filter_.btn.repaint()
            self._table_model.add_query(filter_.query)
        self._table_model.update_highlights()


class Filter:
    def __init__(self, enabled, text, column, query, btn):

        self.enabled = enabled
        self.text = text
        self.column = column
        self.query = query

        self.btn = btn
        self.btn.setIconSize(QtCore.QSize(10, 10))

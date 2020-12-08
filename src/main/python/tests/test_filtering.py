import unittest

import pandas as pd
from PySide2 import QtWidgets

from package.api.filtering import FilterManager
from package.main_table import MainTableModel
from package.api.exceptions import FilterInvalidError


class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.mw = QtWidgets.QApplication()

    def setUp(self) -> None:
        df = pd.DataFrame({
            "Col1": [10, 11, 12, 13, 14],
            "Col2": ["python", "rust", "javascript", "java", "c++"]
        })

        self.filter_manager = FilterManager(None, None)
        self.table_model = MainTableModel(df, self.filter_manager)
        self.filter_manager.set_model(self.table_model)
        self.filter_manager.file_opened()
        # print(df)

    def test_add_filter_string_simple(self):
        self.filter_manager.add(text="Col2 : rust", neg=False)

        df_expected = pd.DataFrame(index=[1],
                                   data={
                                       "Col1": [11],
                                       "Col2": ["rust"]
                                   })
        pd.testing.assert_frame_equal(df_expected, self.table_model.df)
        print(self.table_model.df)

    def test_add_filter_string_wildcard(self):
        self.filter_manager.add(text="Col2 : java*", neg=False)

        df_expected = pd.DataFrame(index=[2, 3],
                                   data={
                                       "Col1": [12, 13],
                                       "Col2": ["javascript", "java"]
                                   })
        pd.testing.assert_frame_equal(df_expected, self.table_model.df)
        print(self.table_model.df)

    def test_add_filter_int(self):
        self.filter_manager.add(text="Col1 < 12", neg=False)

        df_expected = pd.DataFrame(index=[0, 1],
                                   data={
                                       "Col1": [10, 11],
                                       "Col2": ["python", "rust"]
                                   })
        pd.testing.assert_frame_equal(df_expected, self.table_model.df)
        print(self.table_model.df)

    def test_filter_column_not_existing(self):
        with self.assertRaises(FilterInvalidError):
            self.filter_manager.add(text="Col3 < 12", neg=False)


if __name__ == '__main__':
    unittest.main()

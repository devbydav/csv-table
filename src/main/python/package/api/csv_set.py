import logging
import pathlib

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype

from package.api.exceptions import CsvReadError
from package.api.utils import log_time_it
from package.api.config import Config

logger = logging.getLogger(__name__)


class CsvSet:

    def __init__(self, config: Config):
        self._config = config
        self._files = None  # paths to the csv files, directories and/or files (str tuple)

        # generated
        self.df = None  # full set of data (df)
        self._available_columns = None  # columns available (including the ones not imported)
        self.df_columns = None  # columns in the imported df
        self.numeric_columns = None
        self.string_columns = None

    @property
    def available_columns(self):
        if self._files:
            df = self._read_csv(self._files[0], nrows=0)
            return list(df.columns)

    @property
    def extension(self):
        if self._files:
            return self._files[0].suffix[1:]

    @property
    def title(self):
        title = str(self._files[0])
        if len(self._files) > 2:
            title += f" + {len(self._files) - 1} autres"
        elif len(self._files) == 2:
            title += " + 1 autre"
        return title

    def __str__(self):
        return f"CSV_SET : files={self._files}\n"

    def read_files(self, files=None, append=False):
        """Reads csv files : new ones if arg files is provided, otherwise re-reads current ones"""
        # updating self.files if new files are provided
        if files:
            valid_files = []
            for file_path_str in files:
                file_path = pathlib.Path(r'{}'.format(file_path_str))
                if file_path.is_file():
                    valid_files.append(file_path)
                else:
                    logger.warning(f"Trying to open {file_path_str} but it doesn't exist")
                    raise CsvReadError(f"The file {file_path_str} does not exist")

            self._files = valid_files

            if self.extension != self._config.csv_extension:
                self._config.load_csv_config(self.extension)

        # re new files if they provided, or just re-read current ones otherwise
        if self._files:
            self.import_data()

    @log_time_it
    def import_data(self):
        """Imports the data from csv files, raises ValueError"""

        if self._config.hide_undesired:
            def usecols(col):
                return col not in self._config.undesired_columns
        else:
            usecols = None

        dfs = (self._read_csv(file, usecols=usecols, na_values=["", " ", "inv"], nrows=self._config.m_max_lines)
               for file in self._files)

        df = pd.concat(dfs, ignore_index=True, sort=False)

        if self._config.hide_empty:
            df.dropna(how='all', axis=1, inplace=True)

        self.df_columns = list(df.columns)

        self.numeric_columns = {col for col, dtype in zip(self.df_columns, df.dtypes) if is_numeric_dtype(dtype)}
        self.string_columns = {col for col, dtype in zip(self.df_columns, df.dtypes) if is_string_dtype(dtype)}

        for column in self.string_columns:
            df[column] = df[column].fillna("")

        self.df = df

    def _read_csv(self, file, usecols=None, nrows=None, na_values=None, dtype=None):
        return pd.read_csv(file, engine="python", index_col=False, usecols=usecols, na_values=na_values, dtype=dtype,
                           encoding=self._config.m_encoding, sep=self._config.m_separator, header=self._config.m_header,
                           comment=self._config.m_comment, skip_blank_lines=self._config.m_skip_blank_lines,
                           nrows=nrows)

import yaml
import logging
import pathlib

from package.api.exceptions import ConfigSettingError

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self._config_dir = pathlib.Path(__file__).resolve().parent.parent.parent / "config"
        self.open_file_dir = None  # directory for dialog to open new file
        self.open_file_filters = None
        self._gen_config_file = self._config_dir / "gen_config.yaml"

        self.csv_extension = None
        self.m_encoding = None  # encoding of csv files (str)
        self.m_comment = None  # single char. If found at the beginning of a line, the line will be ignored (str)
        self.m_skip_blank_lines = None  # ignore all blank lines
        self.m_header = None  # nb of lines to skip before header, after blank (if skipped) and commented
        self.m_separator = None  # separator in csv files (str)
        self.m_max_lines = None
        self.hide_empty = None
        self.hide_undesired = None
        self._undesired_columns = None  # set

        self.custom = None

    @property
    def comment(self):
        return self.m_comment or ""

    @comment.setter
    def comment(self, new):
        if not new:
            self.m_comment = None
            return
        new = str(new)
        if len(new) > 1:
            raise ConfigSettingError("Le commentaire doit être un caractère unique")
        self.m_comment = new

    @property
    def encoding(self):
        return self.m_encoding

    @encoding.setter
    def encoding(self, new):
        self.m_encoding = new

    @property
    def header(self):
        return self.m_header

    @header.setter
    def header(self, new):
        if not new:
            self.m_header = None
            return
        try:
            self.m_header = int(new)
        except ValueError:
            raise ConfigSettingError("Ce champ doit être vide ou un nombre")

    @property
    def max_lines(self):
        return self.m_max_lines or ""

    @max_lines.setter
    def max_lines(self, new):
        if not new:
            self.m_max_lines = None
            return
        try:
            self.m_max_lines = int(new)
        except ValueError:
            raise ConfigSettingError("Ce champ doit être vide ou un nombre > 0")

    @property
    def separator(self):
        if self.m_separator == "\t":
            return ""
        return self.m_separator

    @separator.setter
    def separator(self, new):
        if not new:
            self.m_separator = "\t"
        else:
            self.m_separator = str(new)

    @property
    def skip_blank_lines(self):
        return self.m_skip_blank_lines

    @skip_blank_lines.setter
    def skip_blank_lines(self, new):
        self.m_skip_blank_lines = bool(new)

    @property
    def undesired_columns(self):
        return self._undesired_columns

    @undesired_columns.setter
    def undesired_columns(self, new):
        try:
            self._undesired_columns = set(new)
        except ValueError:
            logger.warning(f"Cannot convert {new} to set")

    def set_config(self, encoding="latin_1", comment="", skip_blank_lines=False, header=2, separator="", max_lines=5000,
                   hide_empty=True, hide_undesired=False, undesired_columns=None):

        self.encoding = encoding
        self.comment = comment
        self.skip_blank_lines = skip_blank_lines
        self.header = header
        self.separator = separator
        self.max_lines = max_lines
        self.hide_empty = hide_empty
        self.hide_undesired = hide_undesired
        self.undesired_columns = undesired_columns or set()

    def _get_csv_config_file(self, check_exists=False):
        # specific csv file
        csv_file = self._config_dir / f"config_{self.csv_extension}.yaml"
        if not check_exists or csv_file.is_file():
            return csv_file

        # default csv file
        csv_file = self._config_dir / "default_csv_config.yaml"
        if csv_file.is_file():
            return csv_file

    def load_gen_config(self):
        open_dir = None
        open_filters = None
        self.custom = None
        if self._gen_config_file.is_file():
            with open(self._gen_config_file, "r") as yaml_file:
                d = yaml.safe_load(yaml_file)
                if d:
                    open_dir = d.get("dir")
                    open_filters = d.get("filters")
                    self.custom = d.get("custom")

        self.open_file_dir = open_dir or str(pathlib.Path.home())
        self.open_file_filters = ";;".join(open_filters) if open_filters else "Csv (*.csv);;All (*.*)"

    def load_csv_config(self, extension):
        """Loads the config for specified file extension"""
        self.csv_extension = extension

        # get the config file
        config_file = self._get_csv_config_file(check_exists=True)

        if config_file:
            # load the config
            with open(config_file, "r") as yaml_file:
                d = yaml.safe_load(yaml_file)
                if d:
                    self.set_config(**d)
                    return

        # default config if has not been loaded
        self.set_config()
        logger.warning("Loading hardcoded default csv config")

    def save_csv_config(self):
        """Saves the config for the current file extension"""

        if not self._config_dir.is_dir():
            self._config_dir.mkdir(parents=True)

        config_file = self._get_csv_config_file(check_exists=False)

        config_dict = {"encoding": self.encoding,
                       "separator": self.separator,
                       "comment": self.comment,
                       "header": self.header,
                       "skip_blank_lines": self.skip_blank_lines,
                       "max_lines": self.max_lines,
                       "hide_empty": self.hide_empty,
                       "hide_undesired": self.hide_undesired}

        if self._undesired_columns:
            config_dict["undesired_columns"] = list(self._undesired_columns)

        with open(config_file, "w") as yaml_file:
            yaml.safe_dump(config_dict, yaml_file, default_flow_style=False)

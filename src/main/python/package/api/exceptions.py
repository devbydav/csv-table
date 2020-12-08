class FilterInvalidError(Exception):
    pass


class ConfigSettingError(Exception):
    """Configuration could not be set"""
    pass


class CsvReadError(Exception):
    """Error when reading a csv file"""
    pass


class CustomError(Exception):
    """Raise this exception in case of problem with custom operation"""
    pass

import sys

from fbs_runtime.application_context.PySide2 import ApplicationContext, cached_property

from package.main_window import MainWindow

file_path_strs = sys.argv[1:] if len(sys.argv) > 1 else None


if __name__ == '__main__':
    appctxt = ApplicationContext()
    window = MainWindow(ctx=appctxt, file_path_strs=file_path_strs)
    window.resize(1000, 700)
    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
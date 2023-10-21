import logging
import datetime

class Logger:
    def __init__(self, logpath: str=None, loglevel: str=None):
        self.logpath = logpath
        self.loglevel = loglevel
        self.logger = logging.getLogger('hikvision')
        self.logger.setLevel(logging.DEBUG)

        #logfile = logpath if logpath != None else 'app.log'
        handler = None
        if logpath is None:
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(logpath)

        formatter = logging.Formatter('%(asctime)s.%(msecs)06d %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _log(self, level: int, msg: str):
        self.logger.log(level, msg)

    def log_info(self, msg: str):
        self._log(logging.INFO, msg)

    def log_debug(self, msg: str):
        self._log(logging.DEBUG, msg)

    def log_error(self, msg: str):
        self._log(logging.ERROR, msg)

    def log_warn(self, msg: str):
        self._log(logging.WARN, msg)

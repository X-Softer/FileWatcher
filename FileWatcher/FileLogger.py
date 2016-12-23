from datetime import datetime
from enum import IntEnum
import os

class LogEntryType(IntEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

class FLogger(object):
    """Simple logger"""
    
    file_ext = "log"
    need_to_print = False
    log_level = LogEntryType.DEBUG

    def __init__(self, file_path):
        self.file_path = file_path

    def debug(self, mess):
        self.write_to_log(LogEntryType.DEBUG, mess)

    def info(self, mess):
        self.write_to_log(LogEntryType.INFO, mess)

    def warning(self, mess):
        self.write_to_log(LogEntryType.WARNING, mess)

    def error(self, mess):
        self.write_to_log(LogEntryType.ERROR, mess)

    def write_to_log(self, type, mess):
        if(int(type) >= int(self.log_level)):
            if type == LogEntryType.DEBUG:
                prefix = "[DEBUG]"
            elif type == LogEntryType.INFO:
                prefix = "[INFO]"
            elif type == LogEntryType.WARNING:
                prefix = "[WARNING]"
            elif type == LogEntryType.ERROR:
                prefix = "[ERROR]"
            else:
                prefix = ""

            mess_str = "{0:%Y-%m-%d %H:%M:%S} {1}: {2}".format(datetime.now(), prefix, mess)
            file_name = "{0:%Y-%m-%d}.{1}".format(datetime.now(), self.file_ext)
            full_file_name = os.path.join(self.file_path, file_name)

            if self.need_to_print :
                print(mess_str)
            
            with open(full_file_name, mode = "a") as log_f:
                log_f.write(mess_str + "\n")

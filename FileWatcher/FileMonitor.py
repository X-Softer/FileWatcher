import sys, os, glob, time
import threading
from datetime import datetime

sys.path.insert(0, "..")

import Common.Logging
import HttpFileSender
import Settings

logger = Common.Logging.FileLogger.FLogger(Settings.LOG_PATH)
logger.need_to_print = True
logger.file_ext = "monitor.log"

sender = HttpFileSender.HttpFileSender(logger)

os.environ['no_proxy'] = '127.0.0.1,localhost'

global break_watcher_flag

def print_file_list (file_list, header = None):
    for fn in file_list:
        msg = header + ": " + fn
        logger.info(msg)
    

def on_added_handler(file_list):
    """On added file handler"""
    print_file_list(file_list, "Added")
    for f in file_list:
        logger.info('Sending file "{0}"...'.format(f));
        send_file(f)


def on_removed_handler(file_list):
    """On remove file handler"""
    print_file_list(file_list, "Remove")


def save_file_list(list):
    """Save list to file"""
    if Settings.FILE_LIST:
        with open(Settings.FILE_LIST, mode="w") as f:
            for fl in list: 
                f.write(fl + "\n")


def load_file_list():
    """Load list from file """
    list = None
    if Settings.FILE_LIST:
        logger.info("Loading initial file list from " + Settings.FILE_LIST)
        with open(Settings.FILE_LIST, mode="r") as f:
            list = [line.strip() for line in f]
    return list


def add_error_to_list(error):
    """ Add error entry to error list, if it defined
    """
    if(Settings.ERROR_LIST):
        with open(Settings.ERROR_LIST, mode="a") as ef:
            ef.write("{0:%Y-%m-%d %H:%M:%S}\t{1}\n".format(datetime.now(), error))
    

def watch_files(search_mask, on_added, on_removed, to_break = None, initial_list = None, on_save_list = None):
    """Simple file watcher"""

    # if it has initial file-list, apply it
    if initial_list : 
        before = initial_list
    else:
        before = glob.glob(search_mask)
    
    while 1:
        # callback for exit
        if to_break :
            s = to_break()
            if s : break

        after = glob.glob(search_mask)

        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added: 
            if on_added : on_added(added)
            if(on_save_list) : on_save_list(after)
        if removed: 
            if on_removed: on_removed(removed)
            if(on_save_list) : on_save_list(after)
        before = after
        time.sleep(1)

def break_watcher():
    global break_watcher_flag
    return break_watcher_flag

def send_file(source_full_fn):
    """ Call file sender to send file
    """
    (source_dir, source_fn) = os.path.split(source_full_fn) 

    (res, desc, resp) =  sender.send_file(Settings.SENDING_URL, source_full_fn, HttpFileSender.PostMethod.MULTIPART_FORM_DATA)
    if res:
        logger.info('File "{0}" was sent. Describe={1} Response={2}'.format(source_full_fn, desc, resp))
    else:
        logger.error('File "{0}" was NOT SENT, error. Describe={1} Response={2}'.format(source_full_fn, desc, resp))
        add_error_to_list(source_full_fn)

def main():
    """ Main process
    """
    global break_watcher_flag
    try:
        break_watcher_flag = False

        init_file_list = load_file_list()
        logger.info("Start monitoring for \"" + Settings.SEARCH_MASK + "\"")

        watch_files(Settings.SEARCH_MASK, on_added_handler, on_removed_handler, initial_list = init_file_list, on_save_list = save_file_list)    

    except KeyboardInterrupt:
        logger.warning("Service has been interrupted by keyboard")


if __name__ == "__main__":
    sys.exit(int(main() or 0))


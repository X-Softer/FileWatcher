import http.server
import socketserver
import time
import sys

sys.path.insert(0, "..")

import HttpServer
import Settings

from Common.Logging.FileLogger import FLogger, LogEntryType

logger = FLogger(Settings.LOG_PATH)
logger.need_to_print = True
#logger.log_level = LogEntryType.INFO
logger.file_ext = "receiver.log"

Handler = HttpServer.FRHttpRequestHandler
Handler.store_files_path = Settings.STORE_FILES_PATH
Handler.logger = logger

httpd = socketserver.TCPServer((Settings.HOSTNAME, Settings.PORT), Handler)

try:
    logger.info("Server starts [%s:%s]" % (Settings.HOSTNAME, Settings.PORT))
    httpd.serve_forever()
except KeyboardInterrupt:
    logger.warning("Service has been interrupted by keyboard")
    pass

httpd.server_close()
logger.info("Server has been stopped [%s:%s]" % (Settings.HOSTNAME, Settings.PORT))

#print("Serving at port ", PORT)
#httpd.serve_forever()


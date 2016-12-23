import http.server
import socketserver
import cgi
import re
import os
import sys

from http import HTTPStatus
from FileLogger import LogEntryType

class FRHttpRequestHandler(http.server.BaseHTTPRequestHandler):

    """HTTP request handler with POST"""

    server_version = "PyHttpServer/" + http.server.__version__
    store_files_path = ".";
    logger = None

    # Just for test service
    def do_GET(self):
        """Serve a GET request.
        """
        self.send_response(HTTPStatus.BAD_REQUEST)
        self.end_headers()

    def do_POST(self):
        """ Serve a POST request
        """
        try:
            if self.path == '/store':
                self.write_to_log("Request for /store", LogEntryType.INFO)
                # store multipart/form-data file
                r, info = self.process_post_data()
                if not r:
                    self.write_to_log("Request processing error: {0}".format(info), LogEntryType.ERROR)
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                    self.end_headers()
                else:    
                    self.write_to_log("Request processing result: {0}".format(info), LogEntryType.INFO)
                    self.send_response(HTTPStatus.OK)
                    self.end_headers()
                self.write_response(r, info)
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                self.write_to_log("Wrong URL {0}".format(self.path), LogEntryType.ERROR)
        except Exception as e:
            self.write_to_log("Exception: {0}: {1}" .format(e, self.bug_report()), LogEntryType.ERROR)
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.end_headers()
            self.write_response(False, "System error")

    def write_response(self, r, info):
        """ Write response to out stream 
        """
        if r:
            info = "<response><error>0</error></response>"    
        else:
            info = "<response><error>1</error><description>{0}</description></response>".format(info)    
        self.wfile.write(bytes(info, "utf-8"))

    def process_post_data(self):
        """ Process multipart/form-data stream
        """
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-type is not presented")

        if content_type.find("multipart/form-data") == -1:
            return (False, "Wrong 'Content-type'")

        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        full_fn = os.path.join(self.store_files_path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn2 = re.findall(r'Content-Type:.*',line.decode())
        if fn2:
            line = self.rfile.readline()
            remainbytes -= len(line)
        
        with open(full_fn, 'wb') as out:                
            preline = self.rfile.readline()
            remainbytes -= len(preline)
            while remainbytes > 0:
                line = self.rfile.readline()
                remainbytes -= len(line)
                if boundary in line:
                    preline = preline[0:-1]
                    if preline.endswith(b'\r'):
                        preline = preline[0:-1]
                    out.write(preline)
                    out.close()
                    return (True, "File '%s' uploaded successfully" % full_fn)
                else:
                    out.write(preline)
                    preline = line

        return (False, "Unexpect Ends of data.")    

    def log_request(self, code='-', size='-'):
        """ Overrides base log_request
        """
        if isinstance(code, HTTPStatus):
            code = code.value
        self.write_to_log("'{0}' {1} {2}".format(self.requestline, str(code), str(size)), LogEntryType.DEBUG)

    def write_to_log(self, mess, type):
        """ Write message to log by FLogger object 
        """
        if self.logger:
            if type == LogEntryType.DEBUG:
                self.logger.debug(mess)
            elif type == LogEntryType.INFO:
                self.logger.info(mess)
            elif type == LogEntryType.WARNING:
                self.logger.warning(mess)
            elif type == LogEntryType.ERROR:
                self.logger.error(mess)

    def bug_report(self):
        if sys.exc_info() != (None,None,None) : last_type, last_value, last_traceback = sys.exc_info()
        else : last_type, last_value, last_traceback = sys.last_type, sys.last_value, sys.last_traceback 
        tb, descript = last_traceback, ""
        while tb :
            fname, lno = tb.tb_frame.f_code.co_filename, tb.tb_lineno
            descript += ('\tFile "%s", line %s, in %s\n'%(fname, lno, tb.tb_frame.f_code.co_name))
            tb = tb.tb_next
        descript += ('%s : %s\n'%(last_type.__name__, last_value))
        return descript
        
            

   
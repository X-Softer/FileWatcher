from enum import Enum
import requests
import os
import sys

from Common.Logging.FileLogger import LogEntryType

class PostMethod(Enum):
    MULTIPART_FORM_DATA = 1
    URL_ENCODED = 2

class HttpFileSender(object):
    """ Implements sending file via HTTP by other methods
    """
    logger = None

    def __init__(self, logger = None):
        self.logger = logger

    def send_file(self, url, file_name, method, **kwargs):
        """ Send file via HTTP by other methods (multipart/form or )
            Params:
                Required:
                    file_name    - file_name for send
                    url          - URL for http-service
                Optional:
                    content_type  - value for Content-type http-header
                    add_headers   - dictionary of addition http-headers
                    new_file_name - file name for store (if need to use other name)
            Returns:
                (res, descr, response)
                    status   - boolean result, true - success, false - error
                    descr    - describe result (may be None or empty if success)
                    response - full binary response from HTTP-service
        """
        if not url : raise ValueError("wrong value of 'url'")
        if not file_name : raise ValueError("wrong value of 'file_name'") 
        if (not method or type(method) is not PostMethod): raise ValueError("wrong value of 'channel_type'") 
        
        add_headers = kwargs.get("headers")
        content_type = kwargs.get("content_type")
        new_file_name = kwargs.get("new_file_name")
        
        try:
            if method == PostMethod.MULTIPART_FORM_DATA:
                self.write_to_log('Sending file "{0}" as multipart/form-data'.format(file_name), LogEntryType.DEBUG)
                return self.send_file_as_multipartdata(url = url, file_name = file_name, content_type = content_type, add_headers = add_headers, new_file_name = new_file_name)
            elif method == PostMethod.URL_ENCODED:
                self.write_to_log('Sending file "{0}" as application/x-www-form-urlencoded'.format(file_name), LogEntryType.DEBUG)
                return self.send_file_as_url_encoded(url = url, file_name = file_name, content_type = content_type, add_headers = add_headers, new_file_name = new_file_name)
        except Exception as e:
            self.write_to_log("Exception: {0}: {1}" .format(e, self.bug_report()), LogEntryType.ERROR)
            return (False, "System Error", "")
    
    def send_file_as_multipartdata(self, url, file_name, new_file_name, add_headers, content_type):
        """ Sending file as mulipart/form-data
        """
        if new_file_name: 
            fn = new_file_name
        else:
            (dirn, fn) = os.path.split(file_name)

        headers = {}
        if add_headers:
            if type(add_headers) is not dict:
                raise ValueError("add_headers must be a dict")
            headers.update(add_headers)
        if content_type:
            headers.append("Content-type", content_type)
        #if info :
        #    files = {'file': (fn, info)}
        if not file_name: raise ValueError("file_name parameter must be passed")

        with open(file_name, 'rb') as f:
            files= {'file': (fn, f)}
            r = requests.post(url, files=files)

            if(r.status_code != requests.codes.ok):
                return (False, "Error response. Code={0}".format(r.status_code), r.content)
            return (True, "OK", r.content)

    def send_file_as_url_encoded(self, url, file_name, new_file_name, add_headers, content_type):
        """ Sending file as application/x-www-form-urlencoded
        """
        raise NameError("Method not implemented yet")
    
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
        """ Returnts small trace of exception
        """
        if sys.exc_info() != (None,None,None) : last_type, last_value, last_traceback = sys.exc_info()
        else : last_type, last_value, last_traceback = sys.last_type, sys.last_value, sys.last_traceback 
        tb, descript = last_traceback, ""
        while tb :
            fname, lno = tb.tb_frame.f_code.co_filename, tb.tb_lineno
            descript += ('\tFile "%s", line %s, in %s\n'%(fname, lno, tb.tb_frame.f_code.co_name))
            tb = tb.tb_next
        descript += ('%s : %s\n'%(last_type.__name__, last_value))
        return descript
    
    

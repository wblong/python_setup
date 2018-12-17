#!/usr/bin/env python
#coding: utf-8

import os, math, sys, time
import codecs, socket,urllib,urllib2,urlparse, json, hashlib, random, traceback, platform
import logging
import logging.config
import util

from optparse import OptionParser
from datetime import datetime

class WebApi:
    def __init__(self,logger):
        self.logger = logger
    def http_get(self,url=None,debug=False):
        if url is None:
            self.logger.debug("url is None")
            return False,None
        content=None
        result=True
        connect=None
        try:
            if debug == True:
                self.logger.debug("request: {}".format(url))
            connect = urllib2.urlopen(url, timeout=3)
            content = connect.read()
            if debug == True:
                self.logger.debug("response: '{}'".format(content))
            result = True
        except urllib2.HTTPError as err:
            self.logger.error("error: '{}, url:{}".format(err, url))
            result = False
        except urllib2.URLError as err:
            self.logger.error("error: '{}', url:{}".format(err, url))
            if hasattr(err, 'code'):
                content = err.read()
                self.logger.debug(content)                
            elif hasattr(err, 'reason'):
                pass
            result = False
        except socket.timeout as err:
            self.logger.error(" error: '{}', url:{}".format(err, url))
            result = False
        finally:
            if connect:
                connect.close()
                del connect
            return result, content

    def http_post(self,url=None,data=None,debug=False):
        if url is None:
            self.logger.debug("url is None")
            return False,None
        content=None
        result=True
        connect=None
        req_data=None
        headerdata = {"Content-type": "application/json"}
        if data is not None:
            req_data=json.dumps(data)
            self.logger.debug("request data:{}".format(req_data))
        try:
            if debug == True:
                self.logger.debug("request: {}".format(url))
            req=urllib2.Request(url,req_data,headerdata)
            if debug == True:
                self.logger.debug("request full url:{};data:{}".format(req.get_full_url(),req.get_data()))
            connect = urllib2.urlopen(req, timeout=3)
            content = connect.read()
            if debug == True:
                self.logger.debug("response: '{}'".format(content))
            result = True
        except urllib2.HTTPError as err:
            self.logger.error("error: '{}, url:{}".format(err, url))
            result = False
        except urllib2.URLError as err:
            self.logger.error("error: '{}', url:{}".format(err, url))
            if hasattr(err, 'code'):
                content = err.read()
                self.logger.debug(content)                
            elif hasattr(err, 'reason'):
                pass
            result = False
        except socket.timeout as err:
            self.logger.error(" error: '{}', url:{}".format(err, url))
            result = False
        finally:
            if connect:
                connect.close()
                del connect
            return result, content


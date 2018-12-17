#!/usr/bin/env python
#coding: utf-8

import os, math, sys, time
import logging
import logging.config
import threading

from threading import Lock
from datetime import datetime

class Log:
    m_mutex = Lock()
    m_monitor_dirs = []
    m_running = True

    def create(self, dir, prefix):
        format = '%(asctime)s>%(levelname)s>[%(funcName)s: %(filename)s, %(lineno)d] %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=format,
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filemode='a')
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # create a file handler
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        logpath = "{}/{}_{}.log".format(dir, prefix, now)
        handler = logging.FileHandler(logpath)
        handler.setLevel(logging.DEBUG)

        # create a logging format
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
    
        # add the handlers to the logger
        logger.addHandler(handler)
        return logger

    def get_instance(self):
        return self.logger

    def __init__(self, dir, prefix, expired_days):
        self.dir = dir
        Log.add_dir(dir)

        self.prefix = prefix
        self.expired_days = expired_days
        self.logger = self.create(dir, prefix)

    def stop(self):
        Log.m_running = False

    def start(self):
        self.thread = threading.Thread(target=Log.cleanup_func
                                    , args=(self.expired_days,))
        self.thread.start()

    @staticmethod
    def cleanup_func(expired_days):
        while Log.m_running:
            # copy monitor dirs
            Log.m_mutex.acquire()
            dirs = Log.m_monitor_dirs[:]
            Log.m_mutex.release()
            # clean up
            for dir in dirs:
                if os.path.exists(dir) == False:
                    continue
                file_list = []
                child_list = os.listdir(dir)
                # foreach child file
                for i in range(0, len(child_list)):
                    path = os.path.join(dir, child_list[i])
                    if os.path.isfile(path):
                        file_list.append(path)
                # delete
                for i in range(0, len(file_list)):
                    path = file_list[i]
                    timestamp = os.path.getmtime(path)
                    last_modify_timestamp = datetime.fromtimestamp(timestamp)
                    now = datetime.now()
                    elapse_days = (now.toordinal()-last_modify_timestamp.toordinal())

                    if elapse_days >= expired_days:
                        os.remove(path)
                        print("delete expired file: {}".format(path))
            # interval 1 hour
            time.sleep(60)

    @staticmethod
    def add_dir(dir):
        Log.m_mutex.acquire()
        Log.m_monitor_dirs.append(dir)
        Log.m_monitor_dirs = list(set(Log.m_monitor_dirs))
        Log.m_mutex.release()
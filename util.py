#!/usr/bin/env python
#coding: utf-8

import os, math, sys, time, platform, threading, signal, traceback
import subprocess, re
import time, signal, sys,commands

def kill_process_by_pid(pid):
    os.kill(pid, signal.SIGTERM)

def kill_process(name):
    os_name = platform.system()
    if os_name == "Windows":
        kcmd = "taskkill /f /im {}".format(name)
    else:
        kcmd = "pkill {}".format(name)
    os.system(kcmd)

def get_windows_process():
    tasks = subprocess.check_output(['tasklist']).split("\r\n")
    process_list = []
    for task in tasks:
        m = re.match("(.+?) +(\d+) (.+?) +(\d+) +(\d+.* K).*", task)
        if m is not None:
            process_list.append({"image":m.group(1),
                            "pid":m.group(2),
                            "session_name":m.group(3),
                            "session_num":m.group(4),
                            "mem_usage":m.group(5)                                                                      
                            })
    return process_list

def process_match_on_windows(names, pid):
    process_list = get_windows_process()
    for process in process_list:
        if process["image"] in names and process["pid"] == pid:
            return True
    return False

def kill_old_process(workDir, names):
    filepath = workDir + os.sep + "pid.txt"
    with open(filepath, 'a+') as f:
        old_pid = f.readline()
        if old_pid:
            old_pid = old_pid.strip()
            if process_match_on_windows(names, old_pid):
                kill_process_by_pid(int(old_pid))
    with open(filepath, 'w+') as f :
        f.write('%d\n' % os.getpid())

def try_single_process(workDir, names, logger):
    if platform.system() == "Windows":
        names = map(lambda x: x + ".exe", names)
        kill_old_process(workDir, names)
        return True
    else:
        return False

def getTraceLog(err):
    '''
    save traceback infomation
    '''
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traces = traceback.format_exception(exc_type, exc_value, exc_traceback)
    traceLogs = ""
    for trace in traces:
        traceLogs += trace
    return traceLogs
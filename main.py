#!/usr/bin/env python
#coding: utf-8

from collections import OrderedDict
import json,os,time,hashlib
import stomp
import pika

from stomp.transport import ssl

from log import Log
from util import getTraceLog
from webapi import WebApi

_g_version = "V1.0.0.0"

def readConfig(filename,logger):
    """
    读取配置文件
    """
    config=None
    with open(filename,"rb") as f:
        config=json.load(f)
        logger.debug("setting:{}".format(repr(config)))
    return config

def makeEventRequest(config,logger):
    """
    生成事件订阅请求
    """
    url=None
    data={}
    u_time=int(time.time()*1000)
    config["params_event"]['time']=u_time
    params=json.dumps(config["params_event"])
    raw_url=config['url_event']+params+config['screct']
    md5=hashlib.md5()
    md5.update(raw_url)
    token=md5.hexdigest()
    url="{}{}?token={}".format(config["host"],config["url_event"],token.upper())
    data=config["params_event"]
    logger.debug("event url:{};data:{}".format(url,repr(data)))
    return url,data
def makeUserIdRequest(config,logger):
    """
    生成用户ID请求
    """
    url=None
    data={}
    u_time=int(time.time()*1000)
    config["params_user"]["time"]=u_time
    params=json.dumps(config["params_user"])
    raw_url=config["url_user"]+params+config['screct']
    md5=hashlib.md5()
    md5.update(raw_url)
    token=md5.hexdigest()
    url="{}{}?token={}".format(config["host"],config["url_user"],token.upper())
    data=config["params_user"]
    logger.debug("user uuid request:{};data:{}".format(url,repr(data)))
    return url,data

def getMQData(content,logger):
    """
    获取MQ地址和路由
    """
    logger.debug("raw mqdata:{}".format(content))
    destination=None
    mqURL=[]
    msg=json.loads(content)
    errorCode=msg.get("errorCode")
    if errorCode==0:
        data=msg.get("data",None)
        if data is not None:
            destination="/topic/{}".format(data.get("destination",None))
            host,port=data.get("mqURL",None).split(':')
            port=int(port)
            temp_url=[]
            temp_url.append(host)
            temp_url.append(port)
            mqURL.append(tuple(temp_url))
            logger.debug("destination:{};mqURL:{}".format(destination,mqURL))
        else:
            logger.debug("Request Data is None")
    else:
        logger.error("Request Data Failed,Error:{}".format(errorCode))
    return destination,mqURL

def getUserData(content,logger):
    """
    获取用户uuid
    """
    logger.debug("raw userdata:{}".format(content))
    useruuid=None
    msg=json.loads(content)
    errorCode=msg.get("errorCode")
    if errorCode==0:
        data=msg.get("data",None)
        if data is not None:
            useruuid=data
            logger.debug("useruuid:{}".format(useruuid))
        else:
            logger.debug("Request Data is None")
    else:
        logger.error("Request Data Failed,Error:{}".format(errorCode))
    return useruuid

class Listener(object):
    """
    ActiveMQ 回调函数类
    """
    def __init__(self,logger,setting):
        self.logger=logger
        self.setting=setting
        self.connection=None
        self.channel=None

    def on_message(self,headers,message):
        self.logger.debug('message:%s'% message)
        self.process(message)

    def on_error(self,header,message):
        self.logger.error("received an error %s"% message)

    def on_connected(self,header,body):
        self.logger.debug("connected %s"% body)
        try:
            username=self.setting["username"]
            password=self.setting["password"]
            host=self.setting["host"]
            port=self.setting["port"]
            virtualhost=self.setting["virtualhost"]
            credentials=pika.PlainCredentials(username,password)
            self.connection = pika.BlockingConnection(                      \
                                    pika.ConnectionParameters(              \
                                                                host,       \
                                                                port,       \
                                                                virtualhost,\
                                                                credentials))
            self.channel = self.connection.channel()
            # self.channel.queue_declare(queue='hello')
        except Exception as err:
             logger.error("Error:{}".format(getTraceLog(err)))
        

    def on_disconnected(self):
        self.logger.debug("disconnected")
        if self.connection is not None:
            self.connection.close()

    def on_connecting(self,host_and_port):
        self.logger.debug("connecting %s %d" % host_and_port)

    def process(self,msg):
        self.logger.debug("process <{}>".format(repr(msg)))
        """
        {"calltime":"2018/12/23 15:20:22","windowid":3}
        """
        self.channel.basic_publish(                                         \
                                    exchange=self.setting["exchange"],      \
                                    routing_key=self.setting["routing_key"],\
                                    body=repr(msg))

def receive_from_topic(host_and_port,destination,logger,setting):
    """
    ActiveMQ 从主题接收信息
    """
    try:
        # conn=stomp.Connection10(host_and_port)
        conn=stomp.Connection(host_and_ports=host_and_port)
        conn.set_listener("Listener",Listener(logger,setting))
        # conn.set_ssl(for_hosts=host_and_port,ssl_version=ssl.PROTOCOL_SSLv23)
        conn.start()
        conn.connect("admin","admin",wait=True)
        conn.subscribe(destination,"trkj")
        while True:
            time.sleep(30)
        conn.disconnect()
    except Exception as err:
        logger.error("Error:{}".format(getTraceLog(err)))
    


if __name__=="__main__":
    
    appname="main"
    work_dir=os.getcwd()
    log_dir=work_dir+os.sep+"log"
    log=Log(log_dir,appname,3)
    logger=log.get_instance()
    log.start()
    logger.debug("{} {}, pid:{}".format(appname, _g_version, os.getpid()))
    
    try:
        filename=os.getcwd()+os.sep+"setting.json"
        config=readConfig(filename,logger)
        take_req=WebApi(logger)
        if config is not None:
            url,data=makeUserIdRequest(config,logger)
            result,content=take_req.http_post(url,data,True)
            if result == True:
                useruuid=getUserData(content,logger)

            url,data=makeEventRequest(config,logger)
            result, content=take_req.http_post(url,data,True)
            if result == True:
                destination,mqURL=getMQData(content,logger)
                ## connecting to activemq
                # host_and_port=[("127.0.0.1",61613)]
                # destination="/topic/{}".format("ADSB.Receiver")
                receive_from_topic(mqURL,destination,logger,config["rabbitmq"])   
            # host_and_port=[("127.0.0.1",61613)]
            # destination="/topic/{}".format("ADSB.Receiver1")
            # receive_from_topic(host_and_port,destination,logger,config["rabbitmq"])   
    except Exception as err:
        logger.error("Error:{}".format(getTraceLog(err)))


    
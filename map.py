#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import syslog
import time
import re
import sys
import os
import MySQLdb

class log():
    """
    Send log messages to syslog
    syslogtag = str(), facility = int(), priority = int(), message = str()
    are input parameters
    """
    syslogtag = str()
    message = str()
    facilitys = [syslog.LOG_USER, syslog.LOG_CRON, syslog.LOG_LOCAL0, syslog.LOG_LOCAL1, syslog.LOG_LOCAL2, syslog.LOG_LOCAL3, syslog.LOG_LOCAL4, syslog.LOG_LOCAL5, syslog.LOG_LOCAL6, syslog.LOG_LOCAL7]
    prioritys = [syslog.LOG_DEBUG, syslog.LOG_INFO, syslog.LOG_NOTICE, syslog.LOG_WARNING, syslog.LOG_ERR, syslog.LOG_CRIT, syslog.LOG_ALERT, syslog.LOG_EMERG]
    facility = facilitys[0]
    priority = prioritys[0]

    def __init__(self, facility = 0, priority = 0, syslogtag = "python"):
        """Initiate syslog parameters"""

        self.priority = self.prioritys[priority]
        self.facility = self.facilitys[facility]
        self.syslogtag = syslogtag

    def __del__(self):
        """destroctor"""
        return

    def logger(self, message):
        """Send log message to the syslog with preset parameters"""
        message = re.sub("[\n\r]+", " ", message)
        message = message[:950]

        syslog.openlog(self.syslogtag, (syslog.LOG_PID + syslog.LOG_NOWAIT), self.facility)
        syslog.syslog(self.priority, message)
        syslog.closelog()

class setup():
    """A variety of executive setting functions"""
    def __init__(self):
        """Initiate and include some class"""
        dir = os.path.dirname(__file__)
        includedir = os.path.join(dir, "./")
        sys.path.append(includedir)
        
        from Config import Config

        self.Conf = Config()
        self.Log = log()

    def __del__(self):
        """Destructor"""
        self.Conf = None
        self.log = None
        return

    def identifiString(self, string = str()):
        """Identify a database name string"""
        formated = str()
        if not re.search(r"%[xXc]", string, re.U):
            formated = time.strftime(string)

        return formated

    def getMySQLhost(self):
        """Return MySQL host"""
        return self.Conf.MySQLconnector["host"]

    def getMySQLuser(self):
        """Return MySQL user name"""
        return self.Conf.MySQLconnector["user"]

    def getMySQLpassword(self):
        """Return MySQL users password"""
        return self.Conf.MySQLconnector["password"]

    def getMySQLdatabase(self):
        """Return the reformated log db string"""
        dbName = self.identifiString(self.Conf.MySQLconnector["database"])
        return dbName

    def getMySQLtable(self, tblname = ''):
        """Return the reformated log table name"""
        tblName = self.identifiString(self.Conf.MySQLconnector["tableprefix"]) + tblname
        return tblName

    def getLogLevel(self):
        """Return the loging level"""
        return self.Conf.loglevel

class db():
    """
    Database connection class
    hostname = str(), username = str(), password = str(), databes = str()
    are input parameters
    """

    hostname = str()
    username = str()
    password = str()
    database = str()

    def __init__(self, host, user, passwd, database):
        """Initiate database connection parameters"""

        self.hostname = host
        self.username = user
        self.password = passwd
        self.database = database

    def __del__(self):
        """destructor"""

        return

    def connector(self):
        """Create and return mysql connector object"""

        try:
            conn = MySQLdb.connect(host = self.hostname, user = self.username, passwd = self.password, db = self.database)
        except MySQLdb.Error, e:
            message = "Error in db.connector(): %d, %s" % (e.args[0], e.args[1])
            mLog = log(0,7,"nagios-status-map.db.connector")
            mLog.logger(message)
            return -1
        else:
            return conn

    def runQuery(self, connect, querry):
        """Run MySQL querry on selected database"""

        try:
            cursor = connect.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(querry)
            resoult_set = cursor.fetchall()
        except MySQLdb.Error, e:
            message = "Error in db.runQuery(): %d, %s" % (e.args[0], e.args[1])
            mLog = log(0,7,"nagios-status-map.db.connector")
            mLog.logger(message)
            return -1
        else:
            return resoult_set

class map():
    # Containing all setup parameters
    SET = object
    
    # Database represent object
    dbObj = object
    # DB connectivity pointer
    dbConn = object

    # syslog connectivity object
    L = log(0,0,'nagios-map')

    def __init__(self):
        # Loading setup
        self.SET = setup()

        # Connect to the database
        self.dbObj = db(self.SET.getMySQLhost(), self.SET.getMySQLuser(), self.SET.getMySQLpassword(), self.SET.getMySQLdatabase())
        self.dbConn = self.dbObj.connector()
        self.L.logger('map init')

    def __del__(self):
        
        return

    def allHosts(self):
        """Returns list of hashes contains hostnames and our id's"""
        hosts = self.dbObj.runQuery(self.dbConn, 'SELECT host_object_id AS id, display_name AS name FROM nagios_hosts;')
        return hosts

    def getMapObjectSize(self, nagiosObjectId):
        """Calculate map object size from number of hosts service checks number"""
        obj_size = self.dbObj.runQuery(self.dbConn, 'SELECT COUNT(*) * %i AS size FROM ndoutils.nagios_services WHERE host_object_id =  %i' % (self.SET.Conf.mapObjEnlargeFactor, nagiosObjectId))
        return int(obj_size[0]['size'])

    def checkSuperParent(self, nagiosObjectId):
        """Returns number of parents for super parent host"""
        Q = 'SELECT COUNT(*) AS num FROM nagios_host_parenthosts WHERE host_id = (SELECT host_id FROM nagios_hosts WHERE host_object_id = %i);' % nagiosObjectId
        # self.L.logger('SQL QUERY: %s' % Q)
        host_num = self.dbObj.runQuery(self.dbConn, Q)
        return host_num[0]['num']

    def checkChildsNum(self, nagiosObjectId):
        """Returns number of parents"""
        Q = 'SELECT COUNT(*) AS num FROM nagios_host_parenthosts WHERE parent_host_object_id = %i' % nagiosObjectId
        # self.L.logger('SQL QUERY: %s' % Q)
        host_num = self.dbObj.runQuery(self.dbConn, Q)
        return host_num[0]['num']

    def getObjectName(self, nagiosObjectId):
        """Returns with object name"""
        Q = 'SELECT name1 AS name FROM nagios_objects WHERE object_id = %i' % nagiosObjectId
        # self.L.logger('SQL QUERY: %s' % Q)
        host_name = self.dbObj.runQuery(self.dbConn, Q)
        return str(host_name[0]['name'])

    def getHostLinkState(self, nagiosObjectId):
        """Returns with network lint state"""
        link = "down"
        Q = "SELECT state FROM map_host_alive WHERE host_id = %i;" % nagiosObjectId
        # self.L.logger('SQL QUERY: %s' % Q)
        aliveState = self.dbObj.runQuery(self.dbConn, Q)
        if len(aliveState) > 0:
            if aliveState[0]['state'] == 0:
                link = "up"
        else:
            link = "up"
        return link

    def generateMapTree(self, superParent):
        tree = { 'children': list() }
        childs = self.dbObj.runQuery(self.dbConn, 'SELECT nh.host_object_id AS child_host_id FROM nagios_host_parenthosts nhp JOIN nagios_hosts nh ON nh.host_id = nhp.host_id WHERE parent_host_object_id = %i;' % superParent)
        if len(childs) > 0:
            for child in childs:
                if self.checkChildsNum(child['child_host_id']) > 0:
                    self.L.logger( "ParentName: %s, childnum: %i" % ( self.getObjectName(child['child_host_id']),self.checkSuperParent(child['child_host_id']) ))
                    tree['children'].append( {
                                                'name': self.getObjectName(child['child_host_id']),
                                                'size': self.getMapObjectSize(child['child_host_id']),
                                                'link': self.getHostLinkState(child['child_host_id']),
                                                'children': self.generateMapTree(child['child_host_id'])['children']
                                              } )
                else:
                    self.L.logger("No existent child host")
                    tree['children'].append( {
                                                'name': self.getObjectName(child['child_host_id']),
                                                'link': self.getHostLinkState(child['child_host_id']),
                                                'size': self.getMapObjectSize(child['child_host_id'])
                                              } )
            
        return tree
    
def index(req):
    req.content_type = 'application/json'
    resultSet = dict()
    # syslog connectivity object
    L = log(0,0,'nagios-map')

    # MAP object
    MAP = map()
    
    # List of all nagios host names and ids
    hosts = MAP.allHosts()
    
    # Search superparent(s) hosts
    for host in hosts:
        if MAP.checkSuperParent(host['id']) < 1:
            L.logger("Super parent host: %i. %s" % (host['id'], host['name']))
            resultSet = {'name': host['name'], 'size': MAP.getMapObjectSize(host['id']), 'children': MAP.generateMapTree(host['id'])['children'] }
            
    
    return resultSet

"""
CREATE  TABLE `ndoutils`.`map_host_service_status` (
  `id` MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `host_object_id` MEDIUMINT UNSIGNED NULL ,
  `service_object_id` MEDIUMINT UNSIGNED NULL ,
  `status` MEDIUMINT UNSIGNED NULL ,
  PRIMARY KEY (`id`) )
ENGINE = MEMORY
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;
"""

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

    def getMySQLtable(self):
        """Return the reformated log table name"""
        tblName = self.identifiString(self.Conf.MySQLconnector["table"])
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
        


def index():
    SET = setup()
    dbObj = db(SET.getMySQLhost(), SET.getMySQLuser(), SET.getMySQLpassword(), SET.getMySQLdatabase())
    dbConn = dbObj.connector()
    
    L = log(0,0, "nagios-status-map")

    return "Map start"

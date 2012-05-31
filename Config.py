#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config:
    """All setup variables"""
    MySQLconnector = {
        'host': 'localhost',
        'user': 'nagiosmap',
        'password': 'uZ3ooco9asiZ',
        'database': 'ndoutils',
        'tableprefix': 'nagios_'
    }
    
    # Loging level
    loglevel = 0

    # Maximum size of circle on map
    mapObjMaxSize = 10
    
    # Map object enlarge factor
    # set to one (default value is 2.5)
    # for normal size
    mapObjEnlargeFactor = 2.5
    
    #
    hostAliveCheckName = 'check-host-alive'
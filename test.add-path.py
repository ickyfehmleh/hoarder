#!/usr/bin/python2.6
#
#
#

from app.dao import initDatabase
from app.dao.file import FileDAO
from app.dao.disk import DiskDAO

Session = initDatabase()
fileDAO = FileDAO(Session)
diskDAO = DiskDAO(Session)

# get first disk
disk = diskDAO.getAllDisks()[0]

p = fileDAO.createMonitoredPath('/share/expired', 'M', disk )

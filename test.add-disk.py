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

# add disk
disk = diskDAO.createNewDiskWithPath('/share/expired')

#disk = diskDAO.getAllDisks()[0]

print 'Disk free space: ', disk.freeSpace
print 'Disk ID        : ', disk.identifier

#!/usr/bin/python2.6
#
#
#

from app.dao import initDatabase
from app.dao.file import FileDAO
from app.dao.disk import DiskDAO
from app import human_readable as hr

Session = initDatabase()
fileDAO = FileDAO(Session)
diskDAO = DiskDAO(Session)

path = fileDAO.getMonitoredPath('/Users/movies/Movies/2011-06-18' )

print 'Path: %s'
print 'Disk UUID: %s' % path.archiveDisk.identifier
print 'Disk total space: %s' % hr( path.archiveDisk.totalSpace )
print 'Disk free  space: %s' % hr( path.archiveDisk.freeSpace )


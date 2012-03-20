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

# get all disks
allDisks = diskDAO.getAllDisks()
for disk in allDisks:
	print 'All Disks: name=%s' % disk.path
print


# get first disk
disk = diskDAO.getDiskWithId(1)

print 'Disk: %s' % disk.path
print 'Total space: %s' % hr( disk.totalSpace )
print 'Free  space: %s' % hr( disk.freeSpace )


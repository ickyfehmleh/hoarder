#!/usr/bin/python2.6
#
#
#
from app.dao import initDatabase
from app.dao.file import FileDAO
from app.dao.disk import DiskDAO
from app import human_readable as hr
import time

Session = initDatabase(debug=True)
fileDAO = FileDAO(Session)

# get last n files
lastFiles = fileDAO.getLastFilesAdded()

print 'Default len: %d' % len(lastFiles)
for f in lastFiles:
	print '--> File: %s || Date Added: %s' % (f.fileName, time.ctime( f.dateAdded ) )
print

print 'Trying to fetch the last 3'
lastFiles = fileDAO.getLastFilesAdded(num=3)
for f in lastFiles:
	print '--> File: %s || Date Added: %s' % (f.fileName, time.ctime( f.dateAdded ) )
print
